from numba import cuda
import cudf
import numpy as np
import cupy as cp

from cudf.utils.utils import scalar_broadcast_to


def get_str_replacement_series(replacement, bool_mask):
    """
     get replacement series with replacement at places marked by bool mask and empty other wise
    """
    word_ser = cudf.Series(scalar_broadcast_to("", size=len(bool_mask)))
    word_ser.iloc[bool_mask] = replacement

    return word_ser


def get_index_replacement_series(word_strs, replacment_index, bool_mask):
    """
     get replacement series with nulls at places marked by bool mask
    """
    valid_indexes = ~bool_mask
    word_strs = word_strs.str.get(replacment_index)
    word_strs = cudf.Series(word_strs)
    word_strs.iloc[valid_indexes] = ""

    return word_strs


def replace_suffix(word_strs, suffix, replacement, can_replace_mask):
    """ 
        replaces string column with valid suffix with replacement
    """

    len_suffix = len(suffix)
    if replacement == "":
        stem_ser = get_stem_series(word_strs, len_suffix, can_replace_mask)
        return stem_ser
    else:
        stem_ser = get_stem_series(word_strs, len_suffix, can_replace_mask)
        if isinstance(replacement, str):
            replacement_ser = get_str_replacement_series(replacement, can_replace_mask)
        if isinstance(replacement, int):
            replacement_ser = get_index_replacement_series(
                word_strs, replacement, can_replace_mask
            )
        else:
            assert ValueError(
                "replacement: {} value should be a string or a int".format(replacement)
            )

        return stem_ser + replacement_ser


@cuda.jit("void(int32[:], boolean[:], int32)")
def subtract_valid(input_array, valid_bool_array, sub_val):
    pos = cuda.grid(1)
    if pos < input_array.size:
        if valid_bool_array[pos]:
            input_array[pos] = input_array[pos] - sub_val


def get_stem_series(word_strs, suffix_len, can_replace_mask):
    """
        word_strs: input string column
        suffix_len: length of suffix to replace
        can_repalce_mask: bool array marking strings where to replace
    """
    NTHRD = 1024
    NBLCK = int(np.ceil(float(len(word_strs)) / float(NTHRD)))

    start_series = cudf.Series(cp.zeros(len(word_strs), dtype=cp.int32))
    end_ser = word_strs.str.len()

    end_ar = end_ser._column.data_array_view
    can_replace_mask_ar = can_replace_mask._column.data_array_view

    subtract_valid[NBLCK, NTHRD](end_ar, can_replace_mask_ar, suffix_len)
    return word_strs.str.slice_from(starts=start_series, stops=end_ser.fillna(0))