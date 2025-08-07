#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Low-level printing utility functions.

Provides basic string manipulation utilities for formatting and
processing text output, used by higher-level printing functions.
"""

import math
from typing import Union


def prepend_string_lines(prepend_string: str, main_string: str) -> str:
    """
    Prepend prepend_string to each line in main_string.

    Args:
        prepend_string: String to prepend to each line
        main_string: Multi-line string to process

    Returns:
        String with prepend_string added to the beginning of each line
    """
    out_string = ''
    for line in main_string.split('\n'):
        out_string += prepend_string + line + '\n'
    out_string = out_string[:-1]
    return out_string


def int_if(number: Union[int, float]) -> Union[int, float]:
    """
    Convert float to int if it is an exact int.

    Args:
        number: Number to potentially convert

    Returns:
        Integer if the number is exactly an integer, otherwise the original number
    """
    if int(number) == number:
        return int(number)
    else:
        return number


def fstr(flt: float) -> str:
    """
    Automatic, nice formatting of float to string.

    Formats floats with appropriate precision based on magnitude:
    - Very small numbers: more decimal places
    - Medium numbers: fewer decimal places
    - Large numbers: scientific notation

    Args:
        flt: Float to format

    Returns:
        Nicely formatted string representation of the float
    """
    try:
        first_nonzero_dig = math.log10(abs(flt))
    except ValueError:
        return str(0)
    if first_nonzero_dig < 0:
        truncate = 3 - int(first_nonzero_dig)
        return str(int_if(float(f'{flt:.{truncate}f}')))
    if first_nonzero_dig >= 0 and first_nonzero_dig < 2:
        truncate = 2 - int(first_nonzero_dig)
        return str(int_if(float(f'{flt:.{truncate}f}')))
    elif first_nonzero_dig >= 2 and first_nonzero_dig < 5:
        return str(int_if(float(f'{flt:.0f}')))
    else:
        sci_flt = f'{flt:e}'.split('e')
        coeff = float(sci_flt[0])
        round_coeff = fstr(coeff)
        return round_coeff + 'e' + sci_flt[1]
