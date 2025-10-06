import hashlib

M_BITS = 160
MOD = 1 << M_BITS

def sha1_int(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest(), 16)

def id_in_interval(id_int: int, start: int, end: int, inclusive_start=False, inclusive_end=False) -> bool:
    start %= MOD
    end %= MOD
    id_int %= MOD

    if start < end:
        left = id_int > start if not inclusive_start else id_int >= start
        right = id_int < end if not inclusive_end else id_int <= end
        return left and right
    elif start > end:
        if inclusive_start and id_int == start:
            return True
        if inclusive_end and id_int == end:
            return True
        return id_int > start or id_int < end
    else:
        # start == end
        if inclusive_start or inclusive_end:
            return True
        return False
