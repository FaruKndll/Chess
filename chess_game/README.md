# Satranç Oyunu

Bu proje, insan oyuncunun yapay zekaya karşı oynayabileceği bir satranç oyunudur.

## Özellikler

- İnsan oyuncu beyaz taşlarla, yapay zeka siyah taşlarla oynar
- Klasik satranç kurallarına uygun hareket sistemi
- Şah çekme durumu otomatik olarak tespit edilir ve bildirilir
- Piyon terfi sistemi
- Algebraic notasyon ile hamle kaydı
- Basit yapay zeka sistemi

## Kurulum

1. Python 3.8 veya daha yüksek bir sürümü yükleyin
2. Gerekli kütüphaneleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

## Oyunu Çalıştırma

```
python chess_game.py
```

## Nasıl Oynanır

1. Beyaz taşlarla başlarsınız
2. Oynamak istediğiniz taşa tıklayın
3. Taşı götürmek istediğiniz kareye tıklayın
4. Yapay zeka otomatik olarak hamlesini yapacaktır
5. Piyon son sıraya ulaştığında, terfi seçenekleri sunulacaktır

## Özel Durumlar

- Şah çekildiğinde otomatik olarak uyarı verilir
- Şah mat olduğunda oyun sona erer ve kazanan ilan edilir
- Pat durumunda oyun berabere biter
