import os
import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pyarrow

# --- 地址正規化工具 ---
OLD_TO_NEW_CITY = {
    '台北縣': '新北市',
    '台中縣': '臺中市',
    '台南縣': '臺南市',
    '高雄縣': '高雄市',
    '台北市': '臺北市',
    '台中市': '臺中市',
    '台南市': '臺南市',
}

def normalize_address(addr):
    addr = str(addr).strip()
    for old, new in OLD_TO_NEW_CITY.items():
        addr = addr.replace(old, new)
    addr = addr.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    addr = re.sub(r'(\d+)\s+(?=[巷弄樓])', r'\1', addr)
    addr = re.sub(r'([段路街道])\s+', r'\1', addr)
    addr = re.sub(r'(\d)\s+(\d+號)', r'\1\2', addr)  # 修復 2 1號 → 21號
    addr = re.sub(r'(?<=[^\s])(\d+號)', r' \1', addr)  # 號前補空白
    return addr

# --- 加入經緯度 ---
def append_geocode(df, address_col='address'):
    geolocator = Nominatim(user_agent="my_geocoder")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    df[address_col] = df[address_col].apply(normalize_address)
    df['location'] = df[address_col].apply(geocode)
    df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
    df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else None)
    df.drop(columns=['location'], inplace=True)
    return df

# --- 日期正規化工具 ---
def fix_date_columns_custom(parquet_path, fill_strategy='mode'):
    df = pd.read_parquet(parquet_path)
    date_cols = [col for col in df.columns if any(k in col.lower() for k in ['date', 'day', 'year'])]
    if not date_cols:
        print("❌ 沒有找到任何包含日期的欄位。")
        return df

    print(f"🗂️ 處理日期欄位: {date_cols}")

    for col in date_cols:
        original = df[col].astype(str)
        original = original.where(~original.str.contains('[a-zA-Z]', na=False))
        original = original.str.replace(r'^(\d{2,3})[./-](\d{1,2})[./-](\d{1,2})$', 
                                        lambda m: f"{int(m.group(1)) + 1911}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", 
                                        regex=True)
        original = original.str.replace(r'^(\d{4})[./-](\d{1,2})$', r'\1-\2-01', regex=True)
        original = original.str.replace(r'^(\d{2})[./-](\d{1,2})[./-](\d{1,2})$', 
                                        lambda m: f"20{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" 
                                        if int(m.group(1)) < 30 else 
                                        f"19{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", 
                                        regex=True)
        df[col] = pd.to_datetime(original, format='%Y-%m-%d', errors='coerce')

        if fill_strategy == 'mode':
            fill_value = df[col].mode(dropna=True)
            if not fill_value.empty:
                df[col] = df[col].fillna(fill_value.iloc[0])
        elif fill_strategy == 'mean':
            df[col] = df[col].fillna(df[col].dropna().mean())
        elif fill_strategy == 'median':
            df[col] = df[col].fillna(df[col].dropna().median())
    return df

# --- 主程序 ---
if __name__ == '__main__':
    base_path = os.path.dirname(__file__)
    csv_folder = os.path.join(base_path, 'data_csv')

    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            csv_path = os.path.join(csv_folder, filename)
            print(f"🔍 處理檔案: {csv_path}")

            try:
                # 讀取 CSV
                df = pd.read_csv(csv_path, skiprows=1)

                # 如果有地址欄位，進行正規化與地理編碼
                if 'address' in df.columns:
                    df = append_geocode(df)

                # 儲存為 parquet
                parquet_path = os.path.splitext(csv_path)[0] + '.parquet'
                df.to_parquet(parquet_path, engine="pyarrow", index=False)
                print(f"✅ 已轉為 parquet: {parquet_path}")

                # 修正 parquet 檔中的日期欄位
                df_fixed = fix_date_columns_custom(parquet_path)
                df_fixed.to_parquet(parquet_path, engine="pyarrow", index=False)
                print(f"✅ 日期修正完成：{parquet_path}")

            except Exception as e:
                print(f"❌ 發生錯誤：{filename}\n原因：{e}")
