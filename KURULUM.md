# Kurulum

## Gerekenler

- **Asura's Wrath (Xbox 360)**, klasör olarak çıkarılmış hâlde.
  İçinde `BCGame\CookedXbox360\` olmalı. ISO ise önce klasöre çıkar.
  Xenia klasörden de çalışır ve ISO'yu yeniden paketlemene gerek yok.
- **Xenia** emülatörü (Canary sürümü test edildi)
- **Python 3.8+**: [python.org](https://www.python.org/downloads/)
  Kurulumda **"Add Python to PATH"** seçeneğini işaretle.

Python kurulu mu diye bakmak için:

```bash
python --version
```

---

## Hangi modu seçmeliyim

| | Önerilen | Sade |
|---|---|---|
| Komut | (bayraksız) | `--sade` |
| `ç Ç ö Ö ü Ü` | gerçek görünür | ASCII (`c C o O u U`) |
| `ı ş ğ İ Ş Ğ` | ASCII | ASCII |
| Emülatör ayarı | konsol dili **Almanca** olmalı | gerekmez |

Çoğu kişi için önerilen mod daha iyi. İki tıklık bir ayar karşılığında
metin belirgin biçimde daha okunaklı oluyor.

---

## Adım 1: Ana oyun

Depoyu indir:

```bash
git clone https://github.com/Ehtisam/asuras-wrath-tr.git
cd asuras-wrath-tr
```

Yamayı uygula:

```bash
python yamala.py "C:\yol\AsurasWrath"
```

Sade mod istiyorsan:

```bash
python yamala.py "C:\yol\AsurasWrath" --sade
```

Verdiğin yol, içinde `BCGame` klasörü olan klasör olmalı.

Çıktı şuna benzer:

```
ANA OYUN
  okunuyor : Coalesced_INT.bin
  yedek    : Coalesced_DEU.bin.turkceyama_yedek
  yazildi  : Coalesced_DEU.bin  (8324 satir cevrildi)
```

---

## Adım 2: Emülatör dili (sade mod kullanmadıysan)

Xenia'nın ayarlarından **konsol dilini Almanca** yap. Bu ayar Xbox 360'ın
panel dilini taklit eder. Xenia'nın kendi ayar menüsünde ya da
yapılandırma dosyasında bulunur.

Bu ayar yapılmazsa Türkçe metin görünmez ve oyun İngilizce açılır.

---

## Adım 3: DLC (kurduysan)

DLC bölümlerinin metni ana veritabanında bulunmaz. Bu metin DLC
paketlerinin kendi içindedir. Bu yüzden ayrı bir adım gerekir.

DLC klasörü Xenia'da genellikle şuradadır:

```
<Xenia klasörü>\content\0000000000000000\43430817\00000002
```

`43430817` oyunun kimliğidir. İçinde uzun harf-rakam adlı, uzantısız,
yüzlerce MB'lık dosyalar olmalı.

```bash
python yamala.py "C:\yol\AsurasWrath" --dlc "C:\Xenia\content\0000000000000000\43430817\00000002"
```

Sade mod kullandıysan aynı bayrağı buraya da ekle:

```bash
python yamala.py "C:\yol\AsurasWrath" --sade --dlc "C:\Xenia\...\00000002"
```

Çıktı:

```
DLC
       yedek aliniyor (1687 MB)...
  [OK] Part IV (Nirvana)        7 dosya, 570 satir
  [OK] Lost Episodes 1 (Ryu)    4 dosya, 105 satir
  [OK] Lost Episodes 2 (Akuma)  4 dosya, 100 satir
```

Kurulu olmayan DLC listede çıkmaz. Bu normaldir.

> **Dikkat:** DLC'lerin iki kopyası olabilir. Xenia kendi content
> klasöründen okur. Başka bir yerde sakladığın kopyayı yamalarsan
> oyunda hiçbir şey değişmez.

---

## Doğrulama

Oyunu aç ve şunlara bak:

- Ana menü ve bölüm isimleri Türkçe
- Onay pencerelerinde `Evet / Hayir / Tamam` (hâlâ `Ja / Nein / Okay`
  görüyorsan yama uygulanmamış)
- Önerilen mod kullandıysan `ç ö ü` harfleri düzgün
- DLC kurduysan: Part IV'te Chakravartin'in diyalogları Türkçe,
  Lost Episodes'ta görev açıklamaları Türkçe

---

## Geri alma

```bash
python yamala.py "C:\yol\AsurasWrath" --geri-al
```

DLC de yamaladıysan:

```bash
python yamala.py "C:\yol\AsurasWrath" --geri-al --dlc "C:\Xenia\...\00000002"
```

Yama, değiştirdiği her dosyanın yanına `.turkceyama_yedek` uzantılı bir
kopya bırakır. Geri alma bunları yerine koyar.

DLC yedekleri paketlerle aynı boyuttadır (birkaç GB tutabilir). Yamanın
çalıştığından emin olduktan sonra bu yedekleri silebilirsin. Yedekler
silindikten sonra geri dönmek için oyunu/DLC'yi yeniden kurman gerekir.

---

## Sorun giderme

**`python` komutu bulunamadı**
Python kurulu değil ya da PATH'e eklenmemiş. Yeniden kurarken
"Add Python to PATH" seçeneğini işaretle.

**`BCGame\CookedXbox360 bulunamadi`**
Yanlış klasör verdin. İçinde `BCGame` klasörü olan klasörü ver. Bir üst
ya da bir alt klasör çalışmaz.

**Hiçbir şey Türkçe görünmüyor**
- Xenia'yı tamamen kapatıp yeniden aç (yalnızca oyunu kapatmak yetmez)
- Sade mod kullanmıyorsan konsol dilinin Almanca olduğunu kontrol et

**Ana oyun Türkçe ancak DLC bölümleri çevrilmemiş görünüyor**
Adım 3'ü uygulamadın ya da yanlış klasöre uyguladın. Xenia'nın kendi
content klasörünü kullandığından emin ol.

**Türkçe karakterler boş kutu ya da boşluk görünüyor**
`--sade` moduna geç. O modda hiç özel karakter kullanılmaz. Ana oyunu ve
DLC'yi aynı modla kurmayı unutma.

**`dosya yapilari uyusmuyor` hatası**
Oyun sürümün beklenenden farklı. Sorun bildir ve hangi sürümü
kullandığını yaz.

**Oyun siyah ekranda kalıyor**
Bu yama `Startup_LOC_*.xxx` dosyalarına dokunmaz. Onlardan birini elle
değiştirdiysen geri al.
