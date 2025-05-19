import requests
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

def run():
    # --- Step 0: 認証 ---
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Google Sheets 認証
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Weekly live information").sheet1  # スプレッドシート名に合わせて！

    # --- Step 1: Sweet Rain のスケジュールページからテキスト取得 ---
    today = datetime.datetime.now()
    current_month = today.month
    current_year = today.year
    # 現在の月のlive番号を計算（例: 2025年5月はlive165）
    # 2025年5月がlive165なので、2025年1月はlive161、2024年1月はlive149と仮定
    base_year = 2024
    base_month = 1
    base_live = 149
    current_live = base_live + (current_year - base_year) * 12 + (current_month - base_month)
    # 来月のlive番号を計算
    next_month = current_month + 1
    next_year = current_year
    if next_month > 12:
        next_month = 1
        next_year += 1
    next_live = base_live + (next_year - base_year) * 12 + (next_month - base_month)
    # 現在の月と来月のURLを取得
    current_url = f"http://jazzsweetrain.com/live{current_live}.html"
    next_url = f"http://jazzsweetrain.com/live{next_live}.html"
    print(f"現在の月のURL: {current_url}")
    print(f"来月のURL: {next_url}")
    # 現在の月のページを取得
    res_current = requests.get(current_url)
    res_current.encoding = 'shift_jis'
    soup_current = BeautifulSoup(res_current.text, "html.parser")
    text_current = soup_current.get_text(separator="\n", strip=True)
    # 来月のページを取得
    res_next = requests.get(next_url)
    res_next.encoding = 'shift_jis'
    soup_next = BeautifulSoup(res_next.text, "html.parser")
    text_next = soup_next.get_text(separator="\n", strip=True)
    # 両方のテキストを結合
    text = text_current + "\n" + text_next

    # --- Step 2: ChatGPTに整形依頼 ---
    prompt = f"""
以下はライブハウス「中野Sweet Rain」のスケジュールページの全文です。
この中から、ライブ日程・開演時間（わかれば）・出演者名・チャージ金額（円）を抽出して、
必ず7列（「日付, 時間, アーティスト名, チャージ金額（¥）, 会場名, 住所, 予約URL」）で出力してください。

重要な注意点：
1. 日付は必ず「YYYY年MM月DD日」の形式で、**月も日も必ず2桁で出力してください**（例：2025年05月01日）
2. 会場名は必ず「Sweet Rain」、住所は必ず「東京都中野区中野5-46-5」、予約URLは各行とも「{current_url}」を入れてください
3. 列が不足している場合は必ず補完してください
4. 5月と6月の両方の情報を必ず含めてください
5. すべてのライブ情報を漏れなく抽出してください
6. テキスト内のすべての日付を確認し、見落としがないようにしてください
7. 日付順に並べてください
8. チャージ金額は「円」を付けて出力してください（例：3300円）

出力形式：
日付, 時間, アーティスト名, チャージ金額（¥）, 会場名（Sweet Rain）, 住所（東京都中野区中野5-46-5）, 予約URL（{current_url}）

全文：
{text}
"""

    print("🧠 ChatGPTに問い合わせ中...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    structured_text = response.choices[0].message.content.strip()
    print("✅ ChatGPT整形結果:\n", structured_text)

    # --- Step 3: テキストをスプレッドシート形式に変換 ---
    rows = []
    for line in structured_text.split("\n"):
        columns = [col.strip() for col in line.split(",")]
        if len(columns) >= 7:
            rows.append(columns)

    # --- Step 4: 重複チェックして書き込み ---
    existing = sheet.get_all_values()
    existing_keys = {(row[0], row[2]) for row in existing}
    new_rows = [row for row in rows if (row[0], row[2]) not in existing_keys]

    for row in new_rows:
        sheet.append_row(row)

    print(f"[Sweet Rain] {len(new_rows)} 件のライブ情報を追加しました。")
