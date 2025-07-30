import os
import pyarrow  
import pandas

'''
以下將 \data_csv資料夾內的 .csv檔案，讀出後忽略第一列的中文欄位資料，另存新檔為.parquet。
'''
import os
import pandas as pd
import pyarrow  # 確保已安裝 pyarrow

def csvToParquet():
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'data_csv')

    for filename in os.listdir(path):
        if filename.endswith('.csv'):
            fullpath = os.path.join(path, filename)
            print(f"找到 .csv 的檔案: {fullpath}")

            try:
                # 嘗試讀取 CSV（跳過第一列）
                df = pd.read_csv(fullpath, skiprows=1)
            except Exception as e:
                print(f"[錯誤] 無法讀取 CSV：{fullpath}\n原因：{e}")
                continue  # 跳過此檔案，繼續處理下一個

            try:
                # 構造 .parquet 檔案路徑
                parquet_filename = os.path.splitext(filename)[0] + '.parquet'
                parquet_path = os.path.join(path, parquet_filename)

                # 嘗試儲存為 Parquet
                df.to_parquet(parquet_path, engine="pyarrow", index=False)
                print(f"轉換完成 ➜ {parquet_path}")
            except Exception as e:
                print(f"[錯誤] 無法轉換為 Parquet：{fullpath}\n原因：{e}")
                continue

    print(f"轉換程序結束，來源資料夾：{path}")


'''
讀取csv檔，轉存成parquet檔
'''
import os
import pandas as pd
import pyarrow

def convert_single_csv_to_parquet(csv_path, skiprows=1, output_path=None):
    """
    將單一 CSV 檔轉換為 Parquet 檔。

    參數:
        csv_path (str): CSV 檔案的完整路徑
        skiprows (int): 要跳過的資料列數（預設為 1）
        output_path (str or None): 輸出的 Parquet 路徑。若為 None，則與 CSV 同資料夾同檔名。

    回傳:
        str or None: 成功時回傳 Parquet 檔路徑；失敗時回傳 None
    """
    try:
        # 讀取 CSV（跳過第一列）
        df = pd.read_csv(csv_path, skiprows=skiprows)
    except Exception as e:
        print(f"[錯誤] 讀取 CSV 失敗：{csv_path}\n原因：{e}")
        return None

    try:
        # 建立輸出路徑（若未指定）
        if output_path is None:
            base, _ = os.path.splitext(csv_path)
            output_path = base + '.parquet'

        # 儲存為 Parquet
        df.to_parquet(output_path, engine="pyarrow", index=False)
        print(f"✅ 轉換完成 ➜ {output_path}")
        return output_path
    except Exception as e:
        print(f"[錯誤] 無法寫入 Parquet：{output_path}\n原因：{e}")
        return None


'''
讀取parquet檔，進行日期的修正。
'''
import pandas as pd
import numpy as np
import re

def fix_date_columns_custom(parquet_path, fill_strategy='mode'):
    """
    修正 parquet 檔案中所有包含 'date', 'day', 'year' 的欄位。
    - 排除含英文字母的日期資料
    - 若只有年月，補上日為01
    - 民國年、兩位數年份等轉為西元年
    - 無法解析者轉為 NaT，並用該欄有效資料補值

    fill_strategy 可為 'mode', 'median', 'mean'
    """
    df = pd.read_parquet(parquet_path)

    # 找出包含 year、date 或 day 的欄位
    date_cols = [col for col in df.columns if any(k in col.lower() for k in ['date', 'day', 'year'])]

    if not date_cols:
        print("❌ 沒有找到任何包含 'date', 'day', 'year' 的欄位。")
        return df

    print(f"🗂️ 找到日期欄位: {date_cols}")

    for col in date_cols:
        original = df[col].astype(str)

        # 1. 移除含英文字母的值
        original = original.where(~original.str.contains('[a-zA-Z]', na=False))

        # 2. 民國年轉換（如 110/05/01 → 2021/05/01）
        original = original.str.replace(r'^(\d{2,3})[./-](\d{1,2})[./-](\d{1,2})$', 
                                        lambda m: f"{int(m.group(1)) + 1911}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", 
                                        regex=True)

        # 3. 只有年月 → 補上 -01
        original = original.str.replace(r'^(\d{4})[./-](\d{1,2})$', r'\1-\2-01', regex=True)

        # 4. 兩位數年份處理（假設 20xx）
        original = original.str.replace(r'^(\d{2})[./-](\d{1,2})[./-](\d{1,2})$', 
                                        lambda m: f"20{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" 
                                        if int(m.group(1)) < 30 else 
                                        f"19{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", 
                                        regex=True)

        # 5. 轉換為 datetime，無法解析為 NaT
        df[col] = pd.to_datetime(original, format='%Y-%m-%d',errors='coerce')

        # 6. 補值策略
        if fill_strategy == 'mode':
            fill_value = df[col].mode(dropna=True)
            if not fill_value.empty:
                df[col] = df[col].fillna(fill_value.iloc[0])
        elif fill_strategy == 'mean':
            fill_value = df[col].dropna().mean()
            df[col] = df[col].fillna(fill_value)
        elif fill_strategy == 'median':
            fill_value = df[col].dropna().median()
            df[col] = df[col].fillna(fill_value)
        else:
            print(f"⚠️ 不支援的 fill_strategy: {fill_strategy}，將跳過補值。")

    return df





# import os
# from your_module import convert_single_csv_to_parquet  # 如果函式在其他檔案中

if __name__ == '__main__':
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'data_csv')

    for filename in os.listdir(path):
        if filename.endswith('.csv'):
            fullpath = os.path.join(path, filename)
            print(f"找到 .csv 的檔案: {fullpath}")

            try:
                result = convert_single_csv_to_parquet(
                    csv_path=fullpath,
                    skiprows=1,
                    output_path=None
                )
                if result:
                    print(f"✅ 成功轉換：{result}")
                    fix_date_columns_custom(result)
                else:
                    print(f"⚠️ 轉換失敗：{fullpath}")

            except Exception as e:
                print(f"❌ 發生例外錯誤，無法處理檔案：{fullpath}\n原因：{e}")
