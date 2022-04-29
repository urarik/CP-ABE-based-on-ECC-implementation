def extendedEuclid(a, b):
    if a == 0:
        return b, 0, 1
    gcd, y1, x1 = extendedEuclid(b % a, a)
    x = x1 - (b // a) * y1
    y = y1
    return gcd, x, y


def inverse(a, p):
    if a < 0:
        return p - inverse(-a, p)
    (gcd, x, y) = extendedEuclid(a, p)
    return x % p
