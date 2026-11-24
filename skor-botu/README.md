# Skor tahmin botu

Her sabah 09:17'de (Türkiye saati) iddaa bültenindeki o günün **tüm futbol maçlarını** tahmin eder ve Telegram'a gönderir.

## Telegram'a ne gelir

- **En net 10 tahmin:** Modelin en emin olduğu maçlar, iddaa oranıyla birlikte.
- **Oranı modelden yüksek olanlar:** Modelin olasılığı × iddaa oranı belirgin şekilde 1'in üstünde olan seçenekler (maç sonucu, 2.5 alt/üst, karşılıklı gol).
- **Türkiye maçlarının tamamı:** Tahmini skor, 1-X-2, 2.5 üst, KG ve önemli eksik oyuncular.
- **Ek dosya (tam bülten):** Bültendeki her maç için model olasılıkları, iddaa oranları ve orandan çıkan gerçek olasılık, xG, ilk yarı, son 5 maç formu, aralarındaki son maçlar, sakat/cezalı oyuncular ve MBS. Telefonda açılır, takım ya da lig aranabilir.

## Veri kaynakları

| Kaynak | Ne için |
|---|---|
| iddaa.com bülteni | Günün maçları, oranlar, MBS |
| Maçkolik canlı sonuçlar | iddaa'da oynanan tüm turnuvaların maç sonuçları (Türkiye'de Süper Lig'den 3. Lig'e, PGL ve amatöre kadar). Her maçta iddaa kodu olduğu için bülten maçlarıyla birebir eşleşir |
| Maçkolik maç sayfası | Sakat ve cezalı oyuncular (oynadığı maç ve gol sayısıyla); Maçkolik GitHub'dan gelen isteklerin bir kısmını reddettiği için her gün tüm maçlarda gelmeyebilir |
| football-data.co.uk | Eski sezonlar: İngiltere (4 lig + National League), İskoçya (4), Almanya, İtalya, İspanya, Fransa (2'şer), Hollanda, Belçika, Portekiz, Türkiye, Yunanistan; ayrıca Arjantin, Avusturya, Brezilya, Çin, Danimarka, Finlandiya, İrlanda, Japonya, Meksika, Norveç, Polonya, Romanya, İsveç, İsviçre, ABD |
| tff.org | Bu sezonun Süper Lig, 1. Lig, 2. Lig ve 3. Lig maçları (tüm gruplar) |
| [penaltyblog](https://github.com/martineastwood/penaltyblog) | iddaa oranlarındaki kâr payını çıkarıp gerçek olasılığı hesaplamak (Shin yöntemi) |

## Model

- Her takımın hücum ve savunma gücü geçmiş maçlardan hesaplanır, yakın tarihli maçlar daha ağır sayılır (Poisson + Dixon-Coles).
- Eski sezon kaynaklarındaki takımlar Maçkolik takımlarına iki yolla bağlanır: son haftalarda iki tarafta da görünen ortak maçlar (aynı gün, aynı skor, benzer ad) ve bugün/yarın oynayacak takımlar için ad benzerliği. Arşiv büyüdükçe eşleşme artar.
- Kupa ve Avrupa maçlarında farklı liglerin gücü henüz yeterli veriyle karşılaştırılamadığı için model, iddaa oranlarından çıkan olasılıkla yarı yarıya harmanlanır ve bu maçlar "oranı modelden yüksek" listesine alınmaz. Modelin orandan çok uzaklaştığı seçenekler de (muhtemelen eksik veri) bu listeye girmez.
- Eksik oyuncular: oyuncunun oynadığı maç oranı ve attığı gollerin takım içindeki payına göre hücum en çok %25 düşürülür, kaleci/defans eksikliğinde savunma en çok %25 zayıflatılır. Bu kaba bir kuraldır, geçmiş verilerle test edilmedi.
- Son bir yılda 5'ten az maçı olan takımlar için tahmin yapılmaz ("yetersiz veri"), yalnızca oranlar gösterilir.
- Geriye dönük test (Avrupa ligleri, Ağustos 2025'ten bu yana): 1-X-2 isabeti ortalama %54. penaltyblog'un Dixon-Coles modeli de aynı maçlarda denendi; Premier League, La Liga ve Bundesliga'da bu modelden biraz daha zayıf kaldığı için kullanılmadı.

Tahminler olasılıktır, kesin sonuç değildir.

## Kurulum (bir kez)

1. **Botu oluşturun:** Telegram'da `@BotFather`'a yazın, `/newbot` deyin, bir ad verin. Size verdiği uzun anahtarı (token) kopyalayın.
2. **Sohbet kimliğini bulun:** Yeni botunuza herhangi bir mesaj atın. Sonra tarayıcıda `https://api.telegram.org/bot<TOKEN>/getUpdates` adresini açın. `"chat":{"id":123456789` kısmındaki sayı sohbet kimliğinizdir. Bir kanala göndermek için botu kanala yönetici yapın ve kimlik olarak `@kanaladi` yazın.
3. **GitHub'a kaydedin:** Depoda *Settings → Secrets and variables → Actions → New repository secret*:
   - `TELEGRAM_TOKEN` = BotFather'ın verdiği anahtar
   - `TELEGRAM_CHAT_ID` = sohbet kimliği (birden fazlaysa virgülle ayırın)
4. **Deneyin:** *Actions → Skor tahmin botu → Run workflow*.

## Notlar

- Maçkolik GitHub sunucularına yalnızca yaklaşık son 4 haftanın sonuçlarını veriyor. Bu yüzden arşiv `data/mackolik/` klasöründe birikir ve her gün büyür; ilk haftalarda tahminler az veriyle yapılır, mesajda uyarı çıkar.
- Her günün tahminleri `data/tahminler/` klasörüne kaydedilir (ileride isabet raporu için).
- Tam bülten dosyası Telegram'a gelmese bile Actions çalıştırmasının sayfasında "tahmin-bulteni" adıyla 14 gün durur.
- Yerelde denemek için: `pip install -r requirements.txt` ve `python run.py --dry-run`. Belirli bir gün için `--date 2026-11-24`.
