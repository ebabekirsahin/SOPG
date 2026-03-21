import streamlit as st
import requests
from datetime import date, timedelta
import time

# ──────────────────────────────────────────────────────────────
# SAYFA AYARI
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚽ Betting Analyst Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.header-box {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #30363d; border-radius: 12px;
    padding: 1.5rem 2rem; margin-bottom: 1.5rem; text-align: center;
}
.header-box h1 { color: #58a6ff; margin: 0; font-size: 1.8rem; }
.header-box p  { color: #8b949e; margin: 0.4rem 0 0; font-size: 0.95rem; }
.match-header  { color: #58a6ff; font-size: 1.05rem; font-weight: 700; margin-bottom: 0.3rem; }
.odd-pill {
    display: inline-block; background: #21262d;
    border: 1px solid #30363d; color: #c9d1d9;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.78rem; margin: 2px 3px 2px 0;
}
.info-card {
    background: #0d1117; border: 1px solid #1f6feb;
    border-left: 4px solid #1f6feb; border-radius: 6px;
    padding: 0.8rem 1rem; font-size: 0.88rem; color: #c9d1d9;
    margin-bottom: 1rem; line-height: 1.8;
}
.analysis-out {
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 8px; padding: 1.2rem;
    font-size: 0.84rem; color: #e6edf3;
    line-height: 1.8; white-space: pre-wrap;
    max-height: 650px; overflow-y: auto;
}
.step-badge {
    display: inline-block; background: #1f6feb33;
    color: #58a6ff; border: 1px solid #1f6feb55;
    border-radius: 6px; padding: 1px 8px;
    font-size: 0.75rem; margin-right: 6px; font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
  <h1>⚽ BETTING DATA ANALYST PRO</h1>
  <p>football-data.org (ücretsiz) + Claude AI · Gerçek Maç Verisi · 8 Adımlı Profesyonel Analiz</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔑 API Anahtarları")

    st.markdown("""
    <div class="info-card">
    <b>1) football-data.org</b><br>
    → <a href="https://www.football-data.org/client/register" target="_blank">football-data.org/client/register</a><br>
    → E-posta ile kayıt → anında key gelir<br>
    → Kredi kartı YOK · Tamamen ücretsiz<br><br>
    <b>2) Claude API</b><br>
    → <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a><br>
    → API Keys → Create Key
    </div>
    """, unsafe_allow_html=True)

    fdorg_key = st.text_input(
        "football-data.org API Key",
        type="password",
        placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )
    claude_key = st.text_input(
        "Anthropic Claude API Key",
        type="password",
        placeholder="sk-ant-...",
    )

    st.divider()
    st.markdown("## ⚙️ Filtreler")

    LEAGUES = {
        "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": "PL",
        "La Liga 🇪🇸": "PD",
        "Bundesliga 🇩🇪": "BL1",
        "Serie A 🇮🇹": "SA",
        "Ligue 1 🇫🇷": "FL1",
        "Eredivisie 🇳🇱": "DED",
        "Primeira Liga 🇵🇹": "PPL",
        "Champions League ⭐": "CL",
        "Tüm Ligler (birden fazla çek)": None,
    }

    sel_league_label = st.selectbox("Lig Seç", list(LEAGUES.keys()))
    sel_league_code  = LEAGUES[sel_league_label]

    sel_date  = st.date_input("Maç Tarihi", value=date.today())
    max_match = st.slider("Maks. Maç Sayısı", 1, 20, 10)

    st.divider()
    st.caption("API: football-data.org v4 · AI: Claude Sonnet")

# ──────────────────────────────────────────────────────────────
# football-data.org YARDIMCI FONKSİYONLAR
# ──────────────────────────────────────────────────────────────
BASE = "https://api.football-data.org/v4"

def fdorg(path: str, key: str, params: dict = None) -> dict:
    """football-data.org'a istek at."""
    headers = {"X-Auth-Token": key}
    try:
        r = requests.get(f"{BASE}{path}", headers=headers,
                         params=params or {}, timeout=15)
        if r.status_code == 429:
            st.warning("⏳ API rate limit — 1 dakika bekleniyor...")
            time.sleep(61)
            r = requests.get(f"{BASE}{path}", headers=headers,
                             params=params or {}, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Hatası [{path}]: {e}")
        return {}

def get_matches(key: str, league_code: str | None, target_date: str, limit: int) -> list:
    """Belirtilen gün için maçları çek."""
    params = {"dateFrom": target_date, "dateTo": target_date, "status": "SCHEDULED"}
    if league_code:
        path = f"/competitions/{league_code}/matches"
    else:
        path = "/matches"
    data = fdorg(path, key, params)
    return data.get("matches", [])[:limit]

def get_head2head(key: str, match_id: int) -> list:
    """H2H geçmişini çek (son 5)."""
    data = fdorg(f"/matches/{match_id}/head2head", key, {"limit": 6})
    return data.get("matches", [])

def get_team_matches(key: str, team_id: int) -> list:
    """Takımın son 5 maçını çek."""
    data = fdorg(f"/teams/{team_id}/matches", key,
                 {"status": "FINISHED", "limit": 5})
    return data.get("matches", [])

def form_str(matches: list, team_id: int) -> str:
    """Sonuçlardan G/B/M string üret."""
    out = []
    for m in reversed(matches):
        hid = m["homeTeam"]["id"]
        hg  = m["score"]["fullTime"]["home"] or 0
        ag  = m["score"]["fullTime"]["away"] or 0
        if hid == team_id:
            out.append("G" if hg > ag else "B" if hg == ag else "M")
        else:
            out.append("G" if ag > hg else "B" if hg == ag else "M")
    return "-".join(out) if out else "Veri yok"

def h2h_str(matches: list) -> str:
    """H2H maçlarını özetle."""
    parts = []
    for m in matches[:5]:
        ht = m["homeTeam"]["shortName"] or m["homeTeam"]["name"]
        at = m["awayTeam"]["shortName"] or m["awayTeam"]["name"]
        hg = m["score"]["fullTime"]["home"]
        ag = m["score"]["fullTime"]["away"]
        if hg is None:
            continue
        parts.append(f"{ht} {hg}-{ag} {at}")
    return " | ".join(parts) if parts else "Veri yok"

def build_prompt(match: dict, h2h: list, hform: list, aform: list) -> str:
    """API verilerini analiz promptuna çevir."""
    h    = match["homeTeam"]
    a    = match["awayTeam"]
    comp = match["competition"]["name"]
    dt   = match["utcDate"][:10]

    # Odds (football-data free plan'da bazen gelir, gelmezse boş)
    odds = match.get("odds", {})
    o1   = odds.get("homeWin", "?")
    ox   = odds.get("draw",    "?")
    o2   = odds.get("awayWin", "?")

    hf = form_str(hform, h["id"])
    af = form_str(aform, a["id"])
    h2 = h2h_str(h2h)

    prompt = f"""
### MAÇ: {h['name']} vs {a['name']}
- Lig: {comp}
- Tarih: {dt}
- MS Oranları: 1={o1} | X={ox} | 2={o2}
- {h['name']} Son 5 Form: {hf}
- {a['name']} Son 5 Form: {af}
- H2H Son 6 Maç: {h2}
""".strip()
    return prompt

# ──────────────────────────────────────────────────────────────
# CLAUDE ANALİZ
# ──────────────────────────────────────────────────────────────
SYSTEM = """Sen bir Profesyonel Betting Data Analyst ve Prediction Engine'sin.
Sana verilen maç verilerine dayanarak aşağıdaki 8 maddelik analizi EKSİKSİZ üret:

## 1) EN OLASI SKOR TAHMİNİ
En yüksek olasılıklı tek skor + yüzdesi (örn: 2-1 %31)

## 2) ALTERNATİF SKOR DAĞILIMI
En az 5 skor, her biri yüzdeli (örn: 1-1 %22, 2-0 %17...)

## 3) İY / MS TAHMİNİ
- İlk yarı 1/X/2 yüzdeleri
- Maç sonu 1/X/2 yüzdeleri
- En olası 4 İY/MS kombinasyonu yüzdeli (örn: 1/1 %36, X/1 %18...)

## 4) KG VAR–YOK & ÜST/ALT
- KG VAR (%...) | KG YOK (%...)
- 2.5 ÜST (%...) | 2.5 ALT (%...)
- 3.5 ÜST (%...)

## 5) 2/1 – 1/2 DÖNÜŞ TESPİTİ
- 2/1 ihtimali (%...) | 1/2 ihtimali (%...)
- Oran anomalisi yorumu
- Form ve tempo pattern analizi

## 6) ORAN–SKOR PATTERN ANALİZİ
Bu oran aralığının tarihsel pattern analizi, en baskın skor tipi, KG eğilimi.

## 7) MAÇ RİSK SEVİYESİ
Düşük / Orta / Yüksek — kısa gerekçe

## 8) BANKO – ORTA – SÜRPRİZ
- 🔒 BANKO: [tahmin] — gerekçe
- ⚡ ORTA RİSK: [tahmin] — gerekçe
- 💎 SÜRPRİZ: [tahmin + tahmini oran] — gerekçe

Kurallar:
- Tüm tahminler yüzesel olasılığa dayalı olsun
- Kişisel yorum değil, veri + pattern analizi
- Oran verisi eksikse form ve H2H'dan çıkar
- Profesyonel bahis analizi dili kullan"""

def claude_analyze(prompt: str, key: str) -> str:
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2500,
                "system": SYSTEM,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=90,
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception as e:
        return f"❌ Claude Hatası: {e}"

# ──────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────
for k in ["matches", "prompts", "analyses"]:
    if k not in st.session_state:
        st.session_state[k] = {} if k != "matches" else []

# ──────────────────────────────────────────────────────────────
# ANA BUTONLAR
# ──────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([3, 2, 2])
with c1:
    st.markdown(f"**{sel_league_label}** · {sel_date.strftime('%d.%m.%Y')} · Maks {max_match} maç")
with c2:
    fetch_btn = st.button("🔍 Maçları Çek", type="primary", use_container_width=True)
with c3:
    all_btn = st.button("🤖 Tümünü Analiz Et", use_container_width=True)

st.divider()

# ──────────────────────────────────────────────────────────────
# MAÇLARI ÇEK
# ──────────────────────────────────────────────────────────────
if fetch_btn:
    if not fdorg_key:
        st.error("⛔ football-data.org API Key giriniz.")
        st.stop()

    with st.spinner("📡 Maçlar çekiliyor..."):
        matches = get_matches(
            fdorg_key,
            sel_league_code,
            sel_date.strftime("%Y-%m-%d"),
            max_match,
        )

    if not matches:
        st.warning("⚠️ Bu tarih/lig için planlanmış maç bulunamadı. Farklı bir tarih dene.")
    else:
        st.session_state.matches   = matches
        st.session_state.prompts   = {}
        st.session_state.analyses  = {}
        st.success(f"✅ {len(matches)} maç bulundu! Veriler hazırlanıyor...")

        bar = st.progress(0, text="Form & H2H verileri çekiliyor...")
        for i, m in enumerate(matches):
            mid  = m["id"]
            hid  = m["homeTeam"]["id"]
            aid  = m["awayTeam"]["id"]
            h2h  = get_head2head(fdorg_key, mid)
            hf   = get_team_matches(fdorg_key, hid)
            af   = get_team_matches(fdorg_key, aid)
            st.session_state.prompts[mid] = build_prompt(m, h2h, hf, af)
            bar.progress(
                (i + 1) / len(matches),
                text=f"({i+1}/{len(matches)}) {m['homeTeam']['name']} – {m['awayTeam']['name']}",
            )
            time.sleep(0.4)   # Rate limit: free plan 10 req/dak

        bar.empty()
        st.success("✅ Tüm veriler hazır! Analiz için maçı aç veya Tümünü Analiz Et'e bas.")

# ──────────────────────────────────────────────────────────────
# TOPLU ANALİZ
# ──────────────────────────────────────────────────────────────
if all_btn:
    if not st.session_state.matches:
        st.warning("Önce Maçları Çek!")
    elif not claude_key:
        st.error("⛔ Claude API Key giriniz.")
    else:
        bar2 = st.progress(0, text="Claude analizleri üretiliyor...")
        items = list(st.session_state.prompts.items())
        for i, (mid, prompt) in enumerate(items):
            m_name = next(
                (f"{x['homeTeam']['name']} – {x['awayTeam']['name']}"
                 for x in st.session_state.matches if x["id"] == mid), str(mid)
            )
            bar2.progress((i) / len(items), text=f"({i+1}/{len(items)}) {m_name} analiz ediliyor...")
            result = claude_analyze(prompt, claude_key)
            st.session_state.analyses[mid] = result
            time.sleep(0.5)
        bar2.progress(1.0, text="Tamamlandı!")
        time.sleep(0.5)
        bar2.empty()
        st.success("✅ Tüm analizler tamamlandı! Aşağıdaki maçları aç.")

# ──────────────────────────────────────────────────────────────
# MAÇ LİSTESİ
# ──────────────────────────────────────────────────────────────
if st.session_state.matches:
    st.markdown(f"## 📋 Maçlar ({len(st.session_state.matches)} maç)")

    for m in st.session_state.matches:
        mid   = m["id"]
        hname = m["homeTeam"]["name"]
        aname = m["awayTeam"]["name"]
        comp  = m["competition"]["name"]
        utc   = m["utcDate"][11:16]
        odds  = m.get("odds", {})

        label = f"⚽  {hname}  –  {aname}  |  {comp}  |  {utc} UTC"
        if mid in st.session_state.analyses:
            label = "✅ " + label

        with st.expander(label):
            # Oranlar
            o1 = odds.get("homeWin", "–")
            ox = odds.get("draw",    "–")
            o2 = odds.get("awayWin", "–")
            st.markdown(f"""
            <span class='odd-pill'>1: {o1}</span>
            <span class='odd-pill'>X: {ox}</span>
            <span class='odd-pill'>2: {o2}</span>
            """, unsafe_allow_html=True)

            # Ham veri önizleme
            if mid in st.session_state.prompts:
                with st.expander("📊 Ham Veri (API'den gelen)", expanded=False):
                    st.code(st.session_state.prompts[mid], language="markdown")

            # Tek maç analiz butonu
            col_a, col_b = st.columns([2, 1])
            with col_b:
                if st.button("🤖 Bu Maçı Analiz Et", key=f"a_{mid}"):
                    if not claude_key:
                        st.error("Claude API Key giriniz.")
                    elif mid not in st.session_state.prompts:
                        st.warning("Önce Maçları Çek!")
                    else:
                        with st.spinner("Analiz üretiliyor..."):
                            res = claude_analyze(st.session_state.prompts[mid], claude_key)
                            st.session_state.analyses[mid] = res

            # Analiz sonucu
            if mid in st.session_state.analyses:
                st.markdown("---")
                st.markdown(
                    f"<div class='analysis-out'>{st.session_state.analyses[mid]}</div>",
                    unsafe_allow_html=True,
                )
                st.download_button(
                    "⬇️ Analizi İndir (.txt)",
                    data=st.session_state.analyses[mid],
                    file_name=f"{hname}_vs_{aname}_{sel_date}.txt",
                    mime="text/plain",
                    key=f"dl_{mid}",
                )

# ──────────────────────────────────────────────────────────────
# BAŞLANGIÇ EKRANI
# ──────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div class="info-card">
    <b style="color:#58a6ff; font-size:1rem">🚀 Nasıl Kullanılır?</b><br><br>
    <span class="step-badge">1</span> Sol sidebar → <b>football-data.org</b>'dan ücretsiz key al (2 dk)<br>
    <span class="step-badge">2</span> Sol sidebar → <b>Claude API Key</b> gir (console.anthropic.com)<br>
    <span class="step-badge">3</span> Lig ve tarih seç → <b>Maçları Çek</b><br>
    <span class="step-badge">4</span> Tek maç için <b>Analiz Et</b> veya <b>Tümünü Analiz Et</b><br>
    <span class="step-badge">5</span> 8 maddelik profesyonel analiz raporu al 🎯<br><br>
    <b>football-data.org Ücretsiz Plan Kapsamı:</b><br>
    Premier League · La Liga · Bundesliga · Serie A · Ligue 1 · Eredivisie · Champions League<br><br>
    <b>Rate Limit:</b> 10 istek/dakika (otomatik olarak yönetilir)<br>
    <b>Claude maliyeti:</b> ~$0.003 / maç (çok ucuz)
    </div>
    """, unsafe_allow_html=True)
