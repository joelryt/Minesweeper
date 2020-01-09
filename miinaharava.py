import random
import time
import haravasto
import ikkunasto

tila = {
    "kentta": [],
    "jaljella": []
}
nakyva_tila = {
    "nakyva_kentta": []
}
tilastokirja = {
    "pvm": None,
    "kellonaika": None,
    "aloitusaika": None,
    "lopetusaika": None,
    "kestoaika": None,
    "kestovuorot": 0,
    "lopputulos": None
}
kentan_tiedot = {
    "korkeus": None,
    "leveys": None,
    "miinojen_lkm": None,
    "lippujen_lkm": 0
}
syotteet = {
    "ikkuna": None,
    "korkeus": None,
    "leveys": None,
    "miinojen_lkm":None
}
loppuikkuna = {
    "ikkuna": None,
}
tilastot = []

def main():
    """
    Lataa pelin grafiikat, luo peli-ikkunan ja asettaa käsittelijäfunktiot.
    """
    alkunollaus()
    luo_kentta(kentan_tiedot["korkeus"], kentan_tiedot["leveys"], kentan_tiedot["miinojen_lkm"])
    korkeus = kentan_tiedot["korkeus"] * 40
    leveys = kentan_tiedot["leveys"] * 40
    haravasto.lataa_kuvat("spritet")
    haravasto.luo_ikkuna(leveys, korkeus)
    haravasto.aseta_piirto_kasittelija(piirra_kentta)
    haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)
    tilastokirja["aloitusaika"] = time.time()
    haravasto.aloita()
    
def piirra_kentta():
    """
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    """
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()
    for i, rivi in enumerate(nakyva_tila["nakyva_kentta"]):
        y = i * 40
        for j, sarake in enumerate(nakyva_tila["nakyva_kentta"][0]):
            x = j * 40
            haravasto.lisaa_piirrettava_ruutu(nakyva_tila["nakyva_kentta"][i][j], x, y)
    haravasto.piirra_ruudut()
    paivita_lippujen_maara()
    
def miinoita(miinakentta, vapaat_ruudut, miinojen_lkm):
    """
    Asettaa kentällä N kpl miinoja satunnaisiin paikkoihin.
    """
    for ruutu in range(miinojen_lkm):
        x, y = random.choice(vapaat_ruudut)
        miinakentta[y][x] = "x"
        vapaat_ruudut.remove((x, y))
        
def kasittele_hiiri(x, y, painike, muokkausnappaimet):
    """
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    Merkkaa tai avaa klikatun ruudun.
    """
    painikkeet = {
        haravasto.HIIRI_VASEN: "vasen",
        haravasto.HIIRI_KESKI: "keski",
        haravasto.HIIRI_OIKEA: "oikea",
    }
    x_koord = int(x / 40)
    y_koord = int(y / 40)
    painettu_painike = painikkeet[painike]
    kentan_tiedot["lippujen_lkm"] = 0
    for rivi in nakyva_tila["nakyva_kentta"]:
        kentan_tiedot["lippujen_lkm"] += rivi.count("f")
    if painettu_painike == "oikea":
        if nakyva_tila["nakyva_kentta"][y_koord][x_koord] == " " and \
        kentan_tiedot["lippujen_lkm"] < kentan_tiedot["miinojen_lkm"]:
            nakyva_tila["nakyva_kentta"][y_koord][x_koord] = "f"
            piirra_kentta()
            tilastokirja["kestovuorot"] += 1
            paivita_lippujen_maara()
        elif nakyva_tila["nakyva_kentta"][y_koord][x_koord] == "f":
            nakyva_tila["nakyva_kentta"][y_koord][x_koord] = " "
            piirra_kentta()
            tilastokirja["kestovuorot"] += 1
            paivita_lippujen_maara()
    if painettu_painike == "vasen" and nakyva_tila["nakyva_kentta"][y_koord][x_koord] == " ":
        if tila["kentta"][y_koord][x_koord] == " ":
            tulvataytto(tila["kentta"], x_koord, y_koord)
            piirra_kentta()
            tilastokirja["kestovuorot"] += 1
            paivita_lippujen_maara()
            tarkista_lopetus(nakyva_tila["nakyva_kentta"])
        elif tila["kentta"][y_koord][x_koord] == "x":
            nakyva_tila["nakyva_kentta"] = tila["kentta"]
            piirra_kentta()
            tilastokirja["kestovuorot"] += 1
            tarkista_lopetus(nakyva_tila["nakyva_kentta"], miinaosuma=True)

def tulvataytto(miinakentta, alku_x, alku_y):
    """
    Merkitsee kentällä olevat tuntemattomat ruudut turvalliseksi siten, että
    täyttö aloitetaan klikatusta ruudusta.
    """
    miinat_vieressa = []
    tyhjat_ruudut = []
    tayttopisteet = [(alku_x, alku_y)]
    while int(len(tayttopisteet)) != 0:
        x, y = tayttopisteet.pop()
        if y == 0:
            y0 = 0
        elif y > 0:
            y0 = y - 1
        for vierekkainen_ruutu in miinakentta:    
            if x == 0:
                x0 = x - 1
            elif x > 0:
                x0 = x - 2
            while -1 <= x0 < len(miinakentta[1]) - 1 and 0 <= y0 <= len(miinakentta) - 1 \
            and x - 2 <= x0 < x + 1 and y - 1 <= y0 <= y + 1:
                x0 += 1
                ruutu = miinakentta[y0][x0]
                if ruutu == " ":
                    tyhjat_ruudut.append((x0, y0))
                elif ruutu == "x":
                    miinat_vieressa.append(ruutu)
            y0 += 1
        if int(len(miinat_vieressa)) == 0:
            tayttopisteet += tyhjat_ruudut
            tyhjat_ruudut.clear()
        else:
            tyhjat_ruudut.clear()
        tila["kentta"][y][x] = str(int(len(miinat_vieressa)))
        nakyva_tila["nakyva_kentta"][y][x] = tila["kentta"][y][x]
        miinat_vieressa.clear()
       
def tarkista_lopetus(nakyva_miinakentta, miinaosuma=False):
    """
    Tarkistaa täyttyykö pelin lopetusehdot. Jos täyttyy, sulkee peli-ikkunan,
    tallentaa pelin tiedot ja lopuksi tyhjentää vanhan pelin tiedot.
    """
    avatut_ruudut = 0
    for rivi in nakyva_miinakentta:
        avatut_ruudut += rivi.count("0")
        avatut_ruudut += rivi.count("1")
        avatut_ruudut += rivi.count("2")
        avatut_ruudut += rivi.count("3")
        avatut_ruudut += rivi.count("4")
        avatut_ruudut += rivi.count("5")
        avatut_ruudut += rivi.count("6")
        avatut_ruudut += rivi.count("7")
        avatut_ruudut += rivi.count("8")
    if miinaosuma:
        tilastokirja["lopputulos"] = "Häviö"
        tilastokirja["lopetusaika"] = time.time()
        lisaa_tilasto()
        tallenna_tilastot("miinaharavatilastot.txt")
        nayta_lopputulos()
        nollaa_tiedot()
        haravasto.lopeta()
    elif avatut_ruudut == int(len(tila["jaljella"])):
        nakyva_tila["nakyva_kentta"] = tila["kentta"]
        piirra_kentta()
        tilastokirja["lopputulos"] = "Voitto"
        tilastokirja["lopetusaika"] = time.time()
        lisaa_tilasto()
        tallenna_tilastot("miinaharavatilastot.txt")
        nayta_lopputulos(True)
        nollaa_tiedot()
        haravasto.lopeta()
        
def lataa_tilastot(tiedosto):
    """
    Lataa pelattujen pelien tilastot.
    """
    try:
        with open(tiedosto) as lahde:
            for rivi in lahde.readlines():
                tilastot.append(rivi.strip())
    except IOError:
        print("Tiedoston avaaminen ei onnistu. Alustetaan tyhjä tilastotiedosto")
                
def tallenna_tilastot(tiedosto):
    """
    Tallentaa pelatun pelin tiedot.
    """
    with open(tiedosto, "w") as kohde:
        for peli in tilastot:
            kohde.write("{}\n".format(peli))
            
def lisaa_tilasto():
    """
    Lisää pelatun pelin tilastot tallennettavaan tilastolistaan.
    """
    aseta_aika()
    tilastot.append("Päivämäärä ja kellonaika: {} {}. Kesto: {:.1f} minuuttia, "
        "{} vuoroa. Lopputulos: {}. Kentän koko {}x{}, miinojen lukumäärä: {}".format(
            tilastokirja["pvm"], 
            tilastokirja["kellonaika"], 
            tilastokirja["kestoaika"],
            tilastokirja["kestovuorot"],
            tilastokirja["lopputulos"],
            kentan_tiedot["korkeus"],
            kentan_tiedot["leveys"],
            kentan_tiedot["miinojen_lkm"]
            ))
    
def aseta_aika():
    """
    Asettaa päivämäärän ja kellonajan, jolloin peli on pelattu. Laskee myös pelin keston.
    """
    vuosi = time.localtime(time.time()).tm_year
    kuukausi = time.localtime(time.time()).tm_mon
    paiva = time.localtime(time.time()).tm_mday
    tunnit = time.localtime(time.time()).tm_hour
    minuutit = time.localtime(time.time()).tm_min
    pvm = "{}.{}.{}".format(paiva, kuukausi, vuosi)
    kellonaika = "{:02}:{:02}".format(tunnit, minuutit)
    tilastokirja["pvm"] = pvm
    tilastokirja["kellonaika"] = kellonaika
    tilastokirja["kestoaika"] = (tilastokirja["lopetusaika"] - tilastokirja["aloitusaika"]) / 60

def lue_tilastot():
    """
    Tulostaa pelattujen pelien tilastot.
    """
    tilastoikkuna = ikkunasto.luo_ali_ikkuna("Tilastot")
    tilastolaatikko = ikkunasto.luo_tekstilaatikko(tilastoikkuna)
    for peli in tilastot:
        ikkunasto.kirjoita_tekstilaatikkoon(tilastolaatikko, peli)
        
def luo_valikko():
    """
    Luo valikkoikkunan.
    """
    ikkuna = ikkunasto.luo_ikkuna("Miinaharava")
    nappikehys = ikkunasto.luo_kehys(ikkuna, ikkunasto.YLA)
    uusipelinappi = ikkunasto.luo_nappi(nappikehys, "Uusi peli", pyyda_syotteet)
    tilastonappi = ikkunasto.luo_nappi(nappikehys, "Tilastot", lue_tilastot)
    lopetusnappi = ikkunasto.luo_nappi(nappikehys, "Lopeta", ikkunasto.lopeta)
    ikkunasto.kaynnista()

def pyyda_syotteet():
    """
    Pyytää pelajaalta pelikentän koon ja miinojen lukumäärän.
    """
    if syotteet["ikkuna"]:
        ikkunasto.poista_elementti(syotteet["ikkuna"])
        syotteet["ikkuna"] = None
    if loppuikkuna["ikkuna"]:
        sulje_lopputulos()
        loppuikkuna["ikkuna"] = None
    syotteet["ikkuna"] = ikkunasto.luo_ali_ikkuna("Pelikentän tiedot")
    ikkunasto.luo_tekstirivi(syotteet["ikkuna"], "Pelikentän korkeus:")
    syotteet["korkeus"] = ikkunasto.luo_tekstikentta(syotteet["ikkuna"])
    ikkunasto.luo_tekstirivi(syotteet["ikkuna"], "Pelikentän leveys:")
    syotteet["leveys"] = ikkunasto.luo_tekstikentta(syotteet["ikkuna"])
    ikkunasto.luo_tekstirivi(syotteet["ikkuna"], "Miinojen lukumäärä:")
    syotteet["miinojen_lkm"] = ikkunasto.luo_tekstikentta(syotteet["ikkuna"])
    ikkunasto.luo_vaakaerotin(syotteet["ikkuna"])
    aloitusnappi = ikkunasto.luo_nappi(syotteet["ikkuna"], "Aloita", tarkista_syotteet)
        
def tarkista_syotteet():
    """
    Tarkistaa syötteet. Jos syötteet kelpaa, käynnistää pelin.
    """
    try:
        kentan_tiedot["korkeus"] = abs(int(ikkunasto.lue_kentan_sisalto(syotteet["korkeus"])))
        kentan_tiedot["leveys"] = abs(int(ikkunasto.lue_kentan_sisalto(syotteet["leveys"])))
        kentan_tiedot["miinojen_lkm"] = abs(int(ikkunasto.lue_kentan_sisalto(syotteet["miinojen_lkm"])))
    except ValueError:
        ikkunasto.avaa_viesti_ikkuna(
            "Virhe",
            "Anna kentän leveydeksi ja korkeudeksi sekä miinojen lukumääräksi jokin positiivinen \
            kokonaisluku.",
            True
        )
    else:
        main()
            
def luo_kentta(kentan_korkeus, kentan_leveys, miinojen_lkm):
    """
    Luo ja miinoittaa miinoitettavan kentän, luo pelaajalle näytettävän kentän sekä luo
    listan jäljelle jääneistä ruuduista.
    """
    for rivi in range(kentan_korkeus):
        tila["kentta"].append([])
        for sarake in range(kentan_leveys):
            tila["kentta"][-1].append(" ")
    for rivi in range(kentan_korkeus):
        nakyva_tila["nakyva_kentta"].append([])
        for sarake in range(kentan_leveys):
            nakyva_tila["nakyva_kentta"][-1].append(" ")
    for x in range(kentan_leveys):
        for y in range(kentan_korkeus):
            tila["jaljella"].append((x, y))
    miinoita(tila["kentta"], tila["jaljella"], kentan_tiedot["miinojen_lkm"])
    
def nollaa_tiedot():
    """
    Nollaa pelin tilan, jotta uusi peli voidaan aloittaa puhtaalta pöydältä.
    """
    ikkunasto.poista_elementti(syotteet["ikkuna"])
    tila["kentta"] = []
    tila["jaljella"] = []
    nakyva_tila["nakyva_kentta"] = []
    tilastokirja["pvm"] = None
    tilastokirja["kellonaika"] = None
    tilastokirja["aloitusaika"] = None
    tilastokirja["lopetusaika"] = None
    tilastokirja["kestoaika"] = None
    tilastokirja["kestovuorot"] = 0
    tilastokirja["lopputulos"] = None
    kentan_tiedot["korkeus"] = None
    kentan_tiedot["leveys"] = None
    kentan_tiedot["miinojen_lkm"] = None
    kentan_tiedot["lippujen_lkm"] = 0
    syotteet["ikkuna"] = None
    syotteet["korkeus"] = None
    syotteet["leveys"] = None
    syotteet["miinojen_lkm"] = None
    
def nayta_lopputulos(voitto=False):
    """
    Näyttää pelaajalle pelatun pelin tiedot pelin päätyttyä.
    """
    loppuikkuna["ikkuna"] = ikkunasto.luo_ali_ikkuna("Lopputulos")
    if voitto:
        ikkunasto.luo_tekstirivi(loppuikkuna["ikkuna"], "Voitit pelin!")
    else:
        ikkunasto.luo_tekstirivi(loppuikkuna["ikkuna"], "Osuit miinaan. Hävisit pelin.")
    ikkunasto.luo_tekstirivi(loppuikkuna["ikkuna"], "Kesto: {:.1f} minuuttia, {} vuoroa".format(
        tilastokirja["kestoaika"],
        tilastokirja["kestovuorot"]
        ))
    ikkunasto.luo_nappi(loppuikkuna["ikkuna"], "Valikkoon", sulje_lopputulos)
    
def sulje_lopputulos():
    """
    Sulkee lopputulosikkunan.
    """
    ikkunasto.poista_elementti(loppuikkuna["ikkuna"])
    
def alkunollaus():
    """
    Tyhjentää miinakentät, nollaa vuorot ja aloitusajan.
    """
    tila["kentta"] = []
    tila["jaljella"] = []
    nakyva_tila["nakyva_kentta"] = []
    kentan_tiedot["lippujen_lkm"] = 0
    tilastokirja["aloitusaika"] = None
    tilastokirja["kestovuorot"] = 0
    
def paivita_lippujen_maara():
    """
    Päivittää merkattujen ruutujen määrän ja näyttää tiedon peli-ikkunassa.
    """
    kentan_tiedot["lippujen_lkm"] = 0
    for rivi in nakyva_tila["nakyva_kentta"]:
        kentan_tiedot["lippujen_lkm"] += rivi.count("f")
    x = kentan_tiedot["leveys"] * 40 - 53
    haravasto.piirra_tekstia("{}/{}".format(kentan_tiedot["lippujen_lkm"], \
        kentan_tiedot["miinojen_lkm"]), x, 25, fontti="serif", koko=10)
    
lataa_tilastot("miinaharavatilastot.txt")    
luo_valikko()