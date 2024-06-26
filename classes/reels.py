


from consts.app_consts import *
from classes.reel_strip import ReelStrip
import copy
from classes.win_calc import WinCalc

# presets format = [[1,2,3,38,2], [4,52,26,2,4], [7,8,99,3,11]]
# if no presets are given or it runs out, generate random stops
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

    """
    Does the entire spin sequence here, the main spin function
    """
    def do_spin(self, presets = None):
        while self.rounds_left > 0 or self.cur_mode == "cascade":
            print(self.rounds_left, self.cur_mode, self.cur_scatter_wins, self.in_freespin)
            
            # cascade is a follow up and doesnt use up rounds
            if self.cur_mode == "base":
                self.rounds_left -= 1
            
            # default next-mode is base
            self.next_mode = "base"
            
            if self.cur_mode == "base":
                self.cur_display = self.get_base_display(self.presets)
                # DEBUG: print stops
                # for rs in self.reelstrips:
                #     print(rs.last_stop)
            else:
                self.cur_display = self.get_next_cascade_display()

            # calc wins
            win_calc = WinCalc(DONT_CASCADE, SCATTER_SYMBOLS, WILD_SYMBOLS)
            cur_wins = win_calc.calc_wins(self.cur_display)
            self.cur_seq_wins = cur_wins["seq_wins"]
            self.cur_scatter_wins = cur_wins["scatter_wins"]

            if self.cur_seq_wins:
                self.next_mode = "cascade"

            # scatter awards 1 round for trigger and retrigger
            if self.cur_scatter_wins:
                if self.in_freespin:
                    self.rounds_left += 1
                else:
                    self.in_freespin = True
                    self.rounds_left += 1

            # calculate total pay for the one round of cascade/base
            # also groups win positions 
            total_pay = 0
            cascade_positions = set()
            for symbol in self.cur_seq_wins:
                total_pay += self.cur_seq_wins[symbol]["pay"]
                cascade_positions = cascade_positions.union(self.cur_seq_wins[symbol]["positions"])

            cascade_positions = list(cascade_positions)

            # gets scatter win positions
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
    
    """     
    Gets the base display, a normal spin
    """
    def get_base_display(self, presets = None):
        self.reset()
        
        cur_preset = None
        if presets:
            cur_preset = self.presets.pop()

        if cur_preset is not None and len(cur_preset) > 0:
            print("Using preset: ", cur_preset)
            return [reelstrip.get_stop_result(ROWS, value) for reelstrip, value in zip(self.reelstrips, cur_preset)]
        else:
            return [reelstrip.get_stop_result(ROWS) for reelstrip in self.reelstrips]
    
    """
    Cascades the display and gets the new symbols
    """
    def get_next_cascade_display(self):

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
            self.cur_display[i] = to_add[i] + self.cur_display[i]

        return self.cur_display

    """
    Resets reelstrips
    """
    def reset(self):
        for reelstrip in self.reelstrips:
            reelstrip.reset()