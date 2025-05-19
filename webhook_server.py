from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    body = request.get_json()
    print("📩 Webhook受信データ:")
    print(json.dumps(body, indent=2, ensure_ascii=False))

    try:
        events = body["events"]
        for event in events:
            user_id = event["source"]["userId"]
            print(f"✅ 取得した userId: {user_id}")
    except Exception as e:
        print("❌ パース失敗:", e)

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5001)
