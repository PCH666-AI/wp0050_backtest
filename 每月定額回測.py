# ------------------------------------------------------------
# 0050 每月定額 $10,000 回測（Streamlit 版）
# ------------------------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

# --- 新增：中文字型註冊 ---------------------------------------
import matplotlib.font_manager as fm
from pathlib import Path

font_path = Path(__file__).resolve().parent / 'fonts' / 'NotoSansTC-Regular.otf'  # ← 副檔名若是 .ttf 就改掉
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Noto Sans TC'
else:
    st.warning(f'找不到字型檔 {font_path}，中文可能顯示為方框')

# ------------------------------------------------------------
pd.set_option('mode.chained_assignment', None)   # 關閉 SettingWithCopy 警告


def main():
    # 1. 讀資料 ------------------------------------------------
    stock    = pd.read_csv('0050歷史股價.csv', encoding='utf-8-sig', low_memory=False)
    dividend = pd.read_csv('0050歷史股利.csv', encoding='utf-8-sig', low_memory=False)

    # 2. 初始化變數 --------------------------------------------
    max_price = stock.loc[0, '收盤價(元)']
    month_check = int(stock.loc[0, '年月日'].split('/')[1])   # 判斷是否為當月第一筆
    stock['除息金額'] = 0

    cost, cum_dividend, shares = [0], [0], [0]
    market_value, date = [], []

    # 3. 主迴圈：逐日模擬 --------------------------------------
    for i in range(len(stock)):
        close = stock.loc[i, '收盤價(元)']

        # ── 每月第一天買進 NT$10,000 ──
        month = int(stock.loc[i, '年月日'].split('/')[1])
        if month == month_check:
            buy_shares = int(10_000 / close)
            shares.append(shares[-1] + buy_shares)
            cost.append(cost[-1] + int(buy_shares * close))

            month_check += 1
            if month_check == 13:
                month_check = 1
        else:
            # 非買進日 → 持股與成本沿用前一天
            shares.append(shares[-1])
            cost.append(cost[-1])

        # ── 除息 ──
        if stock.loc[i, '年月日'] in dividend['除息日'].tolist():
            cash = float(dividend.loc[
                dividend['除息日'] == stock.loc[i, '年月日'], '息值(元)'])
            stock.loc[i, '除息金額'] = cash

        cum_dividend.append(cum_dividend[-1] + stock.loc[i, '除息金額'] * shares[-1])
        cost[-1] -= stock.loc[i, '除息金額'] * shares[-1]      # 股利直接抵成本

        # ── 市值、日期 ──
        market_value.append(int(close * shares[-1]))
        y, m, _ = stock.loc[i, '年月日'].split('/')
        date.append(f'{y}/{m}')

    # 4. 後處理：移掉開頭 0，並確保長度一致 --------------------
    cost.pop(0); shares.pop(0); cum_dividend.pop(0)

    min_len = min(len(date), len(cost), len(cum_dividend), len(market_value))
    date, cost        = date[:min_len],        cost[:min_len]
    cum_dividend      = cum_dividend[:min_len]
    market_value      = market_value[:min_len]

    # 5. 畫圖 --------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.set_title('0050 每月定額 $10,000 回測', size=16)
    ax1.set_xlabel('Date'); ax1.set_ylabel('Value (NTD)')
    ax1.xaxis.set_major_locator(MultipleLocator(12))
    for tick in ax1.get_xticklabels():
        tick.set_rotation(45)

    ax1.plot(date, market_value, label='市值', color='indianred')
    ax1.bar(date, cost, color='orange', label='成本')
    ax1.bar(date, cum_dividend, bottom=cost, color='red', label='累積股利')

    ax1.legend(loc='upper left'); ax1.grid(linewidth=0.5)
    plt.tight_layout()

    return plt.gcf()   # 把圖傳給 Streamlit


# ------------------------------------------------------------
# Streamlit 入口
# ------------------------------------------------------------
st.set_page_config(page_title='0050 每月定額回測', layout='wide')
st.title('0050 ETF 每月定額回測')

if st.button('開始跑回測'):
    chart = main()
    st.pyplot(chart)
