import streamlit as st
import requests
import math
import time
from datetime import date

st.set_page_config(
    page_title="⚽ BetAnalyst Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── API KEY'LER (sabit) ──────────────────────────────────────
FD_KEY   = "5cc88bf0dbac4fb699482886eb4c2270"
GROQ_KEY = "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"

# ═══════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#0a0f1a}

.hero{background:linear-gradient(135deg,#060d1a,#0d1f3c);border:1px solid #1e3a5f;
border-radius:16px;padding:1.6rem 2rem;margin-bottom:1.2rem;text-align:center}
.hero h1{color:#fff;margin:0;font-size:1.8rem;font-weight:700;letter-spacing:-1px}
.hero h1 em{color:#00e5a0;font-style:normal}
.hero p{color:#4a6080;margin:.4rem 0 0;font-size:.8rem}

/* Maç başlık kartı */
.mcard{background:#0d1525;border:1px solid #1a2e4a;border-radius:14px;
padding:1.2rem 1.4rem;margin-bottom:.8rem}
.mcard-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:.3rem}
.mcard-teams{font-size:1.1rem;font-weight:700;color:#00e5a0;letter-spacing:.5px}
.mcard-teams em{color:#fff;font-style:normal;font-size:.85rem;margin:0 .6rem}
.mcard-meta{font-size:.75rem;color:#4a6080}
.mcard-league{font-size:.72rem;color:#2a4060;margin-top:2px}

/* Senaryo kartları — fotoğraftaki gibi */
.scenario-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0}
.scenario-box{background:#111e30;border:1px solid #1a2e4a;border-radius:10px;
padding:10px 8px;text-align:center}
.scenario-box .slabel{font-size:.65rem;color:#4a6080;text-transform:uppercase;
letter-spacing:.08em;margin-bottom:4px}
.scenario-box .sval{font-size:1.15rem;font-weight:700;color:#00e5a0;
font-family:'JetBrains Mono',monospace}
.scenario-box.featured{border-color:#00e5a0;background:#071a12}
.scenario-box.featured .sval{color:#00ff99}
.scenario-row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;
margin:6px 0;padding:10px;background:#0d1a28;border-radius:10px;
border:1px solid #162030}
.scenario-row:hover{border-color:#1e3a5f}

/* Olasılık barlar */
.prob-section{margin:12px 0}
.prob-row{display:flex;align-items:center;gap:10px;margin:6px 0}
.prob-label{font-size:.75rem;color:#8899aa;min-width:110px;text-align:right}
.prob-bar-wrap{flex:1;background:#111e30;border-radius:4px;height:8px;overflow:hidden}
.prob-bar-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,#0062ff,#00e5a0)}
.prob-pct{font-size:.8rem;font-weight:600;color:#00e5a0;min-width:42px;text-align:right;
font-family:'JetBrains Mono',monospace}

/* MS 1/X/2 büyük gösterge */
.ms-trio{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:10px 0}
.ms-cell{background:#0d1a28;border:1px solid #1a2e4a;border-radius:10px;
padding:12px 8px;text-align:center}
.ms-cell .mc-label{font-size:.65rem;color:#4a6080;text-transform:uppercase;letter-spacing:.08em}
.ms-cell .mc-pct{font-size:1.4rem;font-weight:700;color:#00e5a0;
font-family:'JetBrains Mono',monospace;margin:4px 0}
.ms-cell .mc-name{font-size:.65rem;color:#8899aa}
.ms-cell.fav{border-color:#00e5a0;background:#071a12}
.ms-cell.fav .mc-pct{color:#00ff99}

/* İY/MS kombolar */
.combo-section{background:#0d1525;border:1px solid #1a2e4a;border-radius:12px;padding:14px}
.combo-title{font-size:.7rem;color:#4a6080;text-transform:uppercase;
letter-spacing:.1em;margin-bottom:10px}
.combo-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.combo-cell{background:#111e30;border:1px solid #1a2e4a;border-radius:8px;
padding:8px 6px;text-align:center}
.combo-cell .ck{font-size:.95rem;font-weight:700;color:#e2e8f0;
font-family:'JetBrains Mono',monospace}
.combo-cell .cv{font-size:.7rem;color:#4a6080;margin-top:2px}
.combo-cell.c1{border-color:#f59e0b;background:#1a1200}
.combo-cell.c1 .ck{color:#fbbf24}
.combo-cell.c1 .cv{color:#92700a}
.combo-cell.c2{border-color:#00e5a0;background:#071a12}
.combo-cell.c2 .ck{color:#00e5a0}
.combo-cell.c3{border-color:#6d28d9;background:#150d2a}
.combo-cell.c3 .ck{color:#c4b5fd}

/* Tahmin + riskli kutular */
.pred-box{border-radius:10px;padding:12px 16px;margin:6px 0;
display:flex;align-items:center;gap:12px}
.pred-box.banko{background:#071a12;border:1px solid #166534}
.pred-box.orta{background:#0c1a2e;border:1px solid #1d4ed8}
.pred-box.surpriz{background:#150d2a;border:1px solid #6d28d9}
.pred-box.risky{background:#1a0c00;border:1px solid #9a3412}
.pred-icon{font-size:1.3rem}
.pred-content .ptag{font-size:.65rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase}
.pred-content.banko .ptag{color:#86efac}
.pred-content.orta  .ptag{color:#93c5fd}
.pred-content.surpriz .ptag{color:#c4b5fd}
.pred-content.risky .ptag{color:#fb923c}
.pred-content .ppick{font-size:.95rem;font-weight:700;color:#f1f5f9;margin:2px 0}
.pred-content .pwhy{font-size:.72rem;color:#6b7280}

/* Analiz metin kutusu */
.analysis-box{background:#060d1a;border:1px solid #1a2e4a;border-radius:12px;
padding:1.2rem 1.4rem;font-size:.83rem;color:#c0cfe0;line-height:1.95;
white-space:pre-wrap;max-height:700px;overflow-y:auto;
font-family:'JetBrains Mono',monospace}

/* Dönüş kartları */
.donus-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}
.donus-card{background:#0d1a28;border:1px solid #1a2e4a;border-radius:10px;padding:12px}
.donus-card h4{font-size:.78rem;color:#8899aa;margin:0 0 8px;font-weight:600}
.donus-card .dval{font-size:1.5rem;font-weight:700;color:#00e5a0;
font-family:'JetBrains Mono',monospace}
.donus-card .dsub{font-size:.7rem;color:#4a6080;margin-top:2px}
.donus-card.hot{border-color:#f59e0b}
.donus-card.hot .dval{color:#fbbf24}

/* Disclaimer */
.disclaimer{background:#0a0f1a;border:1px solid #1a2030;border-radius:8px;
padding:8px 12px;font-size:.7rem;color:#2a4060;text-align:center;margin-top:16px}

/* Tab fix */
div[data-testid="stExpander"]{border:1px solid #1a2e4a!important;
border-radius:12px!important;background:#0d1525!important;overflow:hidden}
.stTabs [data-baseweb="tab-list"]{background:#0d1525;border-radius:8px;padding:4px;gap:4px}
.stTabs [data-baseweb="tab"]{border-radius:6px;color:#4a6080;font-size:.8rem;padding:5px 12px}
.stTabs [aria-selected="true"]{background:#111e30!important;color:#00e5a0!important}

button[kind="primary"]{background:#00e5a0!important;color:#060d1a!important;
font-weight:700!important;border:none!important}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>⚽ Bet<em>Analyst</em> Pro</h1>
  <p>football-data.org · Groq Llama 3.3 70B · Maça Özel Profesyonel Analiz</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Filtreler")
    st.success("✅ API key'ler hazır — ekstra giriş gerekmez")

    LEAGUE_GROUPS = {
        "🌍 Avrupa Kulüp": {
            "UEFA Champions League ⭐": "CL",
            "UEFA Europa League":       "EL",
            "UEFA Conference League":   "ECL",
        },
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 İngiltere": {
            "Premier League":           "PL",
            "Championship (2. Lig)":    "ELC",
            "FA Cup":                   "FAC",
        },
        "🇪🇸 İspanya": {"La Liga": "PD"},
        "🇩🇪 Almanya": {"Bundesliga": "BL1"},
        "🇮🇹 İtalya":  {"Serie A": "SA"},
        "🇫🇷 Fransa":  {"Ligue 1": "FL1"},
        "🇳🇱 Hollanda":{"Eredivisie": "DED"},
        "🇵🇹 Portekiz":{"Primeira Liga": "PPL"},
        "🇧🇷 Brezilya":{"Série A (Brasileirão)": "BSA"},
        "🌐 Milli":    {
            "FIFA World Cup": "WC",
            "UEFA Avrupa Şampiyonası": "EC",
        },
    }

    sel_group = st.selectbox("Kategori", list(LEAGUE_GROUPS.keys()))
    sel_label = st.selectbox("Lig", list(LEAGUE_GROUPS[sel_group].keys()))
    sel_code  = LEAGUE_GROUPS[sel_group][sel_label]
    sel_date  = st.date_input("Tarih", value=date.today())
    max_match = st.slider("Maks Maç", 1, 15, 8)
    n_form    = st.slider("Form Maç Sayısı", 5, 12, 8)
    n_h2h     = st.slider("H2H Maç Sayısı", 4, 10, 6)
    groq_model= st.selectbox("Model", ["llama-3.3-70b-versatile", "llama3-70b-8192"])
    debug     = st.checkbox("🐛 Debug", value=False)
    st.caption("Tüm ligler ücretsiz · 500K Groq token/gün")

# ═══════════════════════════════════════════════════════════
# API KATMANI
# ═══════════════════════════════════════════════════════════
BASE = "https://api.football-data.org/v4"

def fd_get(path, params=None):
    try:
        r = requests.get(f"{BASE}{path}", headers={"X-Auth-Token": FD_KEY},
                         params=params or {}, timeout=15)
        if r.status_code == 429:
            st.warning("⏳ Rate limit — 65sn..."); time.sleep(66)
            r = requests.get(f"{BASE}{path}", headers={"X-Auth-Token": FD_KEY},
                             params=params or {}, timeout=15)
        if debug: st.caption(f"🐛 {path} → {r.status_code}")
        return r.json() if r.status_code == 200 else {}
    except Exception as e:
        st.error(f"API: {e}"); return {}

def api_matches(code, dt, lim):
    d = fd_get(f"/competitions/{code}/matches",
               {"dateFrom": dt, "dateTo": dt, "status": "SCHEDULED,TIMED,POSTPONED"})
    return d.get("matches", [])[:lim]

def api_team_matches(tid, n):
    return fd_get(f"/teams/{tid}/matches",
                  {"status": "FINISHED", "limit": n}).get("matches", [])

def api_h2h(mid, n):
    return fd_get(f"/matches/{mid}/head2head", {"limit": n}).get("matches", [])

def api_standings(code):
    try: return fd_get(f"/competitions/{code}/standings")["standings"][0]["table"]
    except: return []

def api_scorers(code):
    return fd_get(f"/competitions/{code}/scorers", {"limit": 20}).get("scorers", [])

# ═══════════════════════════════════════════════════════════
# VERİ İŞLEME
# ═══════════════════════════════════════════════════════════

def parse_form(matches, tid):
    if not matches: return {}
    ms_r, ht_r = [], []
    gf, gc, htgf, htgc = [], [], [], []
    h_gf=h_gc=h_n=a_gf=a_gc=a_n = 0
    for m in matches:
        hid = m["homeTeam"]["id"]
        fh  = m["score"]["fullTime"]["home"] or 0
        fa  = m["score"]["fullTime"]["away"] or 0
        hh  = (m["score"].get("halfTime") or {}).get("home") or 0
        ha  = (m["score"].get("halfTime") or {}).get("away") or 0
        if hid == tid:
            my_f,op_f,my_h,op_h = fh,fa,hh,ha
            h_gf+=fh; h_gc+=fa; h_n+=1
        else:
            my_f,op_f,my_h,op_h = fa,fh,ha,hh
            a_gf+=fa; a_gc+=fh; a_n+=1
        ms_r.append("G" if my_f>op_f else "B" if my_f==op_f else "M")
        ht_r.append("G" if my_h>op_h else "B" if my_h==op_h else "M")
        gf.append(my_f); gc.append(op_f)
        htgf.append(my_h); htgc.append(op_h)
    n = len(ms_r)
    if n == 0: return {}
    pts5    = sum({"G":3,"B":1,"M":0}[r] for r in ms_r[:5])
    tot_gf  = sum(gf); tot_htgf = sum(htgf)
    ht_pct  = round(tot_htgf/tot_gf*100,1) if tot_gf>0 else 45.0
    st_gf   = [f-h for f,h in zip(gf,htgf)]
    st_gc   = [c-h for c,h in zip(gc,htgc)]
    sr = ms_r[0]; sn = 0
    for r in ms_r:
        if r==sr: sn+=1
        else: break
    return {
        "n":n, "form_str":"-".join(ms_r[:6]), "ht_form":"-".join(ht_r[:5]),
        "pts5":pts5, "pts_pct":round(pts5/15*100,1),
        "avg_gf":round(sum(gf)/n,2),  "avg_gc":round(sum(gc)/n,2),
        "ht_avg_gf":round(sum(htgf)/n,2), "ht_avg_gc":round(sum(htgc)/n,2),
        "st_avg_gf":round(sum(st_gf)/n,2),"st_avg_gc":round(sum(st_gc)/n,2),
        "ht_pct":ht_pct, "st_pct":round(100-ht_pct,1),
        "h_avg_gf":round(h_gf/h_n,2) if h_n else 0,
        "h_avg_gc":round(h_gc/h_n,2) if h_n else 0, "h_n":h_n,
        "a_avg_gf":round(a_gf/a_n,2) if a_n else 0,
        "a_avg_gc":round(a_gc/a_n,2) if a_n else 0, "a_n":a_n,
        "btts":sum(1 for f,c in zip(gf,gc) if f>0 and c>0),
        "o25":sum(1 for f,c in zip(gf,gc) if f+c>2),
        "o35":sum(1 for f,c in zip(gf,gc) if f+c>3),
        "cs":sum(1 for c in gc if c==0),
        "fts":sum(1 for f in gf if f==0),
        "streak":f"{sn} {'galibiyet' if sr=='G' else 'beraberlik' if sr=='B' else 'mağlubiyet'} serisi",
        "ms_scores":[f"{f}-{c}" for f,c in zip(gf[:6],gc[:6])],
        "ht_scores":[f"{h}-{a}" for h,a in zip(htgf[:6],htgc[:6])],
    }

def parse_h2h(matches, home_id):
    if not matches: return {}
    hw=aw=dr=ht_hw=ht_aw=ht_dr=rev21=rev12=revx1=revx2=btts=o25 = 0
    gl, ms_sc, ht_sc = [], [], []
    for m in matches:
        hid = m["homeTeam"]["id"]
        fh  = m["score"]["fullTime"]["home"] or 0
        fa  = m["score"]["fullTime"]["away"] or 0
        hh  = (m["score"].get("halfTime") or {}).get("home") or 0
        ha  = (m["score"].get("halfTime") or {}).get("away") or 0
        if hid==home_id: my_f,op_f,my_h,op_h=fh,fa,hh,ha
        else:            my_f,op_f,my_h,op_h=fa,fh,ha,hh
        if my_f>op_f: hw+=1
        elif my_f<op_f: aw+=1
        else: dr+=1
        if my_h>op_h: ht_hw+=1
        elif my_h<op_h: ht_aw+=1
        else: ht_dr+=1
        if my_h<op_h and my_f>op_f: rev21+=1
        if my_h>op_h and my_f<op_f: rev12+=1
        if my_h==op_h and my_f>op_f: revx1+=1
        if my_h==op_h and my_f<op_f: revx2+=1
        if my_f>0 and op_f>0: btts+=1
        if my_f+op_f>2: o25+=1
        gl.append(my_f+op_f)
        ms_sc.append(f"{my_f}-{op_f}")
        ht_sc.append(f"{my_h}-{op_h}")
    n=len(matches)
    p=lambda x: round(x/n*100,1)
    return {
        "n":n,"hw":hw,"dr":dr,"aw":aw,
        "hw_pct":p(hw),"dr_pct":p(dr),"aw_pct":p(aw),
        "ht_hw":ht_hw,"ht_dr":ht_dr,"ht_aw":ht_aw,
        "ht_hw_pct":p(ht_hw),"ht_dr_pct":p(ht_dr),"ht_aw_pct":p(ht_aw),
        "rev21":rev21,"rev21_pct":p(rev21),
        "rev12":rev12,"rev12_pct":p(rev12),
        "revx1":revx1,"revx1_pct":p(revx1),
        "revx2":revx2,"revx2_pct":p(revx2),
        "avg_goals":round(sum(gl)/n,2) if n else 0,
        "o25":o25,"o25_pct":p(o25),
        "btts":btts,"btts_pct":p(btts),
        "ms_scores":ms_sc,"ht_scores":ht_sc,
    }

def find_standing(table, tid):
    for r in table:
        if r.get("team",{}).get("id")==tid: return r
    return {}

def find_scorer(scorers, tid):
    for s in scorers:
        if s.get("team",{}).get("id")==tid:
            p=s.get("player",{})
            return {"name":p.get("name","?"),"goals":s.get("goals",0),"assists":s.get("assists",0)}
    return {}

# ═══════════════════════════════════════════════════════════
# POISSON MODELİ
# ═══════════════════════════════════════════════════════════

def poi(lam, k):
    lam=max(lam,0.01)
    return math.exp(-lam)*(lam**k)/math.factorial(k)

def calc_xg(tf, of, is_home):
    base = tf.get("avg_gf",1.2) if tf else 1.2
    loc  = (tf.get("h_avg_gf" if is_home else "a_avg_gf", base) if tf else base) or base
    opp  = of.get("avg_gc",1.2) if of else 1.2
    return max(0.3, round(base*0.30+loc*0.40+opp*0.30, 3))

def calc_ht_xg(f, full_xg):
    raw = f.get("ht_avg_gf", full_xg*0.43) if f else full_xg*0.43
    return max(0.18, round(raw, 3))

def score_mat(hx, ax, mx=6):
    return {(h,a):round(poi(hx,h)*poi(ax,a)*100,3)
            for h in range(mx+1) for a in range(mx+1)}

def compute_stats(ms_mat, ht_mat):
    p1 =round(sum(v for(h,a),v in ms_mat.items() if h>a),1)
    px =round(sum(v for(h,a),v in ms_mat.items() if h==a),1)
    p2 =round(100-p1-px,1)
    iy1=round(sum(v for(h,a),v in ht_mat.items() if h>a),1)
    iyx=round(sum(v for(h,a),v in ht_mat.items() if h==a),1)
    iy2=round(100-iy1-iyx,1)
    combos={}
    for ir,ip in [("1",iy1),("X",iyx),("2",iy2)]:
        for mr,mp in [("1",p1),("X",px),("2",p2)]:
            combos[f"{ir}/{mr}"]=round(ip*mp/100,2)
    cs=sorted(combos.items(),key=lambda x:-x[1])
    u25=round(sum(v for(h,a),v in ms_mat.items() if h+a>2),1)
    u35=round(sum(v for(h,a),v in ms_mat.items() if h+a>3),1)
    u45=round(sum(v for(h,a),v in ms_mat.items() if h+a>4),1)
    kg =round(sum(v for(h,a),v in ms_mat.items() if h>0 and a>0),1)
    return {
        "p1":p1,"px":px,"p2":p2,
        "iy1":iy1,"iyx":iyx,"iy2":iy2,
        "combos":cs,
        "u25":u25,"alt25":round(100-u25,1),
        "u35":u35,"u45":u45,
        "kg":kg,"kgy":round(100-kg,1),
        "rev21":round(iy2*p1/100,2),
        "rev12":round(iy1*p2/100,2),
    }

# ═══════════════════════════════════════════════════════════
# MAÇA ÖZEL KARAKTER
# ═══════════════════════════════════════════════════════════

def match_chars(h, a, hf, af, h2h, hxg, axg, stats, h_stand, a_stand, h_sc, a_sc):
    c = []
    diff = round(hxg-axg,2)
    if diff>0.5:    c.append(f"EV FAVORİ: xG farkı +{diff} ({hxg} vs {axg})")
    elif diff<-0.5: c.append(f"DEP FAVORİ: xG farkı +{abs(diff)} ({axg} vs {hxg})")
    else:           c.append(f"DENGE: xG hemen hemen eşit ({hxg} vs {axg})")

    hp=hf.get("pts5",0) if hf else 0; ap=af.get("pts5",0) if af else 0
    if hp>=12: c.append(f"{h} ÇOK İYİ FORMDA ({hp}/15)")
    elif hp<=4: c.append(f"{h} KÖTÜ FORMDA ({hp}/15)")
    if ap>=12: c.append(f"{a} ÇOK İYİ FORMDA ({ap}/15)")
    elif ap<=4: c.append(f"{a} KÖTÜ FORMDA ({ap}/15)")

    if hf:
        if hf.get("cs",0)>=3: c.append(f"{h} SAĞLAM SAVUNMA: {hf['cs']}/{hf['n']} kuru kaldı")
        if hf.get("avg_gf",0)>=2.2: c.append(f"{h} GOL MAKİNESİ: {hf['avg_gf']} gol/maç")
        if hf.get("avg_gc",0)>=2.0: c.append(f"{h} SIFIR SAVUNMA: {hf['avg_gc']} yiyor/maç")
        if hf.get("st_pct",55)>=60: c.append(f"{h} 2Y TAKIM: gollerinin %{hf['st_pct']}'i 2Y'de → 2/1 zemini")
        if hf.get("ht_pct",45)>=58: c.append(f"{h} ERKEN BASKI: gollerinin %{hf['ht_pct']}'i İY'de")
    if af:
        if af.get("cs",0)>=3: c.append(f"{a} SAĞLAM SAVUNMA: {af['cs']}/{af['n']} kuru kaldı")
        if af.get("avg_gf",0)>=2.0: c.append(f"{a} ETKİLİ HÜCUM: {af['avg_gf']} gol/maç")
        if af.get("avg_gc",0)>=2.0: c.append(f"{a} SIFIR SAVUNMA: {af['avg_gc']} yiyor/maç")
        if af.get("st_pct",55)>=60: c.append(f"{a} 2Y TAKIM: gollerinin %{af['st_pct']}'i 2Y'de → 1/2 zemini")

    if h2h and h2h.get("n",0)>=3:
        if h2h.get("rev21_pct",0)>=25: c.append(f"H2H 2/1 PATTERN: %{h2h['rev21_pct']} ({h2h['rev21']}/{h2h['n']} maç)")
        if h2h.get("rev12_pct",0)>=25: c.append(f"H2H 1/2 PATTERN: %{h2h['rev12_pct']} ({h2h['rev12']}/{h2h['n']} maç)")
        if h2h.get("o25_pct",0)>=70:   c.append(f"H2H GOL ZİYAFETİ: %{h2h['o25_pct']} 2.5 üst bitti")
        if h2h.get("btts_pct",0)>=65:  c.append(f"H2H KG VAR: %{h2h['btts_pct']} oranında")

    if h_stand and a_stand:
        hp2=h_stand.get("position",10); ap2=a_stand.get("position",10)
        if hp2>=16: c.append(f"DÜŞME TEHLİKESİ: {h} ligde {hp2}. sırada")
        if ap2>=16: c.append(f"DÜŞME TEHLİKESİ: {a} ligde {ap2}. sırada")
        if hp2<=4 and ap2>10: c.append(f"MOTİVASYON FARKI: {h} ({hp2}. sıra) lider grupta, {a} ({ap2}. sıra) arkada")

    if h_sc and h_sc.get("goals",0)>=10:
        c.append(f"GOLCÜ: {h_sc['name']} bu sezon {h_sc['goals']} gol")
    if a_sc and a_sc.get("goals",0)>=10:
        c.append(f"GOLCÜ: {a_sc['name']} bu sezon {a_sc['goals']} gol")

    total_xg = round(hxg+axg,2)
    if total_xg>=3.2:  c.append(f"YÜKSEK xG: Toplam {total_xg} → Çok gollü maç bekleniyor")
    elif total_xg<=1.8:c.append(f"DÜŞÜK xG: Toplam {total_xg} → Az gollü sıkışık maç")
    return c

# ═══════════════════════════════════════════════════════════
# GROQ PROMPT
# ═══════════════════════════════════════════════════════════

def build_prompt(h, a, hf, af, h2h, hxg, axg, h_htxg, a_htxg,
                 stats, h_stand, a_stand, h_sc, a_sc, top_ms, top_ht):
    chars = match_chars(h,a,hf,af,h2h,hxg,axg,stats,h_stand,a_stand,h_sc,a_sc)
    fv = lambda d,k,dv=0: d.get(k,dv) if d else dv
    fl = lambda d,k: " | ".join((d.get(k,[]) if d else [])[:5])
    hs=h_stand or {}; as_=a_stand or {}

    return f"""Sen dünyaca ünlü bir profesyonel futbol bahis analistsin.
Bu maç için YALNIZCA verilen verilere dayalı, jenerik cümle KULLANMADAN, her bölümde takım isimlerini ve gerçek rakamları kullanarak analiz yaz.
Türkçe. Her tahmin yüzdelik olasılıkla.

MAÇIN KARAKTERİ:
{"".join("▶ "+c+chr(10) for c in chars)}

VERİ:
MAÇ: {h} (Ev) vs {a} (Dep)
PUAN: {h} → Sıra:{hs.get('position','?')} {hs.get('won','?')}G-{hs.get('draw','?')}B-{hs.get('lost','?')}M Gol:{hs.get('goalsFor','?')}-{hs.get('goalsAgainst','?')} Puan:{hs.get('points','?')}
PUAN: {a} → Sıra:{as_.get('position','?')} {as_.get('won','?')}G-{as_.get('draw','?')}B-{as_.get('lost','?')}M Gol:{as_.get('goalsFor','?')}-{as_.get('goalsAgainst','?')} Puan:{as_.get('points','?')}
GOLCÜ: {h}: {h_sc.get('name','?') if h_sc else '?'} {h_sc.get('goals',0) if h_sc else 0}gol | {a}: {a_sc.get('name','?') if a_sc else '?'} {a_sc.get('goals',0) if a_sc else 0}gol

{h} FORM (son {fv(hf,'n')} maç):
MS:{fv(hf,'form_str','?')} İY:{fv(hf,'ht_form','?')} Puan:{fv(hf,'pts5')}/15
Son MS: {fl(hf,'ms_scores')} | Son İY: {fl(hf,'ht_scores')}
Gol: {fv(hf,'avg_gf')} attı/{fv(hf,'avg_gc')} yedi | İç saha: {fv(hf,'h_avg_gf')}/{fv(hf,'h_avg_gc')}
İY: {fv(hf,'ht_avg_gf')}gol attı/{fv(hf,'ht_avg_gc')}yedi | 2Y: {fv(hf,'st_avg_gf')}gol attı/{fv(hf,'st_avg_gc')}yedi
GOL ZAMANI: %{fv(hf,'ht_pct',45)} İY — %{fv(hf,'st_pct',55)} 2Y
KG VAR:{fv(hf,'btts')}/{fv(hf,'n')} | 2.5Üst:{fv(hf,'o25')}/{fv(hf,'n')} | CS:{fv(hf,'cs')}/{fv(hf,'n')} | Gol Yok:{fv(hf,'fts')}/{fv(hf,'n')}

{a} FORM (son {fv(af,'n')} maç):
MS:{fv(af,'form_str','?')} İY:{fv(af,'ht_form','?')} Puan:{fv(af,'pts5')}/15
Son MS: {fl(af,'ms_scores')} | Son İY: {fl(af,'ht_scores')}
Gol: {fv(af,'avg_gf')} attı/{fv(af,'avg_gc')} yedi | Deplasman: {fv(af,'a_avg_gf')}/{fv(af,'a_avg_gc')}
İY: {fv(af,'ht_avg_gf')}gol attı/{fv(af,'ht_avg_gc')}yedi | 2Y: {fv(af,'st_avg_gf')}gol attı/{fv(af,'st_avg_gc')}yedi
GOL ZAMANI: %{fv(af,'ht_pct',45)} İY — %{fv(af,'st_pct',55)} 2Y
KG VAR:{fv(af,'btts')}/{fv(af,'n')} | 2.5Üst:{fv(af,'o25')}/{fv(af,'n')} | CS:{fv(af,'cs')}/{fv(af,'n')} | Gol Yok:{fv(af,'fts')}/{fv(af,'n')}

H2H (son {h2h.get('n',0)} maç):
MS: {h} %{h2h.get('hw_pct',0)} / Beraberlik %{h2h.get('dr_pct',0)} / {a} %{h2h.get('aw_pct',0)}
İY: {h} %{h2h.get('ht_hw_pct',0)} / Beraberlik %{h2h.get('ht_dr_pct',0)} / {a} %{h2h.get('ht_aw_pct',0)}
Son MS: {" | ".join(h2h.get('ms_scores',[])[:5])} | Son İY: {" | ".join(h2h.get('ht_scores',[])[:5])}
2.5Üst:%{h2h.get('o25_pct',0)} | KGVAR:%{h2h.get('btts_pct',0)} | GolOrt:{h2h.get('avg_goals',0)}
2/1:{h2h.get('rev21',0)}/{h2h.get('n',0)}(%{h2h.get('rev21_pct',0)}) | 1/2:{h2h.get('rev12',0)}/{h2h.get('n',0)}(%{h2h.get('rev12_pct',0)}) | X/1:{h2h.get('revx1',0)}/{h2h.get('n',0)}(%{h2h.get('revx1_pct',0)})

xG: {h}={hxg}(İY:{h_htxg}) | {a}={axg}(İY:{a_htxg}) | Toplam={round(hxg+axg,2)}
Poisson MS: 1=%{stats['p1']} X=%{stats['px']} 2=%{stats['p2']}
Poisson İY: 1=%{stats['iy1']} X=%{stats['iyx']} 2=%{stats['iy2']}
Top MS: {" | ".join(f"{hg}-{ag}(%{round(v,1)})" for(hg,ag),v in top_ms[:6])}
Top İY: {" | ".join(f"{hg}-{ag}(%{round(v,1)})" for(hg,ag),v in top_ht[:5])}
Kombolar: {" | ".join(f"{k}(%{round(v,1)})" for k,v in stats['combos'][:6])}
KG VAR=%{stats['kg']} | 2.5Üst=%{stats['u25']} | 3.5Üst=%{stats['u35']}
Model 2/1=%{stats['rev21']} H2H 2/1=%{h2h.get('rev21_pct',0)}
Model 1/2=%{stats['rev12']} H2H 1/2=%{h2h.get('rev12_pct',0)}

─────────────────────────────────────────
CEVAP FORMATI (tam olarak bu yapıyı kullan):
─────────────────────────────────────────

### 1) EN OLASI İY SKORU
[İY skor %olasılık] — [Bu maçın İY xG ve İY H2H verisiyle açıklama]

### 2) EN OLASI MS SKORU
[MS skor %olasılık] — [xG, form, H2H ile açıklama]

### 3) İY/MS SENARYO TABLOSI
Her satır: İY [X-Y] → 2Y [X-Y] → MS [X-Y] | %olasılık | Açıklama
En az 4 senaryo yaz. Format önemli — uygulamada kutucuklara alınacak.

### 4) MS 1/X/2 DETAYI
1 (%{stats['p1']}): [Bu maça özgü gerekçe]
X (%{stats['px']}): [Bu maça özgü gerekçe]
2 (%{stats['p2']}): [Bu maça özgü gerekçe]

### 5) GOL TAHMİNLERİ
KG VAR (%{stats['kg']}): [son maç KG trendi]
2.5 ÜST (%{stats['u25']}): [xG ve H2H ile gerekçe]
2.5 ALT (%{stats['alt25']}): [gerekçe]
3.5 ÜST (%{stats['u35']}): [gerekçe]

### 6) 2/1 – 1/2 DÖNÜŞ
2/1 (İY:{a} önde → MS:{h} kazanır): Model %{stats['rev21']} | H2H %{h2h.get('rev21_pct',0)}
→ {h}'ın 2Y gol yükü %{fv(hf,'st_pct',55)} — dönüş zemini: [değerlendir]
→ Senaryo ve net karar (gerçekçi mi?)

1/2 (İY:{h} önde → MS:{a} kazanır): Model %{stats['rev12']} | H2H %{h2h.get('rev12_pct',0)}
→ {a}'nın 2Y gol yükü %{fv(af,'st_pct',55)} — dönüş zemini: [değerlendir]
→ Senaryo ve net karar

KESİN KARAR: [Hangi dönüş daha mümkün ve neden?]

### 7) MAÇ ANALİZİ
[Bu maçın hikayesini anlat — 3-4 cümle, yalnızca bu maçın spesifik verileriyle]

### 8) TAVSİYELER
BANKO: [tahmin] — %güven — [gerekçe]
ORTA: [tahmin] — %güven — [gerekçe]
RİSKLİ: [tahmin + oran beklentisi] — [gerekçe]
SKOR: İY [X-Y] + MS [X-Y] — [gerekçe]
"""

def groq_call(prompt):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":groq_model,"messages":[{"role":"user","content":prompt}],
                  "temperature":0.15,"max_tokens":4000},
            timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Groq Hatası: {e}"

# ═══════════════════════════════════════════════════════════
# ANALİZ PARSE — Groq çıktısından senaryo, tahmin ve metin çıkar
# ═══════════════════════════════════════════════════════════

def parse_analysis(text):
    """Groq çıktısını bölümlere ayır."""
    import re
    sections = {}
    # Başlıkları bul
    parts = re.split(r'###\s*\d+\)\s*', text)
    headers = re.findall(r'###\s*\d+\)\s*(.+)', text)
    for i, (hdr, content) in enumerate(zip(headers, parts[1:])):
        key = hdr.strip().upper()
        sections[key] = content.strip()

    # Senaryo satırlarını parse et
    scenarios = []
    scenario_text = ""
    for k, v in sections.items():
        if "SENARYO" in k or "TABLO" in k:
            scenario_text = v; break
    if scenario_text:
        for line in scenario_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"): continue
            # Format: İY X-Y → 2Y X-Y → MS X-Y | %xx | açıklama
            m = re.search(r'İY\s*(\d-\d).*?2Y\s*(\d-\d).*?MS\s*(\d-\d).*?%?\s*(\d+\.?\d*)', line, re.I)
            if m:
                scenarios.append({
                    "iy": m.group(1), "2y": m.group(2),
                    "ms": m.group(3), "pct": m.group(4),
                    "desc": line
                })
            elif re.search(r'\d-\d', line):
                # Fallback: herhangi skor satırı
                scores = re.findall(r'\d-\d', line)
                pct    = re.search(r'%\s*(\d+\.?\d*)', line)
                if scores:
                    scenarios.append({
                        "iy": scores[0] if len(scores)>0 else "?",
                        "2y": scores[1] if len(scores)>1 else "?",
                        "ms": scores[2] if len(scores)>2 else scores[-1],
                        "pct": pct.group(1) if pct else "?",
                        "desc": line
                    })

    # Tavsiyeler
    preds = {}
    pred_text = ""
    for k, v in sections.items():
        if "TAVSİYE" in k or "TAVSIYE" in k:
            pred_text = v; break
    if pred_text:
        for line in pred_text.split("\n"):
            for tag in ["BANKO","ORTA","RİSKLİ","RISKI","SKOR"]:
                if line.strip().upper().startswith(tag):
                    preds[tag.replace("İ","I").replace("Ş","S")] = line.split(":",1)[-1].strip()

    # Maç analizi metni
    analysis_text = ""
    for k, v in sections.items():
        if "ANALİZ" in k or "ANALIZ" in k:
            analysis_text = v; break
    if not analysis_text:
        analysis_text = text  # Fallback: tam metin

    return sections, scenarios, preds, analysis_text

# ═══════════════════════════════════════════════════════════
# UI RENDER — Fotoğraftaki gibi kartlar
# ═══════════════════════════════════════════════════════════

def render_analysis_ui(h, a, stats, top_ms, top_ht, h2h, hf, af, hxg, axg, analysis_text):
    """Parse edilmiş analizi fotoğraftaki gibi render et."""
    sections, scenarios, preds, match_analysis = parse_analysis(analysis_text)

    # ── 1. Takım başlığı ──────────────────────────────────
    st.markdown(f"""
    <div style="background:#111e30;border:1px solid #1a3050;border-radius:12px;
    padding:14px 16px;margin-bottom:12px">
      <div style="font-size:.7rem;color:#4a6080;margin-bottom:4px">{sel_label.upper()} · {sel_date.strftime('%d.%m.%Y')}</div>
      <div style="font-size:1.2rem;font-weight:700;color:#00e5a0;letter-spacing:.5px">
        {h} <span style="color:#2a4060;font-size:.9rem">VS</span> {a}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 2. Senaryolar ────────────────────────────────────
    if scenarios:
        st.markdown('<div style="font-size:.72rem;color:#4a6080;font-weight:600;'
                    'letter-spacing:.1em;text-transform:uppercase;margin:10px 0 6px">📊 SENARYOLAR</div>',
                    unsafe_allow_html=True)
        for sc in scenarios[:4]:
            st.markdown(f"""
<div class="scenario-row">
  <div class="scenario-box">
    <div class="slabel">İY</div>
    <div class="sval">{sc['iy']}</div>
  </div>
  <div class="scenario-box">
    <div class="slabel">2H</div>
    <div class="sval">{sc['2y']}</div>
  </div>
  <div class="scenario-box featured">
    <div class="slabel">MS</div>
    <div class="sval">{sc['ms']}</div>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        # Fallback: Poisson top skorları
        st.markdown('<div style="font-size:.72rem;color:#4a6080;font-weight:600;'
                    'letter-spacing:.1em;text-transform:uppercase;margin:10px 0 6px">📊 EN OLASI SKORLAR</div>',
                    unsafe_allow_html=True)
        top_ht_scores = top_ht[:4]
        top_ms_scores = top_ms[:4]
        for i in range(min(4, len(top_ms_scores))):
            ht_s = top_ht_scores[i][0] if i < len(top_ht_scores) else ("?","?")
            ms_s = top_ms_scores[i][0]
            iy_str = f"{ht_s[0]}-{ht_s[1]}"
            ms_str = f"{ms_s[0]}-{ms_s[1]}"
            # 2Y = MS - İY
            try:
                sy = f"{ms_s[0]-ht_s[0]}-{ms_s[1]-ht_s[1]}"
                if '-' in sy and (int(sy.split('-')[0])<0 or int(sy.split('-')[1])<0): sy="?"
            except: sy = "?"
            st.markdown(f"""
<div class="scenario-row">
  <div class="scenario-box"><div class="slabel">İY</div><div class="sval">{iy_str}</div></div>
  <div class="scenario-box"><div class="slabel">2H</div><div class="sval">{sy}</div></div>
  <div class="scenario-box featured"><div class="slabel">MS</div><div class="sval">{ms_str}</div></div>
</div>""", unsafe_allow_html=True)

    # ── 3. Tahmin + Riskli ──────────────────────────────
    banko  = preds.get("BANKO","")
    orta   = preds.get("ORTA","")
    riskli = preds.get("RISKI", preds.get("RİSKLİ",""))
    skor   = preds.get("SKOR","")

    if banko:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;background:#071a12;
border:1px solid #166534;border-radius:10px;padding:12px 14px;margin:6px 0">
  <div style="font-size:1.4rem">🎯</div>
  <div>
    <div style="font-size:.65rem;font-weight:700;letter-spacing:.1em;color:#86efac">TAHMİN</div>
    <div style="font-size:.9rem;font-weight:600;color:#00ff99;font-family:'JetBrains Mono',monospace">{banko[:100]}</div>
  </div>
</div>""", unsafe_allow_html=True)

    if riskli:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;background:#1a0c00;
border:1px solid #9a3412;border-radius:10px;padding:12px 14px;margin:6px 0">
  <div style="font-size:1.4rem">⚡</div>
  <div>
    <div style="font-size:.65rem;font-weight:700;letter-spacing:.1em;color:#fb923c">RİSKLİ</div>
    <div style="font-size:.9rem;font-weight:600;color:#fdba74;font-family:'JetBrains Mono',monospace">{riskli[:100]}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── 4. Maç Analizi metin kutusu ───────────────────────
    if match_analysis:
        st.markdown("""
<div style="font-size:.72rem;color:#4a6080;font-weight:600;
letter-spacing:.1em;text-transform:uppercase;margin:14px 0 6px">📋 MAÇ ANALİZİ</div>
""", unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#0d1525;border:1px solid #1a2e4a;border-radius:10px;'
            f'padding:14px;font-size:.82rem;color:#8899aa;line-height:1.9">'
            f'{match_analysis[:600]}</div>', unsafe_allow_html=True)

    # ── 5. Detaylı Tab ────────────────────────────────────
    with st.expander("📈 Detaylı İstatistikler & Dönüş Analizi"):
        t1, t2, t3 = st.tabs(["📊 Olasılıklar", "🔄 Dönüş", "📋 Tam Analiz"])

        with t1:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**MS 1/X/2**")
                fav = max(stats['p1'],stats['px'],stats['p2'])
                for lbl, val, name in [("1", stats['p1'], h), ("X", stats['px'], "Beraberlik"), ("2", stats['p2'], a)]:
                    color = "#00e5a0" if val==fav else "#3b82f6"
                    w = min(100, round(val))
                    st.markdown(f"""
<div class="prob-row">
  <div class="prob-label">{lbl} · {name[:12]}</div>
  <div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:{w}%;background:{color}"></div></div>
  <div class="prob-pct" style="color:{color}">%{val}</div>
</div>""", unsafe_allow_html=True)

                st.markdown("<br>**İY 1/X/2**", unsafe_allow_html=True)
                for lbl, val, name in [("1", stats['iy1'], h), ("X", stats['iyx'], "Beraberlik"), ("2", stats['iy2'], a)]:
                    w = min(100, round(val))
                    st.markdown(f"""
<div class="prob-row">
  <div class="prob-label">İY {lbl} · {name[:10]}</div>
  <div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:{w}%;background:#6d28d9"></div></div>
  <div class="prob-pct" style="color:#c4b5fd">%{val}</div>
</div>""", unsafe_allow_html=True)

            with c2:
                st.markdown("**Gol Tahminleri**")
                for lbl, val, color in [
                    ("KG VAR", stats['kg'], "#10b981"),
                    ("KG YOK", stats['kgy'], "#6b7280"),
                    ("2.5 Üst", stats['u25'], "#f59e0b"),
                    ("2.5 Alt", stats['alt25'], "#6b7280"),
                    ("3.5 Üst", stats['u35'], "#ef4444"),
                    ("4.5 Üst", stats['u45'], "#991b1b"),
                ]:
                    w = min(100, round(val))
                    st.markdown(f"""
<div class="prob-row">
  <div class="prob-label">{lbl}</div>
  <div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:{w}%;background:{color}"></div></div>
  <div class="prob-pct" style="color:{color}">%{val}</div>
</div>""", unsafe_allow_html=True)

            # İY/MS Kombolar
            st.markdown("<br>**İY/MS Kombinasyonları**", unsafe_allow_html=True)
            combo_html = '<div class="combo-grid">'
            for i, (k, v) in enumerate(stats['combos']):
                cls = "combo-cell c1" if i==0 else "combo-cell c2" if i==1 else "combo-cell c3" if i==2 else "combo-cell"
                combo_html += f'<div class="{cls}"><div class="ck">{k}</div><div class="cv">%{round(v,1)}</div></div>'
            combo_html += "</div>"
            st.markdown(combo_html, unsafe_allow_html=True)

        with t2:
            d1, d2 = st.columns(2)
            with d1:
                rv21m = stats['rev21']; rv21h = h2h.get('rev21_pct',0)
                hot = rv21m>10 or rv21h>20
                st.markdown(f"""
<div class="donus-card {'hot' if hot else ''}">
  <h4>2/1 Dönüş<br><small style="color:#4a6080">İY: {a} önde → MS: {h} kazanır</small></h4>
  <div class="dval">%{rv21m}</div>
  <div class="dsub">Model ihtimali</div>
  <div style="margin-top:8px">
    <div class="dsub">H2H geçmiş: <b style="color:#fbbf24">%{rv21h}</b> ({h2h.get('rev21',0)}/{h2h.get('n',0)} maç)</div>
    <div class="dsub">{h} 2Y gol yükü: %{hf.get('st_pct',55) if hf else 55}</div>
    <div class="dsub">{a} İY gol yükü: %{af.get('ht_pct',45) if af else 45}</div>
  </div>
</div>""", unsafe_allow_html=True)

            with d2:
                rv12m = stats['rev12']; rv12h = h2h.get('rev12_pct',0)
                hot2 = rv12m>10 or rv12h>20
                st.markdown(f"""
<div class="donus-card {'hot' if hot2 else ''}">
  <h4>1/2 Dönüş<br><small style="color:#4a6080">İY: {h} önde → MS: {a} kazanır</small></h4>
  <div class="dval">%{rv12m}</div>
  <div class="dsub">Model ihtimali</div>
  <div style="margin-top:8px">
    <div class="dsub">H2H geçmiş: <b style="color:#c4b5fd">%{rv12h}</b> ({h2h.get('rev12',0)}/{h2h.get('n',0)} maç)</div>
    <div class="dsub">{a} 2Y gol yükü: %{af.get('st_pct',55) if af else 55}</div>
    <div class="dsub">{h} İY gol yükü: %{hf.get('ht_pct',45) if hf else 45}</div>
  </div>
</div>""", unsafe_allow_html=True)

            # Dönüş analiz metni
            donus_text = ""
            for k, v in sections.items():
                if "DÖNÜŞ" in k or "DONUS" in k:
                    donus_text = v; break
            if donus_text:
                st.markdown(f'<div class="analysis-box" style="max-height:300px;margin-top:10px">{donus_text}</div>',
                            unsafe_allow_html=True)

        with t3:
            st.markdown(f'<div class="analysis-box">{analysis_text}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Analizi İndir",
                data=analysis_text, file_name=f"{h}_vs_{a}_{sel_date}.txt",
                mime="text/plain", key=f"dl_full_{h[:5]}")

    # Disclaimer
    st.markdown("""
<div class="disclaimer">⚠️ DISCLAIMER — İstatistikler bilgilendirme amaçlıdır. Kesinlik içermez.</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
for k in ["matches","mdata","analyses"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k=="matches" else {}

# ═══════════════════════════════════════════════════════════
# ANA KONTROLLER
# ═══════════════════════════════════════════════════════════
c1, c2, c3 = st.columns([3,2,2])
with c1: st.markdown(f"**{sel_label}** · {sel_date.strftime('%d.%m.%Y')}")
with c2: fetch_btn = st.button("🔍 Maçları Çek", type="primary", use_container_width=True)
with c3: all_btn   = st.button("🤖 Tümünü Analiz Et", use_container_width=True)
st.divider()

# ═══════════════════════════════════════════════════════════
# MAÇLARI ÇEK
# ═══════════════════════════════════════════════════════════
if fetch_btn:
    with st.spinner("📡 Maçlar çekiliyor..."):
        matches = api_matches(sel_code, sel_date.strftime("%Y-%m-%d"), max_match)
    if not matches:
        st.error(f"**{sel_date:%d.%m.%Y} · {sel_label}** için planlanmış maç yok. Farklı tarih dene."); st.stop()
    st.session_state.matches=matches; st.session_state.mdata={}; st.session_state.analyses={}
    st.success(f"✅ {len(matches)} maç bulundu!")
    with st.spinner("📊 Puan & Golcüler..."):
        standings=api_standings(sel_code); scorers=api_scorers(sel_code); time.sleep(0.5)
    bar=st.progress(0)
    for i,m in enumerate(matches):
        mid=m["id"]; hid=m["homeTeam"]["id"]; aid=m["awayTeam"]["id"]
        hn=m["homeTeam"]["name"]; an=m["awayTeam"]["name"]
        bar.progress(i/len(matches), text=f"({i+1}/{len(matches)}) {hn} – {an}")
        hf=parse_form(api_team_matches(hid,n_form),hid)
        af=parse_form(api_team_matches(aid,n_form),aid); time.sleep(0.4)
        h2h=parse_h2h(api_h2h(mid,n_h2h),hid); time.sleep(0.4)
        h_s=find_standing(standings,hid); a_s=find_standing(standings,aid)
        h_sc=find_scorer(scorers,hid);   a_sc=find_scorer(scorers,aid)
        hxg=calc_xg(hf,af,True); axg=calc_xg(af,hf,False)
        h_htxg=calc_ht_xg(hf,hxg); a_htxg=calc_ht_xg(af,axg)
        ms_mat=score_mat(hxg,axg); ht_mat=score_mat(h_htxg,a_htxg,mx=4)
        stats=compute_stats(ms_mat,ht_mat)
        top_ms=sorted(ms_mat.items(),key=lambda x:-x[1])[:12]
        top_ht=sorted(ht_mat.items(),key=lambda x:-x[1])[:6]
        prompt=build_prompt(hn,an,hf,af,h2h,hxg,axg,h_htxg,a_htxg,stats,h_s,a_s,h_sc,a_sc,top_ms,top_ht)
        st.session_state.mdata[mid]={
            "match":m,"prompt":prompt,"hf":hf,"af":af,"h2h":h2h,
            "hxg":hxg,"axg":axg,"h_htxg":h_htxg,"a_htxg":a_htxg,
            "stats":stats,"top_ms":top_ms,"top_ht":top_ht,
        }
    bar.progress(1.0); time.sleep(0.3); bar.empty()
    st.success("✅ Veriler hazır!")

# ═══════════════════════════════════════════════════════════
# TOPLU ANALİZ
# ═══════════════════════════════════════════════════════════
if all_btn:
    if not st.session_state.mdata: st.warning("Önce Maçları Çek!")
    else:
        items=list(st.session_state.mdata.items())
        bar2=st.progress(0)
        for i,(mid,d) in enumerate(items):
            hn=d["match"]["homeTeam"]["name"]; an=d["match"]["awayTeam"]["name"]
            bar2.progress(i/len(items),text=f"({i+1}/{len(items)}) {hn}–{an}")
            st.session_state.analyses[mid]=groq_call(d["prompt"]); time.sleep(0.5)
        bar2.progress(1.0); time.sleep(0.3); bar2.empty()
        st.success("✅ Tümü tamamlandı!")

# ═══════════════════════════════════════════════════════════
# MAÇ LİSTESİ
# ═══════════════════════════════════════════════════════════
if st.session_state.matches:
    st.markdown(f"### ⚽ {len(st.session_state.matches)} Maç · {sel_date.strftime('%d.%m.%Y')}")
    for m in st.session_state.matches:
        mid=m["id"]; hn=m["homeTeam"]["name"]; an=m["awayTeam"]["name"]
        utc=m.get("utcDate","")[:16].replace("T"," ")
        done=mid in st.session_state.analyses
        d=st.session_state.mdata.get(mid,{})
        icon="✅" if done else "🔴"

        with st.expander(f"{icon}  {hn}  vs  {an}  ·  {utc}"):
            if d:
                hf=d.get("hf",{}); af=d.get("af",{})
                h2=d.get("h2h",{}); stats=d.get("stats",{})
                hxg=d.get("hxg",0); axg=d.get("axg",0)
                # Hızlı özet chip'ler
                col_info = (
                    f'<span style="font-size:.75rem;color:#4a6080">'
                    f'xG: <b style="color:#00e5a0">{hxg}</b> – <b style="color:#00e5a0">{axg}</b> &nbsp;|&nbsp; '
                    f'{hn}: <b style="color:#e2e8f0">{hf.get("form_str","?") if hf else "?"}</b> &nbsp;|&nbsp; '
                    f'{an}: <b style="color:#e2e8f0">{af.get("form_str","?") if af else "?"}</b> &nbsp;|&nbsp; '
                    f'H2H: <b style="color:#e2e8f0">{h2.get("hw",0)}G-{h2.get("dr",0)}B-{h2.get("aw",0)}M</b>'
                    f'</span>'
                )
                st.markdown(col_info, unsafe_allow_html=True)

            # Analiz butonu
            if not done:
                if st.button("🤖 Analiz Et", key=f"btn_{mid}", type="primary"):
                    if not d.get("prompt"): st.warning("Önce Maçları Çek!")
                    else:
                        with st.spinner(f"🦙 Groq Llama: {hn} – {an}..."):
                            st.session_state.analyses[mid]=groq_call(d["prompt"])
                        st.rerun()
            else:
                if d:
                    render_analysis_ui(
                        hn, an,
                        d["stats"], d["top_ms"], d["top_ht"],
                        d["h2h"], d["hf"], d["af"],
                        d["hxg"], d["axg"],
                        st.session_state.analyses[mid]
                    )

# ═══════════════════════════════════════════════════════════
# BAŞLANGIÇ
# ═══════════════════════════════════════════════════════════
else:
    st.markdown("""
<div style="background:#0d1525;border:1px solid #1a2e4a;border-radius:12px;padding:1.4rem 1.6rem">
  <div style="font-size:.75rem;color:#4a6080;font-weight:600;letter-spacing:.1em;
  text-transform:uppercase;margin-bottom:10px">🚀 NASIL KULLANILIR?</div>
  <div style="font-size:.85rem;color:#8899aa;line-height:2">
  1. Sol sidebar'dan <b style="color:#e2e8f0">Kategori</b> ve <b style="color:#e2e8f0">Lig</b> seç<br>
  2. <b style="color:#e2e8f0">Tarih</b> seç<br>
  3. <b style="color:#00e5a0">🔍 Maçları Çek</b> butonuna bas<br>
  4. Maçı aç → <b style="color:#00e5a0">🤖 Analiz Et</b> veya <b style="color:#00e5a0">🤖 Tümünü Analiz Et</b><br>
  5. İY / 2H / MS senaryo kartları, 2/1 & 1/2 dönüş analizi, olasılık barları görünür
  </div>
  <div style="font-size:.72rem;color:#2a4060;margin-top:12px">
  ✅ API key'ler hazır · football-data.org + Groq Llama 3.3 70B · Tamamen ücretsiz
  </div>
</div>
""", unsafe_allow_html=True)
