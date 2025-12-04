def safe_float(x):
    """
    Converts any value to float safely.
    If conversion fails → return 0.0
    """
    try:
        if x is None:
            return 0.0
        if isinstance(x, bytes):
            return 0.0
        return float(x)
    except:
        return 0.0


def safe_int(x):
    try:
        if x is None:
            return 0
        if isinstance(x, bytes):
            return 0
        return int(float(x))
    except:
        return 0
