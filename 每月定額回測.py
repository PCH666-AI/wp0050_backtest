# 1. 匯入套件 ----------------------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

pd.set_option('mode.chained_assignment', None)   # 關掉 chained-assignment 警告


# 2. 封裝主程式 --------------------------------------------------------
def main():
    # --- 讀取資料（同資料夾即可） ------------------------------------
    stock    = pd.read_csv('0050歷史股價.csv', encoding='utf-8-sig',
                           low_memory=False, index_col=False)
    dividend = pd.read_csv('0050歷史股利.csv', encoding='utf-8-sig',
                           low_memory=False, index_col=False)

    # --- 初始化變數 ---------------------------------------------------
    max_price = stock.loc[0, '收盤價(元)']
    dd = 0

    cost          = [0]
    cum_dividend  = [0]
    shares        = [0]
    market_value  = []
    stock_price   = []
    date          = []
    count = 0

    # 取第一筆日期的「月」作為買進月份基準
    month_check = int(stock.loc[0, '年月日'].split('/')[1])

    # 新增欄位：除息金額
    stock['除息金額'] = 0

    # --- 主迴圈：逐天計算 --------------------------------------------
    for i in range(len(stock)):

        # (1) 更新 Draw-down
        close_i = stock.loc[i, '收盤價(元)']
        if close_i >= max_price:
            max_price = close_i
            dd = 0
        else:
            dd = close_i / max_price

        # (2) 記錄股價
        stock_price.append(close_i)

        # (3) 取當月
        month = int(stock.loc[i, '年月日'].split('/')[1])

        # (4) 每月第一天買進 10,000 元
        if month == month_check:
            buy_shares = int(10_000 / close_i)             # 可買股數
            shares.append(buy_shares + shares[-1])         # 累計持股
            cost.append(int(close_i * buy_shares) + cost[-1])
            month_check += 1
            if month_check == 13:
                month_check = 1
        else:  # 非買進日 → 值沿用前一天
            cost.append(cost[-1])
            shares.append(shares[-1])

        # (5) 除息
        if stock.loc[i, '年月日'] in dividend['除息日'].tolist():
            money = float(dividend.loc[
                dividend['除息日'] == stock.loc[i, '年月日'], '息值(元)'])
            stock.loc[i, '除息金額'] = money

        # (6) 累積股利、市值、日期
        cum_dividend.append(stock.loc[i, '除息金額'] * shares[-1]   +
                            cum_dividend[-1])
        cost[-1] -= stock.loc[i, '除息金額'] * shares[-1]           # 股利抵成本
        market_value.append(int(close_i * shares[-1]))
        date.append('/'.join(stock.loc[i, '年月日'].split('/')[:2])) # 只留 年/月

        count += 1

    # --- 後處理：移掉開頭 0 並對齊長度 -------------------------------
    cost.pop(0)
    shares.pop(0)
    cum_dividend.pop(0)

    min_len = min(len(date), len(cost), len(cum_dividend), len(market_value))
    date          = date[:min_len]
    cost          = cost[:min_len]
    cum_dividend  = cum_dividend[:min_len]
    market_value  = market_value[:min_len]

    # --- 繪圖 --------------------------------------------------------
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.set_title('0050 Regular Saving Plan $10,000 backtesting', size=16)
    ax1.set_xlabel('Date'); ax1.set_ylabel('Value (NTD)')
    ax1.xaxis.set_major_locator(MultipleLocator(12))
    for tick in ax1.get_xticklabels(): tick.set_rotation(45)

    ax1.plot(date, market_value, label='市值', color='indianred')
    ax1.bar(date, cost, color='orange', label='成本')
    ax1.bar(date, cum_dividend, bottom=cost,
            color='red', label='累積股利')

    ax1.legend(loc='upper left'); ax1.grid(linewidth=0.5)
    plt.tight_layout()

    return plt.gcf()     # 將圖表物件回傳給 Streamlit


# 3. Streamlit 入口 ----------------------------------------------------
st.set_page_config(page_title='0050 Regular Saving Plan', layout='wide')
st.title('0050 ETF 每月定額回測')

if st.button('開始跑回測'):
    chart = main()
    st.pyplot(chart)
