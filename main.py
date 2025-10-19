from flask import Flask, jsonify, request
import requests, os

app = Flask(__name__)

# Кэш для последнего курса
last_rate = None

@app.route("/usd_to_byn")
def usd_to_byn():
    global last_rate

    # получаем параметр даты
    date = request.args.get("date")  # формат "YYYY-MM-DD"
    try:
        # URL к API НБРБ
        url = "https://api.nbrb.by/exrates/rates/usd?parammode=2"
        if date:
            url += f"&ondate={date}"

        # делаем запрос к НБРБ
        response = requests.get(url, timeout=10)
        data = response.json()

        # обновляем кэш только если получили курс
        last_rate = data.get("Cur_OfficialRate")
        return jsonify({"Cur_OfficialRate": last_rate})

    except Exception as e:
        # если ошибка — возвращаем курс из кэша
        if last_rate is not None:
            return jsonify({"Cur_OfficialRate": last_rate, "note": "Использован кэш, НБРБ недоступен"})
        else:
            return jsonify({"error": "НБРБ недоступен и кэш пуст", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
