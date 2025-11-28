import hashlib

from flask import Flask, request, jsonify
from db import TariffPlan, API_db

app = Flask(__name__)
@app.route('/api', methods=['POST'])
def api():
    try:
        data = request.get_json()
        res = API_db().check_api(data['api_key'])
        if res:
            #реализовать через пост запрос отправку на наш продукт, который вернёт данные в json виде или как-нибудь реализовать красиво через pdf
            return 'Доступ разрешён'
        return jsonify({'error': 'Access denied'})
    except Exception as e:
        return jsonify({'error': 'Access denied'})


@app.route('/api_key_get', methods=['GET'])
def api_key_get():
    tarif_name = TariffPlan().get_user_info('Имя_пользователя')[2]

    permission = TariffPlan().get_tariff_settings(tariff_name=tarif_name)
    if permission:
        try:
            from api_generate import generate_api_key
            # через сессиии или через куки достаём имя пользователя
            user_login = 'имя_пользователя'
            user_pswd = TariffPlan().get_password(user_login)
            print(566)
            api_key = generate_api_key('dasewqdsadwq23')
            APIcheck = API_db().check_api(api_key)
            if APIcheck is False:
                API_db().add_api_key(api_key)
                return jsonify({'Your api key:': api_key})
            else:
                while APIcheck is True:
                    api_key = generate_api_key('dasewqdsadwq23')
                    APIcheck = API_db().check_api(api_key)
                API_db().add_api_key(api_key)
                return jsonify({'Your api key:': api_key})
        except Exception as e:
            return jsonify({'error': 'Access denied'})
    else:
        return jsonify({'error': 'Access denied'})


if __name__ == '__main__':
    TariffPlan()
    API_db()
    app.run(debug=True)