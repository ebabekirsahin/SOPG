import streamlit as st
import requests
import math
import time
def _safe_minute(val, default=45):
    """Parse a match minute safely — handles ?, empty, None, 45+2, etc."""
    try:
        s = str(val).replace("'","").strip()
        # "45+2" → 47, "90+4" → 94
        if "+" in s:
            parts = s.split("+")
            return int(parts[0]) + int(parts[1])
        s = s.split()[0]
        return int(s) if s and s[0].isdigit() else default
    except:
        return default

def calc_live_minute(m):
    """
    football-data.org maç nesnesinden gerçek oyun dakikasını hesapla.
    utcDate UTC'dir. Devre arası ~15dk. Stopaj hesaba katılmaz.
    """
    import datetime as _dt

    status = m.get("status", "")
    if status == "PAUSED":
        return 45

    utc_str = m.get("utcDate", "")
    if not utc_str:
        return 45

    try:
        clean = utc_str.rstrip("Z").replace("T", " ")[:19]
        start = _dt.datetime.strptime(clean, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return 45

    now     = _dt.datetime.utcnow()
    elapsed = max(0, int((now - start).total_seconds() / 60))

    if elapsed <= 45:
        return max(1, elapsed)          # 1Y: 1–45
    elif elapsed <= 50 and status == "IN_PLAY":
        return elapsed                  # 1Y uzatma (45+1..45+5) — hâlâ oynanıyor, 45'te donmasın
    elif elapsed <= 65 and status in ("PAUSED", "HT"):
        return 45                       # Devre arası
    elif elapsed <= 65 and status == "IN_PLAY":
        # Feed statusu gecikmeli güncellese bile dakika 45'te kilitlenmesin.
        return max(46, min(50, elapsed - 15))
    else:
        minute = elapsed - 15           # 2Y: devre arası 15dk
        return max(46, min(90, minute))


from datetime import date

st.set_page_config(page_title="⚽ BetAnalyst Pro", page_icon="⚽",
                   layout="wide", initial_sidebar_state="expanded")

import os

def _get_secret(name, env_fallback=None, aliases=()):
    """Streamlit Secrets + environment için dayanıklı, alias destekli okuyucu."""
    names=[]
    for n in (name, env_fallback, *aliases):
        if n and n not in names:
            names.append(n)

    try:
        sec=st.secrets
        for n in names:
            if n in sec and sec[n]:
                return str(sec[n]).strip().strip('"').strip("'")
        for section_name in ("api","keys","secrets","credentials"):
            try:
                section=sec.get(section_name,{})
                if hasattr(section,"get"):
                    for n in names:
                        val=section.get(n) or section.get(n.lower())
                        if val:
                            return str(val).strip().strip('"').strip("'")
            except Exception:
                pass
    except Exception:
        pass

    for n in names:
        val=os.environ.get(n) or os.environ.get(n.upper()) or os.environ.get(n.lower())
        if val:
            return str(val).strip().strip('"').strip("'")
    return None

FD_KEY=_get_secret("FD_KEY","FOOTBALL_DATA_KEY",
                    aliases=("FOOTBALLDATA_KEY","FOOTBALL_DATA_ORG_KEY"))
AF_KEY_DEFAULT=_get_secret("AF_KEY","API_FOOTBALL_KEY",
                           aliases=("AF_API_KEY","APIFOOTBALL_KEY","API_FOOTBALL_TOKEN"))
GROQ_KEY=_get_secret("GROQ_KEY","GROQ_API_KEY",aliases=("GROQ_TOKEN",))
ODDS_API_KEY_DEFAULT=_get_secret("ODDS_API_KEY","THE_ODDS_API_KEY",
                                  aliases=("ODDSAPI_KEY","THE_ODDS_API_TOKEN"))

# AF_KEY tek başına uygulamanın açılması için zorunlu değildir.
# AF yoksa mevcut football-data.org fallback'i çalışmaya devam eder.
# Gerçek API anahtarları hiçbir şekilde kaynak koda gömülmez.
_REQUIRED_MISSING=[]
if not AF_KEY_DEFAULT and not FD_KEY:
    _REQUIRED_MISSING.append("FD_KEY veya AF_KEY")

