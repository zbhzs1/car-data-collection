from __future__ import annotations
import argparse, logging, re, sqlite3, time
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup

FIELDS = ["model", "brand", "price_wan", "energy", "listed_month", "dealer_city", "source"]

def get_html(url: str, retries: int = 3) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; PersonalResearch/1.0)"}
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            return r.text
        except requests.RequestException as exc:
            logging.warning("request failed attempt=%s error=%s", attempt, exc)
            if attempt == retries:
                raise
            time.sleep(attempt)
    raise RuntimeError("unreachable")

def parse(html: str, source: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("article.car-card"):
        def txt(cls):
            node = card.select_one(f".{cls}")
            return node.get_text(" ", strip=True) if node else ""
        price = re.sub(r"[^0-9.]", "", txt("price"))
        rows.append({"model": txt("h2"), "brand": txt("brand"),
                     "price_wan": float(price) if price else None,
                     "energy": txt("energy"), "listed_month": txt("date"),
                     "dealer_city": txt("dealer"), "source": source})
    return pd.DataFrame(rows, columns=FIELDS)

def clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.drop_duplicates(subset=["model", "brand", "dealer_city"])
    out["brand"] = out["brand"].replace({"BYD": "比亚迪", "Tesla": "特斯拉"})
    out["listed_month"] = pd.to_datetime(out["listed_month"], errors="coerce").dt.strftime("%Y-%m")
    out["price_wan"] = pd.to_numeric(out["price_wan"], errors="coerce")
    out.loc[~out["price_wan"].between(1, 300), "price_wan"] = pd.NA
    out = out.dropna(subset=["model", "brand", "price_wan"])
    return out.reset_index(drop=True)

def save(df: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / "cars_clean.csv", index=False, encoding="utf-8-sig")
    df.to_excel(outdir / "cars.xlsx", index=False)
    with sqlite3.connect(outdir / "cars.db") as con:
        df.to_sql("car_info", con, if_exists="replace", index=False)

def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--html", type=Path)
    src.add_argument("--url")
    ap.add_argument("--output", type=Path, default=Path("outputs"))
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=args.output / "run.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    if args.html:
        html, source = args.html.read_text(encoding="utf-8"), str(args.html)
    else:
        html, source = get_html(args.url), args.url
    raw = parse(html, source)
    raw.to_csv(args.output / "cars_raw.csv", index=False, encoding="utf-8-sig")
    clean_df = clean(raw)
    save(clean_df, args.output)
    logging.info("raw=%s clean=%s", len(raw), len(clean_df))
    print(f"采集 {len(raw)} 条，清洗后保留 {len(clean_df)} 条；结果已写入 {args.output.resolve()}")

if __name__ == "__main__":
    main()
