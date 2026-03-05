from personalize import display_name, personalize

def test_display_name():
    assert display_name("Іван", False) == "Іван"
    assert display_name("Іван", True) == "Іван (господар)"

def test_personalize():
    text = "Привіт, {name}!"
    assert personalize(text, "Іван", False) == "Привіт, Іван!"
    assert personalize(text, "Іван", True) == "Привіт, Іван (господар)!"
