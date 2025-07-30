'''
將地址進行正規化後，查找經緯度訊息。
'''

import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# 老舊地名轉換對照表
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
    addr = addr.strip()
    for old, new in OLD_TO_NEW_CITY.items():
        addr = addr.replace(old, new)
    addr = addr.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    addr = re.sub(r'(\d+)\s+(?=[巷弄樓])', r'\1', addr)
    addr = re.sub(r'([段路街道])\s+', r'\1', addr)
    addr = re.sub(r'(\d)\s+(\d+號)', r'\1\2', addr)  # 修復 2 1號 → 21號
    # addr = re.sub(r'(?<=[^\s])(\d+號)', r' \1', addr)  # 號前補空白
    return addr

def simplify_house_number_for_query(addr):
    """
    將「正義路9-2-1號」變為「正義路 9號」，確保「路」與「號碼」之間有空白。
    """
    # 先簡化門牌為主號碼
    addr = re.sub(r'(\d+)-[\d\-]+號', r'\1號', addr)

    # 確保「路」或其他街道類詞後與號碼之間有空白（若沒有）
    addr = re.sub(r'(路|街|大道|巷|弄|段)(\d+號)', r'\1 \2', addr)

    return addr


if __name__ == '__main__':
    df = pd.DataFrame({
        '地址': [
            '台灣 臺中市中區自由路二段 9-7-2號',
            '台中市沙鹿區福成路130巷 21號',
            '台中縣霧峰區新生路 7號',
            '台北縣板橋區文化路一段 188號',
            '台南市東區東門路一段 2號',
            '臺北市大安區信義路三段 99-3-1號'
        ]
    })

    # 正規化地址
    df['地址'] = df['地址'].apply(normalize_address)

    # 複製欄位作為查詢用地址
    df['地址_查詢用'] = df['地址'].apply(simplify_house_number_for_query)

    # 初始化地理編碼器
    geolocator = Nominatim(user_agent="my_geocoder")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # 使用簡化地址查詢經緯度
    df['location'] = df['地址_查詢用'].apply(geocode)
    df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
    df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else None)
    df.drop(columns=['location'], inplace=True)

    print(df)
