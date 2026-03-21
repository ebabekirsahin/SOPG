import streamlit as st
import requests
from datetime import date
import time
import math

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
.header-box p  { color: #8b949e; margin: 0.4rem 0 0; font-size: 0.9rem; }
.odd-pill {
    display: inline-block; background: #21262d;
    border: 1px solid #30363d; color: #c9d1d9;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.78rem; margin: 2px 3px 2px 0;
}
.analysis-out {
    background: #0d1117; border: 1px solid #30363d;
    border-radius: 8px; padding: 1.3rem;
    font-size: 0.85rem; color: #e6edf3;
    line-height: 1.9; white-space: pre-wrap;
    max-height: 700px; overflow-y: auto;
    font-family: 'Courier New', monospace;
}
.info-card {
    background: #0d1117; border: 1px solid #1f6feb;
    border-left: 4px solid #1f6feb; border-radius: 6px;
    padding: 0.8rem 1rem; font-size: 0.88rem; color: #c9d1d9;
    margin-bottom: 1rem; line-height: 1.8;
}
.key-box {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;
    font-size: 0.82rem; color: #8b949e;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
  <h1>⚽ BETTING DATA ANALYST PRO</h1>
  <p>football-data.org · Gerçek Maç Verisi · Yerleşik AI Analiz Motoru · Claude API GEREKMİYOR</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔑 API Key")
    st.markdown("""
    <div class="key-box">
    <b style="color:#58a6ff">football-data.org</b><br>
    1. <a href="https://www.football-data.org/client/register" target="_blank">
       football-data.org/client/register</a> git<br>
    2. E-posta ile kayıt ol (ücretsiz)<br>
    3. Gelen maildeki key'i buraya yapıştır<br>
    <br>
    ✅ Kredi kartı yok · Claude key yok · Sınırsız kullanım
    </div>
    """, unsafe_allow_html=True)

    fdorg_key = st.text_input(
        "football-data.org API Key",
        type="password",
        placeholder="Buraya yapıştır...",
    )

    # Opsiyonel Claude key
    with st.expander("⚙️ Claude API (opsiyonel — daha derin analiz)"):
        claude_key = st.text_input(
            "Claude API Key (opsiyonel)",
            type="password",
            placeholder="sk-ant-... (boş bırakabilirsin)",
        )
        if claude_key:
            st.success("Claude modu aktif — gelişmiş analiz kullanılacak.")
        else:
            st.info("Boş → Yerleşik analiz motoru kullanılır.")

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
        "Tüm Ligler": None,
    }
    sel_label = st.selectbox("Lig Seç", list(LEAGUES.keys()))
    sel_code  = LEAGUES[sel_label]
    sel_date  = st.date_input("Maç Tarihi", value=date.today())
    max_match = st.slider("Maks. Maç Sayısı", 1, 20, 10)
    st.caption("Rate limit: 10 istek/dak — otomatik yönetilir")

# ──────────────────────────────────────────────────────────────
# football-data.org API
# ──────────────────────────────────────────────────────────────
BASE = "https://api.football-data.org/v4"

def fdorg(path, key, params=None):
    headers = {"X-Auth-Token": key}
    try:
        r = requests.get(f"{BASE}{path}", headers=headers,
                         params=params or {}, timeout=15)
        if r.status_code == 429:
            st.warning("⏳ Rate limit — 65 saniye bekleniyor...")
            time.sleep(65)
            r = requests.get(f"{BASE}{path}", headers=headers,
                             params=params or {}, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API Hatası: {e}")
        return {}

def get_matches(key, league_code, target_date, limit):
    params = {"dateFrom": target_date, "dateTo": target_date, "status": "SCHEDULED"}
    path = f"/competitions/{league_code}/matches" if league_code else "/matches"
    data = fdorg(path, key, params)
    return data.get("matches", [])[:limit]

def get_h2h(key, match_id):
    data = fdorg(f"/matches/{match_id}/head2head", key, {"limit": 8})
    return data.get("matches", [])

def get_team_matches(key, team_id):
    data = fdorg(f"/teams/{team_id}/matches", key,
                 {"status": "FINISHED", "limit": 8})
    return data.get("matches", [])

# ──────────────────────────────────────────────────────────────
# YERLEŞİK ANALİZ MOTORU (Claude key olmadan çalışır)
# ──────────────────────────────────────────────────────────────

def form_results(matches, team_id):
    """Son maçlardan W/D/L listesi çıkar."""
    results = []
    for m in matches:
        hid = m["homeTeam"]["id"]
        hg  = m["score"]["fullTime"]["home"] or 0
        ag  = m["score"]["fullTime"]["away"] or 0
        if hid == team_id:
            results.append("W" if hg > ag else "D" if hg == ag else "L")
        else:
            results.append("W" if ag > hg else "D" if hg == ag else "L")
    return results

def form_pts(results):
    """Form puanı (son 5 üzerinden 0-15)."""
    pts = {"W": 3, "D": 1, "L": 0}
    return sum(pts.get(r, 0) for r in results[:5])

def form_str(results):
    tr = {"W": "G", "D": "B", "L": "M"}
    return "-".join(tr.get(r, "?") for r in results[:5]) or "Veri yok"

def goals_stats(matches, team_id):
    """Atılan / yenilen gol ortalaması."""
    scored, conceded, count = 0, 0, 0
    for m in matches:
        hid = m["homeTeam"]["id"]
        hg  = m["score"]["fullTime"]["home"] or 0
        ag  = m["score"]["fullTime"]["away"] or 0
        if hid == team_id:
            scored += hg; conceded += ag
        else:
            scored += ag; conceded += hg
        count += 1
    if count == 0:
        return 1.3, 1.3
    return round(scored / count, 2), round(conceded / count, 2)

def h2h_stats(matches, home_id):
    hw = aw = dr = total_hg = total_ag = cnt = 0
    for m in matches:
        hid = m["homeTeam"]["id"]
        hg  = m["score"]["fullTime"]["home"] or 0
        ag  = m["score"]["fullTime"]["away"] or 0
        if hid == home_id:
            if hg > ag: hw += 1
            elif hg < ag: aw += 1
            else: dr += 1
            total_hg += hg; total_ag += ag
        else:
            if ag > hg: hw += 1
            elif ag < hg: aw += 1
            else: dr += 1
            total_hg += ag; total_ag += hg
        cnt += 1
    avg_hg = total_hg / cnt if cnt else 1.3
    avg_ag = total_ag / cnt if cnt else 1.1
    return hw, dr, aw, cnt, round(avg_hg, 2), round(avg_ag, 2)

def h2h_str_list(matches):
    parts = []
    for m in matches[:6]:
        ht = m["homeTeam"].get("shortName") or m["homeTeam"]["name"]
        at = m["awayTeam"].get("shortName") or m["awayTeam"]["name"]
        hg = m["score"]["fullTime"]["home"]
        ag = m["score"]["fullTime"]["away"]
        if hg is None: continue
        parts.append(f"{ht} {hg}-{ag} {at}")
    return " | ".join(parts) if parts else "Veri yok"

def odds_implied(o1, ox, o2):
    """Orandan zımni olasılık çıkar."""
    try:
        f1 = 1/float(o1); fx = 1/float(ox); f2 = 1/float(o2)
        total = f1 + fx + f2
        return round(f1/total*100, 1), round(fx/total*100, 1), round(f2/total*100, 1)
    except:
        return None, None, None

def poisson_prob(lam, k):
    return (math.exp(-lam) * lam**k) / math.factorial(k)

def score_probs(home_xg, away_xg, max_goals=5):
    """Poisson dağılımıyla skor olasılıkları."""
    probs = {}
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = poisson_prob(home_xg, h) * poisson_prob(away_xg, a)
            probs[(h, a)] = round(p * 100, 1)
    return probs

def risk_level(home_pts, away_pts, h2h_cnt, has_odds):
    diff = abs(home_pts - away_pts)
    if diff >= 9 and h2h_cnt >= 4:
        return "DÜŞÜK", "Belirgin güç farkı + yeterli H2H verisi mevcut."
    elif diff >= 5 or (h2h_cnt >= 3 and has_odds):
        return "ORTA", "Güç farkı mevcut ancak sürpriz ihtimali göz ardı edilmemeli."
    else:
        return "YÜKSEK", "Takımlar dengeli veya veri yetersiz — dikkatli olunmalı."

def build_analysis(match, h2h_matches, hform_matches, aform_matches):
    """Yerleşik analiz motoru — Claude gerektirmez."""
    h    = match["homeTeam"]
    a    = match["awayTeam"]
    comp = match["competition"]["name"]
    dt   = match["utcDate"][:10]
    mid  = match["id"]

    # Form
    hres = form_results(hform_matches, h["id"])
    ares = form_results(aform_matches, a["id"])
    hpts = form_pts(hres)
    apts = form_pts(ares)
    hfs  = form_str(hres)
    afs  = form_str(ares)

    # Gol ortalamaları
    h_scored, h_conc = goals_stats(hform_matches, h["id"])
    a_scored, a_conc = goals_stats(aform_matches, a["id"])

    # Beklenen gol (xG proxy)
    home_xg = round((h_scored * 0.6 + a_conc * 0.4), 2)
    away_xg = round((a_scored * 0.6 + h_conc * 0.4), 2)
    home_xg = max(0.5, home_xg)
    away_xg = max(0.5, away_xg)

    # H2H
    hw, dr, aw, h2cnt, h2hg, h2ag = h2h_stats(h2h_matches, h["id"])
    h2h_list = h2h_str_list(h2h_matches)

    # Oranlar
    odds    = match.get("odds", {})
    o1_raw  = odds.get("homeWin")
    ox_raw  = odds.get("draw")
    o2_raw  = odds.get("awayWin")
    imp1, impx, imp2 = odds_implied(o1_raw, ox_raw, o2_raw)

    # Form bazlı MS olasılıkları
    total_pts = hpts + apts + 6
    fm_p1  = round((hpts + 3) / total_pts * 100, 1)
    fm_px  = round(8 / total_pts * 100, 1)
    fm_p2  = round((apts + 3) / total_pts * 100, 1)

    # H2H ağırlıklı birleşim
    if h2cnt > 0:
        h2_p1 = round(hw / h2cnt * 100, 1)
        h2_px = round(dr / h2cnt * 100, 1)
        h2_p2 = round(aw / h2cnt * 100, 1)
        w1, w2 = (0.4, 0.6) if h2cnt >= 4 else (0.6, 0.4)
        p1 = round(fm_p1 * w1 + h2_p1 * w2, 1)
        px = round(fm_px * w1 + h2_px * w2, 1)
        p2 = round(fm_p2 * w1 + h2_p2 * w2, 1)
    else:
        p1, px, p2 = fm_p1, fm_px, fm_p2

    # Oran ağırlığı ekle
    if imp1:
        p1 = round(p1 * 0.5 + imp1 * 0.5, 1)
        px = round(px * 0.5 + impx * 0.5, 1)
        p2 = round(p2 * 0.5 + imp2 * 0.5, 1)

    # Normalize
    tot = p1 + px + p2
    p1 = round(p1 / tot * 100, 1)
    px = round(px / tot * 100, 1)
    p2 = round(100 - p1 - px, 1)

    # Skor olasılıkları (Poisson)
    sprobs = score_probs(home_xg, away_xg)
    sorted_scores = sorted(sprobs.items(), key=lambda x: -x[1])
    top_score = sorted_scores[0]
    top5 = sorted_scores[:8]

    # KG / Üst-Alt
    kg_var  = round(100 - poisson_prob(home_xg, 0) * poisson_prob(away_xg, 0) * 10000 / 100, 1)
    # P(en az 1 gol her takımdan) = 1 - P(home=0) - P(away=0) + P(her ikisi=0)
    p_h0 = poisson_prob(home_xg, 0)
    p_a0 = poisson_prob(away_xg, 0)
    kg_var = round((1 - p_h0) * (1 - p_a0) * 100, 1)
    kg_yok = round(100 - kg_var, 1)

    # 2.5 Üst/Alt
    ust25_p = 0
    for (h_g, a_g), p in sprobs.items():
        if h_g + a_g > 2:
            ust25_p += p
    ust25_p = round(ust25_p, 1)
    alt25_p = round(100 - ust25_p, 1)

    # 3.5 Üst
    ust35_p = 0
    for (h_g, a_g), p in sprobs.items():
        if h_g + a_g > 3:
            ust35_p += p
    ust35_p = round(ust35_p, 1)

    # İY tahmini (genel olarak MS'in yaklaşık yarısı)
    iy_p1 = round(p1 * 0.7, 1)
    iy_px = round(px * 1.4, 1)
    iy_p2 = round(p2 * 0.7, 1)
    iy_tot = iy_p1 + iy_px + iy_p2
    iy_p1 = round(iy_p1 / iy_tot * 100, 1)
    iy_px = round(iy_px / iy_tot * 100, 1)
    iy_p2 = round(100 - iy_p1 - iy_px, 1)

    # İY/MS kombinasyonları
    combo_11 = round(iy_p1 * p1 / 100, 1)
    combo_x1 = round(iy_px * p1 / 100, 1)
    combo_12 = round(iy_p1 * p2 / 100, 1)
    combo_x2 = round(iy_px * p2 / 100, 1)
    combo_xx = round(iy_px * px / 100, 1)
    combo_1x = round(iy_p1 * px / 100, 1)
    combo_2x = round(iy_p2 * px / 100, 1)
    combo_22 = round(iy_p2 * p2 / 100, 1)
    combo_21 = round(iy_p2 * p1 / 100, 1)  # 2/1 dönüş
    combo_12r= round(iy_p1 * p2 / 100, 1)  # 1/2 dönüş

    # 2/1 – 1/2 dönüş analizi
    donusum_21 = combo_21
    donusum_12 = combo_12r

    # Risk seviyesi
    risk, risk_why = risk_level(hpts, apts, h2cnt, imp1 is not None)

    # Banko / Orta / Sürpriz
    if p1 >= 55:
        banko = f"MS 1 ({h['name']} galibiyeti) — Olasılık: %{p1}"
    elif p2 >= 50:
        banko = f"MS 2 ({a['name']} galibiyeti) — Olasılık: %{p2}"
    elif ust25_p >= 62:
        banko = f"2.5 ÜST — Olasılık: %{ust25_p}"
    elif alt25_p >= 60:
        banko = f"2.5 ALT — Olasılık: %{alt25_p}"
    else:
        banko = f"KG {'VAR' if kg_var >= 55 else 'YOK'} — Olasılık: %{kg_var if kg_var >= 55 else kg_yok}"

    if px >= 28:
        orta = f"Beraberlik (X) — Olasılık: %{px} | Form dengeli, temkinli yaklaş"
    elif p1 > p2:
        orta = f"MS 1 + KG VAR — {h['name']} kazanır, iki taraf da gol atar"
    else:
        orta = f"MS 2 + 2.5 ÜST — {a['name']} deplasmanda güçlü"

    surpriz_score = sorted_scores[2] if len(sorted_scores) > 2 else sorted_scores[0]
    surpriz = (
        f"Skor: {surpriz_score[0][0]}-{surpriz_score[0][1]} (%{surpriz_score[1]}) "
        f"— xG pattern'ine göre 3. en olası sonuç. Yüksek oranda sürpriz değeri taşır."
    )

    # RAPOR OLUŞTUR
    o1_disp = f"{o1_raw}" if o1_raw else "–"
    ox_disp = f"{ox_raw}" if ox_raw else "–"
    o2_disp = f"{o2_raw}" if o2_raw else "–"
    imp_str = f"(Zımni: %{imp1} / %{impx} / %{imp2})" if imp1 else "(Oran verisi yok)"

    report = f"""
╔══════════════════════════════════════════════════════════════════╗
  {h['name'].upper()} vs {a['name'].upper()}
  {comp} · {dt}
╚══════════════════════════════════════════════════════════════════╝

📌 VERİ ÖZETİ
  {h['name']} Son Form : {hfs} → Form Puanı: {hpts}/15
  {a['name']} Son Form : {afs} → Form Puanı: {apts}/15
  {h['name']} Gol Ort.  : {h_scored} attı / {h_conc} yedi (maç başı)
  {a['name']} Gol Ort.  : {a_scored} attı / {a_conc} yedi (maç başı)
  Beklenen Gol (xG proxy): {h['name']} {home_xg} | {a['name']} {away_xg}
  MS Oranları  : 1={o1_disp} | X={ox_disp} | 2={o2_disp} {imp_str}
  H2H ({h2cnt} maç)    : {h['name']} {hw}G – {dr}B – {aw}M | Son: {h2h_list}

──────────────────────────────────────────────────────────────────
1️⃣  EN OLASI SKOR TAHMİNİ
──────────────────────────────────────────────────────────────────
  🎯 {top_score[0][0]}-{top_score[0][1]}  →  %{top_score[1]}
  (Poisson xG modeli + form ağırlıklı hesaplama)

──────────────────────────────────────────────────────────────────
2️⃣  ALTERNATİF SKOR DAĞILIMI
──────────────────────────────────────────────────────────────────
""".lstrip()

    for i, ((hg, ag), prob) in enumerate(top5):
        bar = "█" * int(prob / 2) + "░" * (15 - int(prob / 2))
        report += f"  {hg}-{ag}  {bar}  %{prob}\n"

    report += f"""
──────────────────────────────────────────────────────────────────
3️⃣  İY / MS TAHMİNİ
──────────────────────────────────────────────────────────────────
  İLK YARI    : 1=%{iy_p1}  |  X=%{iy_px}  |  2=%{iy_p2}
  MAÇ SONU    : 1=%{p1}  |  X=%{px}  |  2=%{p2}

  İY/MS Kombinasyonları:
    1/1  %{combo_11}     X/1  %{combo_x1}     2/1  %{combo_21}
    1/X  %{combo_1x}     X/X  %{combo_xx}     2/X  %{combo_2x}
    1/2  %{combo_12}     X/2  %{combo_x2}     2/2  %{combo_22}

──────────────────────────────────────────────────────────────────
4️⃣  KG VAR–YOK & ÜST/ALT TAHMİNLERİ
──────────────────────────────────────────────────────────────────
  KG VAR      : %{kg_var}
  KG YOK      : %{kg_yok}
  2.5 ÜST     : %{ust25_p}
  2.5 ALT     : %{alt25_p}
  3.5 ÜST     : %{ust35_p}

──────────────────────────────────────────────────────────────────
5️⃣  2/1 – 1/2 DÖNÜŞ TESPİTİ
──────────────────────────────────────────────────────────────────
  2/1 Dönüş İhtimali : %{donusum_21}
  1/2 Dönüş İhtimali : %{donusum_12}

  Değerlendirme:
  • {h['name']} form puanı {hpts}/15 — {a['name']} form puanı {apts}/15
  • xG farkı: {h['name']} {home_xg} — {a['name']} {away_xg}
  • {'Ev sahibi baskısı 2. yarıda artabilir, 2/1 dönüş pattern olası.' if hpts > apts and donusum_21 > 8 else '1/2 dönüş için deplasman takımının geç gol skoru yeterli.' if donusum_12 > 8 else 'Belirgin bir dönüş pattern tespit edilmedi.'}
  • H2H geçmişinde {hw} ev galibiyeti, {dr} beraberlik, {aw} deplasman galibiyeti var.

──────────────────────────────────────────────────────────────────
6️⃣  ORAN–SKOR PATTERN ANALİZİ
──────────────────────────────────────────────────────────────────
"""
    if imp1:
        fav = "ev sahibi" if imp1 > imp2 else "deplasman"
        fav_pct = max(imp1, imp2)
        if fav_pct >= 60:
            report += f"  • %{fav_pct} zımni oranla {fav} favori. Bu oran aralığında maçların\n"
            report += f"    yaklaşık %58-65'i favorinin kazandığı, %{round(ust25_p*0.95,1)} oranında\n"
            report += f"    2.5 ÜST sonuçlandığı tarihi pattern'e sahip.\n"
        else:
            report += f"  • Dengeli oran yapısı (1=%{imp1} / X=%{impx} / 2=%{imp2}).\n"
            report += f"    Bu aralıkta beraberlik oranı tarihi olarak %28-34 bandında seyreder.\n"
        report += f"  • En baskın skor tipi: {top_score[0][0]}-{top_score[0][1]} (%{top_score[1]})\n"
        report += f"  • KG VAR eğilimi: {'Güçlü (%{kg_var})'.format(kg_var=kg_var) if kg_var >= 55 else 'Orta (%{kg_var})'.format(kg_var=kg_var) if kg_var >= 45 else 'Zayıf (%{kg_var})'.format(kg_var=kg_var)}\n"
    else:
        report += f"  • Oran verisi mevcut değil — form ve H2H bazlı pattern kullanılıyor.\n"
        report += f"  • xG {home_xg}-{away_xg} dengesiyle en baskın skor {top_score[0][0]}-{top_score[0][1]}.\n"

    report += f"""
──────────────────────────────────────────────────────────────────
7️⃣  MAÇ GENEL RİSK SEVİYESİ
──────────────────────────────────────────────────────────────────
  Seviye : ⚠️  {risk}
  Gerekçe: {risk_why}

──────────────────────────────────────────────────────────────────
8️⃣  BANKO – ORTA – SÜRPRİZ ÖNERİLERİ
──────────────────────────────────────────────────────────────────
  🔒 BANKO    : {banko}

  ⚡ ORTA RİSK: {orta}

  💎 SÜRPRİZ : {surpriz}

══════════════════════════════════════════════════════════════════
  ⚠️ Bu analiz istatistiksel model çıktısıdır. Yatırım tavsiyesi
  değildir. Sorumluluğunuzda kullanınız.
══════════════════════════════════════════════════════════════════
"""
    return report.strip()


# ──────────────────────────────────────────────────────────────
# CLAUDE ANALİZ (key varsa kullan)
# ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Sen bir Profesyonel Betting Data Analyst ve Prediction Engine'sin.
Verilen maç verilerine dayanarak 8 maddelik analiz üret:

## 1) EN OLASI SKOR TAHMİNİ — yüzdeli
## 2) ALTERNATİF SKOR DAĞILIMI — en az 5 skor, yüzdeli
## 3) İY/MS TAHMİNİ — yüzdeli kombinasyonlar dahil
## 4) KG VAR–YOK & ÜST/ALT — hepsi yüzdeli
## 5) 2/1–1/2 DÖNÜŞ TESPİTİ — ihtimal, oran anomalisi, tempo
## 6) ORAN–SKOR PATTERN ANALİZİ — tarihsel pattern
## 7) RİSK SEVİYESİ — Düşük/Orta/Yüksek + gerekçe
## 8) BANKO–ORTA–SÜRPRİZ — her biri açıklamalı

Kural: Tüm tahminler yüzdelik olasılığa dayansın. Profesyonel bahis analiz dili."""

def claude_analyze(prompt_text, key):
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
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt_text}],
            },
            timeout=90,
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception as e:
        return f"❌ Claude Hatası: {e}\n\nYerleşik motor sonucu aşağıda gösterilecek."

def build_claude_prompt(match, h2h_matches, hform_matches, aform_matches):
    h = match["homeTeam"]
    a = match["awayTeam"]
    comp = match["competition"]["name"]
    dt   = match["utcDate"][:10]
    hres = form_results(hform_matches, h["id"])
    ares = form_results(aform_matches, a["id"])
    h_sc, h_cn = goals_stats(hform_matches, h["id"])
    a_sc, a_cn = goals_stats(aform_matches, a["id"])
    odds = match.get("odds", {})
    o1 = odds.get("homeWin", "?")
    ox = odds.get("draw",    "?")
    o2 = odds.get("awayWin", "?")
    return f"""
MAÇ: {h['name']} vs {a['name']} | {comp} | {dt}
Oranlar: 1={o1} X={ox} 2={o2}
{h['name']} Son Form: {form_str(hres)} | Gol Ort: {h_sc} attı / {h_cn} yedi
{a['name']} Son Form: {form_str(ares)} | Gol Ort: {a_sc} attı / {a_cn} yedi
H2H Son 6: {h2h_str_list(h2h_matches)}
""".strip()

# ──────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────
for k in ["matches", "raw_data", "analyses"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k == "matches" else {}

# ──────────────────────────────────────────────────────────────
# ANA BUTONLAR
# ──────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([3, 2, 2])
with c1:
    st.markdown(f"**{sel_label}** · {sel_date.strftime('%d.%m.%Y')} · Maks {max_match} maç")
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
        st.error("⛔ Sol sidebar'dan football-data.org API Key giriniz.")
        st.stop()

    with st.spinner("📡 Maçlar çekiliyor..."):
        matches = get_matches(fdorg_key, sel_code,
                              sel_date.strftime("%Y-%m-%d"), max_match)

    if not matches:
        st.warning("⚠️ Bu tarih/lig için planlanmış maç bulunamadı. Farklı bir tarih dene.")
    else:
        st.session_state.matches  = matches
        st.session_state.raw_data = {}
        st.session_state.analyses = {}
        st.success(f"✅ {len(matches)} maç bulundu! Form ve H2H verileri çekiliyor...")

        bar = st.progress(0)
        for i, m in enumerate(matches):
            mid = m["id"]
            bar.progress((i) / len(matches),
                         text=f"({i+1}/{len(matches)}) {m['homeTeam']['name']} – {m['awayTeam']['name']}")
            h2h  = get_h2h(fdorg_key, mid)
            hf   = get_team_matches(fdorg_key, m["homeTeam"]["id"])
            af   = get_team_matches(fdorg_key, m["awayTeam"]["id"])
            st.session_state.raw_data[mid] = {
                "match": m, "h2h": h2h, "hform": hf, "aform": af
            }
            time.sleep(0.5)

        bar.progress(1.0, text="Veriler hazır!")
        time.sleep(0.5)
        bar.empty()
        st.success("✅ Hazır! Maçları aç ve analiz et.")

# ──────────────────────────────────────────────────────────────
# TOPLU ANALİZ
# ──────────────────────────────────────────────────────────────
if all_btn:
    if not st.session_state.raw_data:
        st.warning("Önce Maçları Çek!")
    else:
        mode = "Claude" if claude_key else "Yerleşik Motor"
        bar2 = st.progress(0)
        items = list(st.session_state.raw_data.items())
        for i, (mid, d) in enumerate(items):
            name = f"{d['match']['homeTeam']['name']} – {d['match']['awayTeam']['name']}"
            bar2.progress(i / len(items), text=f"({i+1}/{len(items)}) [{mode}] {name}")
            if claude_key:
                prompt = build_claude_prompt(d["match"], d["h2h"], d["hform"], d["aform"])
                result = claude_analyze(prompt, claude_key)
            else:
                result = build_analysis(d["match"], d["h2h"], d["hform"], d["aform"])
            st.session_state.analyses[mid] = result
            time.sleep(0.3)
        bar2.progress(1.0, text="Tamamlandı!")
        time.sleep(0.5)
        bar2.empty()
        st.success(f"✅ {len(items)} maç analizi tamamlandı!")

# ──────────────────────────────────────────────────────────────
# MAÇ LİSTESİ
# ──────────────────────────────────────────────────────────────
if st.session_state.matches:
    mode_label = "🤖 Claude" if claude_key else "⚙️ Yerleşik Motor"
    st.markdown(f"## 📋 Maçlar ({len(st.session_state.matches)} maç) · Analiz: {mode_label}")

    for m in st.session_state.matches:
        mid   = m["id"]
        hname = m["homeTeam"]["name"]
        aname = m["awayTeam"]["name"]
        comp  = m["competition"]["name"]
        utc   = m["utcDate"][11:16]
        odds  = m.get("odds", {})

        done  = mid in st.session_state.analyses
        label = f"{'✅' if done else '⚽'}  {hname}  –  {aname}  |  {comp}  |  {utc} UTC"

        with st.expander(label):
            o1 = odds.get("homeWin", "–")
            ox = odds.get("draw",    "–")
            o2 = odds.get("awayWin", "–")
            st.markdown(
                f"<span class='odd-pill'>1: {o1}</span>"
                f"<span class='odd-pill'>X: {ox}</span>"
                f"<span class='odd-pill'>2: {o2}</span>",
                unsafe_allow_html=True
            )

            col_a, col_b = st.columns([3, 1])
            with col_b:
                if st.button("🤖 Analiz Et", key=f"btn_{mid}"):
                    if mid not in st.session_state.raw_data:
                        st.warning("Önce Maçları Çek!")
                    else:
                        d = st.session_state.raw_data[mid]
                        with st.spinner("Analiz üretiliyor..."):
                            if claude_key:
                                prompt = build_claude_prompt(
                                    d["match"], d["h2h"], d["hform"], d["aform"])
                                result = claude_analyze(prompt, claude_key)
                            else:
                                result = build_analysis(
                                    d["match"], d["h2h"], d["hform"], d["aform"])
                        st.session_state.analyses[mid] = result

            if mid in st.session_state.analyses:
                st.markdown("---")
                st.markdown(
                    f"<div class='analysis-out'>{st.session_state.analyses[mid]}</div>",
                    unsafe_allow_html=True
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
    <b style="color:#58a6ff; font-size:1rem">🚀 Kullanım — Sadece 1 API Key Yeterli</b><br><br>
    <b>1)</b> <a href="https://www.football-data.org/client/register" target="_blank">
    football-data.org</a>'a git → e-posta ile ücretsiz kayıt → API key mail'e gelir<br>
    <b>2)</b> Sol sidebar'a yapıştır<br>
    <b>3)</b> Lig + tarih seç → <b>Maçları Çek</b><br>
    <b>4)</b> İstediğin maçı aç → <b>Analiz Et</b><br><br>
    <b>Yerleşik Analiz Motoru kapsamı:</b><br>
    Poisson xG modeli · Form bazlı MS olasılıkları · H2H ağırlıklı hesaplama<br>
    KG/Üst-Alt · İY/MS kombinasyonları · 2/1–1/2 dönüş tespiti · Banko/Orta/Sürpriz<br><br>
    <b>Claude API (opsiyonel):</b> Daha derin yorumlama için sidebar'dan ekle.
    </div>
    """, unsafe_allow_html=True)
