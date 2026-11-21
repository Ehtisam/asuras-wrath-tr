# -*- coding: utf-8 -*-
r"""Hangi girdinin cevrilecegini tek yerden tanimlar.

DIKKAT: dosya adi tek basina BENZERSIZ DEGIL. 'Menu.int' hem
  ..\..\BCGame\Localization\INT\Menu.int
hem
  ..\..\BCGame\Localization\_DefaultFont\INT\Menu.int
olarak var. Esleme yaparken her zaman TAM YOLU kullan.
"""
import re

BS = chr(92)
LF = chr(10)
SEP = '\u241f'


def grup(yol):
    if yol.startswith('..' + BS + '..' + BS + 'Engine' + BS):
        return 'engine'
    if '_DefaultFont' in yol:
        return 'defaultfont'
    if '_TitleFont' in yol:
        return 'titlefont'
    if 'Credittitle' in yol:
        return 'jenerik'
    if 'Localization' in yol:
        return 'ana'
    return 'config'


def ana_kapsam(yol):
    """Cevrilecek asil oyun metni mi?"""
    return grup(yol) == 'ana'


# 4 karakter alti oldugu icin filtreye normalde carpan ama kritik arayuz/oyun
# kelimeleri (Common.int Yes/No/OK, Option.int On/Off, HUD/profil etiketleri...).
# 10.09.2026: Yes/No/OK'in oyun ici test edilene kadar cevrilmeden kaldigini
# fark ettik -- bu yuzden bu istisna listesi eklendi.
KISA_ISTISNA = {'Yes', 'No', 'OK', 'On', 'Off', 'No!', 'Ha!', 'Hm?', 'Hm!',
                'HIT', 'Sex', 'Age',
                # 12.09.2026: Almanca yuvaya yazarken, Ingilizcesi kisa/harfsiz
                # olan bu satirlar filtreye takiliyor ve Almanca metin (ya da
                # oyunun yer tutucusu) ekranda sizip kaliyordu.
                '...', 'Or,', '???'}


def cevrilmeli(v):
    s = v.strip()
    if s in KISA_ISTISNA:
        return True
    if len(s) < 4:
        return False
    if not re.search(r'[A-Za-z]', s):
        return False
    if re.fullmatch(r'[0-9.,:%/ +-]+', s):
        return False
    if re.fullmatch(r'(?i)AW_[0-9]+_[0-9]+' + re.escape('.') + r'int', s):
        return False
    if re.match(r'(?i)TalkDemo[_A-Za-z0-9]* Text[0-9]+', s):
        return False
    return True


def duzlestir(dosyalar, filtre=None):
    """-> {(tamYol, bolum, anahtar): deger}"""
    d = {}
    for yol, bolumler in dosyalar:
        if filtre and not filtre(yol):
            continue
        for bolum, degerler in bolumler:
            for k, v in degerler:
                d[(yol, bolum, k)] = v
    return d
