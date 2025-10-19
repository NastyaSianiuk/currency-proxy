from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import datetime, os

app = Flask(__name__)

# Кэш для сегодняшнего курса
cache_today = None
cache_date = None

@app.route("/usd_to_byn")
def usd_to_byn():
    global cache_today, cache_date

    date_param = request.args.get("date")  # формат YYYY-MM-DD

    # если дата не указана — используем сегодня
    if not date_param:
        date_param = datetime.date.today().strftime("%Y-%m-%d")

    try:
        # Если запрошена сегодняшняя дата и есть кэш — возвращаем кэш
        if date_param == datetime.date.today().strftime("%Y-%m-%d") and cache_today:
            return jsonify({"Cur_OfficialRate": cache_today, "note": "Использован кэш"})

        # URL сайта НБРБ с выбранной датой
        url = f"https://www.nbrb.by/statistics/rates/ratesdaily.asp?ondate={date_param}"

        # делаем запрос к сайту
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # парсим HTML
        soup = BeautifulSoup(response.text, "html.parser")
        table_rows = soup.find_all("tr")

        rate = None
        for row in table_rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                currency_name = cols[0].get_text(strip=True)
                if "Доллар США" in currency_name:
                    # курс в третьей колонке
                    rate_text = cols[2].get_text(strip=True).replace(",", ".")
                    rate = float(rate_text)
                    break

        if rate is None:
            return jsonify({"error": f"Курс USD не найден на {date_param}"}), 404

        # если дата сегодняшняя — обновляем кэш
        if date_param == datetime.date.today().strftime("%Y-%m-%d"):
            cache_today = rate
            cache_date = date_param

        return jsonify({"Cur_OfficialRate": rate})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
