import random

# cascading will just delete elements, and then we'll take number of n missing elements and move the last stop by n idx up, so -, and then take n slice.

class ReelStrip:
    def __init__(self, values):
        self.values = values
        self.last_stop = None

    """
    Generates the reelstop
    """
    def get_stop_result(self, num_elements, stop_idx = None):
        if stop_idx is None:
            # random val in self.values idx
            stop_idx = random.randint(0, len(self.values) - 1)
        self.last_stop = stop_idx

        # wrap-around handling
        return [self.values[i % len(self.values)] for i in range(stop_idx, stop_idx + num_elements)]
    
    """
    Uses the reelstop's last stop to get the result
    """
    def get_stop_result_from_last_stop(self, num_elements):
        return self.get_stop_result(num_elements, self.last_stop)
    
    """
    Moves/climbs the last reelstop up
    """
    def cascade_last_stop_idx(self, move_by):
        # wrap around
        self.last_stop = (self.last_stop - move_by) % len(self.values)

    def reset(self):
        self.last_stop = None