import cudf
from cuml.preprocessing.text.stem.porter_stemmer_utils.suffix_utils import get_stem_series, replace_suffix


def test_get_stem_series():
    word_strs = cudf.Series(["ihop", "packit", "mishit", "crow", "girl", "boy"])
    can_replace_mask = cudf.Series([True, True, True, False, False, False])

    expect = ["ih", "pack", "mish", "crow", "girl", "boy"]
    got = get_stem_series(word_strs, suffix_len=2, can_replace_mask=can_replace_mask)
    assert sorted(list(got.to_pandas().values)) == sorted(expect)


def test_replace_suffix():
    # test 'ing' -> 's'
    word_strs = cudf.Series(["shopping", "parking", "drinking", "sing", "bing"])
    can_replace_mask = cudf.Series([True, True, True, False, False])
    got = replace_suffix(word_strs, "ing", "s", can_replace_mask)
    expect = ["shopps", "parks", "drinks", "sing", "bing"]
    assert sorted(list(got.to_pandas().values)) == sorted(expect)

    ### basic test 'ies' -> 's'
    word_strs = cudf.Series(["shops", "ties"])
    can_replace_mask = cudf.Series([False, True])
    got = replace_suffix(word_strs, "ies", "i", can_replace_mask)

    expect = ["shops", "ti"]
    assert sorted(list(got.to_pandas().values)) == sorted(expect)