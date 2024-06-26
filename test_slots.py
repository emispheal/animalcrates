"""
Unit tests for slots_app.py
"""
# import pytest
from app import app
import json


# sanity check for the server/testing
def test_default_route():
    with app.test_client() as c:
        response = c.get('/')
        assert response.data == b'Hi, server\'s up yep!'

# just a random spin, testing response
def test_handle_random_spin_request():
    with app.test_client() as c:
        response = c.post('/api/spin', json={"presets": []})
        data_dict = json.loads(response.data)
        assert data_dict["status"] == "success"
        slot_data = data_dict["slot_data"]
        assert len(slot_data) > 0
        first_round = slot_data[0]
        assert "display" in first_round
        assert "cascade_positions" in first_round
        assert "scatter_win_positions" in first_round
        assert "cur_mode" in first_round
        assert "next_mode" in first_round
        assert "rounds_left" in first_round
        assert "pay" in first_round

# test a small win one cascade
def test_small_win():
    with app.test_client() as c:
        response = c.post('/api/spin', json={"presets": [0, 1, 2, 3, 4]})
        data_dict = json.loads(response.data)
        slot_data = data_dict["slot_data"]
        assert len(slot_data) == 2
        assert slot_data[0]["cascade_positions"] == [[2, 0], [0, 2], [1, 3], [3, 2]]
        assert slot_data[0]["scatter_win_positions"] == []
        assert slot_data[0]["cur_mode"] == "base"
        assert slot_data[0]["next_mode"] == "cascade"
        assert slot_data[0]["rounds_left"] == 0
        assert slot_data[0]["pay"] == 70
        assert slot_data[0]["display"] == [
            ['bear', 'bunny', 'dog', 'bunny', 'bear'], 
            ['pig', 'bear', 'vulture', 'dog', 'vulture'], 
            ['dog', 'vulture', 'beetle', 'bunny', 'beetle'], 
            ['bunny', 'pig', 'dog', 'pig', 'bunny'], 
            ['beetle', 'vulture', 'vulture', 'bear', 'pig']
        ]
        assert slot_data[1]["cascade_positions"] == []
        assert slot_data[1]["scatter_win_positions"] == []
        assert slot_data[1]["cur_mode"] == "cascade"
        assert slot_data[1]["next_mode"] == "base"
        assert slot_data[1]["rounds_left"] == 0
        assert slot_data[1]["pay"] == 0

# check that wild win bridges symbols and actually acts as a wild
def test_wild_win():
    with app.test_client() as c:
        response = c.post('/api/spin', json={"presets": [15, 8, 7, 0, 0]})
        data_dict = json.loads(response.data)
        slot_data = data_dict["slot_data"]
        assert len(slot_data) == 2
        # make sure the pig is part of a win even with no pig in second col
        assert slot_data[0]["cascade_positions"] == [[2, 3], [0, 1], [2, 2], [3, 4], [2, 1], [0, 0], [1, 3], [3, 0]]
        assert slot_data[0]["display"] == [
            ['pig', 'bear', 'vulture', 'dog', 'vulture'], 
            ['dog', 'vulture', 'bunny', 'eagle', 'bunny'], 
            ['bunny', 'bear', 'pig', 'pig', 'beetle'], 
            ['pig', 'dog', 'beetle', 'bunny', 'pig'], 
            ['dog', 'bear', 'dog', 'beetle', 'beetle']
        ]

# scatter respin testing
def test_retrigger():
    with app.test_client() as c:
        response = c.post('/api/spin', json={"presets": [34, 30, 13, 19, 20]})
        data_dict = json.loads(response.data)
        slot_data = data_dict["slot_data"]
        # 3 frogs, but no retrigger since its cascading/theres a win
        # make sure frogs arent part of win yet 
        assert slot_data[0]["display"] == [
            ['dog', 'frog', 'beetle', 'bear', 'bunny'], 
            ['bunny', 'dog', 'bunny', 'pig', 'pig'], 
            ['bear', 'frog', 'bunny', 'beetle', 'bear'], 
            ['bunny', 'frog', 'pig', 'pig', 'vulture'], 
            ['beetle', 'pig', 'beetle', 'beetle', 'bunny']
        ]
        assert [0,1] not in slot_data[0]["scatter_win_positions"]
        assert [0,1] not in slot_data[0]["cascade_positions"]
        assert slot_data[0]["rounds_left"] == 0
        assert slot_data[0]["next_mode"] == "cascade"
        # eventually, there are no more wins, there should be 1 respin awarded
        for round in slot_data:
            if round["next_mode"] == "base" and len(round["scatter_win_positions"]) >= 3:
                assert round["rounds_left"] == 1
                assert round["cascade_positions"] == []

# wrap around reelstrip carding
def test_wrap_around():
    with app.test_client() as c:
        response = c.post('/api/spin', json={"presets": [0, 0, 0, 0, 0]})
        data_dict = json.loads(response.data)
        slot_data = data_dict["slot_data"]
        assert len(slot_data) == 2
        # need the correct display according to reelstrips for wrap around
        assert slot_data[0]["display"] == [
            ['bear', 'bunny', 'dog', 'bunny', 'bear'], 
            ['pig', 'pig', 'bear', 'vulture', 'dog'], 
            ['bear', 'vulture', 'dog', 'vulture', 'beetle'], 
            ['pig', 'dog', 'beetle', 'bunny', 'pig'], 
            ['dog', 'bear', 'dog', 'beetle', 'beetle']
        ]
        # dog frog beetle should cascade down, from the other end of reelstrip
        assert slot_data[1]["display"] == [
            ['dog', 'frog', 'beetle', 'bunny', 'bunny'], 
            ['dog', 'bunny', 'pig', 'pig', 'vulture'], 
            ['bear', 'pig', 'vulture', 'vulture', 'beetle'], 
            ['beetle', 'pig', 'beetle', 'bunny', 'pig'], 
            ['bunny', 'beetle', 'bear', 'beetle', 'beetle']
        ]