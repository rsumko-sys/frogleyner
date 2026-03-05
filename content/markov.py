"""Простий N-грамний генератор тексту у стилі Маркова."""
import random
from collections import defaultdict
from typing import List, Dict, Tuple


class MarkovNgram:
    """Навчає на корпусі рядків і генерує нові рядки за N-грамними переходами."""

    def __init__(self, n: int = 2):
        self.n = n
        self._chain: Dict[Tuple, List[str]] = defaultdict(list)
        self._starts: List[Tuple] = []

    def train(self, corpus: List[str]) -> None:
        """Навчання на списку речень."""
        for sentence in corpus:
            tokens = sentence.split()
            if len(tokens) < self.n + 1:
                continue
            for i in range(len(tokens) - self.n):
                key = tuple(tokens[i : i + self.n])
                next_token = tokens[i + self.n]
                self._chain[key].append(next_token)
            self._starts.append(tuple(tokens[: self.n]))

    def generate(self, max_tokens: int = 20) -> str:
        """Генерація одного речення."""
        if not self._starts:
            return "ква."

        key = random.choice(self._starts)
        result = list(key)

        for _ in range(max_tokens - self.n):
            choices = self._chain.get(key)
            if not choices:
                break
            next_token = random.choice(choices)
            result.append(next_token)
            key = tuple(result[-self.n :])

        text = " ".join(result)
        if text and text[-1] not in ".!?…":
            text += "."
        return text
