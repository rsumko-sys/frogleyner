import random
import re
from collections import defaultdict, Counter
from typing import Iterable

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+|[.,!?;:]")


def tokenize(s: str) -> list[str]:
    return TOKEN_RE.findall(s.lower())


class MarkovNgram:
    def __init__(self):
        self.bi: dict[str, Counter[str]] = defaultdict(Counter)
        self.tri: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)

    def train(self, texts: Iterable[str]):
        for t in texts:
            if not (t and t.strip()):
                continue
            toks = ["<s>"] + tokenize(t) + ["</s>"]
            for i in range(len(toks) - 1):
                self.bi[toks[i]][toks[i + 1]] += 1
            for i in range(len(toks) - 2):
                self.tri[(toks[i], toks[i + 1])][toks[i + 2]] += 1

    def _sample(self, counter: Counter) -> str:
        total = sum(counter.values())
        if total <= 0:
            return random.choice(list(counter.keys())) if counter else "</s>"
        r = random.randint(1, total)
        cum = 0
        for k, v in counter.items():
            cum += v
            if cum >= r:
                return k
        return random.choice(list(counter.keys()))

    def generate(self, max_tokens: int = 22) -> str:
        w1, w2 = "<s>", "<s>"
        out: list[str] = []
        for _ in range(max_tokens):
            cand = self.tri.get((w1, w2))
            if cand:
                w3 = self._sample(cand)
            else:
                cand2 = self.bi.get(w2) or self.bi.get(w1)
                if not cand2:
                    break
                w3 = self._sample(cand2)

            if w3 == "</s>":
                break
            out.append(w3)
            w1, w2 = w2, w3

        if not out:
            return "ква. жаба думала. жаба передумала."

        s: list[str] = []
        for w in out:
            s.append(w)
            if w not in ".,!?;:" and random.random() < 0.07:
                s.append("\n")
            if w not in ".,!?;:" and random.random() < 0.05:
                s.append("ква")

        text = " ".join(s)
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        text = re.sub(r"\n\s+", "\n", text).strip()
        return text or "ква. жаба думала. жаба передумала."
