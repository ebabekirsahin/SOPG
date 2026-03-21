# ⚽ Betting Data Analyst Pro

Gerçek zamanlı API-Football verisi + Claude AI ile profesyonel futbol tahmin motoru.

## 🚀 Streamlit Cloud Deployment

1. Bu dosyaları bir GitHub reposuna koy (public veya private)
2. [share.streamlit.io](https://share.streamlit.io) → New app → repo seç
3. Main file: `app.py`
4. Deploy!

## 🔑 Gerekli API Anahtarları (Uygulamada sidebar'dan giriliyor)

### API-Football (RapidAPI) — ÜCRETSİZ
1. [rapidapi.com](https://rapidapi.com/api-sports/api/api-football) → Sign up
2. API-Football → Subscribe → Free plan (100 istek/gün)
3. API Key'i kopyala → Uygulamada "RapidAPI Key" alanına yapıştır

### Anthropic Claude API
1. [console.anthropic.com](https://console.anthropic.com) → Sign up
2. API Keys → Create Key
3. Claude API Key'i kopyala → Uygulamada "Claude API Key" alanına yapıştır

## 📊 Çekilen Veriler

Her maç için API-Football'dan otomatik olarak:
- ✅ MS 1/X/2 oranları
- ✅ KG VAR/YOK oranları  
- ✅ 2.5 / 3.5 Üst-Alt oranları
- ✅ Son 5 maç form durumu (ev / deplasman)
- ✅ H2H geçmişi (son 6 maç)
- ✅ Takım gol ortalamaları (sezonluk)

## 🤖 Analiz Çıktısı (8 Madde)

1. En Olası Skor Tahmini (yüzdeli)
2. Alternatif Skor Dağılımı (5+ skor)
3. İY/MS Tahmini + Kombinasyonlar
4. KG VAR/YOK & Üst/Alt Tahminleri
5. 2/1 – 1/2 Dönüş Tespiti
6. Oran-Skor Pattern Analizi
7. Maç Risk Seviyesi
8. Banko / Orta / Sürpriz Önerileri

## 📁 Dosya Yapısı

```
betting_analyst/
├── app.py           # Ana uygulama
├── requirements.txt # Bağımlılıklar
└── README.md        # Bu dosya
```

## ⚠️ Notlar

- API-Football Free: 100 istek/gün → Her maç ~5-6 istek → ~15-20 maç/gün
- Claude analizi: ~$0.003-0.005 / maç (çok ucuz)
- Streamlit Cloud ücretsiz plan yeterli
