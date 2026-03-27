# Uvoz biblioteka
import math as m
import random as r

# Inicijalizacija parametara
PS = 30                     # Broj čestica u roju
BROJ_ITERACIJA = 10000      # Broj iteracija
C = 1.49445                 # Konstanta privlačenja - koliko jako xb (cilj prema kojem se kreće) vuče česticu
OMEGA = 0.9                 # Početna inercija - koliko čestica "nastavlja ravno"
MINUS = 0.00007             # Za koliko se smanjuje omega nakon svake iteracije

# Definiranje granica unutar kojih čestice smiju biti
U1_MIN = 0
U1_MAX = 512
U2_MIN = -100
U2_MAX = 1000

# Definiranje funkcije izlaza -> funkcija čiji minimum tražimo
# Prima koodrinate u1 i u2 i vraća broj - visinu terena na toj lokaciji - čim manji broj to bolje
def izlaz(u1: float, u2: float) -> float:
    if u1 > u2:
        # try | except -> math.exp() može proizvesi preveliki broj (OverflowError)
        # u tom slučaju vrača float('inf') - čestica se trewtira kao jako loše rješenje i neće ići tamo
        # kada se vrati ovo rješenje ono se tretira kao loše i onda se refrashing_gap smanjuje
        try:
            return m.sin(u1 + u2*u2) * m.exp(abs(1 - m.sqrt(u1*u1 + 2.5*u2*u2)))
        except OverflowError:
            return float('inf')
    elif u1 - 2*u2 <= 0.5:
        return u2 * m.cos(u1*u2 + 2.3*u1) - 0.6
    else:
        return 2 / (3 + m.sin(u2))

# DIMENZIJA je u1 ili u1 - samo jedna točka
# Dimenzije su dvije točke

# Granica - Pci - računa se prema formuli iz uputa
# Ona predstavlja omjer vjerojatnosti hoće li čestica za određenu dimenziju uzezti svoju dimenziju PB-a
# ili tuđu (od pobjednika nasumične dvojke)
# Što je Pci veći -> veća šansa da čestica gleda sebe
# Što je Pci manji -> veća šansa da čestica gleda tuđe
# Ovaj Pci se koristi kod 'izracunaj_xb'
def granica(ps, i: int) -> float:
    return 0.05 + 0.45 * (m.exp(10 * (i - 1) / (ps - 1)) - 1) / (m.exp(10) - 1)

# Inicijaliziranje
def inicijalizacija():
    # Vrijednosti se postavljaju na liste jer za svaku česticu treba postojati njena vrijednost
    # x je koordinata gdje se čestica trenutno nalazi [u1_0, u2_0], ...
    # v je za koliko se miće u idućem koraku (brzina) - [v1_0, v2_0], ...
    # xpb je osobni personal best [u1_0, u2_0], ...
    # fpb je vrijednost funkcije izlaz na personal best poziciji - koliko je dobar taj best rezultat (manji = bolji)
    # Pc je granica vjerojatnosti - provjerava ase kor racunanja xb - razliak izmedu odabira tuđih i svojih dimenzija
    x, v, xpb, fpb, Pc = [], [], [], [], []
    
    # Ponavljanje 30 puta jer imamo 30 čestica
    for i in range(PS):
        # Postavljanje početne pozicije - unutar definiranog raspona
        x.append([r.uniform(U1_MIN, U1_MAX), r.uniform(U2_MIN, U2_MAX)])
        # Postavljanje početne brzine, odnosno za koliko se pomiće u sljedećem koraku
        v.append([0.0, 0.0])
        # Personal best je inicijalizirana lokacija jer je to jedina lokacija 
        xpb.append(x[i].copy())
        # Pozivanje funkcije izlaz na personal best poziciji - ona sprema rezultat - manji rez = bolji rez
        fpb.append(izlaz(x[i][0], x[i][1]))
        # Računa se granica i ona se sprema kao nova granica
        Pc.append(granica(PS, i+1))
    
    # Postavljanje brojača za svaku česticu
    # Brojač se umanjuje svaki put kada čestica dobije novo rješenje lošije od najboljeg osobnog rješenja
    refreshing_gap = []
    for i in range(PS):
        refreshing_gap.append(7)
    
    # Vraćanje vrijednosti
    return x, v, xpb, fpb, refreshing_gap, Pc

# Računanje xb-a (cilj prema kojem se cestica treba kretati) za svaku česticu
# xb je koordinata kamo se cestica dallje krece
# uzimaju se dimenzije ili od nje ili od 
def izracunaj_xb(i, xpb, fpb, Pc):
    # Kreiranje liste gdje ce se ovo spremati
    xb = []
    # Dvije dimenzije
    for d in range(2):
        # Ako je p < Pc[i] - osobna granica - vjerojatnos
        if r.random() < Pc[i]:
            xb.append(xpb[i][d])                # uzimas se komponenta s najbolje osobne pozicije
        else:
            j, k = r.sample(range(PS), 2)       # odabiru se dvije slučajne čestice j i k
            if fpb[j] < fpb[k]:                 # Ona koja ima manji rez funkcija izlaza - ima bolji rez
                xb.append(xpb[j][d])            # i uzimaju se njene kordinate
            else:
                xb.append(xpb[k][d])
    return xb

# Glavni PSO algoritam
def pso():

    # Brisanje stare SCV datoteke
    open("rezultat_1b.csv", "w").close()
    # Postavljanje header-a u CSV-u
    with open("rezultat_1b.csv", "w") as f:
        f.write("iteracija,u1,u2,vrijednost\n")

    # Inicijaliziranje pocenih vrijednosti
    x, v, xpb, fpb, refreshing_gap, Pc = inicijalizacija()
    
    # Računajnje cilja prema kojem se čestice kreću
    # To je kombinacija koordinata složena od PB-ova različitih čestica
    # Za svaku dimenziju (u1, u2) posebno odlučuje, hoću li uzeti svoju dim PB-a
    # ili dimenziju PB pobjednika nasumične dvojke
    xb = []
    for i in range(PS):
        xb.append(izracunaj_xb(i, xpb, fpb, Pc))

    # Unutar algoritma omega se smanjuje savku iteraciju
    # Smanjuje se jer algoritam ima dvije faze:
    # Početak - čestica ima veliku inerciju - nastavlja ici u dosadađnjem smjeru -> istražuje veliko područje
    # Kraj - čestica ima malu inerciju - lako mjenja smjer prema cilju -> fino pretražuje oko dobrog mjesta
    omega = OMEGA
    
    # Za svaku iteraciju (10000) se radi sljedeće
    for iteracija in range(BROJ_ITERACIJA):
        # Za svaku česticu (30)
        for i in range(PS):
            # 1. Ažuriranje brzine i pozicije - prema formuli
            for d in range(2):
                R = r.random()
                v[i][d] = omega * v[i][d] + C * R * (xb[i][d] - x[i][d])
                x[i][d] = x[i][d] + v[i][d]

            # 2. Provjera granice tehnikom novi nasumični polođaj
            if x[i][0] < U1_MIN or x[i][0] > U1_MAX:
                x[i][0] = r.uniform(U1_MIN, U1_MAX)
            if x[i][1] < U2_MIN or x[i][1] > U2_MAX:
                x[i][1] = r.uniform(U2_MIN, U2_MAX)

            # 3, Izračunavanje nove vrijednosti funkcije
            f = izlaz(x[i][0], x[i][1])

            # 4. Ažuriraj xpb i fpb ako je bolje
            if f < fpb[i]:
                fpb[i] = f
                xpb[i] = x[i].copy()

            # 5. Ako nije bolje, umanji refreshing_gap, ako je vec 0 ona se ponovno postalja xb
            else:
                refreshing_gap[i] -= 1
                if refreshing_gap[i] == 0:
                    xb[i] = izracunaj_xb(i, xpb, fpb, Pc)
                    refreshing_gap[i] = 7

        omega -= MINUS
        
        # spremi globalno najbolje u csv
        najbolji_f = min(fpb)                   # Iz liste svih 30 fpb vrijednosti uzmi najmanji broj (= globalno najbolji rez)
        najbolji_i = fpb.index(najbolji_f)      # Pronađi koji indeks (koja čestica) ima taj najmanji rezultat
        najbolji_x = xpb[najbolji_i]            # Uzmi koordinate te čestice

        with open("rezultat_1b.csv", "a") as f:
            f.write(f"{iteracija+1},{najbolji_x[0]},{najbolji_x[1]},{najbolji_f}\n")
    
    print(f"Najbolje rješenje: {najbolji_f}")
    print(f"u1 = {najbolji_x[0]}, u2 = {najbolji_x[1]}")

if __name__ == "__main__":
    pso()