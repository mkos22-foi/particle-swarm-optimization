# chmod +x simulacija
import math as m
import random as r
import subprocess

PS = 30
BROJ_ITERACIJA = 10000
C = 1.49445
OMEGA = 0.9
MINUS = 0.00007

U1_MIN = 0
U1_MAX = 512
U2_MIN = -100
U2_MAX = 1000

# BOUNDS je lista granica za svaku dimenziju
BOUNDS = [
    (0.0, 3.0),         # u1 ide od 0 do 3
    (0.0001, 0.99),     # u2 ide od 0.0001 do 0.99
    (5.0, 100000.0),    # u3 ide od 5 do 100000
]
DIM = len(BOUNDS)       # Automatski daj ebroj elemenata u listi
# Ako profesor da novu simulaciju s 4 param, samo dodam novi par u bounds i DIM se ažurira

def izlaz(u1, u2, u3):
    result = subprocess.run(
        ["./simulacija", str(u1), str(u2), str(u3)],
        capture_output=True, text=True
        # Uhvati što program ispiše (inače bi se ispisalo na ekran)
        # Vrati kao tekst ne, ne kao byte
    )
    return float(result.stdout.strip())
    # Result.stdout -> što je program ispisao
    # satrip() -> makni razmake / newline na kraju
    # float(...) -> pretvori tekst u broj

def granica(ps, i: int) -> float:
    return 0.05 + 0.45 * (m.exp(10 * (i - 1) / (ps - 1)) - 1) / (m.exp(10) - 1)

def inicijalizacija():
    x, v, xpb, fpb, Pc = [], [], [], [], []
    
    for i in range(PS):
        x.append([r.uniform(lo, hi) for lo, hi in BOUNDS])

        v.append([0.0] * DIM)

        xpb.append(x[i].copy())
        fpb.append(izlaz(*x[i]))
        Pc.append(granica(PS, i+1))
    
    refreshing_gap = [7] * PS
    
    return x, v, xpb, fpb, refreshing_gap, Pc

def izracunaj_xb(i, xpb, fpb, Pc):
    xb = []
    for d in range(DIM):
        if r.random() < Pc[i]:
            xb.append(xpb[i][d])
        else:
            j, k = r.sample(range(PS), 2)
            if fpb[j] < fpb[k]:
                xb.append(xpb[j][d])
            else:
                xb.append(xpb[k][d])
    return xb

def pso():
    open("rezultat_1c.csv", "w").close()  # briše stari csv
    with open("rezultat_1c.csv", "w") as f:
        f.write("iteracija,u1,u2,u3,vrijednost\n")
    x, v, xpb, fpb, refreshing_gap, Pc = inicijalizacija()

    xb = []
    for i in range(PS):
        xb.append(izracunaj_xb(i, xpb, fpb, Pc))

    omega = OMEGA
    
    for iteracija in range(BROJ_ITERACIJA):
        for i in range(PS):
            # 1. ažuriraj brzinu i poziciju
            for d in range(DIM):
                R = r.random()
                v[i][d] = omega * v[i][d] + C * R * (xb[i][d] - x[i][d])
                x[i][d] = x[i][d] + v[i][d]

            # 2. provjeri granice
            for d in range(DIM):
                if x[i][d] < BOUNDS[d][0] or x[i][d] > BOUNDS[d][1]:
                    x[i][d] = r.uniform(BOUNDS[d][0], BOUNDS[d][1])

            # 3. izračunaj novu vrijednost funkcije
            f = izlaz(*x[i])

            # 4. ažuriraj xpb i fpb ako je bolje
            if f < fpb[i]:
                fpb[i] = f
                xpb[i] = x[i].copy()

            # 5. inače umanji refreshing_gap, ako ==0 preračunaj xb
            else:
                refreshing_gap[i] -= 1
                if refreshing_gap[i] == 0:
                    xb[i] = izracunaj_xb(i, xpb, fpb, Pc)
                    refreshing_gap[i] = 7

        omega -= MINUS

        # spremi globalno najbolje u csv
        najbolji_f = min(fpb)
        najbolji_i = fpb.index(najbolji_f)
        najbolji_x = xpb[najbolji_i]

        if iteracija % 100 == 0:
            print(f"Iteracija {iteracija}, najbolje: {najbolji_f}")

        with open("rezultat_1c.csv", "a") as f:
            f.write(f"{iteracija+1},{najbolji_x[0]},{najbolji_x[1]},{najbolji_x[2]},{najbolji_f}\n")
    
    print(f"Najbolje rješenje: {najbolji_f}")
    print(f"u1 = {najbolji_x[0]}, u2 = {najbolji_x[1]}, u3 = {najbolji_x[2]}")
pso()