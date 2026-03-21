import streamlit as st, requests, math, time
from datetime import date

st.set_page_config(page_title="⚽ Pro Betting Analyst", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
.hero{background:linear-gradient(135deg,#0a0e1a,#0f1e35);border:1px solid #1e3a5f;border-radius:14px;padding:1.8rem 2.5rem;margin-bottom:1.5rem;text-align:center}
.hero h1{color:#60a5fa;margin:0;font-size:1.9rem;font-weight:700}
.hero p{color:#6b7280;margin:.4rem 0 0;font-size:.88rem}
.guide{background:#0f1923;border:1px solid #1e3a5f;border-left:3px solid #3b82f6;border-radius:8px;padding:.9rem 1rem;font-size:.82rem;color:#9ca3af;line-height:2;margin-bottom:1rem}
.guide a{color:#60a5fa}.guide b{color:#e5e7eb}
.opill{display:inline-block;background:#1f2937;border:1px solid #374151;color:#d1d5db;padding:3px 10px;border-radius:20px;font-size:.78rem;margin:2px 3px 2px 0}
.abox{background:#060b14;border:1px solid #1e3a5f;border-radius:10px;padding:1.4rem 1.6rem;font-size:.84rem;color:#e5e7eb;line-height:2;white-space:pre-wrap;max-height:800px;overflow-y:auto;font-family:'Courier New',monospace}
.dbox{background:#111827;border:1px solid #374151;border-radius:6px;padding:.8rem 1rem;font-size:.76rem;color:#6b7280;font-family:'Courier New',monospace;max-height:280px;overflow-y:auto;white-space:pre-wrap}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>⚽ PRO BETTING ANALYST v4</h1><p>football-data.org + Groq Llama 3.3 70B · Tamamen Ücretsiz · İY Skor + MS Skor + 2/1 1/2 Dönüş Analizi</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🔑 API Anahtarları")
    st.markdown("""<div class="guide">
<b style="color:#60a5fa">1) Groq API — ÜCRETSİZ</b><br>
→ <a href="https://console.groq.com" target="_blank">console.groq.com</a> → Google giriş → API Keys → Create Key<br>
→ <b>gsk_</b> ile başlar · 500K token/gün · Kart YOK<br><br>
<b style="color:#60a5fa">2) football-data.org — ÜCRETSİZ</b><br>
→ <a href="https://www.football-data.org/client/register" target="_blank">football-data.org/client/register</a><br>
→ E-posta kayıt → Key mail'e gelir
</div>""", unsafe_allow_html=True)
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    fd_key   = st.text_input("football-data.org Key", type="password", placeholder="Mail'den key...")
    st.divider()
    LEAGUES = {"Premier League":"PL","La Liga":"PD","Bundesliga":"BL1","Serie A":"SA","Ligue 1":"FL1","Eredivisie":"DED","Primeira Liga":"PPL","Champions League":"CL"}
    sel_label = st.selectbox("Lig", list(LEAGUES.keys()))
    sel_code  = LEAGUES[sel_label]
    sel_date  = st.date_input("Tarih", value=date.today())
    max_match = st.slider("Maks Maç", 1,15,8)
    st.divider()
    use_h2h=st.checkbox("H2H",value=True); use_form=st.checkbox("Form",value=True)
    n_h2h=st.slider("H2H Sayısı",3,10,6); n_form=st.slider("Form Sayısı",3,10,8)
    debug=st.checkbox("Debug",value=False)

BASE="https://api.football-data.org/v4"
def fd(path,key,params=None):
    try:
        r=requests.get(f"{BASE}{path}",headers={"X-Auth-Token":key},params=params or {},timeout=15)
        if r.status_code==429:
            st.warning("Rate limit 65sn..."); time.sleep(66)
            r=requests.get(f"{BASE}{path}",headers={"X-Auth-Token":key},params=params or {},timeout=15)
        if debug: st.caption(f"🐛{path}→{r.status_code}")
        return r.json() if r.status_code==200 else {}
    except Exception as e: st.error(f"Bağlantı:{e}"); return {}

def get_matches(key,code,dt,lim):
    return fd(f"/competitions/{code}/matches",key,{"dateFrom":dt,"dateTo":dt,"status":"SCHEDULED,TIMED,POSTPONED"}).get("matches",[])[:lim]
def get_team_matches(key,tid,n): return fd(f"/teams/{tid}/matches",key,{"status":"FINISHED","limit":n}).get("matches",[])
def get_h2h(key,mid,n): return fd(f"/matches/{mid}/head2head",key,{"limit":n}).get("matches",[])
def get_standings(key,code):
    try: return fd(f"/competitions/{code}/standings",key)["standings"][0]["table"]
    except: return []
def get_scorers(key,code): return fd(f"/competitions/{code}/scorers",key,{"limit":15}).get("scorers",[])

def parse_form(matches,tid):
    if not matches: return {}
    res,gf,gc,htgf,htgc=[],[],[],[],[]
    hgf=hgc=hn_=agf=agc=an_=0
    for m in matches:
        hid=m["homeTeam"]["id"]
        mg=m["score"]["fullTime"]["home"] or 0; ag=m["score"]["fullTime"]["away"] or 0
        mht=(m["score"].get("halfTime") or {}).get("home") or 0
        aht=(m["score"].get("halfTime") or {}).get("away") or 0
        if hid==tid: f,c,fh,ch=mg,ag,mht,aht; hgf+=mg;hgc+=ag;hn_+=1
        else:        f,c,fh,ch=ag,mg,aht,mht; agf+=ag;agc+=mg;an_+=1
        res.append("G" if f>c else "B" if f==c else "M")
        gf.append(f);gc.append(c);htgf.append(fh);htgc.append(ch)
    n=len(res); pts=sum({"G":3,"B":1,"M":0}[r] for r in res[:5])
    tgf=sum(gf); thtgf=sum(htgf)
    htr=round(thtgf/tgf*100,1) if tgf>0 else 45.0
    htres=["G" if a>b else "B" if a==b else "M" for a,b in zip(htgf,htgc)]
    sr=res[0] if res else "?"; sn=0
    for r in res:
        if r==sr: sn+=1
        else: break
    lbl={"G":"galibiyet","B":"beraberlik","M":"mağlubiyet"}
    return {"n":n,"form_str":"-".join(res[:6]),"pts5":pts,"pts_pct":round(pts/15*100,1),
            "avg_gf":round(sum(gf)/n,2),"avg_gc":round(sum(gc)/n,2),
            "ht_form":"-".join(htres[:5]),"ht_avg_gf":round(sum(htgf)/n,2),"ht_avg_gc":round(sum(htgc)/n,2),
            "ht_ratio":htr,"st_ratio":round(100-htr,1),
            "h_avg_gf":round(hgf/hn_,2) if hn_ else 0,"h_avg_gc":round(hgc/hn_,2) if hn_ else 0,"h_n":hn_,
            "a_avg_gf":round(agf/an_,2) if an_ else 0,"a_avg_gc":round(agc/an_,2) if an_ else 0,"a_n":an_,
            "btts":sum(1 for f,c in zip(gf,gc) if f>0 and c>0),
            "over25":sum(1 for f,c in zip(gf,gc) if f+c>2),"over35":sum(1 for f,c in zip(gf,gc) if f+c>3),
            "clean_sheets":sum(1 for c in gc if c==0),"failed":sum(1 for f in gf if f==0),
            "streak":f"{sn} maç {lbl.get(sr,'?')} serisi",
            "last_scores":[f"{f}-{c}" for f,c in zip(gf[:6],gc[:6])],
            "ht_last":[f"{a}-{b}" for a,b in zip(htgf[:6],htgc[:6])]}

def parse_h2h(matches,hid):
    if not matches: return {}
    hw=aw=dr=ht_hw=ht_aw=ht_dr=rev21=rev12=btts=over25=0
    gl,sc,ht_sc=[],[],[]
    for m in matches:
        mid_hid=m["homeTeam"]["id"]
        hg=m["score"]["fullTime"]["home"] or 0; ag=m["score"]["fullTime"]["away"] or 0
        hht=(m["score"].get("halfTime") or {}).get("home") or 0
        aht=(m["score"].get("halfTime") or {}).get("away") or 0
        if mid_hid==hid: mg,og,mht,oht=hg,ag,hht,aht
        else:            mg,og,mht,oht=ag,hg,aht,hht
        if mg>og: hw+=1
        elif mg<og: aw+=1
        else: dr+=1
        if mht>oht: ht_hw+=1
        elif mht<oht: ht_aw+=1
        else: ht_dr+=1
        if mht<oht and mg>og: rev21+=1
        if mht>oht and mg<og: rev12+=1
        if mg>0 and og>0: btts+=1
        if mg+og>2: over25+=1
        gl.append(mg+og); sc.append(f"{mg}-{og}"); ht_sc.append(f"{mht}-{oht}")
    n=len(matches)
    return {"n":n,"hw":hw,"dr":dr,"aw":aw,
            "hw_pct":round(hw/n*100,1),"dr_pct":round(dr/n*100,1),"aw_pct":round(aw/n*100,1),
            "ht_hw":ht_hw,"ht_dr":ht_dr,"ht_aw":ht_aw,
            "avg_goals":round(sum(gl)/n,2),"over25":over25,"over25_pct":round(over25/n*100,1),
            "btts":btts,"btts_pct":round(btts/n*100,1),
            "rev21":rev21,"rev21_pct":round(rev21/n*100,1),
            "rev12":rev12,"rev12_pct":round(rev12/n*100,1),
            "scores":sc,"ht_scores":ht_sc}

def find_standing(table,tid):
    for r in table:
        if r.get("team",{}).get("id")==tid: return r
    return {}

def find_scorer(scorers,tid):
    for s in scorers:
        if s.get("team",{}).get("id")==tid:
            p=s.get("player",{}); return f"{p.get('name','?')} — {s.get('goals',0)} gol / {s.get('assists',0)} asist"
    return "Veri yok"

def poi(lam,k): lam=max(lam,0.01); return math.exp(-lam)*(lam**k)/math.factorial(k)
def calc_xg(tf,of,is_home):
    base=tf.get("avg_gf",1.2); loc=tf.get("h_avg_gf" if is_home else "a_avg_gf",base); opp=of.get("avg_gc",1.2)
    if loc==0: loc=base
    return max(0.3,round(base*0.30+loc*0.40+opp*0.30,3))
def smat(hx,ax,mx=6): return {(h,a):round(poi(hx,h)*poi(ax,a)*100,3) for h in range(mx+1) for a in range(mx+1)}

def build_pkg(match,hf,af,h2h,h_s,a_s,scorers):
    h=match["homeTeam"]["name"]; a=match["awayTeam"]["name"]
    hid=match["homeTeam"]["id"]; aid=match["awayTeam"]["id"]
    hxg=calc_xg(hf,af,True) if hf else 1.2; axg=calc_xg(af,hf,False) if af else 1.1
    h_htxg=max(0.2,round(hf.get("ht_avg_gf",hxg*0.43),3)) if hf else round(hxg*0.43,3)
    a_htxg=max(0.2,round(af.get("ht_avg_gf",axg*0.43),3)) if af else round(axg*0.43,3)
    ms=smat(hxg,axg); ht=smat(h_htxg,a_htxg,mx=4)
    tms=sorted(ms.items(),key=lambda x:-x[1]); tht=sorted(ht.items(),key=lambda x:-x[1])
    p1=round(sum(v for(hg,ag),v in ms.items() if hg>ag),1)
    px=round(sum(v for(hg,ag),v in ms.items() if hg==ag),1); p2=round(100-p1-px,1)
    iy1=round(sum(v for(hg,ag),v in ht.items() if hg>ag),1)
    iyx=round(sum(v for(hg,ag),v in ht.items() if hg==ag),1); iy2=round(100-iy1-iyx,1)
    combos={}
    for ir,ip in [("1",iy1),("X",iyx),("2",iy2)]:
        for mr,mp in [("1",p1),("X",px),("2",p2)]: combos[f"{ir}/{mr}"]=round(ip*mp/100,2)
    cs=sorted(combos.items(),key=lambda x:-x[1])
    ph0=poi(hxg,0); pa0=poi(axg,0); kgv=round((1-ph0)*(1-pa0)*100,1)
    u25=round(sum(v for(h_,a_),v in ms.items() if h_+a_>2),1)
    u35=round(sum(v for(h_,a_),v in ms.items() if h_+a_>3),1)
    u45=round(sum(v for(h_,a_),v in ms.items() if h_+a_>4),1)
    r21m=round(iy2*p1/100,2); r12m=round(iy1*p2/100,2)
    def ss(s):
        if not s: return "Veri yok"
        d=s.get("goalDifference",0)
        return f"Sıra:{s.get('position','?')} O:{s.get('playedGames','?')} G:{s.get('won','?')} B:{s.get('draw','?')} M:{s.get('lost','?')} Gol:{s.get('goalsFor','?')}-{s.get('goalsAgainst','?')} AV:{d:+d} P:{s.get('points','?')}"
    def fv(d,k,dv=0): return d.get(k,dv) if d else dv
    def fl(d,k): return " | ".join((d.get(k,[]) if d else [])[:6])
    pkg=(
        f"{'='*58}\nMAÇ: {h} vs {a}\nLİG: {match.get('competition',{}).get('name','?')}\nTARİH: {match.get('utcDate','')[:16].replace('T',' ')} UTC\n{'='*58}\n\n"
        f"PUAN DURUMU:\n  {h}: {ss(h_s)}\n  {a}: {ss(a_s)}\n\n"
        f"GOL KRALI:\n  {h}: {find_scorer(scorers,hid)}\n  {a}: {find_scorer(scorers,aid)}\n\n"
        f"{'─'*48}\n{h} FORM (son {fv(hf,'n')} maç):\n{'─'*48}\n"
        f"  MS Form   : {fv(hf,'form_str','?')} ({fv(hf,'pts5')}/15 puan)\n"
        f"  İY Form   : {fv(hf,'ht_form','?')}\n"
        f"  MS Skorlar: {fl(hf,'last_scores')}\n"
        f"  İY Skorlar: {fl(hf,'ht_last')}\n"
        f"  Genel Gol : {fv(hf,'avg_gf')} attı / {fv(hf,'avg_gc')} yedi\n"
        f"  İç Saha   : {fv(hf,'h_avg_gf')} attı / {fv(hf,'h_avg_gc')} yedi ({fv(hf,'h_n')} maç)\n"
        f"  Deplasman : {fv(hf,'a_avg_gf')} attı / {fv(hf,'a_avg_gc')} yedi ({fv(hf,'a_n')} maç)\n"
        f"  İY Gol Ort: {fv(hf,'ht_avg_gf')} attı / {fv(hf,'ht_avg_gc')} yedi\n"
        f"  GOL ZAMANI: %{fv(hf,'ht_ratio',45)} İY — %{fv(hf,'st_ratio',55)} 2Y  ← KRİTİK VERİ\n"
        f"  KG VAR: {fv(hf,'btts')}/{fv(hf,'n')} | 2.5Üst: {fv(hf,'over25')}/{fv(hf,'n')} | Kuru: {fv(hf,'clean_sheets')}/{fv(hf,'n')}\n"
        f"  Seri: {fv(hf,'streak','?')}\n\n"
        f"{'─'*48}\n{a} FORM (son {fv(af,'n')} maç):\n{'─'*48}\n"
        f"  MS Form   : {fv(af,'form_str','?')} ({fv(af,'pts5')}/15 puan)\n"
        f"  İY Form   : {fv(af,'ht_form','?')}\n"
        f"  MS Skorlar: {fl(af,'last_scores')}\n"
        f"  İY Skorlar: {fl(af,'ht_last')}\n"
        f"  Genel Gol : {fv(af,'avg_gf')} attı / {fv(af,'avg_gc')} yedi\n"
        f"  İç Saha   : {fv(af,'h_avg_gf')} attı / {fv(af,'h_avg_gc')} yedi ({fv(af,'h_n')} maç)\n"
        f"  Deplasman : {fv(af,'a_avg_gf')} attı / {fv(af,'a_avg_gc')} yedi ({fv(af,'a_n')} maç)\n"
        f"  İY Gol Ort: {fv(af,'ht_avg_gf')} attı / {fv(af,'ht_avg_gc')} yedi\n"
        f"  GOL ZAMANI: %{fv(af,'ht_ratio',45)} İY — %{fv(af,'st_ratio',55)} 2Y  ← KRİTİK VERİ\n"
        f"  KG VAR: {fv(af,'btts')}/{fv(af,'n')} | 2.5Üst: {fv(af,'over25')}/{fv(af,'n')} | Kuru: {fv(af,'clean_sheets')}/{fv(af,'n')}\n"
        f"  Seri: {fv(af,'streak','?')}\n\n"
        f"{'─'*48}\nH2H (son {h2h.get('n',0)} maç):\n{'─'*48}\n"
        f"  MS : {h} {h2h.get('hw',0)}G-{h2h.get('dr',0)}B-{h2h.get('aw',0)}M (%{h2h.get('hw_pct',0)}/%{h2h.get('dr_pct',0)}/%{h2h.get('aw_pct',0)})\n"
        f"  İY : {h} {h2h.get('ht_hw',0)}G-{h2h.get('ht_dr',0)}B-{h2h.get('ht_aw',0)}M\n"
        f"  MS Skorlar: {' | '.join(h2h.get('scores',[])[:6])}\n"
        f"  İY Skorlar: {' | '.join(h2h.get('ht_scores',[])[:6])}\n"
        f"  Ort Gol:{h2h.get('avg_goals','?')} | 2.5Üst:{h2h.get('over25',0)}/{h2h.get('n',0)}(%{h2h.get('over25_pct',0)}) | KGVAR:{h2h.get('btts',0)}/{h2h.get('n',0)}(%{h2h.get('btts_pct',0)})\n"
        f"  2/1 DÖNÜŞ: {h2h.get('rev21',0)}/{h2h.get('n',0)} maç (%{h2h.get('rev21_pct',0)}) — İY {a} önde → MS {h} kazandı\n"
        f"  1/2 DÖNÜŞ: {h2h.get('rev12',0)}/{h2h.get('n',0)} maç (%{h2h.get('rev12_pct',0)}) — İY {h} önde → MS {a} kazandı\n\n"
        f"{'─'*48}\nPOİSSON xG:\n{'─'*48}\n"
        f"  {h} xG={hxg} İY-xG={h_htxg} | {a} xG={axg} İY-xG={a_htxg}\n"
        f"  MS: 1=%{p1} X=%{px} 2=%{p2}\n"
        f"  İY: 1=%{iy1} X=%{iyx} 2=%{iy2}\n\n"
        f"  Top 10 MS Skor:\n" + "\n".join(f"    {hg}-{ag}→%{round(v,2)}" for(hg,ag),v in tms[:10])
        +f"\n  Top 6 İY Skor:\n" + "\n".join(f"    {hg}-{ag}→%{round(v,2)}" for(hg,ag),v in tht[:6])
        +f"\n  İY/MS 9 Kombo:\n" + "\n".join(f"    {k}→%{round(v,2)}" for k,v in cs)
        +f"\n  KG VAR=%{kgv} KG YOK=%{round(100-kgv,1)}\n"
        f"  2.5Üst=%{u25} 2.5Alt=%{round(100-u25,1)} 3.5Üst=%{u35} 4.5Üst=%{u45}\n"
        f"  Model 2/1=%{r21m} H2H 2/1=%{h2h.get('rev21_pct',0)}\n"
        f"  Model 1/2=%{r12m} H2H 1/2=%{h2h.get('rev12_pct',0)}\n"
        +f"{'='*58}"
    )
    return pkg,hxg,axg,h_htxg,a_htxg

SYSTEM="""Sen dünyanın en iyi profesyonel futbol bahis analistlerinden birisin.
Verilen maç veri paketini analiz et. Türkçe yaz. Her karar için NEDEN sorusunu cevapla.
ÖNEMLİ: İY skoru ve MS skorunu AYRI tahmin et. Gol zamanlama (%İY vs %2Y) verisini kullan.
2/1 ve 1/2 dönüşü: Model ihtimali + H2H geçmişi + Gol zamanlama verisiyle birlikte analiz et.

## 1) EN OLASI MS + İY SKOR
MS: X-Y (%...) — Gerekçe: xG, form, H2H, puan
İY: X-Y (%...) — Gerekçe: İY xG, İY form, İY H2H
İlk 45 dakikada kim üstün ve neden?

## 2) ALTERNATİF SKORLAR
MS için 8+ skor (X-Y %... — kısa gerekçe)
İY için 4+ skor (X-Y %... — kısa gerekçe)

## 3) İY / MS DETAYLI
İY 1/X/2: yüzde + gerekçe
MS 1/X/2: yüzde + gerekçe
En önemli 3 İY/MS kombosu için senaryo yaz
Tüm 9 komboyu listele

## 4) GOL SAYISI
KG VAR/YOK: % + son form trendi
1.5/2.5/3.5/4.5 Üst-Alt: % + gerekçe
İY gol beklentisi vs 2Y farkı

## 5) 2/1 – 1/2 DÖNÜŞ — ÇOK DETAYLI
2/1: Model:% | H2H:% (%...maçta oldu) | Gol zamanı destekliyor mu? | Senaryo | SONUÇ
1/2: Model:% | H2H:% (%...maçta oldu) | Gol zamanı destekliyor mu? | Senaryo | SONUÇ
KESİN YORUM: Hangi dönüş daha mümkün?

## 6) FORM & GÜÇ
Seri yorumu, iç saha/deplasman farkı, golcü gücü, motivasyon

## 7) DEĞER (VALUE)
Model vs beklenen piyasa oranları, en değerli bahis tipi

## 8) RİSK SEVİYESİ
Düşük/Orta/Yüksek — gerekçe

## 9) TAVSİYELER
🔒 BANKO: [tahmin] — [gerekçe]
⚡ ORTA: [tahmin] — [gerekçe]
💎 SÜRPRİZ: [tahmin + yüksek oran] — [gerekçe]
🎯 SKOR: İY [X-Y] + MS [X-Y] — [gerekçe]"""

def groq_analyze(pkg,key):
    try:
        r=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":SYSTEM},{"role":"user","content":pkg}],"temperature":0.25,"max_tokens":4000},
            timeout=120)
        r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]
    except Exception as e: return f"❌ Groq Hatası: {e}"

for k in ["matches","mdata","analyses"]:
    if k not in st.session_state: st.session_state[k]=[] if k=="matches" else {}

c1,c2,c3=st.columns([3,2,2])
with c1: st.markdown(f"**{sel_label}** · {sel_date:%d.%m.%Y}")
with c2: fetch_btn=st.button("🔍 Maçları Çek",type="primary",use_container_width=True)
with c3: all_btn=st.button("🤖 Tümünü Analiz Et",use_container_width=True)
st.divider()

if fetch_btn:
    if not fd_key: st.error("⛔ football-data.org key giriniz."); st.stop()
    with st.spinner("📡 Maçlar..."):
        matches=get_matches(fd_key,sel_code,sel_date.strftime("%Y-%m-%d"),max_match)
    if not matches: st.error(f"{sel_date:%d.%m.%Y} · {sel_label} için maç bulunamadı."); st.stop()
    st.session_state.matches=matches; st.session_state.mdata={}; st.session_state.analyses={}
    st.success(f"✅ {len(matches)} maç!")
    with st.spinner("📊 Puan & Golcüler..."):
        standings=get_standings(fd_key,sel_code); scorers=get_scorers(fd_key,sel_code); time.sleep(0.5)
    bar=st.progress(0)
    for i,m in enumerate(matches):
        mid=m["id"]; hid=m["homeTeam"]["id"]; aid=m["awayTeam"]["id"]
        hn=m["homeTeam"]["name"]; an=m["awayTeam"]["name"]
        bar.progress(i/len(matches),text=f"({i+1}/{len(matches)}) {hn} – {an}")
        hf_r=get_team_matches(fd_key,hid,n_form) if use_form else []
        af_r=get_team_matches(fd_key,aid,n_form) if use_form else []
        hf=parse_form(hf_r,hid); af=parse_form(af_r,aid); time.sleep(0.4)
        h2h_r=get_h2h(fd_key,mid,n_h2h) if use_h2h else []
        h2h=parse_h2h(h2h_r,hid); time.sleep(0.4)
        h_s=find_standing(standings,hid); a_s=find_standing(standings,aid)
        pkg,hxg,axg,h_htxg,a_htxg=build_pkg(m,hf,af,h2h,h_s,a_s,scorers)
        st.session_state.mdata[mid]={"match":m,"pkg":pkg,"hf":hf,"af":af,"h2h":h2h,"hxg":hxg,"axg":axg,"h_htxg":h_htxg,"a_htxg":a_htxg}
    bar.progress(1.0); time.sleep(0.4); bar.empty(); st.success("✅ Veriler hazır!")

if all_btn:
    if not st.session_state.mdata: st.warning("Önce Maçları Çek!")
    elif not groq_key: st.error("⛔ Groq API Key!")
    else:
        bar2=st.progress(0); items=list(st.session_state.mdata.items())
        for i,(mid,d) in enumerate(items):
            hn=d["match"]["homeTeam"]["name"]; an=d["match"]["awayTeam"]["name"]
            bar2.progress(i/len(items),text=f"({i+1}/{len(items)}) {hn}–{an}")
            st.session_state.analyses[mid]=groq_analyze(d["pkg"],groq_key); time.sleep(0.5)
        bar2.progress(1.0); time.sleep(0.3); bar2.empty(); st.success("✅ Tamamlandı!")

if st.session_state.matches:
    st.markdown(f"## 📋 Maçlar ({len(st.session_state.matches)})")
    for m in st.session_state.matches:
        mid=m["id"]; hn=m["homeTeam"]["name"]; an=m["awayTeam"]["name"]
        comp=m.get("competition",{}).get("name",""); utc=m.get("utcDate","")[:16].replace("T"," ")
        done=mid in st.session_state.analyses; d=st.session_state.mdata.get(mid,{})
        with st.expander(f"{'✅' if done else '⚽'}  {hn}  –  {an}  |  {comp}  |  {utc}"):
            if d.get("hxg"):
                h2=d.get("h2h",{})
                st.markdown(f"<span class='opill'>🏠{hn} xG:{d['hxg']} İY:{d.get('h_htxg','?')}</span>"
                            f"<span class='opill'>✈️{an} xG:{d['axg']} İY:{d.get('a_htxg','?')}</span>"
                            f"<span class='opill'>H2H {h2.get('hw',0)}G-{h2.get('dr',0)}B-{h2.get('aw',0)}M</span>"
                            f"<span class='opill'>2/1:%{h2.get('rev21_pct',0)} 1/2:%{h2.get('rev12_pct',0)}</span>",unsafe_allow_html=True)
            if d.get("pkg"):
                with st.expander("📊 Ham Veri"):
                    st.markdown(f"<div class='dbox'>{d['pkg']}</div>",unsafe_allow_html=True)
            ca,cb=st.columns([3,1])
            with cb:
                if st.button("🤖 Analiz Et",key=f"a_{mid}"):
                    if not groq_key: st.error("⛔ Groq Key!")
                    elif not d.get("pkg"): st.warning("Önce Maçları Çek!")
                    else:
                        with st.spinner(f"Groq: {hn}–{an}..."):
                            st.session_state.analyses[mid]=groq_analyze(d["pkg"],groq_key)
            if mid in st.session_state.analyses:
                st.markdown("---")
                st.markdown(f"<div class='abox'>{st.session_state.analyses[mid]}</div>",unsafe_allow_html=True)
                st.download_button("⬇️ İndir",data=st.session_state.analyses[mid],file_name=f"{hn}_vs_{an}_{sel_date}.txt",mime="text/plain",key=f"dl_{mid}")
else:
    st.markdown("""<div class="guide" style="font-size:.88rem;line-height:2.1">
<b style="color:#60a5fa;font-size:1rem">⚽ Tamamen Ücretsiz — İki Key</b><br><br>
<b>1) Groq API</b> → <a href="https://console.groq.com" target="_blank">console.groq.com</a> → Google giriş → API Keys → Create → gsk_... ile başlar · 500K token/gün<br>
<b>2) football-data.org</b> → <a href="https://www.football-data.org/client/register" target="_blank">football-data.org/client/register</a> → E-posta → Key mail'e gelir<br><br>
<b>Analiz:</b> İY skor + MS skor ayrı · Gol zamanı (%İY vs %2Y) · H2H İY&MS skorları · 2/1&1/2 dönüş üçlü analiz · 9 İY/MS kombo · Poisson xG · Golcüler
</div>""",unsafe_allow_html=True)
