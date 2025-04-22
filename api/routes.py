from flask import Blueprint, jsonify, request
import requests

api_bp = Blueprint('api', __name__)

EXTERNAL_API_URL = "https://countriesnow.space/api/v0.1/countries/population"

@api_bp.route('/population', methods=['GET'])
def get_population():
    """
    Проксі-ендпоінт для отримання даних про населення зі стороннього API.
    Може приймати параметри country, start_year, end_year.
    """
    try:
        # Отримати всі дані зі стороннього API
        response = requests.get(EXTERNAL_API_URL)
        response.raise_for_status()
        data = response.json().get('data', [])

        # Фільтрація за параметрами (якщо передані)
        country = request.args.get('country')
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)

        if country:
            data = [item for item in data if item['country'].lower() == country.lower()]

        # Додаткова фільтрація за роками
        if start_year or end_year:
            for item in data:
                item['populationCounts'] = [
                    p for p in item['populationCounts']
                    if (not start_year or p['year'] >= start_year) and (not end_year or p['year'] <= end_year)
                ]

        return jsonify({"status": "success", "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
