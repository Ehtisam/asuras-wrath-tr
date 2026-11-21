# -*- coding: utf-8 -*-
r"""Asura's Wrath - Turkce Yama Kurucusu

Bu script oyun dosyasi ICERMEZ. Senin kendi oyun dosyani okur, icindeki
metinleri Turkce karsiliklariyla degistirir ve sonucu yine senin klasorune
yazar. Once otomatik yedek alir.

KULLANIM
    python yamala.py "<oyun klasoru>"
    python yamala.py "<oyun klasoru>" --sade
    python yamala.py "<oyun klasoru>" --dlc "<dlc klasoru>"
    python yamala.py "<oyun klasoru>" --geri-al

<oyun klasoru> = icinde BCGame\CookedXbox360\ olan klasor

MODLAR
    (varsayilan)  Almanca yuvaya yazar. c o u gercek gorunur.
                  Konsol dilini Almanca yapman gerekir.
    --sade        Ingilizce yuvaya yazar. Tum ozel harfler ASCII olur.
                  Dil ayari degistirmene gerek yok.

GEREKSINIM: Python 3.8+
"""
import hashlib
import json
import os
import shutil
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BURASI, 'arac'))
import coalesced
import kapsam

# Fontta bulunmayan harfler icin indirgeme haritalari
SADE = {'ı': 'i', 'İ': 'I', 'ş': 's', 'Ş': 'S', 'ğ': 'g', 'Ğ': 'G',
        'ç': 'c', 'Ç': 'C', 'ö': 'o', 'Ö': 'O', 'ü': 'u', 'Ü': 'U',
        'â': 'a', 'Â': 'A', 'î': 'i', 'Î': 'I', 'û': 'u', 'Û': 'U'}
# Almanca fontta c o u VAR, i s g YOK
YARI = {'ş': 's', 'Ş': 'S', 'ğ': 'g', 'Ğ': 'G', 'İ': 'I', 'ı': 'i'}

ALT_YOL = os.path.join('BCGame', 'CookedXbox360')


def hashla(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:16]


def indirge(s, harita):
    return ''.join(harita.get(c, c) for c in s)


def sozlukleri_yukle(sade):
    """-> (oyun_sozlugu, motor_sozlugu)

    Ikisi AYRI tutulur: motor metinleri (Yes/No/LOADING gibi) 'engine'
    kapsamina, oyun metinleri 'ana'/'defaultfont' kapsamina uygulanir.
    Motor tarafinda kisa-metin filtresi CALISMAZ -- 'yes'/'no' gibi
    3 harfli degerler aksi halde atlanirdi.
    """
    kok = os.path.join(BURASI, 'ceviri')
    harita = SADE if sade else YARI

    def yukle(ad):
        yol = os.path.join(kok, ad)
        if not os.path.exists(yol):
            return {}
        return json.load(open(yol, encoding='utf-8'))

    oyun = yukle('sozluk.json')
    oyun.update(yukle('dlc_sozluk.json'))
    motor = yukle('motor_sozluk.json')

    return ({k: indirge(v, harita) for k, v in oyun.items()},
            {k: indirge(v, harita) for k, v in motor.items()})


def yedekle(yol):
    yedek = yol + '.turkceyama_yedek'
    if not os.path.exists(yedek):
        shutil.copy2(yol, yedek)
        return True
    return False


def geri_al(cooked):
    n = 0
    for ad in os.listdir(cooked):
        if ad.endswith('.turkceyama_yedek'):
            hedef = os.path.join(cooked, ad[:-len('.turkceyama_yedek')])
            shutil.copy2(os.path.join(cooked, ad), hedef)
            os.remove(os.path.join(cooked, ad))
            print('   geri alindi: %s' % os.path.basename(hedef))
            n += 1
    return n


def ana_oyun(cooked, sozluk, motor_sozluk, sade):
    # Ingilizce metnin kaynagi. Daha once --sade ile kurulum yapildiysa
    # Coalesced_INT.bin artik Turkce olur; o yuzden yedek varsa ONU kullan.
    int_yol = os.path.join(cooked, 'Coalesced_INT.bin')
    int_yedek = int_yol + '.turkceyama_yedek'
    if os.path.exists(int_yedek):
        int_yol = int_yedek
    if not os.path.exists(int_yol):
        print('HATA: Coalesced_INT.bin bulunamadi: %s' % cooked)
        return False

    hedef_ad = 'Coalesced_INT.bin' if sade else 'Coalesced_DEU.bin'
    hedef_yol = os.path.join(cooked, hedef_ad)
    if not os.path.exists(hedef_yol):
        print('HATA: %s bulunamadi.' % hedef_ad)
        return False

    print('  okunuyor : %s' % os.path.basename(int_yol))
    kaynak = coalesced.load(int_yol)          # Ingilizce metnin kaynagi
    hedef = coalesced.load(hedef_yol)         # yazilacak yapi

    if len(kaynak) != len(hedef):
        print('HATA: dosya yapilari uyusmuyor. Oyun surumu farkli olabilir.')
        return False

    # Ingilizce tarafta hangi pozisyon hangi Turkce metni alacak
    pozisyon = {}
    ad_ile = {}
    for fi, (yol, bolumler) in enumerate(kaynak):
        g = kapsam.grup(yol)
        for si, (bolum, degerler) in enumerate(bolumler):
            for vi, (k, v) in enumerate(degerler):
                t = None
                if g in ('ana', 'defaultfont') and kapsam.cevrilmeli(v):
                    t = sozluk.get(hashla(v))
                elif g == 'engine':
                    # motor metinlerinde kisa-metin filtresi UYGULANMAZ
                    t = motor_sozluk.get(hashla(v))
                if t:
                    pozisyon[(fi, si, vi)] = t
                    if g == 'ana':
                        ad_ile[(bolum, k)] = t

    cevrilen = 0
    yeni = []
    for fi, (yol, bolumler) in enumerate(hedef):
        g = kapsam.grup(yol)
        yb = []
        for si, (bolum, degerler) in enumerate(bolumler):
            yd = []
            for vi, (k, v) in enumerate(degerler):
                nv = v
                if g in ('ana', 'engine'):
                    t = pozisyon.get((fi, si, vi))
                    if t:
                        nv = t
                        cevrilen += 1
                elif g == 'defaultfont':
                    t = ad_ile.get((bolum, k)) or pozisyon.get((fi, si, vi))
                    if t:
                        nv = t
                        cevrilen += 1
                yd.append((k, nv))
            yb.append((bolum, yd))
        yeni.append((yol, yb))

    if yedekle(hedef_yol):
        print('  yedek    : %s.turkceyama_yedek' % hedef_ad)
    coalesced.save(hedef_yol, yeni)

    # geri okuyup dogrula
    kontrol = coalesced.load(hedef_yol)
    if len(kontrol) != len(hedef):
        print('HATA: yazilan dosya geri okunamadi!')
        return False

    print('  yazildi  : %s  (%d satir cevrildi)' % (hedef_ad, cevrilen))
    return True


def dlc_yamala(dlc_kok, sozluk, sade):
    sys.path.insert(0, os.path.join(BURASI, 'arac'))
    from stfs import STFS

    IMZA = {'DLCBIGEXPAND': 'Part IV (Nirvana)',
            'DLCCOLLABO01': 'Lost Episodes 1 (Ryu)',
            'DLCCOLLABO02': 'Lost Episodes 2 (Akuma)'}
    uzanti = 'int' if sade else 'deu'

    def kv_coz(ham):
        r = []
        for satir in ham.decode('utf-16-le', errors='replace').split('\r\n'):
            t = satir.lstrip('﻿')
            if t.strip() and not t.strip().startswith((';', '[')) and '=' in t:
                a, v = t.split('=', 1)
                r.append((satir, a.strip(), v))
            else:
                r.append((satir, None, None))
        return r

    bulunan = 0
    for ad in sorted(os.listdir(dlc_kok)):
        tam = os.path.join(dlc_kok, ad)
        if not os.path.isfile(tam) or ad.endswith('.turkceyama_yedek'):
            continue
        try:
            s = STFS(tam)
        except Exception:
            continue
        adlar = set(g['ad'] for g in s.dosyalar)
        etiket = None
        for imza, e in IMZA.items():
            if imza in adlar:
                etiket = e
                break
        if etiket is None:
            continue
        bulunan += 1

        icerik = {g['ad']: g for g in s.dosyalar}
        isler = []
        for g in s.dosyalar:
            if not g['ad'].lower().endswith('.' + uzanti):
                continue
            if 'credittitle' in g['ad'].lower():
                continue
            kok = g['ad'].rsplit('.', 1)[0]
            en_ad = kok + '.int'
            if en_ad not in icerik:
                continue
            en_harita = {k: v for _, k, v in kv_coz(s.oku(icerik[en_ad])) if k}
            yeni_satirlar = []
            n = 0
            for satir, k, v in kv_coz(s.oku(g)):
                if k is None:
                    yeni_satirlar.append(satir)
                    continue
                en = en_harita.get(k)
                t = sozluk.get(hashla(en)) if en else None
                if t:
                    yeni_satirlar.append('%s=%s' % (k, t))
                    n += 1
                else:
                    yeni_satirlar.append(satir)
            govde = '\r\n'.join(yeni_satirlar)
            if not govde.startswith('﻿'):
                govde = '﻿' + govde
            veri = govde.encode('utf-16-le')
            if (len(veri) + 0xFFF) // 0x1000 <= g['blok_sayisi']:
                isler.append((g, veri, n))

        if not isler:
            print('  [--] %-24s uygun dosya yok' % etiket)
            continue

        if yedekle(tam):
            print('       yedek aliniyor (%.0f MB)...' % (os.path.getsize(tam) / 1048576))
        toplam = 0
        for g, veri, n in isler:
            s.yaz(g, veri)
            toplam += n
        print('  [OK] %-24s %d dosya, %d satir' % (etiket, len(isler), toplam))

    return bulunan


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sade = '--sade' in sys.argv
    geri = '--geri-al' in sys.argv
    dlc_kok = None
    if '--dlc' in sys.argv:
        i = sys.argv.index('--dlc')
        if i + 1 < len(sys.argv):
            dlc_kok = sys.argv[i + 1]
            if dlc_kok in args:
                args.remove(dlc_kok)

    if not args:
        print(__doc__)
        return 1

    oyun = args[0]
    cooked = os.path.join(oyun, ALT_YOL)
    if not os.path.isdir(cooked):
        print('HATA: %s bulunamadi.' % cooked)
        print('Oyun klasorunu ver (icinde BCGame klasoru olan).')
        return 1

    print('=' * 62)
    print("  Asura's Wrath - Turkce Yama")
    print('=' * 62)
    print('Oyun : %s' % oyun)

    if geri:
        print()
        print('GERI ALMA')
        n = geri_al(cooked)
        if dlc_kok and os.path.isdir(dlc_kok):
            n += geri_al(dlc_kok)
        print()
        print('%d dosya geri alindi.' % n if n else 'Geri alinacak yedek bulunamadi.')
        return 0

    print('Mod  : %s' % ('SADE (Ingilizce yuva, tum harfler ASCII)' if sade
                         else 'ONERILEN (Almanca yuva, c o u gercek)'))
    print()

    sozluk, motor_sozluk = sozlukleri_yukle(sade)
    print('Sozluk: %d oyun + %d motor karsiligi'
          % (len(sozluk), len(motor_sozluk)))
    print()
    print('ANA OYUN')
    if not ana_oyun(cooked, sozluk, motor_sozluk, sade):
        return 1

    if dlc_kok:
        print()
        print('DLC')
        if not os.path.isdir(dlc_kok):
            print('  HATA: DLC klasoru bulunamadi: %s' % dlc_kok)
        else:
            n = dlc_yamala(dlc_kok, sozluk, sade)
            if n == 0:
                print('  DLC paketi bulunamadi. Yolu kontrol et.')

    print()
    print('=' * 62)
    print('TAMAM.')
    if not sade:
        print()
        print('SIMDI: Xenia ayarlarindan konsol dilini ALMANCA yap.')
        print('Yoksa Turkce metin gorunmez.')
    print()
    print('Geri almak icin:  python yamala.py "%s" --geri-al' % oyun)
    print('=' * 62)
    return 0


if __name__ == '__main__':
    sys.exit(main())
