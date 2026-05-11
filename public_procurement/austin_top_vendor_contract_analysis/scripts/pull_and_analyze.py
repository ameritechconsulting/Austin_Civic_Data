"""
Austin Top Vendor Contract Analysis
Sources:
  - Contracts (professional services):      data.austintexas.gov/resource/84ih-p28j
  - Purchase Orders (goods/commodities):    data.austintexas.gov/resource/3ebq-e9iz
"""

import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

BASE   = Path(__file__).resolve().parents[1]
RAW    = BASE / "data" / "raw"
PROC   = BASE / "data" / "processed"
OUT    = BASE / "outputs" / "final"
for d in [RAW, PROC, OUT]:
    d.mkdir(parents=True, exist_ok=True)

SOCRATA = "https://data.austintexas.gov/resource"

# ── 1. CONTRACTS (professional services, engineering, construction) ─────────

def fetch_contracts(limit=500):
    url = f"{SOCRATA}/84ih-p28j.json"
    params = {
        "$limit": limit,
        "$where": "ma_prch_lmt_am IS NOT NULL",
        "$order": "ma_prch_lmt_am DESC",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df.to_csv(RAW / "contracts_raw.csv", index=False)
    print(f"Contracts fetched: {len(df)} rows")
    return df


def process_contracts(df):
    df = df.copy()
    numeric = ["ma_prch_lmt_am", "ma_itd_ord_am", "ma_do_rfed_am"]
    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Normalize vendor names (strip whitespace, title-case)
    df["vendor"] = df["lgl_nm"].str.strip().str.upper()

    # Aggregate by vendor
    agg = (
        df.groupby("vendor")
        .agg(
            total_authorized=("ma_prch_lmt_am", "sum"),
            total_ordered=("ma_itd_ord_am", "sum"),
            num_contracts=("ma_prch_lmt_am", "count"),
            categories=("cat_dscr", lambda x: " | ".join(x.dropna().unique()[:3])),
        )
        .reset_index()
        .sort_values("total_authorized", ascending=False)
    )

    # Utilization rate: how much of the authorized amount is actually ordered
    agg["utilization_pct"] = (agg["total_ordered"] / agg["total_authorized"] * 100).round(1)

    agg.to_csv(PROC / "contracts_by_vendor.csv", index=False)
    return agg


# ── 2. PURCHASE ORDERS (goods / commodities) ────────────────────────────────

def fetch_purchase_orders(limit=200):
    url = f"{SOCRATA}/3ebq-e9iz.json"
    params = {
        "$select": "lgl_nm, sum(itm_tot_am) as total_spend, count(*) as num_orders",
        "$group": "lgl_nm",
        "$order": "total_spend DESC",
        "$limit": limit,
        "$where": "itm_tot_am IS NOT NULL",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df.to_csv(RAW / "purchase_orders_raw.csv", index=False)
    print(f"Purchase orders fetched: {len(df)} vendor groups")
    return df


def process_purchase_orders(df):
    df = df.copy()
    df["total_spend"] = pd.to_numeric(df["total_spend"], errors="coerce").fillna(0)
    df["num_orders"]  = pd.to_numeric(df["num_orders"],  errors="coerce").fillna(0).astype(int)
    df["vendor"]      = df["lgl_nm"].str.strip().str.upper()
    df = df.sort_values("total_spend", ascending=False).reset_index(drop=True)
    df.to_csv(PROC / "purchase_orders_by_vendor.csv", index=False)
    return df


# ── 3. COMBINED TOP 50 ──────────────────────────────────────────────────────

def build_top50(contracts_agg, po_agg):
    # Tag each source
    contracts_agg["source"] = "Professional Services / Contracts"
    po_agg = po_agg.copy().rename(columns={"total_spend": "total_authorized"})
    po_agg["total_ordered"] = po_agg["total_authorized"]
    po_agg["num_contracts"] = po_agg["num_orders"]
    po_agg["utilization_pct"] = 100.0
    po_agg["categories"] = "Goods / Commodities"
    po_agg["source"] = "Purchase Orders (Goods)"

    combined = pd.concat(
        [
            contracts_agg[["vendor", "total_authorized", "total_ordered",
                            "num_contracts", "utilization_pct", "categories", "source"]],
            po_agg[["vendor", "total_authorized", "total_ordered",
                    "num_contracts", "utilization_pct", "categories", "source"]],
        ],
        ignore_index=True,
    )

    # De-duplicate: if a vendor appears in both, keep separate rows (they are different contract types)
    top50 = combined.sort_values("total_authorized", ascending=False).head(50).reset_index(drop=True)
    top50.index += 1
    top50.to_csv(OUT / "top50_vendors_combined.csv")
    return top50


# ── 4. REPEAT VENDOR ANALYSIS ───────────────────────────────────────────────

def repeat_vendor_analysis(contracts_agg):
    repeat = contracts_agg[contracts_agg["num_contracts"] >= 3].sort_values(
        "num_contracts", ascending=False
    )
    repeat.to_csv(PROC / "repeat_vendors_3plus_contracts.csv", index=False)
    return repeat


# ── 5. PRINT REPORT ─────────────────────────────────────────────────────────

def print_report(top50, repeat, contracts_agg, po_agg):
    print("\n" + "="*80)
    print("CITY OF AUSTIN — TOP 50 VENDOR CONTRACT ANALYSIS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    print("="*80)

    print(f"\nTotal contract spend analyzed (professional services): "
          f"${contracts_agg['total_authorized'].sum():,.0f}")
    po_total = po_agg["total_spend"].sum() if "total_spend" in po_agg.columns else po_agg["total_authorized"].sum()
    print(f"Total purchase order spend analyzed (goods):           "
          f"${po_total:,.0f}")

    print("\n── TOP 50 VENDORS BY AUTHORIZED CONTRACT VALUE ──────────────────────────────")
    print(f"{'#':>3}  {'Vendor':<50} {'Authorized':>16}  {'Contracts':>9}  Source")
    print("-"*100)
    for i, row in top50.iterrows():
        print(f"{i:>3}. {row['vendor'][:49]:<50} ${row['total_authorized']:>15,.0f}"
              f"  {row['num_contracts']:>9}  {row['source']}")

    print("\n── TOP REPEAT VENDORS (3+ Contracts) ────────────────────────────────────────")
    print(f"{'#':>3}  {'Vendor':<50} {'Contracts':>9}  {'Total Auth':>16}  {'Utilization':>11}")
    print("-"*95)
    for i, (_, row) in enumerate(repeat.head(20).iterrows(), 1):
        print(f"{i:>3}. {row['vendor'][:49]:<50} {row['num_contracts']:>9}  "
              f"${row['total_authorized']:>15,.0f}  {row['utilization_pct']:>10.1f}%")

    print("\n── CONCENTRATION ANALYSIS ───────────────────────────────────────────────────")
    top5_share  = contracts_agg.head(5)["total_authorized"].sum() / contracts_agg["total_authorized"].sum() * 100
    top10_share = contracts_agg.head(10)["total_authorized"].sum() / contracts_agg["total_authorized"].sum() * 100
    print(f"  Top 5 vendors  = {top5_share:.1f}% of total contract value")
    print(f"  Top 10 vendors = {top10_share:.1f}% of total contract value")

    print("\nOutput files saved to outputs/final/ and data/processed/\n")


# ── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching City of Austin contract data...")
    contracts_raw = fetch_contracts(limit=500)
    contracts_agg = process_contracts(contracts_raw)

    print("Fetching City of Austin purchase order data...")
    po_raw = fetch_purchase_orders(limit=200)
    po_agg = process_purchase_orders(po_raw)

    top50  = build_top50(contracts_agg, po_agg)
    repeat = repeat_vendor_analysis(contracts_agg)

    print_report(top50, repeat, contracts_agg, po_agg)
    print("Done.")
