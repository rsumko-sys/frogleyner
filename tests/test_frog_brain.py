from frog_brain import frog_fact, frog_joke

def test_frog_fact():
    fact = frog_fact()
    assert isinstance(fact, str)
    assert len(fact) > 0

def test_frog_joke():
    joke = frog_joke()
    assert isinstance(joke, str)
    assert len(joke) > 0
