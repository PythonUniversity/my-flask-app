from flask import Flask, jsonify
from ZADANIE2.zadanie2 import find_crossovers, calculate_total_btc_traded

app = Flask(__name__)

@app.route('/find_crossovers', methods=['GET'])
def get_crossovers():
    crossovers = find_crossovers()
    return jsonify(crossovers)

@app.route('/calculate_total_btc_traded', methods=['GET'])
def get_total_btc_traded():
    total_traded = calculate_total_btc_traded()
    return jsonify(total_traded)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
