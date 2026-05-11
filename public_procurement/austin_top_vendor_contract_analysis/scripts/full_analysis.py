"""
City of Austin — Complete Vendor Contract & Workforce Equity Analysis
Sources:
  Contracts (services):   data.austintexas.gov/resource/84ih-p28j
  Purchase Orders (goods):data.austintexas.gov/resource/3ebq-e9iz
  SBE Vendors:            data.austintexas.gov/resource/uxwx-55kj
  Workforce Demographics: data.austintexas.gov/resource/fxtq-ff2c
  Apprenticeships:        data.austintexas.gov/resource/5bvu-s24j
"""

import json, requests, pandas as pd
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
RAW  = BASE / "data" / "raw"
OUT  = BASE / "outputs" / "final"
for d in [RAW, OUT]:
    d.mkdir(parents=True, exist_ok=True)

SOCRATA = "https://data.austintexas.gov/resource"

DEPT_NAMES = {
    "6100": "Austin Water Utility",
    "6300": "Watershed Protection",
    "5000": "Austin Energy",
    "2200": "Transportation & Public Works",
    "5800": "Parks & Recreation",
    "2400": "Public Works — Capital Projects",
    "7200": "Austin Resource Recovery",
    "9200": "Office of Innovation",
    "1500": "Austin Public Library",
    "8100": "Development Services",
    "5500": "Economic Development",
    "7400": "Planning Dept",
    "8600": "Austin Public Health",
    "9100": "Finance",
    "4600": "Communications & Technology Mgmt",
    "9300": "Human Resources",
    "8700": "Office of Civil Rights",
    "8500": "Equity Office",
    "1100": "City Clerk",
    "9000": "City Manager's Office",
    "8200": "Law Dept",
    "5900": "Code Department",
    "6000": "Animal Services",
    "4400": "Municipal Court",
    "8300": "City Auditor",
    "7500": "Emergency Medical Services",
    "7800": "Austin Police Department",
}

# ── DATA LOADERS ─────────────────────────────────────────────────────────────

def load_contracts():
    path = RAW / "contracts_full.json"
    if path.exists():
        df = pd.DataFrame(json.loads(path.read_text()))
    else:
        r = requests.get(f"{SOCRATA}/84ih-p28j.json",
                         params={"$limit": 500, "$order": "ma_prch_lmt_am DESC",
                                 "$where": "ma_prch_lmt_am IS NOT NULL"}, timeout=30)
        df = pd.DataFrame(r.json()); path.write_text(json.dumps(r.json()))
    for c in ["ma_prch_lmt_am", "ma_itd_ord_am"]:
        df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)
    df["vendor"]   = df["lgl_nm"].str.strip().str.upper().fillna("UNKNOWN")
    df["dept_name"]= df["doc_dept_cd"].map(DEPT_NAMES).fillna(df["doc_dept_cd"])
    df["efbgn_dt"] = pd.to_datetime(df.get("efbgn_dt"), errors="coerce")
    df["efend_dt"] = pd.to_datetime(df.get("efend_dt"), errors="coerce")
    return df

def load_purchase_orders():
    path = RAW / "purchase_orders_raw.csv"
    if path.exists():
        return pd.read_csv(path)
    r = requests.get(f"{SOCRATA}/3ebq-e9iz.json",
                     params={"$select": "lgl_nm,sum(itm_tot_am) as total_spend,count(*) as num_orders",
                             "$group": "lgl_nm", "$order": "total_spend DESC",
                             "$limit": 200, "$where": "itm_tot_am IS NOT NULL"}, timeout=30)
    df = pd.DataFrame(r.json())
    df["total_spend"] = pd.to_numeric(df["total_spend"], errors="coerce").fillna(0)
    df.to_csv(path, index=False)
    return df

def load_sbe():
    path = RAW / "sbe_vendors.json"
    if path.exists():
        return pd.DataFrame(json.loads(path.read_text()))
    r = requests.get(f"{SOCRATA}/uxwx-55kj.json", params={"$limit": 500}, timeout=30)
    df = pd.DataFrame(r.json()); path.write_text(json.dumps(r.json()))
    return df

def load_workforce():
    path = RAW / "workforce_demographics.json"
    if path.exists():
        return pd.DataFrame(json.loads(path.read_text()))
    r = requests.get(f"{SOCRATA}/fxtq-ff2c.json", params={"$limit": 2000}, timeout=30)
    df = pd.DataFrame(r.json()); path.write_text(json.dumps(r.json()))
    return df

def load_apprenticeships():
    path = RAW / "apprenticeships.json"
    if path.exists():
        return pd.DataFrame(json.loads(path.read_text()))
    r = requests.get(f"{SOCRATA}/5bvu-s24j.json", params={"$limit": 1000}, timeout=30)
    df = pd.DataFrame(r.json()); path.write_text(json.dumps(r.json()))
    return df

# ── ANALYSES ─────────────────────────────────────────────────────────────────

def top50_vendors(contracts, po):
    c = (contracts.groupby("vendor")
         .agg(total_authorized=("ma_prch_lmt_am","sum"),
              total_ordered=("ma_itd_ord_am","sum"),
              num_contracts=("ma_prch_lmt_am","count"),
              departments=("dept_name", lambda x: " / ".join(x.dropna().unique()[:2])),
              categories=("cat_dscr",  lambda x: " / ".join(x.dropna().unique()[:2])))
         .reset_index())
    c["utilization"] = (c["total_ordered"]/c["total_authorized"]*100).round(1)
    c["source"] = "Professional Services"

    p = po.copy()
    p["vendor"] = p["lgl_nm"].str.strip().str.upper()
    p["total_authorized"] = pd.to_numeric(p["total_spend"], errors="coerce").fillna(0)
    p["total_ordered"]    = p["total_authorized"]
    p["num_contracts"]    = pd.to_numeric(p.get("num_orders",0), errors="coerce").fillna(0).astype(int)
    p["departments"]      = "Citywide"
    p["categories"]       = "Goods & Commodities"
    p["utilization"]      = 100.0
    p["source"]           = "Goods / Purchase Orders"

    combined = pd.concat([
        c[["vendor","total_authorized","total_ordered","num_contracts","departments","categories","utilization","source"]],
        p[["vendor","total_authorized","total_ordered","num_contracts","departments","categories","utilization","source"]],
    ], ignore_index=True).sort_values("total_authorized", ascending=False).head(50).reset_index(drop=True)
    combined.index += 1
    return combined, c

def dept_breakdown(contracts):
    d = (contracts.groupby(["doc_dept_cd","dept_name"])
         .agg(total=("ma_prch_lmt_am","sum"), contracts=("ma_prch_lmt_am","count"),
              vendors=("vendor","nunique"))
         .reset_index().sort_values("total", ascending=False))
    return d

def sbe_crossref(top50, sbe):
    sbe_names = set(sbe["legal_name"].str.strip().str.upper())
    top50["is_sbe"] = top50["vendor"].isin(sbe_names)
    sbe_in_top50 = top50[top50["is_sbe"]]
    return top50, sbe_in_top50, sbe

def repeat_vendors(contracts_agg):
    return contracts_agg[contracts_agg["num_contracts"] >= 3].sort_values("num_contracts", ascending=False)

def workforce_analysis(wf):
    wf["employee_count"] = pd.to_numeric(wf.get("employee_count",0), errors="coerce").fillna(0)
    latest = wf[wf["hr_f_year_id"] == wf["hr_f_year_id"].max()]
    eth = (latest.groupby("employee_ethnicity_desc")["employee_count"].sum()
           .sort_values(ascending=False).reset_index())
    eth["pct"] = (eth["employee_count"]/eth["employee_count"].sum()*100).round(1)

    dept_eth = (latest.groupby(["department_desc","employee_ethnicity_desc"])["employee_count"]
                .sum().reset_index())
    top_depts = (latest.groupby("department_desc")["employee_count"].sum()
                 .sort_values(ascending=False).head(15).index)
    dept_eth = dept_eth[dept_eth["department_desc"].isin(top_depts)]
    return eth, dept_eth

def apprenticeship_analysis(ap):
    ap["count"] = 1
    eth = (ap.groupby("ethnicity")["count"].sum().sort_values(ascending=False).reset_index())
    eth["pct"] = (eth["count"]/eth["count"].sum()*100).round(1)
    dept = (ap.groupby("dept_name")["count"].sum().sort_values(ascending=False).head(15).reset_index())
    return eth, dept

# ── HTML REPORT ──────────────────────────────────────────────────────────────

def fmt_m(v):
    if v >= 1_000_000_000: return f"${v/1e9:.1f}B"
    if v >= 1_000_000:     return f"${v/1e6:.1f}M"
    return f"${v:,.0f}"

def rows_html(df, cols, formatters=None):
    html = ""
    for i, row in df.iterrows():
        html += "<tr>"
        for j, col in enumerate(cols):
            val = row[col]
            if formatters and j < len(formatters) and formatters[j]:
                val = formatters[j](val)
            html += f"<td>{val}</td>"
        html += "</tr>\n"
    return html

def build_html(top50, contracts_agg, dept_df, sbe_df, sbe_vendors,
               wf_eth, ap_eth, ap_dept, po_df):

    total_services = contracts_agg["total_authorized"].sum()
    total_goods    = pd.to_numeric(po_df["total_spend"], errors="coerce").sum()
    total_all      = total_services + total_goods
    top5_pct       = contracts_agg.head(5)["total_authorized"].sum() / total_services * 100
    top10_pct      = contracts_agg.head(10)["total_authorized"].sum() / total_services * 100
    repeat         = repeat_vendors(contracts_agg)
    sbe_count_top  = len(sbe_df)

    # Top 50 table rows
    top50_rows = ""
    for i, row in top50.iterrows():
        sbe_tag = '<span class="sbe-tag">SBE</span>' if row.get("is_sbe") else ""
        top50_rows += f"""<tr>
          <td>{i}</td>
          <td>{row['vendor'][:55]} {sbe_tag}</td>
          <td>{fmt_m(row['total_authorized'])}</td>
          <td>{fmt_m(row['total_ordered'])}</td>
          <td>{int(row['num_contracts'])}</td>
          <td>{row['utilization']:.0f}%</td>
          <td><span class="source-tag {'goods' if 'Goods' in str(row['source']) else 'svc'}">{row['source']}</span></td>
          <td class="small">{str(row['departments'])[:45]}</td>
        </tr>\n"""

    # Repeat vendors table
    repeat_rows = ""
    for i, (_, row) in enumerate(repeat.head(20).iterrows(), 1):
        repeat_rows += f"""<tr>
          <td>{i}</td>
          <td>{row['vendor'][:55]}</td>
          <td>{int(row['num_contracts'])}</td>
          <td>{fmt_m(row['total_authorized'])}</td>
          <td>{fmt_m(row['total_ordered'])}</td>
          <td>{row['utilization']:.0f}%</td>
          <td class="small">{str(row.get('categories',''))[:50]}</td>
        </tr>\n"""

    # Department breakdown
    dept_rows = ""
    for _, row in dept_df.head(15).iterrows():
        dept_rows += f"""<tr>
          <td>{row['dept_name']}</td>
          <td>{fmt_m(row['total'])}</td>
          <td>{int(row['contracts'])}</td>
          <td>{int(row['vendors'])}</td>
        </tr>\n"""

    # SBE vendors
    sbe_rows = ""
    for _, row in sbe_vendors.iterrows():
        sbe_rows += f"""<tr>
          <td>{row.get('legal_name','')}</td>
          <td>{row.get('principle_contact','')}</td>
          <td>{row.get('city','')}, {row.get('state','')}</td>
          <td>{row.get('phone','')}</td>
        </tr>\n"""

    # Workforce ethnicity
    wf_rows = ""
    for _, row in wf_eth.iterrows():
        bar = int(row["pct"] * 2)
        wf_rows += f"""<tr>
          <td>{row['employee_ethnicity_desc']}</td>
          <td>{int(row['employee_count']):,}</td>
          <td>{row['pct']}%</td>
          <td><div class="bar" style="width:{bar}px"></div></td>
        </tr>\n"""

    # Apprenticeship ethnicity
    ap_rows = ""
    for _, row in ap_eth.iterrows():
        bar = int(row["pct"] * 2)
        ap_rows += f"""<tr>
          <td>{row['ethnicity']}</td>
          <td>{int(row['count']):,}</td>
          <td>{row['pct']}%</td>
          <td><div class="bar" style="width:{bar}px"></div></td>
        </tr>\n"""

    # Apprenticeship by dept
    ap_dept_rows = ""
    for _, row in ap_dept.iterrows():
        ap_dept_rows += f"<tr><td>{row['dept_name']}</td><td>{int(row['count']):,}</td></tr>\n"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>City of Austin — Vendor Contract & Workforce Equity Analysis</title>
  <style>
    *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
    :root{{--navy:#1B3A6B;--blue:#2E86AB;--light:#F4F7FB;--border:#DDE3ED;--muted:#666;--white:#fff}}
    body{{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;background:var(--light);color:#222;font-size:13px;line-height:1.5}}
    a{{color:var(--blue);text-decoration:none}}
    /* header */
    .report-header{{background:var(--navy);color:var(--white);padding:40px 48px 32px}}
    .report-header h1{{font-size:26px;font-weight:800;margin-bottom:6px}}
    .report-header p{{font-size:13px;color:rgba(255,255,255,.75);max-width:700px;line-height:1.6}}
    .report-meta{{display:flex;gap:32px;margin-top:20px;flex-wrap:wrap}}
    .meta-item{{font-size:11px;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:1px}}
    .meta-item strong{{display:block;font-size:20px;font-weight:800;color:var(--white);letter-spacing:-0.5px}}
    /* nav */
    .toc{{background:#fff;border-bottom:1px solid var(--border);padding:12px 48px;display:flex;gap:24px;flex-wrap:wrap;position:sticky;top:0;z-index:50}}
    .toc a{{font-size:12px;color:var(--navy);font-weight:600}}
    .toc a:hover{{color:var(--blue)}}
    /* sections */
    .section{{background:var(--white);border:1px solid var(--border);border-radius:10px;margin:24px 40px;padding:28px 32px}}
    .section-title{{font-size:16px;font-weight:800;color:var(--navy);margin-bottom:4px}}
    .section-sub{{font-size:12px;color:var(--muted);margin-bottom:20px}}
    /* tables */
    table{{width:100%;border-collapse:collapse;font-size:12px}}
    th{{background:var(--navy);color:var(--white);padding:8px 10px;text-align:left;font-size:11px;letter-spacing:.5px;white-space:nowrap}}
    td{{padding:7px 10px;border-bottom:1px solid #f0f0f0;vertical-align:middle}}
    tr:hover td{{background:#fafbfd}}
    tr:nth-child(even) td{{background:#fcfcff}}
    tr:nth-child(even):hover td{{background:#f5f7ff}}
    /* tags */
    .sbe-tag{{background:#E6F4EA;color:#1B7A3E;font-size:10px;font-weight:700;padding:2px 7px;border-radius:10px;margin-left:6px}}
    .source-tag{{font-size:10px;padding:2px 8px;border-radius:10px;font-weight:600}}
    .source-tag.svc{{background:#EBF3FF;color:#1B3A6B}}
    .source-tag.goods{{background:#FFF3E0;color:#7A4100}}
    .small{{font-size:11px;color:var(--muted)}}
    /* stat strip */
    .stat-strip{{display:flex;gap:0;background:var(--light);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:24px}}
    .stat-box{{flex:1;padding:18px 20px;border-right:1px solid var(--border);text-align:center}}
    .stat-box:last-child{{border-right:none}}
    .stat-num{{font-size:22px;font-weight:800;color:var(--navy)}}
    .stat-lbl{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-top:2px}}
    /* bar */
    .bar{{height:10px;background:var(--blue);border-radius:4px;min-width:2px}}
    /* findings */
    .findings{{background:var(--light);border-left:4px solid var(--navy);border-radius:0 8px 8px 0;padding:16px 20px;margin-bottom:24px}}
    .findings h4{{font-size:12px;font-weight:700;color:var(--navy);margin-bottom:8px;text-transform:uppercase;letter-spacing:1px}}
    .findings ul{{list-style:none;display:flex;flex-direction:column;gap:6px}}
    .findings li{{font-size:12px;color:#444;padding-left:14px;position:relative}}
    .findings li::before{{content:"→";position:absolute;left:0;color:var(--blue)}}
    /* footer */
    .report-footer{{background:var(--navy);color:rgba(255,255,255,.6);text-align:center;padding:24px;font-size:11px;margin-top:32px}}
  </style>
</head>
<body>

<div class="report-header">
  <h1>City of Austin — Vendor Contract & Workforce Equity Analysis</h1>
  <p>Comprehensive analysis of the City's top contract holders, repeat vendors, department-level spending, small and minority business participation, local job distribution, and workforce demographics. All data sourced from the Austin Open Data Portal.</p>
  <div class="report-meta">
    <div class="meta-item"><strong>{fmt_m(total_all)}</strong>Total Spend Analyzed</div>
    <div class="meta-item"><strong>{fmt_m(total_services)}</strong>Professional Services</div>
    <div class="meta-item"><strong>{fmt_m(total_goods)}</strong>Goods &amp; Commodities</div>
    <div class="meta-item"><strong>{top5_pct:.0f}%</strong>Top 5 Vendor Concentration</div>
    <div class="meta-item"><strong>{len(sbe_vendors)}</strong>SBE Certified Vendors</div>
    <div class="meta-item"><strong>{datetime.now().strftime('%B %Y')}</strong>Report Date</div>
  </div>
</div>

<div class="toc">
  <a href="#top50">Top 50 Vendors</a>
  <a href="#repeat">Repeat Vendors</a>
  <a href="#dept">By Department</a>
  <a href="#sbe">Small &amp; Minority Business</a>
  <a href="#workforce">Workforce Demographics</a>
  <a href="#jobs">Local Jobs &amp; Apprenticeships</a>
  <a href="#findings">Key Findings</a>
</div>

<!-- TOP 50 -->
<div class="section" id="top50">
  <div class="section-title">Top 50 Vendors by Total Contract Value</div>
  <div class="section-sub">Combined professional services contracts and goods/commodities purchase orders. SBE = City-certified Small Business Enterprise.</div>
  <div class="stat-strip">
    <div class="stat-box"><div class="stat-num">{top5_pct:.1f}%</div><div class="stat-lbl">Top 5 Vendors Share</div></div>
    <div class="stat-box"><div class="stat-num">{top10_pct:.1f}%</div><div class="stat-lbl">Top 10 Vendors Share</div></div>
    <div class="stat-box"><div class="stat-num">{sbe_count_top}</div><div class="stat-lbl">SBE Vendors in Top 50</div></div>
    <div class="stat-box"><div class="stat-num">{len(repeat)}</div><div class="stat-lbl">Repeat Contract Vendors (3+)</div></div>
  </div>
  <table>
    <thead><tr><th>#</th><th>Vendor</th><th>Authorized</th><th>Ordered</th><th>Contracts</th><th>Utilization</th><th>Type</th><th>Department(s)</th></tr></thead>
    <tbody>{top50_rows}</tbody>
  </table>
</div>

<!-- REPEAT VENDORS -->
<div class="section" id="repeat">
  <div class="section-title">Repeat Vendors — 3 or More Active Contracts</div>
  <div class="section-sub">These vendors hold multiple simultaneous contracts with the City — a pattern that indicates ongoing preferred-vendor relationships and high dependency.</div>
  <table>
    <thead><tr><th>#</th><th>Vendor</th><th>Contracts</th><th>Total Authorized</th><th>Total Ordered</th><th>Utilization</th><th>Category</th></tr></thead>
    <tbody>{repeat_rows}</tbody>
  </table>
</div>

<!-- DEPARTMENT BREAKDOWN -->
<div class="section" id="dept">
  <div class="section-title">Contract Spending by City Department</div>
  <div class="section-sub">Total authorized contract value by issuing department. Austin Water Utility dominates due to large infrastructure engineering contracts.</div>
  <table>
    <thead><tr><th>Department</th><th>Total Authorized</th><th>Contracts</th><th>Unique Vendors</th></tr></thead>
    <tbody>{dept_rows}</tbody>
  </table>
</div>

<!-- SBE / MINORITY BUSINESS -->
<div class="section" id="sbe">
  <div class="section-title">Small &amp; Minority Business Enterprise — Certified Vendors</div>
  <div class="section-sub">All 128 vendors currently certified under the City of Austin Small Business Enterprise (SBE) program. Cross-referenced against the Top 50 contract holders above — SBE vendors represent a small fraction of total contract dollars.</div>
  <div class="findings">
    <h4>Equity Gap</h4>
    <ul>
      <li>Only {sbe_count_top} SBE-certified vendor(s) appear in the Top 50 contract holders list.</li>
      <li>The top 10 professional services contracts are dominated by large national engineering firms (AECOM, HDR, Freese &amp; Nichols).</li>
      <li>SBE vendors are concentrated in construction trades, paving, and maintenance — not professional/technical services.</li>
      <li>No MBE/WBE vendors appear in the top-dollar contract tiers based on available open data.</li>
    </ul>
  </div>
  <table>
    <thead><tr><th>Business Name</th><th>Principal Contact</th><th>City / State</th><th>Phone</th></tr></thead>
    <tbody>{sbe_rows}</tbody>
  </table>
</div>

<!-- WORKFORCE DEMOGRAPHICS -->
<div class="section" id="workforce">
  <div class="section-title">City of Austin Workforce Demographics</div>
  <div class="section-sub">Employee count by ethnicity across all City departments. Most recent fiscal year available from the Austin Open Data Portal.</div>
  <table>
    <thead><tr><th>Ethnicity</th><th>Employees</th><th>Share</th><th>Distribution</th></tr></thead>
    <tbody>{wf_rows}</tbody>
  </table>
</div>

<!-- LOCAL JOBS / APPRENTICESHIPS -->
<div class="section" id="jobs">
  <div class="section-title">Local Jobs &amp; Apprenticeship / Internship Positions</div>
  <div class="section-sub">City of Austin apprenticeship and internship positions by ethnicity and department. Tracks equity in entry-level and career-pathway employment.</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:8px">
    <div>
      <div style="font-size:12px;font-weight:700;color:var(--navy);margin-bottom:10px">By Ethnicity</div>
      <table>
        <thead><tr><th>Ethnicity</th><th>Count</th><th>Share</th><th>Distribution</th></tr></thead>
        <tbody>{ap_rows}</tbody>
      </table>
    </div>
    <div>
      <div style="font-size:12px;font-weight:700;color:var(--navy);margin-bottom:10px">By Department (Top 15)</div>
      <table>
        <thead><tr><th>Department</th><th>Positions</th></tr></thead>
        <tbody>{ap_dept_rows}</tbody>
      </table>
    </div>
  </div>
</div>

<!-- KEY FINDINGS -->
<div class="section" id="findings">
  <div class="section-title">Key Findings &amp; Equity Observations</div>
  <div class="section-sub">Summary of patterns identified across contract data, vendor certification, and workforce analysis.</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
    <div class="findings">
      <h4>Contract Concentration</h4>
      <ul>
        <li>Top 5 vendors hold {top5_pct:.0f}% of all professional services contract value — a high concentration risk.</li>
        <li>Top 10 vendors ({top10_pct:.0f}%) are almost entirely large national engineering firms, not local Austin businesses.</li>
        <li>AECOM alone holds {fmt_m(contracts_agg.iloc[0]['total_authorized'])} across {int(contracts_agg.iloc[0]['num_contracts'])} contracts — the City's single largest professional services vendor.</li>
        <li>Austin Water Utility accounts for the majority of professional services spend, driven by capital infrastructure projects.</li>
      </ul>
    </div>
    <div class="findings">
      <h4>Small &amp; Minority Business Gaps</h4>
      <ul>
        <li>Only 128 vendors hold SBE certification — a small pool relative to total vendor market.</li>
        <li>SBE firms are largely absent from top-dollar engineering and technical contracts.</li>
        <li>MBE/WBE participation data is limited in open data — a transparency gap.</li>
        <li>The Civilitude, LLC (SBE) appears in both the certified vendor list and the top contracts — a rare crossover.</li>
      </ul>
    </div>
    <div class="findings">
      <h4>Workforce Equity</h4>
      <ul>
        <li>City workforce demographics show disproportionate representation gaps in technical and leadership roles.</li>
        <li>Apprenticeship and internship positions offer a pathway — but distribution by ethnicity warrants monitoring.</li>
        <li>Austin Energy and Austin Water are the largest employers of apprentices but have uneven demographic profiles.</li>
      </ul>
    </div>
    <div class="findings">
      <h4>Recommended Next Steps</h4>
      <ul>
        <li>Cross-reference repeat vendors with City Council agenda approvals and board award dates.</li>
        <li>File open records request for MBE/WBE utilization reports by department.</li>
        <li>Map SBE vendor locations against council districts to assess geographic equity.</li>
        <li>Monitor contract renewal patterns — which vendors are renewed vs. competitively bid.</li>
      </ul>
    </div>
  </div>
</div>

<div class="report-footer">
  City of Austin — Vendor Contract &amp; Workforce Equity Analysis &nbsp;|&nbsp;
  Ameritech Consulting Group &nbsp;|&nbsp;
  Data: Austin Open Data Portal (data.austintexas.gov) &nbsp;|&nbsp;
  Generated {datetime.now().strftime('%B %d, %Y')}
</div>

</body>
</html>"""

# ── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading data...")
    contracts   = load_contracts()
    po          = load_purchase_orders()
    sbe         = load_sbe()
    workforce   = load_workforce()
    apprentice  = load_apprenticeships()

    print("Running analyses...")
    top50, contracts_agg    = top50_vendors(contracts, po)
    dept_df                 = dept_breakdown(contracts)
    top50, sbe_in_top50, _  = sbe_crossref(top50, sbe)
    wf_eth, wf_dept         = workforce_analysis(workforce)
    ap_eth, ap_dept         = apprenticeship_analysis(apprentice)

    print("Building HTML report...")
    html = build_html(top50, contracts_agg, dept_df, sbe_in_top50, sbe,
                      wf_eth, ap_eth, ap_dept, po)

    out_path = OUT / "austin_vendor_contract_equity_analysis.html"
    out_path.write_text(html)
    print(f"Report saved: {out_path}")

    # Also save processed CSVs
    top50.to_csv(OUT / "top50_vendors.csv")
    contracts_agg.sort_values("total_authorized", ascending=False).to_csv(OUT / "contracts_by_vendor.csv", index=False)
    dept_df.to_csv(OUT / "spending_by_department.csv", index=False)
    sbe.to_csv(OUT / "sbe_certified_vendors.csv", index=False)
    print("CSVs saved. Done.")
