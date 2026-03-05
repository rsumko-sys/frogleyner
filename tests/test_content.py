import pytest
from content import frog_texts, leiner_quotes_ru, markov

def test_pick():
    assert frog_texts.pick(["a", "b"]) in ["a", "b"]

def test_random_thoughts():
    assert isinstance(frog_texts.RANDOM_THOUGHTS, list)
    assert len(frog_texts.RANDOM_THOUGHTS) > 0

def test_one_word():
    assert isinstance(leiner_quotes_ru.ONE_WORD, list)
    assert len(leiner_quotes_ru.ONE_WORD) > 0

def test_markov_generate():
    m = markov.MarkovNgram()
    m.train(["a b c d e f g"])
    out = m.generate(5)
    assert isinstance(out, str)
    assert len(out.split()) >= 2
