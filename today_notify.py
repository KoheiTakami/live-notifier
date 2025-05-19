import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from line_sender import send_line_push

def notify_today():
    load_dotenv()

    # 認証
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Weekly live information").sheet1

    # 今日の日付を取得
    today = datetime.datetime.now().strftime("%Y年%m月%d日")

    # 全データ取得
    rows = sheet.get_all_values()
    headers = rows[0]
    data = rows[1:]

    # 今日のライブを抽出
    todays_events = [row for row in data if row[0] == today]

    if not todays_events:
        print("📭 本日のライブはありません")
        return

    message = f"🎵 本日 {today} のライブ情報\n\n"
    for row in todays_events:
        message += f"🎤 {row[2]} @ {row[4]}（{row[1]}〜 / {row[3]}）\n"

    send_line_push(message)

if __name__ == "__main__":
    notify_today()
