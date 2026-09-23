import html
import json
import re
import urllib.parse
import pandas as pd
import requests
import streamlit as st

from src.data_loader import Dataset
from src.pipeline import ProductTruthPipeline

# -------------------------------------------------------------------
# Product Truth Agent — 3D visual interface
# The existing pipeline, dataset, retrieval and real Luna integration
# remain intact. This file only changes the presentation layer.
# -------------------------------------------------------------------

st.set_page_config(
    page_title="Product Truth Agent",
    page_icon="PT",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------- CSS ---------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root{
  --ink:#151713;
  --muted:#77786f;
  --cream:#f4f1e9;
  --paper:#fbfaf6;
  --line:#d8d4ca;
  --green:#53694d;
  --green2:#78906d;
  --dark:#1c201d;
  --good:#2e7d4f;
  --warn:#b67b22;
}

html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp{
  background:
    radial-gradient(circle at 75% 15%, rgba(120,144,109,.14), transparent 27%),
    radial-gradient(circle at 15% 35%, rgba(209,201,181,.28), transparent 30%),
    linear-gradient(135deg,#f7f4ed 0%,#ece9df 52%,#f7f5ef 100%);
  color:var(--ink);
}
.block-container{max-width:1500px;padding:1.1rem 2.6rem 3rem;}
header[data-testid="stHeader"]{background:transparent;}
footer{visibility:hidden;}

.pt-nav{
  display:flex;align-items:center;justify-content:space-between;
  padding:.25rem 0 1.1rem;border-bottom:1px solid rgba(50,50,40,.14);
}
.pt-brand{display:flex;align-items:center;gap:13px;}
.pt-mark{
  width:43px;height:43px;border:1.5px solid var(--ink);border-radius:50%;
  display:grid;place-items:center;font-family:'Playfair Display',serif;font-size:20px;
  background:rgba(255,255,255,.42);
}
.pt-brandname{font-size:15px;letter-spacing:.23em;font-weight:600;line-height:1.05;}
.pt-brandsub{font-size:9px;letter-spacing:.34em;color:var(--muted);margin-top:4px;}
.pt-links{display:flex;gap:29px;font-size:13px;color:#5d5e58;align-items:center;}
.pt-links .active{color:var(--ink);font-weight:600;}
.pt-search{
  border:1px solid rgba(40,40,30,.16);border-radius:999px;background:rgba(255,255,255,.56);
  padding:10px 16px;min-width:240px;color:#7c7c74;font-size:12px;
}
.pt-pill{
  background:var(--dark);color:white;border-radius:999px;padding:11px 17px;font-size:12px;
  letter-spacing:.02em;
}

.hero{
  display:grid;grid-template-columns:1.02fr 1.5fr;gap:20px;align-items:center;
  padding:5.2rem 0 3.6rem;min-height:590px;
}
.eyebrow{font-family:'DM Mono',monospace;letter-spacing:.28em;font-size:11px;color:#696b61;text-transform:uppercase;}
.hero h1{
  font-family:'Playfair Display',serif;font-size:clamp(54px,6vw,92px);line-height:.9;
  letter-spacing:-.055em;margin:19px 0 24px;color:#161713;
}
.hero-copy{font-size:18px;line-height:1.58;color:#505149;max-width:560px;}
.hero-note{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.1em;color:#8a8b82;margin-top:28px;}

.scene{
  min-height:510px;position:relative;display:flex;align-items:center;justify-content:center;
  perspective:1100px;overflow:visible;
}
.scene-floor{
  position:absolute;width:74%;height:90px;bottom:30px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(42,48,39,.24),transparent 70%);
  filter:blur(10px);
}
.bottle-wrap{position:relative;z-index:4;transform:rotateY(-10deg) rotateX(2deg);transition:transform .5s ease;}
.scene:hover .bottle-wrap{transform:rotateY(8deg) rotateX(-2deg) translateY(-7px);}
.bottle{
  width:176px;height:330px;border-radius:31px 31px 43px 43px;
  background:linear-gradient(90deg,#bcb9ab 0%,#f1eee4 16%,#e9e5d9 58%,#aaa99b 100%);
  box-shadow:22px 30px 45px rgba(44,48,39,.28),inset -10px 0 18px rgba(50,50,40,.13),inset 8px 0 16px rgba(255,255,255,.7);
  position:relative;border:1px solid rgba(60,60,50,.18);
}
.bottle:before{
  content:"";position:absolute;width:83px;height:75px;left:46px;top:-55px;border-radius:16px 16px 8px 8px;
  background:linear-gradient(90deg,#293228,#596b55 45%,#202820);
  box-shadow:inset -7px 0 10px rgba(0,0,0,.25);
}
.bottle:after{
  content:"";position:absolute;left:15px;right:15px;top:80px;height:205px;border-radius:14px;
  background:rgba(250,249,242,.62);border:1px solid rgba(70,70,55,.1);
}
.bottle-label{
  position:absolute;z-index:2;top:118px;left:31px;width:114px;text-align:center;
  font-family:'Playfair Display',serif;color:#30372e;
}
.bottle-label .brand{font-size:17px;letter-spacing:.08em;}
.bottle-label .product{font-size:11px;letter-spacing:.08em;margin-top:13px;}
.bottle-label .rule{height:1px;background:#899082;margin:16px 12px 12px;}
.bottle-label .small{font:9px 'DM Mono',monospace;letter-spacing:.1em;line-height:1.55;}

.float-card{
  position:absolute;z-index:5;background:rgba(252,251,247,.82);backdrop-filter:blur(12px);
  border:1px solid rgba(255,255,255,.9);box-shadow:0 18px 42px rgba(56,58,48,.14);
  border-radius:17px;padding:16px 17px;color:#2a2c27;
  transform-style:preserve-3d;
}
.float-card .kicker{font:9px 'DM Mono',monospace;letter-spacing:.12em;color:#7a7b72;text-transform:uppercase;}
.float-card strong{display:block;margin-top:7px;font-size:13px;}
.float-card p{font-size:10px;color:#77786f;margin:6px 0 0;line-height:1.45;}
.card-a{left:5%;top:13%;width:190px;transform:rotate(-3deg) translateZ(35px);}
.card-b{right:4%;top:9%;width:205px;transform:rotate(3deg) translateZ(25px);}
.card-c{left:7%;bottom:13%;width:205px;transform:rotate(2deg) translateZ(18px);}
.card-d{right:7%;bottom:14%;width:215px;transform:rotate(-2deg) translateZ(28px);}
.connector{position:absolute;z-index:2;height:1px;background:rgba(76,91,71,.38);transform-origin:left center;}
.conn1{width:130px;left:26%;top:29%;transform:rotate(8deg);}
.conn2{width:125px;right:25%;top:28%;transform:rotate(-10deg);}
.conn3{width:150px;left:27%;bottom:31%;transform:rotate(-8deg);}
.conn4{width:145px;right:26%;bottom:31%;transform:rotate(9deg);}

.cta-row{display:flex;gap:13px;align-items:center;margin-top:30px;}
.stButton>button{
  border-radius:999px !important;border:1px solid #1d211d !important;
  min-height:43px !important;padding:0 21px !important;font-size:12px !important;
  background:#1c201d !important;color:#fff !important;
}
.secondary-button .stButton>button{background:rgba(255,255,255,.5) !important;color:#1c201d !important;border-color:#bbb8ae !important;}

.feature-row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:10px 0 42px;}
.feature{
  padding:24px 22px;border-top:1px solid #c9c5bb;border-bottom:1px solid #c9c5bb;
}
.feature .num{font:11px 'DM Mono',monospace;color:#6d6e66;letter-spacing:.13em;}
.feature h3{font:18px 'Playfair Display',serif;margin:10px 0 5px;}
.feature p{font-size:12px;line-height:1.55;color:#77786f;margin:0;}

.trust{
  display:flex;justify-content:space-between;gap:14px;align-items:center;padding:18px 0;
  border-top:1px solid #ccc8be;color:#77786f;font-size:11px;letter-spacing:.12em;
}
.trust span{font-weight:600;color:#3d403a;letter-spacing:.04em;}

.section-head{display:flex;justify-content:space-between;align-items:end;margin:25px 0 18px;}
.section-head h2{font:34px 'Playfair Display',serif;margin:0;letter-spacing:-.03em;}
.section-head p{color:#77786f;font-size:12px;margin:0;}

.analyze-shell{
  background:rgba(250,249,245,.67);border:1px solid rgba(255,255,255,.82);
  box-shadow:0 20px 60px rgba(63,64,54,.10);border-radius:24px;padding:24px;
}
.mode-label{font:10px 'DM Mono',monospace;letter-spacing:.18em;color:#77786f;text-transform:uppercase;}
.result-hero{
  display:grid;grid-template-columns:1fr 1.8fr;gap:18px;margin-top:18px;
}
.result-card{
  background:rgba(255,255,255,.67);border:1px solid #e0ddd3;border-radius:18px;padding:21px;
}
.result-card h3{font:22px 'Playfair Display',serif;margin:8px 0;}
.metric{
  font-size:10px;color:#77786f;text-transform:uppercase;letter-spacing:.1em;
}
.metric-value{font-size:26px;font-weight:600;margin-top:5px;}
.status{
  display:inline-flex;align-items:center;gap:7px;border-radius:999px;padding:7px 11px;
  background:#e8f2e8;color:#2d7044;font-size:11px;font-weight:600;
}
.status.warn{background:#f7eddc;color:#9a691f;}
.data-card{
  background:rgba(255,255,255,.62);border:1px solid #e0ddd3;border-radius:18px;padding:20px;margin-top:16px;
}
.smallcaps{font:10px 'DM Mono',monospace;letter-spacing:.14em;color:#77786f;text-transform:uppercase;}
div[data-testid="stDataFrame"]{border-radius:13px;overflow:hidden;}
@media(max-width:1050px){
  .hero{grid-template-columns:1fr;padding-top:3rem;}
  .scene{min-height:460px;}
  .feature-row{grid-template-columns:1fr;}
  .pt-links{display:none;}
  .result-hero{grid-template-columns:1fr;}
}
@media(max-width:650px){
  .block-container{padding:1rem;}
  .hero h1{font-size:54px;}
  .hero-copy{font-size:16px;}
  .float-card{transform:scale(.82);}
  .card-a{left:-2%}.card-b{right:-4%}.card-c{left:-4%}.card-d{right:-3%}
  .bottle{transform:scale(.88);}
}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------- data ---------------------------------
@st.cache_resource
def get_dataset():
    return Dataset()

D = get_dataset()

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ----------------------------- header -------------------------------
st.markdown(
    """
<div class="pt-nav">
  <div class="pt-brand">
    <div class="pt-mark">PT</div>
    <div>
      <div class="pt-brandname">PRODUCT TRUTH</div>
      <div class="pt-brandsub">AGENT</div>
    </div>
  </div>
  <div class="pt-links">
    <span class="active">Home</span><span>Analyze</span><span>Reports</span><span>Resources</span><span>About</span>
  </div>
  <div style="display:flex;align-items:center;gap:9px;">
    <div class="pt-search">⌕ &nbsp; Search products, claims...</div>
    <div class="pt-pill">R</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------- home ---------------------------------
if st.session_state.page == "Home":
    st.markdown(
        f"""
<div class="hero">
  <div>
    <div class="eyebrow">Same product. Many claims. We find the truth.</div>
    <h1>Product<br>Truth Agent</h1>
    <div class="hero-copy">
      AI-powered product matching, characteristic coding and
      evidence-backed verification across official brand & retail sources.
    </div>
    <div class="cta-row">
      <div id="hero-cta"></div>
    </div>
    <div class="hero-note">REAL DATASET · OFFICIAL SITE PRIORITIZATION · REAL GPT-5.6 LUNA</div>
  </div>
  <div class="scene">
    <div class="scene-floor"></div>
    <div class="float-card card-a"><div class="kicker">Official Listing</div><strong>Brand & Manufacturer</strong><p>Prioritizing direct manufacturer sites and verified retail catalogues.</p></div>
    <div class="float-card card-b"><div class="kicker">Ingredient / taxonomy</div><strong>Structured evidence</strong><p>Module characteristics and permitted values.</p></div>
    <div class="float-card card-c"><div class="kicker">Evidence</div><strong>Verified web sources</strong><p>Candidate pages are filtered for official domain authority.</p></div>
    <div class="float-card card-d"><div class="kicker">Analysis result</div><strong>Verified / needs evidence</strong><p>Validation is applied with rigorous source reasoning.</p></div>
    <div class="connector conn1"></div><div class="connector conn2"></div><div class="connector conn3"></div><div class="connector conn4"></div>
    <div class="bottle-wrap">
      <div class="bottle">
        <div class="bottle-label">
          <div class="brand">PRODUCT</div>
          <div class="product">TRUTH AGENT</div>
          <div class="rule"></div>
          <div class="small">MATCH<br>EVIDENCE<br>VALIDATE</div>
        </div>
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 1], gap="medium")
    with c1:
        if st.button("Get Started  →", key="home_start"):
            st.session_state.page = "Analyze"
            st.rerun()
    with c2:
        st.markdown('<div style="padding:11px 0;color:#65665f;font-size:12px;">◉ Watch how the evidence flows</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div style="padding:11px 0;color:#65665f;font-size:12px;">Live taxonomy validation</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="feature-row">
  <div class="feature"><div class="num">01 · TARGET</div><h3>Prioritizes Official Sites</h3><p>Constructs precise queries targeting brand domains (.com, .in, official portals) and authorized retailers.</p></div>
  <div class="feature"><div class="num">02 · EXTRACT</div><h3>Extracts & verifies evidence</h3><p>Filters out low-grade aggregators and ranks URLs by brand and domain authority.</p></div>
  <div class="feature"><div class="num">03 · VALIDATE</div><h3>Rigorous Reasoning</h3><p>Provides fully traceable reasoning tied directly to the verified source URL.</p></div>
</div>
<div class="trust">
  <div><span>{len(D.modules)}</span> taxonomy modules</div>
  <div><span>{len(D.qa):,}</span> QA rows</div>
  <div><span>{len(D.dev):,}</span> development rows</div>
  <div><span>REAL LUNA</span> model integration</div>
  <div><span>OFFICIAL WEB</span> retrieval priority</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-head"><div><h2>Built for evidence, not guesses.</h2><p>The visual layer sits on top of the enhanced pipeline.</p></div></div>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="analyze-shell">
  <div class="smallcaps">Pipeline</div>
  <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:14px;">
    <span class="status">1 · Dataset</span><span class="status">2 · Official Domain Search</span>
    <span class="status">3 · Product match</span><span class="status">4 · Module</span>
    <span class="status">5 · Luna characteristics</span><span class="status">6 · Validated Reasoning</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

# ----------------------------- analyze -------------------------------
else:
    st.markdown(
        """
<div class="section-head">
  <div><h2>Analyze a product</h2><p>Run the enhanced Product Truth pipeline with official site prioritization.</p></div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("← Back to Home", key="back_home"):
        st.session_state.page = "Home"
        st.rerun()

    st.markdown('<div class="analyze-shell">', unsafe_allow_html=True)

    mode = st.radio(
        "MODE",
        ["QA product", "Development product", "Custom product"],
        horizontal=True,
        label_visibility="visible",
    )

    if mode == "QA product":
        idx = st.number_input("QA row", 0, max(0, len(D.qa) - 1), 0, step=1)
        row = D.qa.iloc[int(idx)].to_dict()
    elif mode == "Development product":
        idx = st.number_input("Development row", 0, max(0, len(D.dev) - 1), 0, step=1)
        row = D.dev.iloc[int(idx)].to_dict()
    else:
        row = {}
        fields = [
            ("ITEM_CODE", "Item code"),
            ("NAN_KEY", "NAN key"),
            ("EXTERNAL_CODE", "Barcode / external code"),
            ("COUNTRY", "Country"),
            ("RETAILER_DESC", "Retailer description"),
            ("RETAILER", "Retailer"),
            ("BRAND", "Brand"),
        ]
        cols = st.columns(2)
        for i, (key, label) in enumerate(fields):
            with cols[i % 2]:
                row[key] = st.text_input(label, key=f"custom_{key}")

    st.markdown('<div class="smallcaps" style="margin:18px 0 9px;">Input product</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([row]), use_container_width=True, hide_index=True)

    run = st.button("Run Product Truth Agent  →", type="primary", key="run_agent")

    st.markdown("</div>", unsafe_allow_html=True)

    if run:
        with st.spinner("Retrieving official brand/retailer web evidence and asking GPT-5.6 Luna..."):
            try:
                result, candidates = ProductTruthPipeline().run(row, web=True)
                st.session_state.last_result = result
                st.session_state.last_candidates = candidates
            except Exception as e:
                st.session_state.last_error = str(e)
                st.session_state.last_result = None

    result = st.session_state.get("last_result")
    error = st.session_state.get("last_error")

    if error and not result:
        st.error(error)
        st.info("If this is a CIS LLM connection timeout, the real Luna service is configured but the current network cannot reach the internal endpoint. Use the approved company remote-access route, then run again.")

    if result:
        errors = result.get("validation_errors", [])
        status_text = "VALIDATED" if not errors else "REVIEW"
        status_class = "status" if not errors else "status warn"
        st.markdown(
            f"""
<div class="result-hero">
  <div class="result-card">
    <div class="metric">Analysis status</div>
    <div style="margin-top:11px;"><span class="{status_class}">● {status_text}</span></div>
    <h3>{html.escape(str(result.get('module') or 'Module not selected'))}</h3>
    <div class="metric">Module confidence</div>
    <div class="metric-value">{html.escape(str(result.get('module_confidence') or '—'))}</div>
  </div>
  <div class="result-card">
    <div class="metric">Matched product</div>
    <h3>{html.escape(str(result.get('BRAND') or 'Unknown brand'))}</h3>
    <div style="font-size:13px;color:#65665f;line-height:1.55;">{html.escape(str(result.get('RETAILER_DESC') or 'No retailer description'))}</div>
    <div style="margin-top:14px;font-size:11px;color:#77786f;word-break:break-all;">{html.escape(str(result.get('product_url') or 'No official candidate URL was selected.'))}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="data-card"><div class="smallcaps">Predicted characteristics</div></div>', unsafe_allow_html=True)
        chars = result.get("characteristics", {})
        if chars:
            st.dataframe(
                pd.DataFrame([{"characteristic": k, "value": v} for k, v in chars.items()]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("No characteristics were returned.")

        st.markdown('<div class="data-card"><div class="smallcaps">Official Reasoning & Traceability</div></div>', unsafe_allow_html=True)
        st.write(result.get("reasoning") or "No reasoning returned.")

        if result.get("missing_characteristics"):
            st.warning("Missing characteristics: " + ", ".join(result["missing_characteristics"]))

        if errors:
            st.error("\n".join(errors))

        candidates = st.session_state.get("last_candidates", [])
        with st.expander("Official Evidence & Ranked Search Candidates"):
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "score": x.get("score"),
                            "title": x.get("title"),
                            "url": x.get("url"),
                            "snippet": x.get("snippet"),
                        }
                        for x in candidates
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )

        with st.expander("Evidence returned by Luna"):
            st.json(result.get("evidence", []))

        with st.expander("Raw result"):
            st.json(result)