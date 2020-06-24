import cudf
import numpy as np
from cuml.preprocessing.text.stem.porter_stemmer_utils.len_flags_utils import len_eq_n, len_gt_n


def test_len_gt_n():
    word_strs = cudf.Series(["a", "abcd", "abc", "abcd"])
    got = len_gt_n(word_strs, 3).values.get()
    expect = np.asarray([False, True, False, True])
    np.testing.assert_array_equal(got, expect)


def test_len_eq_n():
    word_strs = cudf.Series(["a", "abcd", "abc", "abcd"])
    got = len_eq_n(word_strs, 3).values.get()
    expect = np.asarray([False, False, True, False])
    np.testing.assert_array_equal(got, expect)