"""Asura's Wrath (UE3 "BC") Coalesced .bin okuma/yazma.

Format:
    int32  dosyaSayisi                       (big-endian)
    her dosya icin:
        FString dosyaAdi
        int32   bolumSayisi                  (big-endian)
        her bolum icin:
            FString bolumAdi
            int32   degerSayisi              (big-endian)
            her deger icin: FString anahtar, FString deger

FString: int32 uzunluk (big-endian).
    n < 0  -> -n adet UTF-16 LITTLE-endian karakter (null sonlandirici dahil)
    n > 0  -> n byte latin-1/ASCII (null sonlandirici dahil)
    n == 0 -> bos string, hic veri yok
Oyunun kendi dosyalari ISTISNASIZ UTF-16 kullanir (42668 string, 0 ASCII),
bu yuzden yazarken varsayilan force_utf16=True; boylece round-trip byte-exact.
DIKKAT: sayilar big-endian ama string govdeleri little-endian. Karma endian.
"""
import struct

class Reader:
    def __init__(self, data):
        self.d = data
        self.o = 0

    def i32(self):
        v = struct.unpack_from('>i', self.d, self.o)[0]
        self.o += 4
        return v

    def string(self):
        n = self.i32()
        if n == 0:
            return ''
        if n < 0:
            raw = self.d[self.o:self.o - n * 2]
            self.o += -n * 2
            s = raw.decode('utf-16-le')
        else:
            raw = self.d[self.o:self.o + n]
            self.o += n
            s = raw.decode('latin-1')
        return s[:-1] if s.endswith('\x00') else s


class Writer:
    def __init__(self):
        self.parts = []

    def i32(self, v):
        self.parts.append(struct.pack('>i', v))

    def string(self, s, force_utf16=True):
        if s == '':
            self.i32(0)
            return
        body = s + '\x00'
        ascii_ok = not force_utf16 and all(ord(c) < 128 for c in body)
        if ascii_ok:
            self.i32(len(body))
            self.parts.append(body.encode('latin-1'))
        else:
            self.i32(-len(body))
            self.parts.append(body.encode('utf-16-le'))

    def data(self):
        return b''.join(self.parts)


def load(path):
    """-> [(dosyaAdi, [(bolumAdi, [(anahtar, deger), ...]), ...]), ...]"""
    r = Reader(open(path, 'rb').read())
    files = []
    for _ in range(r.i32()):
        name = r.string()
        secs = []
        for _ in range(r.i32()):
            sname = r.string()
            secs.append((sname, [(r.string(), r.string()) for _ in range(r.i32())]))
        files.append((name, secs))
    if r.o != len(r.d):
        raise ValueError('parse artigi: %d / %d' % (r.o, len(r.d)))
    return files


def save(path, files, force_utf16=True):
    w = Writer()
    w.i32(len(files))
    for name, secs in files:
        w.string(name, force_utf16)
        w.i32(len(secs))
        for sname, vals in secs:
            w.string(sname, force_utf16)
            w.i32(len(vals))
            for k, v in vals:
                w.string(k, force_utf16)
                w.string(v, force_utf16)
    open(path, 'wb').write(w.data())
