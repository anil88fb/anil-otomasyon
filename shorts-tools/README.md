# shorts-tools

Shorts üretimine (Why? ve Tuhaf Tahsin) eklenen, açık kaynak projelere dayanan yardımcı araçlar.
Hepsi bulut oturumunda çalışır: modeller GitHub sürümlerinden iner, Hugging Face'e gerek yok.

## Kurulum (oturum başına bir kez)

```bash
bash shorts-tools/kurulum.sh          # ~1-2 dk; Whisper small modeli ~640 MB indirip ~300 MB'ını tutar
```

## Araçlar

| Araç | Ne yapar | Dayandığı proje |
|---|---|---|
| `zamanla.py` | Seslendirmeyi kelime kelime zamanlar, `words.json` / `phrases.json` / `altyazi.srt` üretir. **Çevrimdışı Whisper**: bulutta "Whisper modeli indirilemedi, NO_WHISPER" sorununu çözer. Müzikli seste de çalışır. | k2-fsa/sherpa-onnx (Whisper small + Silero VAD) |
| `kontrol.py` | Bitmiş MP4'ü yüklemeden önce denetler: 1080x1920, süre, ses yüksekliği (LUFS), ilk sesin başladığı an, kesme sıklığı, dosya boyutu. `--duzelt` sesi -14 LUFS'a çeker, `--sikistir` dosyayı küçültür. | Breakthrough/PySceneDetect, FFmpeg loudnorm |
| `ritim.py` | Fon müziğinin vuruşlarını ve en güçlü vurgularını bulur; sahne geçişlerini ve "GÜMM" anlarını müziğe oturtmak için. | librosa/librosa |
| `earshot` (komut) | Yazıyla ses efekti üretir: "a cartoon boing when a character jumps", "crowd cheering, 3 seconds". 922 tasarım, model indirmez, kredi harcamaz. Kullanımı `.claude/skills/earshot` becerisinde. | Leonxlnx/earshot |
| `dekupe.py` | Görselin arka planını kaldırır (şeffaf PNG); kullanıcı fotoğrafı, ürün, nesne görselini sahneye koymak için. `--kenar` ile çıkartma (sticker) konturu. | danielgatis/rembg |

## Kullanım örnekleri

```bash
# 1) Seslendirmeyi zamanla (senaryo ile)
python3 shorts-tools/zamanla.py work/voice.wav --metin script.txt --cikti work
#   -> cizgi-short ve shorts-engine'in beklediği words.json / phrases.json biçiminde

# 2) Müziğin vuruşlarını çıkar
python3 shorts-tools/ritim.py muzik.wav --cikti work/beats.json

# 3) Render bitince denetle, gerekirse düzelt ve küçült
python3 shorts-tools/kontrol.py out/video.mp4 --duzelt --sikistir

# 4) Ses efekti üret (ücretsiz, çevrimdışı)
earshot make "a big low whoosh transition" -o work/sfx/whoosh.ogg

# 5) Görselden arka planı kaldır
python3 shorts-tools/dekupe.py gorseller/ --cikti gorseller/dekupe          # çizim ve fotoğrafta isnet-general-use (varsayılan) en iyisi
```

## cizgi-short (Tuhaf Tahsin) ile kullanım

`timing.py` Whisper bulamayınca sessizlik + hece tahminine düşüyordu. Artık önce:

```bash
python3 <anil-otomasyon>/shorts-tools/zamanla.py ~/ya-olsaydi/<bolum>/work/voice.wav \
  --metin ~/ya-olsaydi/<bolum>/script.txt --cikti ~/ya-olsaydi/<bolum>/work
```

çalıştır; aynı `words.json` / `phrases.json` dosyalarını yazar, `timing.py`'yi çalıştırmana gerek kalmaz.

## Eklenen Claude becerileri

- `turkish-anti-ai-skill`: Tuhaf Tahsin senaryolarındaki çeviri kokusunu ve yapay zekâ izlerini temizler.
- `motion-design`: zamanlama, easing ve hareket ilkeleri (hyperframes ve shorts-engine sahneleri için).
- `earshot`: ses efekti üretimi.

## Bilinen sınırlar

- Whisper kelime zamanlarını doğrudan vermez; konuşma parçaları (VAD) gerçek, parça içindeki kelimeler
  hece sayısına göre dağıtılır. Altyazı ve sahne zamanlaması için yeterli, dudak senkronu için kaba.
- Kısa parçalarda sherpa-onnx "token limit" uyarısı basabilir; senaryo eşleştirmesi bunu telafi eder.
- edge-tts (Microsoft sesleri), YouTube indirme (yt-dlp) ve Hugging Face modelleri bulut proxy'sinde engelli;
  bu yüzden pakete alınmadı. Kendi bilgisayarında çalışırlar.
- `readbeyond/aeneas` (metin-ses hizalama) denendi: Türkçe espeak sesiyle müzikli seste kayıyor, alınmadı.
