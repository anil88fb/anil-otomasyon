# Skor tahmin botu

Her sabah 09:17'de (Türkiye saati) o günün maçlarını tahmin eder ve Telegram'a gönderir.

**Ligler**
- Türkiye: Süper Lig, 1. Lig, 2. Lig (tüm gruplar), 3. Lig (tüm gruplar). Kaynak: tff.org
- Avrupa: Premier League, Championship, La Liga, Bundesliga, Serie A, Ligue 1, Eredivisie, Liga Portugal, Belçika, İskoçya, Yunanistan. Kaynak: football-data.co.uk

**Her maç için:** en olası skor, 1-X-2 olasılıkları, 2.5 üst, karşılıklı gol ve iki takımın son 5 maç formu. Mesajın sonunda günün en net 5 tahmini yer alır.

**Model:** Her takımın hücum ve savunma gücü geçmiş maçlardan hesaplanır, yakın tarihli maçlar daha ağır sayılır (Poisson + Dixon-Coles). Avrupa liglerinde Ağustos 2025'ten bu yana yapılan geriye dönük testte 1-X-2 isabeti ortalama %54 çıktı. Tahminler olasılıktır, kesin sonuç değildir.

## Kurulum (bir kez)

1. **Botu oluşturun:** Telegram'da `@BotFather`'a yazın, `/newbot` deyin, bir ad verin. Size verdiği uzun anahtarı (token) kopyalayın.
2. **Sohbet kimliğini bulun:** Yeni botunuza Telegram'dan herhangi bir mesaj atın. Sonra tarayıcıda `https://api.telegram.org/bot<TOKEN>/getUpdates` adresini açın (TOKEN yerine anahtarınızı yazın). Çıkan yazıda `"chat":{"id":123456789` kısmındaki sayı sohbet kimliğinizdir. Bir kanala göndermek isterseniz botu kanala yönetici yapın ve kimlik olarak `@kanaladi` yazın.
3. **GitHub'a kaydedin:** Depoda *Settings → Secrets and variables → Actions → New repository secret*:
   - `TELEGRAM_TOKEN` = BotFather'ın verdiği anahtar
   - `TELEGRAM_CHAT_ID` = sohbet kimliği (birden fazlaysa virgülle ayırın)
4. **Deneyin:** *Actions → Skor tahmin botu → Run workflow*. Birkaç dakika içinde mesaj gelir.

## Notlar

- İlk çalıştırma TFF'deki tüm haftaları indirdiği için 3–5 dakika sürer; sonraki günler yalnızca açık haftaları çeker. İndirilen veri `data/tff/` klasörüne kaydedilir.
- Bir lig alınamazsa diğerleri yine gönderilir, mesajın sonunda uyarı yer alır.
- Yerelde denemek için: `pip install -r requirements.txt` ve `python run.py --dry-run`.
