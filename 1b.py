import math

# Search limits
u1_min = 0
u1_max = 512
u2_min = -100
u2_max = 1000


# Function to be minimized
def izlaz(u1, u2):
    if u1 > u2:
        return math.sin(u1 + u2**2) * math.exp(abs(1 - math.sqrt(u1**2 + 2.5*u2**2)))
    elif u1 - 2*u2 <= 0.5:
        return u2 * math.cos(u1*u2 + 2.3*u1) - 0.6
    else:
        return 2 / (3 + math.sin(u2))

