
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

if __name__ == '__main__':

    # 範例資料
    df = pd.DataFrame({
        '地址': [
            '台中市沙鹿區中清路八段 496號',
            '台中市沙鹿區福成路130巷 21號',
            '台中市霧峰區新生路 7號'
        ]
    })

    # 初始化地理編碼器
    geolocator = (user_agent="my_geocoder")

    # 加上速率限制器（避免被封鎖）
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # 新增欄位：經緯度
    df['location'] = df['地址'].apply(geocode)
    df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
    df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else None)

    # 移除中間欄位
    df.drop(columns=['location'], inplace=True)

    print(df)
    

#     import os
# import re
# import pandas as pd
# from geopy.geocoders import Nominatim
# from geopy.extra.rate_limiter import RateLimiter

# # =======================
# # 📌 基本設定
# # =======================

# ADDRESS_REPLACE_MAP = {
#     "台北縣": "新北市", "臺北縣": "新北市",
#     "台中縣": "台中市", "臺中縣": "台中市",
#     "台南縣": "台南市", "臺南縣": "台南市",
#     "高雄縣": "高雄市",
#     "臺": "台",
#     "　": "", "–": "-",
#     "（": "(", "）": ")"
# }

# FULLWIDTH_DIGIT_MAP = str.maketrans('０１２３４５６７８９', '0123456789')
# ADDRESS_UNIT_PATTERN = re.compile(r'(縣|市|區|鄉|鎮|村|里|路|街|段|巷|弄|號|樓|號之\d+|號-\d+|樓之\d+)')

# # 初始化 geopy + rate limiter（避免查詢太快被 ban）
# geolocator = Nominatim(user_agent="geo_powerbi")
# geocode = RateLimiter(geolocator.geocode, min_delay_seconds=5)


# # =======================
# # 🧰 工具函數
# # =======================

# def normalize_tw_address(addr, separate_parts=True):
#     if not isinstance(addr, str) or not addr.strip():
#         return None

#     addr = addr.strip().translate(FULLWIDTH_DIGIT_MAP)

#     # 替換常見地名與符號
#     for old, new in ADDRESS_REPLACE_MAP.items():
#         addr = addr.replace(old, new)

#     addr = re.sub(r'^\d{3,5}', '', addr).strip()  # 移除郵遞區號
#     if not addr.startswith("台灣"):
#         addr = "台灣 " + addr
#     addr = re.sub(r'[，。．、\s]+$', '', addr)     # 移除結尾標點
#     addr = re.sub(r'\s+', '', addr)              # 移除多餘空白

#     if separate_parts:
#         addr = ADDRESS_UNIT_PATTERN.sub(r'\1 ', addr)
#         addr = re.sub(r'\s+', ' ', addr).strip()

#     return addr


# def try_fix_minguo_with_letter(val):
#     if pd.isna(val):
#         return val

#     s = str(val).lower()
#     char_map = {'a': '1', 'b': '2', 'c': '3', 'd': '4', 'e': '5',
#                 'f': '6', 'g': '7', 'h': '8', 'i': '9', 'o': '0', 'l': '1'}
#     s_fixed = ''.join(char_map.get(c, c) for c in s)

#     if re.fullmatch(r'\d{7}', s_fixed):
#         try:
#             year = int(s_fixed[:3]) + 1911
#             month = int(s_fixed[3:5])
#             day = int(s_fixed[5:7])
#             return f"{year:04d}-{month:02d}-{day:02d}"
#         except:
#             return None
#     return None


# # =======================
# # 📦 檔案處理主功能
# # =======================

# def convert_single_csv_to_parquet(csv_path, skiprows=1, output_path=None):
#     try:
#         df = pd.read_csv(csv_path, skiprows=skiprows)
#     except Exception as e:
#         print(f"[錯誤] 讀取 CSV 失敗：{csv_path}\n原因：{e}")
#         return None

#     if output_path is None:
#         base, _ = os.path.splitext(csv_path)
#         output_path = base + '.parquet'

#     try:
#         df.to_parquet(output_path, engine="pyarrow", index=False)
#         print(f"✅ 轉換完成 ➜ {output_path}")
#         return output_path
#     except Exception as e:
#         print(f"[錯誤] 無法寫入 Parquet：{output_path}\n原因：{e}")
#         return None


# def fix_date_columns_custom(parquet_path, fill_strategy='mode', save=False, overwrite=False):
#     try:
#         df = pd.read_parquet(parquet_path)
#     except Exception as e:
#         print(f"❌ 讀取 parquet 檔案失敗: {parquet_path}\n{e}")
#         return None

#     date_cols = [col for col in df.columns if any(k in col.lower() for k in ['date', 'day', 'year'])]
#     if not date_cols:
#         print("❌ 沒找到任何日期相關欄位。")
#         return df

#     print(f"🗂️ 找到日期欄位: {date_cols}")

#     for col in date_cols:
#         try:
#             print(f"\n🔧 處理欄位: {col}")
#             original = df[col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

#             fix_mask = original.str.contains(r'[a-zA-Z]', na=False)
#             original.loc[fix_mask] = original[fix_mask].apply(try_fix_minguo_with_letter)

#             mask = original.str.match(r'^\d{10,}$').fillna(False)
#             original = original.where(~mask)

#             # 民國轉換與格式清洗
#             original = original.str.replace(r'^(\d{3})(\d{2})(\d{2})$',
#                 lambda m: f"{int(m.group(1)) + 1911}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", regex=True)

#             original = original.str.replace(r'^(\d{2})(\d{2})(\d{2})$',
#                 lambda m: f"{int(m.group(1)) + 1911}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", regex=True)

#             original = original.str.replace(r'^(\d{2,3})[./-](\d{1,2})[./-](\d{1,2})$',
#                 lambda m: f"{int(m.group(1)) + 1911}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", regex=True)

#             original = original.str.replace(r'^(\d{4})[./-](\d{1,2})$', r'\1-\2-01', regex=True)

#             original = original.str.replace(r'^(\d{2})(\d{2})$',
#                 lambda m: f"{int(m.group(1)) + 1911}-{int(m.group(2)):02d}-01", regex=True)

#             original = original.str.replace(r'^(\d{2})[./-](\d{1,2})[./-](\d{1,2})$',
#                 lambda m: (f"20{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
#                            if int(m.group(1)) < 30 else
#                            f"19{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"), regex=True)

#             df[col] = pd.to_datetime(original, format='%Y-%m-%d', errors='coerce')

#         except Exception as e:
#             print(f"❌ 處理欄位 {col} 發生錯誤：\n{e}")

#     if save:
#         try:
#             output_path = parquet_path if overwrite else parquet_path.replace('.parquet', '_fixed.parquet')
#             df.to_parquet(output_path, index=False)
#             print(f"💾 已儲存修正檔至：{output_path}")
#         except Exception as e:
#             print(f"❌ 儲存檔案失敗：\n{e}")

#     return df


# def add_lat_lon_from_address(df, address_column='address'):
#     if address_column not in df.columns:
#         print(f"⚠️ 欄位 {address_column} 不存在，跳過經緯度處理。")
#         return df

#     print(f"🌐 開始經緯度查詢（欄位：{address_column}）")

#     def safe_geocode(addr):
#         if pd.isna(addr) or not str(addr).strip():
#             return None
#         norm_addr = normalize_tw_address(addr)
#         try:
#             location = geocode(norm_addr)
#             if not location:
#                 print(f"❗ 查無座標：{norm_addr}")
#             return location
#         except Exception as e:
#             print(f"❌ 查詢失敗：{norm_addr}，原因：{e}")
#             return None

#     locations = df[address_column].apply(safe_geocode)
#     df['latitude'] = locations.apply(lambda loc: loc.latitude if loc else None)
#     df['longitude'] = locations.apply(lambda loc: loc.longitude if loc else None)

#     found = df['latitude'].notna().sum()
#     print(f"✅ 經緯度取得率：{found}/{len(df)}（{found / len(df):.1%}）")

#     return df


# # =======================
# # 🚀 主程式入口
# # =======================

# if __name__ == '__main__':
#     base_path = os.path.dirname(__file__)
#     csv_folder = os.path.join(base_path, 'data_csv')

#     for filename in os.listdir(csv_folder):
#         if filename.endswith('.csv'):
#             full_csv_path = os.path.join(csv_folder, filename)
#             print(f"\n📁 處理檔案：{full_csv_path}")

#             parquet_path = convert_single_csv_to_parquet(full_csv_path, skiprows=1)

#             if parquet_path:
#                 df = fix_date_columns_custom(parquet_path, fill_strategy='none', save=False, overwrite=False)
#                 df = add_lat_lon_from_address(df, address_column='address')

#                 final_output = parquet_path.replace('.parquet', '_final.parquet')
#                 df.to_parquet(final_output, index=False)
#                 print(f"✅ 最終檔案儲存至：{final_output}")
#             else:
#                 print(f"⚠️ 無法處理檔案：{full_csv_path}")

