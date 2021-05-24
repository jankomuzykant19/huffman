import zmq
import json
import socket as socc


class Wezel():

    def __init__(self, elem=None, waga=None, lewy=None, prawy=None):
        self.elem = elem
        self.waga = waga
        self.lewy = lewy
        self.prawy = prawy


class KodowanieHuffmana():

    def __init__(self, wiadomosc):
        self.wiadomosc = wiadomosc
        self.slownikWag = {}
        self.listaKodowana = []
        self.slownikKodowany = {}
# Liczymy wagi liter
    def liczenieWag(self, string):
        slownikWyrazow = {}
# Dla każdej litery
        for litery in string:
            if (litery in slownikWyrazow):
                slownikWyrazow[litery] += 1
            else:
                slownikWyrazow[litery] = 1

        return slownikWyrazow
# Wstawiamy węzeł
    def wstawWezel(self, prawy):
        i = 0
        for n in self.listaKodowana:
            if n.waga > prawy.waga:
                i += 1

        self.listaKodowana.insert(i, prawy)
# Tworzymy nowy węzeł na podstawie słownika
    def slownikNaWezly(self):
        for k, v in self.slownikWag.items():
            nowy_wezel = Wezel(elem=k, waga=v)
            self.wstawWezel(nowy_wezel)
# Łączymy ze sobą węzły
    def laczWezly(self):

        while len(self.listaKodowana) > 1:
            w1 = self.listaKodowana.pop()
            w2 = self.listaKodowana.pop()
            w3 = Wezel(elem=None, waga=w1.waga + w2.waga, lewy=w1, prawy=w2)
            self.wstawWezel(w3)
# Zamieniamy drzewo na kody
    def drzewoNaKody(self, prawy, binarnyKod=''):

        if (prawy.elem != None):
            self.slownikKodowany[prawy.elem] = binarnyKod
        # Jeżeli lewy element nie jest none
        if (prawy.lewy != None):
            self.drzewoNaKody(prawy.lewy, binarnyKod + "0")
        # Jeżeli prawy element nie jest none
        if (prawy.prawy != None):
            self.drzewoNaKody(prawy.prawy, binarnyKod + "1")
# Zamieniamy wiadomość na kod binarny
    def wiadomoscnaBinarny(self):
        r = ''
        for c in self.wiadomosc:
            r += self.slownikKodowany[c]
        # print(r)

        self.wiadomosc = r
# Dekoduejmy wiadomość
    def dekoduj(self, slownik):
        temp = ''
        wiadomosc = ''
        for c in self.wiadomosc:
            temp += c
            if temp in slownik:
                wiadomosc += slownik[temp]
                temp = ''
        self.wiadomosc = wiadomosc
# Kodujemy wiadomość
    def koduj(self):
        self.slownikWag = self.liczenieWag(self.wiadomosc)
        self.slownikNaWezly()
        self.laczWezly()

        self.drzewoNaKody(self.listaKodowana[0])
        self.wiadomoscnaBinarny()

# Wybieramy w jakim trybie chcemy pracować
def main():
    print("Wybierz tryb pracy:")
    print("[0] - klient")
    print("[1] - server")
    x = input()
    if (x == "0"):
        client()
    elif (x == "1"):
        server()
    else:
        print("Nieprawidlowy wybor")
    wait = input("Nacisnij [ENTER] aby zakonczyc")

# Nasz serwer
def server():
    with open('tekst.txt', 'r') as file:
        txt = file.read()
    huffman = KodowanieHuffmana(txt)
    huffman.koduj()
    print(huffman.slownikKodowany)
    print(huffman.wiadomosc)
# Łączymy się
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    host_name = socc.gethostname()
    host_ip = socc.gethostbyname(host_name)
    print("IP komputera: " + host_ip)
    print("Wpisz IP klienta: ")
    x = input()
    socket.connect("tcp://" + x + ":5555")
# Tworzymy słownik
    s = json.dumps(huffman.slownikKodowany)
    with open('slownikwyslany.txt', 'w+') as file:
        file.write(s)
    print("Slownik zostal zapisany w pliku 'slownikwyslany.txt'")
    s = s + ".." + huffman.wiadomosc
    socket.send(bytes(s, "utf8"))

# To jest nasz klient
def client():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    host_name = socc.gethostname()
    host_ip = socc.gethostbyname(host_name)
    print("IP komputera:" + host_ip)
    print("Wpisz IP serwera:")
    # Wpisujemy adres IP
    x = input()
    socket.bind("tcp://" + x + ":5555")
    wiadomosc = socket.recv()
    odebrana = wiadomosc.decode("utf-8")
    a, b = odebrana.split('..')
    odebranyslownik = eval(a)
    # Robimy kodowanie huffmana
    huffman = KodowanieHuffmana(b)
    huffman.dekoduj(dict([[v, k] for k, v in odebranyslownik.items()]))
    print(huffman.wiadomosc)
    with open('odebranawiadomosc.txt', 'w+') as file:
        file.write(huffman.wiadomosc)
    print("Wiadomosc zostala zapisana do pliku 'odebranawiadomosc.txt'")
    with open('slownikodebrany.txt', 'w+') as file:
        file.write(a)
    print("Slownik zostal zapisany w pliku 'slownikodebrany.txt'")


if __name__ == '__main__':
    print("Jan Stawiński 224430 // Maciej Bigos 224260 // Telekomunikacja ")
    main()
