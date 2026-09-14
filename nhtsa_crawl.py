"""采集NHTSA vPIC公开车辆品牌API的真实数据。"""
from datetime import datetime, timezone
from pathlib import Path
import json, sqlite3
import pandas as pd
import requests

URL = "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/car?format=json"

def main():
    out = Path("real_data")
    out.mkdir(exist_ok=True)
    r = requests.get(URL, headers={"User-Agent": "car-data-collection/1.0"}, timeout=30)
    r.raise_for_status()
    payload = r.json()
    fetched_at = datetime.now(timezone.utc).isoformat()
    (out / "nhtsa_raw.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = payload.get("Results", [])
    df = pd.DataFrame(rows)
    rename = {"MakeId": "make_id", "MakeName": "make_name", "VehicleTypeId": "vehicle_type_id", "VehicleTypeName": "vehicle_type_name"}
    df = df.rename(columns=rename)
    df["source_url"] = URL
    df["fetched_at_utc"] = fetched_at
    df = df.drop_duplicates(subset=["make_id", "make_name", "vehicle_type_id"])
    df = df.dropna(subset=["make_id", "make_name"])
    df.to_csv(out / "nhtsa_car_makes_clean.csv", index=False, encoding="utf-8-sig")
    df.to_excel(out / "nhtsa_car_makes_clean.xlsx", index=False)
    with sqlite3.connect(out / "nhtsa_car_makes.db") as con:
        df.to_sql("vehicle_makes", con, if_exists="replace", index=False)
    (out / "source.md").write_text(f"来源：{URL}\n抓取时间（UTC）：{fetched_at}\n原始记录：{len(rows)}\n清洗后记录：{len(df)}\n", encoding="utf-8")
    print(f"真实来源抓取完成：原始 {len(rows)} 条，清洗后 {len(df)} 条，来源记录见 {out / 'source.md'}")

if __name__ == "__main__":
    main()
