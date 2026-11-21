# -*- coding: utf-8 -*-
r"""Xbox 360 STFS (CON/LIVE/PIRS) konteyneri icin minimal okuyucu.

DLC ve Title Update paketleri bu formatta. Icindeki dosya listesini cikarir
ve tek tek dosya cikarabilir.

Kullanim:
    python tools/stfs.py liste  <paket>
    python tools/stfs.py cikar  <paket> <dosyaAdi> <hedefYol>
"""
import struct, sys, os

BLOK = 0x1000
VERI_BASI = 0xC000


class STFS:
    def __init__(self, yol):
        self.f = open(yol, 'rb')
        sihir = self.f.read(4)
        if sihir not in (b'CON ', b'LIVE', b'PIRS'):
            raise ValueError('STFS degil: %r' % sihir)
        self.sihir = sihir.decode('ascii')

        self.f.seek(0x340)
        self.header_size = struct.unpack('>I', self.f.read(4))[0]

        # tablo kaydirma: hash tablolarinin blok cinsinden buyuklugu
        self.shift = 0 if (((self.header_size + 0xFFF) & 0xF000) >> 0xC) == 0xB else 1

        # volume descriptor
        self.f.seek(0x37C)
        self.ft_blok_sayisi = struct.unpack('<H', self.f.read(2))[0]
        self.ft_blok_no = struct.unpack('<I', self.f.read(3) + b'\x00')[0]

        self.dosyalar = self._dosya_tablosu()

    # --- blok adresleme (hash tablolari araya giriyor) ---
    def _gercek_blok(self, blok):
        ek = 0
        if blok >= 0xAA:
            ek += ((blok // 0xAA) + 1) << self.shift
        if blok >= 0x70E4:
            ek += ((blok // 0x70E4) + 1) << self.shift
        return ek + blok

    def _offset(self, blok):
        return VERI_BASI + self._gercek_blok(blok) * BLOK

    def _blok_oku(self, blok):
        self.f.seek(self._offset(blok))
        return self.f.read(BLOK)

    # --- dosya tablosu ---
    def _dosya_tablosu(self):
        ham = b''
        for i in range(self.ft_blok_sayisi):
            ham += self._blok_oku(self.ft_blok_no + i)

        girdiler = []
        for ham_indeks, o in enumerate(range(0, len(ham), 0x40)):
            g = ham[o:o + 0x40]
            if len(g) < 0x40:
                break
            bayrak = g[0x28]
            ad_uz = bayrak & 0x3F
            if ad_uz == 0:
                continue
            ad = g[:ad_uz].decode('latin-1')
            klasor_mu = bool(bayrak & 0x80)
            bitisik = bool(bayrak & 0x40)
            blok_sayisi = struct.unpack('<I', g[0x29:0x2C] + b'\x00')[0]
            bas_blok = struct.unpack('<I', g[0x2F:0x32] + b'\x00')[0]
            ust = struct.unpack('>H', g[0x32:0x34])[0]
            boyut = struct.unpack('>I', g[0x34:0x38])[0]
            girdiler.append({
                'ad': ad, 'klasor': klasor_mu, 'bitisik': bitisik,
                'blok_sayisi': blok_sayisi, 'bas_blok': bas_blok,
                'ust': ust, 'boyut': boyut,
                'ham_indeks': ham_indeks,      # dosya tablosundaki gercek sira
                'tablo_offset': o,             # tablo icindeki byte offseti
            })
        # tam yol coz -- 'ust' alani HAM tablo indeksini gosterir
        ham_ile = {g['ham_indeks']: g for g in girdiler}
        for g in girdiler:
            parcalar = [g['ad']]
            u = g['ust']
            kalan = 64
            while u != 0xFFFF and kalan > 0:
                ust_g = ham_ile.get(u)
                if ust_g is None:
                    break
                parcalar.append(ust_g['ad'])
                u = ust_g['ust']
                kalan -= 1
            g['yol'] = '/'.join(reversed(parcalar))
        return girdiler

    # --- yazma destegi ---
    def tablo_girdi_offseti(self, girdi):
        """Dosya tablosu girdisinin konteyner icindeki byte offseti."""
        o = girdi['tablo_offset']
        tablo_blok = o // BLOK
        return self._offset(self.ft_blok_no + tablo_blok) + (o % BLOK)

    def yaz(self, girdi, veri):
        """Dosya icerigini YERINDE degistirir. Blok sayisi degismemeli."""
        gereken = (len(veri) + BLOK - 1) // BLOK
        if gereken > girdi['blok_sayisi']:
            raise ValueError('yeni icerik daha fazla blok istiyor: %d > %d'
                             % (gereken, girdi['blok_sayisi']))
        f = open(self.f.name, 'r+b')
        try:
            # 1) veriyi bloklara yaz (son blogun kalanini sifirla)
            kalan = veri
            for i in range(girdi['blok_sayisi']):
                parca = kalan[:BLOK]
                kalan = kalan[BLOK:]
                f.seek(self._offset(girdi['bas_blok'] + i))
                f.write(parca + bytes(1) * (BLOK - len(parca)))
            # 2) dosya tablosundaki boyut alanini guncelle (+0x34, 4 byte BE)
            f.seek(self.tablo_girdi_offseti(girdi) + 0x34)
            f.write(struct.pack('>I', len(veri)))
        finally:
            f.close()
        girdi['boyut'] = len(veri)

    def oku(self, girdi):
        """Dosya icerigini dondurur."""
        veri = b''
        blok = girdi['bas_blok']
        kalan = girdi['boyut']
        for _ in range(girdi['blok_sayisi']):
            if kalan <= 0:
                break
            b = self._blok_oku(blok)
            veri += b[:min(BLOK, kalan)]
            kalan -= BLOK
            blok += 1          # bitisik varsayimi
        return veri[:girdi['boyut']]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    komut, paket = sys.argv[1], sys.argv[2]
    s = STFS(paket)
    if komut == 'liste':
        print('tur=%s  header=%d  shift=%d  dosya=%d'
              % (s.sihir, s.header_size, s.shift, len(s.dosyalar)))
        for g in s.dosyalar:
            print('%-9s %10d  %s' % ('<klasor>' if g['klasor'] else '', g['boyut'], g['yol']))
    elif komut == 'cikar':
        hedef_ad, hedef_yol = sys.argv[3], sys.argv[4]
        for g in s.dosyalar:
            if g['ad'] == hedef_ad or g['yol'] == hedef_ad:
                veri = s.oku(g)
                os.makedirs(os.path.dirname(hedef_yol) or '.', exist_ok=True)
                open(hedef_yol, 'wb').write(veri)
                print('cikarildi: %s -> %s (%d byte)' % (g['yol'], hedef_yol, len(veri)))
                return 0
        print('bulunamadi:', hedef_ad)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
