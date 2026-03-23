import math

def izlaz(u1, u2):
    if u1 > u2:
        return math.sin(u1 + u2**2) * math.exp(abs(1 - math.sqrt(u1**2 + 2.5*u2**2)))
    elif u1 - 2*u2 <= 0.5:
        return u2 * math.cos(u1*u2 + 2.3*u1) - 0.6
    else:
        return 2 / (3 + math.sin(u2))

