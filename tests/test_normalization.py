from generator.normalization import Normalizer


def test_unicode_normalization1():
    name = 'áąółś😀❤'
    normalizer = Normalizer({})
    assert normalizer.normalize(name) == 'aaols'


def test_unicode_normalization2():
    name = 'kožušček'
    normalizer = Normalizer({})
    assert normalizer.normalize(name) == 'kozuscek'


def test_unicode_normalization3():
    name = 'ᴄeo'  # c in small caps
    normalizer = Normalizer({})
    assert normalizer.normalize(name) == 'ceo'


def test_strip_eth():
    name = 'dog.eth'
    normalizer = Normalizer({})
    assert normalizer.normalize(name) == 'dog'


def test_only_valid_characters():
    name = 'dog_cat'
    normalizer = Normalizer({})
    assert normalizer.normalize(name) == 'dogcat'


def test_ignore_short():
    name = 'as'
    normalizer = Normalizer({})
    assert normalizer.normalize(name) == ''


def test_ignore_namehash():
    name = '[59204fd55f432a2d32b0d89aaf9455324dc11671927bedd3d91ce7b7968e5f80]'
    normalizer = Normalizer({})
    assert normalizer.normalize(name) == ''
