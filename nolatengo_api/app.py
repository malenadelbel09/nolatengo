from flask import Flask, jsonify, request
import os, json, uuid
from flask_cors import CORS
import utils


app = Flask(__name__)

CORS(app)

app.config['USERS_FILE'] = os.path.join('static', 'users.json')
app.config['CARDS_FILE'] = os.path.join('static', 'cards.json')
app.config['TRADES_FILE'] = os.path.join('static', 'trades.json')
app.config['STORES_FILE'] = os.path.join('static', 'stores.json')
app.config['CARDS_DB'] = os.path.join('static', 'DB', 'cards.xlsx')

utils.convert_xlsx_to_json(app.config['CARDS_DB'])

@app.route('/')
def nlt_home():
    return jsonify({"message": "Welcome to No La Tengo Server!!", "status": "200 OK"})


@app.route("/api/v1/users", methods=["GET", "POST"])
def users_manage():
    path = app.config['USERS_FILE']

    if request.method == "GET":
        if os.path.exists(path):
            with open(path, "r") as file:
                users = json.load(file)  # convert json object to python object
                return jsonify({"users": users, "message": "Users database loaded successfully", "status": "200"})

        return jsonify({"users": None, "message": "Users database empity", "status": "204"})

    if request.method == "POST":
        new_user = request.json

        unique_id = new_user['name'][0] + new_user['lastname'][0] + str(uuid.uuid4())[:8]
        new_user['id'] = unique_id

        if not os.path.exists(path):
            with open(path, "w") as file:
                users = list()
                users.append(new_user)
                json.dump(users, file, indent=4) #python dic to json file
                return jsonify({"user": new_user, "message": "User successfully registered", "status": "201"})

        else:
            with open(path, "r+") as file:
                users = json.load(file)  # load read JSON FILE to dict. #loads read JSON STRING to dict

                if any(user['id'] == new_user['id'] for user in users):
                    return jsonify({"user": new_user['id'], "message": "The userId already exists", "status": "304"})

                elif any(user['email'] == new_user['email'] for user in users):
                    return jsonify({"email": new_user['email'], "message": "This email is in use", "status": "304"})

                else:
                    users.append(new_user)
                    file.seek(0)
                    json.dump(users, file, indent=4)  # dump write dic in json file. #dumps convert dic to json string
                    return jsonify({"user": new_user, "message": "User successfully registered", "status": "201"})


@app.route("/api/v1/users/<user_id>", methods=["GET", "PUT", "DELETE"])
def user_manage(user_id):
    path = app.config['USERS_FILE']

    if request.method == "GET":
        if os.path.exists(path):
            with open(path, "r") as file:
                users = json.load(file)

                if any(user['id'] == user_id for user in users):
                    for user in users:
                        if user['id'] == user_id:
                            return jsonify({"user": user, "userId": user_id, "message": "User loaded successfully", "status": "200"})

                return jsonify({"user": user_id, "message": "The user not exists", "status": "204"})

        return jsonify({"users": None, "message": "User database empity", "status": "204"})

    if request.method == "PUT":
        user_updated = request.json

        if os.path.exists(path):
            with open(path, "r+") as file:
                users = json.load(file)

                if any(user['id'] == user_updated['id'] and user['id'] == user_id for user in users):
                    for user in users:
                        if user['id'] == user_id:
                            users.remove(user)
                            users.append(user_updated)

                            with open(path, "w") as f:
                                json.dump(users, f, indent=4)
                                return jsonify({"user": user_updated, "userId": user_id, "message": "User data updated", "status": "200"})

                return jsonify({"user": user_id, "message": "The userId not exists", "status": "304"})

        return jsonify({"users": None, "message": "Users database empity", "status": "204"})

    if request.method == "DELETE":

        if os.path.exists(path):
            with open(path, "r+") as file:
                users = json.load(file)

                for user in users:
                    if user['id'] == user_id:
                        users.remove(user)

                        with open(path, "w") as f:
                            json.dump(users, f, indent=4)
                            return jsonify({"user": user_id, "message": "User deleted successfully", "status": "200"})

                return jsonify({"user": user_id, "message": "The userId not exists", "status": "304"})

        return jsonify({"users": None, "message": "Users database empity", "status": "204"})



@app.route("/api/v1/users/<user_id>/cards", methods=["GET", "POST", "PUT", "DELETE"])
def user_cards_manage(user_id):
    path = app.config['USERS_FILE']
    cards_path = app.config['CARDS_FILE']
    card_id = request.args.get('card_id')

    if request.method == "GET":
        if os.path.exists(path):
            with open(path, "r") as file:
                users = json.load(file)

                if any(user['id'] == user_id for user in users):
                    for user in users:
                        if user['id'] == user_id:
                            return jsonify({"cards": user['cards'], "userId": user_id, "message": "User cards loaded successfully", "status": "200"})

                return jsonify({"user": user_id, "message": "The user not exists", "status": "204"})

        return jsonify({"users": None, "message": "User database empity", "status": "204"})

    if request.method == "POST":
        new_card = request.json

        if os.path.exists(cards_path):
            with open(cards_path, "r") as file:
                cards = json.load(file)
                if any(card['id'] == new_card['id'] for card in cards):

                    if os.path.exists(path):
                        with open(path, "r+") as file:
                            users = json.load(file)

                            if any(user['id'] == user_id for user in users):
                                for user in users:
                                    if user['id'] == user_id:

                                        if not any(card['id'] == new_card['id'] for card in user['cards']):
                                            user_aux = user
                                            user_aux['cards'].append(new_card)

                                            users.remove(user)
                                            users.append(user_aux)

                                            with open(path, "w") as f:
                                                json.dump(users, f, indent=4)
                                                return jsonify({"card": new_card, "userId": user_id, "message": "Card added", "status": "200"})

                                        return jsonify({"card": new_card, "userId": user_id, "message": "The card already exist", "status": "200"})

                            return jsonify({"user": user_id, "message": "The userId not exists", "status": "304"})

                    return jsonify({"users": None, "message": "Users database empity", "status": "204"})

                return jsonify({"card": new_card['id'], "message": "The cardId not exists", "status": "304"})

    if request.method == "PUT":
        uptaded_card = request.json

        if os.path.exists(path):
            with open(path, "r+") as file:
                users = json.load(file)

                if any(user['id'] == user_id for user in users):
                    for user in users:
                        if user['id'] == user_id:

                            if any(card['id'] == uptaded_card['id'] for card in user['cards']):
                                for card in user['cards']:
                                    if card['id'] == uptaded_card['id']:
                                        user_aux = user
                                        user_aux['cards'].remove(card)
                                        user_aux['cards'].append(uptaded_card)

                                        users.remove(user)
                                        users.append(user_aux)

                                        with open(path, "w") as f:
                                            json.dump(users, f, indent=4)
                                            return jsonify(
                                                {"card": uptaded_card, "userId": user_id, "message": "Updated card amount", "status": "200"})

                            return jsonify({"card": uptaded_card['id'], "userId": user_id, "message": "The card not exist","status": "200"})

                return jsonify({"user": user_id, "message": "The userId not exists", "status": "304"})

        return jsonify({"users": None, "message": "Users database empity", "status": "204"})

    if request.method == "DELETE":

        if os.path.exists(path):
            with open(path, "r+") as file:
                users = json.load(file)

                if any(user['id'] == user_id for user in users):
                    for user in users:
                        if user['id'] == user_id:

                            if any(card['id'] == card_id for card in user['cards']):
                                for card in user['cards']:
                                    if card['id'] == card_id:
                                        user['cards'].remove(card)

                                        with open(path, "w") as f:
                                            json.dump(users, f, indent=4)
                                            return jsonify({"card": card_id, "userId": user_id, "message": "Card deleted successfully", "status": "200"})

                            return jsonify({"card": card_id, "message": "The cardId does not exist", "status": "304"})

                return jsonify({"user": user_id, "message": "The userId not exists", "status": "304"})

        return jsonify({"users": None, "message": "Users database empity", "status": "204"})



@app.route("/api/v1/attachments", methods=["GET"])
def cards_view():
    path = app.config["CARDS_FILE"]
    country = request.args.get('country')
    utils.convert_xlsx_to_json(app.config['CARDS_DB'])

    if request.method == 'GET':
        if os.path.exists(path):
            with open(path, "r") as file:
                cards = json.load(file)

                if country is None:
                    return jsonify({"cards": cards, "message": "Cards loaded successfully", "status": "200"})

                else:
                    country_cards = list()
                    if any(card['country'] == country for card in cards):
                        for card in cards:
                            if card['country'] == country:
                                country_cards.append(card)

                        return jsonify({"cards": country_cards, "message": "Cards loaded successfully", "status": "200"})

                    return jsonify({"country": country, "message": "The requested country does not exist","status": "304"})

        return jsonify({"files": None, "message": "Empty database files", "status": "204 NO CONTENT"})



@app.route("/api/v1/trades", methods=["GET", "POST"])
def trades_manage():
    path = app.config['TRADES_FILE']
    cards_path = app.config['CARDS_FILE']
    users_path = app.config["USERS_FILE"]

    if request.method == "GET":
        if os.path.exists(path):
            with open(path, "r") as file:
                trades = json.load(file)
                return jsonify({"trades": trades, "message": "Trades database loaded successfully", "status": "200"})

        return jsonify({"trades": None, "message": "Trades database empity", "status": "204"})

    if request.method == "POST":
        new_trade = request.json

        unique_id = 'TD' + str(uuid.uuid4())[:8]
        new_trade['tradeId'] = unique_id

        if os.path.exists(users_path):
            with open(users_path, "r") as file:
                users = json.load(file)
                if any(user['id'] == new_trade['publisher'] for user in users):

                    if os.path.exists(cards_path):
                        with open(cards_path, "r") as cards_file:
                            cards = json.load(cards_file)
                            if any(card['id'] == new_trade['offer'] for card in cards) and any(card['id'] == new_trade['request'] for card in cards):

                                if not os.path.exists(path):
                                    with open(path, "w") as f:
                                        trades = list()
                                        trades.append(new_trade)
                                        json.dump(trades, f, indent=4)
                                        return jsonify({"trade": new_trade, "message": "Trade successfully registered", "status": "201"})

                                else:
                                    with open(path, "r+") as fp:
                                        trades = json.load(fp)

                                        if any(trade['tradeId'] == new_trade['tradeId'] for trade in trades):
                                            return jsonify({"trade": new_trade['tradeId'], "message": "The tradeId already exists", "status": "304"})

                                        else:
                                            trades.append(new_trade)
                                            fp.seek(0)
                                            json.dump(trades, fp, indent=4)
                                            return jsonify({"trade": new_trade, "message": "Trade successfully registered", "status": "201"})

                            return jsonify({"offer": new_trade['offer'], "request": new_trade['request'], "message": "The cards ids does not exist","status": "304"})

                return jsonify({"user": new_trade['publisher'], "message": "The userId does not exist", "status": "304"})

        return jsonify({"users": None, "message": "Users database empity", "status": "204"})

@app.route("/api/v1/trades/<trade_id>", methods=["GET", "PUT", "DELETE"])
def trade_manage(trade_id):
    path = app.config['TRADES_FILE']

    if request.method == "GET":
        if os.path.exists(path):
            with open(path, "r") as file:
                trades = json.load(file)

                if any(trade['tradeId'] == trade_id for trade in trades):
                    for trade in trades:
                        if trade['tradeId'] == trade_id:
                            return jsonify({"trade": trade, "tradeId": trade_id, "message": "Trade loaded successfully", "status": "200"})

                return jsonify({"trade": trade_id, "message": "The trade not exists", "status": "204"})

        return jsonify({"trads": None, "message": "Trades database empity", "status": "204"})

    if request.method == "PUT":
        trade_updated = request.json

        if os.path.exists(path):
            with open(path, "r+") as file:
                trades = json.load(file)

                if any(trade['tradeId'] == trade_updated['tradeId'] and trade['tradeId'] == trade_id for trade in trades):
                    for trade in trades:
                        if trade['tradeId'] == trade_id:
                            trades.remove(trade)
                            trades.append(trade_updated)

                            with open(path, "w") as f:
                                json.dump(trades, f, indent=4)
                                return jsonify({"trade": trade_updated, "tradeId": trade_id, "message": "Trade data updated", "status": "200"})

                return jsonify({"tradeId": trade_id, "message": "The tradeId not exists", "status": "304"})

        return jsonify({"trade": None, "message": "Trades database empity", "status": "204"})

    if request.method == "DELETE":

        if os.path.exists(path):
            with open(path, "r+") as file:
                trades = json.load(file)

                for trade in trades:
                    if trade['tradeId'] == trade_id:
                        trades.remove(trade)

                        with open(path, "w") as f:
                            json.dump(trades, f, indent=4)
                            return jsonify({"trade": trade_id, "message": "Trade deleted successfully", "status": "200"})

                return jsonify({"trade": trade_id, "message": "The tradeId not exists", "status": "304"})

        return jsonify({"trades": None, "message": "Trades database empity", "status": "204"})

#puntos de venta
@app.route("/api/v1/stores", methods=["GET", "POST"])
def stores_manage():
    path = app.config['STORES_FILE']

    if request.method == "GET":
        if os.path.exists(path):
            with open(path, "r") as file:
                stores = json.load(file)  # convert json object to python object
                return jsonify({"stores": stores, "message": "stores database loaded successfully", "status": "200"})

        return jsonify({"stores": None, "message": "stores database empity", "status": "204"})

    if request.method == "POST":
        new_store = request.json

        unique_id = new_store['address'][2] + str(uuid.uuid4())[:8]
        new_store['id'] = unique_id

        if not os.path.exists(path):
            with open(path, "w") as file:
                stores = list()
                stores.append(new_store)
                json.dump(stores, file, indent=4) #python dic to json file
                return jsonify({"store": new_store, "message": "store successfully registered", "status": "201"})

        else:
            with open(path, "r+") as file:
                stores = json.load(file)  # load read JSON FILE to dict. #loads read JSON STRING to dict

                if any(store['id'] == new_store['id'] for store in stores):
                    return jsonify({"store": new_store['id'], "message": "The storeId already exists", "status": "304"})

                else:
                    stores.append(new_store)
                    file.seek(0)
                    json.dump(stores, file, indent=4)  # dump write dic in json file. #dumps convert dic to json string
                    return jsonify({"store": new_store, "message": "User successfully registered", "status": "201"})


@app.route("/api/v1/users/<store_id>", methods=["GET", "PUT", "DELETE"])
def store_manage(store_id):
    path = app.config['STORES_FILE']

    if request.method == "GET":
        if os.path.exists(path):
            with open(path, "r") as file:
                stores = json.load(file)

                if any(store['id'] == store_id for store in stores):
                    for store in stores:
                        if store['id'] == store_id:
                            return jsonify({"store": store, "storeId": store_id, "message": "User loaded successfully",
                                            "status": "200"})

                return jsonify({"user": store_id, "message": "The user not exists", "status": "204"})

        return jsonify({"stores": None, "message": "store database empity", "status": "204"})

    if request.method == "PUT":
        store_updated = request.json

        if os.path.exists(path):
            with open(path, "r+") as file:
                stores = json.load(file)

                if any(store['id'] == store_updated['id'] and store['id'] == store_id for store in stores):
                    for store in stores:
                        if store['id'] == store_id:
                            stores.remove(store)
                            stores.append(store_updated)

                            with open(path, "w") as f:
                                json.dump(stores, f, indent=4)
                                return jsonify({"store": store_updated, "userId": store_id, "message": "store data updated",
                                                "status": "200"})

                return jsonify({"store": store_id, "message": "The storeId not exists", "status": "304"})

        return jsonify({"store": None, "message": "stores database empity", "status": "204"})

    if request.method == "DELETE":

        if os.path.exists(path):
            with open(path, "r+") as file:
                stores = json.load(file)

                for store in stores:
                    if store['id'] == store_id:
                        stores.remove(store)

                        with open(path, "w") as f:
                            json.dump(stores, f, indent=4)
                            return jsonify({"store": store_id, "message": "store deleted successfully", "status": "200"})

                return jsonify({"store": store_id, "message": "The storeId not exists", "status": "304"})

        return jsonify({"stores": None, "message": "Stores database empity", "status": "204"})

if __name__ == '__main__':
    app.run(debug=True)

