#!/usr/bin/env python3
"""Write a tw-stock-analysis-framework.md report for a variable candidate set."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import os
import re
import statistics
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

try:
    from collect_tw_eps_evidence import collect_eps_evidence_for_stocks
except Exception:  # pragma: no cover - keeps report usable if helper import fails
    collect_eps_evidence_for_stocks = None
try:
    from tw_valuation_model import build_valuation as build_three_layer_valuation
except ImportError:  # importlib callers may place only the repository root on sys.path
    from scripts.tw_valuation_model import build_valuation as build_three_layer_valuation


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
RUN_DATE = os.environ.get("RUN_DATE", date.today().isoformat())
OUTPUT_SUFFIX = RUN_DATE.replace("-", "")
CANDIDATE_COUNT = int(os.environ.get("CANDIDATE_COUNT", os.environ.get("TOP_N", "10")))
CANDIDATE_CODES = [
    code.strip()
    for code in os.environ.get("CANDIDATE_CODES", "").split(",")
    if code.strip()
]
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "tw_stock_analysis_framework")
REPORT_TITLE = os.environ.get("REPORT_TITLE", "台股候選個股分析")
REPORT = OUTPUT / f"{OUTPUT_PREFIX}_{OUTPUT_SUFFIX}.md"
HTML_REPORT = OUTPUT / f"{OUTPUT_PREFIX}_{OUTPUT_SUFFIX}.html"
PROXY_PE_HISTORY_DAYS = 204
DISPLAY_PROXY_PE_HISTORY_DAYS = 756
CURRENT_YEAR = date.today().year
NEXT_YEAR = CURRENT_YEAR + 1
FUTURE_YEAR = CURRENT_YEAR + 2
REQUIRE_FULL_RESEARCH = os.environ.get("REQUIRE_FULL_TW_RESEARCH", "1") != "0"
FULL_RESEARCH_EVIDENCE_PATH = Path(
    os.environ.get("TW_FULL_RESEARCH_EVIDENCE", str(ROOT / "data/tw_full_research_evidence.json"))
)
EPS_RESEARCH_CACHE_PATH = Path(
    os.environ.get("TW_EPS_RESEARCH_CACHE", str(ROOT / "data/tw_eps_research_cache.json"))
)
MANUAL_FORWARD_EPS_EVIDENCE_PATH = Path(
    os.environ.get("TW_MANUAL_FORWARD_EPS_EVIDENCE", str(ROOT / "data/tw_manual_forward_eps_evidence.json"))
)
EPS_RESEARCH_REFRESH = os.environ.get("TW_EPS_RESEARCH_REFRESH", "1") != "0"
EPS_RESEARCH_MAX_RESULTS_PER_QUERY = int(os.environ.get("TW_EPS_RESEARCH_MAX_RESULTS_PER_QUERY", "3"))
TW_EPS_REALTIME_COLLECT = os.environ.get("TW_EPS_REALTIME_COLLECT", "1") != "0"
TW_EPS_LEGACY_SEARCH = os.environ.get("TW_EPS_LEGACY_SEARCH", "0") == "1"
TW_EPS_USED_RULES_PATH = ROOT / "docs/tw_eps_used_rules.md"
GENERIC_SOURCE_HOSTS = {
    "mops.twse.com.tw/mops/web/index",
    "mops.twse.com.tw/mops/web/t05sr01_1",
    "www.twse.com.tw/zh/",
}


def load_market_context() -> tuple[str, float, str]:
    rows = json.loads((ROOT / "data/twse_mi_index_latest.json").read_text(encoding="utf-8-sig"))
    taiex = next((r for r in rows if r.get("指數") == "發行量加權股價指數"), {})
    raw_date = str(taiex.get("日期") or "")
    if len(raw_date) == 7 and raw_date.isdigit():
        market_date = f"{int(raw_date[:3]) + 1911}-{raw_date[3:5]}-{raw_date[5:7]}"
    else:
        market_date = raw_date or RUN_DATE
    pct = to_float_static(taiex.get("漲跌百分比"))
    if math.isnan(pct):
        return market_date, math.nan, "Unknown"
    if pct <= -3:
        regime = "De-risk"
    elif pct <= -1.5:
        regime = "Caution"
    else:
        regime = "Normal"
    return market_date, pct, regime


def to_float_static(value: Any) -> float:
    text = str(value or "").strip().replace(",", "").replace("+", "")
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


MARKET_INDEX_DATE, MARKET_DAILY_CHANGE_PCT, MARKET_REGIME = load_market_context()

COL = {
    "market": "市場 / Market",
    "code": "股票代號 / Ticker",
    "name": "公司名稱 / Company",
    "industry": "產業名稱 / Industry",
    "tier": "新版分級 / Research Tier",
    "score": "研究優先分 / Research Priority Score",
    "confidence": "資料信心% / Data Confidence %",
    "p0_missing": "P0缺口 / P0 Missing Signals",
    "price_date": "價格日 / Price Date",
    "valuation_date": "估值日 / Valuation Date",
    "trend_date": "股價歷史最新日 / Price History Latest Date",
    "revenue_month": "營收年月 / Revenue Month",
    "financial_q": "財報季度 / Financial Quarter",
    "close": "收盤價 / Close",
    "trade_value": "成交值 / Trade Value",
    "market_cap": "市值 / Market Cap",
    "ret5": "5日報酬% / 5D Return %",
    "ret20": "20日報酬% / 20D Return %",
    "ret60": "60日報酬% / 60D Return %",
    "ma20": "20日均線 / 20D MA",
    "ma50": "50日均線 / 50D MA",
    "high52": "52週高點 / 52W High",
    "low52": "52週低點 / 52W Low",
    "pos52": "52週區間位置% / 52W Range Position %",
    "trend_state": "多期間趨勢狀態 / Multi-Period Trend State",
    "pe": "本益比 / P/E",
    "pb": "股價淨值比 / P/B",
    "yield": "殖利率% / Dividend Yield %",
    "ttm_eps": "推算TTM EPS / Implied TTM EPS",
    "reported_ttm_eps": "四季加總TTM EPS / Reported 4Q TTM EPS",
    "ttm_eps_quarters": "TTM涵蓋季度 / TTM EPS Quarters",
    "ttm_eps_status": "TTM完整性 / TTM EPS Status",
    "annual_eps_114": "114年度EPS / 2025 Annual EPS",
    "annual_eps_113": "113年度EPS / 2024 Annual EPS",
    "annual_eps_112": "112年度EPS / 2023 Annual EPS",
    "rev_yoy": "月營收YoY% / Monthly Revenue YoY %",
    "rev_mom": "月營收MoM% / Monthly Revenue MoM %",
    "ytd_yoy": "累計營收YoY% / YTD Revenue YoY %",
    "rev3m_yoy": "近3月營收YoY% / 3M Revenue YoY %",
    "rev_accel": "營收加速度 / Revenue Acceleration",
    "latest_vs_3m": "最新月較3月均值% / Latest vs 3M Avg %",
    "positive_count": "近3月YoY正成長數 / 3M Positive YoY Count",
    "low_base": "近3月低基期提醒 / 3M Low Base Flag",
    "gross_margin": "毛利率% / Gross Margin %",
    "op_margin": "營益率% / Operating Margin %",
    "net_margin": "淨利率% / Net Margin %",
    "eps_q": "最新季EPS / Latest Quarter EPS",
    "previous_quarter_eps": "上一季EPS / Previous Quarter EPS",
    "l2q_annualized_eps": "近兩季年化EPS / L2Q Annualized EPS",
    "current_ratio": "流動比率 / Current Ratio",
    "debt_equity": "負債權益比 / Debt to Equity",
    "margin_util": "融資使用率% / Margin Utilization %",
    "short_util": "融券使用率% / Short Utilization %",
    "flags": "新版風險提醒 / Research Flags",
}


PROFILE: dict[str, dict[str, Any]] = {
    "2317": {
        "intro": "鴻海是全球大型電子製造服務公司，最熟悉的角色是幫品牌客戶大量生產手機、電腦、伺服器與各種電子產品。白話說，它像是全球科技品牌背後的超大型製造與組裝平台；近年重點從消費電子延伸到 AI 伺服器、雲端網通、電動車與零組件。",
        "decision": "不追；AI 伺服器題材強，但現價已偏 Bull/過熱，等回測或 EPS 上修",
        "type": "EMS/AI 伺服器/大型製造平台",
        "thesis": "3M 營收 YoY 約 37.9%，AI 伺服器與雲端網通題材支撐研究優先度，流動性高。",
        "risk": "毛利率與營益率偏低，股價若先反映 AI server 成長，EPS/margin 沒跟上時容易 de-rating。",
        "bear": ["AI 伺服器營收成長若毛利率不高，營收放大不一定等於 EPS 大幅上修。", "大型電子製造受客戶集中、匯率、地緣與產能調度影響，估值不該只看營收成長。", "現價已進過熱/Bull 定價，若下次月營收或 margin 不接，容易先被資金停利。"],
        "trigger": "補雲端網通/AI 伺服器營收占比、毛利率走勢、OCF/NI 與法人籌碼；價格回測 20D/50D 後再評估 starter。",
        "rerating": "AI Server Rerating Watch；需要 EPS/margin 上修把題材轉成財報。",
        "lowpe": "不是低 P/E；是大型 AI server beta 與製造平台候選，安全邊際要靠回測或 EPS 上修。",
    },
    "4739": {
        "intro": "康普是化學材料公司，產品包含觸媒、特用化學品、肥料與電池材料相關產品。白話說，它不是做消費品牌，而是供應工業與電池供應鏈需要的化學材料，景氣會跟化工報價、電池材料需求與產能利用率連動。",
        "decision": "不追；營收動能很強但估值高於 Bull 過熱，等大幅回測或 EPS 明確上修",
        "type": "化學材料/電池材料題材股",
        "thesis": "3M 營收 YoY 超過 100%，Q1 營益率約 13%，題材與基本面短線都強。",
        "risk": "P/E 約 39 倍、60D 漲幅逾 55%，若電池材料報價或出貨不如預期，估值會先修正。",
        "bear": ["3M 營收高成長可能受低基期、報價或出貨節奏影響，不一定能長期延續。", "化工/電池材料容易受原料價、客戶拉貨與產能週期影響，P/E 高時容錯率低。", "現價高於 Bull 過熱，沒有 EPS/margin 再上修就不適合追價。"],
        "trigger": "補電池材料出貨、報價、越南/新產能進度、OCF/NI、存貨與應收；若回到合理區再研究。",
        "rerating": "Momentum Risk；除非 EPS 上修速度高於股價漲幅，否則先用 de-rating 風險看待。",
        "lowpe": "不是低 P/E；是高成長高估值題材股，重點是驗證成長能不能轉 EPS。",
    },
    "2379": {
        "intro": "瑞昱是 IC 設計公司，主要做網路、音訊、電腦週邊與多媒體相關晶片。白話說，很多電腦、主機板、網通設備、耳機或顯示裝置裡的小晶片，可能就有瑞昱的產品；它靠設計晶片賺錢，不自己蓋晶圓廠大量製造。",
        "decision": "不追；品質佳但現價已 Base 過熱往 Bull，等回測或營收/EPS 加速",
        "type": "IC 設計/網通與電腦週邊晶片",
        "thesis": "毛利率接近 50%，品牌與產品線穩，3M 營收 YoY 仍正成長。",
        "risk": "P/E 約 23 倍、估值溫度過熱；若 PC/網通需求或產品組合沒有上修，新增部位安全邊際不足。",
        "bear": ["IC 設計毛利高，但景氣循環下庫存與客戶拉貨會讓營收/EPS 波動。", "3M 營收 YoY 約 12%，成長不算爆發，若估值已提前反映，容易進入盤整或 de-rating。", "缺 OCF/NI、存貨與應收資料，還不能完整確認本輪成長品質。"],
        "trigger": "補產品線需求、庫存水位、毛利率/營益率趨勢、OCF/NI；若價格回測且月營收加速，再提高優先級。",
        "rerating": "Quality Watch；需要營收加速或 margin 上修支撐更高 multiple。",
        "lowpe": "不是低 P/E；是高毛利 IC 設計品質股，但目前估值偏熱。",
    },
    "3406": {
        "intro": "玉晶光主要做手機、相機、車用或其他電子設備裡的光學鏡片與鏡頭零件。你可以把它想成「幫鏡頭把光線準確送到感光元件」的公司；手機拍照規格升級、鏡頭數變多、車用鏡頭增加，通常會影響它的需求。",
        "decision": "不追；列第一優先追蹤，等月營收回升與回測均線",
        "type": "光學/高 beta 成長股",
        "thesis": "光學族群強、Q1 margin 佳、3M 營收仍雙位數成長。",
        "risk": "5 月營收 MoM 大幅下滑且最新月低於 3M 均值，強勢股若補跌會先殺估值。",
        "bear": ["5 月營收 MoM -29.6%，可能是需求或拉貨節奏轉弱。", "OCF/NI、應收、存貨未取得，無法確認盈餘品質。", "市場 de-risk 時，光學強勢股可能先被資金停利。"],
        "trigger": "下一次月營收回到 3M 均值附近，且收盤守住 20D/50D 均線。",
        "rerating": "Watch / Momentum Risk；需要月營收連續性與 margin 延續才能給更高 multiple。",
        "lowpe": "不是典型低 P/E，高成長與品質可觀，但先排除單月轉弱。",
    },
    "2428": {
        "intro": "興勤做的是電子產品裡的保護元件與感測元件，例如防過熱、防突波、防電流異常的小零件。白話說，它像電器和電子設備裡的安全閥，常出現在家電、電源、汽車電子與各種電路板中。",
        "decision": "不追；高品質 Watch，等回檔或橫盤消化",
        "type": "電子零組件/保護元件成長股",
        "thesis": "營收加速度正向、Q1 毛利率與營益率接近 34%/20%，資產負債相對健康。",
        "risk": "60D 漲幅很大，P/E 26 倍已反映不少品質溢價。",
        "bear": ["60D +81.9%，若族群補跌會快速壓縮 multiple。", "官方估值尚未重估至 6/12，追價後安全邊際下降。", "OCF/NI 與存貨未取得，無法排除拉貨或庫存風險。"],
        "trigger": "回測 20D/50D 不破，且下一次月營收 YoY/MoM 維持正向。",
        "rerating": "Watch / Momentum Risk；品質強但價位延伸。",
        "lowpe": "不是低 P/E；偏品質成長股，買點要靠回檔。",
    },
    "6525": {
        "intro": "捷敏-KY屬於半導體後段製程，主要幫晶片做封裝相關服務。晶片設計好、晶圓做出來後，還要包成可以裝到電子產品裡的零件，這段就是它所在的位置。",
        "decision": "觀望偏優先；半導體中較均衡，適合下一輪完整版",
        "type": "半導體封測/後段製程",
        "thesis": "P/E、殖利率、營收成長與 Q1 margin 平衡度較好。",
        "risk": "6/12 參考價已比候選價高很多，短線安全邊際變差。",
        "bear": ["半導體後段景氣若不跟上，P/E 18.8 不一定便宜。", "6/12 參考收盤較候選價高 10% 以上，不能用 6/10 估值直接追。", "OCF/NI、應收、存貨未取得，封測景氣循環風險未確認。"],
        "trigger": "補 OCF/NI、應收、存貨；若 6 月營收延續且回測不破 20D，可升級研究。",
        "rerating": "Normal / Watch；較像基本面均衡候選，不是純題材。",
        "lowpe": "接近低估成長候選，但仍需現金流與存貨確認。",
    },
    "2303": {
        "intro": "聯電是晶圓代工廠，客戶把晶片設計圖交給它，它負責把晶片真的做在晶圓上。白話說，它像晶片產業的專業製造工廠，服務範圍包含通訊、車用、消費電子與工業晶片。",
        "decision": "不追；大型主題 Watch，等急漲消化",
        "type": "大型晶圓代工/半導體 beta",
        "thesis": "流動性極高、營收改善、半導體主題分高。",
        "risk": "60D +120.7%，P/E 29.8，已不是低估值 setup。",
        "bear": ["60D 急漲後，若稼動率或報價未改善，會進入 de-rating。", "Q1 EPS 年化低於 TTM EPS，短期獲利節奏需確認。", "大型半導體受外資、SOX、AI beta 與市場風格影響大。"],
        "trigger": "補近兩季 margin、法人籌碼、估值 percentile；價格至少消化急漲後再看。",
        "rerating": "Momentum Risk / De-rating Mode；必須先問回落 multiple。",
        "lowpe": "不是低 P/E；本輪是流動性與主題強，不是低估值。",
    },
    "2606": {
        "intro": "裕民是散裝航運公司，主要用船運送煤炭、鐵礦砂、穀物等大宗原物料。它的獲利很吃運價，就像貨運費漲時賺得多、運價跌時壓力會變大。",
        "decision": "觀望；低估值循環 Watch，先驗證運價與現金流",
        "type": "航運/景氣循環股",
        "thesis": "P/E 低、殖利率高、3M 營收 YoY 強，Q1 margin 高。",
        "risk": "航運盈餘受運價與供需循環影響，低 P/E 可能是景氣高峰折價。",
        "bear": ["運價若轉弱，低 P/E 會變成景氣高峰假便宜。", "負債權益比 1.21 較高，循環下行時估值要打折。", "OCF/NI 未取得，不能確認高盈餘可收現。"],
        "trigger": "補 BDI/運價、船隊供給、OCF/NI；確認不是景氣高峰後再升級。",
        "rerating": "Normal Valuation Mode；用循環股折價，不給高 multiple。",
        "lowpe": "可能是真低估成長，也可能是循環 value trap；需運價與現金流確認。",
    },
    "2637": {
        "intro": "慧洋-KY是散裝航運公司，主要營運乾散貨船隊，收入會隨運價、船隊調度與大宗原物料需求變動。白話說，它賺的是全球貨物用船運送時的運費差，景氣好時 EPS 會跳很快，景氣轉弱時也會很快回落。",
        "decision": "觀望偏優先；低 P/E 航運候選，先補運價與現金流",
        "type": "散裝航運/循環收益股",
        "thesis": "P/E 約 10.7、殖利率約 4.6%、3M 營收 YoY 約 33.6%，Q1 營益率高。",
        "risk": "航運股低 P/E 常出現在景氣高檔或運價波動期，若 BDI/租金轉弱，估值會快速重評。",
        "bear": ["運價若回落，營收與 EPS 可能同步下修，低 P/E 變成 value trap。", "52W 位置已偏高，若市場風格轉弱，高殖利率也不一定能撐住股價。", "OCF/NI、船隊合約與負債結構未完整接入，循環下行風險仍未確認。"],
        "trigger": "補 BDI/散裝船型運價、OCF/NI、負債結構；若月營收與運價仍同步走強，再升級研究。",
        "rerating": "Normal Valuation Mode；航運股要用循環折價，不用單季 EPS 給高 multiple。",
        "lowpe": "低 P/E 高營收成長候選，但必須先排除運價高峰造成的假便宜。",
    },
    "9945": {
        "intro": "潤泰新主要和不動產開發、商場/住宅建案、資產與轉投資有關。白話說，它不是賣日常消費品的公司，而是靠土地、建案、資產價值與投資收益一起影響獲利。",
        "decision": "觀望偏優先；估值相對合理，但先確認營收來源與資產價值",
        "type": "不動產/轉投資價值股",
        "thesis": "P/E 與 P/B 偏低、殖利率有支撐，3M 營收 YoY 與最新月營收都強。",
        "risk": "低 P/E/P/B 可能來自市場對資產折價、建案認列波動或一次性收益的折價。",
        "bear": ["營收高成長可能來自建案交屋認列，未必能每季延續。", "不動產與轉投資股常需要看 NAV、負債與資產重估，單看 P/E 可能失真。", "若利率、房市政策或資產處分不如預期，低 P/B 不一定會 rerating。"],
        "trigger": "補建案認列節奏、NAV/轉投資價值、OCF/NI 與負債結構；若營收和現金流都能延續，才提高優先級。",
        "rerating": "Value Rerating Candidate；要靠資產價值可見度、現金流與股利支撐，不能只靠低 P/B。",
        "lowpe": "低 P/E 高營收成長候選，但需排除建案認列與一次性收益造成的假成長。",
    },
    "3706": {
        "intro": "神達做伺服器、工業電腦、車用與雲端資料中心相關硬體。白話說，它幫企業或資料中心做比較耐用、可長時間運轉的電腦系統，景氣會跟 AI/雲端、企業 IT 與伺服器需求連動。",
        "decision": "觀望；營收動能強，但 margin 還沒證明能完全轉成 EPS",
        "type": "電腦週邊/伺服器與工業電腦",
        "thesis": "3M 營收 YoY 約 41.5%、月營收 YoY 約 49.3%，P/E 仍在可研究區。",
        "risk": "Q1 營益率只有約 3.7%，若營收來自低毛利案型，股價題材會比獲利先跑。",
        "bear": ["營收高成長但毛利率/營益率偏低，可能是低毛利出貨放大。", "估值溫度已偏熱，新增部位需要等回測或 EPS 上修。", "若 AI/伺服器主題降溫，低 margin 標的容易先被 de-rating。"],
        "trigger": "下一季營益率與 EPS 是否明顯改善；補 OCF/NI、存貨與應收，確認不是只衝營收。",
        "rerating": "Rerating Candidate；題材有，但必須看到 margin 轉換與現金流品質。",
        "lowpe": "不是典型低 P/E；是營收加速與 AI/伺服器 proxy，核心驗證點是 margin。",
    },
    "2618": {
        "intro": "長榮航是航空公司，收入來自載客、貨運與相關航空服務。白話說，它賺的是機票、貨運運價與航線利用率，成本則很受油價、匯率、維修與機隊調度影響。",
        "decision": "觀望；低 P/E 高殖利率候選，但先看旅運/貨運循環",
        "type": "航空/景氣循環與油價敏感股",
        "thesis": "P/E 約 7、殖利率逾 5%，3M 營收 YoY 接近 20%，Q1 營益率仍佳。",
        "risk": "航空盈餘受油價、匯率、票價與貨運運價影響，低 P/E 可能是景氣高峰折價。",
        "bear": ["若票價或貨運運價回落，EPS 會比營收更快被壓縮。", "油價或台幣匯率不利時，margin 會承壓。", "低 P/E 航空股常需要確認循環位置，不可直接當成便宜成長股。"],
        "trigger": "補客運載客率、貨運運價、油價避險、OCF/NI；若月營收與 margin 都延續，再提高優先級。",
        "rerating": "Normal Valuation Mode；航空股用循環折價，除非 EPS 可見度提高才 rerating。",
        "lowpe": "低 P/E 高殖利率候選，但必須排除航空循環高峰與成本反轉風險。",
    },
    "4551": {
        "intro": "智伸科做汽車與工業用精密零組件，產品會用在車子的動力、控制、安全或電子系統相關位置。白話說，它是幫車廠供應鏈做高精度小零件的公司，需求會跟車市、電動車與客戶出貨節奏連動。",
        "decision": "不追；基本面穩但現價偏 Bull/過熱，等回測",
        "type": "汽車零組件/精密加工",
        "thesis": "3M 營收 YoY 約 21.6%，Q1 營益率約 15.3%，資產負債表相對健康。",
        "risk": "P/E 約 20.6 且估值溫度過熱，若車用需求或客戶拉貨不接，容易先修正 valuation。",
        "bear": ["汽車零組件若客戶拉貨放慢，營收與毛利率會同步受壓。", "現價已偏 Bull 情境，EPS 沒上修就不適合追。", "OCF/NI、應收與存貨未取得，無法確認營收品質與庫存風險。"],
        "trigger": "補客戶需求、車用/工業訂單、OCF/NI 與下一季 margin；若價格回到合理區再研究 starter。",
        "rerating": "Quality Watch；要靠 EPS 上修支撐，不然先用 overheat price 管風險。",
        "lowpe": "不是低 P/E；是品質與成長候選，但目前估值安全邊際不足。",
    },
    "1708": {
        "intro": "東鹼是化工公司，產品和工業、農業或清潔相關化學品有關。這類公司常受到原料價格、產品報價與景氣循環影響，營收好不代表每一季毛利都穩。",
        "decision": "不追；便宜成長候選，但等營收止滑",
        "type": "化學/景氣與原料週期股",
        "thesis": "P/E 13.8、Q1 margin 不錯、3M 營收 YoY 仍強。",
        "risk": "5 月營收 MoM -22.7%，且 52W 位置 90.5%，價位不便宜。",
        "bear": ["單月營收明顯降溫，可能是需求或報價轉弱。", "化工產品價格若下行，EPS 會比營收更快下修。", "融資使用率 15.25% 偏高於前十名多數候選，回檔時籌碼風險較高。"],
        "trigger": "下一次月營收止滑，且毛利率/營益率未惡化。",
        "rerating": "Normal / Watch；先排除 value trap。",
        "lowpe": "低 P/E 高成長候選，但未通過單月營收與現金流品質確認。",
    },
    "3617": {
        "intro": "碩天主要做不斷電系統 UPS 和電力備援設備。白話說，當停電或電壓不穩時，它的設備可以讓電腦、機房、工廠或醫療設備不要立刻斷電。",
        "decision": "觀望偏優先；收益/品質 Watch",
        "type": "UPS/電力備援/其他電子",
        "thesis": "P/E 15、殖利率 4.7%、高毛利，52W 位置不高。",
        "risk": "3M 營收 YoY 9.4%，成長動能不如其他前十名。",
        "bear": ["營收成長不夠快，可能只是合理估值而非重估。", "高毛利需要 OCF/NI 驗證，否則品質分不完整。", "成交值相對前十名較低，若市場轉弱流動性較差。"],
        "trigger": "補 OCF/NI、存貨；若營收加速重啟，可提高優先級。",
        "rerating": "Normal Valuation Mode；用收益與品質，不給題材高 multiple。",
        "lowpe": "偏合理估值品質股，不是強成長低 P/E。",
    },
    "6214": {
        "intro": "精誠是資訊服務與系統整合公司，幫企業建置軟體、資訊系統、雲端、資安或資料相關服務。你可以把它想成企業找外部團隊來升級 IT 系統時會合作的廠商。",
        "decision": "觀望；營收強但 margin 待確認",
        "type": "資訊服務/系統整合",
        "thesis": "3M 營收 YoY 34.9%、P/E 15、殖利率 4.2%。",
        "risk": "Q1 營益率只有 4.94%，營收未必能轉 EPS。",
        "bear": ["若營收來自低毛利案型，P/E 15 不一定便宜。", "Q1 營益率偏低，費用或專案結構可能吃掉成長。", "OCF/NI、應收未取得，系統整合應收風險需補。"],
        "trigger": "下一季營益率改善，且應收/OCF 沒有背離。",
        "rerating": "Normal / Watch；題材不重要，重點是 margin 轉換。",
        "lowpe": "低 P/E 高營收成長候選，但未通過 margin 檢查。",
    },
    "6257": {
        "intro": "矽格屬於半導體封測廠，主要做晶片測試與封裝相關服務。白話說，晶片做出來後要確認能不能穩定工作、再包成可交付的零件，這段需求會跟半導體景氣、客戶拉貨與 AI/車用/消費電子循環連動。",
        "decision": "不追；半導體動能 Watch，等估值消化或 EPS 上修",
        "type": "半導體封測/測試服務",
        "thesis": "3M 營收 YoY 約 21.7%，Q1 毛利率與營益率不錯，60D 股價動能強。",
        "risk": "P/E 已約 30 倍且 60D 漲幅高，若 EPS 沒有上修，容易進入 de-rating。",
        "bear": ["封測景氣若未跟上股價，30 倍 P/E 會先被壓縮。", "52W 位置偏高，新增部位容易買在資金熱區。", "OCF/NI、應收、存貨與法人籌碼未取得，無法確認成長品質與籌碼續航。"],
        "trigger": "補法人/投信、自營、OCF/NI 與下一次月營收；若 EPS/margin 上修且回測不破 20D/50D，再升級研究。",
        "rerating": "Momentum Risk；需要 EPS/margin 上修才能支撐較高 multiple。",
        "lowpe": "不是低 P/E；是半導體復甦與股價動能候選，估值安全邊際不足。",
    },
    "1342": {
        "intro": "八貫做的是高強度複合材料與相關加工品，應用在戶外、救生、工業或特殊用途材料。白話說，它賣的不是一般布料，而是有耐磨、耐壓或特殊功能要求的材料產品。",
        "decision": "不追；基本面強但等拉回",
        "type": "小中型材料/其他類高位股",
        "thesis": "3M 營收 YoY 37.5%、Q1 營益率 20.4%、殖利率 5.6%。",
        "risk": "52W 位置 100%，P/B 4.03，追價風險最高之一。",
        "bear": ["價格在 52 週高點，市場轉弱時容易先被停利。", "P/B 4.03 已不低，若月營收不如預期會壓縮。", "小中型股若流動性縮，跌停/跳空風險比大型股高。"],
        "trigger": "離開 52 週高點或回測不破後，再用下一次月營收驗證。",
        "rerating": "Momentum Risk；基本面強但價位太滿。",
        "lowpe": "P/E 不高、成長強，但高位與 P/B 使安全邊際不足。",
    },
    "3022": {
        "intro": "威強電做工業電腦、嵌入式系統與邊緣運算相關硬體。白話說，它做的不是一般家用電腦，而是放在工廠、醫療、零售、自動化設備或 AI edge 場景裡長時間運作的電腦。",
        "decision": "不追；轉機 Watch，等 margin 接上",
        "type": "工業電腦/AI edge 轉機股",
        "thesis": "月營收 YoY 92.4%、營收加速度 82.7、P/B 1.31。",
        "risk": "Q1 營益率只有 2.29%，營收尚未證明能轉 EPS。",
        "bear": ["營收高成長但營益率低，可能是低毛利或費用吃掉成長。", "52W 位置 94.35%，題材已先反映在股價。", "OCF/NI、應收、存貨未取得，轉機股最怕塞貨或低品質成長。"],
        "trigger": "下一季營益率/EPS 改善，並補應收/存貨，才可從 Theme Watch 升級。",
        "rerating": "Watch / Rerating Candidate，但未過題材轉財報驗證。",
        "lowpe": "不是低 P/E；是低 P/B + 高營收轉機，margin 是核心門檻。",
    },
    "3025": {
        "intro": "星通屬於通信網路設備與系統相關公司，需求常受電信、企業網路、專案出貨與設備更新週期影響。白話說，它看起來像營收加速題材股，但最後仍要看專案毛利與回款品質。",
        "decision": "觀望偏優先；營收高成長候選，等 margin 與應收驗證",
        "type": "通信網路/專案型成長股",
        "thesis": "月營收 YoY 與 MoM 明顯加速，3M 營收 YoY 接近 100%，Q1 毛利率與營益率佳。",
        "risk": "P/B 偏高且融資使用率不低，若專案毛利或下月營收不接，容易被估值修正。",
        "bear": ["營收高成長可能來自一次性專案，若不能延續，P/E 與 P/B 會快速被打回。", "融資使用率偏高，小型題材股回檔時容易有籌碼壓力。", "OCF/NI、應收與存貨未取得，專案型公司必須確認回款與庫存。"],
        "trigger": "下一次月營收仍維持高基期成長，並補應收、存貨、OCF/NI；若價格回測不破 20D/50D，可升級研究。",
        "rerating": "Rerating Candidate；但要用 EPS/margin 與現金流確認，不只看營收爆發。",
        "lowpe": "不是傳統低 P/E；是營收加速與品質候選，估值安全邊際需靠回檔或 EPS 上修。",
    },
    "2101": {
        "intro": "南港主要做輪胎與橡膠相關產品，另外也常被市場用資產、土地或轉投資角度評價。白話說，它一邊有製造業的輪胎景氣循環，一邊也有資產價值能不能被市場重新看見的問題。",
        "decision": "觀望偏優先；低 P/E 與營收彈性可研究，但先排除一次性或資產題材誤判",
        "type": "輪胎/橡膠/資產價值候選",
        "thesis": "P/E 約 10.9、52W 位置不高，3M 營收 YoY 很強，現價仍未進過熱減碼區。",
        "risk": "3M 營收 YoY 很高可能受低基期或認列節奏影響，且最新月低於 3M 均值，不能直接視為可持續成長。",
        "bear": ["營收大幅成長若來自低基期或一次性認列，下一季 EPS 未必同步上修。", "橡膠與輪胎受原料、匯率與終端需求影響，毛利率若下滑會抵銷營收彈性。", "資產題材若沒有明確處分、開發或股利政策，低 P/B/低 P/E 不一定會 rerating。"],
        "trigger": "補輪胎出貨、原料成本、資產價值/NAV、OCF/NI 與應收存貨；下月營收需避免明顯回落。",
        "rerating": "Value / Cyclical Rerating Watch；需確認營收不是一次性，且資產價值有釋放路徑。",
        "lowpe": "低 P/E 高營收成長候選，但必須排除低基期、資產認列與循環高峰造成的假便宜。",
    },
    "2476": {
        "intro": "鉅祥做精密金屬零組件與電子零件相關產品，常用在電子設備、連接、機構或車用/工業應用。白話說，它賣的是設備裡不起眼但需要精密加工的小零件，需求會跟終端電子與客戶拉貨週期連動。",
        "decision": "不追；成長與趨勢強，但 52W 位置高且已進過熱減碼區",
        "type": "電子零組件/精密金屬件/高位成長股",
        "thesis": "3M 營收 YoY 約 37.8%，60D 漲幅強，Q1 margin 仍佳，研究價值在於是否有結構性訂單上修。",
        "risk": "P/E 約 29 倍、52W 位置近高檔，現價已高於過熱價；沒有 EPS/margin 上修不適合追。",
        "bear": ["強勢上漲後若下一次月營收不接，估值會先被壓縮。", "電子零組件容易受客戶拉貨、庫存與價格壓力影響，營收強不必然等於 EPS 強。", "缺 OCF/NI、應收與存貨，無法確認高成長是不是高品質訂單。"],
        "trigger": "補主要應用、客戶拉貨、OCF/NI、應收與存貨；只有回測 20D/50D 不破且營收續強才升級。",
        "rerating": "Momentum Risk；除非 EPS/margin 明確上修，先用高位 de-rating 風險管理。",
        "lowpe": "不是低 P/E；是高動能成長候選，安全邊際需靠回檔或財報上修。",
    },
    "6191": {
        "intro": "精成科主要與印刷電路板、電子製造與組裝服務相關。白話說，它幫電子產品做電路板與相關製造，景氣會跟伺服器、網通、消費電子與客戶庫存週期連動。",
        "decision": "觀望偏優先；現價仍在合理區，但急漲後要補營收與現金流品質",
        "type": "PCB/電子製造服務/電子零組件",
        "thesis": "P/E 約 16、3M 營收 YoY 正成長，成交值高，且現價尚未高於過熱減碼區。",
        "risk": "單日漲幅大且營收動能降溫，若只是題材追價，短線容易回測均線。",
        "bear": ["營收動能若放慢，PCB/EMS 的 EPS 上修空間會被質疑。", "單日強漲後若法人與成交量無法延續，容易回到技術試單區。", "缺 OCF/NI、應收與存貨，無法確認訂單品質與庫存風險。"],
        "trigger": "補產品組合、AI/伺服器或車用占比、OCF/NI、應收與存貨；若回測守住 20D/50D 可優先研究。",
        "rerating": "Rerating Watch；需要營收重新加速與 margin 支撐，才給更高 multiple。",
        "lowpe": "偏低 P/E 成長候選，但營收動能與現金流品質還沒驗證完整。",
    },
    "6206": {
        "intro": "飛捷做 POS 收銀系統、工業電腦、觸控終端與商用自動化設備。白話說，它提供店家、餐飲、零售或工業場景會用到的專用電腦與終端設備，需求受企業設備更新和專案出貨影響。",
        "decision": "觀望；品質與殖利率可追蹤，但現價偏 Bull 且跌破 20D 需等轉強",
        "type": "POS/工業電腦/商用終端設備",
        "thesis": "P/E 約 18、殖利率約 4%，Q1 毛利率與營益率不錯，60D 趨勢仍強。",
        "risk": "20D 報酬略負且跌破 20D，短線資金可能已開始降溫；估值溫度偏熱。",
        "bear": ["若商用設備更新不如預期，營收和 EPS 可能從高檔回落。", "現價接近 Bull 定價，沒有月營收或 margin 上修就不該追。", "缺 OCF/NI、應收與存貨，專案型出貨需確認回款品質。"],
        "trigger": "補區域/產品出貨、訂單能見度、OCF/NI、應收與存貨；收回 20D 並站穩後再升級。",
        "rerating": "Quality Watch；若 margin 穩且營收續強可維持評價，否則先用偏熱處理。",
        "lowpe": "不算便宜，但具品質與股利支撐；買點要等回測或趨勢修復。",
    },
    "3034": {
        "intro": "聯詠是 IC 設計公司，主要做顯示驅動晶片與影像/顯示相關控制晶片。白話說，電視、螢幕、手機、平板或車載顯示要把畫面正確顯示出來，背後就需要這類晶片。",
        "decision": "觀望；大型 IC 設計品質候選，但現價已偏 Bull，等回測或營收加速",
        "type": "IC 設計/顯示驅動/半導體",
        "thesis": "P/E 約 20、殖利率仍有支撐，Q1 margin 高，半導體景氣復甦時具研究價值。",
        "risk": "現價接近過熱價且已偏 Bull 定價，若顯示需求或產品組合沒有上修，安全邊際不足。",
        "bear": ["顯示驅動 IC 受面板循環與客戶庫存影響，需求反彈可能不連續。", "高毛利 IC 設計若營收沒有加速，較高估值容易回到合理倍數。", "缺 OCF/NI、存貨與應收，仍需確認庫存與現金流品質。"],
        "trigger": "補面板需求、車用/高階產品占比、存貨與 OCF/NI；若回測 20D/50D 且月營收加速，再提高優先級。",
        "rerating": "Quality Watch；需要營收加速或產品組合改善支撐更高 multiple。",
        "lowpe": "不是深度低估，但屬高品質 IC 設計候選；目前重點是等安全邊際。",
    },
    "3413": {
        "intro": "京鼎是半導體設備與零組件供應商，產品與晶圓廠設備、製程模組或相關精密機構有關。白話說，它不是直接賣晶片，而是賣半導體工廠運轉時需要的設備零組件與系統。",
        "decision": "觀望；半導體設備復甦候選，但營收動能降溫且現價接近過熱",
        "type": "半導體設備/設備零組件",
        "thesis": "P/E 約 17、Q1 margin 尚可，若半導體 capex 復甦，具 EPS 修正可能。",
        "risk": "20D 報酬為負、營收動能降溫，且現價接近 overheat；不適合在未確認前追價。",
        "bear": ["半導體設備需求若延後，訂單與營收可能先走弱。", "月營收動能降溫時，股價若仍在偏熱區，de-rating 風險上升。", "缺 OCF/NI、應收與存貨，設備廠尤其需要確認出貨與回款品質。"],
        "trigger": "補半導體設備訂單、客戶 capex、存貨/應收與 OCF/NI；月營收重新加速後再升級。",
        "rerating": "Cyclical Rerating Watch；要等 capex 與營收同步轉強。",
        "lowpe": "P/E 看似合理，但設備循環未確認前不能定義為低估成長。",
    },
    "3592": {
        "intro": "瑞鼎是 IC 設計公司，主要做顯示驅動與顯示相關晶片。白話說，它的產品讓螢幕可以把影像訊號轉成正確畫面，需求跟面板、車載顯示、筆電/螢幕與消費電子週期相關。",
        "decision": "觀望偏優先；估值仍在合理到偏熱間，股利與 3M 成長可研究",
        "type": "IC 設計/顯示驅動/半導體",
        "thesis": "P/E 約 17、殖利率約 5.3%，3M 營收 YoY 約 31%，現價離 overheat 價仍有距離。",
        "risk": "顯示 IC 受面板循環影響大，若月營收或毛利率反轉，合理估值也會被下修。",
        "bear": ["面板與消費電子需求若轉弱，3M 營收成長可能無法延續。", "IC 設計高毛利需要存貨與 OCF/NI 驗證，避免庫存堆高。", "若同族群估值降溫，偏熱評價會先回到 entry/fair 區。"],
        "trigger": "補產品組合、面板價格/需求、存貨與 OCF/NI；若月營收續強且守住 20D/50D，可優先做完整版。",
        "rerating": "Quality / Yield Watch；股利與合理 P/E 有支撐，但需營收與庫存確認。",
        "lowpe": "接近低 P/E 高成長候選，但要用存貨、現金流與面板循環確認。",
    },
}

LEADING_SIGNAL_LIBRARY: dict[str, list[tuple[str, str, str, str, str, str, str, str, str]]] = {
    "電腦及週邊設備": [
        ("Hyperscaler AI CapEx 與雲端基建預算", "Stage 0", "正向", "間接：客戶需求", "Alphabet 2026 Q1 earnings / CapEx update", "https://abc.xyz/investor/", "A-", "12–36 月", "與公司月營收分屬不同證據鏈"),
        ("AI accelerator／rack-scale 平台出貨與產品轉換", "Stage 0/1", "正向", "間接：上游平台", "NVIDIA FY2027 Q1 results（2026-05-21）", "https://investor.nvidia.com/", "A-", "6–24 月", "用來驗證 AI server 需求，不直接等同個股訂單"),
        ("全球 PC 出貨、AI PC 滲透與記憶體成本", "Stage 0/1", "中性", "間接：終端需求", "Gartner PC market research", "https://www.gartner.com/en/newsroom", "B-", "3–18 月", "適用 PC 品牌／板卡，需和公司產品組合交叉檢查"),
    ],
    "半導體": [
        ("TSMC CapEx、先進製程與先進封裝需求", "Stage 0", "正向", "間接：晶圓代工／客戶鏈", "TSMC quarterly results", "https://investor.tsmc.com/english/quarterly-results/2026/q1", "A", "12–36 月", "驗證半導體景氣與 AI 供應鏈，不直接等同個股市占"),
        ("SEMI 設備銷售、晶圓廠產能與封裝投資展望", "Stage 0", "中性", "間接：產業供給", "SEMI market data", "https://www.semi.org/en/market-data", "B-", "12–36 月", "需確認個股製程／產品是否真正受惠"),
        ("下游 PC、手機、面板與 AI server 出貨組合", "Stage 0/1", "中性", "間接：終端需求", "TrendForce research", "https://www.trendforce.com/presscenter", "B-", "3–18 月", "依公司產品線選擇對應終端，不可混為單一半導體循環"),
    ],
    "光電": [
        ("主要手機客戶出貨、產品組合與高階機種需求", "Stage 0/1", "中性", "間接：客戶需求", "Apple quarterly results", "https://investor.apple.com/investor-relations/default.aspx", "A-", "3–18 月", "客戶營收不等同鏡頭規格或供應份額"),
        ("手機鏡頭顆數、潛望式／高像素規格升級", "Stage 0", "正向", "間接：技術規格", "TrendForce smartphone research", "https://www.trendforce.com/presscenter", "B-", "12–36 月", "需再用公司產品認證與量產時程驗證"),
        ("同業月營收與毛利率變化", "Stage 1/2", "中性", "間接：競爭者", "MOPS monthly revenue / financials", "https://mops.twse.com.tw/mops/web/index", "A", "0–12 月", "同業同步可提高產業訊號可信度"),
    ],
    "航運業": [
        ("BDI／Capesize／Panamax／Supramax 即期與期租運價", "Stage 0/1", "中性", "間接：產業價格", "Baltic Exchange market information", "https://www.balticexchange.com/en/data-services/market-information0.html", "A-", "0–6 月", "需依個股船型組合使用對應指數"),
        ("全球散裝船 orderbook、交船與拆船速度", "Stage 0", "中性", "間接：供給", "UNCTAD maritime transport statistics", "https://unctad.org/topic/transport-and-trade-logistics/review-of-maritime-transport", "A", "12–36 月", "供給成長快於貨量時屬 de-rating 訊號"),
        ("中國鐵礦砂、煤炭、穀物進口與鋼鐵產量", "Stage 0/1", "中性", "間接：貨量需求", "China customs statistics", "http://english.customs.gov.cn/Statics/ReportPre.html", "A", "1–12 月", "應和公司航線、船型與合約結構交叉驗證"),
    ],
    "鋼鐵工業": [
        ("離岸風電區塊開發里程碑、下單與併網時程", "Stage 0/1", "正向", "間接：政策／專案需求", "經濟部能源署離岸風電", "https://www.moeaea.gov.tw/ECW/populace/content/Content.aspx?menu_id=4510", "A", "12–36 月", "政策容量不等同個股得標，需追合約與認列"),
        ("鋼材價格、厚板成本與專案報價差", "Stage 0/1", "中性", "間接：投入成本／ASP", "中鋼月盤價", "https://www.csc.com.tw/csc/hr/cscnews/index.asp", "A-", "1–6 月", "ASP 上升若被原料成本吃掉，margin 不一定改善"),
        ("工程進度、海象窗口與客戶驗收", "Stage 1", "中性", "直接／間接：專案執行", "MOPS重大訊息", "https://mops.twse.com.tw/mops/web/t05sr01_1", "A", "0–18 月", "延誤、成本追加或驗收遞延是主要反向訊號"),
    ],
    "其他": [
        ("房市交易量、建照／使照與建案交屋週期", "Stage 0/1", "中性", "間接：終端需求", "內政部不動產資訊平台", "https://pip.moi.gov.tw/", "A", "3–24 月", "交易量與個案入帳時程需分開判讀"),
        ("央行利率、選擇性信用管制與房貸條件", "Stage 0", "中性", "間接：政策／資金成本", "中央銀行理監事會資料", "https://www.cbc.gov.tw/tw/lp-302-1.html", "A", "6–24 月", "政策收緊會壓估值與資金需求"),
        ("轉投資淨值、股利能力與資產處分／重估", "Stage 1/2", "中性", "直接：資產價值", "MOPS財報與重大訊息", "https://mops.twse.com.tw/mops/web/index", "A", "0–24 月", "一次性處分利益不能直接外推長期 EPS"),
    ],
}

CODE_LEADING_SIGNALS: dict[str, list[tuple[str, str, str, str, str, str, str, str, str]]] = {
    "3706": [
        ("AI server 新平台認證、量產時程與雲端客戶拉貨", "Stage 1", "正向", "直接：產品／客戶承諾", "神達法說、重大訊息與年報", "https://mops.twse.com.tw/mops/web/index", "A-/B", "3–18 月", "需取得產品占比、量產時間與訂單能見度"),
    ],
    "3406": [
        ("新機鏡頭認證、潛望式規格與旺季備貨節奏", "Stage 1", "正向", "直接：產品認證／客戶拉貨", "玉晶光法說與重大訊息", "https://mops.twse.com.tw/mops/web/index", "A-/B", "3–12 月", "月營收之前先追認證與備貨，但客戶名稱可能不揭露"),
    ],
    "2637": [
        ("船隊續約日租金、未來覆蓋率與新船交付", "Stage 1", "中性", "直接：合約／供給", "慧洋-KY法說、重大訊息與月營運公告", "https://mops.twse.com.tw/mops/web/index", "A-", "0–18 月", "比單月營收更領先，需拆船型與合約期間"),
    ],
    "6206": [
        ("大型零售／餐飲客戶換機、POS 專案與訂單能見度", "Stage 1", "中性", "直接：專案／客戶需求", "飛捷法說與重大訊息", "https://mops.twse.com.tw/mops/web/index", "A-/B", "3–18 月", "專案型收入需確認交付與驗收時程"),
    ],
    "6525": [
        ("高功率封裝／散熱訂單、產能利用率與客戶認證", "Stage 1", "正向", "直接：認證／產能", "捷敏-KY法說與重大訊息", "https://mops.twse.com.tw/mops/web/index", "A-/B", "3–18 月", "需證明產品組合改善而非只受整體半導體景氣"),
    ],
    "8016": [
        ("OLED／車用／高階顯示驅動 IC design-in 與晶圓投片", "Stage 0/1", "中性", "直接：技術／供應鏈", "矽創法說與重大訊息", "https://mops.twse.com.tw/mops/web/index", "A-/B", "6–24 月", "design-in 不等同量產，需追投片與出貨"),
    ],
    "9945": [
        ("建案使照、交屋認列排程與南山等轉投資股利", "Stage 1", "中性", "直接：資產／現金流", "潤泰新法說、財報與重大訊息", "https://mops.twse.com.tw/mops/web/index", "A-", "0–24 月", "需拆經常性與一次性收益"),
    ],
    "9958": [
        ("離岸風電基樁／套筒訂單、產能稼動與客戶驗收", "Stage 1", "正向", "直接：訂單／產能", "世紀鋼法說與重大訊息", "https://mops.twse.com.tw/mops/web/index", "A-/B", "3–24 月", "政策容量需轉成個股得標與認列才可升分"),
    ],
    "2357": [
        ("AI PC／電競新品 sell-through、通路庫存與記憶體成本", "Stage 0/1", "中性", "直接＋間接：產品／終端", "華碩法說與全球 PC 出貨資料", "https://mops.twse.com.tw/mops/web/index", "A-/B", "1–12 月", "出貨成長若靠通路塞貨或成本上升，margin 可能不改善"),
    ],
    "3592": [
        ("OLED／車用／高階面板 driver IC design win、投片與量產", "Stage 0/1", "中性", "直接：design win／量產", "瑞鼎法說與重大訊息", "https://mops.twse.com.tw/mops/web/index", "A-/B", "6–24 月", "需以量產時程、ASP 與毛利率驗證"),
    ],
}


def default_profile(d: dict[str, Any]) -> dict[str, Any]:
    industry = d.get("industry") or "未分類產業"
    name = d.get("name") or d.get("code") or "該公司"
    return {
        "intro": f"{name}屬於{industry}。目前本地資料只足夠做財務與價格框架分析；產品、客戶與商業模式需要在下一輪補公司年報、法說或官網資料。",
        "decision": "觀望；資料足夠排序，但公司質化資料需補",
        "type": f"{industry}/待補商業模式",
        "thesis": "篩選分數靠營收、估值、價格趨勢與最新季財報 proxy 支撐。",
        "risk": "產品結構、主要客戶、OCF/NI、應收與存貨未取得，不能把排序分數直接當買進理由。",
        "bear": [
            "營收成長可能來自一次性或低毛利案型，未必能轉成 EPS。",
            "估值位置若已偏熱，新增部位需要等回測或 EPS 上修。",
            "缺 OCF/NI、應收與存貨，無法確認盈餘品質。",
        ],
        "trigger": "補公司產品、客戶結構、OCF/NI、應收、存貨與下一次月營收，再決定是否升級。",
        "rerating": "Watch；需要質化資料與財報品質確認。",
        "lowpe": "目前只能做初步估值判斷，不能直接定義為低估成長股。",
    }


def load_full_research_evidence() -> dict[str, Any]:
    if not FULL_RESEARCH_EVIDENCE_PATH.exists():
        if REQUIRE_FULL_RESEARCH:
            raise SystemExit(
                "完整研究版已設為預設，但缺少研究證據檔："
                f"{FULL_RESEARCH_EVIDENCE_PATH}\n"
                "請先逐檔線上查證並建立 JSON，或僅在明確要產生本地量化版時設定 "
                "REQUIRE_FULL_TW_RESEARCH=0。"
            )
        return {}
    payload = json.loads(FULL_RESEARCH_EVIDENCE_PATH.read_text(encoding="utf-8-sig"))
    return payload.get("tickers", payload)


def is_generic_source_url(url: str) -> bool:
    return any(host in (url or "") for host in GENERIC_SOURCE_HOSTS)


def validate_full_research_entry(code: str, entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ["intro", "type", "thesis", "risk", "trigger", "company_summary_source"]:
        if not str(entry.get(key) or "").strip():
            errors.append(f"{code}: missing {key}")
    bear = entry.get("bear") or entry.get("reverse_evidence") or []
    if len(bear) < 3:
        errors.append(f"{code}: bear/reverse_evidence must have at least 3 items")
    stage_signals = entry.get("stage_signals") or []
    if len(stage_signals) < 3:
        errors.append(f"{code}: stage_signals must have at least 3 sourced rows")
    has_specific_stage01 = False
    for idx, row in enumerate(stage_signals, 1):
        stage = str(row.get("stage") or "")
        url = str(row.get("url") or row.get("source_url") or "")
        if not url:
            errors.append(f"{code}: stage_signals[{idx}] missing source url")
        if ("Stage 0" in stage or "Stage 1" in stage) and url and not is_generic_source_url(url):
            has_specific_stage01 = True
    if not has_specific_stage01:
        errors.append(f"{code}: requires at least one non-generic Stage 0/1 source")
    sources = entry.get("sources") or []
    if len(sources) < 2:
        errors.append(f"{code}: sources must include at least company/IR plus one external or event source")
    return errors


def apply_full_research_profile(d: dict[str, Any], evidence_map: dict[str, Any]) -> None:
    code = str(d.get("code") or "")
    entry = evidence_map.get(code)
    if not entry:
        if REQUIRE_FULL_RESEARCH:
            raise SystemExit(
                f"{code} {d.get('name')}: 缺完整研究證據。"
                f"請先補 {FULL_RESEARCH_EVIDENCE_PATH}，或明確設定 REQUIRE_FULL_TW_RESEARCH=0 才能產生本地量化版。"
            )
        d["research_mode"] = "本地量化版，Stage 0–1 待補"
        return
    errors = validate_full_research_entry(code, entry)
    if errors and REQUIRE_FULL_RESEARCH:
        raise SystemExit("完整研究證據不完整：\n- " + "\n- ".join(errors))
    d.update({k: entry[k] for k in ["intro", "type", "thesis", "risk", "trigger"] if k in entry})
    if entry.get("decision"):
        d["decision"] = entry["decision"]
    if entry.get("bear") or entry.get("reverse_evidence"):
        d["bear"] = entry.get("bear") or entry.get("reverse_evidence")
    if entry.get("rerating"):
        d["rerating"] = entry["rerating"]
    if entry.get("lowpe"):
        d["lowpe"] = entry["lowpe"]
    d["full_research_entry"] = entry
    d["research_mode"] = "完整研究版"


def load_eps_research_cache() -> dict[str, Any]:
    if not EPS_RESEARCH_CACHE_PATH.exists():
        return {"tickers": {}, "last_updated": None}
    try:
        return json.loads(EPS_RESEARCH_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"tickers": {}, "last_updated": None, "load_error": "cache json parse failed"}


def load_manual_forward_eps_evidence() -> dict[str, Any]:
    if not MANUAL_FORWARD_EPS_EVIDENCE_PATH.exists():
        return {}
    try:
        payload = json.loads(MANUAL_FORWARD_EPS_EVIDENCE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload.get("tickers", payload) if isinstance(payload, dict) else {}


def merge_manual_forward_eps_evidence(entry: dict[str, Any], manual_entry: dict[str, Any] | None) -> dict[str, Any]:
    if not manual_entry:
        return entry
    merged = dict(entry or {})

    existing = list(merged.get("evidence_items") or [])
    existing_ids = {
        str(item.get("id") or item.get("source_url") or item.get("url") or "")
        for item in existing
        if isinstance(item, dict)
    }
    for item in manual_entry.get("evidence_items") or []:
        if not isinstance(item, dict):
            continue
        identity = str(item.get("id") or item.get("source_url") or item.get("url") or "")
        if identity and identity in existing_ids:
            continue
        existing.append(item)
        if identity:
            existing_ids.add(identity)
    if existing:
        merged["evidence_items"] = existing

    estimates = dict(merged.get("eps_estimates") or {})
    for group, value in (manual_entry.get("eps_estimates") or {}).items():
        if group == "consensus":
            consensus = dict(estimates.get("consensus") or {})
            for year, item in (value or {}).items():
                consensus[str(year)] = item
            estimates["consensus"] = consensus
        elif group == "broker":
            broker = dict(estimates.get("broker") or {})
            for year, items in (value or {}).items():
                current = list(broker.get(str(year)) or [])
                current_ids = {
                    str(item.get("id") or item.get("source_url") or item.get("url") or "")
                    for item in current
                    if isinstance(item, dict)
                }
                for item in items or []:
                    if not isinstance(item, dict):
                        continue
                    identity = str(item.get("id") or item.get("source_url") or item.get("url") or "")
                    if identity and identity in current_ids:
                        continue
                    current.append(item)
                    if identity:
                        current_ids.add(identity)
                broker[str(year)] = current
            estimates["broker"] = broker
        else:
            estimates[group] = value
    if estimates:
        merged["eps_estimates"] = estimates
    if manual_entry.get("manual_forward_eps_note"):
        merged["manual_forward_eps_note"] = manual_entry["manual_forward_eps_note"]
    return merged


def save_eps_research_cache(cache: dict[str, Any]) -> None:
    EPS_RESEARCH_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cache["last_updated"] = RUN_DATE
    EPS_RESEARCH_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_text_url(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 CodexTWStockResearch/1.0",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.6",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(1_000_000)
    return raw.decode("utf-8", errors="ignore")


def compact_html_text(text: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def duckduckgo_results(query: str) -> list[dict[str, str]]:
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query, "kl": "tw-tzh"})
    page = fetch_text_url(url)
    results: list[dict[str, str]] = []
    for block in re.findall(r'(?is)<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>(.*?)(?=<a[^>]+class="result__a"|$)', page):
        href, title_html, tail = block
        title = compact_html_text(title_html)
        snippet_match = re.search(r'(?is)<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', tail)
        snippet = compact_html_text(snippet_match.group(1)) if snippet_match else compact_html_text(tail)[:500]
        decoded = urllib.parse.unquote(href)
        uddg = urllib.parse.parse_qs(urllib.parse.urlparse(decoded).query).get("uddg")
        result_url = uddg[0] if uddg else decoded
        if title and result_url:
            results.append({"title": title, "url": result_url, "snippet": snippet})
        if len(results) >= EPS_RESEARCH_MAX_RESULTS_PER_QUERY:
            break
    return results


def extract_eps_estimates_from_text(text: str, url: str, title: str) -> list[dict[str, Any]]:
    """Extract conservative year-specific EPS estimate candidates from Chinese snippets/pages."""
    clean = compact_html_text(text)
    candidates: list[dict[str, Any]] = []
    source_host = urllib.parse.urlparse(url).netloc.lower()
    # Keep patterns narrow: require the year and EPS/每股盈餘 near a number.
    patterns = [
        r"(?P<year>20\d{2})[E估預]?\s*(?:年)?[^。；,，]{0,30}(?:EPS|每股盈餘|每股稅後盈餘)[^。；,，]{0,18}(?P<eps>-?\d+(?:\.\d+)?)",
        r"(?:EPS|每股盈餘|每股稅後盈餘)[^。；,，]{0,18}(?P<year>20\d{2})[E估預]?(?:年)?[^。；,，]{0,18}(?P<eps>-?\d+(?:\.\d+)?)",
        r"(?P<year>20\d{2})[E估預][^。；,，]{0,20}(?P<eps>-?\d+(?:\.\d+)?)\s*元",
    ]
    seen: set[tuple[int, float, str]] = set()
    for pat in patterns:
        for m in re.finditer(pat, clean, flags=re.I):
            year = int(m.group("year"))
            eps = to_float(m.group("eps"))
            if year not in {CURRENT_YEAR, NEXT_YEAR, FUTURE_YEAR} or not finite(eps):
                continue
            start, end = max(0, m.start() - 90), min(len(clean), m.end() + 90)
            context = clean[start:end]
            key = (year, round(eps, 3), source_host)
            if key in seen:
                continue
            seen.add(key)
            candidates.append({
                "year": year,
                "eps": eps,
                "source": title or source_host,
                "url": url,
                "broker": source_host or title,
                "date": RUN_DATE,
                "context": context,
            })
    return candidates


def eps_research_queries(d: dict[str, Any]) -> list[str]:
    code = str(d.get("code") or "")
    name = str(d.get("name") or "")
    industry = str(d.get("industry") or "")
    return [
        f"{code} {name} {NEXT_YEAR} EPS 預估 法人 券商",
        f"{code} {name} {CURRENT_YEAR} EPS 預估 法人 券商",
        f"{name} {NEXT_YEAR} 每股盈餘 預估",
        f"{name} {CURRENT_YEAR} 每股盈餘 預估",
        f"{code} {name} {industry} EPS forecast",
    ]


def research_eps_online_for_stock(d: dict[str, Any], cache: dict[str, Any]) -> dict[str, Any]:
    """Refresh online EPS estimate candidates, then return merged cache entry.

    The program intentionally refreshes every run. If refresh fails, older sourced
    candidates remain in cache but the report can show the latest refresh error.
    """
    code = str(d.get("code") or "")
    entry = cache.setdefault("tickers", {}).setdefault(code, {
        "code": code,
        "name": d.get("name"),
        "eps_estimates": {"broker": {}},
        "quarter_eps": {},
        "online_attempts": [],
    })
    if not EPS_RESEARCH_REFRESH:
        entry["last_refresh_status"] = "skipped_by_env"
        return entry

    entry["last_refresh_started_at"] = RUN_DATE
    entry["last_refresh_epoch"] = int(time.time())
    entry.setdefault("online_attempts", [])
    entry.setdefault("eps_estimates", {}).setdefault("broker", {})
    errors: list[str] = []
    new_candidates = 0

    for query in eps_research_queries(d):
        attempt = {"query": query, "date": RUN_DATE, "results": []}
        try:
            results = duckduckgo_results(query)
            for result in results:
                text_for_parse = f"{result.get('title','')}。{result.get('snippet','')}"
                page_error = ""
                try:
                    page_text = fetch_text_url(result["url"], timeout=10)
                    text_for_parse += "。" + compact_html_text(page_text)[:20000]
                except Exception as exc:
                    page_error = str(exc)[:180]
                estimates = extract_eps_estimates_from_text(text_for_parse, result["url"], result.get("title", ""))
                attempt["results"].append({
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "snippet": result.get("snippet"),
                    "page_error": page_error,
                    "estimate_count": len(estimates),
                })
                for est in estimates:
                    year_key = str(est["year"])
                    bucket = entry["eps_estimates"]["broker"].setdefault(year_key, [])
                    identity = hashlib.sha1(f"{est['url']}|{est['eps']}|{est['year']}".encode()).hexdigest()
                    if not any(item.get("id") == identity for item in bucket):
                        est["id"] = identity
                        bucket.append(est)
                        new_candidates += 1
            attempt["status"] = "ok"
        except Exception as exc:
            attempt["status"] = "error"
            attempt["error"] = str(exc)[:240]
            errors.append(f"{query}: {exc}")
        entry["online_attempts"].append(attempt)

    # Keep a bounded audit trail so cache remains readable.
    entry["online_attempts"] = entry["online_attempts"][-30:]
    entry["last_refresh_status"] = "ok" if not errors else "partial_error"
    entry["last_refresh_error"] = "; ".join(errors[:3])
    entry["new_candidate_count"] = new_candidates
    return entry


def merge_eps_research_into_entry(full_entry: dict[str, Any], eps_entry: dict[str, Any]) -> dict[str, Any]:
    """Merge cached/refreshed EPS research without overwriting manually curated fields."""
    merged = dict(full_entry or {})
    merged_est = dict(merged.get("eps_estimates") or {})
    cache_est = eps_entry.get("eps_estimates") or {}
    merged_broker = {str(k): list(v) for k, v in (merged_est.get("broker") or {}).items()}
    for year, items in (cache_est.get("broker") or {}).items():
        bucket = merged_broker.setdefault(str(year), [])
        existing = {item.get("id") or f"{item.get('url')}|{item.get('eps')}" for item in bucket if isinstance(item, dict)}
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict):
                continue
            key = item.get("id") or f"{item.get('url')}|{item.get('eps')}"
            if key not in existing:
                bucket.append(item)
                existing.add(key)
    if merged_broker:
        merged_est["broker"] = merged_broker
    if cache_est.get("consensus") and not merged_est.get("consensus"):
        merged_est["consensus"] = cache_est["consensus"]
    if merged_est:
        merged["eps_estimates"] = merged_est
    if eps_entry.get("quarter_eps") and not merged.get("quarter_eps"):
        merged["quarter_eps"] = eps_entry["quarter_eps"]
    merged["eps_research_refresh"] = {
        "status": eps_entry.get("last_refresh_status"),
        "error": eps_entry.get("last_refresh_error"),
        "new_candidate_count": eps_entry.get("new_candidate_count", 0),
        "cache_path": str(EPS_RESEARCH_CACHE_PATH),
        "searched_at": eps_entry.get("last_refresh_started_at"),
    }
    return merged


def eps_evidence_complete(entry: dict[str, Any], d: dict[str, Any] | None = None) -> bool:
    """Return True only when evidence is enough to avoid immediate TTM fallback."""
    estimates = entry.get("eps_estimates") or {}
    consensus_map = estimates.get("consensus") or entry.get("eps_consensus") or {}
    broker_map = estimates.get("broker") or entry.get("broker_eps_estimates") or {}
    for year in [str(NEXT_YEAR), str(CURRENT_YEAR)]:
        item = consensus_map.get(year) or consensus_map.get(int(year)) or {}
        count = to_float(item.get("analyst_count") or item.get("source_count") or item.get("count"))
        eps = to_float(item.get("median_eps") or item.get("eps") or item.get("value"))
        if finite(eps) and finite(count) and count >= 3:
            return True
        raw_items = broker_map.get(year) or broker_map.get(int(year)) or []
        if isinstance(raw_items, dict):
            raw_items = raw_items.get("items") or raw_items.get("estimates") or []
        values = [to_float(x.get("eps") or x.get("median_eps") or x.get("value")) for x in raw_items if isinstance(x, dict)]
        if len([x for x in values if finite(x)]) >= 3:
            return True
    quarter_eps = entry.get("quarter_eps") or {}
    latest_q = to_float((d or {}).get("eps_q") or quarter_eps.get("latest_quarter_eps"))
    previous_q = to_float(
        quarter_eps.get("previous_quarter_eps")
        or quarter_eps.get("previous")
        or entry.get("previous_quarter_eps")
        or (d or {}).get("previous_quarter_eps")
    )
    return finite(latest_q) and finite(previous_q)


def ensure_eps_evidence_for_stock(d: dict[str, Any], evidence_map: dict[str, Any]) -> dict[str, Any]:
    """Refresh EPS evidence before EPS_used selection when local evidence is incomplete.

    Before modifying Taiwan stock EPS valuation logic, read
    docs/tw_eps_used_rules.md and follow it exactly. Do not redesign EPS_used
    rules unless explicitly requested.
    """
    code = str(d.get("code") or "")
    entry = evidence_map.get(code) or d.get("full_research_entry") or {}
    if eps_evidence_complete(entry, d):
        return entry
    if not TW_EPS_REALTIME_COLLECT:
        return entry
    if collect_eps_evidence_for_stocks is None:
        entry = dict(entry)
        entry["eps_collection"] = {
            "collection_status": "failed",
            "error_message": "collect_tw_eps_evidence.py import failed",
            "rules_path": str(TW_EPS_USED_RULES_PATH.relative_to(ROOT)),
        }
        return entry
    collect_eps_evidence_for_stocks([code], force=False)
    refreshed = load_full_research_evidence().get(code, {})
    if refreshed:
        evidence_map[code] = refreshed
        return refreshed
    return entry


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_float(value: Any) -> float:
    if value is None:
        return math.nan
    text = str(value).replace(",", "").strip()
    if not text:
        return math.nan
    try:
        return float(text)
    except ValueError:
        return math.nan


def fmt(value: Any, digits: int = 1, suffix: str = "") -> str:
    x = to_float(value)
    if math.isnan(x):
        return "未取得"
    return f"{x:,.{digits}f}{suffix}"


def fmt_pct(value: float) -> str:
    if math.isnan(value):
        return "未取得"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def tw_date(text: str) -> str:
    text = (text or "").strip()
    if len(text) == 7 and text.isdigit():
        return f"{int(text[:3]) + 1911}-{text[3:5]}-{text[5:7]}"
    if len(text) == 5 and text.isdigit():
        return f"{int(text[:3]) + 1911}-{text[3:5]}"
    return text or "未取得"


def percentile(values: list[float], q: float) -> float:
    clean = sorted(v for v in values if not math.isnan(v))
    if not clean:
        return math.nan
    pos = (len(clean) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return clean[int(pos)]
    return clean[lo] * (hi - pos) + clean[hi] * (pos - lo)


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not math.isnan(value)


def fmt_date(value: Any) -> str:
    return str(value or "未取得")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def safe_min(values: list[float]) -> float:
    clean = [v for v in values if finite(v)]
    return min(clean) if clean else math.nan


def safe_median(values: list[float]) -> float:
    clean = [v for v in values if finite(v)]
    return statistics.median(clean) if clean else math.nan


def eps_label_for(eps_type: str) -> str:
    return {
        "CONSENSUS_NEXT_YEAR": "Consensus Next-Year P/E",
        "BROKER_MEDIAN_NEXT_YEAR": "Proxy Next-Year P/E",
        "CONSENSUS_CURRENT_YEAR": "Consensus Current-Year P/E",
        "BROKER_MEDIAN_CURRENT_YEAR": "Proxy Current-Year P/E",
        "L2Q_ANNUALIZED": "L2Q Annualized P/E",
        "TTM": "TTM P/E",
    }.get(eps_type, "P/E")


def eps_confidence_for(eps_type: str) -> str:
    return {
        "CONSENSUS_NEXT_YEAR": "High",
        "BROKER_MEDIAN_NEXT_YEAR": "Medium",
        "CONSENSUS_CURRENT_YEAR": "Medium-High",
        "BROKER_MEDIAN_CURRENT_YEAR": "Medium",
        "L2Q_ANNUALIZED": "Medium-Low",
        "TTM": "Low",
    }.get(eps_type, "Low")


def eps_consensus_for_year(entry: dict[str, Any], year: int) -> dict[str, Any]:
    estimates = entry.get("eps_estimates") or {}
    consensus_map = estimates.get("consensus") or entry.get("eps_consensus") or {}
    item = consensus_map.get(str(year)) or consensus_map.get(year) or {}
    eps = to_float(item.get("median_eps") or item.get("eps") or item.get("value"))
    count = to_float(item.get("analyst_count") or item.get("source_count") or item.get("count"))
    age_days = to_float(item.get("source_age_days") or item.get("age_days"))
    if not finite(age_days):
        matching_ages = [
            to_float(evidence.get("source_age_days") or evidence.get("age_days"))
            for evidence in entry.get("evidence_items") or []
            if str(evidence.get("estimate_year") or "") == str(year)
            and finite(to_float(evidence.get("source_age_days") or evidence.get("age_days")))
        ]
        age_days = min(matching_ages) if matching_ages else math.nan
    return {
        "eps": eps,
        "count": int(count) if finite(count) else 0,
        "source": item.get("source") or item.get("source_note") or "",
        "age_days": age_days,
    }


def broker_eps_for_year(entry: dict[str, Any], year: int) -> dict[str, Any]:
    estimates = entry.get("eps_estimates") or {}
    broker_map = estimates.get("broker") or entry.get("broker_eps_estimates") or {}
    raw_items = broker_map.get(str(year)) or broker_map.get(year) or []
    if isinstance(raw_items, dict):
        raw_items = raw_items.get("items") or raw_items.get("estimates") or []
    values: list[float] = []
    ages: list[float] = []
    independent_keys: set[str] = set()
    for idx, item in enumerate(raw_items if isinstance(raw_items, list) else []):
        if not isinstance(item, dict):
            continue
        eps = to_float(item.get("eps") or item.get("median_eps") or item.get("value"))
        if not finite(eps):
            continue
        age = to_float(item.get("source_age_days") or item.get("age_days"))
        if finite(age) and age > 180:
            continue
        key = str(item.get("broker") or item.get("source") or item.get("url") or f"row-{idx}").strip()
        if key in independent_keys:
            continue
        independent_keys.add(key)
        values.append(eps)
        if finite(age):
            ages.append(age)
    return {
        "eps": safe_median(values),
        "count": len(values),
        "values": values,
        "source": f"{len(values)} independent broker estimates" if values else "",
        "age_days": max(ages) if ages else math.nan,
        "dispersion": (max(values) - min(values)) / abs(safe_median(values)) if len(values) >= 2 and safe_median(values) else math.nan,
    }


def year_eps_summary(entry: dict[str, Any], year: int, label: str) -> dict[str, Any]:
    consensus = eps_consensus_for_year(entry, year)
    broker = broker_eps_for_year(entry, year)
    if finite(consensus["eps"]):
        return {
            "eps": consensus["eps"],
            "count": consensus["count"],
            "type": f"CONSENSUS_{label}",
            "source": consensus["source"],
            "eligible": consensus["count"] >= 3,
            "age_days": consensus.get("age_days"),
        }
    if finite(broker["eps"]):
        return {
            "eps": broker["eps"],
            "count": broker["count"],
            "type": f"BROKER_MEDIAN_{label}",
            "source": broker["source"],
            "eligible": broker["count"] >= 3,
            "age_days": broker.get("age_days"),
        }
    return {"eps": math.nan, "count": 0, "type": "UNAVAILABLE", "source": "", "eligible": False, "age_days": math.nan}


def select_eps_used(d: dict[str, Any]) -> dict[str, Any]:
    """Select exactly one Taiwan EPS_used; never mix current-year and next-year estimates."""
    entry = d.get("full_research_entry") or {}
    current = year_eps_summary(entry, CURRENT_YEAR, "CURRENT_YEAR")
    next_ = year_eps_summary(entry, NEXT_YEAR, "NEXT_YEAR")
    future = year_eps_summary(entry, FUTURE_YEAR, "FUTURE_YEAR")
    latest_q = to_float(d.get("eps_q"))
    quarter_eps = entry.get("quarter_eps") or {}
    previous_q = to_float(
        quarter_eps.get("previous_quarter_eps")
        or quarter_eps.get("previous")
        or entry.get("previous_quarter_eps")
        or d.get("previous_quarter_eps")
    )
    l2q = (latest_q + previous_q) * 2 if finite(latest_q) and finite(previous_q) else math.nan
    ttm = to_float(d.get("ttm_eps"))

    next_consensus = eps_consensus_for_year(entry, NEXT_YEAR)
    next_broker = broker_eps_for_year(entry, NEXT_YEAR)
    current_consensus = eps_consensus_for_year(entry, CURRENT_YEAR)
    current_broker = broker_eps_for_year(entry, CURRENT_YEAR)

    if next_consensus["count"] >= 3 and finite(next_consensus["eps"]):
        eps_used, eps_year, eps_type = next_consensus["eps"], str(NEXT_YEAR), "CONSENSUS_NEXT_YEAR"
    elif next_broker["count"] >= 3 and finite(next_broker["eps"]):
        eps_used, eps_year, eps_type = next_broker["eps"], str(NEXT_YEAR), "BROKER_MEDIAN_NEXT_YEAR"
    elif current_consensus["count"] >= 3 and finite(current_consensus["eps"]):
        eps_used, eps_year, eps_type = current_consensus["eps"], str(CURRENT_YEAR), "CONSENSUS_CURRENT_YEAR"
    elif current_broker["count"] >= 3 and finite(current_broker["eps"]):
        eps_used, eps_year, eps_type = current_broker["eps"], str(CURRENT_YEAR), "BROKER_MEDIAN_CURRENT_YEAR"
    elif finite(l2q):
        eps_used, eps_year, eps_type = l2q, "run_rate", "L2Q_ANNUALIZED"
    else:
        eps_used, eps_year, eps_type = ttm, "TTM", "TTM"

    latest = to_float(d.get("latest_close") or d.get("close"))
    pe_used = latest / eps_used if finite(latest) and finite(eps_used) and eps_used > 0 else math.nan
    source_note = "Consensus/broker EPS 需由 full research evidence 提供；年度分開統計，不混合今年與明年。"
    if eps_type == "L2Q_ANNUALIZED":
        source_note = "未取得足夠 consensus/broker EPS；採最近兩季 EPS 年化。"
    elif eps_type == "TTM":
        source_note = "未取得足夠 consensus/broker EPS，也缺近兩季 EPS；採 TTM EPS。"

    return {
        "current_year_eps": current["eps"],
        "current_year_eps_source_count": current["count"],
        "current_year_eps_type": current["type"],
        "current_year_eps_age_days": current.get("age_days"),
        "next_year_eps": next_["eps"],
        "next_year_eps_source_count": next_["count"],
        "next_year_eps_type": next_["type"],
        "next_year_eps_age_days": next_.get("age_days"),
        "future_year_eps": future["eps"],
        "future_year_eps_source_count": future["count"],
        "latest_quarter_eps": latest_q,
        "previous_quarter_eps": previous_q,
        "l2q_annualized_eps": l2q,
        "ttm_eps_for_reference": ttm,
        "eps_used": eps_used,
        "eps_year": eps_year,
        "eps_type": eps_type,
        "eps_confidence": eps_confidence_for(eps_type),
        "pe_used": pe_used,
        "pe_label": eps_label_for(eps_type),
        "collection_status": (entry.get("eps_collection") or {}).get("collection_status", "not_collected"),
        "query_count": (entry.get("eps_collection") or {}).get("query_count", 0),
        "best_source_quality": (entry.get("eps_collection") or {}).get("best_source_quality", ""),
        "duplicate_count": (entry.get("eps_collection") or {}).get("duplicate_count", 0),
        "needs_manual_review": (entry.get("eps_collection") or {}).get("needs_manual_review", eps_type == "TTM"),
        "source_note": source_note,
        "valuation_note": "PE_used = current_price / EPS_used；EPS 預估未達同年度 3 份時不得用於 EPS_used。",
    }


def peer_stats(all_rows: list[dict[str, str]], industry: str) -> dict[str, float]:
    pes = [
        to_float(r[COL["pe"]])
        for r in all_rows
        if r.get(COL["industry"]) == industry and 0 < to_float(r.get(COL["pe"])) < 120
    ]
    return {
        "count": float(len(pes)),
        "min": min(pes) if pes else math.nan,
        "q1": percentile(pes, 0.25),
        "median": statistics.median(pes) if pes else math.nan,
        "q3": percentile(pes, 0.75),
        "max": max(pes) if pes else math.nan,
    }


def peer_weight(peer: dict[str, float]) -> tuple[float, float, float]:
    """Evidence-weight peer valuation by sample size and P/E dispersion."""
    count = peer.get("count", 0.0)
    if count < 3:
        base = 0.0
    elif count <= 5:
        base = 0.10
    elif count <= 14:
        base = 0.20
    else:
        base = 0.25
    q1 = peer.get("q1")
    q3 = peer.get("q3")
    dispersion = q3 / q1 if finite(q1) and finite(q3) and q1 > 0 else math.nan
    if not finite(dispersion):
        penalty = 0.4 if base else 0.0
    elif dispersion <= 2.0:
        penalty = 1.0
    elif dispersion <= 3.0:
        penalty = 0.7
    else:
        penalty = 0.4
    return base * penalty, base, dispersion


def valuation_confidence_label(d: dict[str, Any], v: dict[str, float]) -> str:
    own_count = (d.get("own_pe_proxy") or {}).get("count", 0)
    peer_count = (d.get("peer_pe") or {}).get("count", 0)
    revenue_ok = not math.isnan(to_float(d.get("rev3m_yoy")))
    financial_ok = not math.isnan(to_float(d.get("eps_q"))) and not math.isnan(to_float(d.get("op_margin")))
    if finite(v.get("latest_pe")) and own_count >= 180 and peer_count >= 10 and revenue_ok and financial_ok:
        return "高"
    if finite(v.get("latest_pe")) and own_count >= 120 and peer_count >= 5 and revenue_ok:
        return "中"
    return "低"


def rerating_model(d: dict[str, Any], valuation: dict[str, float]) -> dict[str, float]:
    own = d.get("own_pe_proxy") or {}
    eps = to_float(d.get("eps_used"))
    latest = to_float(d.get("latest_close"))
    traditional = valuation.get("fair_pe")
    recent_raw = safe_median([own.get("p50_3m"), own.get("p50_6m")])
    recent_effective = (
        min(recent_raw, own.get("p90_1y"))
        if finite(recent_raw) and finite(own.get("p90_1y"))
        else math.nan
    )
    rerating_fair = (
        traditional * 0.50 + recent_effective * 0.50
        if finite(traditional) and finite(recent_effective)
        else traditional
    )
    regime_p75 = safe_median([own.get("p75_3m"), own.get("p75_6m")])
    overheat_p90 = safe_median([own.get("p90_3m"), own.get("p90_6m")])
    current_pe = valuation.get("latest_pe")

    ret20 = to_float(d.get("ret20"))
    ret60 = to_float(d.get("ret60"))
    rev3m = to_float(d.get("rev3m_yoy"))
    rev_accel = to_float(d.get("rev_accel"))
    positive_count = to_float(d.get("positive_count"))
    op_margin = to_float(d.get("op_margin"))
    eps_q = to_float(d.get("eps_q"))
    low_base = str(d.get("low_base") or "").strip()
    margin_util = to_float(d.get("margin_util"))
    pos52 = to_float(d.get("pos52"))

    market_score = 0.0
    if finite(own.get("p50_3m")) and finite(traditional) and own["p50_3m"] > traditional:
        market_score += 10
    if finite(own.get("p50_6m")) and finite(traditional) and own["p50_6m"] > traditional:
        market_score += 10
    if finite(recent_effective) and finite(traditional) and recent_effective > traditional:
        market_score += 10
    if finite(ret20) and finite(ret60) and ret20 > 0 and ret60 > 0:
        market_score += 10

    fundamental_score = 0.0
    if finite(rev3m) and rev3m > 10:
        fundamental_score += 8
    if finite(rev_accel) and rev_accel > 0:
        fundamental_score += 8
    if finite(positive_count) and positive_count >= 2:
        fundamental_score += 6
    if finite(eps_q) and eps_q > 0:
        fundamental_score += 5
    if finite(op_margin) and op_margin > 0:
        fundamental_score += 5
    if finite(rev3m) and finite(op_margin) and rev3m > 20 and op_margin > 8:
        fundamental_score += 4
    if not low_base or low_base in {"0", "False", "false", "否", "N", "n"}:
        fundamental_score += 4
    fundamental_score = min(40.0, fundamental_score)

    risk_deduction = 0.0
    if finite(margin_util) and margin_util > 35:
        risk_deduction += 10
    elif finite(margin_util) and margin_util > 20:
        risk_deduction += 5
    if finite(pos52) and finite(latest) and finite(eps) and eps > 0:
        regime_p75_price = eps * regime_p75 if finite(regime_p75) else math.nan
        overheat_p90_price = eps * overheat_p90 if finite(overheat_p90) else math.nan
        if pos52 > 95 and finite(overheat_p90_price) and latest > overheat_p90_price:
            risk_deduction += 10
        elif pos52 > 85 and finite(regime_p75_price) and latest > regime_p75_price:
            risk_deduction += 5
    if finite(to_float(d.get("trade_value"))) and to_float(d.get("trade_value")) < 50_000_000:
        risk_deduction += 5
    risk_deduction = min(20.0, risk_deduction)
    activation_score = max(0.0, min(100.0, market_score + fundamental_score - risk_deduction))

    if not finite(current_pe):
        classification = "現行 P/E 缺值，無法分類"
    elif finite(traditional) and current_pe <= traditional:
        classification = "傳統合理價內"
    elif finite(rerating_fair) and current_pe <= rerating_fair:
        classification = "Rerating 初期／合理偏高"
    elif finite(regime_p75) and current_pe <= regime_p75:
        classification = "近期市場常態區"
    elif finite(overheat_p90) and current_pe <= overheat_p90:
        classification = "偏熱，需營收/EPS續證明"
    else:
        classification = "高於近期 P90，過熱／需新上修證據"

    return {
        "recent_raw_anchor": recent_raw,
        "recent_effective_anchor": recent_effective,
        "rerating_fair_pe": rerating_fair,
        "regime_p75_pe": regime_p75,
        "rerating_overheat_p90_pe": overheat_p90,
        "rerating_fair_price": eps * rerating_fair if finite(eps) and finite(rerating_fair) else math.nan,
        "regime_p75_price": eps * regime_p75 if finite(eps) and finite(regime_p75) else math.nan,
        "rerating_overheat_p90_price": eps * overheat_p90 if finite(eps) and finite(overheat_p90) else math.nan,
        "rerating_market_score": market_score,
        "rerating_fundamental_score": fundamental_score,
        "rerating_risk_deduction": risk_deduction,
        "rerating_activation_score": activation_score,
        "rerating_classification": classification,
    }


def valuation_model(d: dict[str, Any]) -> dict[str, float]:
    eps = to_float(d.get("eps_used"))
    official_pe = to_float(d["pe"])
    latest_close = to_float(d["latest_close"])
    latest_pe = latest_close / eps if eps and not math.isnan(eps) and not math.isnan(latest_close) else official_pe
    own = d["own_pe_proxy"]
    peer = d["peer_pe"]
    ma20 = to_float(d["ma20"])
    ma50 = to_float(d["ma50"])

    if math.isnan(eps) or eps <= 0:
        unavailable = {
            key: math.nan
            for key in [
                "latest_pe", "eps_used", "pe_used", "self_fair_pe", "peer_weight",
                "peer_base_weight", "peer_dispersion", "peer_fair_capped",
                "stress_pe", "entry_pe", "fair_pe", "upper_fair_pe", "overheat_pe",
                "stress_price", "entry_price", "fair_price", "upper_fair_price",
                "technical_test_price", "chase_stop_price", "risk_stop_price",
                "overheat_price", "recent_raw_anchor", "recent_effective_anchor",
                "rerating_fair_pe", "regime_p75_pe", "rerating_overheat_p90_pe",
                "rerating_fair_price", "regime_p75_price",
                "rerating_overheat_p90_price", "rerating_market_score",
                "rerating_fundamental_score", "rerating_risk_deduction",
                "rerating_activation_score",
            ]
        }
        unavailable.update({
            "fair_method": "EPS_used 不可用，停止產生目標價",
            "valuation_confidence": "低",
            "rerating_classification": "資料不足，無法分類",
        })
        return unavailable

    self_fair = own.get("p50")
    peer_w, peer_base_w, peer_dispersion = peer_weight(peer)
    peer_median = peer.get("median")
    peer_fair_capped = (
        clamp(peer_median, self_fair * 0.75, self_fair * 1.25)
        if finite(peer_median) and finite(self_fair) and self_fair > 0
        else math.nan
    )
    if finite(self_fair) and finite(peer_fair_capped):
        fair_pe = self_fair * (1 - peer_w) + peer_fair_capped * peer_w
        fair_method = 1.0
    elif finite(self_fair):
        fair_pe = self_fair
        fair_method = 2.0
    elif finite(peer_median):
        fair_pe = peer_median
        fair_method = 3.0
    else:
        fair_pe = latest_pe
        fair_method = 4.0

    stress_pe = safe_min([own.get("p10"), fair_pe * 0.70, peer.get("q1")])
    entry_pe = safe_min([own.get("p25"), fair_pe * 0.85, peer_fair_capped * 0.90 if finite(peer_fair_capped) else math.nan])
    upper_fair_pe = safe_min([own.get("p75"), fair_pe * 1.15])
    overheat_pe = safe_min([own.get("p90"), fair_pe * 1.35, peer.get("q3")])

    if not finite(stress_pe):
        stress_pe = fair_pe * 0.70
    if not finite(entry_pe):
        entry_pe = fair_pe * 0.85
    if not finite(upper_fair_pe):
        upper_fair_pe = fair_pe * 1.15
    if not finite(overheat_pe):
        overheat_pe = fair_pe * 1.35

    technical_test = safe_min([ma50, latest_close * 0.92])
    chase_stop = safe_min([ma20, latest_close * 0.96])
    risk_stop = safe_min([eps * stress_pe * 0.97, technical_test * 0.95])

    out = {
        "latest_pe": latest_pe,
        "eps_used": eps,
        "pe_used": latest_pe,
        "self_fair_pe": self_fair,
        "peer_weight": peer_w,
        "peer_base_weight": peer_base_w,
        "peer_dispersion": peer_dispersion,
        "peer_fair_capped": peer_fair_capped,
        "fair_method": fair_method,
        "stress_pe": stress_pe,
        "entry_pe": entry_pe,
        "fair_pe": fair_pe,
        "upper_fair_pe": upper_fair_pe,
        "overheat_pe": overheat_pe,
        "stress_price": eps * stress_pe,
        "entry_price": eps * entry_pe,
        "fair_price": eps * fair_pe,
        "upper_fair_price": eps * upper_fair_pe,
        "technical_test_price": technical_test,
        "chase_stop_price": chase_stop,
        "risk_stop_price": risk_stop,
        "overheat_price": eps * overheat_pe,
    }
    out["valuation_confidence"] = valuation_confidence_label(d, out)
    out.update(rerating_model(d, out))
    return out


def build_res_qualitative_evidence(entry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Reuse at most two cached company/event sources across all qualitative RES rows."""
    buckets = {
        "consensus_guidance": ("guidance", "展望", "全年", "出貨成長", "營收成長", "毛利率", "需求"),
        "orders_capacity": ("backlog", "order", "訂單", "能見度", "客戶拉貨", "出貨排程", "長約"),
        "pricing_power": ("asp", "漲價", "product mix", "產品組合", "高階產品", "產能滿載", "交期", "supply constraint"),
        "industry": ("capex", "ai server", "data center", "產業", "同業", "需求"),
    }
    candidates = []
    for item in (entry.get("stage_signals") or []) + (entry.get("evidence_items") or []):
        text = "；".join(str(item.get(k) or "") for k in ("signal", "note", "raw_text_excerpt", "source_title"))
        url = item.get("source_url") or item.get("url")
        if text.strip() and url:
            candidates.append((text, url, item))
    # One source can support several categories; cap the entire qualitative pass at two sources.
    selected_urls = []
    out: dict[str, dict[str, Any]] = {}
    for key, words in buckets.items():
        for text, url, item in candidates:
            if not any(word.lower() in text.lower() for word in words):
                continue
            if url not in selected_urls and len(selected_urls) >= 2:
                continue
            if url not in selected_urls:
                selected_urls.append(url)
            company_direct = any(token in str(url).lower() for token in ("mops.twse.com.tw", "ir.", "investor", "company"))
            evidence_type = "Direct" if company_direct and key != "industry" else "Proxy" if key in ("industry", "pricing_power") else "Direct"
            out[key] = {
                "evidence_type": evidence_type,
                "source_date": item.get("source_date") or "",
                "source_title": item.get("source_title") or "cached company/event evidence",
                "excerpt": text[:240],
                "source_url": url,
                "score": 7.0 if evidence_type == "Direct" else 4.0,
            }
            break
    out["_source_count"] = {"value": len(selected_urls)}
    return out


def load_rows() -> list[dict[str, Any]]:
    rows = read_csv(OUTPUT / f"tw_stock_candidates_{OUTPUT_SUFFIX}.csv")
    full_research_evidence = load_full_research_evidence()
    manual_forward_eps_evidence = load_manual_forward_eps_evidence()
    eps_research_cache = load_eps_research_cache()
    history = json.loads((ROOT / "data/tw_daily_price_history_by_stock.json").read_text(encoding="utf-8-sig"))[
        "stocks"
    ]
    quarterly_eps = json.loads((ROOT / "data/tw_quarterly_eps_by_stock.json").read_text(encoding="utf-8-sig")).get("stocks", {})
    income_rows = json.loads((ROOT / "data/tw_income_listed_general_latest.json").read_text(encoding="utf-8-sig"))
    income_rows += read_csv(ROOT / "data/tw_income_otc_general_latest.csv")
    balance_rows = json.loads((ROOT / "data/tw_balance_listed_general_latest.json").read_text(encoding="utf-8-sig"))
    balance_rows += read_csv(ROOT / "data/tw_balance_otc_general_latest.csv")
    income_by_code = {str(row.get("公司代號") or ""): row for row in income_rows}
    balance_by_code = {str(row.get("公司代號") or ""): row for row in balance_rows}
    res_financial_path = ROOT / "data/tw_res_financial_metrics.json"
    res_financials = (
        json.loads(res_financial_path.read_text(encoding="utf-8")).get("stocks", {})
        if res_financial_path.exists() else {}
    )
    if CANDIDATE_CODES:
        by_code = {row.get(COL["code"]): row for row in rows}
        missing = [code for code in CANDIDATE_CODES if code not in by_code]
        if missing:
            raise SystemExit(f"候選資料缺少指定股票：{', '.join(missing)}")
        selected = [by_code[code] for code in CANDIDATE_CODES]
    else:
        selected = rows[:CANDIDATE_COUNT] if CANDIDATE_COUNT > 0 else rows
    out: list[dict[str, Any]] = []
    for rank, r in enumerate(selected, 1):
        code = r[COL["code"]]
        eligible_history = [
            row for row in history.get(code, [])
            if row.get("date") and str(row.get("date")) <= RUN_DATE
        ]
        latest = (eligible_history or [{}])[-1]
        d = {k: r[v] for k, v in COL.items() if v in r}
        d.update(PROFILE.get(code, default_profile(d)))
        apply_full_research_profile(d, full_research_evidence)
        if manual_forward_eps_evidence.get(code):
            d["full_research_entry"] = merge_manual_forward_eps_evidence(
                d.get("full_research_entry") or full_research_evidence.get(code) or {},
                manual_forward_eps_evidence.get(code),
            )
            full_research_evidence[code] = d["full_research_entry"]
        ensured_entry = ensure_eps_evidence_for_stock(d, full_research_evidence)
        if ensured_entry:
            d["full_research_entry"] = ensured_entry
        if manual_forward_eps_evidence.get(code):
            d["full_research_entry"] = merge_manual_forward_eps_evidence(
                d.get("full_research_entry") or {},
                manual_forward_eps_evidence.get(code),
            )
        if TW_EPS_LEGACY_SEARCH:
            eps_cache_entry = research_eps_online_for_stock(d, eps_research_cache)
            if d.get("full_research_entry"):
                d["full_research_entry"] = merge_eps_research_into_entry(d["full_research_entry"], eps_cache_entry)
        d["rank"] = rank
        d["price_date_fmt"] = tw_date(d["price_date"])
        d["valuation_date_fmt"] = tw_date(d["valuation_date"])
        d["revenue_month_fmt"] = tw_date(d["revenue_month"])
        d["latest_close"] = latest.get("close")
        d["latest_date"] = latest.get("date", d["trend_date"])
        d["latest_trade_value"] = latest.get("Trading_money")
        d["q1_annual_eps"] = to_float(d["eps_q"]) * 4 if not math.isnan(to_float(d["eps_q"])) else math.nan
        d.update(select_eps_used(d))
        d["legacy_eps_used"] = d.get("eps_used")
        d["legacy_eps_type"] = d.get("eps_type")
        d["legacy_eps_year"] = d.get("eps_year")
        d["close_delta"] = (
            (to_float(d["latest_close"]) / to_float(d["close"]) - 1) * 100
            if not math.isnan(to_float(d["latest_close"])) and not math.isnan(to_float(d["close"]))
            else math.nan
        )
        clean_history_all = sorted(
            (
                x for x in history.get(code, [])
                if x.get("date")
                and str(x.get("date")) <= RUN_DATE
                and not math.isnan(to_float(x.get("close")))
            ),
            key=lambda x: str(x.get("date")),
        )[-DISPLAY_PROXY_PE_HISTORY_DAYS:]
        clean_history = clean_history_all[-PROXY_PE_HISTORY_DAYS:]
        closes = [to_float(x.get("close")) for x in clean_history if not math.isnan(to_float(x.get("close")))]
        eps = to_float(d["eps_used"])
        proxy_pes = [c / eps for c in closes if eps and not math.isnan(eps)]
        def window_proxy(days: int, q: float) -> float:
            return percentile(proxy_pes[-days:], q) if proxy_pes else math.nan

        all_proxy_rows = [
            {**x, "proxy_pe": to_float(x.get("close")) / eps}
            for x in clean_history_all
            if eps and not math.isnan(eps) and not math.isnan(to_float(x.get("close")))
        ]
        def proxy_window_row(label: str, days: int, confidence: str) -> dict[str, Any]:
            items = all_proxy_rows[-days:]
            vals = [to_float(x.get("proxy_pe")) for x in items if not math.isnan(to_float(x.get("proxy_pe")))]
            return {
                "label": label,
                "days": days,
                "count": len(vals),
                "start": items[0].get("date") if items else "",
                "end": items[-1].get("date") if items else "",
                "p10": percentile(vals, 0.10),
                "p50": percentile(vals, 0.50),
                "p75": percentile(vals, 0.75),
                "p90": percentile(vals, 0.90),
                "confidence": confidence,
                "verification": "已重算驗證" if vals else "資料不足",
            }

        d["peer_pe"] = peer_stats(rows, d["industry"])
        d["own_pe_proxy"] = {
            "count": float(len(proxy_pes)),
            "p10": percentile(proxy_pes, 0.10),
            "p25": percentile(proxy_pes, 0.25),
            "p50": percentile(proxy_pes, 0.50),
            "p75": percentile(proxy_pes, 0.75),
            "p90": percentile(proxy_pes, 0.90),
            "p50_3m": window_proxy(63, 0.50),
            "p75_3m": window_proxy(63, 0.75),
            "p90_3m": window_proxy(63, 0.90),
            "p50_6m": window_proxy(126, 0.50),
            "p75_6m": window_proxy(126, 0.75),
            "p90_6m": window_proxy(126, 0.90),
            "p90_1y": window_proxy(204, 0.90),
        }
        d["own_pe_proxy_windows"] = [
            proxy_window_row("3M", 63, "中高"),
            proxy_window_row("6M", 126, "中高"),
            proxy_window_row("1Y", 252, "中高" if len(all_proxy_rows) >= 252 else "中（資料不足252筆）"),
            proxy_window_row("2Y", 504, "中（長期 proxy 降權）"),
            proxy_window_row("3Y", 756, "中（長期 proxy 降權）"),
        ]
        d["valuation"] = valuation_model(d)
        d["legacy_action_text"] = action_label(d)
        d["legacy_implied_pricing_label"] = implied_pricing_label(d)
        d["legacy_entry_zone"] = entry_zone(d)
        d["legacy_valuation"] = dict(d["valuation"])
        peer_min = to_float(d["peer_pe"].get("min"))
        peer_max = to_float(d["peer_pe"].get("max"))
        research_entry = d.get("full_research_entry") or {}
        current_consensus = (
            ((research_entry.get("eps_estimates") or {}).get("consensus") or {}).get(str(CURRENT_YEAR))
            or {}
        )
        revision_item = next(
            (
                item for item in research_entry.get("evidence_items") or []
                if str(item.get("estimate_year") or "") == str(CURRENT_YEAR)
                and finite(to_float(item.get("eps")))
                and finite(to_float(item.get("previous_eps")))
            ),
            {},
        )
        revision_now = to_float(revision_item.get("eps"))
        revision_prev = to_float(revision_item.get("previous_eps"))
        if finite(revision_now) and finite(revision_prev) and revision_prev != 0:
            revision_pct = revision_now / revision_prev - 1
            eps_revision_score = 10.0 if revision_pct >= 0.02 else 7.0 if revision_pct > 0 else 3.0
        else:
            revision_pct = math.nan
            eps_revision_score = math.nan
        d["forward_eps_revision_pct"] = revision_pct
        d["forward_eps_consensus_url"] = current_consensus.get("source_url") or revision_item.get("source_url") or ""
        consensus_low = to_float(current_consensus.get("low_eps"))
        consensus_high = to_float(current_consensus.get("high_eps"))
        consensus_median = to_float(current_consensus.get("median_eps"))
        forward_eps_dispersion = (
            (consensus_high - consensus_low) / consensus_median
            if finite(consensus_low) and finite(consensus_high) and finite(consensus_median) and consensus_median != 0
            else math.nan
        )
        d["forward_eps_dispersion"] = forward_eps_dispersion
        q_entry = quarterly_eps.get(d.get("code")) or {}
        quarter_map = q_entry.get("quarters") or {}
        latest_q_key = str(d.get("financial_q") or "")
        prior_q_key = ""
        q_match = re.fullmatch(r"(\d{3})Q([1-4])", latest_q_key)
        if q_match:
            prior_q_key = f"{int(q_match.group(1)) - 1:03d}Q{q_match.group(2)}"
        latest_q_eps = to_float((quarter_map.get(latest_q_key) or {}).get("eps"))
        prior_q_eps = to_float((quarter_map.get(prior_q_key) or {}).get("eps"))
        eps_latest_yoy = (
            latest_q_eps / prior_q_eps - 1
            if finite(latest_q_eps) and finite(prior_q_eps) and prior_q_eps != 0 else math.nan
        )
        income_row = income_by_code.get(d.get("code")) or {}
        balance_row = balance_by_code.get(d.get("code")) or {}
        parent_net_income = to_float(income_row.get("淨利（淨損）歸屬於母公司業主"))
        parent_equity = to_float(balance_row.get("歸屬於母公司業主之權益合計"))
        roe_annualized = (
            parent_net_income * 4 / parent_equity * 100
            if finite(parent_net_income) and finite(parent_equity) and parent_equity != 0 else math.nan
        )
        current_assets = to_float(balance_row.get("流動資產"))
        current_liabilities = to_float(balance_row.get("流動負債"))
        calculated_current_ratio = (
            current_assets / current_liabilities
            if finite(current_assets) and finite(current_liabilities) and current_liabilities != 0
            else to_float(d.get("current_ratio"))
        )
        qualitative = build_res_qualitative_evidence(research_entry)
        res_financial = res_financials.get(d.get("code")) or {}
        for key in (
            "gm_yoy_change", "om_yoy_change", "nm_yoy_change",
            "gm_qoq_change", "om_qoq_change", "ocf", "capex", "fcf", "ocf_to_ni",
        ):
            value = to_float(res_financial.get(key))
            if finite(value):
                d[key] = value
        d["res_financial_source"] = res_financial.get("source") or ""
        d["res_financial_source_url"] = res_financial.get("source_url") or ""
        d["res_financial_period"] = res_financial.get("latest_period") or ""
        d["res_cash_flow_period"] = res_financial.get("cash_flow_period") or ""
        industry_ev = qualitative.get("industry") or {
            "evidence_type": "Proxy",
            "source_date": d.get("price_date_fmt"),
            "source_title": "Google CapEx / AI infrastructure research hypothesis",
            "excerpt": "產業需求只作 proxy evidence，不等同公司取得訂單。",
            "source_url": "",
            "score": 3.0,
        }
        res_evidence_types = {
            "eps_acceleration": "Calculated" if finite(eps_latest_yoy) else "Missing",
            "revenue_acceleration": "Calculated" if finite(to_float(d.get("rev3m_yoy"))) else "Missing",
            "margin_expansion": "Calculated" if finite(to_float(d.get("gm_yoy_change"))) or finite(to_float(d.get("om_yoy_change"))) else "Missing",
            "cash_flow": "Calculated" if finite(d.get("fcf")) else "Missing",
            "balance_roe": "Calculated" if finite(roe_annualized) or finite(to_float(d.get("debt_equity"))) else "Missing",
            "consensus_guidance": (qualitative.get("consensus_guidance") or {}).get("evidence_type", "Missing"),
            "industry": industry_ev.get("evidence_type", "Proxy"),
            "orders_capacity": (qualitative.get("orders_capacity") or {}).get("evidence_type", "Missing"),
            "pricing_power": (qualitative.get("pricing_power") or {}).get("evidence_type", "Missing"),
        }
        d["eps_latest_yoy"] = eps_latest_yoy
        d["eps_prior_year_quarter"] = prior_q_key
        d["eps_prior_year_quarter_value"] = prior_q_eps
        d["roe_annualized"] = roe_annualized
        d["current_ratio"] = calculated_current_ratio
        d["res_qualitative_evidence"] = qualitative
        d["res_industry_evidence"] = industry_ev
        d["res_evidence_types"] = res_evidence_types
        model_input = {
            "current_price": d.get("latest_close"),
            "reported_ttm_eps": d.get("reported_ttm_eps"),
            "implied_ttm_eps": d.get("ttm_eps"),
            "ttm_status": d.get("ttm_eps_status"),
            "last_fy_eps": d.get("annual_eps_114"),
            "prev_fy_eps": d.get("annual_eps_113"),
            "latest_quarter_eps": d.get("latest_quarter_eps"),
            "previous_quarter_eps": d.get("previous_quarter_eps"),
            "l2q_annualized_eps": d.get("l2q_annualized_eps"),
            "current_year_eps": d.get("current_year_eps"),
            "current_year_source_count": d.get("current_year_eps_source_count"),
            "current_year_type": d.get("current_year_eps_type"),
            "current_year_age_days": d.get("current_year_eps_age_days"),
            "next_year_eps": d.get("next_year_eps"),
            "next_year_source_count": d.get("next_year_eps_source_count"),
            "next_year_type": d.get("next_year_eps_type"),
            "next_year_age_days": d.get("next_year_eps_age_days"),
            "history_closes": [to_float(x.get("close")) for x in clean_history_all],
            "history_rows": clean_history_all,
            "quarterly_eps": quarter_map,
            "peer_median_pe": d["peer_pe"].get("median"),
            "peer_count": d["peer_pe"].get("count"),
            "peer_dispersion_ratio": peer_max / peer_min if finite(peer_min) and finite(peer_max) and peer_min > 0 else math.nan,
            "revenue_3m_yoy": d.get("rev3m_yoy"),
            "revenue_acceleration": d.get("rev_accel"),
            "gross_margin": d.get("gross_margin"),
            "operating_margin": d.get("op_margin"),
            "gm_yoy_change": d.get("gm_yoy_change"),
            "om_yoy_change": d.get("om_yoy_change"),
            "debt_to_equity": d.get("debt_equity"),
            "current_ratio": calculated_current_ratio,
            "roe": roe_annualized,
            "eps_latest_yoy": eps_latest_yoy,
            "fcf": d.get("fcf"),
            "ocf_to_ni": d.get("ocf_to_ni"),
            "res_evidence_types": res_evidence_types,
            "guidance_score": (qualitative.get("consensus_guidance") or {}).get("score"),
            "industry_confirmation_score": industry_ev.get("score"),
            "orders_evidence_score": (qualitative.get("orders_capacity") or {}).get("score"),
            "pricing_power_score": (qualitative.get("pricing_power") or {}).get("score"),
            "eps_revision_score": eps_revision_score,
            "forward_eps_dispersion": forward_eps_dispersion,
            # Missing cash-conversion/margin bridge fields intentionally remain missing;
            # TW_FETS awards no points and applies its evidence caps.
        }
        d["valuation_v2"] = build_three_layer_valuation(model_input)
        d["legacy_pe_used"] = d["legacy_valuation"].get("pe_used")
        d["legacy_traditional_fair"] = d["legacy_valuation"].get("fair_price")
        d["legacy_overheat_price"] = d["legacy_valuation"].get("overheat_price")
        d["eps_used"] = d["valuation_v2"]["ttm_eps"]
        d["eps_type"] = "REPORTED_TTM_BASELINE" if d["valuation_v2"]["ttm_source_note"].startswith("reported") else "IMPLIED_TTM_FALLBACK"
        d["eps_year"] = "TTM"
        d["eps_confidence"] = d["valuation_v2"]["ttm_quality"]
        d["pe_used"] = (
            to_float(d.get("latest_close")) / to_float(d.get("eps_used"))
            if finite(d.get("latest_close")) and finite(d.get("eps_used")) and to_float(d.get("eps_used")) > 0
            else math.nan
        )
        d["pe_label"] = "Trailing P/E"
        out.append(d)
    save_eps_research_cache(eps_research_cache)
    return out


def valuation_table(d: dict[str, Any]) -> str:
    v = d.get("valuation_v2") or {}
    if not v:
        return "三層估值：資料不足。"
    f, fets, res = v.get("forward", {}), v.get("fets", {}), v.get("res", {})
    ladder = v.get("growth_ladder") or {}
    ladder_text = (
        f"{fmt(ladder.get('q25'))} / {fmt(ladder.get('q35'))} / {fmt(ladder.get('q50'))} / "
        f"{fmt(ladder.get('q65'))} / {fmt(ladder.get('q75'))}"
        if ladder else "不適用（Growth gap <= 0 或缺有效 forward evidence）"
    )
    market_q_text = (
        fmt(v.get("market_implied_q") * 100, 1, "%")
        if finite(v.get("market_implied_q"))
        else "不適用（Growth gap <= 0 或缺有效 forward evidence）"
    )
    return "\n".join([
        "#### 8.1 Conservative valuation：Reported TTM EPS baseline",
        "",
        "| 項目 | 數值 | 定義 |",
        "|---|---:|---|",
        f"| TTM EPS | {fmt(v.get('ttm_eps'), 2)} | {v.get('ttm_source_note')}；quality {v.get('ttm_quality')} |",
        f"| Historical anchor P/E | {fmt(v.get('historical_anchor_pe'))}x | median(2Y, 3Y point-in-time P/E P50) |",
        f"| Peer-clamped P/E | {fmt(v.get('peer_clamped_pe'))}x | 同業只作 sanity check；權重 {fmt(v.get('peer_weight', 0)*100, 0, '%')} |",
        f"| Conservative P/E | {fmt(v.get('conservative_pe'))}x | 歷史錨點與受限同業加權 |",
        f"| Stress / Entry / Fair / Upper | {fmt(v.get('stress_price'))} / {fmt(v.get('conservative_entry'))} / {fmt(v.get('conservative_fair'))} / {fmt(v.get('conservative_upper'))} | 全部以 reported TTM EPS 為分母 |",
        "",
        "#### 8.2 EPS valuation layer",
        "",
        "| Layer | EPS | 價格 | 信心 / 意義 |",
        "|---|---:|---:|---|",
        f"| Conservative fair | {fmt(v.get('ttm_eps'), 2)} | {fmt(v.get('conservative_fair'))} | 已實現 TTM baseline |",
        f"| Trust-adjusted fair | {fmt(v.get('trust_adjusted_eps'), 2)} | {fmt(v.get('trust_adjusted_fair'))} | TW_FETS {fmt(fets.get('score'), 0)}/100；Trust {fmt(fets.get('trust_pct', 0)*100, 0, '%')} |",
        f"| Forward growth anchor proxy | {fmt(f.get('eps'), 2)} | {fmt(v.get('forward_growth_anchor'))} | {f.get('type')}；{v.get('forward_fair_confidence')}；不是 true historical forward P/E |",
        f"| EPS revision bull / EPS+rerating bull | - | {fmt(v.get('eps_revision_bull'))} / {fmt(v.get('eps_rerating_bull'))} | 情境，不是主目標價 |",
        "",
        f"重要口徑：True historical forward P/E unavailable。`current-TTM 歷史倍數 × forward EPS` 可能同時把成長放進 EPS 與倍數，因此本報只稱 **Forward growth anchor proxy**，不把它冒充客觀 Forward fair。",
        "",
        "#### 8.3 Growth pass-through / FETS / RES",
        "",
        f"- Growth ladder q25/q35/q50/q65/q75：{ladder_text}。",
        f"- Market-implied q：{market_q_text}；Price Zone：{v.get('price_zone')}。",
        f"- TW_FETS：{fmt(fets.get('score'), 0)}/100；evidence completeness {fmt(fets.get('evidence_completeness'), 0, '%')}；hard caps：{', '.join(x[0] for x in fets.get('hard_caps', [])) or '無'}。",
        f"- TW_RES：{fmt(res.get('score'), 0)}/100；{res.get('status')}。Google CapEx / AI 題材只提高研究優先度，不證明公司取得訂單。",
        f"- 主動作：{v.get('action')}。",
    ])


def tw_fets_table(d: dict[str, Any]) -> str:
    """Render the auditable 100-point Taiwan Forward EPS Trust Score."""
    v = d.get("valuation_v2") or {}
    fets = v.get("fets") or {}
    forward = v.get("forward") or {}
    modules = fets.get("modules") or {}
    module_rows = [
        (
            "A. Revenue validation", "revenue", 15,
            f"3M revenue YoY {fmt(d.get('rev3m_yoy'), 1, '%')}；acceleration {fmt(d.get('rev_accel'), 1)}",
            "月營收是否已驗證 forward EPS 的營收假設",
        ),
        (
            "B. EPS validation", "eps", 15,
            f"TTM vs last FY {fmt(v.get('eps_yoy_vs_last_fy') * 100 if finite(v.get('eps_yoy_vs_last_fy')) else math.nan, 1, '%')}；forward type {forward.get('type')}",
            "已實現 TTM、L2Q run-rate 與 forward estimate 是否同向",
        ),
        (
            "C. Margin validation", "margin", 12,
            f"GM {fmt(d.get('gross_margin'), 1, '%')}；OM {fmt(d.get('op_margin'), 1, '%')}；YoY/QoQ bridge 未取得",
            "缺少 margin bridge 時不得因單季 margin 自動給滿分",
        ),
        (
            "D. Cash-flow quality", "cash_flow", 10,
            "OCF/NI、FCF、應收與存貨：Missing Data",
            "缺資料不補假值，並觸發 Trust hard cap",
        ),
        (
            "E. Balance-sheet risk", "balance_sheet", 10,
            f"Debt/Equity {fmt(d.get('debt_equity'), 2)}；Current ratio {fmt(d.get('current_ratio'), 2)}",
            "檢查槓桿與短期償債風險",
        ),
        (
            "F. Guidance / management tone", "guidance", 8,
            "公司 guidance：未取得時為 0 分",
            "只有公司正式 guidance 或可核驗管理層說法才給分",
        ),
        (
            "G. Forward EPS source quality", "forward_source_quality", 15,
            f"{forward.get('type')}；source count {forward.get('source_count', 0)}；age {fmt(forward.get('age_days'), 0)} days"
            + (f"；[即時共識來源]({d.get('forward_eps_consensus_url')})" if d.get("forward_eps_consensus_url") else ""),
            "同年度分析師數、時效與來源品質；L2Q fallback 只給低分",
        ),
        (
            "H. EPS revision evidence", "eps_revision", 10,
            f"current-year consensus revision {fmt(d.get('forward_eps_revision_pct') * 100 if finite(d.get('forward_eps_revision_pct')) else math.nan, 1, '%')}",
            "同一 FactSet snapshot 的現值相對前值；上修給分、下修不美化",
        ),
        (
            "I. Estimate reliability", "estimate_reliability", 5,
            f"source count {forward.get('source_count', 0)}；dispersion "
            f"{fmt(d.get('forward_eps_dispersion') * 100 if finite(d.get('forward_eps_dispersion')) else math.nan, 1, '%')}",
            "來源數達門檻才給基本分；無 dispersion 不得給滿分",
        ),
    ]
    rows = [
        "| 模組 | 分數 | 來源數字 / Missing Data | 判斷規則 |",
        "|---|---:|---|---|",
    ]
    for label, key, maximum, evidence, rule in module_rows:
        rows.append(
            f"| {label} | {fmt(modules.get(key), 0)}/{maximum} | {evidence} | {rule} |"
        )
    caps = "；".join(
        f"{reason} → <= {cap * 100:.0f}%"
        for reason, cap in fets.get("hard_caps", [])
    ) or "無額外 hard cap"
    rows.extend([
        f"| **合計** | **{fmt(fets.get('score'), 0)}/100** | evidence completeness {fmt(fets.get('evidence_completeness'), 0, '%')} | confidence {fets.get('confidence')} |",
        "",
        f"Trust mapping 後並套 hard caps：**Trust {fmt(fets.get('trust_pct', 0) * 100, 0, '%')}**；q_final {fmt(fets.get('q_final', 0) * 100, 0, '%')}。",
        "",
        f"Hard caps：{caps}。",
    ])
    return "\n".join([
        "#### 8.4 TW_FETS：Forward EPS Trust Score",
        "",
        *rows,
    ])


def _score_0_2(value: Any, high: float, low: float) -> int:
    value = to_float(value)
    if not finite(value):
        return 0
    return 2 if value >= high else 1 if value >= low else 0


def _source_link(url: str | None, title: str = "來源") -> str:
    return f"[{title}]({url})" if url else "Missing Data"


def _forward_evidence(d: dict[str, Any]) -> dict[str, Any]:
    forward = (d.get("valuation_v2") or {}).get("forward") or {}
    year = NEXT_YEAR if forward.get("year") == "next_year" else CURRENT_YEAR if forward.get("year") == "current_year" else None
    items = [
        item for item in ((d.get("full_research_entry") or {}).get("evidence_items") or [])
        if year is not None and str(item.get("estimate_year") or "") == str(year)
    ]
    items.sort(key=lambda item: to_float(item.get("source_age_days")) if finite(item.get("source_age_days")) else 99999)
    return items[0] if items else {}


def us_style_tw_valuation_sections(d: dict[str, Any]) -> str:
    """Render the complete US-style 7.2A–7.2H valuation sequence for Taiwan."""
    v = d.get("valuation_v2") or {}
    fwd, fets, res = v.get("forward") or {}, v.get("fets") or {}, v.get("res") or {}
    peer, windows = d.get("peer_pe") or {}, v.get("proxy_windows") or {}
    anchor = to_float(v.get("historical_anchor_pe"))
    lower, upper = anchor * .75, anchor * 1.25
    recent = to_float(v.get("recent_rerating_pe"))
    fwd_eps, ttm, current = to_float(fwd.get("eps")), to_float(v.get("ttm_eps")), to_float(d.get("latest_close"))
    growth_bridge = fwd_eps / ttm - 1 if finite(fwd_eps) and finite(ttm) and ttm != 0 else math.nan
    ladder = v.get("growth_ladder") or {}
    market_q = to_float(v.get("market_implied_q"))
    market_q_text = fmt(market_q * 100, 1, "%") if finite(market_q) else "不適用（Growth gap <= 0 或缺有效 forward evidence）"
    growth_gap = to_float(v.get("growth_gap"))
    forward_ev = _forward_evidence(d)
    mops_url = "https://mops.twse.com.tw/mops/web/index"

    # 7.2A Peer sanity.
    dispersion = (
        to_float(peer.get("max")) / to_float(peer.get("min"))
        if finite(peer.get("max")) and finite(peer.get("min")) and to_float(peer.get("min")) > 0 else math.nan
    )
    peer_quality = "high" if to_float(peer.get("count")) >= 10 and finite(dispersion) and dispersion <= 3 else (
        "medium" if to_float(peer.get("count")) >= 5 else "low"
    )
    p50_2y = to_float((windows.get("2Y") or {}).get("p50"))
    p50_3y = to_float((windows.get("3Y") or {}).get("p50"))
    peer_weight_pct = to_float(v.get("peer_weight")) * 100
    blended_pe = (
        anchor * (1 - to_float(v.get("peer_weight")))
        + to_float(v.get("peer_clamped_pe")) * to_float(v.get("peer_weight"))
        if finite(anchor) and finite(v.get("peer_clamped_pe")) and finite(v.get("peer_weight"))
        else anchor
    )
    section_a = "\n".join([
        "#### 7.2A Peer Valuation Sanity Check：同業估值限制與品質",
        "",
        "同業只作 sanity check，不可直接決定 fair。台股目前以同業 trailing P/E 對 current-TTM 模型作限制；未取得同業 Forward P/E 時不得混稱。",
        "",
        "| 項目 | 數值 | 公式 / 定義 | 處理 |",
        "|---|---:|---|---|",
        "| Peer Median Forward P/E | Missing Data | 未取得同業同日 forward EPS/P/E | 不使用、不反推 |",
        f"| Peer Median Trailing P/E | {fmt(peer.get('median'))}x | 同產業官方 trailing P/E 中位數；樣本 {fmt(peer.get('count'), 0)} | 只作 current-TTM sanity check |",
        f"| Peer Clamp Lower Bound | {fmt(lower)}x | Historical Conservative Anchor × 75% | 限制同業下緣 |",
        f"| Peer Clamp Upper Bound | {fmt(upper)}x | Historical Conservative Anchor × 125% | 限制同業上緣 |",
        f"| Peer-clamped Trailing P/E | {fmt(v.get('peer_clamped_pe'))}x | clamp(Peer Median Trailing P/E, Lower, Upper) | 權重 {fmt(v.get('peer_weight', 0)*100, 0, '%')}；只准降低或驗證 Conservative fair，不得抬高超過自身歷史錨 |",
        f"| Peer Dispersion Ratio | {fmt(dispersion)}x | max(peer trailing P/E) / min(peer trailing P/E) | 品質：{peer_quality}；高分散時降權 |",
        f"| Normalized Historical Anchor | {fmt(anchor)}x | median({fmt(p50_2y)}x, {fmt(p50_3y)}x) | 2Y／3Y point-in-time P50 正常化錨 |",
        f"| Blended Conservative P/E | {fmt(blended_pe)}x | {fmt(anchor)} × {fmt(100-peer_weight_pct,0)}% + {fmt(v.get('peer_clamped_pe'))} × {fmt(peer_weight_pct,0)}% | 同業只作受限 sanity check |",
        f"| **Final Conservative P/E** | **{fmt(v.get('conservative_pe'))}x** | min(Normalized Anchor {fmt(anchor)}x, Blended {fmt(blended_pe)}x) | 同業不得把 Conservative P/E 抬高 |",
        f"| **Conservative Fair** | **{fmt(v.get('conservative_fair'))}** | TTM EPS {fmt(ttm,2)} × Conservative P/E {fmt(v.get('conservative_pe'))}x | 已實現獲利的防守合理價 |",
    ])

    # 7.2B Growth pass-through.
    section_b = "\n".join([
        "#### 7.2B Growth Pass-through Valuation：EPS 成長反映模型",
        "",
        "目的：衡量市場應該把 Forward EPS 成長反映多少到股價。q 由 FES-Lite 決定，不可因股價上漲人工提高。",
        "",
        "| 變數 | 數值 | 公式 | 定義 |",
        "|---|---:|---|---|",
        f"| Current Price | {fmt(current)} | {d.get('latest_date')} 正式收盤價 | 所有估值層與 market-implied q 的比較基準 |",
        f"| Valuation EPS | {fmt(fwd_eps, 2)} | 有效 consensus/broker；否則 L2Q fallback | {fwd.get('type')}；不是 Conservative baseline |",
        f"| EPS Growth Bridge | {fmt(growth_bridge * 100 if finite(growth_bridge) else math.nan, 1, '%')} | Valuation EPS / TTM EPS - 1 | forward 分母相對已實現 TTM 的成長橋 |",
        f"| Internal Growth Multiple | {fmt(anchor)}x | median(2Y, 3Y point-in-time P/E P50) | 正常化估值錨；每日使用當時市場可知 TTM EPS |",
        f"| Recent 1Y Rerating Check | {fmt(recent)}x | 1Y point-in-time P/E P50 | 只檢查近期重估，不直接進 Conservative fair |",
        f"| 1Y Regime Change | {fmt(to_float(v.get('recent_rerating_change'))*100,1,'%')} | 1Y P50 ÷ Normalized Anchor − 1 | {v.get('recent_rerating_status')} |",
        f"| Short Crowding Change | {fmt(to_float(v.get('short_crowding_change'))*100,1,'%')} | 3M P50 ÷ 6M P50 − 1 | {v.get('short_crowding_status')} |",
        f"| Conservative Fair Price | {fmt(v.get('conservative_fair'))} | TTM EPS × Conservative P/E | 防守型合理價 |",
        f"| Full Growth Anchor Price | {fmt(v.get('forward_growth_anchor'))} | Valuation EPS × Internal Growth Multiple | forward 完全兌現的 proxy 上限情境 |",
        f"| Growth Gap | {fmt(growth_gap)} | Full Growth Anchor - Conservative Fair | 可爭議的成長定價空間 |",
        f"| Market-implied q | {market_q_text} | (Current Price - Conservative Fair) / Growth Gap | 現價已反映多少 growth gap；可高於 100% |",
        "",
        "| q 節點 | 價格 | 公式 | 定義 |",
        "|---|---:|---|---|",
        f"| Growth Fair q=25% | {fmt(ladder.get('q25'))} | Conservative Fair + 25% × Growth Gap | 成長低度反映 |",
        f"| Growth Fair q=35% | {fmt(ladder.get('q35'))} | Conservative Fair + 35% × Growth Gap | 成長部分反映 |",
        f"| Growth Fair q=50% | {fmt(ladder.get('q50'))} | Conservative Fair + 50% × Growth Gap | 成長中度反映 |",
        f"| Growth Fair q=65% | {fmt(ladder.get('q65'))} | Conservative Fair + 65% × Growth Gap | 成長高度反映 |",
        f"| Growth Fair q=75% | {fmt(ladder.get('q75'))} | Conservative Fair + 75% × Growth Gap | 成長充分反映 |",
        "",
        f"Recent rerating check：1Y point-in-time P50 {fmt(recent)}x，相對 2Y/3Y 正常化錨 {fmt(anchor)}x 為 {fmt(to_float(v.get('recent_rerating_ratio')) * 100, 1, '%')}。1Y 高於正常化錨只標示近期 rerating / crowded trade，不因此提高 Conservative P/E 或 q。",
        "",
        f"自動判讀：1Y regime = **{v.get('recent_rerating_status')}**（{fmt(to_float(v.get('recent_rerating_change'))*100,1,'%')}）；3M／6M short crowding = **{v.get('short_crowding_status')}**（{fmt(to_float(v.get('short_crowding_change'))*100,1,'%')}）。短線判讀只影響擁擠與風控，不提高 Conservative Fair。",
    ])

    # 7.2C FES-Lite.
    fm, rm = fets.get("modules") or {}, res.get("modules") or {}
    fes_a = _score_0_2(fm.get("eps"), 12, 6)
    fes_b = _score_0_2(rm.get("orders_capacity"), 7, 1)
    fes_c = _score_0_2(fm.get("revenue"), 12, 6)
    margin_cash = to_float(fm.get("margin")) + to_float(fm.get("cash_flow"))
    fes_d = 2 if margin_cash >= 15 else 1 if margin_cash > 0 else 0
    peer_available = to_float(peer.get("count")) >= 5
    fes_e = 2 if peer_available and finite(v.get("trust_adjusted_fair")) and current <= to_float(v.get("trust_adjusted_fair")) else (
        1 if peer_available and finite(v.get("forward_growth_anchor")) and current <= to_float(v.get("forward_growth_anchor")) else 0
    )
    fes_total = fes_a + fes_b + fes_c + fes_d + fes_e
    q_from_fes = 0.25 if fes_total <= 2 else 0.35 if fes_total <= 4 else 0.50 if fes_total <= 6 else 0.65 if fes_total <= 8 else 0.75
    q_final = min(q_from_fes, to_float(fets.get("q_final")) if finite(fets.get("q_final")) else q_from_fes)
    forward_date = forward_ev.get("source_date") or d.get("valuation_date_fmt") or ""
    forward_title = str(forward_ev.get("source_title") or f"{fwd.get('type')} EPS evidence").replace("|", "/")
    forward_text = str(forward_ev.get("note") or f"Forward EPS {fmt(fwd_eps, 2)}；type {fwd.get('type')}").replace("|", "/")
    forward_url = forward_ev.get("source_url") or forward_ev.get("url")
    evidence_rows = [
        f"| forward_eps | {forward_date or 'Missing Data'} | {forward_text} | {'正向' if finite(growth_bridge) and growth_bridge > 0 else '中性/負向'} | {_source_link(forward_url, forward_title)} |",
        f"| revenue_conversion | {d.get('revenue_month_fmt') or 'Missing Data'} | 3M revenue YoY {fmt(d.get('rev3m_yoy'), 1, '%')}；acceleration {fmt(d.get('rev_accel'), 1)} | {'正向' if to_float(d.get('rev3m_yoy')) > 0 else '負向'} | {_source_link(mops_url, 'MOPS')} |",
        f"| customer_capex_demand | {d.get('price_date_fmt') or 'Missing Data'} | Google CapEx 受惠鏈為研究假設；不等同公司已取得 Google 訂單 | 中性 | Missing Data |",
    ]
    section_c = "\n".join([
        "#### 7.2C FES-Lite：批次版基本面證據分數",
        "",
        "批次版基本面證據分數：FES-Lite = A + B + C + D + E；每模組 0–2 分，合計 0–10 分。每檔最多列 3 條核心 evidence。",
        "",
        "| 模組 | 分數 | 定義 |",
        "|---|---:|---|",
        f"| A. EPS / guidance | {fes_a}/2 | EPS 或公司 guidance 是否支持未來 EPS 成長 |",
        f"| B. Orders / backlog / demand | {fes_b}/2 | 未來營收是否有 orders、backlog、book-to-bill 或需求支撐 |",
        f"| C. Revenue conversion | {fes_c}/2 | demand 是否已開始轉成月營收 |",
        f"| D. Margin / FCF | {fes_d}/2 | 成長是否轉成 margin、EPS quality 或 FCF |",
        f"| E. Valuation / peer sanity | {fes_e}/2 | 現價與 Growth Fair，以及同業估值是否支持 |",
        f"| **合計** | **{fes_total}/10** | q_from_FES {fmt(q_from_fes*100, 0, '%')}；q_final {fmt(q_final*100, 0, '%')} |",
        "",
        f"Hard caps：{'; '.join(reason for reason, _ in fets.get('hard_caps', [])) or '無'}。",
        "",
        "| source type | source date | metric / value / reason | direction | source link |",
        "|---|---|---|---|---|",
        *evidence_rows,
    ])

    # 7.2D Integrated ladder.
    node_rows = [
        ("Bear Stress", v.get("stress_price"), "Conservative Fair × 75%", "thesis 受壓時的風險檢查", "跌破需檢查 price stop 與 thesis stop"),
        ("Value Entry", v.get("conservative_entry"), "Conservative Fair × 85%", "不依賴 Growth 的價值研究區", "thesis intact 才分批研究"),
        ("Conservative Fair", v.get("conservative_fair"), "TTM EPS × Conservative P/E", "防守型合理價", "低於此線才是價值型研究區"),
        ("Trust-adjusted Fair", v.get("trust_adjusted_fair"), "Trust-adjusted EPS × Internal Growth Multiple", "FETS 折扣後的成長合理價", "主成長價格參考"),
        ("Forward Growth Anchor", v.get("forward_growth_anchor"), "Forward EPS × Internal Growth Multiple", "forward 完全兌現的 proxy 情境", "樂觀上緣，不是 base fair"),
        ("Current Price", current, "基準日收盤價", f"隱含 q {market_q_text}", "與本表唯一主階梯比較"),
    ]
    node_lines = [
        f"| {name} | {fmt(price) if finite(price) else '不適用'} | {formula} | {definition} | {action} |"
        for name, price, formula, definition, action in node_rows
    ]
    section_d = "\n".join([
        "#### 7.2D Integrated Price Ladder：整合價格階梯與操作規則",
        "",
        "**本表是全報告唯一的主價格階梯。** 歷史 P/E 分位只用來產生倍數與判斷擁擠，不是另一套進出場價。",
        "",
        "| Node | Price | Formula | Definition | Action meaning |",
        "|---|---:|---|---|---|",
        *node_lines,
        "",
        f"估值結論：目前價格 {fmt(current)}；Conservative Fair {fmt(v.get('conservative_fair'))}；Market-implied q {market_q_text}；FES-Lite {fes_total}/10，q_final {fmt(q_final*100, 0, '%')}。",
        "",
        "| Action | Rule |",
        "|---|---|",
        f"| 新買 | {v.get('action')} |",
        f"| 續抱 | {'可續抱但不追價' if current >= to_float(v.get('trust_adjusted_fair')) else '依 thesis 與 FETS 續抱'} |",
        f"| 停損 | Stress {fmt(v.get('stress_price'))} 是 thesis review 線；EPS、營收、margin、FCF 或訂單 thesis broken 時重估 |",
    ])

    # 7.2E EPS layers.
    trust_eps = to_float(v.get("trust_adjusted_eps"))
    trust_pe = to_float(v.get("trust_adjusted_fair")) / trust_eps if finite(trust_eps) and trust_eps != 0 else math.nan
    section_e = "\n".join([
        "#### 7.2E EPS Valuation Layer：Conservative / Trust-adjusted / Forward Fair",
        "",
        "三層估值：Conservative fair 回答已實現 TTM 值多少；Trust-adjusted fair 回答 FETS 支持相信幾成；Forward fair 欄位在台股為 Forward growth anchor proxy。",
        "",
        f"Historical forward P/E input：{fmt(anchor)}x；basis：median(2Y, 3Y point-in-time P/E P50) normalized anchor；true historical forward P/E unavailable。FETS {fmt(fets.get('score'), 0)}/100，Trust {fmt(fets.get('trust_pct', 0)*100, 0, '%')}。",
        "",
        "| Layer | EPS | P/E | Price | Meaning |",
        "|---|---:|---:|---:|---|",
        f"| Current market | - | {fmt(current/ttm if finite(current) and finite(ttm) and ttm != 0 else math.nan)}x trailing | {fmt(current)} | 基準日 {d.get('latest_date')} 正式現價 |",
        f"| Conservative fair | {fmt(ttm, 2)} | {fmt(v.get('conservative_pe'))}x | {fmt(v.get('conservative_fair'))} | reported TTM baseline |",
        f"| Trust-adjusted fair | {fmt(trust_eps, 2)} | {fmt(trust_pe)}x | {fmt(v.get('trust_adjusted_fair'))} | FETS 折扣 Forward EPS growth gap |",
        f"| Forward fair / growth anchor proxy | {fmt(fwd_eps, 2)} | {fmt(anchor)}x | {fmt(v.get('forward_growth_anchor'))} | forward 完全兌現；不是 true historical forward P/E |",
        "",
        "Historical forward P/E unavailable；Forward fair 使用 historical current-TTM P/E proxy，信心依 forward source quality 降權。",
    ])

    # 7.2F Detailed FETS.
    fets_specs = [
        ("Revenue validation", "revenue", 15, d.get("revenue_month_fmt"), "MOPS monthly revenue", f"3M YoY {fmt(d.get('rev3m_yoy'),1,'%')}；acceleration {fmt(d.get('rev_accel'),1)}", "用最新月營收驗證 forward EPS", mops_url),
        ("EPS validation", "eps", 15, d.get("valuation_date_fmt"), "MOPS EPS history", f"TTM {fmt(ttm,2)}；last FY {fmt(v.get('last_fy_eps'),2)}；L2Q {fmt(v.get('l2q_annualized_eps'),2)}", "用已實現 EPS 與 run-rate 驗證 forward EPS", mops_url),
        ("Margin validation", "margin", 12, d.get("valuation_date_fmt"), "Latest quarterly income statement", f"GM {fmt(d.get('gross_margin'),1,'%')}；OM {fmt(d.get('op_margin'),1,'%')}；YoY/QoQ bridge {'available' if finite(d.get('gm_yoy_change')) else 'Missing Data'}", "確認成長是否進入 margin", mops_url),
        ("Cash-flow quality", "cash_flow", 10, "", "Missing Data", "OCF/NI、FCF、應收與存貨 Missing Data", "確認 EPS 成長的現金流品質", None),
        ("Balance sheet risk", "balance_sheet", 10, d.get("valuation_date_fmt"), "Latest balance sheet", f"Debt/Equity {fmt(d.get('debt_equity'),2)}；Current ratio {fmt(d.get('current_ratio'),2)}", "檢查 leverage 與流動性", mops_url),
        ("Guidance / management tone", "guidance", 8, "", "Missing Data", "公司 guidance Missing Data", "公司 guidance 是否支持 forward EPS；分析師共識不可冒充公司 guidance", None),
        ("Forward EPS source quality", "forward_source_quality", 15, forward_date, forward_title, f"{fwd.get('type')}；EPS {fmt(fwd_eps,2)}；source count {fwd.get('source_count',0)}；age {fmt(fwd.get('age_days'),0)}", "直接 consensus 優於 L2Q fallback", forward_url),
        ("EPS revision evidence", "eps_revision", 10, forward_date, "FactSet current-year EPS revision" if finite(d.get("forward_eps_revision_pct")) else "Missing Data", f"current-year consensus revision {fmt(d.get('forward_eps_revision_pct') * 100 if finite(d.get('forward_eps_revision_pct')) else math.nan, 1, '%')}", "估計修正是 forward EPS 信任 bonus；上修與下修分開計分", forward_url if finite(d.get("forward_eps_revision_pct")) else None),
        ("Estimate reliability", "estimate_reliability", 5, forward_date, forward_title if forward_ev else "Missing Data", f"analyst/source count {fwd.get('source_count',0)}；current-year dispersion {fmt(d.get('forward_eps_dispersion') * 100 if finite(d.get('forward_eps_dispersion')) else math.nan,1,'%')}", "來源數與同快照高低估範圍共同衡量可靠度", forward_url),
    ]
    fets_rows = []
    for category, key, maximum, source_date, title, excerpt, rationale, url in fets_specs:
        score = to_float(fm.get(key))
        selected = excerpt if excerpt else "Missing Data"
        fets_rows.append(
            f"| {category} | {selected} | {fmt(score,1)} / {maximum} | {source_date or 'Missing Data'} | {title or 'Missing Data'} | {excerpt or 'Missing Data'} | {rationale} | {_source_link(url)} |"
        )
    section_f = "\n".join([
        "#### 7.2F FETS：Forward EPS Trust Score",
        "",
        f"FETS = {fmt(fets.get('score'),1)}/100；Trust {fmt(fets.get('trust_pct',0)*100,1,'%')}；evidence completeness {fmt(fets.get('evidence_completeness'),0,'%')}；confidence {fets.get('confidence')}。",
        "",
        "| category | selected_option | score | source_date | source_title | raw_text_excerpt | rationale | source_url |",
        "|---|---|---:|---|---|---|---|---|",
        *fets_rows,
        "",
        "| Derived output | Value | Formula |",
        "|---|---:|---|",
        f"| Trust-adjusted EPS | {fmt(trust_eps,2)} | TTM EPS + Trust% × (Forward EPS - TTM EPS) |",
        f"| Trust-adjusted fair | {fmt(v.get('trust_adjusted_fair'))} | Conservative fair + Trust% × Growth gap |",
    ])

    # 7.2G Detailed RES.
    qev = d.get("res_qualitative_evidence") or {}
    iev = d.get("res_industry_evidence") or {}
    etypes = d.get("res_evidence_types") or {}
    def qualitative_spec(key: str, missing_text: str) -> tuple[str, str, str, str | None]:
        ev = qev.get(key) or {}
        return (
            str(ev.get("excerpt") or missing_text),
            str(ev.get("source_date") or ""),
            str(ev.get("source_title") or "Missing Data"),
            ev.get("source_url"),
        )
    guidance_text, guidance_date, guidance_title, guidance_url = qualitative_spec("consensus_guidance", "有限搜尋後仍無公司 guidance")
    orders_text, orders_date, orders_title, orders_url = qualitative_spec("orders_capacity", "有限搜尋後仍無公司 backlog / order visibility")
    pricing_text, pricing_date, pricing_title, pricing_url = qualitative_spec("pricing_power", "有限搜尋後仍無 ASP / 漲價 / 產能限制證據")
    fcf_value = to_float(d.get("fcf"))
    ocf_ni_value = to_float(d.get("ocf_to_ni"))
    structured_fin_url = d.get("res_financial_source_url") or mops_url
    structured_fin_title = d.get("res_financial_source") or "MOPS structured financial statements"
    structured_fin_period = d.get("res_financial_period") or d.get("valuation_date_fmt")
    res_specs = [
        ("EPS acceleration", "eps_acceleration", 15, f"{d.get('financial_q')} EPS {fmt(d.get('latest_quarter_eps'),2)} vs {d.get('eps_prior_year_quarter')} {fmt(d.get('eps_prior_year_quarter_value'),2)}；YoY {fmt(d.get('eps_latest_yoy')*100 if finite(d.get('eps_latest_yoy')) else math.nan,1,'%')}", d.get("valuation_date_fmt"), "MOPS quarterly EPS history", mops_url),
        ("Revenue acceleration", "revenue_acceleration", 15, f"3M monthly revenue YoY {fmt(d.get('rev3m_yoy'),1,'%')}；3M-vs-6M acceleration {fmt(d.get('rev_accel'),1)}", d.get("revenue_month_fmt"), "MOPS monthly revenue", mops_url),
        ("Margin expansion", "margin_expansion", 12, f"GM YoY {fmt(d.get('gm_yoy_change'),1,'ppt')} / QoQ {fmt(d.get('gm_qoq_change'),1,'ppt')}；OM YoY {fmt(d.get('om_yoy_change'),1,'ppt')} / QoQ {fmt(d.get('om_qoq_change'),1,'ppt')}；NM YoY {fmt(d.get('nm_yoy_change'),1,'ppt')}", structured_fin_period, structured_fin_title, structured_fin_url),
        ("FCF support", "cash_flow", 10, f"OCF {fmt(d.get('ocf'))}；CapEx {fmt(d.get('capex'))}；FCF = OCF - absolute CapEx = {fmt(fcf_value)}；OCF/NI {fmt(ocf_ni_value,2)}", d.get("res_cash_flow_period") or structured_fin_period, structured_fin_title, structured_fin_url),
        ("Balance sheet / ROE support", "balance_roe", 8, f"Debt/Equity {fmt(d.get('debt_equity'),2)}；Current ratio {fmt(d.get('current_ratio'),2)}；annualized ROE proxy {fmt(d.get('roe_annualized'),1,'%')}", d.get("valuation_date_fmt"), "TWSE / TPEx balance sheet + income statement", mops_url),
        ("Guidance confirmation", "consensus_guidance", 10, guidance_text, guidance_date, guidance_title, guidance_url),
        ("Industry confirmation", "industry", 10, str(iev.get("excerpt") or "產業 proxy evidence；不等同公司訂單"), str(iev.get("source_date") or d.get("price_date_fmt") or ""), str(iev.get("source_title") or "Industry proxy"), iev.get("source_url")),
        ("Backlog / order visibility", "orders_capacity", 10, orders_text, orders_date, orders_title, orders_url),
        ("Pricing power / supply constraint", "pricing_power", 10, pricing_text, pricing_date, pricing_title, pricing_url),
    ]
    res_rows = []
    for category, key, maximum, excerpt, source_date, title, url in res_specs:
        score = to_float(rm.get(key))
        res_rows.append(
            f"| {category} | {excerpt} | {fmt(score,1)} / {maximum} | {etypes.get(key, 'Missing')} | {source_date or 'Missing Data'} | {title} | {excerpt} | {'由結構化財務資料計算' if etypes.get(key) == 'Calculated' else '直接證據優先；proxy 不等同公司訂單' if etypes.get(key) in ('Direct','Proxy') else '官方資料與有限搜尋後仍無法取得'} | {_source_link(url)} |"
        )
    evidence_count = int(res.get("evidence_completeness") or 0)
    res_conf = res.get("confidence") or "Low"
    section_g = "\n".join([
        "#### 7.2G RES：Rerating Evidence Score",
        "",
        f"RES = {fmt(res.get('score'),1)}/100；Status：{res.get('status')}；evidence completeness {evidence_count}/9；confidence {res_conf}。",
        "",
        (f"**{res.get('conclusion')}**" if res.get("conclusion") else "Quantitative evidence is calculated first; qualitative gaps remain explicitly separated."),
        "",
        "| category | selected_option | score | evidence_type | source_date | source_title | raw_text_excerpt | rationale | source_url |",
        "|---|---|---:|---|---|---|---|---|---|",
        *res_rows,
    ])

    # 7.2H Entry/Stop/Zone.
    section_h = "\n".join([
        "#### 7.2H Entry / Stop / Price Zone",
        "",
        "本節只解讀 7.2D 的主階梯，不再建立第二套 Entry／Stop 價格。",
        "",
        "| 價格位置 | 意義 |",
        "|---|---|",
        "| < Conservative fair | 便宜，但要確認 thesis |",
        "| Conservative fair–Trust-adjusted fair | 合理偏低 / partial forward EPS priced |",
        "| Trust-adjusted fair–Forward growth anchor | 已反映較多 forward EPS |",
        "| > Forward growth anchor | 必須看 RES；Confirmed rerating 才能視為有充分重估證據，否則維持 Evidence improving / Likely overheat / Insufficient evidence |",
        "",
        f"目前 Price Zone：**{v.get('price_zone')}**。Stop loss 是 thesis review 或風險預算線，不是單純固定百分比。",
    ])
    return "\n\n".join([section_a, section_b, section_c, section_d, section_e, section_f, section_g, section_h])


def tw_rerating_model_table(d: dict[str, Any]) -> str:
    v = d["valuation"]
    if not v:
        return "#### 7.2A 台股 Rerating Model\n\n未取得足夠 EPS/P/E，無法計算 Rerating Model。"
    return "\n".join([
        "#### 7.2A 台股 Rerating Model（傳統合理價與市場 regime 分離）",
        "",
        f"目前價格：{fmt(d.get('latest_close'))}；狀態：{v['rerating_classification']}；Rerating 成立度 {fmt(v['rerating_activation_score'], 0)}/100。固定 50% 是估值情境混合權重，成立度只作可信度判讀，不會改變 Fair 公式。",
        "",
        "| 項目 | P/E | 對應價格 | 用途 |",
        "|---|---:|---:|---|",
        f"| Traditional Fair | {fmt(v['fair_pe'])}x | {fmt(v['fair_price'])} | 主要合理價錨；自身歷史 + 受限同業 |",
        f"| 近期原始錨點 | {fmt(v['recent_raw_anchor'])}x | {fmt(to_float(d['eps_used']) * v['recent_raw_anchor'] if finite(v['recent_raw_anchor']) else math.nan)} | median(3M、6M P50) |",
        f"| 近期有效錨點 | {fmt(v['recent_effective_anchor'])}x | {fmt(to_float(d['eps_used']) * v['recent_effective_anchor'] if finite(v['recent_effective_anchor']) else math.nan)} | min(近期 P50, 1Y P90)，避免短線過熱直接抬高 fair |",
        f"| Rerating Fair | {fmt(v['rerating_fair_pe'])}x | {fmt(v['rerating_fair_price'])} | Traditional Fair ×50% + 近期有效錨點 ×50% |",
        f"| Regime P75 | {fmt(v['regime_p75_pe'])}x | {fmt(v['regime_p75_price'])} | median(3M、6M P75)；近期市場常態上緣，不是內在價值 |",
        f"| Overheat P90 | {fmt(v['rerating_overheat_p90_pe'])}x | {fmt(v['rerating_overheat_p90_price'])} | median(3M、6M P90)；高於此線需新一輪營收/EPS/margin 上修 |",
        "",
        "| 成立度構成 | 分數 | 說明 |",
        "|---|---:|---|",
        f"| 市場 regime | {fmt(v['rerating_market_score'], 0)}/40 | 3M/6M P50 是否高於 Traditional Fair、近期有效錨點、20D/60D 趨勢 |",
        f"| 基本面證據 | {fmt(v['rerating_fundamental_score'], 0)}/40 | 3M 營收 YoY、營收加速度、正成長月數、EPS、營益率、低基期提醒 |",
        f"| 籌碼/過熱扣分 | -{fmt(v['rerating_risk_deduction'], 0)}/20 | 融資使用率、52W 高位、流動性與高於 regime 線風險 |",
        f"| 合計 | {fmt(v['rerating_activation_score'], 0)}/100 | 規則型成立度，不是歷史校準機率 |",
    ])


def eps_scenarios(d: dict[str, Any]) -> list[tuple[str, float]]:
    base = to_float(d.get("eps_used"))
    if math.isnan(base):
        return []
    return [("Bear", base * 0.85), ("Base", base), ("Bull", base * 1.15)]


def scenario_prices(d: dict[str, Any], eps: float) -> dict[str, float]:
    v = d["valuation"]
    return {
        "stress": eps * v["stress_pe"],
        "entry": eps * v["entry_pe"],
        "fair": eps * v["fair_pe"],
        "overheat": eps * v["overheat_pe"],
        "latest_pe": eps * v["latest_pe"],
    }


def current_position_text(current: float, prices: dict[str, float]) -> str:
    if math.isnan(current):
        return "缺現價"
    if current <= prices["stress"]:
        return f"低於 Stress {fmt_pct((current / prices['stress'] - 1) * 100)}"
    if current <= prices["entry"]:
        return "Stress~Entry"
    if current <= prices["fair"]:
        return "Entry~Fair"
    if current <= prices["overheat"]:
        return "Fair~Overheat"
    return f"高於 Overheat {fmt_pct((current / prices['overheat'] - 1) * 100)}"


def implied_pricing_scenario(d: dict[str, Any]) -> str:
    scenarios = eps_scenarios(d)
    if not scenarios:
        return "未取得 EPS，無法判斷現價隱含情境。"
    current = to_float(d["latest_close"])
    if math.isnan(current):
        return "缺最新價，無法判斷現價隱含情境。"
    price_map = {name: scenario_prices(d, eps) for name, eps in scenarios}
    bear_fair = price_map["Bear"]["fair"]
    base_fair = price_map["Base"]["fair"]
    bull_fair = price_map["Bull"]["fair"]
    bull_overheat = price_map["Bull"]["overheat"]
    base_overheat = price_map["Base"]["overheat"]

    if current > bull_overheat:
        label = "高於 Bull 過熱"
        note = "市場定價比樂觀情境還激進；除非 EPS/margin 再上修，否則不追。"
    elif current >= bull_overheat * 0.98:
        label = "接近 Bull 過熱"
        note = "市場已接近用樂觀 EPS 加高估值定價，持有者要檢查停利。"
    elif current >= bull_fair:
        label = "Bull 情境"
        note = "市場在押樂觀 EPS 或估值重評，後續要靠財報兌現。"
    elif current >= base_overheat:
        label = "Base 過熱、往 Bull 定價"
        note = "以基本 EPS 看已偏熱，但還沒完全進入 Bull 合理區。"
    elif current >= base_fair:
        label = "Base 情境偏高"
        note = "現價高於基本情境合理價，新增部位需要等回測。"
    elif current >= bear_fair:
        label = "Bear/Base 之間"
        note = "市場沒有完全給到基本情境，若 thesis intact 才有研究價值。"
    else:
        label = "Bear 情境或更低"
        note = "市場用悲觀情境定價；要先確認不是基本面壞掉。"

    nearest = min(
        ((name, abs(current - price_map[name]["fair"])) for name, _ in scenarios),
        key=lambda x: x[1],
    )[0]
    return f"{label}；最接近 {nearest} Fair 價。{note}"


def implied_pricing_label(d: dict[str, Any]) -> str:
    return implied_pricing_scenario(d).split("；", 1)[0]


def scenario_matrix_table(d: dict[str, Any]) -> str:
    v = d["valuation"]
    scenarios = eps_scenarios(d)
    if not v or not scenarios:
        return "情境價格矩陣：未取得足夠 EPS/P/E。"
    current = to_float(d["latest_close"])
    lines = [
        (
            f"| 情境 | EPS | Stress {fmt(v['stress_pe'])}x | Entry {fmt(v['entry_pe'])}x | "
            f"Fair {fmt(v['fair_pe'])}x | Overheat {fmt(v['overheat_pe'])}x | "
            f"最新 P/E {fmt(v['latest_pe'])}x | 現價 {fmt(current)} 對比 |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for name, eps in scenarios:
        prices = scenario_prices(d, eps)
        lines.append(
            f"| {name} | {fmt(eps, 2)} | {fmt(prices['stress'])} | {fmt(prices['entry'])} | "
            f"{fmt(prices['fair'])} | {fmt(prices['overheat'])} | {fmt(prices['latest_pe'])} | "
            f"{current_position_text(current, prices)} |"
        )
    return "\n".join(lines)


def action_label(d: dict[str, Any]) -> str:
    if d.get("valuation_v2"):
        return str(d["valuation_v2"].get("action") or "估值資料不足")
    v = d["valuation"]
    if not v or not finite(v.get("entry_price")) or not finite(v.get("overheat_price")):
        return "EPS/估值資料不足；不建立目標價或新增部位"
    latest = to_float(d["latest_close"])
    if math.isnan(latest):
        return "缺最新價，僅能研究"
    if latest <= v["entry_price"]:
        return "落入估值進場區；只可小量 starter，需 thesis intact"
    if latest <= v["technical_test_price"]:
        return "接近技術試單區；等月營收/margin 確認"
    if latest >= v["overheat_price"]:
        return "已進過熱減碼區；現價不追，偏續抱/減碼檢查"
    if latest > v["upper_fair_price"]:
        return "高於合理上緣；不追，等回到技術試單或估值區"
    return "在合理區；續抱/研究，新增需等明確驗證"


def entry_zone(d: dict[str, Any]) -> str:
    v = d["valuation"]
    return f"{fmt(v['stress_price'])}-{fmt(v['entry_price'])}" if v else "未取得"


def risk_tag(d: dict[str, Any]) -> str:
    latest = to_float(d["latest_close"])
    v = d["valuation"]
    if v and not math.isnan(latest) and latest >= v["overheat_price"]:
        return "高風險"
    if to_float(d["pos52"]) >= 80 or to_float(d["ret60"]) >= 40:
        return "中高風險"
    return "中風險"


def market_gate_note() -> str:
    return (
        f"市場閘門：{MARKET_REGIME}。說明：本地篩選報告已更新加權指數至 {MARKET_INDEX_DATE}，"
        f"當天發行量加權股價指數 {fmt_pct(MARKET_DAILY_CHANGE_PCT)}，未觸發單日風險閘門。"
        "少數候選的日價歷史仍落後於價格日，操作上仍需依個股旗標確認資料完整性。"
    )


def recent_move_text(d: dict[str, Any]) -> str:
    return f"5D {fmt(d['ret5'], 1, '%')} / 20D {fmt(d['ret20'], 1, '%')} / 60D {fmt(d['ret60'], 1, '%')}"


def bear_base_bull_position(d: dict[str, Any]) -> str:
    """Locate current price against the same three scenario targets as 14.1.4."""
    v = d.get("valuation_v2") or {}
    windows = v.get("proxy_windows") or {}
    current = to_float(d.get("latest_close"))
    ttm = to_float(v.get("ttm_eps"))
    anchor = to_float(v.get("historical_anchor_pe"))
    forward_eps = to_float((v.get("forward") or {}).get("eps"))
    long_p75 = safe_median([
        (windows.get("2Y") or {}).get("p75"),
        (windows.get("3Y") or {}).get("p75"),
    ])
    bear = ttm * .80 * anchor * .75 if finite(ttm) and finite(anchor) else math.nan
    base = to_float(v.get("trust_adjusted_fair"))
    bull_pe = safe_min([anchor * 1.15 if finite(anchor) else math.nan, long_p75])
    bull = forward_eps * bull_pe if finite(forward_eps) and finite(bull_pe) else math.nan
    if not finite(current) or not finite(bear):
        return "情境資料不足"
    if current < bear:
        return f"低於 Bear（{fmt(bear)}）"
    if not finite(base):
        return "Base 情境資料不足"
    if current < base:
        return f"Bear～Base（Base {fmt(base)}）"
    if not finite(bull):
        return f"高於 Base（{fmt(base)}）；Bull不足"
    if current < bull:
        return f"Base～Bull（Bull {fmt(bull)}）"
    return f"高於 Bull（{fmt(bull)}）"


def source_numbers(d: dict[str, Any]) -> str:
    v2 = d.get("valuation_v2") or {}
    forward = v2.get("forward") or {}
    fets = v2.get("fets") or {}
    return "\n".join(
        [
            "| 模組 | 核心數字 | 判斷 |",
            "|---|---|---|",
            f"| 價格/時點 | 候選價 {fmt(d['close'])}（{d['price_date_fmt']}）；日價歷史參考 {fmt(d['latest_close'])}（{d['latest_date']}）；差異 {fmt(d['close_delta'], 1, '%')} | 價格日與最新日價不同，估值只能視為候選日參考 |",
            f"| 成長 | 月營收 YoY {fmt(d['rev_yoy'], 1, '%')}、MoM {fmt(d['rev_mom'], 1, '%')}、3M YoY {fmt(d['rev3m_yoy'], 1, '%')}、加速度 {fmt(d['rev_accel'])} | 月營收是先行線索；要搭配毛利率、營益率與現金流確認有沒有真的變成獲利 |",
            f"| 品質 | Q1 毛利率 {fmt(d['gross_margin'], 1, '%')}、營益率 {fmt(d['op_margin'], 1, '%')}、淨利率 {fmt(d['net_margin'], 1, '%')}、EPS {fmt(d['eps_q'], 2)} | OCF/NI、應收與存貨未取得，品質分不能升級為完整 A-List |",
            f"| EPS/估值 | Reported TTM EPS {fmt(v2.get('ttm_eps'), 2)}；Trailing P/E {fmt(d.get('pe_used'))}x；Forward candidate {fmt(forward.get('eps'), 2)}（{forward.get('type')}）；TW_FETS {fmt(fets.get('score'), 0)}/100 | Conservative fair 只用 reported TTM；consensus/broker/L2Q 只進 forward growth layer |",
            f"| 股價/籌碼 | {recent_move_text(d)}；52W 位置 {fmt(d['pos52'], 1, '%')}、融資使用率 {fmt(d['margin_util'], 1, '%')} | {risk_tag(d)}；越接近高位，越需要等回測或新財報確認，不用排名去追價 |",
            f"| 大盤 | 發行量加權股價指數 {MARKET_INDEX_DATE} 日漲跌 {fmt_pct(MARKET_DAILY_CHANGE_PCT)}；regime {MARKET_REGIME} | 大盤與個股 Price Zone 分開判讀 |",
            f"| 現價情境 | {v2.get('price_zone')} | 依 Conservative／Trust-adjusted／Forward Growth Anchor 三層判斷；不是舊 Bull/Overheat 模型 |",
        ]
    )


def eps_research_refresh_note(d: dict[str, Any]) -> str:
    entry = d.get("full_research_entry") or {}
    refresh = entry.get("eps_research_refresh") or {}
    status = refresh.get("status") or "not_run"
    error = refresh.get("error") or ""
    new_count = refresh.get("new_candidate_count", 0)
    cache_path = refresh.get("cache_path") or str(EPS_RESEARCH_CACHE_PATH)
    searched_at = refresh.get("searched_at") or RUN_DATE
    if status == "ok":
        return f"本次已線上刷新 EPS 研究快取（{searched_at}），新增候選估計 {new_count} 筆；快取：`{cache_path}`。"
    if status == "partial_error":
        return f"本次已嘗試線上刷新 EPS 研究快取，但部分查詢失敗；新增候選估計 {new_count} 筆；錯誤摘要：{error or '未提供'}；快取：`{cache_path}`。"
    if status == "skipped_by_env":
        return f"本次因 `TW_EPS_RESEARCH_REFRESH=0` 跳過線上 EPS refresh；僅使用既有快取/手動 evidence；快取：`{cache_path}`。"
    return f"本次 EPS 線上 refresh 狀態：{status}；快取：`{cache_path}`。"


def supplementary_eps_count(d: dict[str, Any]) -> int:
    entry = d.get("full_research_entry") or {}
    return len([item for item in entry.get("evidence_items") or [] if not item.get("used_for_EPS_used")])


def supplementary_eps_note(d: dict[str, Any]) -> str:
    entry = d.get("full_research_entry") or {}
    items = [item for item in entry.get("evidence_items") or [] if not item.get("used_for_EPS_used")]
    if not items:
        return "未找到額外 EPS 預估；估值僅使用 EPS_used。"
    best = sorted(items, key=lambda item: (str(item.get("source_quality") or "Z"), item.get("source_age_days") if item.get("source_age_days") is not None else 9999))[0]
    return (
        f"已找到額外 EPS evidence {len(items)} 筆；最佳補充："
        f"{best.get('estimate_year')}E EPS {fmt(best.get('eps'), 2)}，"
        f"{best.get('broker_name') or best.get('source_domain') or best.get('source_quality')}；"
        f"Not used: {best.get('excluded_reason') or 'not selected'}"
    )


def supplementary_eps_evidence_section(d: dict[str, Any]) -> str:
    entry = d.get("full_research_entry") or {}
    items = entry.get("evidence_items") or []
    if not items:
        return "尚未保存額外 EPS evidence。"
    rows = []
    for item in sorted(items, key=lambda x: (not bool(x.get("used_for_EPS_used")), str(x.get("estimate_year") or ""), x.get("source_age_days") if x.get("source_age_days") is not None else 9999)):
        used = "是" if item.get("used_for_EPS_used") else "否"
        reason = item.get("excluded_reason") or ("EPS_used 主分母" if item.get("used_for_EPS_used") else "")
        title = str(item.get("source_title") or item.get("source_domain") or item.get("source_name") or "source")[:40].replace("|", " ")
        eps_display = str(item.get("eps_range") or item.get("eps_display") or fmt(item.get("eps"), 2)).replace("|", "/")
        source_nature = str(item.get("source_nature") or item.get("estimate_type") or "").replace("|", "/")
        note = str(item.get("note") or "").replace("|", "/")
        rows.append(
            "| "
            + " | ".join([
                str(item.get("estimate_year") or "未明"),
                eps_display,
                source_nature,
                str(item.get("source_quality") or ""),
                str(item.get("source_date") or ""),
                str(item.get("source_age_days") if item.get("source_age_days") is not None else ""),
                str(item.get("recency_status") or ""),
                str(item.get("broker_name") or ""),
                fmt(item.get("target_price"), 1),
                str(item.get("rating") or ""),
                used,
                reason,
                note,
                f"[{title}]({item.get('source_url') or item.get('url') or '#'})",
            ])
            + " |"
        )
    intro = (
        "EPS_used = 估值主計算使用；補充 EPS 證據 = 額外參考，不一定納入估值。"
        "若 EPS_used 不是 broker EPS，但有找到 broker EPS，通常是因同年度獨立來源不足 3 份、來源過舊或品質不足，僅列為補充證據。"
    )
    return "\n".join([
        intro,
        "",
        "| 年度 | EPS / 區間 | 來源/性質 | 品質 | 日期 | age | recency | broker | 目標價 | rating | 用於EPS_used | excluded_reason | 備註 | 來源 |",
        "|---:|---:|---|---|---|---:|---|---|---:|---|---|---|---|---|",
        *rows,
    ])


def own_pe_proxy_table(d: dict[str, Any]) -> str:
    eps = to_float((d.get("valuation_v2") or {}).get("ttm_eps"))
    windows_map = (d.get("valuation_v2") or {}).get("proxy_windows") or {}
    windows = [{"label": k, **v} for k, v in windows_map.items()]
    if not windows:
        return "自身近期 P/E proxy 資料不足。"
    table_rows = []
    for row in windows:
        table_rows.append(
            f"| {row.get('label')} | {row.get('count')} | {row.get('start') or '未取得'} 至 {row.get('end') or '未取得'} | "
            f"{fmt(row.get('p10'))}x | {fmt(row.get('p50'))}x | {fmt(row.get('p75'))}x | {fmt(row.get('p90'))}x | "
            f"{row.get('confidence')} | {row.get('verification')} |"
        )
    return "\n".join([
        "本表採 point-in-time P/E：每個交易日收盤價 ÷ 當時市場已可知的最近四季 EPS。為避免前視偏誤，季度 EPS 以保守法定申報截止日才視為可用（Q1 5/15、Q2 8/14、Q3 11/14、Q4 次年 3/31）；若公司更早公告，本表不提前使用。",
        "",
        f"當期分母稽核：最新 TTM EPS 為 {fmt(eps, 2)}；quality {(d.get('valuation_v2') or {}).get('ttm_quality')}。Conservative anchor 固定採 2Y／3Y point-in-time P50 中位數；1Y P50 只作近期 rerating check。",
        "",
        "| 窗口 | 價格資料筆數 | 起訖日 | P10 | P50 | P75 | P90 | 可信度 | 驗證 |",
        "|---|---:|---|---:|---:|---:|---:|---|---|",
        *table_rows,
        "",
        "P10／P50／P90 只用來估計歷史倍數位置與擁擠度，不另外換算成進場、合理或減碼價格；正式價格判斷只看 7.2D Integrated Price Ladder。",
    ])


def stock_section(d: dict[str, Any]) -> str:
    bear_lines = "\n".join([f"{i}. {x}" for i, x in enumerate(d["bear"], 1)])
    v = d["valuation"]
    nv = d.get("valuation_v2") or {}
    current = to_float(d.get("latest_close"))
    technical_test = safe_min([to_float(d.get("ma50")), current * .92])
    ma50 = to_float(d.get("ma50"))
    ttm = to_float(nv.get("ttm_eps"))
    conservative_pe = to_float(nv.get("conservative_pe"))
    anchor = to_float(nv.get("historical_anchor_pe"))
    forward_eps = to_float((nv.get("forward") or {}).get("eps"))
    trust = to_float((nv.get("fets") or {}).get("trust_pct"))
    conservative_fair = to_float(nv.get("conservative_fair"))
    forward_anchor = to_float(nv.get("forward_growth_anchor"))
    matrix = "\n".join(
        [
            "| 價格/基本面狀態 | 計算公式（實際代入） | Thesis intact：基本面故事還成立 | Thesis damaged：基本面故事被破壞 |",
            "|---|---|---|---|",
            f"| 現價 {fmt(current)} | {d.get('latest_date')} 正式收盤價 | {nv.get('action')} | 不買；若已持有則減碼／退出 |",
            f"| 技術執行參考 <= {fmt(technical_test)} | min(50DMA {fmt(ma50)}, 現價 {fmt(current)} × 92% = {fmt(current*.92)}) = {fmt(technical_test)} | 僅決定執行節奏，不改變合理價；仍需月營收與 margin 驗證 | 不接刀，等待新財報證據 |",
            f"| Stress／thesis review <= {fmt(nv.get('stress_price'))} | Conservative Fair {fmt(conservative_fair)} × 75% = {fmt(nv.get('stress_price'))} | 低價不是自動買點，先確認 thesis 未受損 | 退出觀察名單或只保留追蹤 |",
            f"| Value Entry {fmt(nv.get('stress_price'))}–{fmt(nv.get('conservative_entry'))} | 下緣 = Fair × 75% = {fmt(nv.get('stress_price'))}；上緣 = Fair × 85% = {fmt(nv.get('conservative_entry'))} | thesis intact 且市場不再 de-risk 時，才分批研究 | 若 thesis 壞，低價不是買點 |",
            f"| Conservative Fair {fmt(conservative_fair)} | TTM EPS {fmt(ttm,2)} × Conservative P/E {fmt(conservative_pe)}x = {fmt(conservative_fair)} | 已實現 TTM 的防守合理價 | thesis damaged 時優先降風險 |",
            f"| Trust-adjusted Fair {fmt(nv.get('trust_adjusted_fair'))} | Fair {fmt(conservative_fair)} + Trust {fmt(trust*100,0,'%')} × (Forward Anchor {fmt(forward_anchor)} − Fair {fmt(conservative_fair)}) = {fmt(nv.get('trust_adjusted_fair'))} | 已反映 FETS 支持的部分 forward 成長 | forward 證據轉弱即回看 Conservative Fair |",
            f"| Forward Growth Anchor >= {fmt(forward_anchor)} | Forward EPS {fmt(forward_eps,2)} × Normalized Anchor {fmt(anchor)}x = {fmt(forward_anchor)} | 只有 RES 為 Confirmed rerating 才能支持；否則不追／減碼檢查 | Thesis damaged 時優先退出 |",
        ]
    )
    return f"""## {d['rank']}. {d['code']} {d['name']} - {d['decision']}

### 公司白話介紹

{d['intro']}

### 1. 一句話結論

{nv.get('action')}。Price Zone：{nv.get('price_zone')}。理由：{d['thesis']} 主要風險：{d['risk']}

### 2. 市場 regime 與投資組合閘門

- {market_gate_note()}
- De-risk 白話：市場風險升高時，先降低追價與新買速度；不是所有股票都要賣，而是買點要更嚴格。
- 投資組合：本輪是台股分析，只檢查台股可用現金、台股持股與同產業曝險；美股部位不納入此台股單股判斷。
- 目前缺口：未取得台幣可用現金、現有台股持股與交易額度，因此不能計算可買股數。

### 3. 產業與國際情勢

- 產業：{d['industry']}；白話類型：{d['type']}。
- 這類股票主要看：營收是否延續、毛利率/營益率是否撐住、股價是否已先反映太多好消息。
- 國際變數：電子/半導體看全球科技景氣與客戶拉貨；航運看運價與大宗物料需求；化工看原料與產品報價；資訊服務看企業 IT 預算。
- 結論：產業題材可以加分，但不能取代 EPS、現金流與估值位置。

### 4. Bear case first

{bear_lines}

Bear case first 白話：先問「我會錯在哪裡」。它不是看空，而是避免只找支持買進的理由。若任一項發生：不加碼；若已持有同族群，先降風險或等正式月營收/季報確認。

### 5. 價格與部位

- 正式候選價格：{fmt(d['close'])}，價格日 {d['price_date_fmt']}，來源為候選 CSV 展開欄位。
- 日價歷史參考：{fmt(d['latest_close'])}，日期 {d['latest_date']}，來源為本地日價歷史快取。
- 目前部位：未取得此台股持股；若沒有持股，所有「減碼」只代表若已持有時的風控動作。

### 6. 來源數字表

{source_numbers(d)}

### 7. EPS 模組

EPS 階層：reported TTM EPS 是 Conservative valuation baseline；同年度 consensus / broker EPS 只作 forward candidate；完全沒有可信 forward EPS 時，最後才用 L2Q annualized 作低信心 run-rate fallback。不同年度的預估不可混算。

| 欄位 | 數值 | 說明 |
|---|---:|---|
| Current price | {fmt(d.get('latest_close'))} | 正式價格日 {d.get('latest_date')}；所有 P/E、Price Zone 與 market-implied q 的現價基準 |
| reported TTM EPS | {fmt((d.get('valuation_v2') or dict()).get('ttm_eps'), 2)} | quality {(d.get('valuation_v2') or dict()).get('ttm_quality')}；{(d.get('valuation_v2') or dict()).get('ttm_source_note')} |
| 114 / 113 / 112 年 EPS | {fmt(d.get('annual_eps_114'), 2)} / {fmt(d.get('annual_eps_113'), 2)} / {fmt(d.get('annual_eps_112'), 2)} | 年度 cycle 與 normalized sanity check，不直接取代 TTM |
| current_year_EPS（{CURRENT_YEAR}E） | {fmt(d.get('current_year_eps'), 2)} | 來源數 {fmt(d.get('current_year_eps_source_count'), 0)}；type {d.get('current_year_eps_type')} |
| next_year_EPS（{NEXT_YEAR}E） | {fmt(d.get('next_year_eps'), 2)} | 來源數 {fmt(d.get('next_year_eps_source_count'), 0)}；type {d.get('next_year_eps_type')} |
| future_year_EPS（{FUTURE_YEAR}E） | {fmt(d.get('future_year_eps'), 2)} | 來源數 {fmt(d.get('future_year_eps_source_count'), 0)}；只揭露，不參與 EPS_used 優先序 |
| latest_quarter_EPS | {fmt(d.get('latest_quarter_eps'), 2)} | 財報季度 {d['financial_q']} |
| previous_quarter_EPS | {fmt(d.get('previous_quarter_eps'), 2)} | 由 screen dataset 或 full research evidence 補入；若未補則不可算 L2Q |
| L2Q_annualized_EPS | {fmt(d.get('l2q_annualized_eps'), 2)} | (latest quarter EPS + previous quarter EPS) × 2；不是最新單季 ×4 |
| forward EPS candidate | {fmt(((d.get('valuation_v2') or dict()).get('forward') or dict()).get('eps'), 2)} | {((d.get('valuation_v2') or dict()).get('forward') or dict()).get('type')}；source count {((d.get('valuation_v2') or dict()).get('forward') or dict()).get('source_count')} |
| trust-adjusted EPS | {fmt((d.get('valuation_v2') or dict()).get('trust_adjusted_eps'), 2)} | TTM + Trust% × (forward candidate − TTM) |
| Trailing P/E | {fmt(d.get('pe_used'))}x | current price / reported TTM EPS |
| supplementary_eps_count | {supplementary_eps_count(d)} | 額外 EPS evidence 筆數；不一定納入 EPS_used |
| supplementary_eps_note | - | {supplementary_eps_note(d)} |

L2Q annualized EPS is a run-rate check only. 若 forward consensus / broker 全部不足，才可作 `L2Q_RUN_RATE_FALLBACK`，且 Trust <=45%；它不是 analyst consensus。

若 forward evidence 完全不足：Trust-adjusted EPS 回到 TTM，且不建立 forward growth anchor。

online_refresh：{eps_research_refresh_note(d)}

嚴格禁止：不能把 {CURRENT_YEAR}E 與 {NEXT_YEAR}E EPS 預估合併計算 count 或 median；1–2 份券商預估只能揭露。最新單季 EPS×4（目前 {fmt(d['q1_annual_eps'], 2)}）不得成為 forward candidate。

Bear/Base/Bull 僅作敏感度；主結論改由 Conservative / Trust-adjusted / Forward growth anchor 三層與 Price Zone 決定。

### 7.1 自身近期 P/E Proxy

{own_pe_proxy_table(d)}

### 7.2 補充 EPS 證據

{supplementary_eps_evidence_section(d)}

### 8. 估值模組

{us_style_tw_valuation_sections(d)}

- 估值結論：Conservative Fair {fmt(nv.get('conservative_fair'))}；Trust-adjusted Fair {fmt(nv.get('trust_adjusted_fair'))}；Forward Growth Anchor {fmt(nv.get('forward_growth_anchor'))}。
- 現價動作：{nv.get('action')}
- P/B 白話：股價相對每股淨值，常用來看資產型、循環股或高位股是不是已經太貴。

### 9. 價格結論（引用 7.2D）

唯一主價格階梯請看 **7.2D Integrated Price Ladder**，本節不再重複列價。現價 {fmt(d['latest_close'])}；Price Zone：{nv.get('price_zone')}；Market-implied q {fmt(nv.get('market_implied_q')*100 if finite(nv.get('market_implied_q')) else math.nan, 1, '%')}。

- 若 forward type 是 L2Q fallback，必須等下一季 EPS、月營收、margin 與 cash conversion 驗證。

### 10. 最後操作建議

本週最佳動作：{nv.get('action')}。若要交易，必須先更新台股可用現金、停損價與單筆風險預算。

### 11. 停損與停利

- 價格風控只引用 7.2D：Value Entry {fmt(nv.get('conservative_entry'))}；Stress / thesis review {fmt(nv.get('stress_price'))}。
- 若只是技術試單：跌破 50D/技術試單區後，若接下來 2-3 個交易日站不回去，代表市場不願意接，停止新增風險。
- Thesis stop：EPS/consensus 下修、月營收轉弱、margin 壓縮、OCF/NI 惡化、存貨/應收暴增或訂單證據消失。大盤大跌時先區分 system de-risk 與 thesis damaged，不機械停損。

### 12. 品質與財報風險

- Margin：Q1 毛利率 {fmt(d['gross_margin'], 1, '%')}、營益率 {fmt(d['op_margin'], 1, '%')}、淨利率 {fmt(d['net_margin'], 1, '%')}。
- 資產負債：流動比率 {fmt(d['current_ratio'], 2)}、負債權益比 {fmt(d['debt_equity'], 2)}。
- OCF/NI 白話：營業現金流 / 淨利，用來確認帳上賺到的錢有沒有真的收成現金。
- 強制缺口：OCF/NI、應收、存貨未取得；不能確認盈餘品質，也不能排除塞貨、庫存或回款風險。

### 13. 低本益比高成長檢查

{d['lowpe']} 必要條件中的 OCF/NI、應收、存貨與近兩季 EPS 未取得，所以只能列 Watch，不可判定為真低估成長。

### 14. Rerating / De-rating 檢查

Rerating 白話是「市場願意給更高估值」；De-rating 是「市場把估值打回低一階」。近期 1Y P/E 只作 rerating check，不直接抬高 Conservative P/E；股價高於 Forward Growth Anchor 時，必須由 RES 驗證。

{multibagger_reassessment(d)}

### 15. 強勢股/崩盤股分類

- 趨勢狀態：{d['trend_state']}；20D {fmt(d['ret20'], 1, '%')}，60D {fmt(d['ret60'], 1, '%')}，52W 位置 {fmt(d['pos52'], 1, '%')}。
- 50D 白話：最近約 50 個交易日的平均價格，可粗略看中期市場成本。
- 分類：強勢股觀察，不是崩盤股；但若市場轉弱或跌破 20D/50D，先降追價意願。

### 16. 部位與風險預算

- 未驗證 thesis starter：單筆虧損上限以總資產 0.1%-0.3% 為上限。
- 台股可用現金、匯率、手續費、現有台股部位：未取得，因此不能算股數。
- 若一定要做，必須先定停損價，再用 `可買股數 = 單筆最大可承受虧損 / (買進價 - 停損價)`。

### 17. 價格 x thesis 決策矩陣

{matrix}

### 18. 下一個驗證點

{d['trigger']} 同時補 OCF/NI、應收、存貨、法人/投信、自營、借券與事件日曆。

### 19. 資料完整性檢查

- 已取得：價格/成交值、P/E、P/B、殖利率、月營收、3M rolling 營收、Q1 margin/EPS、20D/60D/均線/52W 位置、融資融券 proxy、reported TTM 與 forward candidate。
- 已補估值：同產業 current peer P/E、3M／6M／1Y／2Y／3Y point-in-time P/E、2Y／3Y正常化錨、Conservative P/E詳細算式與三層價格。
- 未取得/待補：台股持股與可用現金、部分 OCF/NI／應收帳款／存貨、精確公司申報時間戳、EV/EBITDA、FCF yield、外資／投信／自營、借券與事件日曆。
- 影響：資料信心 {fmt(d['confidence'], 0, '%')}；缺 P0 現金流品質資料，因此買進只能是條件式，不升級成無條件 A-List。

"""


def score_band_text(fundamental: int, price: int) -> str:
    if fundamental >= 56:
        fundamental_band = "高延展：需求、成長與財務已有多項驗證"
    elif fundamental >= 42:
        fundamental_band = "中高延展：論點合理，但仍有關鍵資料待補"
    elif fundamental >= 28:
        fundamental_band = "尚未確立：產業方向可能成立，公司捕獲能力未充分證明"
    else:
        fundamental_band = "偏弱：缺乏持續成長或財務驗證"
    if price >= 23:
        price_band = "現價具吸引力：Base/Bull 尚未充分定價"
    elif price >= 16:
        price_band = "現價中性：有空間，但需要上修或更好的買點"
    elif price >= 9:
        price_band = "現價要求偏高：公司可以很好，但報酬風險普通"
    else:
        price_band = "現價過熱／低容錯：已反映大量 Bull 情境"
    return (
        f"- 基本面分解讀：**{fundamental_band}**。\n"
        f"- 現價分解讀：**{price_band}**。\n"
        "- 組合判讀：基本面高、現價低代表可留核心倉但不代表可追價；"
        "基本面與現價都高，才是較佳新增研究區。"
    )


def leading_signal_markdown(d: dict[str, Any]) -> list[str]:
    """Return actively researched Stage 0–1 signals for the stock and industry."""
    entry = d.get("full_research_entry") or {}
    if entry.get("stage_signals"):
        rendered = []
        for row in entry["stage_signals"]:
            signal = row.get("signal") or row.get("description") or ""
            stage = row.get("stage") or ""
            direction = row.get("direction") or "中性"
            evidence_type = row.get("evidence_type") or row.get("type") or ""
            source = row.get("source") or row.get("source_name") or "來源"
            url = row.get("url") or row.get("source_url") or "#"
            quality = row.get("quality") or row.get("level") or ""
            lead = row.get("lead_time") or row.get("lead") or ""
            verified = row.get("verification") or row.get("verified") or ""
            rendered.append(
                f"| {signal} | {stage} | {direction} | {evidence_type} | [{source}]({url}) | {quality} | {lead} | {verified} |"
            )
        return rendered
    rows = list(CODE_LEADING_SIGNALS.get(d["code"], []))
    rows.extend(LEADING_SIGNAL_LIBRARY.get(d["industry"], []))
    if not rows:
        rows.extend([
            ("客戶 CapEx、產品 roadmap 與終端需求", "Stage 0", "中性", "間接：需求源頭", "MOPS／公司法說／產業主管機關", "https://mops.twse.com.tw/mops/web/index", "D", "12–36 月", "尚未建立產業專屬來源；不得因此假設正面"),
            ("訂單、認證、產能、交期與預付款", "Stage 1", "中性", "直接：商業化", "MOPS重大訊息與公司法說", "https://mops.twse.com.tw/mops/web/t05sr01_1", "D", "3–24 月", "需主動補公司與上下游第二來源"),
        ])
    return [
        f"| {signal} | {stage} | {direction} | {evidence_type} | [{source}]({url}) | {quality} | {lead} | {verified} |"
        for signal, stage, direction, evidence_type, source, url, quality, lead, verified in rows
    ]


def multibagger_reassessment(d: dict[str, Any]) -> str:
    """Detailed post-target reassessment for every Taiwan stock."""
    v = d.get("valuation_v2") or {}
    rev3m = to_float(d.get("rev3m_yoy"))
    gross = to_float(d.get("gross_margin"))
    op_margin = to_float(d.get("op_margin"))
    net_margin = to_float(d.get("net_margin"))
    pe = to_float(d.get("pe_used"))
    eps_used = to_float(d.get("eps_used"))
    latest = to_float(d.get("latest_close"))
    ret60 = to_float(d.get("ret60"))
    debt_equity = to_float(d.get("debt_equity"))
    positive_count = to_float(d.get("positive_count"))
    confidence = to_float(d.get("confidence"))

    def finite(value: Any) -> bool:
        return isinstance(value, (int, float)) and not math.isnan(value)

    demand_score = 2
    if finite(rev3m):
        demand_score = 11 if rev3m >= 30 else 9 if rev3m >= 15 else 7 if rev3m >= 5 else 5 if rev3m > 0 else 2
    supply_score = 4  # No consistent lead-time/capacity dataset in the current input.
    moat_score = 8 if finite(gross) and gross >= 40 else 6 if finite(gross) and gross >= 25 else 4
    commitment_score = 7 if finite(positive_count) and positive_count >= 3 else 5 if finite(positive_count) and positive_count >= 2 else 3
    margin_score = 8 if finite(op_margin) and op_margin >= 15 else 6 if finite(op_margin) and op_margin >= 8 else 4
    financial_score = 9 if finite(eps_used) and finite(net_margin) and finite(rev3m) else 6
    market_share_score = 4 if finite(confidence) and confidence >= 70 else 3
    fundamental_total = sum([
        demand_score, supply_score, moat_score, commitment_score,
        margin_score, financial_score, market_share_score,
    ])

    if not finite(latest):
        price_unpriced = 0
    elif latest <= v["conservative_entry"]:
        price_unpriced = 11
    elif latest <= v["conservative_fair"]:
        price_unpriced = 9
    elif latest <= v["trust_adjusted_fair"]:
        price_unpriced = 6
    elif latest <= v["forward_growth_anchor"]:
        price_unpriced = 3
    else:
        price_unpriced = 0
    valuation_support = 7 if finite(pe) and pe <= v["conservative_pe"] else (
        5 if finite(pe) and pe <= v["historical_anchor_pe"] * 1.15 else 2
    )
    balance_score = 5 if finite(debt_equity) and debt_equity <= 0.7 else 3 if finite(debt_equity) and debt_equity <= 1.5 else 1
    crowding_score = 5 if finite(ret60) and ret60 <= 15 else 3 if finite(ret60) and ret60 <= 40 else 1
    price_total = price_unpriced + valuation_support + balance_score + crowding_score

    fundamental_rows = [
        ("需求不可逆性與市場空間", demand_score, 12, f"近 3 月營收 YoY {fmt(rev3m, 1, '%')}", "仍需客戶、政策或終端需求交叉驗證"),
        ("供給瓶頸與擴產難度", supply_score, 10, "檢查交期、產能、認證、良率與擴產時程", "目前輸入沒有一致的交期/產能資料，因此限制分數"),
        ("技術、認證與客戶護城河", moat_score, 10, d["type"], "需確認客戶集中、切換成本與替代方案"),
        ("客戶承諾、訂單與 backlog", commitment_score, 10, f"近 3 月 YoY 正成長月數 {fmt(positive_count, 0)}", "月營收不等於合約或 backlog，不可給滿分"),
        ("ASP、margin 與營運槓桿", margin_score, 10, f"毛利率 {fmt(gross, 1, '%')}；營益率 {fmt(op_margin, 1, '%')}", "缺逐季 ASP 與 margin bridge"),
        ("營收、EPS 與現金流驗證", financial_score, 12, f"EPS_used {fmt(eps_used, 2)}（{d.get('eps_type')}）；淨利率 {fmt(net_margin, 1, '%')}", "OCF/NI、存貨與應收未取得"),
        ("市占率與競爭優勢", market_share_score, 6, d["thesis"], "缺正式市占率與競爭者量化資料"),
    ]
    price_rows = [
        ("現價尚未反映 Base/Bull", price_unpriced, 12, f"現價 {fmt(latest)}；Trust-adjusted fair {fmt(v['trust_adjusted_fair'])}", "現價越接近 Forward Growth Anchor，分數越低"),
        ("估值下檔保護", valuation_support, 8, f"Trailing P/E {fmt(pe)}；Conservative P/E {fmt(v['conservative_pe'])}", "若 TTM 品質或 point-in-time 樣本不足，估值信心下降"),
        ("稀釋、負債與資本需求", balance_score, 5, f"負債權益比 {fmt(debt_equity, 2)}", "缺完整淨負債、增資與資本支出橋"),
        ("擁擠度、預期門檻與時程", crowding_score, 5, f"60D {fmt(ret60, 1, '%')}；52W 位置 {fmt(d.get('pos52'), 1, '%')}", "急漲或高檔利多鈍化時扣分"),
    ]
    fundamental_table = "\n".join(
        ["| 基本面延展類別 | 分數 | 支持證據 | 扣分／待驗證 |", "|---|---:|---|---|"]
        + [f"| {label} | {score}/{maximum} | {support} | {deduction} |" for label, score, maximum, support, deduction in fundamental_rows]
        + [f"| **基本面合計** | **{fundamental_total}/70** | 判斷公司能否捕獲長期產業成長 | 不等同現價可買 |"]
    )
    price_table = "\n".join(
        ["| 現價報酬風險類別 | 分數 | 支持證據 | 扣分／待驗證 |", "|---|---:|---|---|"]
        + [f"| {label} | {score}/{maximum} | {support} | {deduction} |" for label, score, maximum, support, deduction in price_rows]
        + [f"| **現價合計** | **{price_total}/30** | 判斷從目前價格出發的風險報酬 | 分數越高越有利 |"]
    )

    windows = v.get("proxy_windows") or {}
    anchor = to_float(v.get("historical_anchor_pe"))
    ttm_eps = to_float(v.get("ttm_eps"))
    trust_eps = to_float(v.get("trust_adjusted_eps"))
    forward_eps = to_float((v.get("forward") or {}).get("eps"))
    long_p75 = safe_median([
        (windows.get("2Y") or {}).get("p75"),
        (windows.get("3Y") or {}).get("p75"),
    ])
    bear_pe = anchor * .75 if finite(anchor) else math.nan
    base_pe = (
        to_float(v.get("trust_adjusted_fair")) / trust_eps
        if finite(v.get("trust_adjusted_fair")) and finite(trust_eps) and trust_eps > 0
        else math.nan
    )
    bull_pe = safe_min([anchor * 1.15 if finite(anchor) else math.nan, long_p75])
    scenarios = [
        ("Bear", "TTM EPS × 80%", ttm_eps * .80 if finite(ttm_eps) else math.nan, bear_pe,
         "Normalized Anchor × 75%", 35, "需求轉弱、margin 下滑；先檢查 thesis，不因低價自動買進"),
        ("Base", "Trust-adjusted EPS", trust_eps, base_pe,
         "Trust-adjusted Fair ÷ Trust-adjusted EPS", 45, "月營收、EPS、margin 與 FETS 證據延續"),
        ("Bull", (v.get("forward") or {}).get("type") or "Forward EPS", forward_eps, bull_pe,
         "min(Normalized Anchor × 115%, median(2Y/3Y P75))", 20, "Forward EPS 兌現，且訂單、margin、FCF 與 RES 同時驗證"),
    ]
    scenario_lines = [
        "| 情境 | EPS口徑 | EPS | P/E口徑 | 終值 P/E | 目標價 | 現價倍數 | 機率 | 必要條件／失效訊號 |",
        "|---|---|---:|---|---:|---:|---:|---:|---|",
    ]
    weighted_multiple = 0.0
    scenario_multiple: dict[str, float] = {}
    for name, eps_basis, scenario_eps, terminal_pe, pe_basis, probability, condition in scenarios:
        target = scenario_eps * terminal_pe if finite(scenario_eps) and finite(terminal_pe) else math.nan
        multiple = target / latest if finite(target) and finite(latest) and latest else math.nan
        scenario_multiple[name] = multiple
        if finite(multiple):
            weighted_multiple += multiple * probability / 100
        scenario_lines.append(
            f"| {name} | {eps_basis} | {fmt(scenario_eps, 2)} | {pe_basis} | {fmt(terminal_pe, 1)}x | "
            f"{fmt(target, 1)} | {fmt(multiple, 2)}x | {probability}% | {condition} |"
        )

    if weighted_multiple >= 1.8:
        conclusion = "模型具兩倍附近潛力，但必須補足訂單、產能與現金流證據，現階段不可直接追價"
        action = "等待下一驗證點／不追價"
    elif weighted_multiple >= 1.3:
        conclusion = "較合理為 3–4 年 1.3–1.8 倍，是否升格為倍數候選取決於 EPS、margin 與現金流驗證"
        action = "續抱但不追價／等待驗證"
    else:
        conclusion = "目前成長大致已反映或倍數證據不足，優先依估值與 thesis 管理部位"
        action = "保留核心倉、交易倉依估值停利"

    generic_rows = [] if d.get("full_research_entry") else [
        f"| {d['thesis']} | Stage 0/1 | 正向 | 間接：產業研究假說 | [公開資訊觀測站公司資料](https://mops.twse.com.tw/mops/web/index) | D | 6–36 月 | 需客戶、供應商或政策第二來源 |",
        f"| {d['risk']} | Stage 2/3 | 負向 | 反向：thesis 失效 | [公開資訊觀測站重大訊息](https://mops.twse.com.tw/mops/web/t05sr01_1) | D | 即時至 24 月 | 不得因未驗證而忽略 |",
    ]
    signals = "\n".join([
        "| 訊號 | 階段 | 方向 | 直接／間接 | 來源與日期 | 品質 | 領先期 | 驗證 |",
        "|---|---|---|---|---|---:|---:|---|",
        *leading_signal_markdown(d),
        f"| 近 3 月營收 YoY {fmt(rev3m, 1, '%')}、最新月 YoY {fmt(d.get('rev_yoy'), 1, '%')} | Stage 1/2 | {'正向' if finite(rev3m) and rev3m > 0 else '負向'} | 直接：公司營收 | [MOPS 月營收（{d.get('revenue_month') or '最新可得'}）](https://mops.twse.com.tw/mops/web/t05st10_ifrs) | A | 0–12 月 | 已反映營收，未等同訂單 |",
        f"| 毛利率 {fmt(gross, 1, '%')}、營益率 {fmt(op_margin, 1, '%')}、EPS {fmt(d.get('eps_q'), 2)} | Stage 2 | 中性 | 直接：財務 | [MOPS 財務報告（{d.get('financial_q') or '最新可得'}）](https://mops.twse.com.tw/mops/web/t163sb04) | A | 0–12 月 | 已反映損益；OCF/NI 待補 |",
        f"| 收盤 {fmt(latest)}、P/E {fmt(pe)}、60D {fmt(ret60, 1, '%')} | Stage 3 | {'負向' if price_total < 16 else '中性'} | 直接：市場定價 | [TWSE／TPEx 行情與估值（{d.get('latest_date') or d.get('price_date_fmt')}）](https://www.twse.com.tw/zh/) | A-/B | 即時 | 價格已驗證 |",
        *generic_rows,
    ])
    reverse = "\n".join(f"- {item}" for item in d["bear"][:5])
    return f"""#### 14.1 停利後倍數成長再評估（Post-Target Multibagger Reassessment）

**固定執行，不設啟動條件。** 一句話結論：**{conclusion}**。本節從目前價格重新檢查倍數潛力與 de-rating 風險，不因尚未達停利價而省略。

##### 14.1.1 Stage 0–3 訊號、來源與品質

{signals}

完整研究版必須逐檔線上查 Stage 0–1 的客戶 CapEx、產品 roadmap、政策／終端需求、認證、訂單、產能、交期、報價與競爭者訊號，再用 Stage 2 月營收／財務與 Stage 3 市場定價驗證。若本節只出現 MOPS/TWSE 通用入口，代表尚未完成完整線上深研，不能把它當成已驗證 rerating evidence。

##### 14.1.2 多頭與至少三項反向證據

- 多頭：{d['thesis']}
- 下一催化：{d['trigger']}
- 至少三項反向證據：
{reverse}

##### 14.1.3 倍數成長雙分數

{fundamental_table}

{price_table}

{score_band_text(fundamental_total, price_total)}

總分 {fundamental_total + price_total}/100 只作研究排序，不得用總分掩蓋估值過熱、資料缺口或低品質證據。

##### 14.1.4 Bear / Base / Bull 倍數模型

目前價格：{fmt(latest)}。本節不再引用舊 EPS_used／P10／P25／P90 價格模型，而與 7.2D 共用 TTM、Trust-adjusted、Forward 三層。Bear/Base/Bull 機率合計 100%，Extreme Bull 不納入主結論。

{chr(10).join(scenario_lines)}

- Bear：EPS = TTM {fmt(ttm_eps,2)} × 80% = {fmt(ttm_eps*.8 if finite(ttm_eps) else math.nan,2)}；P/E = Normalized Anchor {fmt(anchor)} × 75% = {fmt(bear_pe)}x。
- Base：EPS = TTM {fmt(ttm_eps,2)} + Trust {fmt((v.get('fets') or {}).get('trust_pct',0)*100,0,'%')} × (Forward {fmt(forward_eps,2)} − TTM {fmt(ttm_eps,2)}) = {fmt(trust_eps,2)}；目標價固定等於 Trust-adjusted Fair {fmt(v.get('trust_adjusted_fair'))}。
- Bull：EPS = Forward candidate {fmt(forward_eps,2)}；P/E = min(Anchor × 115% = {fmt(anchor*1.15 if finite(anchor) else math.nan)}x, 2Y/3Y P75 中位數 {fmt(long_p75)}x) = {fmt(bull_pe)}x。
- 機率加權倍數：**{fmt(weighted_multiple, 2)}x**。
- Bear/Base/Bull：約 **{fmt(scenario_multiple.get('Bear'), 2)}x / {fmt(scenario_multiple.get('Base'), 2)}x / {fmt(scenario_multiple.get('Bull'), 2)}x**。
- 若主要報酬來自終值 P/E 擴張，而不是營收、margin、EPS 或現金流，上述倍數可信度必須下修。

##### 14.1.5 最終判斷與重評

| 項目 | 結論 |
|---|---|
| 最可能倍數／時間 | {conclusion}；模型期間約 3–4 年 |
| 資料完整度／信心 | 低至中；月營收、margin、EPS 與估值已取得，OCF/NI、訂單、產能、存貨及應收仍待補 |
| 下一必要驗證點 | {d['trigger']} |
| 固定重評 | 每月營收公布後更新；每季財報後完整重評 |
| 立即重評條件 | EPS/margin、月營收、訂單/產能、競爭、重大訊息改變，或股價／EPS 較本次變動超過 20% |
| 最終操作標籤 | **{action}** |

> 目前只能證明產業方向與部分財務趨勢值得追蹤，若缺少訂單、供給與現金流三角驗證，尚不足以證明該公司能從現價再次實現倍數成長。
"""


HIGHLIGHT_TERMS: list[tuple[str, str]] = [
    ("高於 Bull 過熱", "hl-risk"),
    ("接近 Bull 過熱", "hl-risk"),
    ("Base 過熱、往 Bull 定價", "hl-risk"),
    ("停損/退出", "hl-risk"),
    ("過熱減碼區", "hl-risk"),
    ("過熱減碼", "hl-risk"),
    ("高風險", "hl-risk"),
    ("中高風險", "hl-risk"),
    ("不追", "hl-risk"),
    ("減碼", "hl-risk"),
    ("退出", "hl-risk"),
    ("停損", "hl-risk"),
    ("過熱", "hl-risk"),
    ("可小量 starter", "hl-action"),
    ("可小量試單", "hl-action"),
    ("技術試單區", "hl-action"),
    ("估值進場區", "hl-action"),
    ("分批停利", "hl-action"),
    ("可小量", "hl-action"),
    ("續抱", "hl-action"),
    ("停利", "hl-action"),
    ("試單", "hl-action"),
    ("進場區", "hl-action"),
    ("starter", "hl-action"),
    ("未取得/待補", "hl-missing"),
    ("資料信心下降", "hl-missing"),
    ("不能計算", "hl-missing"),
    ("不可判定", "hl-missing"),
    ("未取得", "hl-missing"),
    ("待補", "hl-missing"),
    ("缺口", "hl-missing"),
    ("Risk-on", "hl-ok"),
    ("低風險", "hl-ok"),
    ("低估", "hl-ok"),
    ("合理區", "hl-ok"),
    ("thesis intact", "hl-ok"),
]
HIGHLIGHT_CLASS = {term: class_name for term, class_name in HIGHLIGHT_TERMS}
HIGHLIGHT_RE = re.compile("|".join(re.escape(term) for term, _ in sorted(HIGHLIGHT_TERMS, key=lambda x: len(x[0]), reverse=True)))
IMPORTANT_NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_])("
    r"\d{4}-\d{2}-\d{2}"
    r"|(?:&gt;=|&lt;=|>=|<=)\s*[+-]?\d{1,4}(?:,\d{3})*(?:\.\d+)?(?:%|x|倍)?"
    r"|[+-]?\d{1,4}(?:,\d{3})*(?:\.\d+)?\s*-\s*[+-]?\d{1,4}(?:,\d{3})*(?:\.\d+)?(?:%|x|倍)?"
    r"|[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:%|x|倍)?"
    r"|[+-]?\d+\.\d+(?:%|x|倍)?"
    r"|[+-]?\d+(?:%|x|倍)"
    r"|[+-]\d+"
    r"|[1-9]\d{2,}(?:\.\d+)?"
    r")(?![A-Za-z0-9_])"
)


def numeric_class(token: str) -> str:
    compact = token.replace(" ", "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", compact):
        return "num-date"
    if "%" in compact:
        if compact.startswith("+"):
            return "num-up"
        if compact.startswith("-"):
            return "num-down"
        return "num-percent"
    if compact.startswith("+"):
        return "num-up"
    if compact.startswith("-"):
        return "num-down"
    if compact.endswith("x") or compact.endswith("倍"):
        return "num-multiple"
    if compact.startswith("&gt;=") or compact.startswith("&lt;=") or compact.startswith(">=") or compact.startswith("<="):
        return "num-price"
    if "-" in compact:
        return "num-price"
    return "num-key"


def emphasize_numbers(escaped: str) -> str:
    def repl(match: re.Match[str]) -> str:
        token = match.group(1)
        return f"<span class=\"num {numeric_class(token)}\">{token}</span>"

    return IMPORTANT_NUMBER_RE.sub(repl, escaped)


def emphasize_segment(segment: str, mark_numbers: bool = True) -> str:
    escaped = html.escape(segment)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    if mark_numbers:
        escaped = emphasize_numbers(escaped)

    def repl(match: re.Match[str]) -> str:
        term = match.group(0)
        class_name = HIGHLIGHT_CLASS.get(term, "hl-action")
        return f"<span class=\"hl {class_name}\">{term}</span>"

    return HIGHLIGHT_RE.sub(repl, escaped)


def md_inline(text: str, mark_numbers: bool = True) -> str:
    parts = re.split(r"(\[[^\]]+\]\(https?://[^)]+\)|`[^`]+`)", text)
    rendered: list[str] = []
    for part in parts:
        if not part:
            continue
        if part.startswith("`") and part.endswith("`"):
            rendered.append(f"<code>{html.escape(part[1:-1])}</code>")
        elif part.startswith("["):
            match = re.fullmatch(r"\[([^\]]+)\]\((https?://[^)]+)\)", part)
            if match:
                label, url = match.groups()
                rendered.append(
                    f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">'
                    f"{emphasize_segment(label, mark_numbers=mark_numbers)}</a>"
                )
        else:
            rendered.append(emphasize_segment(part, mark_numbers=mark_numbers))
    return "".join(rendered)


def table_to_html(lines: list[str]) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [row for row in rows if row and not all(set(cell) <= {"-", ":"} for cell in row)]
    if not rows:
        return ""
    headers = rows[0]
    table_classes = ["data-table"]
    if len(headers) >= 7:
        table_classes.append("wide-table")
    elif len(headers) >= 5:
        table_classes.append("medium-table")
    head = "".join(f"<th>{md_inline(cell)}</th>" for cell in headers)
    body_rows = []
    for row in rows[1:]:
        cells = []
        for idx, cell in enumerate(row):
            header = headers[idx] if idx < len(headers) else ""
            mark_numbers = header not in {"Rank", "代號"}
            cells.append(f"<td>{md_inline(cell, mark_numbers=mark_numbers)}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        f"<div class=\"table-wrap\"><table class=\"{' '.join(table_classes)}\">"
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>"
    )


def markdown_to_html(md: str, code: str) -> str:
    section_id_by_number = {
        "1": "conclusion",
        "2": "regime",
        "3": "industry",
        "4": "bear",
        "5": "price",
        "6": "numbers",
        "7": "eps",
        "8": "valuation",
        "9": "targets",
        "10": "action",
        "11": "risk",
        "12": "quality",
        "13": "lowpe",
        "14": "rerating",
        "15": "momentum",
        "16": "position",
        "17": "matrix",
        "18": "next",
        "19": "data",
    }
    out: list[str] = []
    lines = md.splitlines()
    i = 0
    section_open = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(table_to_html(block))
            continue
        if stripped.startswith("## "):
            out.append(
                f"<h2 id=\"{html.escape(code)}-overview\">{md_inline(stripped[3:], mark_numbers=False)}</h2>"
            )
            i += 1
            continue
        if stripped.startswith("### "):
            if section_open:
                out.append("</section>")
            title = stripped[4:]
            section_id = "company"
            m = re.match(r"(\d+)(?:\.(\d+))?(?:\.|\s)\s*", title)
            if m:
                section_id = section_id_by_number.get(m.group(1), m.group(1))
                if m.group(2):
                    section_id = f"{section_id}-{m.group(2)}"
            out.append(
                f"<section id=\"{html.escape(code)}-{html.escape(section_id)}\" "
                f"class=\"report-section\" data-section=\"{html.escape(section_id)}\">"
                f"<h3>{md_inline(title, mark_numbers=False)}</h3>"
            )
            section_open = True
            i += 1
            continue
        if stripped.startswith("##### "):
            out.append(f"<h5>{md_inline(stripped[6:], mark_numbers=False)}</h5>")
            i += 1
            continue
        if stripped.startswith("#### "):
            subtitle = stripped[5:]
            subsection_match = re.match(r"(\d+\.\d+)", subtitle)
            subsection_attr = (
                f' data-subsection="{html.escape(subsection_match.group(1))}"'
                if subsection_match else ""
            )
            out.append(
                f"<h4{subsection_attr}>{md_inline(subtitle, mark_numbers=False)}</h4>"
            )
            i += 1
            continue
        if stripped.startswith("> "):
            out.append(f"<blockquote>{md_inline(stripped[2:])}</blockquote>")
            i += 1
            continue
        if stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            out.append("<ul>" + "".join(f"<li>{md_inline(item)}</li>" for item in items) + "</ul>")
            continue
        if re.match(r"\d+\. ", stripped):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                items.append(re.sub(r"^\d+\. ", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{md_inline(item)}</li>" for item in items) + "</ol>")
            continue
        out.append(f"<p>{md_inline(stripped)}</p>")
        i += 1
    if section_open:
        out.append("</section>")
    return "\n".join(out)


def stock_status_badge(d: dict[str, Any]) -> tuple[str, str]:
    action = action_label(d)
    if "資料不足" in action or "缺最新價" in action:
        return "資料不足", "status-missing"
    if "過熱" in action or "不追" in action or "減碼" in action:
        return "不追/減碼", "status-risk"
    if "合理" in action or "續抱" in action:
        return "合理/續抱", "status-ok"
    if "試單" in action or "starter" in action or "進場" in action:
        return "試單", "status-action"
    return "研究", "status-watch"


def render_html(rows: list[dict[str, Any]], quick_rows: list[str], title: str = REPORT_TITLE) -> str:
    stock_buttons = []
    articles = []
    for d in rows:
        code = html.escape(d["code"])
        name = html.escape(d["name"])
        status_label, status_class = stock_status_badge(d)
        selected = "true" if d["rank"] == 1 else "false"
        stock_buttons.append(
            f'<button class="tab-button {status_class}" id="tab-{code}" role="tab" '
            f'aria-controls="panel-{code}" aria-selected="{selected}" data-code="{code}" data-name="{name}">'
            f'{code} <span>{name}</span><em>{html.escape(status_label)}</em></button>'
        )
        article_class = "panel" if d["rank"] == 1 else "panel hidden"
        articles.append(
            f'<article id="panel-{code}" class="{article_class}" role="tabpanel" '
            f'aria-labelledby="tab-{code}" data-code="{code}">'
            f"{markdown_to_html(stock_section(d), d['code'])}</article>"
        )

    section_buttons = [
        ("regime", "1. 市場與持股閘門"),
        ("industry", "2. 產業與國際情勢"),
        ("bear", "4. Bear Case"),
        ("price", "5. 價格與部位"),
        ("numbers", "6. 來源數字"),
        ("eps", "7. EPS 模組"),
        ("valuation", "8. 估值模組"),
        ("targets", "9. 價格結論"),
        ("action", "10. 操作建議"),
        ("risk", "11. 停損停利"),
        ("quality", "12. 品質風險"),
        ("lowpe", "13. 低 P/E 成長"),
        ("rerating", "14. Rerating / 倍數再評估"),
        ("matrix", "17. Price × Thesis"),
        ("next", "18. 下一驗證點"),
        ("data", "19. 資料完整性"),
    ]
    section_nav = "".join(
        f'<a href="#" data-section="{html.escape(sec)}">{html.escape(label)}</a>'
        for sec, label in section_buttons
    )
    quick_html = table_to_html(quick_rows)
    quick_legend_html = """
      <div class="quick-legend" aria-label="快速結論欄位圖例">
        <div><strong>① 價值研究區</strong><span>Stress～Value Entry = Conservative Fair × 75%～85%；低於 Stress 先查 thesis。</span></div>
        <div><strong>② 技術執行參考</strong><span>min(50DMA, 現價 × 92%)；只決定執行節奏，不改變 Price Zone。</span></div>
        <div><strong>③ Forward Growth Anchor</strong><span>Forward EPS × 2Y/3Y P50 正常化錨；超過後用 RES 判斷是否過熱。</span></div>
      </div>
      <p class="quick-action-note"><strong>Price Zone／現價動作：</strong>Below Stress＝先查 thesis → Stress～Entry＝可分批研究 → Entry～Conservative Fair＝只宜小量 → Conservative～Trust-adjusted＝部分成長定價，新增需 FETS → Trust-adjusted～Forward Anchor＝續抱、不追價 → 高於 Forward Anchor＝需 RES。</p>
      <p class="quick-action-note"><strong>Bear/Base/Bull 情境：</strong>把現價和 14.1.4 的三個情境目標價比較；它回答「現價落在哪個財務情境」，不是估值區間，因此不等同 Price Zone。</p>
    """.strip()
    for d in rows:
        code = html.escape(d["code"])
        quick_html = quick_html.replace(
            f"<td>{code}</td>",
            f'<td><button class="summary-stock-jump" data-code="{code}">{code}</button></td>',
        )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}（{len(rows)} 檔） {RUN_DATE}</title>
<style>
:root {{
  color-scheme: light;
  --bg: #f6f7f9;
  --panel: #ffffff;
  --text: #1f2933;
  --muted: #667085;
  --line: #d9dee7;
  --accent: #126c5b;
  --accent-soft: #e3f3ef;
  --risk: #9f3412;
  --top-offset: 176px;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}}
.app {{
  min-height: 100vh;
}}
.hero {{
  padding: 24px 32px 18px;
  border-bottom: 1px solid var(--line);
  background: linear-gradient(135deg, #0f3d37, #126c5b);
  color: #fff;
}}
.hero h1 {{ margin: 0 0 8px; font-size: 28px; }}
.hero p {{ margin: 4px 0; color: #d8f3ec; }}
.tabs {{
  position: sticky;
  top: 0;
  z-index: 6;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 10px 24px;
  border-bottom: 1px solid var(--line);
  background: rgba(255,255,255,.96);
  backdrop-filter: blur(8px);
}}
.tab-button {{
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 999px;
  padding: 7px 11px;
  cursor: pointer;
  font-weight: 800;
  color: #1f2933;
}}
.tab-button span {{ margin-left: 4px; color: var(--muted); font-weight: 650; }}
.tab-button em {{
  display: none;
  margin-left: 6px;
  padding: 1px 6px;
  border-radius: 999px;
  font-style: normal;
  font-size: 11px;
}}
.tab-button[aria-selected="true"] {{
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-soft);
  box-shadow: inset 0 0 0 1px var(--accent);
}}
.report-shell {{
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}}
.section-nav {{
  position: sticky;
  top: 62px;
  max-height: calc(100vh - 78px);
  overflow: auto;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
}}
.section-nav strong {{
  display: block;
  margin-bottom: 8px;
  color: #163b35;
}}
.section-nav a {{
  display: block;
  padding: 7px 8px;
  margin: 2px 0;
  border-radius: 8px;
  color: #334155;
  text-decoration: none;
  font-size: 13px;
}}
.section-nav a:hover,
.section-nav a.active {{
  color: var(--accent);
  background: var(--accent-soft);
  font-weight: 800;
}}
.nav-divider {{
  height: 1px;
  margin: 8px 0;
  background: var(--line);
}}
.panel {{
  max-width: 1120px;
  margin: 0 auto 28px;
  padding: 24px 28px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
  box-shadow: 0 8px 30px rgba(15, 23, 42, .04);
}}
.hidden {{ display: none !important; }}
.topbar {{
  position: sticky;
  top: 0;
  z-index: 5;
  padding: 10px 14px 8px;
  border-bottom: 1px solid var(--line);
  background: var(--panel);
}}
.topbar-head {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}}
.topbar-title {{
  min-width: 0;
}}
.stock-filter {{
  width: min(240px, 32vw);
  height: 34px;
  border: 1px solid var(--line);
  border-radius: 7px;
  padding: 6px 9px;
  color: var(--text);
  background: #fff;
  font: inherit;
  font-size: 14px;
}}
.stock-filter:focus {{
  outline: 2px solid #b6d8d0;
  border-color: var(--accent);
}}
.page-content {{
  min-width: 0;
  padding: 18px 24px 56px;
}}
.analysis-layout {{
  display: grid;
  grid-template-columns: 184px minmax(0, 1fr);
  gap: 18px;
  min-width: 0;
  margin-top: 18px;
}}
.side-nav {{
  position: sticky;
  top: var(--top-offset);
  align-self: start;
  max-height: calc(100vh - var(--top-offset) - 18px);
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  overflow: auto;
}}
.analysis-content {{
  min-width: 0;
}}
h1 {{ font-size: 24px; margin: 0 0 8px; }}
h2 {{ font-size: 24px; margin: 8px 0 16px; }}
h3 {{ font-size: 18px; margin: 24px 0 8px; padding-top: 8px; border-top: 1px solid var(--line); }}
h4 {{ font-size: 17px; margin: 26px 0 10px; color: #163b35; }}
h5 {{ font-size: 15px; margin: 20px 0 8px; color: #334155; }}
blockquote {{ margin: 14px 0; padding: 10px 14px; border-left: 4px solid var(--risk); background: #fff7ed; }}
p, li {{ font-size: 15px; }}
code {{ background: #eef1f5; padding: 1px 5px; border-radius: 4px; }}
.muted {{ color: var(--muted); font-size: 14px; }}
.hl {{
  display: inline-block;
  padding: 0 5px;
  border-radius: 5px;
  font-weight: 800;
  line-height: 1.45;
}}
.hl-risk {{ color: #8a1f11; background: #fde8df; }}
.hl-action {{ color: #075985; background: #e0f2fe; }}
.hl-missing {{ color: #7c2d12; background: #ffedd5; }}
.hl-ok {{ color: #166534; background: #dcfce7; }}
.num {{
  display: inline-block;
  padding: 0 4px;
  border-radius: 4px;
  font-weight: 750;
  font-variant-numeric: tabular-nums;
  line-height: 1.45;
  background: #eef2ff;
  color: #3730a3;
}}
.num-up {{ color: #166534; background: #dcfce7; }}
.num-down {{ color: #991b1b; background: #fee2e2; }}
.num-percent {{ color: #075985; background: #e0f2fe; }}
.num-price {{ color: #6d28d9; background: #ede9fe; }}
.num-multiple {{ color: #854d0e; background: #fef3c7; }}
.num-date {{ color: #374151; background: #eef2f7; }}
.stock-list {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(112px, 1fr));
  gap: 6px;
  margin-top: 8px;
  max-height: 94px;
  overflow: auto;
  padding-right: 2px;
}}
.stock-tab {{
  min-width: 0;
  text-align: left;
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 7px;
  padding: 7px 8px;
  cursor: pointer;
}}
.stock-tab[hidden] {{ display: none; }}
.stock-tab .tab-code {{ display: block; color: var(--muted); font-size: 11px; line-height: 1.2; }}
.stock-tab strong {{
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  line-height: 1.25;
}}
.stock-tab em {{
  display: inline-block;
  margin-top: 3px;
  padding: 1px 5px;
  border-radius: 999px;
  font-style: normal;
  font-size: 11px;
  font-weight: 800;
  line-height: 1.45;
}}
.status-risk em {{ color: #8a1f11; background: #fde8df; }}
.status-action em {{ color: #075985; background: #e0f2fe; }}
.status-missing em {{ color: #7c2d12; background: #ffedd5; }}
.status-ok em {{ color: #166534; background: #dcfce7; }}
.status-watch em {{ color: #374151; background: #eef2f7; }}
.stock-tab.active {{
  border-color: var(--accent);
  background: var(--accent-soft);
  box-shadow: inset 0 0 0 1px var(--accent);
}}
.toolbar {{
  display: grid;
  gap: 7px;
}}
.section-jump {{
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 7px;
  padding: 8px 9px;
  cursor: pointer;
  font-size: 13px;
  text-align: left;
}}
.section-jump:hover {{ border-color: var(--accent); color: var(--accent); }}
.section-jump.active {{ border-color: var(--accent); background: var(--accent-soft); color: var(--accent); font-weight: 800; }}
.summary-stock-jump {{
  border: 1px solid #b9c7d8;
  border-radius: 7px;
  padding: 5px 9px;
  background: #fff;
  color: #174f8a;
  font-weight: 800;
  cursor: pointer;
}}
.summary-stock-jump:hover {{ border-color: var(--accent); background: var(--accent-soft); }}
.summary {{
  margin: 0 0 18px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--panel);
}}
.quick-legend {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin: 8px 0;
}}
.quick-legend > div {{
  padding: 9px 11px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #f8fafc;
}}
.quick-legend strong {{ display: block; color: #174f8a; }}
.quick-legend span {{ display: block; margin-top: 2px; color: var(--muted); font-size: 12px; }}
.quick-action-note {{ margin: 8px 0 10px; font-size: 13px; color: #475467; }}
@media (max-width: 760px) {{
  .quick-legend {{ grid-template-columns: 1fr; }}
}}
.summary-scroll {{ max-width: 100%; overflow: hidden; }}
.stock-report {{
  display: none;
  max-width: 1120px;
  margin: 18px auto 0;
  padding: 22px 26px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
}}
.stock-report.active {{ display: block; }}
.table-wrap {{
  max-width: 100%;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  overscroll-behavior-x: contain;
}}
table {{ width: 100%; border-collapse: collapse; min-width: 760px; }}
th, td {{
  padding: 9px 10px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
  font-size: 14px;
  line-height: 1.5;
}}
th {{ background: #f0f3f7; font-weight: 700; }}
tr:last-child td {{ border-bottom: 0; }}
.medium-table {{ min-width: 1120px; table-layout: fixed; }}
.wide-table {{ min-width: 1680px; table-layout: fixed; }}
.medium-table th, .medium-table td,
.wide-table th, .wide-table td {{
  overflow-wrap: break-word;
  word-break: normal;
}}
.summary-table,
.summary table {{
  width: 4050px;
  min-width: 4050px;
  table-layout: fixed;
}}
.summary th,
.summary td {{
  white-space: nowrap;
  word-break: keep-all;
  overflow-wrap: normal;
}}
.summary th:nth-child(1), .summary td:nth-child(1) {{ width: 58px; }}
.summary th:nth-child(2), .summary td:nth-child(2) {{ width: 82px; }}
.summary th:nth-child(3), .summary td:nth-child(3) {{ width: 120px; }}
.summary th:nth-child(4), .summary td:nth-child(4) {{ width: 150px; }}
.summary th:nth-child(5), .summary td:nth-child(5) {{ width: 105px; }}
.summary th:nth-child(6), .summary td:nth-child(6) {{ width: 245px; }}
.summary th:nth-child(7), .summary td:nth-child(7) {{ width: 310px; }}
.summary th:nth-child(8), .summary td:nth-child(8) {{ width: 170px; }}
.summary th:nth-child(9), .summary td:nth-child(9) {{ width: 155px; }}
.summary th:nth-child(10), .summary td:nth-child(10) {{ width: 180px; }}
.summary th:nth-child(11), .summary td:nth-child(11) {{ width: 200px; }}
.summary th:nth-child(6), .summary td:nth-child(6),
.summary th:nth-child(7), .summary td:nth-child(7),
.summary th:nth-child(11), .summary td:nth-child(11) {{
  white-space: normal;
  word-break: keep-all;
  overflow-wrap: break-word;
}}
.summary th:nth-child(12), .summary td:nth-child(12) {{ width: 245px; }}
.summary th:nth-child(13), .summary td:nth-child(13) {{ width: 155px; }}
.summary th:nth-child(14), .summary td:nth-child(14) {{ width: 105px; }}
.summary th:nth-child(15), .summary td:nth-child(15) {{ width: 92px; }}
.summary th:nth-child(16), .summary td:nth-child(16) {{ width: 190px; }}
.summary th:nth-child(17), .summary td:nth-child(17) {{ width: 120px; }}
.summary th:nth-child(18), .summary td:nth-child(18) {{ width: 100px; }}
.summary th:nth-child(19), .summary td:nth-child(19) {{ width: 105px; }}
.summary th:nth-child(20), .summary td:nth-child(20) {{ width: 110px; }}
.summary th:nth-child(21), .summary td:nth-child(21) {{ width: 230px; }}
.summary th:nth-child(22), .summary td:nth-child(22) {{ width: 130px; }}
.summary th:nth-child(23), .summary td:nth-child(23),
.summary th:nth-child(24), .summary td:nth-child(24) {{ width: 145px; }}
.summary th:nth-child(25), .summary td:nth-child(25) {{ width: 105px; }}
.summary th:nth-child(26), .summary td:nth-child(26) {{ width: 190px; }}
@media (max-width: 860px) {{
  .hero {{ padding: 18px 16px; }}
  .tabs {{ position: static; padding: 10px 12px; }}
  .report-shell {{ grid-template-columns: 1fr; }}
  .section-nav {{ position: static; max-height: none; }}
  .panel {{ padding: 16px; }}
  .topbar {{ position: static; }}
  .topbar-head {{ display: block; }}
  .stock-filter {{ width: 100%; margin-top: 8px; }}
  .stock-list {{ grid-template-columns: repeat(2, minmax(0, 1fr)); max-height: 164px; }}
  .page-content {{ padding: 12px; }}
  .analysis-layout {{ grid-template-columns: 1fr; }}
  .side-nav {{ position: static; max-height: none; }}
  .toolbar {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .stock-report {{ padding: 16px; }}
}}
</style>
</head>
<body>
<div class="app">
<header class="hero">
  <h1>{html.escape(title)}（{len(rows)} 檔）</h1>
  <p>流程依據：tw-stock-analysis-framework.md | 產出日：{RUN_DATE} 台北時間 | 用途：投資研究與風險提示，不構成個人化財務建議。</p>
  <p>閱讀方式比照美股版：上方切換個股，左側跳章節；URL 可直接連到 #代號-章節。</p>
</header>
<nav class="tabs" id="tabs" aria-label="股票頁籤">{''.join(stock_buttons)}</nav>
<main class="page-content">
    <section class="summary">
      <h2>快速結論總表</h2>
      {quick_legend_html}
      <div class="summary-scroll">{quick_html}</div>
    </section>
    <div class="report-shell" id="analysis-area">
      <aside class="section-nav" id="section-nav" aria-label="本檔章節導覽">
        <strong id="section-nav-title">個股章節</strong>
        <a href="#" data-section="overview">完整分析頂端</a>
        <a href="#" data-section="company">公司白話介紹</a>
        <a href="#" data-section="conclusion">一句話結論</a>
        <div class="nav-divider"></div>
        {section_nav}
      </aside>
      <div id="content" class="analysis-content">
        {''.join(articles)}
      </div>
    </div>
</main>
</div>
<script>
const tabButtons = Array.from(document.querySelectorAll('.tab-button[data-code]'));
const panels = Array.from(document.querySelectorAll('[role="tabpanel"]'));
const sectionLinks = Array.from(document.querySelectorAll('#section-nav [data-section]'));
let activeCode = {json.dumps(rows[0]["code"] if rows else "")};
function updateSectionLinks(code) {{
  activeCode = code;
  const tab = tabButtons.find(item => item.dataset.code === code);
  const name = tab?.dataset.name || '';
  document.getElementById('section-nav-title').textContent = code + (name ? ' ' + name : '') + ' 個股章節';
  sectionLinks.forEach(link => {{
    link.href = '#' + code + '-' + link.dataset.section;
  }});
}}
function selectStock(code, scrollToPanel = false, hashTarget = null) {{
  tabButtons.forEach(button => button.setAttribute('aria-selected', button.dataset.code === code ? 'true' : 'false'));
  panels.forEach(panel => panel.classList.toggle('hidden', panel.dataset.code !== code));
  updateSectionLinks(code);
  if (hashTarget || code) history.replaceState(null, '', '#' + (hashTarget || code));
  if (scrollToPanel) document.getElementById(code + '-overview')?.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
}}
tabButtons.forEach(button => button.addEventListener('click', () => selectStock(button.dataset.code, true)));
document.querySelectorAll('.summary-stock-jump').forEach(button => {{
  button.addEventListener('click', () => {{
    selectStock(button.dataset.code, true);
  }});
}});
sectionLinks.forEach(link => link.addEventListener('click', event => {{
  event.preventDefault();
  const target = document.getElementById(activeCode + '-' + link.dataset.section);
  if (target) {{
    sectionLinks.forEach(item => item.classList.toggle('active', item.dataset.section === link.dataset.section));
    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    history.replaceState(null, '', link.href);
  }}
}}));
document.addEventListener('keydown', event => {{
  if (event.target.matches('input, textarea')) return;
  if (event.key === '[') {{
    const current = tabButtons.findIndex(button => button.dataset.code === activeCode);
    const next = (current - 1 + tabButtons.length) % tabButtons.length;
    selectStock(tabButtons[next].dataset.code, true);
  }}
  if (event.key === ']') {{
    const current = tabButtons.findIndex(button => button.dataset.code === activeCode);
    const next = (current + 1) % tabButtons.length;
    selectStock(tabButtons[next].dataset.code, true);
  }}
}});
const rawHash = location.hash?.slice(1);
const codes = {json.dumps([d["code"] for d in rows])};
const hashCode = codes.find(code => rawHash === code || rawHash?.startsWith(code + '-')) || activeCode;
selectStock(hashCode, false, rawHash && document.getElementById(rawHash) ? rawHash : null);
if (rawHash && document.getElementById(rawHash)) requestAnimationFrame(() => document.getElementById(rawHash).scrollIntoView());
</script>
</body>
</html>"""


def main() -> None:
    rows = load_rows()
    quick_rows = [
        f"| Rank | 代號 | 公司 | 產業 | 最新價 | Price Zone | 現價動作 | ①價值研究區 | ②技術執行參考 | ③Forward Growth Anchor | Bear/Base/Bull 情境 | 近日漲跌 5D/20D/60D | 大盤日漲跌 | 大盤Regime | PE_used | EPS_type | 3M營收YoY | 52W位置 | TTM EPS | {CURRENT_YEAR}E / FY1 consensus EPS | {NEXT_YEAR}E / FY2 consensus EPS | Trailing P/E | Forward EPS/type | FETS/Trust | Conservative Fair | Trust-adjusted Fair | Market q | RES |",
        "|---:|---|---|---|---:|---|---|---:|---:|---:|---|---|---|---|---:|---|---:|---:|---:|---|---|---:|---|---|---:|---:|---:|---|",
    ]
    for d in rows:
        v = d["valuation_v2"]
        f, fets, res = v["forward"], v["fets"], v["res"]
        current = to_float(d.get("latest_close"))
        technical_test = safe_min([to_float(d.get("ma50")), current * .92])
        entry_range = f"{fmt(v.get('stress_price'))}-{fmt(v.get('conservative_entry'))}"
        overheat = v.get("forward_growth_anchor")
        quick_rows.append(
            f"| {d['rank']} | {d['code']} | {d['name']} | {d['industry']} | {fmt(d['latest_close'])} | "
            f"{v.get('price_zone')} | {v.get('action')} | {entry_range} | <= {fmt(technical_test)} | >= {fmt(overheat)} | "
            f"{bear_base_bull_position(d)} | {recent_move_text(d)} | "
            f"{MARKET_INDEX_DATE} {fmt_pct(MARKET_DAILY_CHANGE_PCT)} | {MARKET_REGIME} | "
            f"{fmt(v.get('trailing_pe'))} | REPORTED_TTM_BASELINE | {fmt(d.get('rev3m_yoy'), 1, '%')} | {fmt(d.get('pos52'), 1, '%')} | "
            f"{fmt(v['ttm_eps'], 2)} | "
            f"{fmt(d.get('current_year_eps'), 2)} / {d.get('current_year_eps_type')} / n={fmt(d.get('current_year_eps_source_count'), 0)} | "
            f"{fmt(d.get('next_year_eps'), 2)} / {d.get('next_year_eps_type')} / n={fmt(d.get('next_year_eps_source_count'), 0)} | "
            f"{fmt(v.get('trailing_pe'))}x | {fmt(f.get('eps'), 2)} / {f.get('type')} | "
            f"{fmt(fets.get('score'), 0)} / {fmt(fets.get('trust_pct', 0)*100, 0, '%')} | "
            f"{fmt(v.get('conservative_fair'))} | {fmt(v.get('trust_adjusted_fair'))} | "
            f"{fmt(v.get('market_implied_q')*100 if finite(v.get('market_implied_q')) else math.nan, 1, '%')} | "
            f"{fmt(res.get('score'), 0)} {res.get('status')} |"
        )

    stock_count = len(rows)
    body = f"""# tw_stock_candidates_{OUTPUT_SUFFIX} - tw-stock-analysis-framework.md 候選個股分析（{stock_count} 檔）

產出日期：{RUN_DATE}  
流程依據：`tw-stock-analysis-framework.md`。  
篩選來源：`output/tw_stock_candidates_{OUTPUT_SUFFIX}.csv` 的前 {stock_count} 檔候選；實際檔數由 `CANDIDATE_COUNT` 決定，排序本身只作研究順序。  
結論層級：投資研究與風險控管，不構成個人化財務建議或買賣指令。

## 專案流程記憶

- 台股個股分析：使用 `tw-stock-analysis-framework.md`。
- 選股 screen：使用 `stock-screening-candidate-framework.md`。
- 本報告不使用其他報告化流程。

## 前置閘門總結

- 市場 regime：{MARKET_REGIME}；本地篩選報告已更新至 {MARKET_INDEX_DATE} 加權指數 {fmt_pct(MARKET_DAILY_CHANGE_PCT)}，未觸發單日風險閘門。
- 投資組合：本輪是台股分析，只檢查台股持股、台幣可用現金與同產業曝險；目前未取得台股持股與可用現金，所以不能計算股數。
- 共同已補估值：同產業 current peer P/E、3M／6M／1Y／2Y／3Y point-in-time P/E、2Y／3Y P50 正常化錨、1Y rerating check、三層估值與整合價格階梯。
- 共同資料缺口：精確到公司的歷史申報時間戳、部分 OCF/NI／應收／存貨、法人／投信／自營、借券、FCF yield、EV/EBITDA及完整事件日曆；沒有實際申報時間戳時以保守法定期限避免前視偏誤。
- 共同結論：不是「全部只觀察」；現價多數在合理上緣或過熱區，所以不追，但每檔已給條件式進場/試單/減碼價格帶。

## 快速結論表

### 快速判讀圖例

| 標記 | 欄位真正用途 | 計算／判讀方式 |
|---|---|---|
| ① | **價值研究區**，不是到價自動買進 | `Stress～Entry = Conservative Fair × 75%～85%`；低於 Stress 先做 thesis review |
| ② | **技術執行參考**，不改變合理價 | `min(50DMA, 現價 × 92%)`；只決定執行節奏，不改變 Price Zone |
| ③ | **Forward Growth Anchor**，不是到價必賣 | `Forward EPS × 2Y/3Y P50正常化錨`；超過後用 RES 判斷是否過熱 |

Price Zone與現價動作完全對應：`Below Stress＝先查thesis`；`Stress～Entry＝可分批研究`；`Entry～Conservative Fair＝只宜小量`；`Conservative～Trust-adjusted＝部分成長定價，新增需FETS`；`Trust-adjusted～Forward Anchor＝續抱、不追價`；`高於Forward Anchor＝需RES驗證`。

Bear/Base/Bull情境是把現價和14.1.4三個情境目標價比較，回答「現價落在哪個財務情境」；Price Zone回答「現價位於三層估值階梯哪一段」。兩者用途不同。

{chr(10).join(quick_rows)}

{''.join(stock_section(d) for d in rows)}
## Sources

| 類型 | 使用內容 | 檔案/來源 |
|---|---|---|
| 流程 | 台股個股分析固定流程 | `tw-stock-analysis-framework.md` |
| 候選排序 | {RUN_DATE} 本次 {stock_count} 檔候選與展開欄位 | `output/tw_stock_candidates_{OUTPUT_SUFFIX}.csv` |
| 市場 regime | {MARKET_INDEX_DATE} 加權指數 {fmt_pct(MARKET_DAILY_CHANGE_PCT)}，{MARKET_REGIME} | `output/tw_stock_screen_report_{OUTPUT_SUFFIX}.md`、`data/twse_mi_index_latest.json` |
| 持倉閘門 | 台股持股與台幣可用現金未取得 | 本地資料缺口 |
| 日價歷史 | {MARKET_INDEX_DATE} 參考收盤與成交值 | `data/tw_daily_price_history_by_stock.json` |
| 原始官方入口 | TWSE 行情/估值/公司資料/融資融券 | https://www.twse.com.tw/zh/ |
"""
    REPORT.write_text(body, encoding="utf-8")
    HTML_REPORT.write_text(render_html(rows, quick_rows, REPORT_TITLE), encoding="utf-8")
    print(REPORT)
    print(HTML_REPORT)


if __name__ == "__main__":
    main()
