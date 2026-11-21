# Asura's Wrath Türkçe Yama (Xbox 360)

Asura's Wrath'in Xbox 360 sürümü için bir Türkçe yama. Ana oyunu ve üç DLC bölümünü kapsar. Xenia emülatöründe denendi.

Bu depoda oyun dosyası bulunmaz. Yama, senin bilgisayarındaki oyun dosyalarını okur ve çeviriyi orada uygular.

## Kapsam

| İçerik | Durum |
|---|---|
| Ana oyun (diyaloglar, menüler, koleksiyon, sistem mesajları) | Çevrildi |
| Part IV: Nirvana (DLC) | Çevrildi |
| Lost Episodes 1: Ryu (DLC) | Çevrildi |
| Lost Episodes 2: Akuma (DLC) | Çevrildi |
| Jenerik (çalışanların adları) | Çevrilmedi |

Toplam 3854 benzersiz çeviri. Oyundaki çevrilebilir metnin tamamı.

## Kurulum

Python 3.8 ya da üstü gerekir.

```bash
git clone https://github.com/Ehtisam/asuras-wrath-tr.git
cd asuras-wrath-tr
python yamala.py "C:\yol\AsurasWrath"
```

Ardından Xenia'nın konsol dilini Almanca yap. Sebebi aşağıda.

DLC'ler de kuruluysa:

```bash
python yamala.py "C:\yol\AsurasWrath" --dlc "C:\Xenia\content\0000000000000000\43430817\00000002"
```

Yamayı geri almak için:

```bash
python yamala.py "C:\yol\AsurasWrath" --geri-al
```

Ayrıntılı anlatım: [KURULUM.md](KURULUM.md)

## Konsol dili neden Almanca

Oyunun İngilizce yazı tipi paketinde Türkçeye özgü harflerin hiçbiri yok, `ç ö ü` bile. Almanca yazı tipi paketinde ise bunlar zaten bulunuyor.

Bu yüzden yama Türkçe metni Almanca dil yuvasına yazar. Konsol dili Almanca seçilince oyun o yazı tipini kullanır ve `ç Ç ö Ö ü Ü` düzgün görünür. Oyunun metni Türkçe kalır, Almanca dilden yalnızca yazı tipi alınır.

`ı ş ğ İ Ş Ğ` harfleri hiçbir Batı Avrupa dilinde bulunmadığı için o yazı tipinde de yok. Bu harfler ASCII karşılıklarıyla (`i s g I S G`) yazılır.

Dil ayarıyla uğraşmak istemeyenler için:

```bash
python yamala.py "C:\yol\AsurasWrath" --sade
```

Bu mod İngilizce dil yuvasına yazar ve bütün Türkçe harfleri ASCII karşılıklarına çevirir. Dil ayarı gerekmez ancak `ç ö ü` de kaybolur.

## Bilinen sınırlar

- `ı ş ğ İ Ş Ğ` harfleri ASCII karşılıklarıyla yazılır. Çözümü, yazı tipi paketine yeni harf çizimleri eklemek. Bu denendi ancak paket sıkıştırılmış olduğu ve mevcut araçlar bu biçimi düzenleyemediği için tamamlanamadı.
- Burst göstergesindeki büyük yazı ve kombo sayacı gibi bazı ekran yazıları birer çizim olarak dokuya (texture) gömülü. Bunlar metin düzenlemesiyle değişmez.
- Açılıştaki otomatik kayıt uyarısı emülatörün ya da konsolun sistem penceresinden gelir. Oyun dosyasıyla değiştirilemez.
- Jenerik bir isim listesi olduğu için İngilizce kalır.
- Türkçe kelimeler İngilizcedekilerden uzun olduğu için birkaç menü metni kutusuna sığmayabilir. Bu oynanışı etkilemez.

## Nasıl çalışır

Oyunun bütün metni `Coalesced_<DIL>.bin` adlı bir veritabanında durur. DLC bölümlerinin metni DLC paketlerinin kendi içindedir ve ana veritabanının üzerine yazılır.

`yamala.py` sırasıyla şunları yapar:

1. `Coalesced_INT.bin` dosyasını (İngilizce kaynak) okur.
2. Her metnin özetini (hash) çıkarıp depodaki sözlükte karşılığını arar.
3. Sonucu `Coalesced_DEU.bin` olarak oyun klasörüne yazar.
4. `--dlc` verildiyse DLC paketlerinin içindeki metin dosyalarını da günceller.

Yazmadan önce değişen her dosyanın yedeğini (`.turkceyama_yedek`) alır.

`ceviri/*.json` dosyalarında anahtar olarak İngilizce metnin kendisi yerine SHA-1 özeti kullanılır. Böylece depoda oyunun senaryosu bulunmaz, yalnızca Türkçe çeviri bulunur. Yama, oyundaki metnin özetini çıkarıp sözlükle eşleştirir.

## Klasörler

```
yamala.py              kurulum betiği
arac/                  dosya biçimi okuyucuları (Coalesced, STFS)
ceviri/                çeviri sözlükleri
KURULUM.md             ayrıntılı kurulum
DISCLAIMER.md          yasal durum
```

## Teşekkür

Çevirinin bir bölümü, PS3 sürümü için yapılmış Türkçe fan yamasını temel alır. O çeviriyi yapanlara teşekkürler. Kalan metinler ve mevcut çevirinin yazım düzeltmeleri yapay zekâ destekli çeviri ve elle kontrolle tamamlandı.

## Lisans

- Araçlar: [MIT](LICENSE)
- Çeviri metinleri: Ücretsiz dağıtım, ticari kullanım dışı

Bu proje Capcom ya da CyberConnect2 ile ilişkili değildir ve onlar tarafından onaylanmamıştır. Ayrıntı: [DISCLAIMER.md](DISCLAIMER.md)
