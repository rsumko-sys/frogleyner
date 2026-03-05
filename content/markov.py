import random
from collections import defaultdict
from typing import List


class MarkovNgram:
    """Simple n-gram Markov chain for text generation."""

    def __init__(self, n: int = 2):
        self.n = n
        self._model: dict = defaultdict(list)
        self._starts: List[tuple] = []

    def train(self, corpus: List[str]) -> None:
        for text in corpus:
            tokens = text.split()
            if len(tokens) < self.n + 1:
                if tokens:
                    self._starts.append(tuple(tokens))
                continue
            for i in range(len(tokens) - self.n):
                key = tuple(tokens[i : i + self.n])
                self._model[key].append(tokens[i + self.n])
            self._starts.append(tuple(tokens[: self.n]))

    def generate(self, max_tokens: int = 20) -> str:
        if not self._starts:
            return "ква."

        start = random.choice(self._starts)
        result = list(start)

        for _ in range(max_tokens - len(start)):
            key = tuple(result[-self.n :])
            if key not in self._model or not self._model[key]:
                break
            next_token = random.choice(self._model[key])
            result.append(next_token)

        return " ".join(result)
