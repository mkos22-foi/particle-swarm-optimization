import math
import random

# Search limits
u1_min = 0
u1_max = 512
u2_min = -100
u2_max = 1000

# Algorithm parameters
refreshing_gap = 7
ps = 30
iterations = 10000
C = 1.49445
omega = 0.9
omega_diff = 0.00007

# Function to be minimized
def izlaz(u1, u2):
    if u1 > u2:
        return math.sin(u1 + u2**2) * math.exp(abs(1 - math.sqrt(u1**2 + 2.5*u2**2)))
    elif u1 - 2*u2 <= 0.5:
        return u2 * math.cos(u1*u2 + 2.3*u1) - 0.6
    else:
        return 2 / (3 + math.sin(u2))

# 
def initialization():
    x   = []        # positions
    v   = []        # speed
    xpb = []        # personal best position
    fpb = []        # values ​​of personal bests

    for i in range(ps):
        # nasumična početna pozicija
        u1 = random.uniform(u1_min, u1_max)
        u2 = random.uniform(u2_min, u2_max)

        x.append([u1, u2])
        v.append([0.0, 0.0])   # speed = 0 at beggining
        xpb.append([u1, u2])   # personal best = start position
        fpb.append(izlaz(u1, u2))

    return x, v, xpb, fpb

