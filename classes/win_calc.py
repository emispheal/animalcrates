
from consts.app_consts import *

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
                        if (symbol == candidate_symbol or symbol in self.wild_symbols) and col_idx - seq_wins[candidate_symbol]["last_col"] <= 1:
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