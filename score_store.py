from collections import defaultdict, deque

score_history = defaultdict(lambda: deque(maxlen=100))

def add_score(api_key, score):
    score_history[api_key].append(score)
