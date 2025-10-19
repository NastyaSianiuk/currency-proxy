from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Currency Proxy Server is running! ✅ Use /usd_to_byn to get the USD→BYN rate."

@app.route("/usd_to_byn")
def usd_to_byn():
    try:
        url = "https://www.nbrb.by/api/exrates/rates/usd?parammode=2"
        response = requests.get(url, timeout=5)
        data = response.json()
        return jsonify({"Cur_OfficialRate": data["Cur_OfficialRate"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
