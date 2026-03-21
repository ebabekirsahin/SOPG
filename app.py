import streamlit as st
import requests
import json
from datetime import datetime, date
import time

# ─────────────────────────────────────────────
# SAYFA AYARLARI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="⚽ Betting Data Analyst Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;
}
.main-header h1 { color: #e94560; margin: 0; font-size: 2rem; }
.main-header p { color: #a8b2d8; margin: 0.5rem 0 0; font-size: 1rem; }
.match-card {
    background: #1a1a2e; border: 1px solid #0f3460;
    border-radius: 10px; padding: 1rem; margin-bottom: 1rem;
}
.match-card h3 { color: #e94560; margin: 0 0 0.5rem; font-size: 1.1rem; }
.odds-badge {
    display: inline-block; background: #0f3460;
    color: #a8b2d8; padding: 2px 8px; border-radius: 6px;
    font-size: 0.8rem; margin: 2px;
}
.section-header {
    color: #e94560; font-size: 1rem; font-weight: 700;
    border-bottom: 1px solid #0f3460; padding-bottom: 6px; margin: 1rem 0 0.5rem;
}
.analysis-box {
    background: #0d1117; border: 1px solid #21262d;
    border-radius: 8px; padding: 1rem; font-family: monospace;
    white-space: pre-wrap; font-size: 0.85rem; color: #e6edf3;
    line-height: 1.7; max-height: 600px; overflow-y: auto;
}
.banko-badge { background: #1a7a4a; color: #7ee787; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; }
.orta-badge  { background: #7a5a00; color: #e3b341; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; }
.surpriz-badge { background: #6e2c82; color: #d2a8ff; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; }
.info-box {
    background: #0d2137; border-left: 3px solid #1f6feb;
    padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; font-size: 0.9rem;
}
stSpinner > div { color: #e94560 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>⚽ BETTING DATA ANALYST PRO</h1>
    <p>API-Football + Claude AI · Gerçek Zamanlı Veri · Profesyonel Tahmin Motoru</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR – API KEYS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔑 API Anahtarları")
    st.markdown("""
    <div class="info-box">
    <b>API-Football</b> → <a href="https://rapidapi.com/api-sports/api/api-football" target="_blank">RapidAPI</a>'den ücretsiz al<br>
    <b>Claude API</b> → <a href="https://console.anthropic.com" target="_blank">Anthropic Console</a>'dan al
    </div>
    """, unsafe_allow_html=True)
    
    rapidapi_key = st.text_input("RapidAPI Key (API-Football)", type="password",
                                  placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                  help="RapidAPI → API-Football → Subscribe (Free: 100 req/gün)")
    
    claude_api_key = st.text_input("Anthropic Claude API Key", type="password",
                                    placeholder="sk-ant-...",
                                    help="console.anthropic.com → API Keys")
    
    st.divider()
    st.markdown("## ⚙️ Filtreler")
    
    selected_league = st.selectbox(
        "Lig Seç",
        options=[
            ("Tümü", None),
            ("Süper Lig (Türkiye)", 203),
            ("Premier League (İngiltere)", 39),
            ("La Liga (İspanya)", 140),
            ("Bundesliga (Almanya)", 78),
            ("Serie A (İtalya)", 135),
            ("Ligue 1 (Fransa)", 61),
            ("Champions League", 2),
            ("Europa League", 3),
        ],
        format_func=lambda x: x[0]
    )
    
    selected_date = st.date_input("Maç Tarihi", value=date.today())
    
    max_matches = st.slider("Maks. Maç Sayısı", 1, 20, 10)
    
    st.divider()
    st.markdown("### 📊 Veri Kaynakları")
    use_odds      = st.checkbox("İddaa Oranları", value=True)
    use_h2h       = st.checkbox("H2H Geçmişi", value=True)
    use_form      = st.checkbox("Form Durumu", value=True)
    use_standings = st.checkbox("Puan Durumu", value=True)
    
    st.divider()
    st.caption("v2.0 | API-Football + Claude Sonnet")

# ─────────────────────────────────────────────
# API-FOOTBALL HELPER
# ─────────────────────────────────────────────
RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"

def api_football_get(endpoint: str, params: dict, api_key: str) -> dict:
    """API-Football RapidAPI isteği at."""
    url = f"https://{RAPIDAPI_HOST}/v3/{endpoint}"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Hatası [{endpoint}]: {e}")
        return {}

def get_fixtures(api_key: str, league_id: int | None, target_date: str, limit: int) -> list:
    """Belirtilen tarihteki maçları çek."""
    params = {"date": target_date, "status": "NS"}
    if league_id:
        params["league"] = league_id
        params["season"] = target_date[:4]
    data = api_football_get("fixtures", params, api_key)
    fixtures = data.get("response", [])
    return fixtures[:limit]

def get_odds(api_key: str, fixture_id: int) -> dict:
    """Maç oranlarını çek (MS1/X/2, KG, 2.5Üst)."""
    data = api_football_get("odds", {"fixture": fixture_id, "bookmaker": 8}, api_key)
    result = {"ms": {}, "kg": {}, "ust25": {}, "ust35": {}}
    try:
        bets = data["response"][0]["bookmakers"][0]["bets"]
        for bet in bets:
            name = bet["name"]
            values = {v["value"]: v["odd"] for v in bet["values"]}
            if name == "Match Winner":
                result["ms"] = {
                    "home": values.get("Home", "?"),
                    "draw": values.get("Draw", "?"),
                    "away": values.get("Away", "?"),
                }
            elif name == "Both Teams Score":
                result["kg"] = {
                    "yes": values.get("Yes", "?"),
                    "no":  values.get("No",  "?"),
                }
            elif name == "Goals Over/Under":
                result["ust25"] = {"over": values.get("Over 2.5", "?"), "under": values.get("Under 2.5", "?")}
                result["ust35"] = {"over": values.get("Over 3.5", "?")}
    except (KeyError, IndexError):
        pass
    return result

def get_h2h(api_key: str, h2h_str: str) -> list:
    """H2H geçmişini çek."""
    data = api_football_get("fixtures/headtohead", {"h2h": h2h_str, "last": 6}, api_key)
    return data.get("response", [])

def get_team_form(api_key: str, team_id: int, season: int) -> list:
    """Son 5 maç formunu çek."""
    data = api_football_get("fixtures", {
        "team": team_id, "last": 5, "season": season
    }, api_key)
    return data.get("response", [])

def get_standings(api_key: str, league_id: int, season: int) -> list:
    """Puan durumunu çek."""
    data = api_football_get("standings", {"league": league_id, "season": season}, api_key)
    try:
        return data["response"][0]["league"]["standings"][0]
    except (KeyError, IndexError):
        return []

def form_string(fixtures: list, team_id: int) -> str:
    """Fixture listesinden G/B/M string üret."""
    symbols = []
    for f in reversed(fixtures):
        home = f["teams"]["home"]
        away = f["teams"]["away"]
        hg = f["goals"]["home"] or 0
        ag = f["goals"]["away"] or 0
        if home["id"] == team_id:
            symbols.append("G" if hg > ag else ("B" if hg == ag else "M"))
        else:
            symbols.append("G" if ag > hg else ("B" if hg == ag else "M"))
    return "-".join(symbols) if symbols else "Veri yok"

def h2h_summary(h2h_list: list, home_id: int) -> str:
    """H2H maçlarını özetle."""
    results = []
    for f in h2h_list[:5]:
        hg = f["goals"]["home"] or 0
        ag = f["goals"]["away"] or 0
        ht = f["teams"]["home"]["name"]
        at = f["teams"]["away"]["name"]
        results.append(f"{ht} {hg}-{ag} {at}")
    return " | ".join(results) if results else "Veri yok"

def get_team_stats(api_key: str, team_id: int, league_id: int, season: int) -> dict:
    """Takım genel istatistiklerini çek."""
    data = api_football_get("teams/statistics", {
        "team": team_id, "league": league_id, "season": season
    }, api_key)
    return data.get("response", {})

# ─────────────────────────────────────────────
# CLAUDE ANALİZ
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """Sen bir Profesyonel Betting Data Analyst ve Prediction Engine'sin.
Gerçek API verilerine dayanarak futbol maçları için aşağıdaki 8 maddelik analizi EKSIKSIZ ver:

## 1) EN OLASI SKOR TAHMİNİ
En yüksek olasılıklı skor ve yüzdesi (örn: 2-1 %31)

## 2) ALTERNATİF SKOR DAĞILIMI (en az 5 skor)
Her skor yüzde ile (örn: 1-1 %22, 2-0 %18 ...)

## 3) İY / MS TAHMİNİ
- İY 1/X/2 yüzdeleri
- MS 1/X/2 yüzdeleri
- En olası 4 İY/MS kombinasyonu (örn: 1/1 %38)

## 4) KG VAR–YOK & ÜST/ALT
- KG VAR (%...) | KG YOK (%...)
- 2.5 ÜST (%...) | 2.5 ALT (%...)
- 3.5 ÜST (%...)

## 5) 2/1 – 1/2 DÖNÜŞ TESPİTİ
- 2/1 ihtimali (%...) | 1/2 ihtimali (%...)
- Oran anomalisi, tempo analizi, pattern değerlendirmesi

## 6) ORAN–SKOR PATTERN ANALİZİ
Bu oran aralığının tarihsel pattern analizi, en baskın skor, KG eğilimi.

## 7) MAÇ RİSK SEVİYESİ
Düşük / Orta / Yüksek + kısa gerekçe

## 8) BANKO – ORTA – SÜRPRİZ
- 🔒 BANKO: [tahmin] – gerekçe
- ⚡ ORTA RİSK: [tahmin] – gerekçe
- 💎 SÜRPRİZ: [tahmin + oran] – gerekçe
- Skor sürprizi varsa özellikle belirt

Kurallar: Yalnızca veri+pattern analizi. Kişisel yorum yok. Tüm tahminler yüzdesel olasılığa dayanmalı."""

def claude_analyze(match_data: str, claude_key: str) -> str:
    """Claude Sonnet ile analiz üret."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": claude_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2500,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": match_data}],
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"Claude API Hatası: {e}"

# ─────────────────────────────────────────────
# MAÇLARI ÇEK VE GÖSTERMEKLİ FORMATLA
# ─────────────────────────────────────────────
def build_match_prompt(fixture: dict, odds: dict, h2h: list,
                        home_form: list, away_form: list,
                        home_stats: dict, away_stats: dict) -> str:
    """Tüm API verisini analiz promptuna çevir."""
    h = fixture["teams"]["home"]
    a = fixture["teams"]["away"]
    league = fixture["league"]
    date_str = fixture["fixture"]["date"][:10]

    home_goals_for  = home_stats.get("goals", {}).get("for",  {}).get("average", {}).get("total", "?")
    home_goals_ag   = home_stats.get("goals", {}).get("against", {}).get("average", {}).get("total", "?")
    away_goals_for  = away_stats.get("goals", {}).get("for",  {}).get("average", {}).get("total", "?")
    away_goals_ag   = away_stats.get("goals", {}).get("against", {}).get("average", {}).get("total", "?")

    home_form_str = form_string(home_form, h["id"])
    away_form_str = form_string(away_form, a["id"])
    h2h_str       = h2h_summary(h2h, h["id"])

    ms  = odds.get("ms", {})
    kg  = odds.get("kg", {})
    u25 = odds.get("ust25", {})
    u35 = odds.get("ust35", {})

    prompt = f"""
### MAÇ ANALİZİ: {h['name']} vs {a['name']}
- Lig: {league['name']} ({league['country']})
- Tarih: {date_str}
- Oranlar MS: 1={ms.get('home','?')} | X={ms.get('draw','?')} | 2={ms.get('away','?')}
- KG VAR={kg.get('yes','?')} | KG YOK={kg.get('no','?')}
- 2.5 ÜST={u25.get('over','?')} | 2.5 ALT={u25.get('under','?')} | 3.5 ÜST={u35.get('over','?')}
- {h['name']} Son 5 Form: {home_form_str}
- {a['name']} Son 5 Form: {away_form_str}
- {h['name']} Gol Ort.: {home_goals_for} attı / {home_goals_ag} yedi (maç başı)
- {a['name']} Gol Ort.: {away_goals_for} attı / {away_goals_ag} yedi (maç başı)
- H2H Son 6: {h2h_str}
"""
    return prompt.strip()

# ─────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.markdown("### 📅 Seçilen Parametreler")
    st.write(f"**Tarih:** {selected_date.strftime('%d.%m.%Y')} | **Lig:** {selected_league[0]} | **Maks. Maç:** {max_matches}")

with col3:
    fetch_btn = st.button("🔍 Maçları Çek", type="primary", use_container_width=True)
    analyze_all_btn = st.button("🤖 Tümünü Analiz Et", use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "fixtures" not in st.session_state:
    st.session_state.fixtures = []
if "match_data" not in st.session_state:
    st.session_state.match_data = {}
if "analyses" not in st.session_state:
    st.session_state.analyses = {}

# ─────────────────────────────────────────────
# MAÇLARI ÇEK
# ─────────────────────────────────────────────
if fetch_btn:
    if not rapidapi_key:
        st.error("⛔ RapidAPI Key giriniz (sol sidebar).")
    else:
        with st.spinner("🔄 API-Football'dan maçlar çekiliyor..."):
            fixtures = get_fixtures(
                rapidapi_key,
                selected_league[1],
                selected_date.strftime("%Y-%m-%d"),
                max_matches
            )
        if not fixtures:
            st.warning("⚠️ Bu tarih/lig için maç bulunamadı.")
        else:
            st.session_state.fixtures = fixtures
            st.session_state.match_data = {}
            st.session_state.analyses = {}
            st.success(f"✅ {len(fixtures)} maç bulundu!")

            season = selected_date.year

            progress = st.progress(0, text="Veriler hazırlanıyor...")
            for i, fix in enumerate(fixtures):
                fid  = fix["fixture"]["id"]
                hid  = fix["teams"]["home"]["id"]
                aid  = fix["teams"]["away"]["id"]
                lid  = fix["league"]["id"]
                h2h_str = f"{hid}-{aid}"

                odds_data  = get_odds(rapidapi_key, fid)       if use_odds   else {}
                h2h_data   = get_h2h(rapidapi_key, h2h_str)    if use_h2h    else []
                home_form  = get_team_form(rapidapi_key, hid, season)  if use_form  else []
                away_form  = get_team_form(rapidapi_key, aid, season)  if use_form  else []
                home_stats = get_team_stats(rapidapi_key, hid, lid, season)
                away_stats = get_team_stats(rapidapi_key, aid, lid, season)

                prompt = build_match_prompt(fix, odds_data, h2h_data,
                                            home_form, away_form,
                                            home_stats, away_stats)
                st.session_state.match_data[fid] = {
                    "fixture": fix, "odds": odds_data,
                    "prompt": prompt
                }
                progress.progress((i + 1) / len(fixtures),
                                   text=f"({i+1}/{len(fixtures)}) {fix['teams']['home']['name']} vs {fix['teams']['away']['name']}")
                time.sleep(0.3)  # rate limit koruma

            progress.empty()

# ─────────────────────────────────────────────
# MAÇLARI LİSTELE
# ─────────────────────────────────────────────
if st.session_state.fixtures:
    st.markdown(f"## 📋 Maç Listesi ({len(st.session_state.fixtures)} maç)")

    for fix in st.session_state.fixtures:
        fid = fix["fixture"]["id"]
        h   = fix["teams"]["home"]["name"]
        a   = fix["teams"]["away"]["name"]
        lg  = fix["league"]["name"]
        dt  = fix["fixture"]["date"][11:16]
        md  = st.session_state.match_data.get(fid, {})
        odds = md.get("odds", {})
        ms   = odds.get("ms", {})
        kg   = odds.get("kg", {})
        u25  = odds.get("ust25", {})

        with st.expander(f"⚽ {h} – {a}  |  {lg}  |  {dt}", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**MS Oranları**")
                st.markdown(f"""
                <span class='odds-badge'>1: {ms.get('home','–')}</span>
                <span class='odds-badge'>X: {ms.get('draw','–')}</span>
                <span class='odds-badge'>2: {ms.get('away','–')}</span>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("**KG / Gol**")
                st.markdown(f"""
                <span class='odds-badge'>KG VAR: {kg.get('yes','–')}</span>
                <span class='odds-badge'>2.5Üst: {u25.get('over','–')}</span>
                <span class='odds-badge'>2.5Alt: {u25.get('under','–')}</span>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown("**Eylem**")
                analyze_btn = st.button(f"🤖 Analiz Et", key=f"btn_{fid}")

            # Ham veri önizleme
            if md.get("prompt"):
                with st.expander("📊 Ham Veri Önizleme", expanded=False):
                    st.code(md["prompt"], language="markdown")

            # Analiz butonu
            if analyze_btn:
                if not claude_api_key:
                    st.error("⛔ Claude API Key giriniz.")
                else:
                    with st.spinner(f"🤖 {h} – {a} analiz ediliyor..."):
                        result = claude_analyze(md["prompt"], claude_api_key)
                        st.session_state.analyses[fid] = result

            # Analiz sonucu
            if fid in st.session_state.analyses:
                st.markdown("---")
                st.markdown(f"### 📈 Analiz Sonucu: {h} – {a}")
                st.markdown(
                    f"<div class='analysis-box'>{st.session_state.analyses[fid]}</div>",
                    unsafe_allow_html=True
                )
                st.download_button(
                    label="⬇️ Analizi İndir (.txt)",
                    data=st.session_state.analyses[fid],
                    file_name=f"analiz_{h}_vs_{a}_{date.today()}.txt",
                    mime="text/plain",
                    key=f"dl_{fid}"
                )

# ─────────────────────────────────────────────
# TÜMÜNÜ ANALİZ ET
# ─────────────────────────────────────────────
if analyze_all_btn and st.session_state.match_data:
    if not claude_api_key:
        st.error("⛔ Claude API Key giriniz.")
    else:
        st.markdown("## 🤖 Toplu Analiz Başlatılıyor...")
        progress2 = st.progress(0)
        items = list(st.session_state.match_data.items())
        for i, (fid, md) in enumerate(items):
            h = md["fixture"]["teams"]["home"]["name"]
            a = md["fixture"]["teams"]["away"]["name"]
            with st.spinner(f"({i+1}/{len(items)}) {h} – {a} analiz ediliyor..."):
                result = claude_analyze(md["prompt"], claude_api_key)
                st.session_state.analyses[fid] = result
            progress2.progress((i + 1) / len(items))
            time.sleep(1)
        st.success("✅ Tüm analizler tamamlandı! Maçları yukarıdan açarak görebilirsin.")

# ─────────────────────────────────────────────
# BOŞKEN
# ─────────────────────────────────────────────
if not st.session_state.fixtures:
    st.markdown("""
    <div class="info-box">
    <h3 style="color:#58a6ff; margin:0 0 0.5rem">🚀 Nasıl Kullanılır?</h3>
    <ol style="margin:0; padding-left:1.2rem; line-height:2">
        <li>Sol sidebar'dan <b>RapidAPI Key</b> ve <b>Claude API Key</b> gir</li>
        <li>Lig ve tarih seç</li>
        <li><b>Maçları Çek</b> butonuna bas → API-Football'dan gerçek veriler gelir</li>
        <li>Tek maç için <b>Analiz Et</b> veya hepsi için <b>Tümünü Analiz Et</b></li>
        <li>8 maddelik profesyonel tahmin raporunu al 🎯</li>
    </ol>
    <br>
    <b>🔑 Ücretsiz API Hesapları:</b><br>
    • <a href="https://rapidapi.com/api-sports/api/api-football" target="_blank">API-Football</a> → Ücretsiz 100 istek/gün (≈15-20 maç analizi)<br>
    • <a href="https://console.anthropic.com" target="_blank">Anthropic Claude</a> → Pay-as-you-go, çok ucuz
    </div>
    """, unsafe_allow_html=True)
