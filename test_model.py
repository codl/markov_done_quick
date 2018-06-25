from model import TrigramMarkovChain


def test_tokenize_empty():
    assert TrigramMarkovChain.tokenize('') == tuple()


def test_tokenize():
    assert TrigramMarkovChain.tokenize('foo bar! (baz.)') == (
            'foo',
            ' bar',
            '!',
            ' (',
            'baz',
            '.)')
