"""
Numbers functionality
"""

import re
import math
from decimal import Decimal, ROUND_HALF_UP


_SUBSCRIPTS = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
}


def is_float(value: str) -> bool:
    """Check value for float"""

    try:
        float(value)
    except (ValueError, TypeError):
        return False

    return True


def to_num(value) -> bool:
    """Convert value to int or float"""

    if value is None:
        return None

    if isinstance(value, str):
        value = float(value.strip())

    if not value % 1:
        value = int(value)

    return value


def to_int(value) -> int:
    """Choose only decimal"""

    if not value:
        return 0

    return int(re.sub(r"\D", "", str(value)))


def get_float(value) -> list:
    """Get a list of floats"""

    if value is None:
        return []

    numbers = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", value)
    return [float(number) for number in numbers]


def find_decimals(value):
    """Get count of decimal"""

    if isinstance(value, str):
        while value[-1] == "0":
            value = value[:-1]

    return abs(Decimal(str(value)).as_tuple().exponent)


def get_whole(value):
    """Get whole view of a number"""

    if isinstance(value, int) or (isinstance(value, str) and "." not in value):
        # NOTE: to remove 0 in the start of the string
        return str(int(value))

    # NOTE: float for add . to int & support str
    value = float(value)

    # NOTE: to avoid the exponential form of the number
    return f"{value:.{find_decimals(value)}f}"


def simplify_value(value, decimals=4):
    """Get the significant part of a number"""

    if value is None:
        return None

    value = get_whole(value)
    if "." not in value:
        value += "."

    whole, fractional = value.split(".")

    if value[0] == "-":
        sign = "-"
        whole = whole[1:]
    else:
        sign = ""

    if whole != "0":
        digit = len(whole)
        value = whole + "." + fractional[: max(0, decimals - digit)]

    else:
        offset = 0
        while fractional and fractional[0] == "0":
            offset += 1
            fractional = fractional[1:]

        value = "0." + "0" * offset + fractional[:decimals]

    while value[-1] == "0":
        value = value[:-1]

    if value[-1] == ".":
        value = value[:-1]

    return sign + value


def pretty(value, decimals=None, sign=False, symbol="’"):
    """Decorate the number beautifully"""

    if value is None:
        return None

    data = str(float(value))

    if decimals is not None:
        cur = len(data.split(".", maxsplit=1)[0])
        data = str(round(value, max(0, decimals - cur)))

    if data.rsplit(".", maxsplit=1)[-1] == "0":
        data = data.split(".", maxsplit=1)[0]

    if data == "0":
        return "0"

    if symbol:
        data = add_radix(data, symbol)

    if sign:
        if data[0] != "-":
            data = "+" + data

    return data


def add_sign(value):
    """Add sign to a number"""

    if value is None:
        return None

    sign = ""

    if float(value) > 0:
        sign = "+"
    elif value == 0:
        value = abs(value)

    return f"{sign}{get_whole(value)}"


def add_radix(value, symbol="’"):
    """Add radix to a number"""

    if value is None:
        return None

    value = str(value)

    if "." in value:
        integer, fractional = value.split(".")
    else:
        integer = value
        fractional = ""

    if integer[0] == "-":
        sign = "-"
        integer = integer[1:]
    # elif integer[0] == '+':
    #     sign = '+'
    #     integer = integer[1:]
    else:
        sign = ""

    data = ""
    ind = 0
    for i in integer[::-1]:
        if ind and ind % 3 == 0:
            data = symbol + data
        ind += 1
        data = i + data

    data = sign + data
    if fractional:
        data += "." + fractional

    return data


def mul(x, y):
    """Multiply fractions correctly"""
    if x is None or y is None:
        return None
    return float(Decimal(str(x)) * Decimal(str(y)))


def div(x, y):
    """Divide fractions correctly"""
    if x is None or y is None:
        return None
    return float(Decimal(str(x)) / Decimal(str(y)))


def add(x, y):
    """Subtract fractions correctly"""
    if x is None or y is None:
        return None
    return float(Decimal(str(x)) + Decimal(str(y)))


def sub(x, y):
    """Subtract fractions correctly"""
    if x is None or y is None:
        return None
    return float(Decimal(str(x)) - Decimal(str(y)))


def to_step(value, step=1, side=False):
    """Change value step"""

    if value is None:
        return None

    value = div(value, step)
    if side:
        value = math.ceil(value)
    else:
        value = math.floor(value)
    value = mul(value, step)

    if step >= 1:
        value = int(value)

    return value


def _to_subscript(n: int) -> str:
    """Convert an integer n to a string of subscript digits."""
    return "".join(_SUBSCRIPTS[d] for d in str(n))


def compress_zeros(x: int | float, round: int | None = None) -> str | None:
    """
    Given a float or decimal‐string x, return a string where
    runs of leading zeros in the fraction are shown as:
      one '0' plus a subscript count of the zeros.
    If `round` is provided, the remaining digits after the zeros
    are rounded to that many places.

    Examples:
      compress_zeros(0.00012)           -> '0.0₃12'
      compress_zeros(0.00012, round=2)  -> '0.0₃12'
      compress_zeros(0.0123)            -> '0.0123'  (only one leading zero, so unchanged)
      compress_zeros(0.0123456, round=3)-> '0.0123'
      compress_zeros(1.000045)          -> '1.0₄45'
      compress_zeros(-0.0010959999999999997522, round=3)
                                        -> '-0.0₂11'
    """

    if x is None:
        return None

    dec_x = Decimal(str(x))
    s = format(dec_x, "f")

    # no fractional part
    if "." not in s:
        return s

    int_part, frac = s.split(".", 1)

    # count leading zeros in the fractional part
    zero_run = len(frac) - len(frac.lstrip("0"))

    # If rounding is requested, do it first
    if round is not None:
        # ensure at least one zero is counted for quantization
        places = max(zero_run, 1) + round
        quant = Decimal(f"1e-{places}")
        dec_q = dec_x.quantize(quant, rounding=ROUND_HALF_UP)
        s_q = format(dec_q, "f")

        # if rounding eliminated fractional part
        if "." not in s_q:
            return s_q

        int_part_q, frac_q = s_q.split(".", 1)
        # for zero_run == 0 or 1, we just return the rounded string
        if zero_run <= 1:
            return s_q

        # strip any trailing zeros, then compress
        frac_q = frac_q.rstrip("0")
        if not frac_q:
            return int_part_q
        tail = frac_q[zero_run:]
        return f"{int_part_q}.0{_to_subscript(zero_run)}{tail}"

    # No rounding: only compress if more than one leading zero
    if zero_run <= 1:
        return s

    tail = frac[zero_run:]

    # build compressed form
    return f"{int_part}.0{_to_subscript(zero_run)}{tail}"
