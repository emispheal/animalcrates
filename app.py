

from flask import Flask, jsonify, request
from app_consts import *
from reels import Reels

app = Flask(__name__)

@app.route('/', methods=['GET'])
def default_route():
    return "Hi, server's up yep!"

# no pooling, just make n break
"""
Main spin function to get entire spin from for client
"""
@app.route('/api/spin', methods=['POST'])
def handle_spin_request():
    resp_dict = request.get_json()
    presets = resp_dict.get("presets")

    if presets is None:
        reel = Reels(REELSTRIPS)
    else:
        reel = Reels(REELSTRIPS, [presets])

    reel.do_spin()

    data = {
        'version': '0.1',
        'status': 'success',
        'slot_data': reel.final_data,
    }
    return jsonify(data)

"""
Debug func, prints display to console
"""
def pretty_print(display):
    for j in range(5):
        for i in range(5):
            print(display[i][j], end="\t")
        print("\n", end="")

if __name__ == '__main__':
    app.run(debug=True)

