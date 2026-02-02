import unicodedata

import six
from janome.tokenizer import Tokenizer


ja_tokenizer = Tokenizer()


class AllTokenizer(object):
    def __init__(self, do_lower_case=True):
        self.do_lower_case = do_lower_case

    def tokenize(self, text, drop_prun=True, language=None):
        text = convert_to_unicode(text)
        text = self._clean_text(text)
        if language == "ja":
            text = self._tokenize_ja_chars(text)
        else:
            text = self._tokenize_chinese_chars(text)

        orig_tokens = whitespace_tokenize(text)
        split_tokens = []
        for token in orig_tokens:
            if self.do_lower_case:
                token = token.lower()
            split_tokens.extend(self._run_split_on_punc(token, drop_prun))

        output_tokens = whitespace_tokenize(" ".join(split_tokens))
        output_text = "\001" + "\001".join(output_tokens) + "\001" if output_tokens else ""
        return output_text

    def _run_split_on_punc(self, text, drop_prun):
        chars = list(text)
        i = 0
        start_new_word = True
        output = []
        while i < len(chars):
            char = chars[i]
            if _is_punctuation(char):
                if not drop_prun:
                    output.append([char])
                start_new_word = True
            else:
                if start_new_word:
                    output.append([])
                start_new_word = False
                output[-1].append(char)
            i += 1

        return ["".join(x) for x in output]

    def _tokenize_chinese_chars(self, text):
        output = []
        for char in text:
            cp = ord(char)
            if self._is_chinese_char(cp):
                output.append(" ")
                output.append(char)
                output.append(" ")
            else:
                output.append(char)
        return "".join(output)

    def _tokenize_ja_chars(self, text):
        output = [token.surface for token in ja_tokenizer.tokenize(text)]
        return " ".join(output)

    def _is_chinese_char(self, cp):
        if (
            (cp >= 0x4E00 and cp <= 0xA000)
            or (cp >= 0x3400 and cp <= 0x4DBF)
            or (cp >= 0x3040 and cp <= 0x309F)
            or (cp >= 0x30A0 and cp <= 0x30FF)
            or (cp >= 0x31F0 and cp <= 0x31FF)
            or (cp >= 0xAC00 and cp <= 0xD7AF)
            or (cp >= 0x1100 and cp <= 0x11FF)
            or (cp >= 0x3130 and cp <= 0x318F)
            or (cp >= 0x0E00 and cp <= 0x0E7F)
        ):
            return True
        return False

    def _clean_text(self, text):
        output = []
        for char in text:
            cp = ord(char)
            if cp == 0 or cp == 0xFFFD or _is_control(char):
                continue
            if _is_whitespace(char):
                output.append(" ")
            else:
                output.append(char)
        return "".join(output)


def convert_to_unicode(text):
    if six.PY3:
        if isinstance(text, str):
            return text
        if isinstance(text, bytes):
            return text.decode("utf-8", "ignore")
        raise ValueError("Unsupported string type: %s" % (type(text)))
    if six.PY2:
        if isinstance(text, str):
            return text.decode("utf-8", "ignore")
        if isinstance(text, unicode):  # noqa: F821
            return text
        raise ValueError("Unsupported string type: %s" % (type(text)))
    raise ValueError("Not running on Python2 or Python 3?")


def _is_whitespace(char):
    if char == " " or char == "\t" or char == "\n" or char == "\r":
        return True
    cat = unicodedata.category(char)
    return cat == "Zs"


def _is_control(char):
    if char == "\t" or char == "\n" or char == "\r":
        return False
    cat = unicodedata.category(char)
    return cat.startswith("C")


def _is_punctuation(char):
    cp = ord(char)
    if (33 <= cp <= 47) or (58 <= cp <= 64) or (91 <= cp <= 96) or (123 <= cp <= 126):
        return True
    cat = unicodedata.category(char)
    return cat.startswith("P")


def whitespace_tokenize(text):
    text = text.strip()
    if not text:
        return []
    return text.split()
