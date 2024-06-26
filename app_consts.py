ROWS = 5
COLS = 5

MIN_CONSECUTIVE = 3
MIN_SCATTER = 3

DONT_CASCADE = ["frog"]
WILD_SYMBOLS = ["eagle"]
SCATTER_SYMBOLS = ["frog"]

["bear", "beetle", "bunny", "pig", "vulture", "frog", "dog", "eagle"]

REELSTRIPS = [
    ["bear","bunny","dog","bunny","bear","bunny","bunny","dog","beetle","bunny","bear","pig","dog","beetle","pig","pig","bear","vulture","dog","vulture","dog","pig","bear","bunny","beetle","dog","bear","dog","beetle","beetle","dog","pig","bear","pig","dog","frog","beetle"],
    ["pig","pig","bear","vulture","dog","vulture","beetle","pig","dog","vulture","bunny","eagle","bunny","bear","bunny","beetle","bunny","bear","pig","pig","bunny","beetle","pig","bear","dog","beetle","beetle","bear","pig","bear","bunny","dog","bunny"],
    ["bear","vulture","dog","vulture","beetle","bunny","beetle","bunny","bear","pig","pig","beetle","dog","bear","frog","bunny","beetle","bear","bunny","bear","pig","pig","beetle","pig","pig","vulture","dog","bunny","bear","pig","pig","beetle","dog","eagle","vulture","beetle","pig","dog","vulture","beetle","beetle","vulture","bear","vulture","pig","bear","bear","pig"],
    ["pig","dog","beetle","bunny","pig","dog","pig","bunny","pig","vulture","dog","bear","bunny","beetle","dog","dog","beetle","vulture","beetle","bunny","frog","pig","pig","vulture","eagle","vulture","dog","bear","beetle","bunny","pig","beetle","pig","pig","vulture","dog","pig","bunny","beetle","dog","bunny","pig","bunny","beetle"],
    ["dog","bear","dog","beetle","beetle","vulture","vulture","bear","pig","pig","beetle","bear","dog","vulture","bunny","beetle","dog","dog","beetle","vulture","beetle","pig","beetle","beetle","bunny","eagle","beetle","pig","pig","vulture","dog","pig","bunny","beetle"],
]

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