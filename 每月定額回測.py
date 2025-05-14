import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

pd.set_option('mode.chained_assignment', None)

# -------------------------------------------------
def main():
    # 讀檔（同資料夾，所以用相對路徑）
    stock    = pd.read_csv('0050歷史股價.csv', encoding='utf-8-sig')
    dividend = pd.read_csv('0050歷史股利.csv', encoding='utf-8-sig')

    # ---------- 初始化 ----------
    max_price = stock.loc[0, '收盤價(元)']
    dd = 0

    true_cost = [0]; true_cost_reduce = [0]; true_cost_increase = [0]
    cost = [0]; cost_reduce = [0]; cost_increase = [0]; cost_reinvest = [0]
    cum_dividend = [0]; cum_dividend_reduce = [0]; cum_dividend_increase = [0]
    shares = [0]; shares_reduce = [0]; shares_increase = [0]; shares_reinvest = [0]
    market_value = []; market_value_reduce = []; market_value_increase = []
    stock_price = []; date = []

    month_check = int(stock.loc[0, '年月日'].split('/')[1])
    stock['除息金額'] = 0
    # ---------- 主迴圈 ----------
    for i in range(len(stock)):
        # Draw-down 判斷
        if stock.loc[i, '收盤價(元)'] >= max_price:
            max_price = stock.loc[i, '收盤價(元)']
            dd = 0
        else:
            dd = stock.loc[i, '收盤價(元)'] / max_price

        # 每月定額 & 跌深調整
        if dd == 0:
            quota_reduce  = 10000
            quota_increase = 10000
        elif dd < 0.8:
            quota_reduce  = 6000
            quota_increase = 14000

        month = int(stock.loc[i, '年月日'].split('/')[1])
        if month == month_check:                       # 每月第一天
            shares.append(int(10000 / stock.loc[i, '收盤價(元)']) + shares[-1])
            shares_reduce.append(int(quota_reduce / stock.loc[i, '收盤價(元)']) + shares_reduce[-1])
            shares_increase.append(int(quota_increase / stock.loc[i, '收盤價(元)']) + shares_increase[-1])
            shares_reinvest.append(int(10000 / stock.loc[i, '收盤價(元)']) + shares_reinvest[-1])

            true_cost.append(int(stock.loc[i, '收盤價(元)'] * int(10000 / stock.loc[i, '收盤價(元)'])) + cost[-1])
            true_cost_reduce.append(int(stock.loc[i, '收盤價(元)'] * int(quota_reduce / stock.loc[i, '收盤價(元)'])) + cost_reduce[-1])
            true_cost_increase.append(int(stock.loc[i, '收盤價(元)'] * int(quota_increase / stock.loc[i, '收盤價(元)'])) + cost_increase[-1])

            cost.append(int(stock.loc[i, '收盤價(元)'] * int(10000 / stock.loc[i, '收盤價(元)'])) + cost[-1])
            cost_reduce.append(int(stock.loc[i, '收盤價(元)'] * int(quota_reduce / stock.loc[i, '收盤價(元)'])) + cost_reduce[-1])
            cost_increase.append(int(stock.loc[i, '收盤價(元)'] * int(quota_increase / stock.loc[i, '收盤價(元)'])) + cost_increase[-1])
            cost_reinvest.append(int(stock.loc[i, '收盤價(元)'] * int(10000 / stock.loc[i, '收盤價(元)'])) + cost_reinvest[-1])

            month_check += 1
            if month_check == 13:
                month_check = 1
        else:                                          # 不是買進日 → 值沿用昨天
            cost.append(cost[-1]);          cost_reduce.append(cost_reduce[-1])
            cost_increase.append(cost_increase[-1]);   cost_reinvest.append(cost_reinvest[-1])
            shares.append(shares[-1]);      shares_reduce.append(shares_reduce[-1])
            shares_increase.append(shares_increase[-1]); shares_reinvest.append(shares_reinvest[-1])

        # 是否為除息日
        if stock.loc[i, '年月日'] in dividend['除息日'].tolist():
            money = float(dividend.loc[dividend['除息日'] == stock.loc[i, '年月日'], '息值(元)'])
            stock.loc[i, '除息金額'] = money
            cost[-1]          -= int(money * shares[-1])
            cost_reduce[-1]   -= int(money * shares_reduce[-1])
            cost_increase[-1] -= int(money * shares_increase[-1])
        else:
            cum_dividend.append(stock.loc[i, '除息金額'] * shares[-1] + cum_dividend[-1])
            cum_dividend_reduce.append(stock.loc[i, '除息金額'] * shares_reduce[-1] + cum_dividend_reduce[-1])
            cum_dividend_increase.append(stock.loc[i, '除息金額'] * shares_increase[-1] + cum_dividend_increase[-1])

            market_value.append(int(stock.loc[i, '收盤價(元)'] * shares[-1]))
            market_value_reduce.append(int(stock.loc[i, '收盤價(元)'] * shares_reduce[-1]))
            market_value_increase.append(int(stock.loc[i, '收盤價(元)'] * shares_increase[-1]))

            y, m, _ = stock.loc[i, '年月日'].split('/')
            date.append(f'{y}-{m}')

    # 移除 list 開頭的 0
    for lst in (cost, cost_reduce, cost_increase, cost_reinvest,
                shares, shares_reduce, shares_increase, shares_reinvest,
                cum_dividend, cum_dividend_reduce, cum_dividend_increase):
        if lst and lst[0] == 0:
            lst.pop(0)

    # --------- **關鍵修補：對齊長度** ---------
    min_len = min(len(date), len(cost), len(cum_dividend),
                  len(market_value), len(market_value_reduce), len(market_value_increase))
    date                 = date[:min_len]
    market_value         = market_value[:min_len]
    market_value_reduce  = market_value_reduce[:min_len]
    market_value_increase= market_value_increase[:min_len]
    cost                 = cost[:min_len]
    cum_dividend         = cum_dividend[:min_len]
    # ----------------------------------------

    # ───── 圖 1：市值 + 成本 + 股利 ─────
    fig, ax1 = plt.subplots()
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    ax1.set_title('0050 每月定額 $10,000 回測', size=16)
    ax1.set_xlabel('Date'); ax1.set_ylabel('Value')
    ax1.xaxis.set_major_locator(MultipleLocator(12))
    for tick in ax1.get_xticklabels(): tick.set_rotation(45)

    ax1.plot(date, market_value,          label='市值(正常定額)',      color='indianred')
    ax1.plot(date, market_value_increase, label='市值(跌深加碼40%)',   color='steelblue')
    ax1.plot(date, market_value_reduce,   label='市值(跌深減碼40%)',   color='seagreen')

    ax1.bar(date, cost,         color='orange', label='成本(正常定額)')
    ax1.bar(date, cum_dividend, bottom=cost, color='red', label='累積股利')
    ax1.legend(loc='upper left'); ax1.grid(); plt.tight_layout()

    # ───── 圖 2：三策略最終數據比較 ─────
    fig2, ax2 = plt.subplots()
    lbl  = ['跌深加碼40%', '正常定額', '跌深減碼40%']
    mv   = [market_value_increase[-1], market_value[-1], market_value_reduce[-1]]
    cs   = [cost_increase[-1],         cost[-1],        cost_reduce[-1]]
    width = 0.25; x = np.arange(len(lbl))
    bar1 = ax2.bar(x - width/2, cs, width, label='Cost',  color=['lightblue','sandybrown','lightgreen'])
    bar2 = ax2.bar(x + width/2, mv, width, label='Value', color=['steelblue','indianred','seagreen'])
    ax2.set_ylabel('Value'); ax2.set_xticks(x); ax2.set_xticklabels(lbl)
    ax2.set_title('定期定額三種方式比較', size=16); ax2.grid(axis='y')

    for bars in (bar1, bar2):
        for r in bars:
            h = r.get_height()
            ax2.annotate(f'{h}', xy=(r.get_x()+r.get_width()/2, h),
                         xytext=(0,1), textcoords='offset points',
                         ha='center', va='bottom')
    plt.tight_layout()
    # ----------------------------------------

    return plt.gcf()        # 把「最後一張圖」回傳給 Streamlit

# ========== Streamlit 入口 ==========
st.set_page_config(page_title='0050 每月定額回測', layout='wide')
st.title('0050 ETF 每月定額回測')

if st.button('開始跑回測'):
    chart = main()
    st.pyplot(chart)
