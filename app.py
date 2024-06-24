

from flask import Flask, jsonify
import random
import copy

app = Flask(__name__)

ROWS = 5
COLS = 5

MIN_CONSECUTIVE = 3
MIN_SCATTER = 3

DONT_CASCADE = ["frog"]
WILD_SYMBOLS = ["eagle"]
SCATTER_SYMBOLS = ["frog"]

["bear", "beetle", "bunny", "pig", "vulture", "frog", "dog", "eagle"]


PAYTABLE = {
    'S': [0] * 25,
    'bear': [0, 0, 5, 20, 40, 80],
    'beetle': [0, 0, 25, 80, 150, 300],
    'bunny': [0, 0, 15, 50, 80, 150],
    'pig': [0, 0, 15, 50, 80, 150],
    'vulture': [0, 0, 10, 40, 70, 100],
    'frog': [0, 0, 10, 40, 70, 100],
    'dog': [0, 0, 10, 40, 70, 100],
    'eagle': [0, 0, 10, 40, 70, 100],
}

# no pooling, just make n break

# cascading will just delete elements, and then we'll take number of n missing elements and move the last stop by n idx up, so -, and then take n slice.

class ReelStrip:
    def __init__(self, values):
        self.values = values
        self.last_stop = None

    def get_stop_result(self, num_elements, stop_idx = None):
        if stop_idx is None:
            # random val in self.values idx
            stop_idx = random.randint(0, len(self.values) - 1)
        self.last_stop = stop_idx

        # wrap-around handling
        return [self.values[i % len(self.values)] for i in range(stop_idx, stop_idx + num_elements)]
    
    def get_stop_result_from_last_stop(self, num_elements):
        return self.get_stop_result(num_elements, self.last_stop)
    
    def cascade_last_stop_idx(self, move_by):
        # wrap around
        self.last_stop = (self.last_stop - move_by) % len(self.values)

    def reset(self):
        self.last_stop = None

# presets format = [[1,2,3,38,2], [4,52,26,2,4], [7,8,99,3,11]]
# unused presets ignored.
class Reels:
    def __init__(self, reelstrips, presets = None):
        self.reelstrips = [ReelStrip(reelstrip) for reelstrip in reelstrips]
        self.presets = presets
        self.rounds_left = 1
        self.in_freespin = False
        self.next_mode = "base"
        self.cur_mode = "base"
        self.cur_display = None
        self.cur_seq_wins = None
        self.cur_scatter_wins = None
        self.final_data = []

    def do_spin(self, presets = None):
        while self.rounds_left > 0 or self.cur_mode == "cascade":
            print(self.rounds_left, self.cur_mode, self.cur_scatter_wins)
            
            # cascade is a follow up
            if self.cur_mode == "base":
                self.rounds_left -= 1
            
            # default next-mode is base
            self.next_mode = "base"
            
            if self.cur_mode == "base":
                self.cur_display = self.get_base_display(self.presets)
                for rs in self.reelstrips:
                    print(rs.last_stop)
            else:
                self.cur_display = self.get_next_cascade_display()

            win_calc = WinCalc(DONT_CASCADE, SCATTER_SYMBOLS, WILD_SYMBOLS)
            cur_wins = win_calc.calc_wins(self.cur_display)
            self.cur_seq_wins = cur_wins["seq_wins"]
            self.cur_scatter_wins = cur_wins["scatter_wins"]

            if self.cur_seq_wins:
                self.next_mode = "cascade"

            if self.cur_scatter_wins:
                if self.in_freespin:
                    self.rounds_left += 1
                else:
                    self.in_freespin = True
                    self.rounds_left += 1

            total_pay = 0
            cascade_positions = set()
            for symbol in self.cur_seq_wins:
                total_pay += self.cur_seq_wins[symbol]["pay"]
                cascade_positions = cascade_positions.union(self.cur_seq_wins[symbol]["positions"])

            cascade_positions = list(cascade_positions)


            scatter_positions = []
            for symbol in self.cur_scatter_wins:
                scatter_positions += self.cur_scatter_wins[symbol]["positions"]


            self.final_data.append(
                {
                    'display': copy.deepcopy(self.cur_display),
                    'cascade_positions': cascade_positions,
                    'scatter_win_positions': scatter_positions,
                    'cur_mode': self.cur_mode,
                    'next_mode': self.next_mode,
                    'rounds_left': self.rounds_left,
                    'pay': total_pay,
                }
            )

            self.cur_mode = self.next_mode
            

    def get_base_display(self, presets = None):
        self.reset()
        
        cur_preset = None
        if presets:
            cur_preset = self.presets.pop()

        if cur_preset is not None:
            print("Using preset: ", cur_preset)
            return [reelstrip.get_stop_result(ROWS, values) for reelstrip, values in zip(self.reelstrips, cur_preset)]
        else:
            return [reelstrip.get_stop_result(ROWS) for reelstrip in self.reelstrips]
        
    def get_next_cascade_display(self):
        # print("Getting next cascade display")
        # replace all cascaded positions with dummy Xs
        for symbols in self.cur_seq_wins:
            if self.cur_seq_wins[symbols]["cascade"]:
                for pos in self.cur_seq_wins[symbols]["positions"]:
                    col_idx = pos[0]
                    row_idx = pos[1]
                    self.cur_display[col_idx][row_idx] = "X"
        
        # remove all Xs from display
        self.cur_display = [[symbol for symbol in col if symbol != "X"] for col in self.cur_display]

        to_add = []

        for col_idx, col in enumerate(self.cur_display):
            if len(col) < ROWS:
                num_missing_rows = ROWS - len(col)
                self.reelstrips[col_idx].cascade_last_stop_idx(num_missing_rows)
                to_add.append(self.reelstrips[col_idx].get_stop_result_from_last_stop(num_missing_rows))
            else:
                to_add.append([])

        for i in range(COLS):
            self.cur_display[i] += to_add[i]

        return self.cur_display


    
    def reset(self):
        for reelstrip in self.reelstrips:
            reelstrip.reset()


class WinCalc:
    def __init__(self, cascade_exceptions = [], scatter_symbols = [], wild_symbols = []):
        self.cascade_exceptions = cascade_exceptions
        self.scatter_symbols = scatter_symbols
        self.wild_symbols = wild_symbols

    """
    Iterative calc ways seq_wins

    returns: 
    {

    }
    """
    def calc_wins(self, display):

        # normal sequential seq_wins
        seq_wins = {}
        
        for col_idx, col in enumerate(display):
            if col_idx == 0:
                # first reel should be all candidates, no wilds by reelstrip design for this game, ignore scatters
                for row_idx, symbol in enumerate(col):
                    if symbol not in self.scatter_symbols:
                        # cascade True means it should pop.
                        should_cascade = symbol not in self.cascade_exceptions
                        
                        if symbol not in seq_wins:
                            seq_wins[symbol] = {"positions": [(col_idx, row_idx)], "occurences_per_col": [1], "length": 1, "last_col": col_idx, "cascade": should_cascade}
                        else:
                            seq_wins[symbol]["positions"].append((col_idx, row_idx))
                            seq_wins[symbol]["occurences_per_col"][-1] += 1
            else:
                # not the first reel
                for row_idx, symbol in enumerate(col):
                    for candidate_symbol in seq_wins:
                        if (symbol == candidate_symbol or symbol in self.wild_symbols) and seq_wins[candidate_symbol]["last_col"] - col_idx <= 1:
                            seq_wins[candidate_symbol]["positions"].append((col_idx, row_idx))

                            if seq_wins[candidate_symbol]["last_col"] != col_idx:
                                seq_wins[candidate_symbol]["length"] += 1
                                seq_wins[candidate_symbol]["last_col"] = col_idx
                                seq_wins[candidate_symbol]["occurences_per_col"].append(1)
                            else:
                                seq_wins[candidate_symbol]["occurences_per_col"][-1] += 1

        # prune seq_wins
        symbols_to_remove = []
        for symbol in seq_wins:
            if seq_wins[symbol]["length"] < MIN_CONSECUTIVE:
                # seq_wins.pop(symbol)
                symbols_to_remove.append(symbol)
            else:
                # calculate and clean up
                num_ways = 1
                for occurences in seq_wins[symbol]["occurences_per_col"]:
                    num_ways *= occurences
                seq_wins[symbol]["num_ways"] = num_ways
                seq_wins[symbol].pop("occurences_per_col")
                seq_wins[symbol].pop("last_col")
                seq_wins[symbol]["pay"] = seq_wins[symbol]["num_ways"] * PAYTABLE[symbol][seq_wins[symbol]["length"]]

        # remove
        for symbol in symbols_to_remove:
            seq_wins.pop(symbol)

        scatter_wins = {}
        # just iterate again for scatters to not complicate loop, small n*n
        # only want scatter wins if no cascades to not  double up
        if not seq_wins:
            for col_idx, col in enumerate(display):
                for row_idx, symbol in enumerate(col):
                    if symbol in self.scatter_symbols:
                        if symbol not in scatter_wins:
                            scatter_wins[symbol] = {"positions": [(col_idx, row_idx)], "occurences": 1, "cascade": False}
                        else:
                            scatter_wins[symbol]["positions"].append((col_idx, row_idx))
                            scatter_wins[symbol]["occurences"] += 1
            
            # prune scatter_wins
            symbols_to_remove = []
            for symbol in scatter_wins:
                if scatter_wins[symbol]["occurences"] < MIN_SCATTER:
                    # scatter_wins.pop(symbol)
                    symbols_to_remove.append(symbol)
            
            for symbol in symbols_to_remove:
                scatter_wins.pop(symbol)




        # keep them separate
        return {"seq_wins": seq_wins, "scatter_wins": scatter_wins}

def get_reelstrips():
    ["bear", "beetle", "bunny", "pig", "vulture", "frog", "dog", "eagle"]

    return [
        ["bear","bunny","dog","bunny","bear","bunny","bunny","dog","beetle","bunny","bear","pig","dog","beetle","pig","pig","bear","vulture","dog","vulture","dog","pig","bear","bunny","beetle","dog","bear","dog","beetle","beetle","dog","pig","bear","pig","dog","frog","beetle"],
        ["pig","pig","bear","vulture","dog","vulture","beetle","pig","dog","vulture","bunny","eagle","bunny","bear","bunny","beetle","bunny","bear","pig","pig","bunny","beetle","pig","bear","dog","beetle","beetle","bear","pig","bear","bunny","dog","bunny"],
        ["bear","vulture","dog","vulture","beetle","bunny","beetle","bunny","bear","pig","pig","beetle","dog","bear","frog","bunny","beetle","bear","bunny","bear","pig","pig","beetle","pig","pig","vulture","dog","bunny","bear","pig","pig","beetle","dog","eagle","vulture","beetle","pig","dog","vulture","beetle","beetle","vulture","bear","vulture","pig","bear","bear","pig"],
        ["pig","dog","beetle","bunny","pig","dog","pig","bunny","pig","vulture","dog","bear","bunny","beetle","dog","dog","beetle","vulture","beetle","bunny","frog","pig","pig","vulture","eagle","vulture","dog","bear","beetle","bunny","pig","beetle","pig","pig","vulture","dog","pig","bunny","beetle","dog","bunny","pig","bunny","beetle"],
        ["dog","bear","dog","beetle","beetle","vulture","vulture","bear","pig","pig","beetle","bear","dog","vulture","bunny","beetle","dog","dog","beetle","vulture","beetle","pig","beetle","beetle","bunny","eagle","beetle","pig","pig","vulture","dog","pig","bunny","beetle"],
    ]

@app.route('/api/data', methods=['GET'])
def get_spin_request():
    reel = Reels(get_reelstrips(), [[17,23,18,13,23]])
    reel.do_spin()

    data = {
        'message': 'Hello, World!',
        'status': 'success',
        'slot_data': reel.final_data,
    }
    return jsonify(data)

@app.route('/api/test', methods=['GET'])
def get_some_request():

    data = {
        'message': 'Hello, World! testing',
        'status': 'success',
    }
    return jsonify(data)

@app.route('/', methods=['GET'])
def default_route():
    return "Hello"

def pretty_print(display):
    for j in range(5):
        for i in range(5):
            print(display[i][j], end="\t")
        print("\n", end="")

if __name__ == '__main__':
    app.run(debug=True)
    # reel = Reels(get_reelstrips())
    # print(reel.get_base_display())
    # pretty_print(reel.get_base_display(reel.presets))
    # cur_display = reel.get_base_display(reel.presets)
    # wincalc = WinCalc(DONT_CASCADE, SCATTER_SYMBOLS, WILD_SYMBOLS)
    # print(wincalc.calc_wins(cur_display))

    # reel = Reels(get_reelstrips(), [[17,23,18,13,23]])
    # reel.do_spin()
    # print(reel.final_data)


# TESTS: check wrawp around, check scatter only at end, check scatter retrigger, check freespins, check multi presets