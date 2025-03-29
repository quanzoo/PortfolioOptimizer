import pandas as pd
from pyodide.http import open_url
from pyscript import display
from js import console
from pyscript import window, document
import portopt
import warnings

warnings.filterwarnings("ignore")

# 初期ボラティリティ
document.querySelector("input#vol").value = 10

# データ読み込み
url_rets = "https://quanzoo.github.io/PortfolioOptimizer/data/returns.csv"
all_rets = pd.read_csv(open_url(url_rets), index_col=0)
url_rfrs = "https://quanzoo.github.io/PortfolioOptimizer/data/rfrs.csv"
rfrs = pd.read_csv(open_url(url_rfrs), index_col=0)

# 期待リターン計算、初期値設定
ar = portopt.annualize_rets(all_rets, 12)

for asset in ar.index:
    document.querySelector("input#er_" + asset).value = round(ar[asset] * 100, 2)

# Loadingをオフ
document.getElementById('loading').close()

def log(message):
    # log to pandas dev console
    print(message)
    # log to JS console
    console.log(message)

def checked(event):
    asset = event.currentTarget.getAttribute("id")
    if document.querySelector("input#" + asset).checked:
        document.querySelector("input#er_" + asset).removeAttribute("disabled")
    else:
        document.querySelector("input#er_" + asset).setAttribute("disabled", "disabled")

def Optimize(event):
    document.querySelector("div#output").style.display = "none"

    document.querySelector("div#error").style.display = "none"
    
    for asset in ar.index:   
        document.querySelector("tr#wgt_" + asset).style.display = 'none'
    
    target_vol = float(document.querySelector("input#vol").value) / 100

    # 投資対象資産のリスト
    assets = document.querySelectorAll('input[name="assets"]:checked')

    if len(assets) == 0:
        document.querySelector("div#error").style.display = "block"
        display("Error: 資産を１つ以上選択してください", target="error", append=False)                
        return
    
    list_assets = []
    for a in assets:
        list_assets.append(a.value)

    # 期待リターン入力
    er = pd.Series(dtype=float)
    for a in list_assets:
        er[a] = float(document.querySelector("input#er_" + a).value) / 100
    
    # 分散共分散計算
    rets = all_rets[list_assets]
    cov = rets.cov() * 12
    
    # アセット上下限
    n = er.shape[0]
    bounds = ((0.0, 1.0),) * n

    # ウエイト計算
    wgt = portopt.maximize_ret(target_vol, er, cov, bounds)
    wgt = pd.DataFrame(wgt, index=list_assets)
    
    # ポートフォリオパフォーマンス計算
    port_er = portopt.portfolio_return(wgt, er)[0]
    port_vol = portopt.portfolio_vol(wgt, cov)[0][0]
    rfr = portopt.annualize_rets(rfrs, 12)[0]
    port_sr = (port_er - rfr) / port_vol
    
    document.querySelector("div#output").style.display = "block"

    wgt.columns = ["ウエイト"]
    
    for a in wgt.index:    
        document.querySelector("tr#wgt_" + a).style.display = 'table-row'
        document.querySelector("td#wgt_" + a).textContent = '{:.1%}'.format(wgt.loc[a, "ウエイト"])
    
    #結果表示
    document.querySelector("td#port_er").textContent = '{:.1%}'.format(port_er)
    document.querySelector("td#port_vol").textContent = '{:.1%}'.format(port_vol)
    document.querySelector("td#port_sr").textContent = '{:.2f}'.format(port_sr)


    

    
