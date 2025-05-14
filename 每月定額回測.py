# ------------------------------------------------------------
# 0050 每月定額 $10,000 回測（Streamlit 版）
# ------------------------------------------------------------
import streamlit as st

# ★ Streamlit 指令一定要先呼叫 set_page_config ★
st.set_page_config(page_title='0050 每月定額回測', layout='wide')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

# --- 中文字型註冊 --------------------------------------------
import matplotlib.font_manager as fm
from pathlib import Path

# 1) 指向 fonts 資料夾裡的字型檔
font_path = Path(__file__).parent / 'fonts' / 'NotoSansTC-Regular.otf'
# 2) 若找得到就註冊並指定；找不到只 print 提示，不呼叫 st.warning()
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Noto Sans TC'
else:
    print(f'⚠ 找不到字型檔 {font_path}，中文可能顯示為方框')

pd.set_option('mode.chained_assignment', None)   # 關閉 SettingWithCopy 警告


# ------------------------------------------------------------
def main():
    # 1. 讀資料 ------------------------------------------------
    stock    = pd.read_csv('0050歷史股價.csv', encoding='utf-8-sig')
    dividend = pd.read_csv('0050歷史股利.csv', encoding='utf-8-sig')

    # 2. 初始化變數 --------------------------------------------
    month_check = int(stock.loc[0, '年月日'].split('/')[1])
    stock['除息金額'] = 0

    cost, cum_dividend, shares = [0], [0], [0]
    market_value, date = [], []

    # 3. 主迴圈 -----------------------------------------------
    for i in range(len(stock)):
        close = stock.loc[i, '收盤價(元)']

        # ── 每月第一天買進 ──
        month = int(stock.loc[i, '年月日'].split('/')[1])
        if month == month_check:
            buy = int(10_000 / close)
            shares.append(shares[-1] + buy)
            cost.append(cost[-1] + buy * close)

            month_check = 1 if month_check == 12 else month_check + 1
        else:
            shares.append(shares[-1])
            cost.append(cost[-1])

        # ── 除息 ──
        if stock.loc[i, '年月日'] in dividend['除息日'].tolist():
            cash = float(dividend.loc[
                dividend['除息日'] == stock.loc[i, '年月日'], '息值(元)'])
            stock.loc[i, '除息金額'] = cash

        cum_dividend.append(cum_dividend[-1] + stock.loc[i, '除息金額'] * shares[-1])
        cost[-1] -= stock.loc[i, '除息金額'] * shares[-1]

        market_value.append(int(close * shares[-1]))
        y, m, _ = stock.loc[i, '年月日'].split('/')
        date.append(f'{y}/{m}')

    # 4. 後處理 ------------------------------------------------
    cost.pop(0); shares.pop(0); cum_dividend.pop(0)
    n = min(len(date), len(cost), len(cum_dividend), len(market_value))
    date, cost, cum_dividend, market_value = (
        date[:n], cost[:n], cum_dividend[:n], market_value[:n])

    # 5. 畫圖 --------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title('0050 每月定額 $10,000 回測', size=16)
    ax.set_xlabel('Date'); ax.set_ylabel('Value (NTD)')
    ax.xaxis.set_major_locator(MultipleLocator(12))
    for t in ax.get_xticklabels(): t.set_rotation(45)

    ax.plot(date, market_value, label='市值', color='indianred')
    ax.bar(date, cost, color='orange', label='成本')
    ax.bar(date, cum_dividend, bottom=cost, color='red', label='累積股利')

    ax.legend(loc='upper left'); ax.grid(linewidth=0.5)
    plt.tight_layout()

    return plt.gcf()


# ------------------------------------------------------------
# Streamlit 介面
# ------------------------------------------------------------
st.title('0050 ETF 每月定額回測')

if st.button('開始跑回測'):
    st.pyplot(main())
