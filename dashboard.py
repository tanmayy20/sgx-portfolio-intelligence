"""SGX Portfolio Intelligence — Singapore equity portfolio analytics.

Educational research tool. Market data is supplied by Yahoo Finance via yfinance.
This project is an adaptation of PortfolioManagementDashboard by GraberTopG;
see LICENSE and README for attribution and licence information.
"""
from datetime import date, timedelta
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

warnings.filterwarnings("ignore")

st.set_page_config(page_title="SGX Portfolio Intelligence", page_icon="📈", layout="wide")

# ── Singapore investment universe ──────────────────────────────────────────
STOCKS = {
    "DBS Group": "D05.SI", "OCBC": "O39.SI", "UOB": "U11.SI",
    "Singtel": "Z74.SI", "Singapore Airlines": "C6L.SI", "SGX": "S68.SI",
    "Keppel": "BN4.SI", "Wilmar International": "F34.SI",
    "CapitaLand Integrated Commercial Trust": "C38U.SI",
    "Mapletree Industrial Trust": "ME8U.SI", "CapitaLand Investment": "9CI.SI",
    "Frasers Centrepoint Trust": "J69U.SI", "Mapletree Logistics Trust": "M44U.SI",
    "ComfortDelGro": "C52.SI", "ST Engineering": "S63.SI",
}
BENCHMARK = "^STI"
BENCHMARK_NAME = "Straits Times Index"
SECTORS = {
    "D05.SI":"Banks", "O39.SI":"Banks", "U11.SI":"Banks",
    "Z74.SI":"Telecommunications", "C6L.SI":"Industrials & Transport",
    "S68.SI":"Financial Services", "BN4.SI":"Industrials",
    "F34.SI":"Consumer & Agriculture", "C38U.SI":"REITs",
    "ME8U.SI":"REITs", "9CI.SI":"Real Estate", "J69U.SI":"REITs",
    "M44U.SI":"REITs", "C52.SI":"Industrials & Transport", "S63.SI":"Industrials",
}
COLORS = {"navy":"#142B4A", "teal":"#0F8B8D", "mint":"#DDF3EF", "ink":"#172B3A", "muted":"#718096", "line":"#E6ECF1", "bg":"#F5F8FA", "green":"#16856B", "red":"#C65353"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"], .stApp {{font-family:'DM Sans',sans-serif; color:{COLORS['ink']};}}
.stApp {{background:{COLORS['bg']};}}
.block-container {{padding-top:2rem; padding-bottom:3rem; max-width:1500px;}}
h1,h2,h3 {{font-family:'Manrope',sans-serif; color:{COLORS['navy']}; letter-spacing:-.035em;}}
h1 {{font-size:2.15rem!important; font-weight:800!important;}}
h2 {{font-weight:700!important;}}
[data-testid="stSidebar"] {{background:#FFFFFF; border-right:1px solid {COLORS['line']};}}
[data-testid="stMetric"] {{background:#FFFFFF; border:1px solid {COLORS['line']}; padding:16px 18px; border-radius:12px; box-shadow:0 2px 8px rgba(20,43,74,.035);}}
[data-testid="stMetricLabel"] p {{color:{COLORS['muted']}!important; font-size:.78rem!important; font-weight:600!important;}}
[data-testid="stMetricValue"] {{color:{COLORS['navy']}!important; font-family:'Manrope',sans-serif;}}
.stTabs [data-baseweb="tab-list"] {{gap:8px; border-bottom:1px solid {COLORS['line']};}}
.stTabs [data-baseweb="tab"] {{background:#fff; border:1px solid {COLORS['line']}; border-radius:9px 9px 0 0; padding:10px 17px; color:{COLORS['muted']};}}
.stTabs [aria-selected="true"] {{color:{COLORS['teal']}!important; border-bottom:3px solid {COLORS['teal']}!important;}}
.stButton>button {{background:{COLORS['navy']}; color:#fff; border:0; border-radius:8px; font-weight:600;}}
.stButton>button:hover {{background:{COLORS['teal']}; color:white; border:0;}}
section[data-testid="stSidebar"] .stMultiSelect {{background:#fff;}}
.hero {{background:linear-gradient(110deg,#142B4A 0%,#1C4964 58%,#0F8B8D 100%); padding:27px 30px; border-radius:16px; color:#fff; margin-bottom:22px;}}
.hero-kicker {{font-size:.72rem; text-transform:uppercase; letter-spacing:.16em; opacity:.78; font-weight:700;}}
.hero-title {{font-family:'Manrope',sans-serif; font-size:1.85rem; font-weight:800; margin:7px 0 4px; color:#fff;}}
.hero-sub {{font-size:.92rem; opacity:.82;}}
.section-note {{color:{COLORS['muted']}; font-size:.85rem; margin-top:-8px;}}
.small-card {{background:#fff; border:1px solid {COLORS['line']}; border-radius:12px; padding:16px 18px;}}
div[data-testid="stAlert"] {{border-radius:10px;}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar controls ────────────────────────────────────────────────────────
st.sidebar.markdown("## SGX Intelligence")
st.sidebar.caption("Singapore equity portfolio research")
st.sidebar.divider()
name_to_ticker = {v:k for k,v in STOCKS.items()}
default_names = ["DBS Group", "OCBC", "UOB", "Singtel", "Singapore Airlines", "SGX", "CapitaLand Integrated Commercial Trust", "Mapletree Industrial Trust"]
selected_names = st.sidebar.multiselect("Portfolio universe", list(STOCKS.keys()), default=default_names, help="Choose up to 10 Singapore-listed securities.")
if not selected_names:
    selected_names = default_names
if len(selected_names) > 10:
    st.sidebar.warning("The dashboard is limited to 10 holdings. Only the first 10 are used.")
    selected_names = selected_names[:10]
selected = [STOCKS[n] for n in selected_names]
weight_mode = st.sidebar.radio("Allocation method", ["Equal weight", "Custom weights"], horizontal=False)
custom_weights = {}
if weight_mode == "Custom weights":
    st.sidebar.caption("Set approximate portfolio weights. They will be normalised to 100%.")
    for n in selected_names:
        custom_weights[STOCKS[n]] = st.sidebar.number_input(n, min_value=0.0, max_value=100.0, value=100.0/len(selected_names), step=1.0, key=f"w_{STOCKS[n]}")
    if sum(custom_weights.values()) <= 0:
        st.sidebar.error("Enter at least one positive weight.")
period_label = st.sidebar.selectbox("Historical period", ["1 year", "3 years", "5 years", "10 years"], index=1)
period_years = {"1 year":1,"3 years":3,"5 years":5,"10 years":10}[period_label]
end_date = date.today()
start_date = end_date - timedelta(days=365*period_years + 10)

# ── Data loading ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_prices(tickers, start, end):
    symbols = list(dict.fromkeys(list(tickers) + [BENCHMARK]))
    raw = yf.download(symbols, start=start, end=end, auto_adjust=True, progress=False, group_by="column", threads=True)
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = raw.columns.get_level_values(0)
        field = "Close" if "Close" in level0 else level0[0]
        prices = raw[field]
    else:
        prices = raw[["Close"]].rename(columns={"Close": symbols[0]})
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()
    return prices.dropna(how="all").sort_index()

st.markdown(f'''<div class="hero"><div class="hero-kicker">Singapore · Public Markets · Portfolio Analytics</div><div class="hero-title">SGX Portfolio Intelligence</div><div class="hero-sub">Portfolio construction, performance attribution and risk monitoring · Reporting currency: SGD</div></div>''', unsafe_allow_html=True)
with st.spinner("Retrieving Singapore market data from Yahoo Finance..."):
    prices_all = load_prices(tuple(selected), start_date.isoformat(), end_date.isoformat())

if prices_all.empty:
    st.error("Market data could not be retrieved. Check your internet connection or try again later. Yahoo Finance availability can vary by ticker.")
    st.stop()
available = [t for t in selected if t in prices_all.columns and prices_all[t].notna().sum() > 20]
if not available:
    st.error("None of the selected SGX securities returned sufficient price history. Try another selection.")
    st.stop()
prices = prices_all[available].dropna(how="all")
returns = prices.pct_change().dropna(how="all")
if weight_mode == "Custom weights" and sum(custom_weights.values()) > 0:
    w = pd.Series({t: custom_weights.get(t, 0) for t in available}, dtype=float)
    w = w / w.sum()
else:
    w = pd.Series(1/len(available), index=available)
w = w.reindex(available).fillna(0)
portfolio_returns = returns[available].fillna(0).mul(w, axis=1).sum(axis=1)
bench = prices_all[BENCHMARK].dropna() if BENCHMARK in prices_all.columns else pd.Series(dtype=float)
common = portfolio_returns.index.intersection(bench.index)
if len(common) > 10:
    portfolio_returns = portfolio_returns.loc[common]
    benchmark_returns = bench.pct_change().reindex(common).dropna()
    portfolio_returns = portfolio_returns.reindex(benchmark_returns.index)
else:
    benchmark_returns = pd.Series(dtype=float)

# daily return series and key metrics
if len(portfolio_returns) < 2:
    st.error("Not enough overlapping trading observations to calculate portfolio analytics.")
    st.stop()
nav = (1 + portfolio_returns).cumprod()
nav = nav / nav.iloc[0] * 100
ann_return = (nav.iloc[-1]/100)**(252/len(portfolio_returns))-1
ann_vol = portfolio_returns.std()*np.sqrt(252)
risk_free = 0.025  # illustrative constant SGD risk-free assumption; editable in methodology
sharpe = (ann_return-risk_free)/ann_vol if ann_vol and np.isfinite(ann_vol) else np.nan
running_max = nav.cummax()
drawdown = nav/running_max-1
max_drawdown = drawdown.min()
portfolio_value = st.sidebar.number_input("Illustrative portfolio value (SGD)", min_value=1000, max_value=1000000000, value=1000000, step=10000)

# ── Header context ──────────────────────────────────────────────────────────
last_date = prices.index[-1].strftime("%d %b %Y")
st.caption(f"Selected universe: {len(available)} securities  ·  Data through {last_date}  ·  Benchmark: {BENCHMARK_NAME}  ·  Currency: SGD")

# ── Tabs ────────────────────────────────────────────────────────────────────
t_over, t_hold, t_risk, t_corr, t_opt, t_method = st.tabs(["Overview", "Holdings & Allocation", "Risk Analytics", "Diversification", "Optimisation", "Methodology"])

with t_over:
    st.subheader("Portfolio at a glance")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Portfolio value", f"S${portfolio_value:,.0f}")
    c2.metric("Annualised return", f"{ann_return:.2%}")
    c3.metric("Annualised volatility", f"{ann_vol:.2%}")
    c4.metric("Sharpe ratio", f"{sharpe:.2f}" if np.isfinite(sharpe) else "N/A")
    c5.metric("Maximum drawdown", f"{max_drawdown:.2%}")
    st.markdown("### Growth of S$100 invested")
    growth = pd.DataFrame({"Portfolio":nav})
    if not benchmark_returns.empty:
        growth["Straits Times Index"] = (1+benchmark_returns).cumprod()*100
    fig = px.line(growth, color_discrete_sequence=[COLORS["teal"], COLORS["navy"]], labels={"value":"Indexed value (S$)","index":"Date","variable":"Series"})
    fig.update_layout(template="plotly_white", height=390, margin=dict(l=10,r=10,t=25,b=10), legend_title="", hovermode="x unified")
    fig.update_xaxes(showgrid=False); fig.update_yaxes(gridcolor=COLORS["line"])
    st.plotly_chart(fig, use_container_width=True)
    left,right = st.columns([1.2,1])
    with left:
        st.markdown("### Portfolio drawdown")
        ddfig = go.Figure(go.Scatter(x=drawdown.index,y=drawdown*100,fill="tozeroy",line=dict(color=COLORS["red"],width=1.5),name="Drawdown"))
        ddfig.update_layout(template="plotly_white",height=280,margin=dict(l=10,r=10,t=10,b=10),yaxis_title="Drawdown (%)")
        ddfig.update_yaxes(gridcolor=COLORS["line"]); st.plotly_chart(ddfig,use_container_width=True)
    with right:
        st.markdown("### Benchmark snapshot")
        if not benchmark_returns.empty:
            bret=(1+benchmark_returns).prod()-1
            pret=(1+portfolio_returns).prod()-1
            st.metric("Portfolio cumulative return",f"{pret:.2%}")
            st.metric("STI cumulative return",f"{bret:.2%}")
            st.metric("Active return",f"{pret-bret:+.2%}")
        else: st.info("STI benchmark data was unavailable for the selected period.")

with t_hold:
    st.subheader("Holdings and capital allocation")
    allocation = pd.DataFrame({"Company": [name_to_ticker.get(t,t) for t in available], "Ticker":available, "Sector":[SECTORS.get(t,"Other") for t in available], "Weight":w.values, "Allocation (SGD)":w.values*portfolio_value})
    a,b=st.columns([1,1.25])
    with a:
        pie=px.pie(allocation,names="Company",values="Weight",hole=.62,color_discrete_sequence=px.colors.qualitative.Safe)
        pie.update_traces(textposition="outside",textinfo="percent",hole=.62)
        pie.update_layout(template="plotly_white",height=370,margin=dict(l=10,r=10,t=15,b=10),legend_title="Holding")
        st.plotly_chart(pie,use_container_width=True)
    with b:
        sector=allocation.groupby("Sector",as_index=False)["Weight"].sum().sort_values("Weight")
        bar=px.bar(sector,x="Weight",y="Sector",orientation="h",text=sector["Weight"].map(lambda x:f"{x:.1%}"),color_discrete_sequence=[COLORS["teal"]])
        bar.update_layout(template="plotly_white",height=370,margin=dict(l=10,r=10,t=15,b=10),xaxis_tickformat=".0%",showlegend=False)
        st.plotly_chart(bar,use_container_width=True)
    st.markdown("### Position register")
    allocation["Weight"] = allocation["Weight"].map(lambda x:f"{x:.2%}")
    allocation["Allocation (SGD)"] = allocation["Allocation (SGD)"].map(lambda x:f"S${x:,.0f}")
    st.dataframe(allocation,hide_index=True,use_container_width=True)

with t_risk:
    st.subheader("Risk monitoring")
    downside=portfolio_returns[portfolio_returns<0]
    var95=float(np.quantile(portfolio_returns,0.05))
    cvar95=float(downside[downside<=var95].mean()) if len(downside) else var95
    beta=np.nan
    if not benchmark_returns.empty and benchmark_returns.std()>0:
        aligned=pd.concat([portfolio_returns,benchmark_returns],axis=1).dropna()
        if len(aligned)>2: beta=np.cov(aligned.iloc[:,0],aligned.iloc[:,1])[0,1]/np.var(aligned.iloc[:,1])
    r1,r2,r3,r4=st.columns(4)
    r1.metric("Historical VaR · 95%",f"{var95:.2%}")
    r2.metric("Historical CVaR · 95%",f"{cvar95:.2%}")
    r3.metric("Beta vs STI",f"{beta:.2f}" if np.isfinite(beta) else "N/A")
    r4.metric("Downside deviation",f"{np.sqrt(np.mean(np.minimum(portfolio_returns,0)**2)*252):.2%}")
    st.markdown("### Rolling 60-session volatility")
    rolling=portfolio_returns.rolling(60).std()*np.sqrt(252)*100
    rf=go.Figure(go.Scatter(x=rolling.index,y=rolling,line=dict(color=COLORS["teal"],width=2),name="Rolling volatility"))
    rf.update_layout(template="plotly_white",height=330,margin=dict(l=10,r=10,t=10,b=10),yaxis_title="Annualised volatility (%)")
    rf.update_yaxes(gridcolor=COLORS["line"]); st.plotly_chart(rf,use_container_width=True)
    st.caption("Historical VaR/CVaR are estimates from the selected sample, not forecasts or loss limits.")

with t_corr:
    st.subheader("Correlation and diversification")
    corr=returns[available].corr()
    labels=[name_to_ticker.get(t,t) for t in corr.columns]
    heat=go.Figure(go.Heatmap(z=corr.values,x=labels,y=labels,zmin=-1,zmax=1,colorscale="RdYlBu",text=np.round(corr.values,2),texttemplate="%{text}",colorbar_title="Correlation"))
    heat.update_layout(template="plotly_white",height=570,margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(heat,use_container_width=True)
    st.markdown("### Concentration")
    hhi=float((w**2).sum())
    st.metric("Herfindahl–Hirschman Index",f"{hhi:.3f}",help="Sum of squared portfolio weights. Higher values indicate greater concentration.")

with t_opt:
    st.subheader("Portfolio optimisation laboratory")
    st.write("Compare simple allocation strategies using historical daily returns. This is an educational illustration, not a forecast.")
    min_w=float(st.slider("Maximum weight per security",10,100,40,5))/100
    if len(available)<2:
        st.info("Select at least two securities to compare allocations.")
    else:
        mu=returns[available].mean()*252
        cov=returns[available].cov()*252
        inv_vol=1/(returns[available].std()*np.sqrt(252)).replace(0,np.nan)
        rp=(inv_vol/inv_vol.sum()).fillna(1/len(available))
        # Long-only minimum-variance search using deterministic random portfolios.
        rng=np.random.default_rng(17)
        candidates=[]
        for _ in range(12000):
            x=rng.dirichlet(np.ones(len(available))*1.5)
            if x.max()<=min_w+1e-9:
                vol=float(np.sqrt(x@cov.values@x))
                ret=float(x@mu.values)
                candidates.append((ret,vol,x))
        if candidates:
            best=min(candidates,key=lambda z:z[1])
            maxsh=max(candidates,key=lambda z:(z[0]-risk_free)/z[1] if z[1]>0 else -999)
            rows=[]
            for label,weights in [("Equal weight",np.repeat(1/len(available),len(available))),("Inverse volatility",rp.values),("Minimum variance",best[2]),("Maximum Sharpe",maxsh[2])]:
                pr=float(weights@mu.values); pv=float(np.sqrt(weights@cov.values@weights)); sr=(pr-risk_free)/pv if pv>0 else np.nan
                rows.append({"Strategy":label,"Expected annual return":pr,"Annual volatility":pv,"Sharpe ratio":sr})
            comp=pd.DataFrame(rows)
            st.dataframe(comp.style.format({"Expected annual return":"{:.2%}","Annual volatility":"{:.2%}","Sharpe ratio":"{:.2f}"}),hide_index=True,use_container_width=True)
            optweights=pd.DataFrame({"Ticker":available,"Company":[name_to_ticker.get(t,t) for t in available],"Min variance weight":best[2],"Max Sharpe weight":maxsh[2]})
            st.markdown("### Suggested model weights")
            st.dataframe(optweights.style.format({"Min variance weight":"{:.1%}","Max Sharpe weight":"{:.1%}"}),hide_index=True,use_container_width=True)
            st.caption("Optimisation uses randomly sampled long-only portfolios subject to the selected single-name cap. Results are sensitive to historical estimates and sampling; increase sample count for more precision.")
        else:
            st.warning("No feasible portfolios found under this maximum weight. Increase the cap or select more securities.")

with t_method:
    st.subheader("Methodology, assumptions and data limitations")
    st.markdown("""
    **Market data.** Daily adjusted prices are requested from Yahoo Finance through `yfinance`. SGX symbols use the `.SI` suffix; the Straits Times Index is requested as `^STI`. Data availability, corporate-action adjustments and historical coverage depend on the upstream provider.

    **Portfolio returns.** The application computes daily weighted returns from selected securities. Equal-weight allocation is the default; custom weights are normalised to 100%. The illustrative portfolio value is used only to translate weights into SGD position amounts.

    **Performance.** Annualised return is estimated from the indexed portfolio series using 252 trading sessions. Annualised volatility is daily standard deviation multiplied by √252. Sharpe ratio uses a fixed illustrative 2.5% SGD risk-free assumption; it is not a live MAS bill yield.

    **Risk.** Historical VaR is the 5th percentile of daily returns; CVaR is the average return in the tail at or below that threshold. Maximum drawdown is measured from the running peak. Beta is estimated against the STI using overlapping daily observations.

    **Optimisation.** Minimum variance and maximum Sharpe allocations are selected from a deterministic random sample of long-only portfolios subject to a user-defined maximum position weight. These estimates are highly sensitive to the historical sample and should not be treated as forward-looking expected returns.

    **Important.** This is an educational portfolio analytics project, not investment advice, a trading system or a regulated financial service. Verify all data independently before making investment decisions.
    """)
    st.markdown("### Data source")
    st.link_button("Yahoo Finance", "https://finance.yahoo.com/", use_container_width=False)
    st.markdown("### Project information")
    st.write("Singapore-focused adaptation of the open-source PortfolioManagementDashboard by GraberTopG. Original project attribution and Apache 2.0 licence are retained in this repository.")

st.divider()
st.caption("SGX Portfolio Intelligence · Educational research application · Data source: Yahoo Finance · Reporting currency: SGD")
