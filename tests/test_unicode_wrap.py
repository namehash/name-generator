from generator.utils.unicode_wrap import unicode_wrap


def test_wrap():
    assert unicode_wrap('foo bar') == 'foo bar'
    assert unicode_wrap('fóó bar') == 'f(243)(243) bar'
    assert unicode_wrap('fóó 0 bar') == 'f(243)(243) (48) bar'


def test_empty():
    assert unicode_wrap('') == ''
