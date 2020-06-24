from stem.porter_stemmer_utils.consonant_vowel_utils import is_vowel, is_consonant
from stem.porter_stemmer_utils.len_flags_utils import len_gt_n, len_eq_n
import cudf


def ends_with_double_constant(string_ser):
    len_flag = len_gt_n(string_ser, 1)

    last_2_chars_equal = string_ser.str.get(-1) == string_ser.str.get(-2)
    is_last_consonant_bool_mask = is_consonant(string_ser, -1)

    return is_last_consonant_bool_mask & last_2_chars_equal & len_flag


def last_char_in(string_ser, characters):
    last_char_strs = string_ser.str.get(-1)
    last_char_ser = cudf.Series(last_char_strs)
    last_char_flag = None
    for char in characters:
        if last_char_flag is not None:
            last_char_flag = last_char_flag | (last_char_ser == char)
        else:
            last_char_flag = last_char_ser == char
    return last_char_flag


def last_char_not_in(string_ser, characters):
    last_char_strs = string_ser.str.get(-1)
    last_char_ser = cudf.Series(last_char_strs)
    last_char_flag = None
    for char in characters:
        if last_char_flag is not None:
            last_char_flag = last_char_flag & (last_char_ser != char)
        else:
            last_char_flag = last_char_ser != char
    return last_char_flag


def ends_cvc(string_ser, mode="NLTK_EXTENSIONS"):
    """Implements condition *o from the paper

    From the paper:

        *o  - the stem ends cvc, where the second c is not W, X or Y
              (e.g. -WIL, -HOP).
    """

    if mode == "NLTK_EXTENSIONS":

        # rule_1
        # len(word) >= 3
        # and self._is_consonant(word, len(word) - 3)
        # and not self._is_consonant(word, len(word) - 2)
        # and self._is_consonant(word, len(word) - 1)
        # and word[-1] not in ("w", "x", "y")

        len_flag = len_gt_n(string_ser, 2)

        first_consonant = is_consonant(string_ser, -3)
        middle_vowel = is_vowel(string_ser, -2)
        last_consonant = is_consonant(string_ser, -1)

        last_char_strs = string_ser.str.get(-1)

        # converting to series to all strings
        last_char_ser = cudf.Series(last_char_strs)
        last_char_flag = None
        for char in ["w", "x", "y"]:
            if last_char_flag is not None:
                last_char_flag = last_char_flag & (last_char_ser != char)
            else:
                last_char_flag = last_char_ser != char

        rule_1 = (
            len_flag & first_consonant & middle_vowel & last_consonant & last_char_flag
        )
        # rule_2
        # self.mode == self.NLTK_EXTENSIONS
        # and len(word) == 2
        # and not self._is_consonant(word, 0)
        # and self._is_consonant(word, 1)
        len_flag = len_eq_n(string_ser, 2)
        first_char = cudf.logical_not(is_consonant(string_ser, 0))
        second_char = is_consonant(string_ser, 1)
        rule_2 = len_flag & first_char & second_char

        return rule_1 | rule_2
    else:
        assert NotImplementedError


def ends_with_suffix(str_ser, suffix):
    return str_ser.str.endswith(suffix)