import unicodedata
import pickle
import logging
import random

logger = logging.getLogger(__name__)


class TrigramMarkovChain(object):
    def __init__(self):
        # trigrams format:
        # key is (word_1, word_2)
        # value is a dict with key = word_3 and value = frequency
        # None in either of these word values means past the ends of the string
        # so word_1 = None and word_2 = None gives us words that begin
        # a string
        # and word_3 = None means the string ends there
        # word_3 may start with a space. if word_3 does not start with a
        # space then it should be appended to the preceding string without
        # a space
        self.trigrams = dict()

    @classmethod
    def tokenize(cls, string):
        tokens = list()
        buf = ""
        SYMBOL = 1
        ALPHANUM = 2
        current_token = None
        for char in string:
            category = unicodedata.category(char)

            if char == " ":
                char_type = None
            elif category[0] in "LN":
                char_type = ALPHANUM
            else:
                char_type = SYMBOL

            if char_type == current_token:
                buf += char
            else:
                if current_token:
                    tokens.append(buf)
                    buf = ''
                current_token = char_type
                buf += char

        if buf.strip() != '':
            tokens.append(buf)

        return tuple(tokens)

    def ingest(self, string):
        tokens = self.tokenize(string)
        prev_tokens = (None, None)

        tokens += (None,)
        for token in tokens:
            if prev_tokens not in self.trigrams:
                self.trigrams[prev_tokens] = dict()
            if token not in self.trigrams[prev_tokens]:
                self.trigrams[prev_tokens][token] = 0
            self.trigrams[prev_tokens][token] += 1

            if token is not None:
                prev_tokens = (prev_tokens[1], token.strip().lower())

    def load(self, path):
        with open(path, 'rb') as f:
            self.trigrams = pickle.load(f)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.trigrams, f)

    @classmethod
    def from_file(cls, path):
        instance = cls()
        instance.load(path)
        return instance

    def next_token(self, token, token_2):
        candidates = self.trigrams.get((token, token_2), None)
        if not candidates:
            logger.warning("Couldn't find trigram for tokens ('%s', '%s')", token, token_2)
            return None

        pool = list()
        for key in candidates.keys():
            for _ in range(candidates[key]):
                pool.append(key)

        return random.choice(pool)

    def make_phrase(self):
        string = ""
        prev_tokens = (None, None)
        while True:
            token = self.next_token(*prev_tokens)
            if token is None:
                return string
            string += token
            prev_tokens = (prev_tokens[1], token.strip().lower())
