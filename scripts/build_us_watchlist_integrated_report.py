#!/usr/bin/env python3
"""Build the integrated US multi-stock report.

This report keeps a variable multi-stock summary table and upgrades each ticker tab
with the deeper US single-stock framework: formal-close price stage,
verified long current-EPS P/E proxy, valuation-source breakdown, peer table,
Bear/Base/Bull, Price x Thesis, and non-mechanical stop-loss logic.
"""

from __future__ import annotations

import html as html_lib
import json
import math
import pathlib
import re
import statistics
import subprocess
import time
import urllib.request
from datetime import date, datetime
from html.parser import HTMLParser

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:  # Tests for pure valuation math should not require the scraper dependency.
    BeautifulSoup = None


BASE = pathlib.Path("/Users/linwj/Documents/股票分析")
BASIS_DATE = "2026-06-16"
RUN_DATE = "2026-06-17"
REPORT_TITLE = "美股多檔個股分析"

PRIMARY_OUT = BASE / "output/us_watchlist_integrated_analysis_20260617_basis_2026-06-16.html"
PRIMARY_DOC = BASE / "docs/reports/us_watchlist_integrated_analysis_20260617_basis_2026-06-16.html"
PRIMARY_PUB = BASE / "published_reports/us_watchlist_integrated_analysis_20260617_basis_2026-06-16.html"
PRIMARY_JSON = BASE / "output/us_watchlist_integrated_analysis_data_20260617_basis_2026-06-16.json"
VALUATION_SNAPSHOT = BASE / f"data/us_valuation_snapshot_{BASIS_DATE.replace('-', '')}.json"
FORWARD_EPS_EVIDENCE = BASE / f"data/us_forward_eps_evidence_{BASIS_DATE.replace('-', '')}.json"
POINT_IN_TIME_EPS_CACHE = BASE / "data/us_point_in_time_eps_history.json"

# Keep the user's "new version" path updated too.
LEGACY_OUT = BASE / "output/us_watchlist_full_analysis_20260616.html"
LEGACY_DOC = BASE / "docs/reports/us_watchlist_full_analysis_20260616.html"
LEGACY_PUB = BASE / "published_reports/us_watchlist_full_analysis_20260616.html"
LEGACY_JSON = BASE / "output/us_watchlist_full_analysis_data_20260616.json"

TICKERS = "LLY GE GEV ETN PANW CRWD ISRG XYL CEG RTX MU MRVL COHR ANET VRT GOOGL TSM NVDA AVGO".split()

IR_URLS = {
    "LLY": "https://investor.lilly.com/",
    "GE": "https://www.geaerospace.com/investor-relations",
    "GEV": "https://www.gevernova.com/investors",
    "ETN": "https://www.eaton.com/us/en-us/company/investor-relations.html",
    "PANW": "https://investors.paloaltonetworks.com/",
    "CRWD": "https://ir.crowdstrike.com/",
    "ISRG": "https://isrg.intuitive.com/",
    "XYL": "https://investors.xylem.com/",
    "CEG": "https://investor.constellationenergy.com/",
    "RTX": "https://www.rtx.com/investors",
    "MU": "https://investors.micron.com/",
    "MRVL": "https://investor.marvell.com/",
    "COHR": "https://www.coherent.com/company/investor-relations",
    "ANET": "https://investors.arista.com/",
    "VRT": "https://investors.vertiv.com/",
    "GOOGL": "https://abc.xyz/investor/",
    "TSM": "https://investor.tsmc.com/english",
    "NVDA": "https://investor.nvidia.com/",
    "AVGO": "https://investors.broadcom.com/",
}

# Verified research links available on or before the report basis date. These
# are used as cross-checks; company IR remains the preferred primary source.
RESEARCH_CROSSCHECKS = {
    "LLY": ("2026-04-30", "Q1 GLP-1 sales, total revenue and raised outlook cross-check", "https://www.marketwatch.com/story/lillys-stock-rallies-as-sales-of-glp-1-drugs-nearly-double-09c01977"),
    "GE": ("2026-04-21", "Q1 commercial/defense orders, revenue and guidance cross-check", "https://www.barrons.com/articles/ge-aerospace-earnings-stock-price-f1336e48"),
    "GEV": ("2026-04-22", "Q1 orders, backlog, segment margin and raised outlook primary release", "https://www.gevernova.com/sites/default/files/gev_webcast_pressrelease_04222026.pdf"),
    "ETN": ("2025-11-03", "Data-center construction backlog and liquid-cooling expansion cross-check", "https://www.marketwatch.com/story/eaton-takes-aim-at-500-billion-data-center-backlog-with-its-latest-biggest-buyout-this-year-73af5cc2"),
    "PANW": ("2026-06-03", "Fiscal Q3 revenue, backlog and AI-security demand cross-check", "https://www.barrons.com/articles/palo-alto-earnings-stock-price-edc413d0"),
    "CRWD": ("2026-06-03", "Fiscal Q1 ARR, revenue and raised outlook cross-check", "https://www.wsj.com/business/earnings/crowdstrike-lifts-outlook-after-swinging-to-first-quarter-profit-1a0b5a57"),
    "ISRG": ("2026-04-22", "Q1 procedure growth, placements, revenue and margin outlook cross-check", "https://www.barrons.com/articles/intuitive-surgical-earnings-stock-price-dd043033"),
    "XYL": ("2026-06-16", "Company filings and quarterly-results entry point", "https://investors.xylem.com/financial-information/quarterly-results"),
    "CEG": ("2026-05-11", "Q1 earnings, Crane restart and grid constraint cross-check", "https://www.barrons.com/articles/constellation-energy-earnings-stock-price-d3b7c846"),
    "RTX": ("2026-04-21", "Q1 backlog, segment growth and raised guidance cross-check", "https://www.wsj.com/business/earnings/rtx-boosts-guidance-on-defense-business-strength-b824a7a4"),
    "MU": ("2025-12-17", "DRAM supply constraint, HBM demand and capacity timing cross-check", "https://www.tomshardware.com/pc-components/dram/micron-outlines-grim-outlook-for-dram-supply-in-first-earnings-call-since-killing-crucial-memory-and-ssd-brand-ceo-says-it-can-only-meet-half-to-two-thirds-of-demand"),
    "MRVL": ("2026-05-27", "Fiscal Q1 AI bookings, data-center growth and raised outlook cross-check", "https://www.investors.com/news/technology/marvell-stock-mrvl-fiscal-q1-2027-earnings/"),
    "COHR": ("2026-05-06", "Fiscal Q3 revenue, gross margin and Q4 guidance cross-check", "https://www.barrons.com/articles/coherent-earnings-stock-price-960ce9bf"),
    "ANET": ("2026-05-06", "Q1 revenue, earnings, supply constraint and margin cross-check", "https://www.barrons.com/articles/arista-networks-earnings-stock-price-04ad6ebc"),
    "VRT": ("2026-04-22", "Q1 results and investor-presentation entry point", "https://investors.vertiv.com/financials/quarterly-results/default.aspx"),
    "GOOGL": ("2026-04-29", "Q1 Search, Cloud, Gemini adoption and capex cross-check", "https://www.androidcentral.com/phones/google-pixel/alphabet-earnings-q2-2026"),
    "TSM": ("2026-01-15", "2026 capex, advanced-process/packaging capacity and AI demand cross-check", "https://www.tomshardware.com/tech-industry/semiconductors/tsmc-very-nervous-about-ai-bubble-concerns-despite-another-record-setting-quarter-but-assured-of-demand-ceo-says-careless-investment-would-be-a-disaster-for-tsmc-for-sure-company-will-invest-usd52-usd56-billion-in-capex"),
    "NVDA": ("2026-05-21", "Fiscal Q1 revenue, platform mix, margin and Q2 outlook cross-check", "https://www.tomshardware.com/tech-industry/artificial-intelligence/nvidia-no-longer-reports-sales-of-graphics-solutions-as-a-separate-segment-posts-eye-watering-usd81-6-billion-q1-profit-thanks-to-ai-boom"),
    "AVGO": ("2026-06-03", "Fiscal Q2 AI semiconductor revenue, customer commitments and Q3 outlook cross-check", "https://www.wsj.com/business/earnings/broadcom-revenue-climbs-on-ai-chip-demand-7accd3b2"),
}

INDIRECT_SOURCES = {
    "LLY": ("2026-05-21", "Pipeline／替代產品：retatrutide Phase 3 顯示下一代 obesity franchise 延展性", "https://www.wsj.com/health/pharma/eli-lillys-new-weight-loss-treatment-shows-promising-results-ca189c18"),
    "GE": ("2026-04-21", "航空需求／油價：高油價與航空流量是 aftermarket 強度的反向產業訊號", "https://www.barrons.com/articles/ge-aerospace-earnings-stock-price-f1336e48"),
    "GEV": ("2026-05-20", "電網／資料中心：PJM 提前資料中心容量採購，反映區域容量短缺", "https://www.marketwatch.com/story/constellations-and-vistras-stocks-rally-as-power-grid-operator-speeds-up-data-center-deals-67b95021"),
    "ETN": ("2025-11-03", "資料中心建設：產業 construction backlog 與液冷併購支出驗證電力密度需求", "https://www.marketwatch.com/story/eaton-takes-aim-at-500-billion-data-center-backlog-with-its-latest-biggest-buyout-this-year-73af5cc2"),
    "PANW": ("2026-06-03", "AI agent 身分與存取風險提高，間接支持 identity/platform security 支出", "https://www.barrons.com/articles/palo-alto-earnings-stock-price-edc413d0"),
    "CRWD": ("2026-06-03", "同業交叉：PANW backlog 與 AI-security urgency 同步，支持資安需求不是單一公司現象", "https://www.barrons.com/articles/palo-alto-earnings-stock-price-edc413d0"),
    "ISRG": ("2026-04-22", "競爭／替代：Medtronic、J&J 與再製器械是程序量之外的反向產業訊號", "https://www.barrons.com/articles/intuitive-surgical-earnings-stock-price-dd043033"),
    "XYL": ("2026-06-16", "公共水務支出與客戶專案需以 EPA/地方預算和公司 orders 交叉驗證", "https://www.epa.gov/water-infrastructure"),
    "CEG": ("2026-05-20", "PJM 容量採購提前，為核電／獨立電力商的需求與容量價格間接訊號", "https://www.marketwatch.com/story/constellations-and-vistras-stocks-rally-as-power-grid-operator-speeds-up-data-center-deals-67b95021"),
    "RTX": ("2026-04-21", "國防預算與商用 aftermarket 同時支撐，但供應鏈與引擎維修成本會限制轉換", "https://www.wsj.com/business/earnings/rtx-boosts-guidance-on-defense-business-strength-b824a7a4"),
    "MU": ("2026-05-21", "NVIDIA 平台出貨與 AI 系統成長是 HBM 需求的客戶端間接訊號", "https://www.tomshardware.com/tech-industry/artificial-intelligence/nvidia-no-longer-reports-sales-of-graphics-solutions-as-a-separate-segment-posts-eye-watering-usd81-6-billion-q1-profit-thanks-to-ai-boom"),
    "MRVL": ("2026-05-21", "NVIDIA／hyperscaler AI 系統成長，支持 optics、switch、custom XPU attach 的需求鏈", "https://www.tomshardware.com/tech-industry/artificial-intelligence/nvidia-no-longer-reports-sales-of-graphics-solutions-as-a-separate-segment-posts-eye-watering-usd81-6-billion-q1-profit-thanks-to-ai-boom"),
    "COHR": ("2026-05-27", "Marvell 800G/1.6T 與 CPO bookings 是光元件供應鏈的獨立需求訊號", "https://www.investors.com/news/technology/marvell-stock-mrvl-fiscal-q1-2027-earnings/"),
    "ANET": ("2026-04-29", "Alphabet 大幅提高 AI CapEx，是 Ethernet/AI cluster networking 的客戶端訊號", "https://www.marketwatch.com/livecoverage/alphabet-earnings-google-stock-results-cloud-ai/card/alphabet-raises-ai-spending-plans-for-2026-and-2027-YemWtwomb9wm6FcozjEc"),
    "VRT": ("2026-04-29", "Hyperscaler AI CapEx 提高，間接支持機房電力與冷卻需求", "https://www.marketwatch.com/livecoverage/alphabet-earnings-google-stock-results-cloud-ai/card/alphabet-raises-ai-spending-plans-for-2026-and-2027-YemWtwomb9wm6FcozjEc"),
    "GOOGL": ("2026-06-03", "Broadcom 揭露 Google TPU 長約，從供應商端驗證自研 AI 計算投資", "https://www.wsj.com/business/earnings/broadcom-revenue-climbs-on-ai-chip-demand-7accd3b2"),
    "TSM": ("2026-05-21", "NVIDIA AI 平台營收與出貨是先進製程／封裝需求的客戶端交叉驗證", "https://www.tomshardware.com/tech-industry/artificial-intelligence/nvidia-no-longer-reports-sales-of-graphics-solutions-as-a-separate-segment-posts-eye-watering-usd81-6-billion-q1-profit-thanks-to-ai-boom"),
    "NVDA": ("2026-04-29", "Alphabet 2026/2027 CapEx 上修是 hyperscaler AI 基建需求的客戶端驗證", "https://www.marketwatch.com/livecoverage/alphabet-earnings-google-stock-results-cloud-ai/card/alphabet-raises-ai-spending-plans-for-2026-and-2027-YemWtwomb9wm6FcozjEc"),
    "AVGO": ("2026-04-29", "Alphabet CapEx 與 Cloud/AI 成長，從客戶端驗證 TPU 與 networking 需求", "https://www.marketwatch.com/livecoverage/alphabet-earnings-google-stock-results-cloud-ai/card/alphabet-raises-ai-spending-plans-for-2026-and-2027-YemWtwomb9wm6FcozjEc"),
}

GEV_MULTIBAGGER = {
    "conclusion": (
        "GEV 的需求、訂單、backlog、margin 與 FCF 已進入 Stage 2 財務驗證，"
        "但 2026-06-16 的 53.12x Forward P/E 也屬 Stage 3 高度定價。"
        "Base 情境不支持從 $982.35 再翻倍；較合理是 3–4 年約 1.1–1.6 倍，"
        "2 倍以上需要 2030–2031 Extreme Bull，機率低。"
    ),
    "primary_stage": "Stage 2：中期財務驗證",
    "secondary_stage": "Stage 3：市場高度定價",
    "signals": [
        ("總公司訂單 $18.3B，organic +71%；backlog 季增 $13B 至 $163B", "Stage 2", "正向", "2026-04-22 GEV 1Q26 press release", "A", "0–12 月", "財務已驗證"),
        ("Gas Power backlog 44GW、slot reservations 56GW；合計 100GW，年底目標至少 110GW", "Stage 1/2", "正向", "2026-04-22 GEV 1Q26 press release", "A", "6–24 月", "合約/預訂已驗證"),
        ("Electrification Q1 data-center equipment orders $2.4B，高於 2025 全年", "Stage 1/2", "正向", "2026-04-22 GEV press release/transcript", "A", "6–24 月", "訂單已驗證"),
        ("Electrification orders $7.1B、book-to-bill 約 2.5x；equipment backlog $38.6B、年增 75%", "Stage 2", "正向", "2026-04-22 GEV 1Q26 press release", "A", "0–24 月", "財務已驗證"),
        ("Revenue $9.3B、年增 16%；adjusted EBITDA margin 9.6%、年增 390bps", "Stage 2", "正向", "2026-04-22 GEV 1Q26 press release", "A", "0–12 月", "損益已驗證"),
        ("2026 guidance 上修至 revenue $44.5–45.5B、EBITDA margin 12–14%、FCF $6.5–7.5B", "Stage 2", "正向", "2026-04-22 GEV 1Q26 press release", "A-", "0–12 月", "仍待後續季度兌現"),
        ("Wind Q1 revenue -23%，segment EBITDA -$382M、margin -26.7%", "Stage 2", "負向", "2026-04-22 GEV 1Q26 press release", "A", "0–12 月", "財務已驗證"),
        ("基準日 Forward P/E 53.12x，股價已高於 Base fair", "Stage 3", "負向", "2026-06-16 同快照估值資料", "B", "即時", "價格已驗證")
    ],
    "fundamental_scores": [
        ("需求不可逆性與市場空間", 12, 12, "AI 用電、電網更新與可靠電源需求同時發生"),
        ("供給瓶頸與擴產難度", 10, 10, "燃氣輪機槽位、變壓器與 HVDC 產能具長交期"),
        ("技術、認證與客戶護城河", 9, 10, "大型 installed base、Grid/Power 整合能力；Wind 拖累扣 1"),
        ("客戶承諾、訂單與 backlog", 10, 10, "100GW backlog/slot reservations、Electrification book-to-bill 2.5x"),
        ("ASP、margin 與營運槓桿", 8, 10, "Power/Electrification margin 擴張，但 Wind 虧損"),
        ("營收、EPS 與 FCF 驗證", 8, 12, "Revenue、EBITDA、FCF 已驗證；Q1 FCF 含顯著 working-capital benefit"),
        ("市占率與競爭優勢", 4, 6, "Gas/installed base 強，惟同業擴產與專案執行仍需追蹤")
    ],
    "price_scores": [
        ("現價尚未反映 Base/Bull", 2, 12, "53.12x Forward P/E 已反映大量成長"),
        ("估值下檔保護與 FCF 支撐", 2, 8, "FCF 強但 EV/EBITDA 與 Forward P/E 偏高"),
        ("稀釋、淨負債與資本需求", 4, 5, "資產負債表仍強，且有回購；擴產與 Prolec 整合需資本"),
        ("擁擠度、預期門檻與時程", 1, 5, "AI power 敘事高度一致，必須持續超預期")
    ],
    "scenarios": [
        ("Bear", "2028", 52.0, "約 10.4%", 20.0, 30.0, 600.0, 0.61, 25, "Wind/專案成本拖累、需求遞延、multiple 收縮"),
        ("Base", "2028", 56.0, "約 13.5%", 28.0, 38.0, 1064.0, 1.08, 50, "Power/Electrification 依 backlog 轉收入，margin 持續改善"),
        ("Bull", "2030", 70.0, "約 16.2%", 42.0, 38.0, 1596.0, 1.62, 25, "AI/電網超級週期延長、Wind 修復、FCF 高轉換"),
        ("Extreme Bull", "2031", 80.0, "約 18.5%", 55.0, 42.0, 2310.0, 2.35, 5, "僅壓力測試：市占與 margin 同時大幅超預期")
    ],
    "weighted_multiple": 1.10,
    "final_label": "保留核心倉、停利交易倉／不追價",
    "confidence": "中高：需求、供給與財務三類證據齊全；但 3–5 年 EPS 與終值倍數仍屬研究假設",
    "recheck": "2026-07-22 Q2 財報後完整重評；平時每季更新",
    "early_triggers": "Gas slot conversion、Electrification book-to-bill/backlog、Wind 損失、2026 FCF guidance、股價或 Forward EPS 較本次變動 20%",
    "sources": [
        ("GE Vernova 1Q26 earnings press release", "https://www.gevernova.com/sites/default/files/gev_webcast_pressrelease_04222026.pdf"),
        ("GE Vernova 1Q26 earnings presentation", "https://www.gevernova.com/sites/default/files/gev_webcast_presentation_04222026.pdf"),
        ("GE Vernova 1Q26 earnings transcript", "https://www.gevernova.com/sites/default/files/gev_webcast_transcript_04222026.pdf"),
        ("GE Vernova investor overview", "https://www.gevernova.com/investors")
    ]
}

CONFIG = {
    "LLY": dict(
        company="Eli Lilly",
        industry="醫藥 / GLP-1",
        business="糖尿病、肥胖症、腫瘤與免疫藥物；Tirzepatide/Mounjaro/Zepbound 是核心成長引擎。",
        thesis="GLP-1 與代謝疾病平台仍是大型醫藥股中最強成長主線之一，但估值要求 EPS 和產能持續上修。",
        bear="藥價政策、同業 GLP-1 競爭、供應/產能瓶頸、臨床安全性、以及高估值壓縮。",
        peers=["NVO", "MRK", "AMGN", "ABBV"],
        mult=(25, 28, 32, 36),
        action="觀望 / 等回檔",
        priority="好公司但偏貴",
        memo_depth="deep",
        catalyst="GLP-1 產能、處方量、margin 與下一輪指引是 thesis 驗證核心。",
    ),
    "GE": dict(
        company="GE Aerospace",
        industry="航太引擎 / 維修",
        business="商用與軍用航太引擎、備件、維修服務；服務收入與 backlog 是主要護城河。",
        thesis="航太引擎與維修需求硬，服務收入品質好；但若現價高於 fair，新增倉位要等回檔或 EPS 上修。",
        bear="航太供應鏈、引擎品質/維修成本、航空景氣放緩、以及高品質溢價回落。",
        peers=["RTX", "HON", "TDG", "LMT"],
        mult=(34, 38, 42, 46),
        action="續抱可，新增觀望",
        priority="好公司但等回檔",
        memo_depth="standard",
        catalyst="商用航太交付、引擎維修服務收入、backlog 與 margin。",
    ),
    "GEV": dict(
        company="GE Vernova",
        industry="電力設備 / AI 電力",
        business="Gas Power、Grid、Wind；受惠資料中心電力、電網升級與燃氣輪機需求。",
        thesis="電力設備是 5-10 年主線，但 GEV 已是擁擠熱門交易；你的剩餘 2 股以續抱、風控、不加碼為主。",
        bear="估值高、風電波動、grid/gas backlog 若未延續、Q2 FCF 或 margin 沒上修會壓 multiple。",
        peers=["ETN", "VRT", "HUBB", "PWR"],
        mult=(40, 45, 52, 60),
        action="續抱 2 股 / 不加碼",
        priority="持股風控",
        memo_depth="deep",
        catalyst="AI 資料中心電力需求、grid backlog、Gas Power 訂單、FCF 轉換率。",
    ),
    "ETN": dict(
        company="Eaton",
        industry="電力設備 / 資料中心配電",
        business="電力管理、配電、工業與車用電氣設備；data center electrical orders 是核心催化。",
        thesis="品質比多數 AI infra 主題股穩，適合放在核心候選清單，但仍要等估值或技術回檔。",
        bear="資料中心訂單放緩、電力設備交易降溫、FCF/EV 倍數不低、工業週期回落。",
        peers=["GEV", "VRT", "HUBB", "PWR"],
        mult=(22, 26, 30, 34),
        action="等回檔小量研究",
        priority="優先研究",
        memo_depth="deep",
        catalyst="Data center orders、electrical backlog、organic growth、margin guide。",
    ),
    "PANW": dict(
        company="Palo Alto Networks",
        industry="資安平台",
        business="網路安全、雲安全、SASE、XSIAM/AI security 平台。",
        thesis="資安支出剛性高，平台化有護城河；但高估值需要 billings、ARR 與 margin 繼續證明。",
        bear="billings/guidance 放緩、平台化轉型折扣、同業競爭、AI 資安題材過熱。",
        peers=["CRWD", "ZS", "FTNT", "CHKP"],
        mult=(50, 60, 70, 80),
        action="觀望 / 等明顯回檔",
        priority="高估值觀察",
        memo_depth="standard",
        catalyst="Billings、RPO/ARR、platformization 進度與 operating margin。",
    ),
    "CRWD": dict(
        company="CrowdStrike",
        industry="雲端資安 / Endpoint",
        business="Falcon 平台、endpoint、cloud、identity、SIEM/LogScale。",
        thesis="雲端資安龍頭，ARR 韌性強，但 forward multiple 非常緊，適合等大幅回檔再研究。",
        bear="GAAP 獲利弱、Fwd P/E 極高、成長只要放慢就殺估值、事件風險。",
        peers=["PANW", "ZS", "S", "FTNT"],
        mult=(80, 95, 115, 135),
        action="觀望，不追",
        priority="高估值觀察",
        memo_depth="standard",
        catalyst="ARR、net retention、endpoint/cloud/security platform 擴張。",
    ),
    "ISRG": dict(
        company="Intuitive Surgical",
        industry="機器手術 / 醫療科技",
        business="da Vinci 系統、器械耗材、服務；裝機基礎與耗材 recurring revenue。",
        thesis="醫療科技龍頭、護城河強，但成長已非早期爆發；估值需搭配 procedure growth 修復。",
        bear="程序量放緩、系統裝機不足、醫院資本支出壓力、高估值。",
        peers=["SYK", "MDT", "EW", "BSX"],
        mult=(30, 35, 42, 48),
        action="觀望 / 等估值回落",
        priority="好公司但等回檔",
        memo_depth="standard",
        catalyst="Procedure growth、da Vinci 5 adoption、system placement、gross margin。",
    ),
    "XYL": dict(
        company="Xylem",
        industry="水處理 / 基礎設施",
        business="水泵、水處理、測量與基礎設施服務。",
        thesis="水資源與基建需求穩，波動低於 AI 熱門股；適合做防守型長線候選。",
        bear="成長速度較慢、估值若過高會壓報酬、公共基建預算延後。",
        peers=["WTS", "ITRI", "ECL", "DOV"],
        mult=(16, 18, 22, 25),
        action="可列低波動研究",
        priority="優先研究",
        memo_depth="standard",
        catalyst="Water infrastructure spending、margin、orders、free cash flow。",
    ),
    "CEG": dict(
        company="Constellation Energy",
        industry="核電 / 電力",
        business="美國核電與低碳電力資產，受惠 AI data center 長約電力需求。",
        thesis="核電重估與 AI 用電長線成立，但政策、電價與 PPA 節奏會讓估值波動大。",
        bear="核電營運、政策風險、電價回落、PPA 不如預期、題材擁擠。",
        peers=["VST", "NEE", "PEG", "DUK"],
        mult=(18, 20, 24, 28),
        action="觀望 / 等回檔",
        priority="好公司但等回檔",
        memo_depth="standard",
        catalyst="AI data center PPA、核電政策、電價與容量市場。",
    ),
    "RTX": dict(
        company="RTX",
        industry="國防航太",
        business="Pratt & Whitney、Collins Aerospace、Raytheon 防務系統。",
        thesis="防務和航太維修需求韌性高，估值相對部分航太高品質股不極端。",
        bear="引擎品質/供應鏈、國防預算、成本超支、商用航太週期。",
        peers=["GE", "LMT", "NOC", "HON"],
        mult=(20, 22, 26, 30),
        action="可小量研究",
        priority="優先研究",
        memo_depth="standard",
        catalyst="防務訂單、Pratt & Whitney 成本、Collins margin、backlog。",
    ),
    "MU": dict(
        company="Micron",
        industry="HBM / 記憶體",
        business="DRAM、NAND、HBM；受惠 AI memory 和報價循環。",
        thesis="HBM/DRAM 報價上行帶來 EPS 彈性，但記憶體高度循環，低 Forward P/E 不等於低風險。",
        bear="記憶體景氣高峰、capex 過度、報價回落、庫存循環反轉。",
        peers=["WDC", "STX", "NXPI", "ADI"],
        mult=(7, 9, 12, 15),
        action="高波動觀望",
        priority="高 beta 觀察",
        memo_depth="deep",
        catalyst="HBM 報價、DRAM/NAND 合約價、capex discipline、下一季 guide。",
    ),
    "MRVL": dict(
        company="Marvell",
        industry="ASIC / 網通半導體",
        business="資料中心、客製 ASIC、網通與儲存晶片。",
        thesis="AI ASIC 與網通 ramp 有想像空間，但估值吃執行與客戶 ramp 速度。",
        bear="AI revenue ramp 慢、非 AI 業務疲弱、毛利率未改善、估值高。",
        peers=["AVGO", "NVDA", "AMD", "QCOM"],
        mult=(40, 45, 55, 65),
        action="觀望 / 等回檔",
        priority="高 beta 觀察",
        memo_depth="standard",
        catalyst="AI custom silicon revenue、networking ramp、gross margin。",
    ),
    "COHR": dict(
        company="Coherent",
        industry="光通訊 / 光學元件",
        business="光通訊、雷射、材料與光學元件；AI 800G/1.6T/CPO 是彈性來源。",
        thesis="AI 光通訊彈性大，但你已清倉；重點是等訊號而非追回，需 EPS/FCF 修復。",
        bear="高 beta、FCF 壓力、毛利率、產能週期、客戶 capex 或光模組價格壓力。",
        peers=["LITE", "CIEN", "GLW", "AAOI"],
        mult=(35, 42, 48, 55),
        action="已清倉，等再進場訊號",
        priority="高 beta 觀察",
        memo_depth="deep",
        catalyst="800G/1.6T demand、光通訊訂單、margin、FCF 轉正。",
    ),
    "ANET": dict(
        company="Arista Networks",
        industry="AI Ethernet / 交換器",
        business="雲端資料中心 Ethernet switch，AI cluster networking。",
        thesis="AI Ethernet 受惠明確，但市場已充分認知；適合好公司 watch，不適合追價。",
        bear="估值高、雲端客戶集中、AI networking 競爭、成長降速。",
        peers=["CSCO", "JNPR", "CIEN", "HPE"],
        mult=(34, 38, 45, 52),
        action="觀望 / 等回檔",
        priority="好公司但偏貴",
        memo_depth="standard",
        catalyst="Cloud titan spending、AI Ethernet adoption、gross margin。",
    ),
    "VRT": dict(
        company="Vertiv",
        industry="資料中心電力 / 散熱",
        business="UPS、電力、液冷/熱管理與資料中心基建。",
        thesis="AI data center power/thermal 直接受惠，但交易擁擠且估值高。",
        bear="訂單預期太高、供應鏈/執行風險、margin 未上修、題材退潮。",
        peers=["ETN", "GEV", "NVT", "HUBB"],
        mult=(34, 38, 45, 52),
        action="觀望，不追",
        priority="好公司但偏貴",
        memo_depth="standard",
        catalyst="Data center thermal/power backlog、liquid cooling、margin。",
    ),
    "GOOGL": dict(
        company="Alphabet",
        industry="AI 軟體 / 雲 / 廣告",
        business="Google Search、YouTube、Cloud、Gemini/AI。",
        thesis="大型股中估值較可研究，現金流強；AI capex 是壓力也是護城河投資。",
        bear="搜尋競爭、監管、AI capex ROI 不明、雲端成長放緩。",
        peers=["MSFT", "META", "AMZN", "AAPL"],
        mult=(22, 24, 28, 32),
        action="大型股中較可研究",
        priority="優先研究",
        memo_depth="deep",
        catalyst="Search share、Cloud growth、AI monetization、capex discipline。",
    ),
    "TSM": dict(
        company="Taiwan Semiconductor",
        industry="晶圓代工 / AI 先進製程",
        business="先進製程、CoWoS/先進封裝、AI GPU/ASIC 供應鏈核心。",
        thesis="AI bottleneck 最核心之一，基本面品質高；若估值未過熱，是大型 AI 供應鏈首選候選。",
        bear="地緣政治、capex、匯率、先進製程需求波動、ADR 估值口徑差異。",
        peers=["NVDA", "AVGO", "ASML", "AMD"],
        mult=(18, 20, 24, 28),
        action="核心候選，等回檔",
        priority="優先研究",
        memo_depth="deep",
        catalyst="CoWoS capacity、N2/N3 utilization、AI/HPC revenue、monthly revenue。",
    ),
    "NVDA": dict(
        company="NVIDIA",
        industry="AI GPU / 平台",
        business="GPU、networking、CUDA 軟體生態與 AI 系統平台。",
        thesis="AI 算力核心，EPS 上修能力仍強，是本批最值得研究的大型 AI 股之一。",
        bear="hyperscaler capex 放緩、ASIC 替代、出口管制、gross margin 壓縮、估值壓縮。",
        peers=["AVGO", "AMD", "TSM", "MRVL"],
        mult=(18, 20, 24, 30),
        action="AI 大型股中較值得研究",
        priority="優先研究",
        memo_depth="deep",
        catalyst="Blackwell/rack-scale demand、networking、gross margin、China/export risk。",
    ),
    "AVGO": dict(
        company="Broadcom",
        industry="ASIC / 網通 / 軟體",
        business="AI ASIC、網通晶片、VMware 軟體現金流。",
        thesis="AI ASIC + 軟體現金流品質強，但現價已反映不少預期；新增等回檔或估計上修。",
        bear="客戶集中、VMware 整合、AI ASIC 預期過高、債務與軟體整合風險。",
        peers=["NVDA", "MRVL", "QCOM", "AMD"],
        mult=(20, 22, 27, 32),
        action="續抱可，新增等回檔",
        priority="好公司但偏貴",
        memo_depth="deep",
        catalyst="AI ASIC orders、VMware cash flow、margin、FCF/deleveraging。",
    ),
}

PEER_BUSINESS = {
    "NVO": "GLP-1 / diabetes / obesity drugs",
    "MRK": "大型製藥 / oncology / vaccines",
    "AMGN": "biotech / specialty pharma",
    "ABBV": "immunology / oncology / aesthetics",
    "RTX": "國防航太 / engines / systems",
    "HON": "工業自動化 / 航太 / 建築科技",
    "TDG": "航太零組件 / aftermarket",
    "LMT": "國防主承包商",
    "ETN": "配電 / 電力管理 / data center electrical",
    "VRT": "資料中心電力 / thermal",
    "HUBB": "電氣設備 / utility components",
    "PWR": "電力工程 / grid construction",
    "CRWD": "endpoint / cloud security",
    "ZS": "zero trust / cloud security",
    "FTNT": "network security appliances/platform",
    "CHKP": "enterprise network security",
    "PANW": "platform cybersecurity",
    "S": "AI endpoint security",
    "SYK": "medtech / orthopedics",
    "MDT": "medical devices",
    "EW": "structural heart devices",
    "BSX": "medical devices",
    "WTS": "water technologies",
    "ITRI": "utility metering / water analytics",
    "ECL": "water/industrial services",
    "DOV": "industrial components",
    "VST": "power generation / retail energy",
    "NEE": "utility / renewables",
    "PEG": "regulated utility",
    "DUK": "regulated utility",
    "NOC": "defense prime",
    "WDC": "storage / NAND / HDD",
    "STX": "HDD / mass storage",
    "NXPI": "auto/industrial semiconductors",
    "ADI": "analog semiconductors",
    "AVGO": "AI ASIC / networking / software",
    "NVDA": "AI GPU / networking platform",
    "AMD": "GPU / CPU / AI accelerators",
    "QCOM": "mobile/edge AI semiconductors",
    "LITE": "optical components",
    "CIEN": "optical networking systems",
    "GLW": "fiber/glass/optical materials",
    "AAOI": "optical transceivers/modules",
    "CSCO": "networking equipment",
    "JNPR": "networking equipment",
    "HPE": "servers / networking / AI systems",
    "NVT": "electrical enclosures / connections",
    "MSFT": "cloud / AI software",
    "META": "ads / AI infra / social platforms",
    "AMZN": "e-commerce / AWS / AI cloud",
    "AAPL": "consumer devices / services",
    "TSM": "advanced foundry / CoWoS",
    "ASML": "EUV lithography",
    "MRVL": "custom ASIC / networking silicon",
}

FIELDS = [
    "Market Cap",
    "PE Ratio",
    "Forward PE",
    "PS Ratio",
    "P/FCF Ratio",
    "EV / EBITDA",
    "Debt / Equity",
    "52-Week Price Change",
    "50-Day Moving Average",
    "200-Day Moving Average",
    "Average Volume (20 Days)",
    "Earnings Per Share (EPS)",
    "Gross Margin",
    "Operating Margin",
    "FCF Margin",
    "Price Target",
    "Analyst Consensus",
    "EPS Growth Forecast (3Y)",
    "Revenue Growth Forecast (3Y)",
    "Earnings Date",
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8", "ignore")
    except Exception:
        # Some local sessions lose system DNS while direct network is still fine.
        # Cloudflare currently serves stockanalysis.com at these addresses; curl
        # --resolve preserves TLS SNI while bypassing broken local DNS.
        completed = subprocess.run(
            [
                "curl",
                "--resolve",
                "stockanalysis.com:443:104.18.18.17",
                "-sL",
                "--max-time",
                "30",
                url,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if not completed.stdout:
            raise RuntimeError(f"empty curl response for {url}")
        return completed.stdout


class TextLineParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)


def text_lines(page_html: str) -> list[str]:
    if BeautifulSoup is None:
        parser = TextLineParser()
        parser.feed(page_html)
        return [line.strip() for line in parser.parts if line.strip()]
    soup = BeautifulSoup(page_html, "html.parser")
    return [line.strip() for line in soup.get_text("\n").split("\n") if line.strip()]


def after(lines: list[str], label: str) -> str | None:
    for index, value in enumerate(lines):
        if value == label and index + 1 < len(lines):
            return lines[index + 1]
    return None


def num(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).replace("$", "").replace(",", "").replace("%", "").strip()
    if text.lower() in {"n/a", "nan", "none", ""}:
        return None
    match = re.search(r"-?(?:\d+(?:\.\d+)?|\.\d+)", text)
    return float(match.group(0)) if match else None


def scaled_num(value: object) -> float | None:
    """Parse compact financial values such as 197.73M, 31.29B, or 1.98T."""
    if value is None:
        return None
    text = str(value).replace("$", "").replace(",", "").strip()
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*([KMBT]?)", text, re.I)
    if not match:
        return num(value)
    scale = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}
    return float(match.group(1)) * scale[match.group(2).upper()]


def price_from_lines(lines: list[str]) -> tuple[float | None, str, str, str | None, str | None]:
    for index, value in enumerate(lines):
        if "Real-Time Price" in value or "Delayed Price" in value:
            for j in range(index + 1, min(index + 14, len(lines))):
                if re.fullmatch(r"[0-9,]+(?:\.\d+)?", lines[j]):
                    price = num(lines[j])
                    move = lines[j + 1] if j + 1 < len(lines) else ""
                    timestamp = lines[j + 2] if j + 2 < len(lines) else ""
                    ah_price = None
                    ah_move = None
                    if j + 3 < len(lines) and re.fullmatch(r"[0-9,]+(?:\.\d+)?", lines[j + 3]):
                        ah_price = lines[j + 3]
                        ah_move = lines[j + 4] if j + 4 < len(lines) else None
                    return price, move, timestamp, ah_price, ah_move
    return None, "", "", None, None


def stats(ticker: str) -> dict:
    url = f"https://stockanalysis.com/stocks/{ticker.lower()}/statistics/"
    page = fetch(url)
    lines = text_lines(page)
    price, move, timestamp, ah_price, ah_move = price_from_lines(lines)
    data = {
        "ticker": ticker,
        "url": url,
        "stats_price": price,
        "stats_move": move,
        "stats_timestamp": timestamp,
        "after_hours_price": ah_price,
        "after_hours_move": ah_move,
    }
    for field in FIELDS:
        data[field] = after(lines, field)
    # Navigation also contains "Market Cap" and "Revenue". Read these values
    # from their actual report sections instead of accepting the first label.
    for index, value in enumerate(lines):
        if value == "Total Valuation":
            for j in range(index + 1, min(index + 12, len(lines) - 1)):
                if lines[j] == "Market Cap":
                    data["Market Cap"] = lines[j + 1]
                    break
        if value == "Income Statement":
            for j in range(index + 1, min(index + 12, len(lines) - 1)):
                if lines[j] == "Revenue":
                    data["Revenue (TTM Display Currency)"] = lines[j + 1]
                    break
    for index, value in enumerate(lines):
        if value.startswith(("NYSE:", "NASDAQ:")):
            data["company_line"] = lines[index - 1]
            data["exchange"] = value
            break
    return data


def history(ticker: str) -> list[dict]:
    url = f"https://stockanalysis.com/api/symbol/s/{ticker}/history?range=Max&period=Daily"
    data = json.loads(fetch(url))["data"]
    return data


def percentile(values: list[float], percentile_value: float) -> float | None:
    values = sorted(values)
    if not values:
        return None
    k = (len(values) - 1) * percentile_value / 100
    floor_index = math.floor(k)
    ceil_index = math.ceil(k)
    if floor_index == ceil_index:
        return values[int(k)]
    return values[floor_index] * (ceil_index - k) + values[ceil_index] * (k - floor_index)


def median(values: list[float | None]) -> float | None:
    cleaned = [value for value in values if value is not None]
    return statistics.median(cleaned) if cleaned else None


def change(new: float | None, old: float | None) -> float | None:
    return (new / old - 1) * 100 if new and old else None


def fmt(value: float | None, digits: int = 2) -> str:
    return "待補" if value is None else f"{value:,.{digits}f}"


def money(value: float | None) -> str:
    if value is None:
        return "待補"
    return f"-${fmt(abs(value))}" if value < 0 else f"${fmt(value)}"


def ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}x"


def pct(value: float | None) -> str:
    if value is None:
        return "待補"
    return ("+" if value >= 0 else "") + f"{value:.1f}%"


def parse_move_pct(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"\((-?\d+(?:\.\d+)?)%\)", text)
    return float(match.group(1)) if match else None


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value.strip())
    for fmt_string in ("%Y-%m-%d", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(cleaned, fmt_string).date()
        except ValueError:
            pass
    return None


def classify_price(price: float | None, stress: float | None, entry: float | None, fair: float | None, upper: float | None) -> str:
    if not price or not stress or not entry or not fair or not upper:
        return "資料不足"
    if price < stress:
        return "低於 Stress，先查 thesis 是否受傷"
    if price < entry:
        return "Stress/Entry 之間，可研究但不自動買"
    if price < fair:
        return "Entry/Fair 之間，等待修復或分批條件"
    if price < upper:
        return "Fair/Upper 之間，不追價"
    return "高於 Upper，需上修證據否則偏熱"


def confidence_for_proxy(label: str, rows: int, expected: int, ticker: str) -> str:
    if rows < expected:
        return "低/上市歷史不足"
    if label in {"2Y", "3Y"}:
        return "中（長期 proxy 降權）"
    if ticker in {"MU", "COHR", "MRVL", "GEV"}:
        return "中（EPS/題材波動較大）"
    return "中高"


def proxy_windows(history_rows: list[dict], eps_ttm: float | None, ticker: str) -> list[dict]:
    windows = []
    denominator_valid = eps_ttm is not None and eps_ttm > 0
    denominator_fragile = denominator_valid and eps_ttm < 0.50
    for label, expected in [("3M", 63), ("6M", 126), ("1Y", 252), ("2Y", 504), ("3Y", 756)]:
        sub = history_rows[: min(expected, len(history_rows))]
        values = [row["c"] / eps_ttm for row in sub if denominator_valid and row.get("c") is not None]
        p10 = percentile(values, 10)
        p50 = percentile(values, 50)
        p75 = percentile(values, 75)
        p90 = percentile(values, 90)
        start = sub[-1]["t"] if sub else "待補"
        end = sub[0]["t"] if sub else "待補"
        # Recompute once to guard against accidental mutation/rounding mistakes.
        verify_values = [row["c"] / eps_ttm for row in sub if denominator_valid and row.get("c") is not None]
        verified = (
            denominator_valid
            and len(values) == len(sub)
            and len(values) == len(verify_values)
            and (p10 is None or abs(p10 - percentile(verify_values, 10)) <= 0.0001)
            and (p50 is None or abs(p50 - percentile(verify_values, 50)) <= 0.0001)
            and (p75 is None or abs(p75 - percentile(verify_values, 75)) <= 0.0001)
            and (p90 is None or abs(p90 - percentile(verify_values, 90)) <= 0.0001)
        )
        confidence = confidence_for_proxy(label, len(sub), expected, ticker)
        if not denominator_valid:
            confidence = "不可用（TTM EPS 非正或缺失）"
        elif denominator_fragile:
            confidence = "低（TTM EPS 接近零，倍數高度失真）"
        windows.append(
            {
                "label": label,
                "expected": expected,
                "n": len(sub),
                "start": start,
                "end": end,
                "p10": p10,
                "p50": p50,
                "p75": p75,
                "p90": p90,
                "conf": confidence,
                "verified": verified,
                "denominator": eps_ttm,
                "denominator_status": (
                    "valid" if denominator_valid and not denominator_fragile
                    else "fragile" if denominator_fragile
                    else "invalid"
                ),
            }
        )
    return windows


def point_in_time_proxy_windows(
    history_rows: list[dict],
    eps_quarters: list[dict],
    eps_ttm: float | None,
    ticker: str,
) -> tuple[list[dict], dict]:
    """Build daily close / TTM EPS available strictly after SEC filing date."""
    quarters = sorted(
        (
            row for row in eps_quarters
            if row.get("period_end") and row.get("available_after") and num(row.get("eps")) is not None
        ),
        key=lambda row: (row["period_end"], row["available_after"], row.get("fiscal_period", "")),
    )
    point_rows = []
    for price_row in reversed(history_rows):  # oldest to newest
        trade_date = str(price_row.get("t") or "")
        close = num(price_row.get("c"))
        available = [row for row in quarters if row["available_after"] < trade_date]
        latest_four = available[-4:]
        if len(latest_four) != 4 or close is None:
            continue
        period_dates = [datetime.strptime(row["period_end"], "%Y-%m-%d").date() for row in latest_four]
        span = (period_dates[-1] - period_dates[0]).days
        gaps = [(period_dates[i + 1] - period_dates[i]).days for i in range(3)]
        if not 240 <= span <= 390 or any(gap < 45 or gap > 150 for gap in gaps):
            continue
        ttm = sum(float(row["eps"]) for row in latest_four)
        if ttm <= 0:
            continue
        point_rows.append({
            "date": trade_date,
            "close": close,
            "ttm_eps": ttm,
            "pe": close / ttm,
            "periods": [f"{row.get('fiscal_year')} {row.get('fiscal_period')}" for row in latest_four],
        })
    point_rows.reverse()  # newest first, matching history_rows
    latest_point_ttm = point_rows[0]["ttm_eps"] if point_rows else None
    audit_gap = (
        abs(latest_point_ttm - eps_ttm) / max(abs(eps_ttm), .01)
        if latest_point_ttm is not None and eps_ttm is not None
        else None
    )
    audit_ok = audit_gap is not None and audit_gap <= .10
    if not audit_ok:
        return proxy_windows(history_rows, eps_ttm, ticker), {
            "method": "current-TTM proxy fallback",
            "status": "fallback",
            "reason": (
                f"SEC point-in-time latest TTM audit gap {audit_gap:.1%} > 10%"
                if audit_gap is not None else "SEC quarterly EPS sequence insufficient"
            ),
            "latest_point_ttm": latest_point_ttm,
            "snapshot_ttm": eps_ttm,
            "audit_gap": audit_gap,
        }
    windows = []
    for label, expected in [("3M", 63), ("6M", 126), ("1Y", 252), ("2Y", 504), ("3Y", 756)]:
        sub = point_rows[: min(expected, len(point_rows))]
        values = [row["pe"] for row in sub]
        windows.append({
            "label": label,
            "expected": expected,
            "n": len(sub),
            "start": sub[-1]["date"] if sub else "待補",
            "end": sub[0]["date"] if sub else "待補",
            "p10": percentile(values, 10),
            "p50": percentile(values, 50),
            "p75": percentile(values, 75),
            "p90": percentile(values, 90),
            "conf": confidence_for_proxy(label, len(sub), expected, ticker),
            "verified": bool(values),
            "denominator": "point-in-time TTM EPS",
            "denominator_status": "valid",
            "method": "point-in-time",
        })
    return windows, {
        "method": "SEC point-in-time",
        "status": "ok",
        "reason": "Daily close / latest four diluted EPS quarters available strictly after SEC filing date",
        "latest_point_ttm": latest_point_ttm,
        "snapshot_ttm": eps_ttm,
        "audit_gap": audit_gap,
    }


def sec_quarterly_revenue_metrics(rows: list[dict], source_url: str | None) -> dict:
    """Calculate latest quarterly YoY and two-quarter acceleration from SEC facts."""
    usable = sorted(
        [
            row for row in rows
            if row.get("period_end") and row.get("filed") and row.get("revenue") is not None
            and row["filed"] <= BASIS_DATE and num(row.get("revenue")) is not None
        ],
        key=lambda row: row["period_end"],
    )
    yoy_rows = []
    for row in usable:
        end = datetime.strptime(row["period_end"], "%Y-%m-%d").date()
        prior_candidates = []
        for prior in usable:
            prior_end = datetime.strptime(prior["period_end"], "%Y-%m-%d").date()
            gap = (end - prior_end).days
            if 330 <= gap <= 400 and prior["period_end"] < row["period_end"] and num(prior.get("revenue")):
                prior_candidates.append((abs(gap - 365), prior))
        if prior_candidates:
            prior = min(prior_candidates, key=lambda pair: pair[0])[1]
            current_value, prior_value = num(row.get("revenue")), num(prior.get("revenue"))
            if current_value is not None and prior_value and prior_value > 0:
                yoy_rows.append({**row, "yoy": current_value / prior_value - 1})
    latest = yoy_rows[-1] if yoy_rows else None
    previous = yoy_rows[-2] if len(yoy_rows) >= 2 else None
    return {
        "latest_yoy": latest.get("yoy") if latest else None,
        "previous_yoy": previous.get("yoy") if previous else None,
        "acceleration": latest["yoy"] - previous["yoy"] if latest and previous else None,
        "period_end": latest.get("period_end") if latest else None,
        "filed": latest.get("filed") if latest else None,
        "source_url": source_url,
    }


def forward_equivalent_proxy(
    proxy_rows: list[dict],
    label: str,
    percentile_key: str,
    eps_ttm: float | None,
    valuation_eps: float | None,
) -> float | None:
    if not eps_ttm or eps_ttm <= 0 or not valuation_eps or valuation_eps <= 0:
        return None
    row = next((row for row in proxy_rows if row.get("label") == label), None)
    value = row.get(percentile_key) if row else None
    return value * eps_ttm / valuation_eps if value is not None else None


def build_rerating_model(item: dict) -> dict:
    """Separate evidence-adjusted fair value from the recent market regime."""
    metric = item.get("valuation_metric") or "P/E"
    proxy_rows = item.get("ps_proxy") if metric == "P/S" else item.get("proxy")
    proxy_rows = proxy_rows or []
    eps_ttm = item.get("eps_ttm")
    denominator = item.get("valuation_denominator")
    traditional_fair = item.get("fairM")
    if metric == "P/S":
        equivalents = {
            f"{label}_{key}": (
                row.get(key)
                if (row := next((r for r in proxy_rows if r.get("label") == label), None))
                else None
            )
            for label in ("3M", "6M", "1Y")
            for key in ("p50", "p75", "p90")
        }
    else:
        equivalents = {
            f"{label}_{key}": forward_equivalent_proxy(
                proxy_rows, label, key, eps_ttm, denominator
            )
            for label in ("3M", "6M", "1Y")
            for key in ("p50", "p75", "p90")
        }
    recent_p50_values = [
        equivalents.get("3M_p50"),
        equivalents.get("6M_p50"),
    ]
    recent_p50_values = [value for value in recent_p50_values if value is not None]
    recent_raw = statistics.median(recent_p50_values) if len(recent_p50_values) == 2 else None
    one_year_p90 = equivalents.get("1Y_p90")
    recent_effective = (
        min(recent_raw, one_year_p90)
        if recent_raw is not None and one_year_p90 is not None
        else None
    )
    recent_p75_values = [
        equivalents.get("3M_p75"),
        equivalents.get("6M_p75"),
    ]
    recent_p75_values = [value for value in recent_p75_values if value is not None]
    regime_p75 = statistics.median(recent_p75_values) if len(recent_p75_values) == 2 else None
    recent_p90_values = [
        equivalents.get("3M_p90"),
        equivalents.get("6M_p90"),
    ]
    recent_p90_values = [value for value in recent_p90_values if value is not None]
    recent_p90 = statistics.median(recent_p90_values) if len(recent_p90_values) == 2 else None
    # Overheat describes the recent regime itself. The 1Y P90 caps the recent
    # effective anchor, but must not pull the 3M/6M P90 boundary downward.
    overheat = recent_p90

    evidence = [
        row for row in item.get("rerating_evidence", [])
        if row.get("verified")
        and row.get("source_url")
        and row.get("date")
        and row["date"] <= BASIS_DATE
        and row.get("type") in {
            "forward_eps_revision",
            "revenue_acceleration",
            "margin_improvement",
            "fcf_improvement",
            "backlog_rpo_orders",
            "business_model_upgrade",
            "customer_capex_demand",
            "capacity_supply_expansion",
            "product_adoption",
        }
    ]
    confirmed_type_names = {
        "forward_eps_revision",
        "revenue_acceleration",
        "margin_improvement",
        "fcf_improvement",
    }
    early_type_names = {
        "backlog_rpo_orders",
        "business_model_upgrade",
        "customer_capex_demand",
        "capacity_supply_expansion",
        "product_adoption",
    }
    evidence_types = {row["type"] for row in evidence}
    confirmed_types = evidence_types & confirmed_type_names
    early_types = evidence_types & early_type_names
    evidence_count = len(evidence)
    six_month_row = next((row for row in proxy_rows if row.get("label") == "6M"), {})
    denominator_positive = bool(denominator and denominator > 0)
    gates = {
        "positive_eps": denominator_positive and (metric == "P/S" or bool(eps_ttm and eps_ttm > 0)),
        "recent_above_traditional": bool(
            traditional_fair
            and equivalents.get("3M_p50")
            and equivalents.get("6M_p50")
            and equivalents["3M_p50"] > traditional_fair
            and equivalents["6M_p50"] > traditional_fair
        ),
        "six_month_persistence": bool(
            six_month_row.get("n", 0) >= six_month_row.get("expected", 126) * 0.80
        ),
        "fundamental_evidence": evidence_count >= 1,
        "effective_anchor_above_fair": bool(
            recent_effective and traditional_fair and recent_effective > traditional_fair
        ),
    }
    market_score = (
        (15.0 if gates["positive_eps"] and equivalents.get("3M_p50") and traditional_fair and equivalents["3M_p50"] > traditional_fair else 0.0)
        + (20.0 if gates["positive_eps"] and equivalents.get("6M_p50") and traditional_fair and equivalents["6M_p50"] > traditional_fair else 0.0)
        + (5.0 if gates["positive_eps"] and gates["six_month_persistence"] else 0.0)
        + (10.0 if gates["positive_eps"] and gates["effective_anchor_above_fair"] else 0.0)
    )
    # One underlying event may mention EPS, revenue, margin, and backlog.
    # Score the origin once at its strongest verified level so a single
    # earnings release cannot manufacture several independent signals.
    origin_scores: dict[str, dict] = {}
    for row in evidence:
        origin_id = row.get("origin_id") or f"{row.get('date')}|{row.get('source_url')}"
        level = row.get("level", "C")
        base_score = {"A": 10.0, "B": 5.0, "C": 2.5}.get(level, 0.0)
        signed_score = base_score if row.get("direction", "positive") == "positive" else -base_score
        bucket = "confirmed" if row.get("type") in confirmed_type_names else "early"
        current = origin_scores.get(origin_id)
        if current is None or abs(signed_score) > abs(current["score"]):
            origin_scores[origin_id] = {
                "score": signed_score,
                "bucket": bucket,
            }
    confirmed_score = max(
        -30.0,
        min(30.0, sum(row["score"] for row in origin_scores.values() if row["bucket"] == "confirmed")),
    )
    early_score = max(
        -20.0,
        min(20.0, sum(row["score"] for row in origin_scores.values() if row["bucket"] == "early")),
    )
    scored_origins: set[str] = set()
    for row in evidence:
        origin_id = row.get("origin_id") or f"{row.get('date')}|{row.get('source_url')}"
        winning = origin_scores.get(origin_id, {})
        row_bucket = "confirmed" if row.get("type") in confirmed_type_names else "early"
        row["score_contribution"] = (
            winning.get("score", 0.0)
            if origin_id not in scored_origins and winning.get("bucket") == row_bucket
            else 0.0
        )
        scored_origins.add(origin_id)
    activation_score = market_score + confirmed_score + early_score
    activation_score = max(0.0, min(100.0, activation_score))
    activation_likelihood = activation_score / 100.0
    # The valuation blend is fixed at 50%. Activation likelihood is reported
    # separately as confidence and must never alter the calculated fair value.
    rerating_blend_weight = 0.50
    active = gates["positive_eps"] and recent_effective is not None and traditional_fair is not None
    adjusted_fair = (
        traditional_fair + max(0.0, recent_effective - traditional_fair) * rerating_blend_weight
        if active and recent_effective is not None
        else traditional_fair
    )
    current_multiple = item.get("current_implied_multiple")
    if not gates["positive_eps"]:
        classification = f"{metric} Rerating 不適用；估值分母非正或缺失"
    elif current_multiple is None:
        classification = f"模型已計算，但現行 {metric} 缺值"
    elif current_multiple <= adjusted_fair:
        classification = "Rerating Fair 內"
    elif regime_p75 and current_multiple <= regime_p75:
        classification = "近期市場常態區（非內在合理價）"
    elif overheat and current_multiple <= overheat:
        classification = "偏熱但未達近期 P90"
    else:
        classification = "高於近期 P90，過熱／需新上修證據"
    return {
        **equivalents,
        "traditional_fair": traditional_fair,
        "recent_raw_p50": recent_raw,
        "recent_effective": recent_effective,
        "regime_p75": regime_p75,
        "overheat_p90": overheat,
        "evidence": evidence,
        "evidence_count": evidence_count,
        "confirmed_evidence_count": len(confirmed_types),
        "early_evidence_count": len(early_types),
        "market_score": market_score,
        "confirmed_score": confirmed_score,
        "early_score": early_score,
        "activation_score": activation_score,
        "activation_likelihood": activation_likelihood,
        "evidence_weight": rerating_blend_weight if active else 0.0,
        "rerating_blend_weight": rerating_blend_weight if active else 0.0,
        "gates": gates,
        "active": active,
        "adjusted_fair": adjusted_fair,
        "adjusted_fair_price": adjusted_fair * denominator if adjusted_fair and denominator else None,
        "regime_p75_price": regime_p75 * denominator if regime_p75 and denominator else None,
        "overheat_price": overheat * denominator if overheat and denominator else None,
        "classification": classification,
    }


def structured_rerating_evidence(
    explicit_evidence: list[dict],
    crosscheck: tuple[str, str, str] | None,
    indirect: tuple[str, str, str] | None = None,
) -> list[dict]:
    """Convert already-verified report events into conservative evidence types."""
    evidence = [dict(row) for row in explicit_evidence]
    for row in evidence:
        row.setdefault("direction", "positive")
        row.setdefault("level", "A")
        row.setdefault("origin_id", f"{row.get('date')}|{row.get('source_url')}")
        row.setdefault("verification", "明示結構化證據；來源與日期已提供")
        row.setdefault("verified", True)
    existing = {row.get("type") for row in evidence}
    for event, evidence_basis, default_level in [
        (crosscheck, "公司／財報事件交叉檢查", "A"),
        (indirect, "客戶／產業早期訊號", "B"),
    ]:
        if not event:
            continue
        event_date, description, source_url = event
        text = description.lower()
        negative = any(
            word in text
            for word in ("slowed", "lowered", "cut", "decline", "down ", "fell", "weaker")
        )
        inferred_types = []
        has_revenue_growth_phrase = any(
            word in text for word in ("revenue", "sales", "organic growth", "organic-growth")
        )
        has_positive_revision_phrase = any(
            word in text for word in ("raised", "guide", "guidance", "outlook", "+")
        )
        if (
            (("eps" in text or has_revenue_growth_phrase) and has_positive_revision_phrase)
            or ("raised" in text and any(word in text for word in ("outlook", "guidance")))
            or "earnings growth" in text
        ):
            inferred_types.append("forward_eps_revision")
        if (
            has_revenue_growth_phrase
            and any(word in text for word in ("raised", "growth", "outlook", "guidance", "+", "above"))
        ):
            inferred_types.append("revenue_acceleration")
        if "margin" in text and any(word in text for word in ("improv", "expan", "record", "+")):
            inferred_types.append("margin_improvement")
        if any(word in text for word in ("fcf", "free cash flow", "cash-flow")) and any(
            word in text for word in ("improv", "growth", "record", "raised", "+")
        ):
            inferred_types.append("fcf_improvement")
        if any(word in text for word in ("orders", "backlog", "rpo", "arr")) and any(
            word in text for word in ("$", "record", "growth", "+", "raised", "above")
        ):
            inferred_types.append("backlog_rpo_orders")
        if any(word in text for word in ("capex", "customer demand", "hyperscaler", "end demand")):
            inferred_types.append("customer_capex_demand")
        if any(word in text for word in ("capacity", "supply constraint", "utilization", "expansion")):
            inferred_types.append("capacity_supply_expansion")
        if any(word in text for word in ("adoption", "shipments", "new products", "platform")):
            inferred_types.append("product_adoption")
        if any(word in text for word in ("new products", "acquisition", "business shift")) and any(
            word in text for word in ("revenue", "bookings", "growth", "%")
        ):
            inferred_types.append("business_model_upgrade")
        if negative and not inferred_types:
            if any(word in text for word in ("eps", "guide", "outlook")):
                inferred_types.append("forward_eps_revision")
            if any(word in text for word in ("revenue", "sales", "growth", "arr")):
                inferred_types.append("revenue_acceleration")
        source_level = default_level
        if default_level == "A" and source_url in IR_URLS.values():
            # A landing page is traceable but weaker than an exact filing,
            # release, transcript, or PDF.
            source_level = "B"
        elif default_level == "A" and not any(
            host in source_url
            for host in ("sec.gov", ".pdf", "/news-releases/", "/press-releases/")
        ):
            source_level = "C"
        if default_level == "B" and any(
            host in source_url for host in ("marketwatch.com", "investors.com", "wsj.com", "businessinsider.com")
        ):
            source_level = "C"
        origin_id = f"{event_date}|{source_url}"
        for evidence_type in inferred_types:
            if evidence_type in existing:
                continue
            evidence.append(
                {
                    "type": evidence_type,
                    "description": description,
                    "date": event_date,
                    "source_url": source_url,
                    "verified": True,
                    "basis": evidence_basis,
                    "level": source_level,
                    "direction": "negative" if negative else "positive",
                    "origin_id": origin_id,
                    "verification": "來源連結、事件日期與方向已納入；同一原始事件僅計分一次",
                }
            )
            existing.add(evidence_type)
    return evidence


def ps_proxy_windows(
    history_rows: list[dict],
    current_ps: float | None,
    current_close: float | None,
    ticker: str,
) -> list[dict]:
    """Historical price / current-sales proxy, normalized from the current P/S."""
    windows = []
    denominator_valid = bool(current_ps and current_ps > 0 and current_close and current_close > 0)
    for label, expected in [("3M", 63), ("6M", 126), ("1Y", 252), ("2Y", 504), ("3Y", 756)]:
        sub = history_rows[: min(expected, len(history_rows))]
        values = [
            current_ps * row["c"] / current_close
            for row in sub
            if denominator_valid and row.get("c") is not None
        ]
        p10 = percentile(values, 10)
        p50 = percentile(values, 50)
        p90 = percentile(values, 90)
        verified = denominator_valid and len(values) == len(sub)
        confidence = confidence_for_proxy(label, len(sub), expected, ticker)
        if not denominator_valid:
            confidence = "不可用（P/S 或正式收盤缺失）"
        elif label in {"2Y", "3Y"}:
            confidence = "中低（current-sales proxy，未使用歷史營收序列）"
        else:
            confidence = "中（current-sales proxy）"
        windows.append(
            {
                "label": label,
                "expected": expected,
                "n": len(sub),
                "start": sub[-1]["t"] if sub else "待補",
                "end": sub[0]["t"] if sub else "待補",
                "p10": p10,
                "p50": p50,
                "p90": p90,
                "conf": confidence,
                "verified": verified,
                "basis_ps": current_ps,
                "basis_close": current_close,
            }
        )
    return windows


def tag_class(text: str) -> str:
    if any(word in text for word in ["高於 Upper", "偏熱", "過熱"]):
        return "overheat"
    if any(word in text for word in ["低於 Stress", "thesis 是否受傷", "thesis damaged"]):
        return "risk"
    if "Fair/Upper" in text:
        return "watch"
    if "Entry/Fair" in text:
        return "key"
    if any(word in text for word in ["不追", "偏貴", "清倉", "不加碼", "風險", "高估值", "負向"]):
        return "risk"
    if any(word in text for word in ["等待", "觀望", "回檔"]):
        return "watch"
    if any(word in text for word in ["優先", "研究", "核心"]):
        return "key"
    return ""


def escape(value: object) -> str:
    return html_lib.escape("" if value is None else str(value))


def strong(value: str, class_name: str = "key") -> str:
    return f'<strong class="{class_name}">{value}</strong>'


def money_html(value: float | None, class_name: str = "key") -> str:
    return strong(money(value), class_name) if value is not None else '<span class="tag muted">待補</span>'


def ratio_html(value: float | None, class_name: str = "key") -> str:
    return strong(ratio(value), class_name) if value is not None else '<span class="tag muted">n/a</span>'


def trailing_pe_html(item: dict) -> str:
    eps = item.get("eps_ttm")
    if eps is not None and eps <= 0:
        return '<span class="tag muted">N/M（EPS 為負）</span>'
    return ratio_html(item.get("pe_calc"))


def pct_html(value: float | None) -> str:
    if value is None:
        return '<span class="tag muted">待補</span>'
    return strong(pct(value), "positive" if value >= 0 else "negative")


def tag_html(text: str) -> str:
    return f'<span class="tag {tag_class(text)}">{escape(text)}</span>'


def table_rows(rows: list[str]) -> str:
    return "".join(rows)


def load_valuation_snapshot() -> dict:
    if not VALUATION_SNAPSHOT.exists():
        raise RuntimeError(
            f"missing valuation snapshot for basis date {BASIS_DATE}: {VALUATION_SNAPSHOT}"
        )
    payload = json.loads(VALUATION_SNAPSHOT.read_text())
    if payload.get("basis_date") != BASIS_DATE:
        raise RuntimeError(
            f"valuation snapshot date {payload.get('basis_date')} != report basis {BASIS_DATE}"
        )
    missing = [ticker for ticker in TICKERS if ticker not in payload.get("tickers", {})]
    if missing:
        raise RuntimeError(f"valuation snapshot missing tickers: {missing}")
    return payload


def load_forward_eps_evidence() -> dict:
    if not FORWARD_EPS_EVIDENCE.exists():
        return {"basis_date": BASIS_DATE, "tickers": {}}
    payload = json.loads(FORWARD_EPS_EVIDENCE.read_text())
    if payload.get("basis_date") != BASIS_DATE:
        raise RuntimeError(
            f"forward EPS evidence date {payload.get('basis_date')} != report basis {BASIS_DATE}"
        )
    return payload


def financials_snapshot(ticker: str) -> dict:
    """Read the latest TTM income-statement snapshot used before the basis date."""
    url = f"https://stockanalysis.com/stocks/{ticker.lower()}/financials/"
    text = fetch(url)

    def first_array_number(field: str) -> float | None:
        match = re.search(rf"{re.escape(field)}:\[([^,\]]+)", text)
        if not match:
            return None
        token = match.group(1).strip()
        if token in {"null", "undefined", ""}:
            return None
        try:
            return float(token)
        except ValueError:
            return num(token)

    last_date = None
    match = re.search(r'lastTrailingDate:"([^"]+)"', text)
    if match:
        last_date = match.group(1)
    financial_currency = None
    match = re.search(r'curr:\{[^}]*financial:"([^"]+)"', text)
    if match:
        financial_currency = match.group(1)
    return {
        "financials_url": url,
        "revenue_ttm": first_array_number("revenue"),
        "net_income_ttm": first_array_number("netIncome"),
        "shares_diluted_ttm": first_array_number("sharesDiluted"),
        "eps_diluted_ttm_financials": first_array_number("epsDiluted"),
        "profit_margin_ttm": first_array_number("profitMargin"),
        "financial_currency": financial_currency,
        "financial_last_date": last_date,
    }


def supplemental_eps_sources(snapshot: dict) -> list[dict[str, str]]:
    """Return non-valuation EPS evidence that should be disclosed, not used for targets."""
    rows: list[dict[str, str]] = []
    for field, label, confidence in [
        ("company_guidance_eps", "Company guidance EPS", "High"),
        ("fy1_consensus_eps", "FY1 consensus EPS", "High"),
        ("fy2_consensus_eps", "FY2 consensus EPS", "High"),
        ("ntm_consensus_eps", "NTM consensus EPS", "High"),
        ("fy2027e_consensus_eps", "FY2027E consensus EPS", "High"),
        ("fy2026e_consensus_eps", "FY2026E consensus EPS", "High"),
    ]:
        value = num(snapshot.get(field))
        if value is None:
            continue
        rows.append({
            "label": label,
            "value": f"{value:.4f}",
            "confidence": confidence,
            "note": str(snapshot.get(f"{field}_basis") or snapshot.get("forward_eps_source_url") or snapshot.get("valuation_eps_basis") or "snapshot field"),
        })
    analyst_count = num(
        snapshot.get("analyst_count")
        or snapshot.get("consensus_analyst_count")
        or snapshot.get("fy1_analyst_count")
        or snapshot.get("ntm_analyst_count")
    )
    if analyst_count is not None:
        rows.append({
            "label": "Analyst count",
            "value": f"{analyst_count:.0f}",
            "confidence": "Context",
            "note": "揭露 coverage 深度；不直接作 valuation EPS",
        })
    return rows


def select_valuation_eps(snapshot: dict) -> tuple[float | None, str, str, str]:
    """Use same-snapshot implied NTM EPS proxy for valuation when Forward P/E exists."""
    close = num(snapshot.get("close"))
    forward_pe = num(snapshot.get("forward_pe"))
    if close is not None and forward_pe:
        return (
            close / forward_pe,
            "same-snapshot implied NTM EPS proxy = close / Forward P/E",
            "IMPLIED_NTM_FROM_FORWARD_PE",
            "Medium-High",
        )
    # A saved explicit valuation EPS with a documented basis is a fallback for
    # special cases where Forward P/E is unavailable or unusable, especially
    # ADR/common-share and cross-currency conversions. It is not the default.
    explicit = num(snapshot.get("valuation_eps"))
    explicit_basis = snapshot.get("valuation_eps_basis")
    if explicit is not None and explicit_basis and explicit_basis != "not available":
        return (
            explicit,
            explicit_basis,
            str(snapshot.get("valuation_eps_type") or "EXPLICIT_VALUATION_EPS_OVERRIDE"),
            str(snapshot.get("valuation_eps_confidence") or "Medium"),
        )
    return None, "not available", "UNAVAILABLE", "Blocked"


def snapshot_valuation_row(snapshot: dict) -> dict:
    """Return the single valuation row that every report section must reuse."""
    valuation_eps, valuation_eps_basis, valuation_eps_type, valuation_eps_confidence = select_valuation_eps(snapshot)
    price = num(snapshot.get("close"))
    pe = num(snapshot.get("pe"))
    eps_ttm = num(snapshot.get("ttm_eps"))
    internally_blocked = False
    if price is not None and pe is not None and eps_ttm is not None:
        calculated_pe = price / eps_ttm
        internally_blocked = abs(calculated_pe - pe) / max(abs(pe), 1) > 0.03
    return {
        "price": price,
        "pe": pe,
        "fpe": num(snapshot.get("forward_pe")),
        "eps_ttm": eps_ttm,
        "eps_fwd": None if internally_blocked else valuation_eps,
        "valuation_eps_basis": valuation_eps_basis,
        "valuation_eps_type": valuation_eps_type,
        "valuation_eps_confidence": valuation_eps_confidence,
        "valuation_blocked": internally_blocked,
    }


def validate_valuation_snapshot(ticker: str, snapshot: dict, history_close: float) -> str | None:
    snap_close = num(snapshot.get("close"))
    pe = num(snapshot.get("pe"))
    fpe = num(snapshot.get("forward_pe"))
    eps_ttm = num(snapshot.get("ttm_eps"))
    valuation_eps, valuation_basis, valuation_eps_type, valuation_eps_confidence = select_valuation_eps(snapshot)
    stored_valuation_eps = num(snapshot.get("valuation_eps"))

    if snap_close is None or abs(snap_close - history_close) > 0.02:
        raise RuntimeError(
            f"{ticker} snapshot close {snap_close} != {BASIS_DATE} history close {history_close}"
        )
    if pe is not None and eps_ttm is not None:
        calculated_pe = snap_close / eps_ttm
        mismatch = abs(calculated_pe - pe) / max(abs(pe), 1)
        if mismatch > 0.03:
            return (
                f"時間錯配：close/TTM EPS={calculated_pe:.2f}x vs source P/E={pe:.2f}x "
                f"（差異 {mismatch:.1%} > 3%）；改採 close/TTM EPS 重算值並降低信心"
            )
    if fpe is not None and stored_valuation_eps is not None and "consensus" not in valuation_basis.lower():
        calculated_eps = snap_close / fpe
        mismatch = abs(calculated_eps - stored_valuation_eps) / max(abs(stored_valuation_eps), 0.01)
        if mismatch > 0.01:
            return (
                f"Forward EPS 錯配：close/Forward P/E={calculated_eps:.2f} "
                f"vs snapshot EPS={stored_valuation_eps:.2f}（差異 {mismatch:.1%} > 1%）；"
                "改採明示 valuation EPS 重算 Forward P/E 並降低信心"
            )
    return None


def historical_forward_multiple_anchor(
    proxy_rows: list[dict],
    eps_ttm: float | None,
    valuation_eps: float | None,
) -> dict:
    """Use 2Y/3Y point-in-time P50 as the normalized trailing anchor."""
    raw = {}
    converted = {}
    if not eps_ttm or eps_ttm <= 0:
        return {"two_year": None, "three_year": None, "median": None}
    for row in proxy_rows:
        if row.get("label") in {"2Y", "3Y"} and row.get("p50") is not None:
            raw[row["label"]] = row["p50"]
            if valuation_eps and valuation_eps > 0:
                converted[row["label"]] = row["p50"] * eps_ttm / valuation_eps
    values = [raw.get("2Y"), raw.get("3Y")]
    values = [value for value in values if value is not None]
    return {
        "two_year": raw.get("2Y"),
        "three_year": raw.get("3Y"),
        "median": statistics.median(values) if values else None,
        "normalized_trailing_pe": statistics.median(values) if values else None,
        "two_year_forward_equivalent": converted.get("2Y"),
        "three_year_forward_equivalent": converted.get("3Y"),
    }


def result(value, formula: str, source: str, confidence: str, warning: str | None = None) -> dict:
    return {
        "value": value,
        "formula": formula,
        "source": source,
        "confidence": confidence,
        "warning": warning,
    }


def compute_eps_bridge(item: dict) -> dict:
    current_price = item.get("close")
    ttm_eps = item.get("eps_ttm")
    forward_pe = item.get("fpe")
    valuation_eps = item.get("valuation_eps")
    growth_bridge = (
        valuation_eps / ttm_eps - 1
        if valuation_eps and ttm_eps and valuation_eps > 0 and ttm_eps > 0
        else None
    )
    implied_only = str(item.get("valuation_eps_type") or "").startswith("IMPLIED_")
    warning = None
    if valuation_eps is None:
        warning = "Missing Data: Valuation EPS 不可用，Growth Pass-through 不得計算。"
    elif implied_only and not has_direct_forward_eps(item):
        warning = "只有 same-snapshot implied EPS，沒有直接 consensus EPS；q_final hard cap = 65%。"
    elif implied_only:
        warning = "valuation EPS 採 same-snapshot implied EPS；FY/NTM consensus 已另列供 FETS/檢核，不與 implied EPS 混用。"
    return {
        "current_price": result(current_price, "基準日正式收盤價", item.get("basis_date") or BASIS_DATE, "High"),
        "ttm_eps": result(ttm_eps, "最新已公布 trailing 12-month EPS", item.get("eps_ttm_basis") or "valuation snapshot", item.get("valuation_confidence") or "Medium"),
        "forward_pe": result(forward_pe, "同快照來源 Forward P/E", item.get("valuation_snapshot_url") or "valuation snapshot", "Medium-High"),
        "valuation_eps": result(valuation_eps, "Current Price / Forward P/E", item.get("valuation_eps_basis") or "valuation snapshot", item.get("valuation_eps_confidence") or "Medium", warning),
        "eps_growth_bridge": result(growth_bridge, "Valuation EPS / TTM EPS - 1", "computed", "Medium" if growth_bridge is not None else "Blocked", warning),
        "implied_eps_only": implied_only,
        "warning": warning,
    }


def compute_ttm_pe_proxy(history_rows: list[dict], eps_ttm: float | None, ticker: str) -> dict:
    proxy = proxy_windows(history_rows, eps_ttm, ticker)
    return result(
        proxy,
        "Historical closing price / latest TTM EPS",
        "StockAnalysis Max history API + same-snapshot TTM EPS",
        "Medium-High" if proxy and all(row.get("verified") for row in proxy) else "Low",
        None if proxy and all(row.get("verified") for row in proxy) else "Missing Data or unverified proxy rows",
    )


def compute_conservative_valuation(
    proxy_rows: list[dict],
    ttm_eps: float | None,
    valuation_eps: float | None,
    peer_median_pe: float | None,
) -> dict:
    anchor = historical_forward_multiple_anchor(proxy_rows, ttm_eps, valuation_eps)
    historical = anchor.get("median")
    lower = historical * 0.75 if historical else None
    upper = historical * 1.25 if historical else None
    peer_clamped = (
        min(max(peer_median_pe, lower), upper)
        if peer_median_pe and lower and upper
        else None
    )
    if historical and peer_clamped:
        fair_multiple = historical * 0.70 + peer_clamped * 0.30
        fair_method = "historical_70_peer_30"
    elif historical:
        fair_multiple = historical
        fair_method = "historical_only"
    else:
        fair_multiple = None
        fair_method = "blocked"
    stress_multiple = min(fair_multiple * 0.75, historical) if fair_multiple and historical else None
    entry_multiple = fair_multiple * 0.85 if fair_multiple else None
    upper_multiple = fair_multiple * 1.15 if fair_multiple else None
    warning = None
    if historical is None:
        warning = "Missing Data: 2Y/3Y point-in-time normalized anchor 不可用，Conservative Valuation 不得輸出。"
    elif anchor.get("two_year") is None or anchor.get("three_year") is None:
        warning = "只有一個歷史窗口可用，Historical Conservative Anchor 信心下降。"
    return {
        **anchor,
        "historical_conservative_anchor": historical,
        "peer_clamp_lower": lower,
        "peer_clamp_upper": upper,
        "peer_clamped_forward_pe": peer_clamped,
        "conservative_fair_multiple": fair_multiple,
        "stress_multiple": stress_multiple,
        "entry_multiple": entry_multiple,
        "upper_multiple": upper_multiple,
        "conservative_eps": ttm_eps,
        "conservative_fair_price": ttm_eps * fair_multiple if ttm_eps and fair_multiple else None,
        "stress_price": ttm_eps * stress_multiple if ttm_eps and stress_multiple else None,
        "entry_price": ttm_eps * entry_multiple if ttm_eps and entry_multiple else None,
        "upper_price": ttm_eps * upper_multiple if ttm_eps and upper_multiple else None,
        "fair_method": fair_method,
        "formula": "Conservative Fair = TTM EPS × (Historical trailing P/E anchor ×70% + peer-clamped trailing P/E ×30%)",
        "source": "2Y/3Y point-in-time trailing P/E P50, TTM EPS, peer trailing P/E median",
        "confidence": "Medium-High" if not warning else "Medium",
        "warning": warning,
    }


def compute_peer_sanity(peer_rows: list[dict], conservative: dict, valuation_metric: str = "P/E") -> dict:
    key = "ps" if valuation_metric == "P/S" else "pe"
    values = sorted(row.get(key) for row in peer_rows[1:] if row.get(key) and row.get(key) > 0)
    dispersion = values[-1] / values[0] if len(values) >= 2 else None
    collective_derating = False
    quality = "low" if dispersion and dispersion > 2.5 else "medium" if values else "Missing Data"
    warning = "Peer dispersion >2.5；E score max = 1，peer valuation quality = low。" if quality == "low" else None
    return {
        "metric": valuation_metric,
        "count": len(values),
        "median": median(values),
        "dispersion_ratio": dispersion,
        "quality": quality,
        "collective_derating": collective_derating,
        "e_score_cap": 1 if quality == "low" else 2,
        "q_cap": 0.50 if collective_derating else None,
        "formula": f"Peer Dispersion Ratio = max(peer {valuation_metric}) / min(peer {valuation_metric})",
        "source": "peer valuation table",
        "confidence": "Medium" if values else "Low",
        "warning": warning,
        "peer_clamp": {
            "lower": conservative.get("peer_clamp_lower"),
            "upper": conservative.get("peer_clamp_upper"),
            "clamped": conservative.get("peer_clamped_forward_pe"),
        },
    }


def apply_conservative_sanity_cap(item: dict, conservative: dict) -> dict:
    """Prevent high forward-implied EPS mismatches from turning rich stocks into false deep value."""
    if item.get("valuation_metric") != "P/E":
        return conservative
    current_pe = item.get("pe")
    ttm_eps = item.get("eps_ttm")
    forward_eps = item.get("valuation_eps")
    fy1_eps = item.get("fy1_consensus_eps")
    fair_multiple = conservative.get("conservative_fair_multiple")
    if not all(value is not None and value > 0 for value in [current_pe, ttm_eps, forward_eps, fair_multiple]):
        return conservative
    fy1_gap = abs(forward_eps / fy1_eps - 1) if fy1_eps and fy1_eps > 0 else None
    cap_needed = (
        fy1_gap is not None
        and fy1_gap > 0.30
        and current_pe > 40
        and conservative.get("conservative_fair_price") is not None
        and item.get("close") is not None
        and conservative["conservative_fair_price"] > item["close"]
    )
    if not cap_needed:
        return conservative
    capped_multiple = min(fair_multiple, current_pe * 0.85)
    if capped_multiple >= fair_multiple:
        return conservative
    updated = dict(conservative)
    updated.update(
        conservative_fair_multiple=capped_multiple,
        stress_multiple=capped_multiple * 0.75,
        entry_multiple=capped_multiple * 0.85,
        upper_multiple=capped_multiple * 1.15,
        conservative_fair_price=ttm_eps * capped_multiple,
        stress_price=ttm_eps * capped_multiple * 0.75,
        entry_price=ttm_eps * capped_multiple * 0.85,
        upper_price=ttm_eps * capped_multiple * 1.15,
        fair_method=f"{conservative.get('fair_method')}_sanity_capped",
    )
    cap_note = (
        f"Conservative P/E sanity cap applied: implied forward EPS / FY1 consensus gap {fy1_gap:.1%} "
        f"and trailing P/E {current_pe:.1f}x >40x；cap = current trailing P/E ×85%."
    )
    updated["warning"] = "；".join([text for text in [conservative.get("warning"), cap_note] if text])
    updated["formula"] = conservative.get("formula") + "; sanity cap = current trailing P/E ×85% when implied-vs-FY1 gap >30%"
    return updated


def compute_growth_pass_through(item: dict, conservative: dict) -> dict:
    proxy_rows = item.get("proxy") or []
    valuation_eps = item.get("valuation_eps")
    current_price = item.get("close")
    three_month = next((row.get("p50") for row in proxy_rows if row.get("label") == "3M"), None)
    six_month = next((row.get("p50") for row in proxy_rows if row.get("label") == "6M"), None)
    one_year = next((row.get("p50") for row in proxy_rows if row.get("label") == "1Y"), None)
    two_year = next((row.get("p50") for row in proxy_rows if row.get("label") == "2Y"), None)
    three_year = next((row.get("p50") for row in proxy_rows if row.get("label") == "3Y"), None)
    values = [value for value in [two_year, three_year] if value is not None and value > 0]
    fallback_used = False
    if not values:
        values = [value for value in [six_month, one_year] if value is not None and value > 0]
        fallback_used = bool(values)
    internal_growth_multiple = statistics.median(values) if values else None
    recent_rerating_change = one_year / internal_growth_multiple - 1 if one_year and internal_growth_multiple else None
    if recent_rerating_change is None:
        recent_rerating_status = "Insufficient data"
    elif recent_rerating_change < -.15:
        recent_rerating_status = "De-rating"
    elif recent_rerating_change < .15:
        recent_rerating_status = "Normal regime"
    elif recent_rerating_change < .30:
        recent_rerating_status = "Rerating"
    else:
        recent_rerating_status = "Strong rerating / potentially crowded"
    short_crowding_change = three_month / six_month - 1 if three_month and six_month else None
    if short_crowding_change is None:
        short_crowding_status = "Insufficient data"
    elif short_crowding_change > .15:
        short_crowding_status = "Rerating accelerating / crowded"
    elif short_crowding_change < -.15:
        short_crowding_status = "Rerating cooling / de-rating"
    else:
        short_crowding_status = "Short-term valuation stable"
    ttm_eps = item.get("eps_ttm")
    conservative_fair = conservative.get("conservative_fair_price")
    if conservative_fair is None and item.get("valuation_metric") == "P/S":
        conservative_fair = item.get("fair")
    full_growth_anchor = (
        valuation_eps * internal_growth_multiple
        if valuation_eps and internal_growth_multiple
        else None
    )
    growth_gap = (
        full_growth_anchor - conservative_fair
        if full_growth_anchor is not None and conservative_fair is not None
        else None
    )
    q_levels = [0.25, 0.35, 0.50, 0.65, 0.75]
    q_fair = {
        q: conservative_fair + q * growth_gap
        for q in q_levels
        if conservative_fair is not None and growth_gap is not None
    }
    market_implied_q = (
        (current_price - conservative_fair) / growth_gap
        if current_price is not None and conservative_fair is not None and growth_gap and growth_gap > 0
        else None
    )
    warning = None
    if internal_growth_multiple is None:
        warning = "Missing Data: 2Y/3Y point-in-time P50 不可用，Growth Pass-through 不得輸出。"
    elif growth_gap is not None and growth_gap <= 0:
        warning = "Growth Gap <= 0；Market-implied q = N/A。"
    elif fallback_used:
        warning = "2Y/3Y 不足，暫以 6M/1Y fallback；Growth Pass-through 信心下降。"
    extra_warnings = [text for text in [warning] if text]
    return {
        "three_month_ttm_pe_proxy_p50": three_month,
        "six_month_ttm_pe_proxy_p50": six_month,
        "one_year_ttm_pe_proxy_p50": one_year,
        "two_year_ttm_pe_proxy_p50": two_year,
        "three_year_ttm_pe_proxy_p50": three_year,
        "internal_growth_multiple": internal_growth_multiple,
        "recent_rerating_change": recent_rerating_change,
        "recent_rerating_status": recent_rerating_status,
        "short_crowding_change": short_crowding_change,
        "short_crowding_status": short_crowding_status,
        "full_growth_anchor_price": full_growth_anchor,
        "growth_gap": growth_gap,
        "q_fair": q_fair,
        "market_implied_q": market_implied_q,
        "formula": "Conservative Fair = TTM EPS × Conservative P/E; Forward Growth Anchor = implied forward EPS × Normalized Anchor; Growth Fair = Conservative Fair + q × Growth Gap",
        "source": "Point-in-time trailing P/E P50, TTM EPS, implied forward EPS, conservative fair",
        "confidence": "Medium" if not warning else "Low",
        "warning": "；".join(extra_warnings) if extra_warnings else None,
    }


def evidence_is_fresh(evidence: dict, max_days: int = 180) -> bool:
    evidence_date = parse_date(evidence.get("date"))
    reference_dt = evidence_reference_date()
    return bool(evidence_date and evidence_date <= reference_dt and (reference_dt - evidence_date).days <= max_days)


def evidence_reference_date() -> date:
    basis_dt = datetime.strptime(BASIS_DATE, "%Y-%m-%d").date()
    run_dt = parse_date(RUN_DATE) or basis_dt
    return max(basis_dt, run_dt)


def select_fes_evidence(item: dict) -> list[dict]:
    rows = []
    for row in item.get("rerating_evidence", []):
        if not row.get("verified") or not row.get("source_url") or not row.get("date") or not evidence_is_fresh(row):
            continue
        rows.append(row)
    priority = {
        "forward_eps_revision": 0,
        "revenue_acceleration": 0,
        "backlog_rpo_orders": 1,
        "customer_capex_demand": 1,
        "capacity_supply_expansion": 1,
        "product_adoption": 1,
        "margin_improvement": 2,
        "fcf_improvement": 2,
        "business_model_upgrade": 2,
    }
    rows.sort(key=lambda row: (priority.get(row.get("type"), 9), row.get("date") or ""))
    selected = []
    used_buckets = set()
    for row in rows:
        bucket = priority.get(row.get("type"), 9)
        if bucket in used_buckets and len(selected) >= 3:
            continue
        selected.append(row)
        used_buckets.add(bucket)
        if len(selected) == 3:
            break
    return selected


def score_fes_lite(item: dict, growth: dict, peer_sanity: dict) -> dict:
    evidence = select_fes_evidence(item)
    evidence_types = {row.get("type") for row in evidence if row.get("direction", "positive") == "positive"}
    negative_types = {row.get("type") for row in evidence if row.get("direction") == "negative"}

    a = 2 if "forward_eps_revision" in evidence_types else 1 if any(t in evidence_types for t in {"revenue_acceleration", "margin_improvement"}) else 0
    b = 2 if any(t in evidence_types for t in {"backlog_rpo_orders", "customer_capex_demand", "capacity_supply_expansion"}) else 1 if "product_adoption" in evidence_types else 0
    c = 2 if "revenue_acceleration" in evidence_types else 1 if b > 0 and item.get("revenue_ttm") is not None else 0
    d = 2 if any(t in evidence_types for t in {"margin_improvement", "fcf_improvement"}) else 1 if item.get("Operating Margin") not in {None, "n/a"} or item.get("FCF Margin") not in {None, "n/a"} else 0

    q50 = (growth.get("q_fair") or {}).get(0.50)
    q75 = (growth.get("q_fair") or {}).get(0.75)
    price = item.get("close")
    if price is not None and q75 is not None and price > q75:
        e = 0
    elif peer_sanity.get("collective_derating"):
        e = 0
    elif price is not None and q50 is not None and price < q50 and peer_sanity.get("quality") != "low":
        e = 2
    else:
        e = 1 if q50 is not None else 0
    e = min(e, peer_sanity.get("e_score_cap", 2))

    total = a + b + c + d + e
    if total <= 2:
        q_from_fes = 0.0
    elif total <= 4:
        q_from_fes = 0.25
    elif total <= 6:
        q_from_fes = 0.50
    elif total <= 8:
        q_from_fes = 0.65
    else:
        q_from_fes = 0.75
    caps = []
    if item.get("eps_bridge", {}).get("implied_eps_only") and not has_direct_forward_eps(item):
        caps.append(("只有 implied EPS，沒有直接 consensus EPS", 0.65))
    if c == 0:
        caps.append(("C = 0，沒有 revenue conversion 證據", 0.50))
    if d == 0:
        caps.append(("D = 0，margin / FCF 轉弱或無改善", 0.50))
    if peer_sanity.get("collective_derating"):
        caps.append(("同業集體 de-rating", 0.50))
    if "forward_eps_revision" in negative_types:
        caps.append(("EPS / guidance 下修", 0.25))
    q_final = apply_q_caps(q_from_fes, caps)

    def evidence_text(types: set[str], fallback: str = "缺 180 天內直接 evidence") -> tuple[str, str | None]:
        row = next((row for row in evidence if row.get("type") in types), None)
        if row:
            return str(row.get("description") or "evidence available"), row.get("source_url")
        return fallback, None

    a_ev, a_url = evidence_text({"forward_eps_revision", "revenue_acceleration", "margin_improvement"})
    b_ev, b_url = evidence_text({"backlog_rpo_orders", "customer_capex_demand", "capacity_supply_expansion", "product_adoption"})
    c_ev, c_url = evidence_text({"revenue_acceleration"}, f"TTM revenue {'available' if item.get('revenue_ttm') is not None else 'missing'}；B={b}/2")
    d_ev, d_url = evidence_text({"margin_improvement", "fcf_improvement"}, f"OM {item.get('Operating Margin') or 'N/A'}；FCF margin {item.get('FCF Margin') or 'N/A'}")
    q50 = (growth.get("q_fair") or {}).get(0.50)
    q75 = (growth.get("q_fair") or {}).get(0.75)
    e_ev = (
        f"price {money(item.get('close'))}; q50 {money(q50)}; q75 {money(q75)}; peer quality {peer_sanity.get('quality')}; E cap {peer_sanity.get('e_score_cap')}"
    )
    module_details = [
        {
            "module": "A. EPS / guidance",
            "score": a,
            "standard": "2=EPS/guidance 上修；1=營收或 margin evidence 間接支持；0=缺直接支持",
            "evidence": a_ev,
            "source_url": a_url,
        },
        {
            "module": "B. Orders / backlog / demand",
            "score": b,
            "standard": "2=orders/backlog/capacity/customer capex；1=product adoption；0=缺需求證據",
            "evidence": b_ev,
            "source_url": b_url,
        },
        {
            "module": "C. Revenue conversion",
            "score": c,
            "standard": "2=營收加速；1=需求證據且 TTM revenue 可驗證；0=尚未轉營收",
            "evidence": c_ev,
            "source_url": c_url,
        },
        {
            "module": "D. Margin / FCF",
            "score": d,
            "standard": "2=margin 或 FCF 明確改善；1=margin/FCF snapshot 可用；0=缺品質證據",
            "evidence": d_ev,
            "source_url": d_url,
        },
        {
            "module": "E. Valuation / peer sanity",
            "score": e,
            "standard": "2=現價低於 q50 且 peer quality 非 low；1=可計算但不便宜；0=高於 q75/同業 de-rating",
            "evidence": e_ev,
            "source_url": None,
        },
    ]
    return {
        "scores": {"A": a, "B": b, "C": c, "D": d, "E": e},
        "total": total,
        "q_from_fes": q_from_fes,
        "q_caps": caps,
        "q_final": q_final,
        "evidence": evidence,
        "module_details": module_details,
        "formula": "FES-Lite = A + B + C + D + E",
        "source": "latest earnings/guidance, orders/backlog/demand, margin/FCF/peer valuation evidence",
        "confidence": "Medium" if evidence else "Low",
        "warning": None if evidence else "Missing Data: 沒有 180 天內可驗證 FES-Lite evidence，不得猜分。",
    }


def evidence_pool(item: dict) -> list[dict]:
    return [
        row for row in item.get("rerating_evidence", [])
        if row.get("verified") and row.get("source_url") and row.get("date")
    ]


def first_evidence(item: dict, types: set[str]) -> dict | None:
    rows = [
        row for row in evidence_pool(item)
        if row.get("type") in types and evidence_is_fresh(row, 365)
    ]
    rows.sort(key=lambda row: row.get("date") or "", reverse=True)
    return rows[0] if rows else None


def has_direct_forward_eps(item: dict) -> bool:
    return any(
        item.get(field) is not None
        for field in ("fy1_consensus_eps", "fy2_consensus_eps", "ntm_consensus_eps", "company_guidance_eps")
    )


def source_age_days(source_date: str | None) -> int | None:
    parsed = parse_date(source_date)
    if parsed is None:
        return None
    return (evidence_reference_date() - parsed).days


def score_source_cap(score: float, max_score: float, row: dict | None) -> float:
    if score <= 0:
        return 0.0
    if not row or not row.get("source_url") or not row.get("date"):
        return 0.0
    days = source_age_days(row.get("date"))
    if days is None or days < 0 or days > 365:
        return 0.0
    capped = score
    if days > 180:
        capped = min(capped, max_score * 0.50)
    url = str(row.get("source_url") or "").lower()
    if any(token in url for token in ("blog", "forum", "reddit", "seekingalpha")):
        capped = min(capped, max_score * 0.30)
    return capped


def score_row(category: str, selected_option: str, score: float, max_score: float, row: dict | None, rationale: str) -> dict:
    return {
        "category": category,
        "selected_option": selected_option,
        "score": score,
        "max_score": max_score,
        "evidence_type": (row or {}).get("evidence_type") or ("Direct" if row and row.get("source_url") else "Missing"),
        "source_title": (row or {}).get("source_title") or (row or {}).get("source") or "Missing Data",
        "source_url": (row or {}).get("source_url"),
        "source_date": (row or {}).get("date"),
        "raw_text_excerpt": (row or {}).get("description") or "Missing Data",
        "rationale": rationale,
    }


def percent_from_text(text: str | None) -> float | None:
    if not text:
        return None
    matches = re.findall(r"([+-]?\d+(?:\.\d+)?)\s*%", text)
    if not matches:
        return None
    return max(abs(float(value)) for value in matches)


def debt_equity_value(item: dict) -> float | None:
    return num(item.get("Debt / Equity"))


def best_revenue_evidence_row(item: dict) -> dict | None:
    revenue_row = first_evidence(item, {"revenue_acceleration"})
    if revenue_row is not None:
        return revenue_row
    sec_rev = item.get("sec_revenue_metrics") or {}
    if sec_rev.get("latest_yoy") is None:
        return None
    acceleration_text = (
        f"；最近兩季 acceleration {sec_rev['acceleration']*100:+.1f}ppt"
        if sec_rev.get("acceleration") is not None else ""
    )
    return {
        "type": "revenue_acceleration",
        "source_title": "SEC Company Facts quarterly revenue",
        "source_url": sec_rev.get("source_url"),
        "date": sec_rev.get("filed") or sec_rev.get("period_end"),
        "description": f"最新季度 Revenue YoY {sec_rev['latest_yoy']*100:+.1f}%{acceleration_text}",
        "verified": True,
        "evidence_type": "Calculated",
    }


def direct_eps_evidence_row(item: dict) -> dict | None:
    row = first_evidence(item, {"forward_eps_revision", "eps_validation"})
    if row is not None:
        return row
    value = item.get("fy1_consensus_eps") or item.get("ntm_consensus_eps")
    if value is None:
        return None
    year = item.get("fy1_consensus_year") or item.get("ntm_consensus_year") or "FY/NTM"
    count = item.get("fy1_analyst_count") or item.get("ntm_analyst_count") or item.get("analyst_count") or "N/A"
    return {
        "type": "eps_validation",
        "source_title": "StockAnalysis forecast",
        "source_url": item.get("forward_eps_source_url") or item.get("valuation_snapshot_url"),
        "date": item.get("forward_eps_source_date") or BASIS_DATE,
        "description": f"{year} consensus EPS {value:.2f}; analysts {count}",
        "verified": True,
        "evidence_type": "Direct",
    }


def metric_snapshot_row(item: dict, metric_type: str) -> dict | None:
    if metric_type == "margin":
        values = [
            ("Gross margin", item.get("Gross Margin")),
            ("Operating margin", item.get("Operating Margin")),
            ("Profit margin", item.get("Profit Margin")),
        ]
        available = [f"{label} {value}" for label, value in values if value not in {None, "n/a", "N/A", ""}]
        if not available:
            return None
        return {
            "type": "margin_snapshot",
            "source_title": "StockAnalysis statistics",
            "source_url": item.get("url") or item.get("valuation_snapshot_url"),
            "date": BASIS_DATE,
            "description": "；".join(available),
            "verified": True,
            "evidence_type": "Proxy",
        }
    if metric_type == "fcf":
        values = [
            ("FCF margin", item.get("FCF Margin")),
            ("P/FCF", item.get("P/FCF Ratio")),
        ]
        available = [f"{label} {value}" for label, value in values if value not in {None, "n/a", "N/A", ""}]
        if not available:
            return None
        return {
            "type": "fcf_snapshot",
            "source_title": "StockAnalysis statistics",
            "source_url": item.get("url") or item.get("valuation_snapshot_url"),
            "date": BASIS_DATE,
            "description": "；".join(available),
            "verified": True,
            "evidence_type": "Proxy",
        }
    return None


def score_fets(item: dict) -> dict:
    rows = []

    revenue_row = best_revenue_evidence_row(item)
    revenue_pct = percent_from_text((revenue_row or {}).get("description"))
    rev_acceleration = (item.get("sec_revenue_metrics") or {}).get("acceleration")
    if revenue_row and revenue_pct and revenue_pct > 20 and (rev_acceleration is None or rev_acceleration > 0):
        rev_score, rev_option = 15, "季度營收 YoY >20%，且最近兩季未減速"
    elif revenue_row and revenue_pct and revenue_pct >= 10:
        rev_score, rev_option = 10, "季度營收 YoY 成長 10-20%"
    elif revenue_row and revenue_pct is not None and revenue_pct >= 0:
        rev_score, rev_option = 5, "季度營收 YoY 成長 0-10%"
    elif revenue_row:
        rev_score, rev_option = 0, "季度營收 YoY 下滑"
    else:
        rev_score, rev_option = 0, "季度 Revenue / guidance / bookings 資料均未取得"
    rev_score = score_source_cap(rev_score, 15, revenue_row)
    rows.append(score_row("Revenue validation", rev_option, rev_score, 15, revenue_row, "用最新營收/成長 evidence 驗證 forward EPS 分母。"))

    eps_row = direct_eps_evidence_row(item)
    eps_pct = percent_from_text((eps_row or {}).get("description"))
    eps_text = (eps_row or {}).get("description", "").lower()
    if eps_row and eps_pct and eps_pct > 25:
        eps_score, eps_option = 15, "EPS YoY 成長 >25% 或明確大幅上修"
    elif eps_row and (eps_pct and eps_pct >= 10 or any(word in eps_text for word in ("raised", "guidance", "outlook"))):
        eps_score, eps_option = 10, "EPS YoY 成長 10-25% 或 guidance 支持"
    elif eps_row:
        eps_score, eps_option = 5, "EPS YoY 成長 0-10% 或語氣正向"
    else:
        eps_score, eps_option = 0, "EPS YoY 下滑或無資料"
    eps_score = score_source_cap(eps_score, 15, eps_row)
    rows.append(score_row("EPS validation", eps_option, eps_score, 15, eps_row, "用 EPS/guidance/估計修正 evidence 驗證 forward EPS。"))

    margin_row = first_evidence(item, {"margin_improvement"}) or metric_snapshot_row(item, "margin")
    margin_text = (margin_row or {}).get("description", "").lower()
    if margin_row and "gross" in margin_text and ("operating" in margin_text or "op margin" in margin_text):
        margin_score, margin_option = 12, "gross + operating margin 同時改善"
    elif margin_row and ("operating" in margin_text or "op margin" in margin_text):
        margin_score, margin_option = 8, "operating margin 改善"
    elif margin_row:
        margin_score, margin_option = (3, "margin snapshot 可用，但缺 YoY/QoQ expansion evidence") if margin_row.get("evidence_type") == "Proxy" else (5, "gross margin 改善")
    else:
        margin_score, margin_option = 0, "gross / operating margin 皆未改善"
    margin_score = score_source_cap(margin_score, 12, margin_row)
    rows.append(score_row("Margin validation", margin_option, margin_score, 12, margin_row, "確認成長是否進入毛利或營益率。"))

    fcf_row = first_evidence(item, {"fcf_improvement"}) or metric_snapshot_row(item, "fcf")
    fcf_text = (fcf_row or {}).get("description", "").lower()
    if fcf_row and "ocf" in fcf_text and "margin" in fcf_text:
        fcf_score, fcf_option = 10, "OCF > NI 且 FCF margin 明顯改善"
    elif fcf_row and "margin" in fcf_text:
        fcf_score, fcf_option = 8, "OCF > NI 或 FCF margin 改善"
    elif fcf_row:
        fcf_score, fcf_option = (3, "FCF snapshot 可用，但缺改善證據") if fcf_row.get("evidence_type") == "Proxy" else (5, "OCF 接近 NI 或 FCF 穩定改善")
    else:
        fcf_score, fcf_option = 0, "OCF < NI 或 FCF 惡化 / 無資料"
    fcf_score = score_source_cap(fcf_score, 10, fcf_row)
    rows.append(score_row("Cash-flow quality", fcf_option, fcf_score, 10, fcf_row, "確認 EPS 成長是否有現金流品質支撐。"))

    de = debt_equity_value(item)
    bs_row = {
        "source_title": "StockAnalysis statistics",
        "source_url": item.get("url") or item.get("valuation_snapshot_url"),
        "date": BASIS_DATE,
        "description": f"Debt/Equity {item.get('Debt / Equity')}",
    } if de is not None else None
    if de is None:
        bs_score, bs_option = 0, "淨負債上升 / leverage 惡化或無資料"
    elif de <= 0:
        bs_score, bs_option = 10, "淨現金或明確 deleveraging"
    elif de <= 0.5:
        bs_score, bs_option = 8, "淨負債下降 / deleveraging 或低槓桿"
    elif de <= 1.5:
        bs_score, bs_option = 5, "leverage 穩定"
    else:
        bs_score, bs_option = 0, "淨負債上升 / leverage 偏高"
    rows.append(score_row("Balance sheet risk", bs_option, bs_score, 10, bs_row, "以 Debt/Equity 作批次版資產負債表風險 proxy。"))

    if eps_row and any(word in eps_text for word in ("raised", "raise", "guidance", "outlook")):
        guide_score, guide_option = 8, "guidance 明確上修"
    elif eps_row:
        guide_score, guide_option = 3, "口頭正向但無數字"
    else:
        guide_score, guide_option = 0, "無 guidance 或下修"
    guide_score = score_source_cap(guide_score, 8, eps_row)
    rows.append(score_row("Guidance / management tone", guide_option, guide_score, 8, eps_row, "公司 guidance 或管理層語氣是否支持 forward EPS。"))

    public_score = sum(row["score"] for row in rows)

    analyst_rows = []
    eps_type = item.get("valuation_eps_type") or ""
    analyst_count = item.get("analyst_count")
    direct_forward_eps = has_direct_forward_eps(item)
    eps_source_row = {
        "source_title": item.get("valuation_snapshot_source") or "valuation snapshot",
        "source_url": item.get("forward_eps_source_url") or item.get("valuation_snapshot_url"),
        "date": item.get("forward_eps_source_date") or BASIS_DATE,
        "description": item.get("fy1_consensus_eps_basis") or item.get("ntm_consensus_eps_basis") or item.get("valuation_eps_basis"),
    }
    if direct_forward_eps and analyst_count and analyst_count >= 5:
        source_score, source_option = 15, "公開 consensus EPS，analyst count >=5"
    elif direct_forward_eps and analyst_count and analyst_count >= 3:
        source_score, source_option = 10, ">=3 份 broker EPS"
    elif direct_forward_eps:
        source_score, source_option = 5, "1-2 份 broker EPS"
    else:
        source_score, source_option = 0, "無明確 forward EPS，只有 implied EPS"
    analyst_rows.append(score_row("Forward EPS source quality", source_option, source_score, 15, eps_source_row if source_score else None, "forward EPS 來源品質；implied EPS 不給 analyst bonus。"))

    if eps_row and evidence_is_fresh(eps_row, 90) and ("fy2" in eps_text and "fy1" in eps_text):
        revision_score, revision_option = 10, "近 90 天 FY1 + FY2 EPS 同時上修"
    elif eps_row and evidence_is_fresh(eps_row, 90):
        revision_score, revision_option = 7, "近 90 天 FY1 EPS 上修或 guidance 上修"
    elif eps_row:
        revision_score, revision_option = 3, "近 90 天持平或較舊正向 evidence"
    else:
        revision_score, revision_option = 0, "無資料 / 下修"
    revision_score = score_source_cap(revision_score, 10, eps_row)
    analyst_rows.append(score_row("EPS revision evidence", revision_option, revision_score, 10, eps_row, "估計修正是 forward EPS 信任度的 bonus，不是必要條件。"))

    reliability_row = eps_source_row if source_score else None
    if analyst_count and analyst_count >= 5 and source_score:
        reliability_score, reliability_option = 5, "consensus / 多券商估計接近"
    elif analyst_count and analyst_count >= 2 and source_score:
        reliability_score, reliability_option = 3, "多數來源方向一致"
    else:
        reliability_score, reliability_option = 0, "無 dispersion / 無法驗證"
    analyst_rows.append(score_row("Estimate reliability", reliability_option, reliability_score, 5, reliability_row, "批次版只在 analyst_count 可驗證時給分。"))

    analyst_bonus = sum(row["score"] for row in analyst_rows)
    total = public_score + analyst_bonus
    if total >= 80:
        trust_pct = 0.90
    elif total >= 65:
        trust_pct = 0.80
    elif total >= 50:
        trust_pct = 0.65
    elif total >= 35:
        trust_pct = 0.45
    else:
        trust_pct = 0.25

    all_rows = rows + analyst_rows
    evidence_completeness = sum(1 for row in all_rows if row.get("source_url") and row.get("source_date") and row.get("score", 0) > 0)
    confidence = "Low" if evidence_completeness < 4 else "Medium" if evidence_completeness < 7 else "Medium-High"
    return {
        "public_score": public_score,
        "analyst_bonus": analyst_bonus,
        "total": total,
        "trust_pct": trust_pct,
        "rows": all_rows,
        "evidence_completeness": evidence_completeness,
        "evidence_possible": len(all_rows),
        "confidence": confidence,
        "warning": "Evidence completeness < 4/7；FETS 不作決定性建議。" if evidence_completeness < 4 else None,
        "formula": "FETS = Public Fundamental Score + Analyst Evidence Bonus",
        "source": "structured evidence + valuation snapshot + statistics",
    }


def score_res(item: dict) -> dict:
    rows = []
    eps_row = direct_eps_evidence_row(item)
    revenue_row = best_revenue_evidence_row(item)
    margin_row = first_evidence(item, {"margin_improvement"}) or metric_snapshot_row(item, "margin")
    fcf_row = first_evidence(item, {"fcf_improvement"}) or metric_snapshot_row(item, "fcf")
    backlog_row = first_evidence(item, {"backlog_rpo_orders"})
    industry_row = first_evidence(item, {"customer_capex_demand", "product_adoption", "business_model_upgrade"})
    pricing_row = first_evidence(item, {"capacity_supply_expansion"})

    for category, row, max_score, options in [
        ("EPS acceleration", eps_row, 15, (0, 5, 10, 15)),
        ("Revenue acceleration", revenue_row, 15, (0, 5, 10, 15)),
    ]:
        text = (row or {}).get("description", "")
        pct_value = percent_from_text(text)
        if row and pct_value and pct_value > 20 and "qoq" in text.lower():
            score, option = options[3], f"{category.split()[0]} YoY >20% 且 QoQ 加速"
        elif row and pct_value and pct_value > 20:
            score, option = options[2], f"{category.split()[0]} YoY >20%"
        elif row:
            score, option = options[1], f"{category.split()[0]} YoY 成長但未加速"
        else:
            score, option = options[0], f"{category.split()[0]} 未加速 / 下滑"
        score = score_source_cap(score, max_score, row)
        rows.append(score_row(category, option, score, max_score, row, "Price > Forward fair 時用來判斷是否為 validated rerating。"))

    margin_text = (margin_row or {}).get("description", "").lower()
    if margin_row and "gross" in margin_text and ("operating" in margin_text or "op margin" in margin_text):
        score, option = 12, "gross + operating margin 同時改善"
    elif margin_row and ("operating" in margin_text or "op margin" in margin_text):
        score, option = 8, "operating margin 改善"
    elif margin_row:
        score, option = (2, "margin snapshot 可用，但缺 expansion evidence") if margin_row.get("evidence_type") == "Proxy" else (5, "gross margin 改善")
    else:
        score, option = 0, "margin 無改善"
    rows.append(score_row("Margin expansion", option, score_source_cap(score, 12, margin_row), 12, margin_row, "rerating 需要 margin 端確認。"))

    fcf_text = (fcf_row or {}).get("description", "").lower()
    if fcf_row and "ocf" in fcf_text and "margin" in fcf_text:
        score, option = 10, "FCF margin + OCF quality 同時改善"
    elif fcf_row and "margin" in fcf_text:
        score, option = 8, "FCF margin 改善"
    elif fcf_row:
        score, option = (2, "FCF snapshot 可用，但缺改善 evidence") if fcf_row.get("evidence_type") == "Proxy" else (5, "FCF 改善但仍弱")
    else:
        score, option = 0, "FCF 無改善"
    rows.append(score_row("FCF support", option, score_source_cap(score, 10, fcf_row), 10, fcf_row, "rerating 需要現金流支撐。"))

    de = debt_equity_value(item)
    bs_row = {
        "source_title": "StockAnalysis statistics",
        "source_url": item.get("url") or item.get("valuation_snapshot_url"),
        "date": BASIS_DATE,
        "description": f"Debt/Equity {item.get('Debt / Equity')}",
    } if de is not None else None
    if de is None or de > 1.5:
        score, option = 0, "leverage 惡化或 ROIC 下滑 / 無資料"
    elif de <= 0.5:
        score, option = 6, "leverage 改善或 ROIC 改善 proxy"
    else:
        score, option = 4, "leverage 穩定"
    rows.append(score_row("Balance sheet / ROIC support", option, score, 8, bs_row, "批次版用 Debt/Equity 作 ROIC/leverage proxy。"))

    eps_text = (eps_row or {}).get("description", "").lower()
    if eps_row and any(word in eps_text for word in ("raised", "raise", "guidance", "outlook")):
        score, option = 10, "guidance 明確上修"
    elif eps_row:
        score, option = 3, "管理層語氣正向但無數字"
    else:
        score, option = 0, "無 guidance 或下修"
    rows.append(score_row("Guidance confirmation", option, score_source_cap(score, 10, eps_row), 10, eps_row, "rerating 需要 guidance confirmation。"))

    if industry_row and backlog_row:
        score, option = 10, "同業 EPS / revenue / backlog 同步上修"
    elif industry_row:
        score, option = 7, "同業財報 / guidance 改善"
    else:
        score, option = 0, "只有單一公司股價上漲或無資料"
    rows.append(score_row("Industry confirmation", option, score_source_cap(score, 10, industry_row), 10, industry_row, "確認 rerating 是否為產業共同基本面。"))

    backlog_text = (backlog_row or {}).get("description", "").lower()
    if backlog_row and (percent_from_text(backlog_text) or 0) > 20:
        score, option = 10, "backlog / RPO / book-to-bill 成長 >20%"
    elif backlog_row:
        score, option = 7, "backlog / RPO / book-to-bill 成長"
    else:
        score, option = 0, "無資料"
    rows.append(score_row("Backlog / order visibility", option, score_source_cap(score, 10, backlog_row), 10, backlog_row, "訂單能見度是否支撐估值重估。"))

    if pricing_row and margin_row:
        score, option = 10, "供不應求 + 漲價 + margin 改善"
    elif pricing_row:
        score, option = 6, "交期拉長 / 產能滿載 / ASP 上升任一成立"
    else:
        score, option = 0, "無資料"
    rows.append(score_row("Pricing power / supply constraint", option, score_source_cap(score, 10, pricing_row), 10, pricing_row, "pricing power 是超過 Forward fair 後的 rerating bonus。"))

    total = sum(row["score"] for row in rows)
    if total >= 75:
        status = "Validated rerating"
    elif total >= 60:
        status = "Probable rerating"
    elif total >= 45:
        status = "Rerating watch"
    elif total >= 30:
        status = "Likely overheat"
    else:
        status = "Overheat / narrative-driven"
    evidence_completeness = sum(1 for row in rows if row.get("source_url") and row.get("source_date") and row.get("score", 0) > 0)
    return {
        "total": total,
        "status": status,
        "rows": rows,
        "evidence_completeness": evidence_completeness,
        "evidence_possible": len(rows),
        "confidence": "Low" if evidence_completeness < 4 else "Medium" if evidence_completeness < 7 else "Medium-High",
        "warning": "Evidence completeness < 4/7；RES 不作決定性建議。" if evidence_completeness < 4 else None,
        "formula": "RES = Confirmed Fundamental Rerating Score + Narrative / Industry Bonus",
        "source": "structured evidence + statistics",
    }


def compute_eps_year_clarity(item: dict) -> dict:
    rows = []
    if item.get("reported_eps_ttm") is not None and item.get("eps_ttm") != item.get("reported_eps_ttm"):
        ttm_type = "NORMALIZED_TTM_PROXY"
        ttm_note = f"reported TTM EPS {money(item.get('reported_eps_ttm'))}；proxy 排除一次性項目"
    else:
        ttm_type = "REPORTED_TTM"
        ttm_note = "latest trailing 12-month EPS"
    rows.append({
        "label": "TTM EPS",
        "eps_used": item.get("eps_ttm"),
        "eps_year": "TTM",
        "eps_type": ttm_type,
        "eps_source": item.get("eps_ttm_basis") or "valuation snapshot",
        "analyst_count": None,
        "pe_label": "Trailing P/E proxy denominator",
        "note": ttm_note,
    })
    rows.append({
        "label": "same-snapshot implied EPS",
        "eps_used": item.get("valuation_eps"),
        "eps_year": "NTM proxy",
        "eps_type": item.get("valuation_eps_type") or "IMPLIED_NTM_FROM_FORWARD_PE",
        "eps_source": item.get("valuation_eps_basis"),
        "analyst_count": item.get("analyst_count"),
        "pe_label": "Forward P/E",
        "note": "Current Price / Forward P/E；沒有直接 consensus 時 q/FETS 需降信心",
    })
    for label, eps_year, eps_type, value_field, year_field, analyst_field, basis_field in [
        ("FY1 consensus EPS", "FY1", "CONSENSUS_FY1", "fy1_consensus_eps", "fy1_consensus_year", "fy1_analyst_count", "fy1_consensus_eps_basis"),
        ("FY2 consensus EPS", "FY2", "CONSENSUS_FY2", "fy2_consensus_eps", "fy2_consensus_year", "fy2_analyst_count", "fy2_consensus_eps_basis"),
        ("NTM consensus EPS", "NTM", "CONSENSUS_NTM", "ntm_consensus_eps", "ntm_consensus_year", "ntm_analyst_count", "ntm_consensus_eps_basis"),
    ]:
        value = item.get(value_field)
        rows.append({
            "label": label,
            "eps_used": value,
            "eps_year": item.get(year_field) or eps_year,
            "eps_type": eps_type if value is not None else "Missing Data",
            "eps_source": item.get(basis_field) or "Missing Data",
            "analyst_count": item.get(analyst_field) or item.get("analyst_count"),
            "pe_label": "Direct consensus EPS" if value is not None else "N/A",
            "note": "揭露與 FETS 使用；不覆蓋 same-snapshot valuation EPS" if value is not None else "未取得直接 consensus；不得和 implied EPS 混用",
        })
    return {
        "rows": rows,
        "eps_used": item.get("valuation_eps"),
        "eps_year": "NTM proxy",
        "eps_type": item.get("valuation_eps_type") or "IMPLIED_NTM_FROM_FORWARD_PE",
        "eps_source": item.get("valuation_eps_basis"),
        "analyst_count": item.get("analyst_count"),
        "pe_label": "Forward P/E",
    }


def compute_forward_eps_layers(item: dict) -> dict:
    if item.get("valuation_blocked"):
        return {
            "historical_forward_pe_proxy": None,
            "historical_forward_pe_basis": "blocked valuation; no reliable same-snapshot valuation EPS",
            "conservative_fair": None,
            "old_model_fair": None,
            "trust_adjusted_eps": None,
            "trust_adjusted_fair": None,
            "forward_fair": None,
            "eps_revision_bull": None,
            "eps_rerating_bull": None,
            "revised_eps_assumption": None,
            "rerating_pe_assumption": None,
            "conservative_entry": None,
            "forward_entry": None,
            "stress_low": None,
            "stress_high": None,
            "price_zone": "Valuation incomplete / blocked",
            "entry_interpretation": item.get("valuation_block_reason") or "可靠 valuation EPS 未取得；不建立目標價",
            "warning": item.get("valuation_block_reason") or "Blocked valuation; no target prices generated.",
        }
    fets = item.get("fets") or score_fets(item)
    conservative = item.get("conservative_valuation") or {}
    growth = item.get("growth_pass_through") or {}
    ttm_eps = item.get("eps_ttm")
    forward_eps = item.get("valuation_eps")
    historical_trailing_pe = growth.get("internal_growth_multiple")
    historical_forward_pe = historical_trailing_pe
    conservative_fair = conservative.get("conservative_fair_price")
    old_model_fair = conservative_fair
    trust_eps = (
        ttm_eps + fets["trust_pct"] * (forward_eps - ttm_eps)
        if ttm_eps is not None and forward_eps is not None
        else None
    )
    forward_fair = forward_eps * historical_forward_pe if forward_eps and historical_forward_pe else None
    trust_fair = trust_eps * historical_forward_pe if trust_eps and historical_forward_pe else None
    revised_eps = forward_eps * 1.20 if forward_eps else None
    rerating_pe = historical_forward_pe * 1.05 if historical_forward_pe else None
    eps_revision_bull = revised_eps * historical_forward_pe if revised_eps and historical_forward_pe else None
    eps_rerating_bull = revised_eps * rerating_pe if revised_eps and rerating_pe else None
    conservative_entry = conservative_fair * 0.85 if conservative_fair else None
    forward_entry = forward_fair * 0.85 if forward_fair else None
    stress_low = conservative_fair * 0.76 if conservative_fair else None
    stress_high = conservative_fair * 0.78 if conservative_fair else None
    price = item.get("close")
    if price is None or conservative_fair is None:
        price_zone = "Missing Data"
        entry_interpretation = "資料不足"
    elif conservative_entry and price < conservative_entry:
        price_zone = "Deep value / conservative entry"
        entry_interpretation = "低於 conservative entry，仍需 thesis check"
    elif price < conservative_fair:
        price_zone = "Below conservative fair"
        entry_interpretation = "低於 conservative fair，若 thesis intact 可研究"
    elif trust_fair and price <= trust_fair:
        price_zone = "Reasonable / partial forward EPS priced"
        entry_interpretation = "需要 FETS 支撐，屬合理偏低至部分 forward EPS 定價"
    elif forward_entry and price <= forward_entry:
        price_zone = "Forward thesis entry zone"
        entry_interpretation = "只有 FETS 中高分時才可新買"
    elif forward_fair and price <= forward_fair:
        price_zone = "Forward thesis priced"
        entry_interpretation = "偏續抱，不建議追高"
    else:
        res = item.get("res") or {}
        status = res.get("status") or "RES required"
        price_zone = f"> Forward Growth Anchor: {status}"
        entry_interpretation = "超過 Forward Growth Anchor，必須用 RES 判斷 rerating 或 overheat"
    return {
        "historical_forward_pe_proxy": historical_forward_pe,
        "historical_forward_pe_basis": "median(2Y, 3Y point-in-time trailing P/E P50); true historical forward P/E unavailable",
        "conservative_fair": conservative_fair,
        "old_model_fair": old_model_fair,
        "trust_adjusted_eps": trust_eps,
        "trust_adjusted_fair": trust_fair,
        "forward_fair": forward_fair,
        "eps_revision_bull": eps_revision_bull,
        "eps_rerating_bull": eps_rerating_bull,
        "revised_eps_assumption": revised_eps,
        "rerating_pe_assumption": rerating_pe,
        "conservative_entry": conservative_entry,
        "forward_entry": forward_entry,
        "stress_low": stress_low,
        "stress_high": stress_high,
        "price_zone": price_zone,
        "entry_interpretation": entry_interpretation,
        "warning": "True historical forward P/E unavailable；Forward Growth Anchor 使用 2Y/3Y point-in-time trailing P/E 正常化錨，屬 growth scenario。",
    }


def compute_price_nodes(item: dict) -> dict:
    if item.get("valuation_blocked"):
        return {
            "bear_stress": None,
            "value_entry": None,
            "conservative_fair": None,
            "selected_growth_fair": None,
            "trust_adjusted_fair": None,
            "forward_growth_anchor": None,
            "current_price": item.get("close"),
            "q_final": None,
            "market_implied_q": None,
            "price_zone": "Valuation incomplete / blocked",
        }
    conservative = item.get("conservative_valuation") or {}
    growth = item.get("growth_pass_through") or {}
    layers = item.get("forward_eps_layers") or {}
    fes = item.get("fes_lite") or {}
    q_final = fes.get("q_final")
    conservative_fair = conservative.get("conservative_fair_price")
    ps_fallback = conservative_fair is None and item.get("valuation_metric") == "P/S"
    if ps_fallback:
        conservative_fair = item.get("fair")
    growth_gap = growth.get("growth_gap")
    selected_growth_fair = (
        conservative_fair + q_final * growth_gap
        if conservative_fair is not None and q_final is not None and growth_gap is not None
        else None
    )
    nodes = {
        "bear_stress": item.get("stress") if ps_fallback else (conservative_fair * 0.75 if conservative_fair is not None else None),
        "value_entry": item.get("entry") if ps_fallback else (conservative_fair * 0.85 if conservative_fair is not None else None),
        "conservative_fair": conservative_fair,
        "selected_growth_fair": selected_growth_fair,
        "trust_adjusted_fair": layers.get("trust_adjusted_fair"),
        "forward_growth_anchor": layers.get("forward_fair") or item.get("upper"),
        "current_price": item.get("close"),
        "q_final": q_final,
        "market_implied_q": growth.get("market_implied_q"),
        "price_zone": layers.get("price_zone"),
    }
    return nodes


def apply_q_caps(q_from_fes: float, caps: list[tuple[str, float]]) -> float:
    applicable = [cap for _reason, cap in caps]
    return min([q_from_fes] + applicable) if applicable else q_from_fes


def compute_integrated_price_ladder(item: dict, conservative: dict, growth: dict) -> dict:
    nodes = item.get("price_nodes") or compute_price_nodes(item)
    fes = item.get("fes_lite") or {}
    layers = item.get("forward_eps_layers") or {}
    q_final = nodes.get("q_final")
    selected_definition = (
        f"FES-Lite {fmt(fes.get('total'), 0)}/10 對應 q={int(q_final * 100)}%"
        if q_final is not None
        else "FES-Lite / q 資料不足"
    )
    rows = [
        ("Bear Stress", nodes.get("bear_stress"), "Conservative Fair × 75%", "thesis 受壓時的風險檢查", "跌破需檢查 price stop 與 thesis stop"),
        ("Value Entry", nodes.get("value_entry"), "Conservative Fair × 85%", "不依賴 Growth 的價值型研究區", "thesis intact 才可分批研究"),
        ("Conservative Fair", nodes.get("conservative_fair"), "TTM EPS × Conservative P/E", "防守型合理價", "低於此線才是價值型研究區"),
        (
            f"Selected Growth Fair q={int(q_final * 100)}%" if q_final is not None else "Selected Growth Fair",
            nodes.get("selected_growth_fair"),
            f"Conservative Fair + {int(q_final * 100)}% × Growth Gap" if q_final is not None else "FES-Lite q × Growth Gap",
            selected_definition,
            "唯一進入操作階梯的 Growth Fair；其他 q 僅作 7.2B 敏感度參考",
        ),
        ("Trust-adjusted Fair", nodes.get("trust_adjusted_fair"), "Trust-adjusted EPS × Internal Growth Multiple", "FETS 折扣 forward EPS 後的合理價", "用來判斷 forward thesis 已反映多少"),
        ("Forward Growth Anchor", nodes.get("forward_growth_anchor"), "Forward implied EPS × Internal Growth Multiple", "EPS 成長完全被承認的上限情境", "不是 base fair；超過後看 RES"),
        ("Current Price", nodes.get("current_price"), "basis-date official close", f"隱含 q 約 {pct((growth.get('market_implied_q') or 0) * 100) if growth.get('market_implied_q') is not None else 'N/A'}", "用於判斷市場已反映多少 growth gap"),
    ]
    return {
        "rows": rows,
        "market_implied_q": growth.get("market_implied_q"),
        "formula": "Integrated Price Ladder combines Conservative Fair and Growth Pass-through nodes",
        "source": "conservative valuation + growth pass-through valuation",
        "confidence": "Medium" if growth.get("growth_gap") is not None else "Low",
        "warning": growth.get("warning"),
    }


def assign_action(item: dict) -> dict:
    price = item.get("close")
    nodes = item.get("price_nodes") or compute_price_nodes(item)
    growth = item.get("growth_pass_through") or {}
    fes = item.get("fes_lite") or {}
    q_fair = growth.get("q_fair") or {}
    q25 = q_fair.get(0.25)
    q50 = q_fair.get(0.50)
    q75 = q_fair.get(0.75)
    fair = nodes.get("conservative_fair")
    score = fes.get("total") or 0
    sanity_capped = "sanity cap applied" in str((item.get("conservative_valuation") or {}).get("warning") or "")
    if price is None or fair is None:
        new_buy = "資料不足"
    elif sanity_capped and price > fair:
        new_buy = "偏貴 / 不追"
    elif price < fair:
        new_buy = "可研究 / 分批"
    elif q25 and price <= q25 and score >= 5:
        new_buy = "可小量"
    elif q50 and price <= q50 and score >= 6:
        new_buy = "續抱為主，小量加倉需理由"
    elif q75 and price <= q75 and score >= 8:
        new_buy = "不追，僅續抱"
    else:
        new_buy = "不新買 / 停利檢查"
    hold = "可續抱" if score >= 5 and (q75 is None or price is None or price <= q75) else "需減碼檢查"
    stop_line = (
        f"第一減碼線 {money(q25)}；硬停損線 {money(fair)}"
        if q25 and q50 and price and price > q25 and price <= q50
        else f"第一減碼線 {money(nodes.get('value_entry'))}；硬停損線 {money(nodes.get('bear_stress'))}"
    )
    thesis_stop = "EPS/guidance 下修、orders/backlog 轉弱、revenue conversion 不成立、margin/FCF 轉弱、同業集體 de-rating 或 EPS thesis broken。"
    return {
        "new_buy": new_buy,
        "hold": hold,
        "stop_line": stop_line,
        "thesis_stop": thesis_stop,
        "formula": "Price zone + FES-Lite + q_final + thesis evidence",
        "source": "Integrated Price Ladder and FES-Lite",
        "confidence": fes.get("confidence") or "Medium",
        "warning": fes.get("warning"),
    }


def historical_sales_multiple_anchor(ps_proxy_rows: list[dict]) -> dict:
    """Use the same 2Y/3Y anchor pattern for current-sales P/S proxy."""
    values_by_label = {
        row.get("label"): row.get("p50")
        for row in ps_proxy_rows
        if row.get("label") in {"2Y", "3Y"} and row.get("p50") is not None
    }
    values = [values_by_label.get("2Y"), values_by_label.get("3Y")]
    values = [value for value in values if value is not None and value > 0]
    return {
        "two_year": values_by_label.get("2Y"),
        "three_year": values_by_label.get("3Y"),
        "median": statistics.median(values) if values else None,
    }


def derive_forward_band_multiples(
    historical_anchor: dict,
    peer_multiple: float | None,
    current_multiple: float | None,
) -> dict:
    """Derive every band multiple from observable, same-basis anchors."""
    historical = historical_anchor.get("median")
    peer_capped = None
    if historical and historical > 0 and peer_multiple and peer_multiple > 0:
        peer_capped = min(max(peer_multiple, historical * 0.75), historical * 1.25)
        fair = historical * 0.70 + peer_capped * 0.30
    elif historical and historical > 0:
        fair = historical
    elif peer_multiple and peer_multiple > 0:
        fair = peer_multiple
    elif current_multiple and current_multiple > 0:
        # Last-resort path for loss-making names with no valid historical P/E
        # and no sufficiently comparable peer. This is explicitly not an
        # independent fair-value conclusion.
        fair = current_multiple
    else:
        return {"stress": None, "entry": None, "fair": None, "upper": None}
    entry = fair * 0.85
    stress = min(fair * 0.75, historical) if historical else fair * 0.75
    upper = fair * 1.15
    return {
        "stress": stress,
        "entry": entry,
        "fair": fair,
        "upper": upper,
        "peer": peer_multiple,
        "peer_capped": peer_capped,
        "current": current_multiple,
        "historical": historical,
        "fair_method": (
            "historical_70_peer_30"
            if historical and peer_capped
            else "historical_only"
            if historical
            else "peer_only"
            if peer_multiple
            else "current_multiple_fallback"
        ),
    }


def relative_gap(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return abs(left - right) / max(abs(right), 0.01)


def valuation_audit(item: dict, snapshot: dict) -> dict:
    """Create a reproducible EPS, P/E, P/S, and forward-valuation audit."""
    close = num(item.get("close"))
    stats_eps = num(snapshot.get("ttm_eps"))
    financial_eps = num(item.get("eps_diluted_ttm_financials"))
    financial_currency = item.get("financial_currency")
    quote_currency = "USD"
    effective_eps = (
        stats_eps
        if stats_eps is not None
        else financial_eps
        if financial_eps is not None and financial_currency in {None, quote_currency}
        else None
    )
    pe_source = num(snapshot.get("pe"))
    pe_calc = close / effective_eps if close and effective_eps and effective_eps > 0 else None
    pe_gap = relative_gap(pe_calc, pe_source)

    market_cap = scaled_num(item.get("Market Cap"))
    revenue_display = scaled_num(item.get("Revenue (TTM Display Currency)"))
    ps_source = num(item.get("PS Ratio"))
    ps_calc = market_cap / revenue_display if market_cap and revenue_display else None
    ps_gap = relative_gap(ps_calc, ps_source)

    eps_gap = relative_gap(financial_eps, stats_eps)
    explicit_conversion = bool(
        snapshot.get("adr_common_share_ratio")
        or snapshot.get("implicit_twd_per_usd")
        or snapshot.get("eps_conversion_basis")
    )
    if stats_eps is None and financial_eps is None:
        eps_status = "statistics / financials EPS 均未取得"
    elif stats_eps is None:
        eps_status = f"statistics EPS 未取得；financials EPS={financial_eps:.4f}"
    elif financial_eps is None:
        eps_status = "financials EPS 未取得"
    elif financial_currency in {None, quote_currency}:
        eps_status = (
            "通過"
            if eps_gap is not None and eps_gap <= 0.03
            else f"不一致（financials {financial_eps:.4f} vs statistics {fmt(stats_eps,4)}）"
        )
    elif explicit_conversion:
        eps_status = f"跨幣別／ADR，已使用明示換算（{financial_currency}→{quote_currency}）"
    else:
        eps_status = f"跨幣別／ADR 待換算（{financial_currency}→{quote_currency}）"

    valuation_eps, valuation_basis, valuation_eps_type, valuation_eps_confidence = select_valuation_eps(snapshot)
    fpe = num(snapshot.get("forward_pe"))
    fpe_calc = close / valuation_eps if close and valuation_eps and valuation_eps > 0 else None
    fpe_gap = relative_gap(fpe_calc, fpe)

    return {
        "stats_eps_ttm": stats_eps,
        "financials_eps_ttm": financial_eps,
        "financial_currency": financial_currency,
        "eps_audit_status": eps_status,
        "eps_audit_gap": eps_gap,
        "pe_source": pe_source,
        "pe_calculated": pe_calc,
        "pe_gap": pe_gap,
        "pe_status": (
            "通過" if pe_gap is not None and pe_gap <= 0.03
            else "N/M（TTM EPS 為負，Trailing P/E 無經濟意義）"
            if effective_eps is not None and effective_eps <= 0
            else "待補" if pe_gap is None
            else "來源 P/E 與 close/EPS 不一致"
        ),
        "market_cap": market_cap,
        "revenue_display_currency": revenue_display,
        "ps_source": ps_source,
        "ps_calculated": ps_calc,
        "ps_gap": ps_gap,
        "ps_status": (
            "通過" if ps_gap is not None and ps_gap <= 0.03
            else "待補" if ps_gap is None
            else "來源 P/S 與 market cap/revenue 不一致"
        ),
        "valuation_eps_audit": valuation_eps,
        "valuation_eps_basis_audit": valuation_basis,
        "valuation_eps_type_audit": valuation_eps_type,
        "valuation_eps_confidence_audit": valuation_eps_confidence,
        "forward_pe_source": fpe,
        "forward_pe_calculated": fpe_calc,
        "forward_pe_gap": fpe_gap,
        "forward_pe_status": (
            "通過" if fpe_gap is not None and fpe_gap <= 0.01
            else "待補" if fpe_gap is None
            else "Forward P/E 與 price/valuation EPS 不一致"
        ),
    }


def build_data() -> tuple[list[dict], dict[str, dict], dict[str, list[dict]]]:
    valuation_snapshot = load_valuation_snapshot()
    forward_eps_evidence = load_forward_eps_evidence()
    point_in_time_eps_cache = (
        json.loads(POINT_IN_TIME_EPS_CACHE.read_text(encoding="utf-8"))
        if POINT_IN_TIME_EPS_CACHE.exists()
        else {"stocks": {}}
    )
    all_needed = set(TICKERS)
    for config in CONFIG.values():
        all_needed.update(config["peers"])

    print("fetch stats", len(all_needed))
    stats_map = {}
    for ticker in sorted(all_needed):
        try:
            stats_map[ticker] = stats(ticker)
            print("stats ok", ticker)
        except Exception as exc:  # noqa: BLE001 - report generation should continue with gaps
            print("stats err", ticker, exc)
            stats_map[ticker] = {
                "ticker": ticker,
                "error": str(exc),
                "url": f"https://stockanalysis.com/stocks/{ticker.lower()}/statistics/",
            }
        time.sleep(0.08)

    history_map = {}
    for ticker in TICKERS:
        try:
            history_map[ticker] = history(ticker)
            print("hist ok", ticker, len(history_map[ticker]), history_map[ticker][0]["t"] if history_map[ticker] else "no rows")
        except Exception as exc:  # noqa: BLE001
            print("hist err", ticker, exc)
            history_map[ticker] = []
        time.sleep(0.08)

    financials_map = {}
    for ticker in TICKERS:
        try:
            financials_map[ticker] = financials_snapshot(ticker)
            print("financials ok", ticker, financials_map[ticker].get("financial_last_date"))
        except Exception as exc:  # noqa: BLE001
            print("financials err", ticker, exc)
            financials_map[ticker] = {
                "financials_url": f"https://stockanalysis.com/stocks/{ticker.lower()}/financials/",
                "financials_error": str(exc),
            }
        time.sleep(0.08)

    critical_stats_failures = [
        ticker for ticker in TICKERS if stats_map.get(ticker, {}).get("error")
    ]
    critical_history_failures = [
        ticker for ticker in TICKERS if not history_map.get(ticker)
    ]
    if critical_stats_failures or critical_history_failures:
        raise RuntimeError(
            "critical data fetch failed; refusing to write report. "
            f"stats={critical_stats_failures}; history={critical_history_failures}"
        )

    data = []
    for ticker in TICKERS:
        source = stats_map[ticker]
        config = CONFIG[ticker]
        item = dict(source)
        item.update(config)
        item.update(financials_map[ticker])
        forward_overlay = (forward_eps_evidence.get("tickers") or {}).get(ticker) or {}
        overlay_eps = forward_overlay.get("eps") or {}
        overlay_evidence = forward_overlay.get("evidence") or []
        raw_rerating_evidence = list(item.get("rerating_evidence", [])) + list(overlay_evidence)
        item["rerating_evidence"] = structured_rerating_evidence(
            raw_rerating_evidence,
            RESEARCH_CROSSCHECKS.get(ticker),
            INDIRECT_SOURCES.get(ticker),
        )

        all_hist_rows = history_map[ticker]
        basis_index = next(
            (index for index, row in enumerate(all_hist_rows) if row.get("t") == BASIS_DATE),
            None,
        )
        if basis_index is None:
            raise RuntimeError(f"{ticker} history does not contain required basis date {BASIS_DATE}")
        # Keep every price-derived metric aligned to the report's declared basis
        # date, even when the API already contains newer completed sessions.
        hist_rows = all_hist_rows[basis_index:]
        close_row = hist_rows[0]
        prev_row = hist_rows[1] if len(hist_rows) > 1 else {}

        item["basis_date"] = close_row.get("t")
        item["close"] = close_row.get("c")
        item["open"] = close_row.get("o")
        item["high"] = close_row.get("h")
        item["low"] = close_row.get("l")
        item["volume"] = close_row.get("v")
        item["day_change"] = close_row.get("ch")
        item["previous_close"] = prev_row.get("c")

        snapshot = dict(valuation_snapshot["tickers"][ticker])
        snapshot.update({key: value for key, value in overlay_eps.items() if value is not None})
        price = item.get("close")
        audit = valuation_audit(item, snapshot)
        item["valuation_audit"] = audit
        warnings = []
        if snapshot.get("fy1_cross_source_warning"):
            warnings.append(str(snapshot["fy1_cross_source_warning"]))
        snapshot_warning = validate_valuation_snapshot(ticker, snapshot, price)
        if snapshot_warning:
            warnings.append(snapshot_warning)
        if str(audit.get("eps_audit_status", "")).startswith("跨幣別／ADR 待換算"):
            warnings.append(
                f"{audit.get('eps_audit_status')}；trailing 比較採 USD ADR statistics EPS，"
                "financials 本位幣 EPS 僅列為替代口徑，不直接互除"
            )
        if audit.get("forward_pe_status") == "Forward P/E 與 price/valuation EPS 不一致":
            warnings.append("Forward P/E 與 price/valuation EPS 不一致；採 price/明示 valuation EPS 重算")
        if str(audit.get("eps_audit_status", "")).startswith("不一致"):
            warnings.append(
                f"Statistics / financials TTM EPS 期間或調整口徑不同：{audit.get('eps_audit_status')}；"
                "trailing P/E 採與 statistics price/P-E 同頁的 statistics EPS"
            )
        pe = num(snapshot.get("pe"))
        fpe = num(snapshot.get("forward_pe"))
        reported_eps_ttm = num(snapshot.get("ttm_eps"))
        eps_ttm = num(snapshot.get("ttm_eps_proxy")) or reported_eps_ttm
        eps_ttm_basis = "same-snapshot statistics TTM EPS"
        if num(snapshot.get("ttm_eps_proxy")) is not None:
            eps_ttm_basis = snapshot.get("ttm_eps_proxy_basis") or "normalized TTM EPS proxy override"
            warnings.append(
                f"reported TTM EPS {fmt(reported_eps_ttm)} 含一次性項目；"
                f"current-EPS proxy / EPS bridge 改用 normalized TTM EPS proxy {fmt(eps_ttm)}。"
            )
        financial_eps_ttm = num(item.get("eps_diluted_ttm_financials"))
        if (
            eps_ttm is None
            and financial_eps_ttm is not None
            and item.get("financial_currency") in {None, "USD"}
        ):
            eps_ttm = financial_eps_ttm
            eps_ttm_basis = "financials diluted TTM EPS fallback"
            warnings.append(
                f"statistics TTM EPS 缺值；補用 financials diluted TTM EPS {financial_eps_ttm:.4f}"
            )
        eps_fwd, valuation_eps_basis, valuation_eps_type, valuation_eps_confidence = select_valuation_eps(snapshot)
        pe_calc = price / eps_ttm if price and eps_ttm else None
        if audit.get("pe_gap") is not None and audit["pe_gap"] > 0.03 and pe_calc is not None:
            pe = pe_calc
        fpe_calc = price / eps_fwd if price and eps_fwd else None
        if audit.get("forward_pe_gap") is not None and audit["forward_pe_gap"] > 0.01 and fpe_calc is not None:
            fpe = fpe_calc
        valuation_block_reason = None
        if eps_fwd is None:
            valuation_block_reason = "可靠 valuation EPS 未取得；本檔目標價已阻擋"
        valuation_warning = "；".join(dict.fromkeys(warnings)) if warnings else None
        if snapshot.get("valuation_eps_type") == "NEXT_DAY_CONSENSUS_PROXY":
            timing_note = (
                f"{BASIS_DATE} 正式收盤；估值分母為次一交易日擷取的最新共識 proxy，"
                "不是完全同日快照，估值信心降為中等"
            )
            valuation_warning = "；".join(
                value for value in [valuation_warning, timing_note] if value
            )
        valuation_confidence = "blocked" if valuation_block_reason else "medium" if valuation_warning else "high"
        pe_conflict = bool(valuation_warning)
        price_quality = valuation_block_reason or valuation_warning or (
            "正式收盤：history API 與同日估值快照已鎖定；通過 3% P/E 時間錯配檢查"
        )

        avg_volume_20 = num(item.get("Average Volume (20 Days)"))
        rvol = item["volume"] / avg_volume_20 if item.get("volume") and avg_volume_20 else None

        item.update(
            pe=pe,
            fpe=fpe,
            eps_ttm=eps_ttm,
            reported_eps_ttm=reported_eps_ttm,
            eps_ttm_proxy_source_url=snapshot.get("ttm_eps_proxy_source_url"),
            eps_ttm_basis=eps_ttm_basis,
            eps_fwd=eps_fwd,
            valuation_eps=eps_fwd,
            valuation_eps_basis=valuation_eps_basis,
            valuation_eps_type=valuation_eps_type,
            valuation_eps_confidence=valuation_eps_confidence,
            analyst_count=num(snapshot.get("analyst_count") or snapshot.get("consensus_analyst_count") or snapshot.get("fy1_analyst_count") or snapshot.get("ntm_analyst_count")),
            fy1_consensus_eps=num(snapshot.get("fy1_consensus_eps")),
            fy1_consensus_year=snapshot.get("fy1_consensus_year"),
            fy1_analyst_count=num(snapshot.get("fy1_analyst_count")),
            fy1_consensus_eps_basis=snapshot.get("fy1_consensus_eps_basis"),
            stockanalysis_fy1_crosscheck_eps=num(snapshot.get("stockanalysis_fy1_crosscheck_eps")),
            fy1_cross_source_gap_pct=num(snapshot.get("fy1_cross_source_gap_pct")),
            fy1_cross_source_warning=snapshot.get("fy1_cross_source_warning"),
            fy2_consensus_eps=num(snapshot.get("fy2_consensus_eps")),
            fy2_consensus_year=snapshot.get("fy2_consensus_year"),
            fy2_analyst_count=num(snapshot.get("fy2_analyst_count")),
            fy2_consensus_eps_basis=snapshot.get("fy2_consensus_eps_basis"),
            ntm_consensus_eps=num(snapshot.get("ntm_consensus_eps")),
            ntm_consensus_year=snapshot.get("ntm_consensus_year"),
            ntm_analyst_count=num(snapshot.get("ntm_analyst_count")),
            ntm_consensus_eps_basis=snapshot.get("ntm_consensus_eps_basis"),
            forward_eps_source_url=snapshot.get("forward_eps_source_url"),
            forward_eps_source_date=snapshot.get("forward_eps_source_date"),
            supplemental_eps_sources=supplemental_eps_sources(snapshot),
            valuation_snapshot_source=valuation_snapshot.get("source"),
            valuation_snapshot_url=(
                snapshot.get("source_url")
                or f"https://stockanalysis.com/stocks/{ticker.lower()}/statistics/"
            ),
            valuation_blocked=valuation_block_reason is not None,
            valuation_block_reason=valuation_block_reason,
            valuation_warning=valuation_warning,
            valuation_confidence=valuation_confidence,
            pe_calc=pe_calc,
            ps=num(item.get("PS Ratio")),
            ps_calc=audit.get("ps_calculated"),
            ps_status=audit.get("ps_status"),
            eps_audit_status=audit.get("eps_audit_status"),
            forward_pe_status=audit.get("forward_pe_status"),
            pe_conflict=pe_conflict,
            price_quality=price_quality,
            rvol=rvol,
            d5=change(hist_rows[0]["c"], hist_rows[5]["c"]) if len(hist_rows) > 5 else None,
            d20=change(hist_rows[0]["c"], hist_rows[20]["c"]) if len(hist_rows) > 20 else None,
            d60=change(hist_rows[0]["c"], hist_rows[60]["c"]) if len(hist_rows) > 60 else None,
        )
        item["eps_bridge"] = compute_eps_bridge(item)

        sec_stock_cache = (point_in_time_eps_cache.get("stocks") or {}).get(ticker) or {}
        pit_eps_rows = sec_stock_cache.get("quarters") or []
        item["proxy"], item["point_in_time_pe_meta"] = point_in_time_proxy_windows(
            hist_rows, pit_eps_rows, eps_ttm, ticker
        )
        item["sec_revenue_metrics"] = sec_quarterly_revenue_metrics(
            sec_stock_cache.get("revenue_quarters") or [],
            sec_stock_cache.get("source_url"),
        )
        item["ps_proxy"] = ps_proxy_windows(
            hist_rows,
            audit.get("ps_calculated") or audit.get("ps_source"),
            price,
            ticker,
        )

        configured_stress_m, configured_entry_m, configured_fair_m, configured_upper_m = config["mult"]
        current_ps = audit.get("ps_calculated") or audit.get("ps_source") or num(item.get("PS Ratio"))
        sales_per_share = price / current_ps if price and current_ps and current_ps > 0 else None
        valuation_metric = (
            "P/S"
            if eps_ttm is not None and eps_ttm <= 0 and sales_per_share and sales_per_share > 0
            else "P/E"
        )
        if valuation_metric == "P/S":
            historical_anchor = historical_sales_multiple_anchor(item["ps_proxy"])
            denominator = sales_per_share
            denominator_basis = "TTM revenue per share = close ÷ same-basis P/S"
            current_implied_multiple = current_ps
            metric_reason = (
                "TTM GAAP EPS 非正，Trailing P/E 不具經濟意義；主估值帶切換為 P/S Proxy，"
                "但 Fair 仍使用歷史 ×70% + 受限同業 ×30% 的同一算法。"
            )
        else:
            historical_anchor = historical_forward_multiple_anchor(item["proxy"], eps_ttm, eps_fwd)
            denominator = eps_ttm
            denominator_basis = eps_ttm_basis
            current_implied_multiple = pe
            metric_reason = (
                "TTM GAAP EPS 為正；Conservative valuation 使用 TTM EPS × point-in-time trailing P/E。Forward implied EPS 只用於 Growth Anchor / Trust-adjusted layer。"
            )
        item["multiple_derivation"] = {
            **historical_anchor,
            "legacy_config": [configured_stress_m, configured_entry_m, configured_fair_m, configured_upper_m],
            "historical_formula": (
                "historical current-sales P/S P50"
                if valuation_metric == "P/S"
                else "2Y/3Y point-in-time trailing P/E P50"
            ),
        }
        item.update(
            valuation_metric=valuation_metric,
            valuation_denominator=denominator,
            valuation_denominator_basis=denominator_basis,
            current_implied_multiple=current_implied_multiple,
            metric_reason=metric_reason,
            sales_per_share=sales_per_share,
        )

        earnings_date = parse_date(item.get("Earnings Date"))
        basis_dt = datetime.strptime(BASIS_DATE, "%Y-%m-%d").date()
        if earnings_date is None:
            item["earnings_status"] = "來源未提供可解析日期，改看估計修正與 IR 更新"
        elif earnings_date <= basis_dt:
            item["earnings_status"] = f"{item.get('Earnings Date')} 已過，不當作下一驗證點"
        else:
            item["earnings_status"] = f"下一/估計財報日：{item.get('Earnings Date')}"

        peer_rows = []
        for peer in [ticker] + config["peers"]:
            peer_stats = stats_map.get(peer, {})
            peer_price = peer_stats.get("stats_price")
            peer_pe = num(peer_stats.get("PE Ratio"))
            peer_fpe = num(peer_stats.get("Forward PE"))
            peer_ps = num(peer_stats.get("PS Ratio"))
            peer_eps_ttm = num(peer_stats.get("Earnings Per Share (EPS)"))
            peer_eps_fwd = peer_price / peer_fpe if peer_price and peer_fpe else None
            peer_basis = "current statistics page"
            # A watchlist ticker may also appear as another company's peer.
            # In that case it must still use the report-basis snapshot, not a
            # newer statistics-page value (the old GEV $18.50 leak).
            if peer in valuation_snapshot["tickers"]:
                peer_snapshot = snapshot_valuation_row(
                    valuation_snapshot["tickers"][peer]
                )
                peer_price = peer_snapshot["price"]
                peer_pe = peer_snapshot["pe"]
                peer_fpe = peer_snapshot["fpe"]
                peer_eps_ttm = peer_snapshot["eps_ttm"]
                peer_eps_fwd = peer_snapshot["eps_fwd"]
                peer_ps = num(stats_map.get(peer, {}).get("PS Ratio"))
                peer_basis = f"{BASIS_DATE} valuation snapshot"
            if peer == ticker:
                peer_price = item.get("close")
                peer_pe = item.get("pe")
                peer_fpe = item.get("fpe")
                peer_eps_ttm = item.get("eps_ttm")
                peer_eps_fwd = item.get("valuation_eps")
                peer_ps = current_ps
                peer_basis = f"{BASIS_DATE} report-audited valuation row"
            peer_rows.append(
                {
                    "ticker": peer,
                    "company": peer_stats.get("company_line", peer),
                    "business": "本體" if peer == ticker else PEER_BUSINESS.get(peer, "同業/相鄰業務"),
                    "relevance": "標的本體" if peer == ticker else "同業/相鄰估值錨",
                    "pe": peer_pe,
                    "fpe": peer_fpe,
                    "ps": peer_ps,
                    "eps_ttm": peer_eps_ttm,
                    "eps_fwd": peer_eps_fwd,
                    "pfcf": num(peer_stats.get("P/FCF Ratio")),
                    "evebitda": num(peer_stats.get("EV / EBITDA")),
                    "url": peer_stats.get("url"),
                    "valuation_basis": peer_basis,
                }
            )
        peer_only = peer_rows[1:]
        item["peer_rows"] = peer_rows
        item["peer_median"] = {
            "pe": median([row["pe"] for row in peer_only]),
            "fpe": median([row["fpe"] for row in peer_only]),
            "ps": median([row["ps"] for row in peer_only]),
            "pfcf": median([row["pfcf"] for row in peer_only]),
            "evebitda": median([row["evebitda"] for row in peer_only]),
        }
        peer_fpes = sorted(row["fpe"] for row in peer_only if row.get("fpe") and row["fpe"] > 0)
        peer_fpe_dispersion = (
            peer_fpes[-1] / peer_fpes[0] if len(peer_fpes) >= 2 else None
        )
        peer_fpe_anchor = item["peer_median"]["fpe"]
        peer_pe_anchor = item["peer_median"]["pe"]
        peer_ps_values = sorted(row["ps"] for row in peer_only if row.get("ps") and row["ps"] > 0)
        peer_ps_dispersion = (
            peer_ps_values[-1] / peer_ps_values[0] if len(peer_ps_values) >= 2 else None
        )
        peer_ps_anchor = item["peer_median"]["ps"]
        if (
            historical_anchor.get("median") is None
            and (
                len(peer_fpes) < 2
                or peer_fpe_dispersion is None
                or peer_fpe_dispersion > 2.0
            )
        ):
            peer_fpe_anchor = None
        if (
            valuation_metric == "P/S"
            and historical_anchor.get("median") is None
            and (
                len(peer_ps_values) < 2
                or peer_ps_dispersion is None
                or peer_ps_dispersion > 2.0
            )
        ):
            peer_ps_anchor = None
        peer_pes = sorted(row["pe"] for row in peer_only if row.get("pe") and row["pe"] > 0)
        peer_pe_dispersion = (
            peer_pes[-1] / peer_pes[0] if len(peer_pes) >= 2 else None
        )
        peer_anchor = peer_ps_anchor if valuation_metric == "P/S" else peer_pe_anchor
        peer_count = len(peer_ps_values) if valuation_metric == "P/S" else len(peer_pes)
        peer_dispersion = peer_ps_dispersion if valuation_metric == "P/S" else peer_pe_dispersion
        peer_raw_median = item["peer_median"]["ps"] if valuation_metric == "P/S" else item["peer_median"]["pe"]
        item["peer_valuation_quality"] = {
            "metric": valuation_metric,
            "count": peer_count,
            "dispersion": peer_dispersion,
            "raw_median": peer_raw_median,
            "anchor_used": peer_anchor,
            "status": (
                "採用（有自身歷史錨點並設 ±25% 限制）"
                if historical_anchor.get("median") is not None and peer_anchor is not None
                else "採用"
                if peer_anchor is not None
                else f"不採用（同業不足或 {valuation_metric} 分散超過 2 倍）"
            ),
        }
        conservative = compute_conservative_valuation(
            item["proxy"],
            item.get("eps_ttm"),
            item.get("valuation_eps"),
            item["peer_median"]["pe"],
        )
        conservative = apply_conservative_sanity_cap(item, conservative)
        item["conservative_valuation"] = conservative
        item["peer_sanity"] = compute_peer_sanity(
            item["peer_rows"],
            conservative,
            valuation_metric,
        )
        derived = derive_forward_band_multiples(
            historical_anchor,
            peer_anchor,
            current_implied_multiple,
        )
        if valuation_metric == "P/E" and conservative.get("conservative_fair_multiple"):
            derived.update(
                {
                    "stress": conservative.get("stress_multiple"),
                    "entry": conservative.get("entry_multiple"),
                    "fair": conservative.get("conservative_fair_multiple"),
                    "upper": conservative.get("upper_multiple"),
                    "peer": item["peer_median"]["pe"],
                    "peer_capped": conservative.get("peer_clamped_forward_pe"),
                    "current": current_implied_multiple,
                    "historical": conservative.get("historical_conservative_anchor"),
                    "fair_method": conservative.get("fair_method"),
                }
            )
        stress_m, entry_m, fair_m, upper_m = (
            derived.get("stress"),
            derived.get("entry"),
            derived.get("fair"),
            derived.get("upper"),
        )
        item["multiple_derivation"].update(derived)
        item.update(stressM=stress_m, entryM=entry_m, fairM=fair_m, upperM=upper_m)
        for name, multiple in [("stress", stress_m), ("entry", entry_m), ("fair", fair_m), ("upper", upper_m)]:
            item[name] = denominator * multiple if denominator and multiple else None
        item["currentToEntry"] = change(item["entry"], price)
        item["stopPct"] = change(item["stress"], item["entry"])
        item["target1Pct"] = change(item["fair"], item["entry"])
        item["target2Pct"] = change(item["upper"], item["entry"])
        item["priceScenario"] = classify_price(price, item["stress"], item["entry"], item["fair"], item["upper"])
        item["rerating_model"] = build_rerating_model(item)
        item["growth_pass_through"] = compute_growth_pass_through(item, conservative)
        item["fes_lite"] = score_fes_lite(
            item,
            item["growth_pass_through"],
            item["peer_sanity"],
        )
        item["eps_year_clarity"] = compute_eps_year_clarity(item)
        item["fets"] = score_fets(item)
        item["forward_eps_layers"] = compute_forward_eps_layers(item)
        item["res"] = score_res(item)
        item["forward_eps_layers"] = compute_forward_eps_layers(item)
        item["price_nodes"] = compute_price_nodes(item)
        item["stress"] = item["price_nodes"].get("bear_stress")
        item["entry"] = item["price_nodes"].get("value_entry")
        item["fair"] = item["price_nodes"].get("conservative_fair")
        item["upper"] = item["price_nodes"].get("selected_growth_fair") or item["price_nodes"].get("forward_growth_anchor")
        item["currentToEntry"] = change(item["entry"], price)
        item["stopPct"] = change(item["stress"], item["entry"])
        item["target1Pct"] = change(item["fair"], item["entry"])
        item["target2Pct"] = change(item["upper"], item["entry"])
        item["priceScenario"] = classify_price(price, item["stress"], item["entry"], item["fair"], item["upper"])
        item["integrated_price_ladder"] = compute_integrated_price_ladder(
            item,
            conservative,
            item["growth_pass_through"],
        )
        item["integrated_action"] = assign_action(item)
        if ticker == "GEV":
            item["decision"] = "持有 2 股，不加碼"
        elif ticker == "COHR":
            item["decision"] = "已清倉，等再進場訊號"
        elif price and item["entry"] and price <= item["entry"] * 1.03:
            item["decision"] = "可小量研究"
        elif price and item["fair"] and price >= item["fair"]:
            item["decision"] = "偏貴 / 不追"
        else:
            item["decision"] = "等待回檔或確認"
        data.append(item)

    return data, stats_map, history_map


CSS = """
:root{--ink:#17202a;--muted:#5f6d7a;--line:#d9e0e7;--bg:#f6f8fb;--panel:#fff;--head:#102033;--blue:#1b5f9e;--green:#1f7a55;--amber:#9a5b00;--red:#a13a3a;--purple:#6750a4}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif;line-height:1.58}
header.hero{background:var(--head);color:#fff;padding:28px clamp(18px,4vw,52px);border-bottom:4px solid #3a87c9}header h1{margin:0 0 8px;font-size:clamp(26px,4vw,40px)}header p{margin:3px 0;color:#dce8f5}
html{scroll-behavior:smooth;scroll-padding-top:86px}
main{width:min(1580px,calc(100vw - 28px));margin:22px auto 48px}section,.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:22px;margin:16px 0}
h2{margin:0 0 12px;font-size:22px}h3{margin:22px 0 10px;font-size:18px;color:#162b43}.muted{color:var(--muted)}.small{font-size:12px;color:var(--muted)}
.note{border-left:4px solid #8aa9c7;padding:8px 12px;background:#f4f8fc;color:#31465c}.warn{border-left:4px solid var(--amber);padding:8px 12px;background:#fff8e8;color:#5d3a00;font-weight:650}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.metric{border:1px solid var(--line);border-left:4px solid #3a87c9;border-radius:8px;padding:14px;background:#fbfdff}.metric strong{display:block;font-size:24px;color:var(--blue)}
.key{color:var(--blue);font-weight:800}.positive{color:var(--green);font-weight:800}.negative,.risk-text{color:var(--red);font-weight:800}.watch-text{color:var(--amber);font-weight:800}.purple{color:var(--purple);font-weight:800}
.tag{display:inline-block;border-radius:999px;padding:3px 9px;font-size:12px;font-weight:700;background:#eaf4ee;color:var(--green);margin:2px 4px 2px 0;white-space:nowrap}.tag.watch{background:#fff4dc;color:var(--amber)}.tag.risk{background:#f9e7e7;color:var(--red);border:1px solid #e8baba}.tag.key{background:#e8f2fb;color:var(--blue)}.tag.muted{background:#edf1f5;color:var(--muted)}.tag.purple{background:#f0eafd;color:var(--purple)}.tag.overheat{background:#f3e9ff;color:#6f2c91;border:1px solid #d8b8ea}
table{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px}th,td{border:1px solid var(--line);padding:8px 9px;vertical-align:top}th{background:#eef4fa;text-align:left}td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}td.num{color:#163e63;font-weight:700}
.summary-scroll{width:100%;overflow-x:auto;padding-bottom:5px}.summary-table{min-width:1540px;table-layout:auto}.summary-table th,.summary-table td{padding:7px 8px}.summary-table td:nth-child(2){min-width:150px}.summary-table td:nth-child(3){min-width:130px}.summary-table td:nth-child(15){min-width:180px}.summary-table td:nth-child(16){min-width:170px}.summary-table td:nth-child(15) .tag{white-space:normal;line-height:1.35;border-radius:10px;margin:0}
tr.current-row td{background:#f4f9ff}tr.entry-row td{background:#f3faf5}tr.watch-row td{background:#fffaf0}tr.risk-row td{background:#fff5f5}tr.upper-row td{background:#fff8ee}tr.audit-row td{background:#f7f4ff}
.tabs{position:sticky;top:0;z-index:8;display:flex;gap:8px;flex-wrap:wrap;background:rgba(246,248,251,.96);backdrop-filter:blur(8px);padding:10px 0;border-bottom:1px solid var(--line)}.tab-button{appearance:none;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--ink);padding:8px 12px;font-weight:700;cursor:pointer}.tab-button:hover{border-color:#7da9d0;background:#f3f8fd}.tab-button[aria-selected=true]{background:var(--blue);border-color:var(--blue);color:#fff}
.report-shell{display:grid;grid-template-columns:210px minmax(0,1fr);gap:16px;align-items:start}.section-nav{position:sticky;top:78px;max-height:calc(100vh - 94px);overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;margin:16px 0}.section-nav strong{display:block;margin:2px 6px 9px;color:#162b43}.section-nav a{display:block;padding:7px 9px;border-radius:6px;color:#415466;text-decoration:none;font-size:13px;line-height:1.3}.section-nav a:hover,.section-nav a.active{background:#e8f2fb;color:var(--blue);font-weight:750}.section-nav .nav-divider{height:1px;background:var(--line);margin:7px 4px}
.panel h2[id],.panel h3[id]{scroll-margin-top:86px}
.hidden{display:none}a{color:var(--blue)}ul{padding-left:20px}.two-col{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:920px){section,.panel{padding:16px}table{display:block;overflow-x:auto;white-space:nowrap}.tabs{position:static;flex-wrap:nowrap;overflow-x:auto}.report-shell{display:block}.section-nav{position:static;display:flex;gap:6px;overflow-x:auto;max-height:none;white-space:nowrap}.section-nav strong,.section-nav .nav-divider{display:none}.section-nav a{border:1px solid var(--line);background:#fff}.two-col{grid-template-columns:1fr}}
"""


def proxy_table(item: dict) -> str:
    pit_meta = item.get("point_in_time_pe_meta") or {}
    is_pit = pit_meta.get("status") == "ok"
    rows = []
    for window in item["proxy"]:
        verified = "已重算驗證" if window["verified"] else "來源需重驗"
        row_class = "" if window["verified"] else "risk-row"
        rows.append(
            f"""<tr class="{row_class}"><td>{window['label']}</td><td class="num">{window['n']}</td><td>{window['start']} 至 {window['end']}</td>
            <td class="num">{ratio_html(window['p10'],'risk-text')}</td><td class="num">{ratio_html(window['p50'])}</td><td class="num">{ratio_html(window.get('p75'))}</td><td class="num">{ratio_html(window['p90'],'watch-text')}</td>
            <td>{escape(window['conf'])}</td><td>{tag_html(verified)}</td></tr>"""
        )
    anchor = next((row for row in item["proxy"] if row["label"] == "1Y"), item["proxy"][0])
    eps = item.get("eps_ttm")
    anchor_rows = []
    for label, key, class_name, meaning in [
        ("1Y P10 壓力區", "p10", "risk-text", "若 thesis intact 才能研究；若基本面壞，不接刀。"),
        ("1Y P50 中位", "p50", "key", "近期中位，不是 overheat，也不是自動買點。"),
        ("1Y P90 偏熱", "p90", "watch-text", "EPS 沒上修就停利/不追。"),
    ]:
        multiple = anchor.get(key)
        price = multiple * eps if multiple and eps else None
        anchor_rows.append(
            f"""<tr><td>{label}</td><td class="num">{ratio_html(multiple,class_name)}</td><td class="num">{money_html(price,class_name)}</td><td>{meaning}</td></tr>"""
        )
    denominator_status = item["proxy"][0].get("denominator_status") if item.get("proxy") else "invalid"
    denominator_note = {
        "valid": "TTM EPS 分母為正且可用。",
        "fragile": "TTM EPS 為正但接近零；倍數極度敏感，只能低信心參考。",
        "invalid": "TTM EPS 非正或缺失；Proxy 不可計算，欄位保留待補。",
    }.get(denominator_status, "EPS 分母狀態待確認。")
    method_text = (
        "本表是 point-in-time P/E：每日調整後收盤價 ÷ 該日市場已知的最近四季 diluted EPS；新申報 EPS 從申報後下一交易日生效。"
        if is_pit else
        f"本表因 {pit_meta.get('reason') or 'SEC 季度 EPS 不足'} 退回 current-TTM proxy：歷史收盤價 ÷ 最新 TTM EPS，不是正統逐日歷史 P/E。"
    )
    return f"""
    <p><strong>{escape(pit_meta.get('method') or 'P/E history')}：</strong>{escape(method_text)}</p>
    <p class="note"><strong>分母稽核：</strong>{escape(denominator_note)} Snapshot TTM {money_html(item.get('eps_ttm'))}；point-in-time 最新 TTM {money_html(pit_meta.get('latest_point_ttm'))}；audit gap {pct_html(pit_meta.get('audit_gap')*100 if pit_meta.get('audit_gap') is not None else None)}。</p>
    <table><thead><tr><th>窗口</th><th class="num">價格資料筆數</th><th>起訖日</th><th class="num">P10</th><th class="num">P50</th><th class="num">P75</th><th class="num">P90</th><th>可信度</th><th>驗證</th></tr></thead><tbody>{table_rows(rows)}</tbody></table>
    <table><thead><tr><th>區間</th><th class="num">P/E</th><th class="num">以目前 TTM 換算價格</th><th>解讀</th></tr></thead><tbody>{table_rows(anchor_rows)}</tbody></table>
    """


def ps_proxy_table(item: dict) -> str:
    rows = []
    for window in item.get("ps_proxy", []):
        rows.append(
            f"""<tr><td>{window['label']}</td><td class="num">{window['n']}</td><td>{window['start']} 至 {window['end']}</td>
            <td class="num">{ratio_html(window['p10'],'risk-text')}</td><td class="num">{ratio_html(window['p50'])}</td>
            <td class="num">{ratio_html(window['p90'],'watch-text')}</td><td>{escape(window['conf'])}</td>
            <td>{tag_html('已重算驗證' if window['verified'] else '來源需重驗')}</td></tr>"""
        )
    one_year = next((row for row in item.get("ps_proxy", []) if row.get("label") == "1Y"), {})
    return f"""
    <p class="note"><strong>P/S Proxy 狀態：可用。</strong>
    基準日重算 P/S {ratio_html(item.get('ps_calc') or item.get('ps'))}；
    1Y P10 / P50 / P90 =
    {ratio_html(one_year.get('p10'),'risk-text')} /
    {ratio_html(one_year.get('p50'))} /
    {ratio_html(one_year.get('p90'),'watch-text')}。</p>
    <p>當 TTM EPS 非正、接近零或 P/E proxy 失真時，補充
    <strong>current-sales P/S proxy</strong>：以基準日重算 P/S 為錨，
    按歷史價格相對基準日價格縮放。這不是逐期歷史 P/S，2Y/3Y 必須降權。</p>
    <table><thead><tr><th>窗口</th><th class="num">價格資料筆數</th><th>起訖日</th>
    <th class="num">P10</th><th class="num">P50</th><th class="num">P90</th><th>可信度</th><th>驗證</th></tr></thead>
    <tbody>{table_rows(rows)}</tbody></table>
    """


def source_number_table(item: dict) -> str:
    pe_note = "同日快照已通過 close / TTM EPS 與來源 P/E 差異 <=3% 驗證"
    row_class = ""
    eps_display = f"TTM EPS {money_html(item['eps_ttm'])}"
    if (
        item.get("reported_eps_ttm") is not None
        and item.get("eps_ttm") is not None
        and abs(item["reported_eps_ttm"] - item["eps_ttm"]) > 0.01
    ):
        eps_display = (
            f"Reported TTM EPS {money_html(item['reported_eps_ttm'])}；"
            f"proxy/valuation TTM EPS {money_html(item['eps_ttm'])}"
        )
    if item.get("valuation_blocked"):
        pe_note = item["valuation_block_reason"]
        row_class = "risk-row"
    elif item.get("valuation_warning"):
        pe_note = f"可計算、信心中等：{item['valuation_warning']}"
        row_class = "watch-row"
    return f"""
    <table><tbody>
      <tr><th>價格/時點</th><td>{money_html(item['close'])}；日漲跌 {pct_html(item['day_change'])}；成交量 <strong>{fmt(item['volume'],0)}</strong>；RVOL {ratio_html(item['rvol'])}</td><td>{escape(item['price_quality'])}</td></tr>
      <tr><th>盤後分離</th><td>After-hours {escape(item.get('after_hours_price') or 'n/a')} {escape(item.get('after_hours_move') or '')}</td><td>盤後資料只作參考，不放入正式收盤計算。</td></tr>
      <tr><th>股價/技術</th><td>5D {pct_html(item['d5'])} / 20D {pct_html(item['d20'])} / 60D {pct_html(item['d60'])}；50DMA {escape(item.get('50-Day Moving Average'))}；200DMA {escape(item.get('200-Day Moving Average'))}；52W {escape(item.get('52-Week Price Change'))}</td><td>來源：Max history API + statistics page。</td></tr>
      <tr><th>EPS</th><td>{eps_display}；本報唯一 valuation EPS {money_html(item['valuation_eps'])}</td><td>TTM/proxy：{escape(item.get('eps_ttm_basis'))}；Valuation：{escape(item['valuation_eps_basis'])}；type {escape(item.get('valuation_eps_type') or '')}；confidence {escape(item.get('valuation_eps_confidence') or '')}。總表、EPS 模組、同業本體列與目標價共用。</td></tr>
      <tr class="{row_class}"><th>估值</th><td>來源 P/E {ratio_html(item['pe'])}；計算 P/E close/TTM EPS {trailing_pe_html(item)}；Forward P/E {ratio_html(item['fpe'])}；來源 P/S {ratio_html(item.get('ps'))}；重算 P/S {ratio_html(item.get('ps_calc'))}；P/FCF {escape(item.get('P/FCF Ratio'))}；EV/EBITDA {escape(item.get('EV / EBITDA'))}</td><td>{pe_note}；P/S {escape(item.get('ps_status'))}</td></tr>
      <tr><th>估值快照</th><td>{escape(item['valuation_snapshot_source'])}</td><td><a href="{escape(item['valuation_snapshot_url'])}">同日基準報告</a></td></tr>
      <tr><th>品質</th><td>GM {escape(item.get('Gross Margin'))}；OM {escape(item.get('Operating Margin'))}；FCF margin {escape(item.get('FCF Margin'))}；Debt/Equity {escape(item.get('Debt / Equity'))}</td><td>用於判斷同業折溢價與估值品質。</td></tr>
      <tr><th>分析師</th><td>目標價 {escape(item.get('Price Target'))}；共識 {escape(item.get('Analyst Consensus'))}；3Y EPS growth {escape(item.get('EPS Growth Forecast (3Y)'))}</td><td>只作 sanity check，不直接作本報目標價。</td></tr>
    </tbody></table>
    """


def eps_bridge(item: dict) -> str:
    valuation_label = escape(item["valuation_eps_basis"])
    audit = item.get("valuation_audit") or {}
    bridge = (item.get("eps_bridge") or {}).get("eps_growth_bridge") or {}
    supplemental = item.get("supplemental_eps_sources") or []
    supplemental_rows = "".join(
        f"<tr><td>{escape(row.get('label'))}</td><td class=\"num\">{escape(row.get('value'))}</td><td>{escape(row.get('confidence'))}</td><td>{escape(row.get('note'))}</td></tr>"
        for row in supplemental
    ) or '<tr><td colspan="4">未取得公司 guidance 或 FY1/FY2 consensus 明細；估值仍採同快照 implied NTM EPS proxy。</td></tr>'
    return f"""
    <table><thead><tr><th>估值口徑</th><th class="num">EPS 分母</th><th class="num">計算</th><th class="num">結果</th><th>說明</th></tr></thead><tbody>
      <tr><td>TTM GAAP / trailing</td><td class="num">{money_html(item['eps_ttm'])}</td><td class="num">{money_html(item['close'])} / {money_html(item['eps_ttm'])}</td><td class="num">{trailing_pe_html(item)}</td><td>{'TTM EPS 為負，P/E 不具經濟意義；保留實際 EPS，不顯示負本益比。' if item.get('eps_ttm') is not None and item.get('eps_ttm') <= 0 else '已實現過去 12 個月；若和來源 P/E 不同，標為口徑差異。'}</td></tr>
      <tr class="watch-row"><td>Forward P/E / implied NTM EPS proxy</td><td class="num">{money_html(item['valuation_eps'])}</td><td class="num">{money_html(item['close'])} / {ratio_html(item['fpe'])}</td><td class="num">{ratio_html(item['fpe'])}</td><td>本報估值固定用 same-snapshot implied NTM EPS proxy；FY consensus/guidance 只揭露，不重算目標價。</td></tr>
      <tr><td>本報唯一 valuation EPS</td><td class="num">{money_html(item['valuation_eps'])}</td><td class="num">{valuation_label}</td><td class="num">{money_html(item['valuation_eps'])}</td><td>type {escape(item.get('valuation_eps_type') or '')}；confidence {escape(item.get('valuation_eps_confidence') or '')}。所有目標價與本體同業列只能引用此欄。</td></tr>
      <tr><td>EPS Growth Bridge</td><td class="num">{pct_html(bridge.get('value') * 100 if bridge.get('value') is not None else None)}</td><td class="num">{money_html(item['valuation_eps'])} / {money_html(item['eps_ttm'])} - 1</td><td class="num">{pct_html(bridge.get('value') * 100 if bridge.get('value') is not None else None)}</td><td>市場 forward EPS 分母比已實現 TTM EPS 高/低多少；這只描述 EPS 分母差異，不直接等於可買幅度。</td></tr>
    </tbody></table>
    <table><thead><tr><th>補充 EPS 來源</th><th class="num">數值</th><th>可信度</th><th>用途</th></tr></thead><tbody>{supplemental_rows}</tbody></table>
    <table><thead><tr><th>硬性稽核</th><th>來源值</th><th>重算值</th><th>狀態</th></tr></thead><tbody>
      <tr><td>TTM EPS</td><td>Statistics {money_html(audit.get('stats_eps_ttm'))}</td><td>Financials {money_html(audit.get('financials_eps_ttm'))}（{escape(audit.get('financial_currency') or '幣別待補')}）</td><td>{escape(audit.get('eps_audit_status'))}</td></tr>
      <tr><td>Trailing P/E</td><td>{ratio_html(audit.get('pe_source'))}</td><td>{'<span class="tag muted">N/M</span>' if audit.get('pe_status','').startswith('N/M') else ratio_html(audit.get('pe_calculated'))}</td><td>{escape(audit.get('pe_status'))}</td></tr>
      <tr><td>Forward P/E</td><td>{ratio_html(audit.get('forward_pe_source'))}</td><td>{ratio_html(audit.get('forward_pe_calculated'))}</td><td>{escape(audit.get('forward_pe_status'))}</td></tr>
      <tr><td>P/S</td><td>{ratio_html(audit.get('ps_source'))}</td><td>{ratio_html(audit.get('ps_calculated'))} = Market Cap / TTM Revenue</td><td>{escape(audit.get('ps_status'))}</td></tr>
    </tbody></table>
    """


def eps_year_clarity_table(item: dict) -> str:
    clarity = item.get("eps_year_clarity") or {}
    rows = "".join(
        f"<tr><td>{escape(row.get('label'))}</td><td class='num'>{money_html(row.get('eps_used'))}</td>"
        f"<td>{escape(row.get('eps_year'))}</td><td>{escape(row.get('eps_type'))}</td>"
        f"<td>{escape(row.get('eps_source'))}</td><td class='num'>{fmt(row.get('analyst_count'),0) if row.get('analyst_count') is not None else 'N/A'}</td>"
        f"<td>{escape(row.get('pe_label'))}</td><td>{escape(row.get('note'))}</td></tr>"
        for row in clarity.get("rows", [])
    )
    return f"""
    <p class="note"><strong>EPS year clarity：</strong>美股 EPS 不再只寫 forward EPS；FY1、FY2、NTM consensus、same-snapshot implied EPS、TTM EPS 必須分列。Missing Data 不補假資料。</p>
    <table><thead><tr><th>EPS label</th><th class="num">EPS_used</th><th>EPS_year</th><th>EPS_type</th><th>EPS_source</th><th class="num">analyst_count</th><th>PE_label</th><th>note</th></tr></thead><tbody>{rows}</tbody></table>
    """


def peer_table(item: dict) -> str:
    rows = []
    for row in item["peer_rows"]:
        class_name = "current-row" if row["ticker"] == item["ticker"] else ""
        rows.append(
            f"""<tr class="{class_name}"><td><a href="{escape(row.get('url') or '#')}">{row['ticker']}</a></td><td>{escape(row['company'])}</td><td>{escape(row['business'])}</td><td>{escape(row['relevance'])}</td>
            <td class="num">{ratio_html(row['pe'])}</td><td class="num">{ratio_html(row['fpe'])}</td><td class="num">{ratio_html(row.get('ps'))}</td><td class="num">{money_html(row['eps_ttm'])}</td><td class="num">{money_html(row['eps_fwd'])}</td><td class="num">{ratio_html(row['pfcf'])}</td><td class="num">{ratio_html(row['evebitda'])}</td></tr>"""
        )
    med = item["peer_median"]
    return f"""
    <table><thead><tr><th>公司</th><th>名稱</th><th>主要產品/業務</th><th>相關性</th><th class="num">P/E</th><th class="num">Forward P/E</th><th class="num">P/S</th><th class="num">TTM EPS</th><th class="num">Implied NTM EPS proxy</th><th class="num">P/FCF</th><th class="num">EV/EBITDA</th></tr></thead><tbody>{table_rows(rows)}</tbody></table>
    <table><thead><tr><th>同業組合</th><th class="num">P/E 中位數</th><th class="num">Forward P/E 中位數</th><th class="num">P/S 中位數</th><th class="num">P/FCF 中位數</th><th class="num">EV/EBITDA 中位數</th></tr></thead><tbody>
      <tr><td>{escape(', '.join(item['peers']))}</td><td class="num">{ratio_html(med['pe'])}</td><td class="num">{ratio_html(med['fpe'])}</td><td class="num">{ratio_html(med['ps'])}</td><td class="num">{ratio_html(med['pfcf'])}</td><td class="num">{ratio_html(med['evebitda'])}</td></tr>
      <tr class="current-row"><td>{item['ticker']}</td><td class="num">{ratio_html(item['pe'])}</td><td class="num">{ratio_html(item['fpe'])}</td><td class="num">{ratio_html(item.get('ps_calc') or item.get('ps'))}</td><td class="num">{escape(item.get('P/FCF Ratio'))}</td><td class="num">{escape(item.get('EV / EBITDA'))}</td></tr>
    </tbody></table>
    <p class="small">同業估值品質：{escape((item.get('peer_valuation_quality') or {}).get('status'))}；
    有效同業數 {fmt((item.get('peer_valuation_quality') or {}).get('count'),0)}；
    {escape((item.get('peer_valuation_quality') or {}).get('metric') or 'Forward P/E')} 最大/最小 {ratio_html((item.get('peer_valuation_quality') or {}).get('dispersion'))}。
    同業中位數只是 sanity check；產業不相同、樣本不足或倍數分散過大時，不納入 Fair。</p>
    """


def valuation_breakdown(item: dict) -> str:
    med = item["peer_median"]
    derivation = item.get("multiple_derivation") or {}
    fair_method = derivation.get("fair_method")
    metric = item.get("valuation_metric") or "P/E"
    denominator = item.get("valuation_denominator")
    denominator_label = "Revenue/share" if metric == "P/S" else "EPS"
    denominator_basis = item.get("valuation_denominator_basis") or item.get("valuation_eps_basis")
    current_metric_label = "現行 P/S" if metric == "P/S" else "現行 Forward P/E"
    historical_metric_name = "歷史 P/S 錨點" if metric == "P/S" else "歷史錨點"
    peer_metric_name = "同業 P/S" if metric == "P/S" else "同業 Forward P/E"
    if fair_method == "historical_70_peer_30":
        fair_formula = (
            f"歷史 × 70% + 同業限制值 × 30% = "
            f"{fmt(derivation.get('historical'))} × 70% + {fmt(derivation.get('peer_capped'))} × 30%"
        )
        derivation_explanation = (
            f"③ 同業限制值 = clamp({peer_metric_name} {ratio(derivation.get('peer'))}, {historical_metric_name} × 75%, {historical_metric_name} × 125%) = {ratio_html(derivation.get('peer_capped'))}。"
            f"④ Fair = {historical_metric_name} × 70% + 同業限制值 × 30% = {fmt(derivation.get('historical'))} × 70% + {fmt(derivation.get('peer_capped'))} × 30% = {ratio_html(derivation.get('fair'))}。"
            f"{current_metric_label} {ratio_html(derivation.get('current'))} 只用來比較現價折溢價，不參與 Fair 計算。"
        )
    elif fair_method == "historical_only":
        fair_formula = f"無合格同業；Fair = {historical_metric_name} {fmt(derivation.get('historical'))}"
        derivation_explanation = f"③ 無合格直接同業，Fair 只採{historical_metric_name} = {ratio_html(derivation.get('fair'))}；{current_metric_label}不參與計算。"
    elif fair_method == "peer_only":
        fair_formula = f"{historical_metric_name}不可用；Fair = 合格同業中位 {fmt(derivation.get('peer'))}"
        derivation_explanation = f"③ 因自身歷史 {metric} 錨點不可用，Fair 採合格直接同業中位 = {ratio_html(derivation.get('fair'))}。"
    else:
        fair_formula = f"無歷史/合格同業；暫用{current_metric_label} {fmt(derivation.get('current'))}"
        derivation_explanation = (
            f"③ 無自身歷史錨點且無合格直接同業，暫用{current_metric_label} {ratio_html(derivation.get('fair'))} 作市場隱含錨；"
            "此結果不是獨立合理價，信心低，需補 direct peer 或 consensus 歷史。"
        )
    rows = []
    for label, key, multiple, class_name, judgement in [
        ("Stress / 風險審核", "stress", item["stressM"], "risk-text", "跌破後檢查 thesis，非自動買點"),
        ("Entry / 第一研究價", "entry", item["entryM"], "positive", "thesis intact 且市場穩定才小量"),
        ("Base fair / 第一目標", "fair", item["fairM"], "key", "合理價，不追價"),
        ("Upper / 第二目標", "upper", item["upperM"], "watch-text", "需 EPS/FCF/backlog 上修，否則停利檢查"),
    ]:
        output_price = item.get(key)
        trailing = output_price / item["eps_ttm"] if output_price and item.get("eps_ttm") and item.get("eps_ttm") > 0 else None
        row_class = "risk-row" if key == "stress" else "entry-row" if key == "entry" else "current-row" if key == "fair" else "upper-row"
        formulas = {
            "stress": f"min(Fair × 75%, {historical_metric_name}) = min({fmt(derivation.get('fair'))} × 75%, {fmt(derivation.get('historical'))})",
            "entry": f"Fair × 85% = {fmt(derivation.get('fair'))} × 85%",
            "fair": fair_formula,
            "upper": f"Fair × 115% = {fmt(derivation.get('fair'))} × 115%",
        }
        rows.append(
            f"""<tr class="{row_class}"><td>{label}</td><td>{escape(denominator_basis)}</td><td class="num">{money_html(denominator)}</td><td class="num">{ratio_html(multiple,class_name)}</td>
            <td>{escape(formulas[key])}</td><td>{fmt(denominator)} × {fmt(multiple)}x = {money(output_price)}</td><td class="num">{money_html(output_price,class_name)}</td>
            <td class="num">{ratio_html(trailing)}</td><td>{judgement}</td></tr>"""
        )
    selected_proxy_rows = (item.get('ps_proxy') if metric == "P/S" else item.get('proxy')) or []
    two_year_proxy_p50 = next((r.get('p50') for r in selected_proxy_rows if r['label']=='2Y'), None)
    three_year_proxy_p50 = next((r.get('p50') for r in selected_proxy_rows if r['label']=='3Y'), None)
    if metric == "P/S":
        historical_formula_text = (
            f"① 2Y 歷史 P/S proxy P50 = {ratio_html(derivation.get('two_year'))}；"
            f"3Y = {ratio_html(derivation.get('three_year'))}。"
        )
    else:
        historical_formula_text = (
            f"① 2Y point-in-time 同口徑倍數 = {fmt(two_year_proxy_p50)} × {fmt(item.get('eps_ttm'))} ÷ {fmt(item.get('valuation_eps'))} = {ratio_html(derivation.get('two_year'))}；"
            f"3Y = {fmt(three_year_proxy_p50)} × {fmt(item.get('eps_ttm'))} ÷ {fmt(item.get('valuation_eps'))} = {ratio_html(derivation.get('three_year'))}。"
        )
    return f"""
    <p><strong>基準日目前價格：{money_html(item.get('close'))}</strong></p>
    <p class="note"><strong>本檔主估值口徑：{escape(metric)}。</strong> {escape(item.get('metric_reason'))}
    本節是 <strong>Conservative Valuation</strong>：防守型合理價 / 下檔估值錨，不是唯一 fair value。Upper 只是 conservative valuation 的上緣，不能直接代表 Growth Fair 天花板。</p>
    <p class="small"><strong>完整倍數算法：</strong>
    {historical_formula_text}
    ② 正常化錨 = median(2Y, 3Y point-in-time P50) = {ratio_html(derivation.get('historical'))}。
    {derivation_explanation}
    ④/⑤ Stress = min(Fair × 75%, 歷史錨點) = {ratio_html(derivation.get('stress'))}；Entry = Fair × 85% = {ratio_html(derivation.get('entry'))}；Upper = Fair × 115% = {ratio_html(derivation.get('upper'))}。</p>
    <table><thead><tr><th>輸出價格/區間</th><th>{escape(denominator_label)} 口徑</th><th class="num">{escape(denominator_label)} 數字</th><th class="num">倍數</th><th>倍數實際計算</th><th>目標價公式</th><th class="num">結果</th><th class="num">換算 trailing P/E</th><th>判斷</th></tr></thead><tbody>{table_rows(rows)}</tbody></table>
    """


def peer_sanity_table(item: dict) -> str:
    peer = item.get("peer_sanity") or {}
    clamp = peer.get("peer_clamp") or {}
    warning = f"<p class='warn'>{escape(peer.get('warning'))}</p>" if peer.get("warning") else ""
    return f"""
    <p><strong>同業只作 sanity check，不可直接決定 fair。</strong>它在本報有三個用途：Conservative Fair 的 peer clamp、FES-Lite 的 E 模組、同業分散度與 de-rating 風險旗標。</p>
    <table><thead><tr><th>項目</th><th class="num">數值</th><th>公式 / 定義</th><th>處理</th></tr></thead><tbody>
      <tr><td>Peer Median P/E</td><td class="num">{ratio_html(peer.get('median'))}</td><td>同業 trailing P/E 中位數</td><td>只作 conservative sanity check</td></tr>
      <tr><td>Peer Clamp Lower Bound</td><td class="num">{ratio_html(clamp.get('lower'))}</td><td>Historical Conservative Anchor × 75%</td><td>限制同業下緣</td></tr>
      <tr><td>Peer Clamp Upper Bound</td><td class="num">{ratio_html(clamp.get('upper'))}</td><td>Historical Conservative Anchor × 125%</td><td>限制同業上緣</td></tr>
      <tr><td>Peer-clamped P/E</td><td class="num">{ratio_html(clamp.get('clamped'))}</td><td>clamp(Peer Median P/E, Lower, Upper)</td><td>最多占 Conservative Fair 30%</td></tr>
      <tr><td>Peer Dispersion Ratio</td><td class="num">{ratio_html(peer.get('dispersion_ratio'))}</td><td>max(peer P/E) / min(peer P/E)</td><td>品質：{escape(peer.get('quality'))}；E score max = {fmt(peer.get('e_score_cap'),0)}</td></tr>
    </tbody></table>
    {warning}
    """


def growth_pass_through_table(item: dict) -> str:
    growth = item.get("growth_pass_through") or {}
    bridge = item.get("eps_bridge") or {}
    valuation_eps = item.get("valuation_eps")
    conservative = item.get("conservative_valuation") or {}
    q_rows = "".join(
        f"<tr><td>Growth Fair q={int(q*100)}%</td><td class='num'>{money_html(value)}</td>"
        f"<td>Conservative Fair + {int(q*100)}% × Growth Gap</td><td>EPS 成長被市場承認並資本化到股價的比例</td></tr>"
        for q, value in sorted((growth.get("q_fair") or {}).items())
    ) or "<tr><td colspan='4'>Missing Data：Growth Gap 不可用時不輸出 q 節點。</td></tr>"
    warning = f"<p class='warn'>{escape(growth.get('warning'))}</p>" if growth.get("warning") else ""
    return f"""
    <p><strong>目的：</strong>衡量市場應該把 Forward EPS 成長反映多少到股價。q 由 FES-Lite 決定，不可因股價上漲人工提高。</p>
    <table><thead><tr><th>變數</th><th class="num">數值</th><th>公式</th><th>定義</th></tr></thead><tbody>
      <tr><td>Valuation EPS</td><td class="num">{money_html(valuation_eps)}</td><td>Current Price / Forward P/E</td><td>本報唯一 valuation EPS</td></tr>
      <tr><td>EPS Growth Bridge</td><td class="num">{pct_html((bridge.get('eps_growth_bridge') or {}).get('value') * 100 if (bridge.get('eps_growth_bridge') or {}).get('value') is not None else None)}</td><td>Valuation EPS / TTM EPS - 1</td><td>市場 forward EPS 分母相對已實現 TTM EPS 的成長橋</td></tr>
      <tr><td>Normalized Growth Multiple</td><td class="num">{ratio_html(growth.get('internal_growth_multiple'))}</td><td>median(2Y, 3Y point-in-time P50)</td><td>正常化估值錨；不因近期股價上漲而提高</td></tr>
      <tr><td>1Y Regime Check</td><td class="num">{pct_html(growth.get('recent_rerating_change')*100 if growth.get('recent_rerating_change') is not None else None)}</td><td>1Y P50 ÷ Normalized Anchor − 1</td><td>{escape(growth.get('recent_rerating_status'))}</td></tr>
      <tr><td>3M/6M Crowding Check</td><td class="num">{pct_html(growth.get('short_crowding_change')*100 if growth.get('short_crowding_change') is not None else None)}</td><td>3M P50 ÷ 6M P50 − 1</td><td>{escape(growth.get('short_crowding_status'))}；只影響風控，不提高 fair</td></tr>
      <tr><td>Conservative Fair Price</td><td class="num">{money_html(conservative.get('conservative_fair_price'))}</td><td>TTM EPS × Conservative P/E</td><td>防守型合理價；不使用 implied forward EPS</td></tr>
      <tr><td>Forward Growth Anchor Price</td><td class="num">{money_html(growth.get('full_growth_anchor_price'))}</td><td>Implied forward EPS × Internal Growth Multiple</td><td>EPS 成長完全被承認的上限情境；不是 base fair</td></tr>
      <tr><td>Growth Gap</td><td class="num">{money_html(growth.get('growth_gap'))}</td><td>Full Growth Anchor Price - Conservative Fair Price</td><td>從保守合理價到完整成長錨點的可爭議上行空間</td></tr>
      <tr><td>Market-implied q</td><td class="num">{pct_html(growth.get('market_implied_q') * 100 if growth.get('market_implied_q') is not None else None)}</td><td>(Current Price - Conservative Fair Price) / Growth Gap</td><td>目前股價已經反映多少 EPS growth gap</td></tr>
    </tbody></table>
    <table><thead><tr><th>q 節點</th><th class="num">價格</th><th>公式</th><th>定義</th></tr></thead><tbody>{q_rows}</tbody></table>
    <p class="small">q 節點保留在 7.2B 作敏感度與位置判讀；7.2D 只把 FES-Lite 決定的單一 q_final 帶入操作階梯，避免同一份報告出現多套操作線。</p>
    {warning}
    """


def fes_lite_table(item: dict) -> str:
    fes = item.get("fes_lite") or {}
    scores = fes.get("scores") or {}
    cap_text = "; ".join(f"{reason}: q ≤ {int(cap*100)}%" for reason, cap in fes.get("q_caps", [])) or "無額外 hard cap"
    detail_rows = "".join(
        f"<tr><td>{escape(row.get('module'))}</td><td class='num'><strong>{fmt(row.get('score'),0)}/2</strong></td>"
        f"<td>{escape(row.get('standard'))}</td><td>{escape(row.get('evidence'))}</td>"
        f"<td>{('<a href=\"' + escape(row.get('source_url')) + '\" target=\"_blank\" rel=\"noopener\">來源</a>') if row.get('source_url') else '規則計算 / 無直接來源'}</td></tr>"
        for row in fes.get("module_details", [])
    )
    evidence_rows = "".join(
        f"<tr><td>{escape(row.get('type'))}</td><td>{escape(row.get('date'))}</td><td>{escape(row.get('description'))}</td><td>{'正向' if row.get('direction','positive') == 'positive' else '負向'}</td><td><a href='{escape(row.get('source_url'))}' target='_blank' rel='noopener'>來源</a></td></tr>"
        for row in fes.get("evidence", [])
    ) or "<tr><td colspan='5'>Missing Data：沒有 180 天內可驗證 evidence，不猜分。</td></tr>"
    warning = f"<p class='warn'>{escape(fes.get('warning'))}</p>" if fes.get("warning") else ""
    return f"""
    <p><strong>批次版基本面證據分數：</strong>FES-Lite = A + B + C + D + E；每模組 0–2 分，合計 0–10 分。每檔最多抓 3 條核心 evidence。</p>
    <table><thead><tr><th>模組</th><th class="num">分數</th><th>判斷標準</th><th>本檔依據</th><th>來源 / 限制</th></tr></thead><tbody>
      {detail_rows}
      <tr class="current-row"><th>合計</th><th class="num">{fmt(fes.get('total'),0)}/10</th><th colspan="3">q_from_FES = {pct_html((fes.get('q_from_fes') or 0) * 100)}；q_final = {pct_html((fes.get('q_final') or 0) * 100)}</th></tr>
    </tbody></table>
    <p class="small"><strong>Hard caps：</strong>{escape(cap_text)}</p>
    <table><thead><tr><th>source type</th><th>source date</th><th>metric / value / reason</th><th>direction</th><th>source link</th></tr></thead><tbody>{evidence_rows}</tbody></table>
    {warning}
    """


def integrated_price_ladder_table(item: dict) -> str:
    ladder = item.get("integrated_price_ladder") or {}
    action = item.get("integrated_action") or {}
    rows = "".join(
        f"<tr><td>{escape(node)}</td><td class='num'>{money_html(price)}</td><td>{escape(formula)}</td><td>{escape(definition)}</td><td>{escape(meaning)}</td></tr>"
        for node, price, formula, definition, meaning in ladder.get("rows", [])
    )
    growth = item.get("growth_pass_through") or {}
    fes = item.get("fes_lite") or {}
    conservative = item.get("conservative_valuation") or {}
    return f"""
    <table><thead><tr><th>Node</th><th class="num">Price</th><th>Formula</th><th>Definition</th><th>Action meaning</th></tr></thead><tbody>{rows}</tbody></table>
    <div class="note"><strong>估值結論：</strong>
    目前價格為 {money_html(item.get('close'))}，相對 Conservative Fair {money_html(conservative.get('conservative_fair_price'))}，
    Market-implied q = {pct_html(growth.get('market_implied_q') * 100 if growth.get('market_implied_q') is not None else None)}，
    代表市場已反映約 {pct(growth.get('market_implied_q') * 100 if growth.get('market_implied_q') is not None else None)} 的 EPS growth gap。
    FES-Lite = {fmt(fes.get('total'),0)}/10，q_final = {pct((fes.get('q_final') or 0) * 100)}。</div>
    <table><tbody>
      <tr><th>新買</th><td>{tag_html(action.get('new_buy') or '資料不足')}</td></tr>
      <tr><th>續抱</th><td>{tag_html(action.get('hold') or '資料不足')}</td></tr>
      <tr><th>停損</th><td>{escape(action.get('stop_line') or '資料不足')}；thesis stop：{escape(action.get('thesis_stop') or '')}</td></tr>
    </tbody></table>
    """


def forward_eps_layer_table(item: dict) -> str:
    layer = item.get("forward_eps_layers") or {}
    fets = item.get("fets") or {}
    ttm_eps = item.get("eps_ttm")
    forward_eps = item.get("valuation_eps")
    pe_proxy = layer.get("historical_forward_pe_proxy")
    rows = [
        ("Conservative fair", ttm_eps, item.get("fairM"), layer.get("conservative_fair"), "不完全相信 forward EPS 成長；以 TTM baseline 對應 2Y/3Y point-in-time 正常化錨"),
        ("Trust-adjusted fair", layer.get("trust_adjusted_eps"), pe_proxy, layer.get("trust_adjusted_fair"), "根據 FETS 只折扣 Forward EPS 與 TTM EPS 的 growth gap"),
        ("Forward Growth Anchor", forward_eps, pe_proxy, layer.get("forward_fair"), "相信 forward EPS 會兌現的 growth anchor；超過後看 RES，不是到價必賣"),
        ("EPS revision bull", layer.get("revised_eps_assumption"), pe_proxy, layer.get("eps_revision_bull"), "情境：Forward EPS 上修 20%，P/E 不擴張"),
        ("EPS + rerating bull", layer.get("revised_eps_assumption"), layer.get("rerating_pe_assumption"), layer.get("eps_rerating_bull"), "情境：Forward EPS 上修 20% 且 P/E 擴張 5%"),
    ]
    rendered = "".join(
        f"<tr><td>{escape(name)}</td><td class='num'>{money_html(eps)}</td><td class='num'>{ratio_html(pe)}</td>"
        f"<td class='num'>{money_html(price)}</td><td>{escape(meaning)}</td></tr>"
        for name, eps, pe, price, meaning in rows
    )
    warning = f"<p class='warn'>{escape(layer.get('warning'))}</p>" if layer.get("warning") else ""
    return f"""
    <p><strong>三層估值：</strong>Conservative fair 回答「只看已實現 TTM 值多少」；Trust-adjusted fair 回答「FETS 支持相信幾成」；Forward Growth Anchor 回答「forward EPS 完全兌現時值多少」。</p>
    <p class="small">Historical forward P/E input：{ratio_html(pe_proxy)}；basis：{escape(layer.get('historical_forward_pe_basis'))}。FETS = {fmt(fets.get('total'),0)}/100，Trust% = {pct_html((fets.get('trust_pct') or 0) * 100)}。</p>
    <table><thead><tr><th>Layer</th><th class="num">EPS</th><th class="num">P/E</th><th class="num">Price</th><th>Meaning</th></tr></thead><tbody>{rendered}</tbody></table>
    {warning}
    """


def entry_stop_framework_table(item: dict) -> str:
    layer = item.get("forward_eps_layers") or {}
    zone_rows = [
        ("< Conservative fair", "便宜，但要確認 thesis"),
        ("Conservative fair - Trust-adjusted fair", "合理偏低 / partial forward EPS priced"),
        ("Trust-adjusted fair - Forward Growth Anchor", "已反映較多 forward EPS"),
        ("> Forward Growth Anchor", "必須看 RES；RES <45 偏 overheat，RES >=75 才是 validated rerating"),
    ]
    zone_rendered = "".join(f"<tr><td>{escape(zone)}</td><td>{escape(meaning)}</td></tr>" for zone, meaning in zone_rows)
    return f"""
    <p class="small">本節只定義 Price Zone 與停損邏輯；所有價格節點均引用 7.2D canonical price_nodes，不在此重算。</p>
    <table><thead><tr><th>價格位置</th><th>意義</th></tr></thead><tbody>{zone_rendered}</tbody></table>
    <p class="note"><strong>目前 Price zone：</strong>{escape(layer.get('price_zone'))}；{escape(layer.get('entry_interpretation'))}。Stop loss 是 thesis review 或風險預算線，不是單純固定百分比。</p>
    """


def score_detail_table(score: dict, title: str, total_label: str) -> str:
    rows = "".join(
        f"<tr><td>{escape(row.get('category'))}</td><td>{escape(row.get('selected_option'))}</td>"
        f"<td class='num'>{fmt(row.get('score'),1)} / {fmt(row.get('max_score'),0)}</td>"
        f"<td>{escape(row.get('evidence_type'))}</td>"
        f"<td>{escape(row.get('source_date'))}</td><td>{escape(row.get('source_title'))}</td>"
        f"<td>{escape(row.get('raw_text_excerpt'))}</td><td>{escape(row.get('rationale'))}</td>"
        f"<td>{('<a href=\"' + escape(row.get('source_url')) + '\" target=\"_blank\" rel=\"noopener\">來源</a>') if row.get('source_url') else 'Missing Data'}</td></tr>"
        for row in score.get("rows", [])
    )
    warning = f"<p class='warn'>{escape(score.get('warning'))}</p>" if score.get("warning") else ""
    extra = (
        f"Public {fmt(score.get('public_score'),1)}/70；Analyst bonus {fmt(score.get('analyst_bonus'),1)}/30；Trust% {pct_html((score.get('trust_pct') or 0) * 100)}"
        if "trust_pct" in score
        else f"Status：{escape(score.get('status'))}"
    )
    return f"""
    <p><strong>{escape(title)}：</strong>{total_label} = {fmt(score.get('total'),1)}/100；{extra}；evidence completeness {fmt(score.get('evidence_completeness'),0)}/{fmt(score.get('evidence_possible') or len(score.get('rows', [])),0)}；confidence {escape(score.get('confidence'))}。</p>
    <table><thead><tr><th>category</th><th>selected_option</th><th class="num">score</th><th>evidence_type</th><th>source_date</th><th>source_title</th><th>raw_text_excerpt</th><th>rationale</th><th>source_url</th></tr></thead><tbody>{rows}</tbody></table>
    {warning}
    """


def fets_table(item: dict) -> str:
    layer = item.get("forward_eps_layers") or {}
    fets = item.get("fets") or {}
    summary = f"""
    <table><tbody>
      <tr><th>Trust-adjusted EPS</th><td class="num">{money_html(layer.get('trust_adjusted_eps'))}</td><td>TTM EPS + Trust% × (Forward EPS - TTM EPS)</td></tr>
      <tr><th>Trust-adjusted fair</th><td class="num">{money_html(layer.get('trust_adjusted_fair'))}</td><td>Trust-adjusted EPS × historical forward P/E proxy</td></tr>
    </tbody></table>
    """
    return score_detail_table(fets, "FETS：Forward EPS Trust Score", "FETS") + summary


def res_table(item: dict) -> str:
    layer = item.get("forward_eps_layers") or {}
    res = item.get("res") or {}
    note = (
        "目前價格高於 Forward Growth Anchor，RES 進入決策。"
        if item.get("close") and layer.get("forward_fair") and item["close"] > layer["forward_fair"]
        else "目前價格未高於 Forward Growth Anchor；RES 先作監控，不作 overheat/rerating 的決定性結論。"
    )
    return f"<p class='note'>{escape(note)}</p>" + score_detail_table(res, "RES：Rerating Evidence Score", "RES")


def render_valuation_tables(item: dict) -> str:
    return (
        valuation_breakdown(item)
        + scenario_matrix(item)
        + f"<h3>7.2A Peer Valuation Sanity Check：同業估值限制與品質</h3>{peer_sanity_table(item)}"
        + f"<h3>7.2B Growth Pass-through Valuation：EPS 成長反映模型</h3>{growth_pass_through_table(item)}"
        + f"<h3>7.2C FES-Lite：批次版基本面證據分數</h3>{fes_lite_table(item)}"
        + f"<h3>7.2D Integrated Price Ladder：整合價格階梯與操作規則</h3>{integrated_price_ladder_table(item)}"
        + f"<h3>7.2E EPS Valuation Layer：Conservative / Trust-adjusted / Forward Fair</h3>{forward_eps_layer_table(item)}"
        + f"<h3>7.2F FETS：Forward EPS Trust Score</h3>{fets_table(item)}"
        + f"<h3>7.2G RES：Rerating Evidence Score</h3>{res_table(item)}"
        + f"<h3>7.2H Entry / Stop / Price Zone</h3>{entry_stop_framework_table(item)}"
    )


def rerating_model_table(item: dict) -> str:
    model = item.get("rerating_model") or {}
    metric = item.get("valuation_metric") or "P/E"
    denominator = item.get("valuation_denominator")
    denominator_label = "Revenue/share" if metric == "P/S" else "EPS"
    current_metric_label = "現行 P/S" if metric == "P/S" else "現行 Forward P/E"
    gates = model.get("gates") or {}
    gate_labels = {
        "positive_eps": f"{denominator_label} 分母可用",
        "recent_above_traditional": "3M、6M P50 均高於傳統 Fair",
        "six_month_persistence": "至少約 6 個月、80% 價格資料",
        "fundamental_evidence": "至少一項有來源基本面證據",
        "effective_anchor_above_fair": "近期有效錨點高於傳統 Fair",
    }
    gate_rows = "".join(
        f"<tr><td>{escape(gate_labels[key])}</td><td>{tag_html('通過' if passed else '未通過')}</td></tr>"
        for key, passed in gates.items()
    )
    evidence_rows = "".join(
        f"<li><strong>{escape(row.get('level','C'))} 級／"
        f"{'正向' if row.get('direction','positive') == 'positive' else '負向'}</strong> "
        f"{escape(row.get('type'))}：{escape(row.get('description'))}（{escape(row.get('date'))}；"
        f"<a href='{escape(row.get('source_url'))}' target='_blank' rel='noopener'>來源</a>；"
        f"本次貢獻 {fmt(row.get('score_contribution'),1)} 分；{escape(row.get('verification'))}）</li>"
        for row in model.get("evidence", [])
    ) or "<li>目前沒有符合格式且已驗證的基本面證據；股價上漲不計分。</li>"
    base_eps = item.get("valuation_eps")
    base_denominator = denominator
    bear_denominator = base_denominator * 0.90 if base_denominator else None
    bull_denominator = base_denominator * 1.10 if base_denominator else None
    ladder = [
        ("Bear Stress", bear_denominator, item.get("stressM"), "基本面受壓＋傳統 Stress"),
        ("Value Entry", base_denominator, item.get("entryM"), "不依賴 Rerating 的價值型研究區"),
        ("Traditional Fair", base_denominator, model.get("traditional_fair"), "傳統內在合理價錨"),
        ("Rerating Fair", base_denominator, model.get("adjusted_fair"), "固定 50% 混合後合理價"),
        ("Regime P75", base_denominator, model.get("regime_p75"), "近期市場常態上緣；不是內在價值"),
        ("Bull P75", bull_denominator, model.get("regime_p75"), f"{denominator_label} 上修 10% 後的強勢情境"),
        ("Overheat P90", base_denominator, model.get("overheat_p90"), f"現行 {denominator_label} 下的近期極端線"),
        ("Bull Overheat", bull_denominator, model.get("overheat_p90"), f"{denominator_label} 上修 10% 後的極端情境"),
    ]
    ladder_rows = "".join(
        f"<tr><td>{label}</td><td class='num'>{money_html(den)}</td><td class='num'>{ratio_html(multiple)}</td>"
        f"<td class='num'>{money_html(den * multiple if den and multiple else None)}</td><td>{meaning}</td></tr>"
        for label, den, multiple, meaning in ladder
    )
    return f"""
    <h4>Rerating Model（傳統合理價與市場 regime 分離）</h4>
    <p><strong>模型：</strong>{tag_html('已計算' if model.get('active') else 'P/E 模型不適用')}；
    <strong>Rerating 成立度：</strong>{pct_html((model.get('activation_likelihood') or 0) * 100)}；
    <strong>目前分類：</strong>{escape(model.get('classification'))}</p>
    <table><thead><tr><th>項目</th><th class="num">倍數</th><th class="num">對應價格</th><th>用途</th></tr></thead><tbody>
      <tr><td>傳統 Fair</td><td class="num">{ratio_html(model.get('traditional_fair'))}</td><td class="num">{money_html(item.get('fair'))}</td><td>主要 Base fair／內在合理價錨</td></tr>
      <tr><td>近期原始錨點</td><td class="num">{ratio_html(model.get('recent_raw_p50'))}</td><td class="num">{money_html(model.get('recent_raw_p50') * denominator if model.get('recent_raw_p50') and denominator else None)}</td><td>median(3M、6M {escape(metric)} P50)</td></tr>
      <tr><td>近期有效錨點</td><td class="num">{ratio_html(model.get('recent_effective'))}</td><td class="num">{money_html(model.get('recent_effective') * denominator if model.get('recent_effective') and denominator else None)}</td><td>min(近期 P50, 1Y {escape(metric)} P90)</td></tr>
      <tr><td>Rerating Fair（固定 50%）</td><td class="num">{ratio_html(model.get('adjusted_fair'))}</td><td class="num">{money_html(model.get('adjusted_fair_price'))}</td><td>傳統 Fair × 50% + 近期有效錨點 × 50%；成立度不參與此公式</td></tr>
      <tr><td>近期市場常態上緣</td><td class="num">{ratio_html(model.get('regime_p75'))}</td><td class="num">{money_html(model.get('regime_p75_price'))}</td><td>median(3M、6M {escape(metric)} P75)；不是內在合理價</td></tr>
      <tr><td>Overheat P90</td><td class="num">{ratio_html(model.get('overheat_p90'))}</td><td class="num">{money_html(model.get('overheat_price'))}</td><td>median(3M、6M {escape(metric)} P90)；高於此線才判近期真正過熱</td></tr>
    </tbody></table>
    <p class="small"><strong>成立度拆解：</strong>市場 regime {fmt(model.get('market_score'),0)}/50；
    已確認基本面 {fmt(model.get('confirmed_score'),1)}/30；
    早期／領先訊號 {fmt(model.get('early_score'),1)}/20；
    合計 {fmt(model.get('activation_score'),0)}/100。
    這是規則型成立度，不是經歷史校準的真實發生機率。Rerating Fair 的混合權重固定為 50%，不隨成立度改變。</p>
    <table><thead><tr><th>成立度條件</th><th>結果</th></tr></thead><tbody>{gate_rows}</tbody></table>
    <ul>{evidence_rows}</ul>
    <h4>Rerating 價格階梯</h4>
    <p><strong>目前價格：{money_html(item.get('close'))}</strong>；
    {escape(current_metric_label)}：{ratio_html(item.get('current_implied_multiple'))}；
    位置：{escape(model.get('classification'))}。</p>
    <table><thead><tr><th>節點</th><th class="num">{escape(denominator_label)} 口徑</th><th class="num">倍數</th><th class="num">價格</th><th>意義</th></tr></thead><tbody>{ladder_rows}</tbody></table>
    """


def scenario_matrix(item: dict) -> str:
    rows = []
    metric = item.get("valuation_metric") or "P/E"
    denominator = item.get("valuation_denominator")
    denominator_label = "Revenue/share" if metric == "P/S" else "EPS"
    multiple_label = "現價 implied P/S" if metric == "P/S" else "現價 implied P/E"
    for name, den, row_class, tone, description in [
        ("Bear", denominator * 0.9 if denominator else None, "risk-row", "risk-text", "估計下修或市場降 multiple"),
        ("Base", denominator, "current-row", "key", "本報估值基準"),
        ("Bull", denominator * 1.1 if denominator else None, "upper-row", "watch-text", "需 EPS/revenue/margin/backlog 上修"),
    ]:
        rows.append(
            f"""<tr class="{row_class}"><td>{name}</td><td class="num">{money_html(den,tone)}</td><td class="num">{ratio_html(item['close']/den if den and item.get('close') else None,tone)}</td>
            <td class="num">{money_html(den*item['stressM'] if den else None,'risk-text')}</td><td class="num">{money_html(den*item['entryM'] if den else None,'positive')}</td>
            <td class="num">{money_html(den*item['fairM'] if den else None)}</td><td class="num">{money_html(den*item['upperM'] if den else None,'watch-text')}</td><td>{description}</td></tr>"""
        )
    return f"""
    <h4>基本面 {escape(denominator_label)} 敏感度表（不含 Rerating）</h4>
    <p><strong>目前價格：{money_html(item.get('close'))}</strong>；
    相對傳統估值位置：{tag_html(item['priceScenario'])}。本表只改變估值分母，不假設近期 multiple 擴張。</p>
    <table><thead><tr><th>情境</th><th class="num">{escape(denominator_label)} 假設</th><th class="num">{escape(multiple_label)}</th><th class="num">Stress</th><th class="num">Entry</th><th class="num">Fair</th><th class="num">Upper</th><th>說明</th></tr></thead><tbody>{table_rows(rows)}</tbody></table>
    """


def target_ladder(item: dict) -> str:
    conservative = item.get("conservative_valuation") or {}
    growth = item.get("growth_pass_through") or {}
    layer = item.get("forward_eps_layers") or {}
    fes = item.get("fes_lite") or {}
    q_final = fes.get("q_final")
    selected_growth = (
        conservative.get("conservative_fair_price") + q_final * growth.get("growth_gap")
        if q_final is not None and conservative.get("conservative_fair_price") is not None and growth.get("growth_gap") is not None
        else None
    )
    rows = [
        ("Stress / thesis review", layer.get("stress_low") or conservative.get("stress_price"), "risk-text", "Conservative fair × 0.76–0.78；低價不是自動買點，先檢查 thesis。"),
        ("Conservative entry", layer.get("conservative_entry") or conservative.get("entry_price"), "positive", "Conservative fair × 85%；只依靠已實現 TTM 的研究價。"),
        ("Conservative fair", layer.get("conservative_fair") or conservative.get("conservative_fair_price"), "key", "不完全相信 forward EPS 成長時的防守合理價。"),
        ("Selected Growth Fair", selected_growth, "watch-text", f"Conservative fair + q_final {pct((q_final or 0)*100)} × Growth Gap；由 FES-Lite 決定。"),
        ("Trust-adjusted fair", layer.get("trust_adjusted_fair"), "watch-text", "FETS 折扣後的 forward growth fair。"),
        ("Forward Growth Anchor", layer.get("forward_fair"), "watch-text", "forward EPS 完全兌現情境；超過後看 RES。"),
        ("Current price", item.get("close"), "", f"Price Zone：{layer.get('price_zone') or 'N/A'}。"),
    ]
    rendered = []
    for label, value, class_name, operation in rows:
        gain = change(value, item.get("close")) if item.get("close") else None
        rendered.append(
            f"""<tr><td>{label}</td><td class="num">{money_html(value,class_name)}</td><td class="num">{pct_html(gain)}</td><td>{escape(operation)}</td></tr>"""
        )
    return f"""
    <p><strong>基準日目前價格：{money_html(item.get('close'))}</strong></p>
    <p class="small">第 8 章只摘要主階梯；完整 q25/q35/q50/q65/q75 放在 7.2B，完整操作規則放在 7.2H，避免重複出現兩套進場價。</p>
    <table><thead><tr><th>價格區</th><th class="num">價格</th><th class="num">相對現價</th><th>操作 / 定義</th></tr></thead><tbody>{table_rows(rendered)}</tbody></table>
    """


def price_position_section(item: dict) -> str:
    return f"""
    <table><tbody>
      <tr><th>{escape(item['basis_date'])} 收盤</th><td class="num">{money_html(item['close'])}</td></tr>
      <tr><th>日漲跌幅</th><td class="num">{pct_html(item['day_change'])}</td></tr>
      <tr><th>成交量 / 相對量</th><td class="num"><strong>{fmt(item['volume'],0)}</strong> / {ratio_html(item['rvol'])}</td></tr>
      <tr><th>5D / 20D / 60D</th><td class="num">{pct_html(item['d5'])} / {pct_html(item['d20'])} / {pct_html(item['d60'])}</td></tr>
      <tr><th>50DMA / 200DMA</th><td class="num">{escape(item.get('50-Day Moving Average'))} / {escape(item.get('200-Day Moving Average'))}</td></tr>
      <tr><th>52 週漲跌幅 / 平均目標價</th><td class="num">{escape(item.get('52-Week Price Change'))} / {escape(item.get('Price Target'))}</td></tr>
      <tr><th>正式價格品質</th><td>{escape(item['price_quality'])}</td></tr>
    </tbody></table>
    """


def final_action_section(item: dict) -> str:
    conservative = item.get("conservative_valuation") or {}
    growth = item.get("growth_pass_through") or {}
    fes = item.get("fes_lite") or {}
    fets = item.get("fets") or {}
    res = item.get("res") or {}
    layer = item.get("forward_eps_layers") or {}
    action = item.get("integrated_action") or {}
    evidence = fes.get("evidence") or []
    support = evidence[0].get("description") if evidence else "Missing Data"
    risk = item.get("bear") or "Missing Data"
    stress_range = (
        f"{money(layer.get('stress_low'))} - {money(layer.get('stress_high'))}"
        if layer.get("stress_low") is not None and layer.get("stress_high") is not None
        else "Missing Data"
    )
    return f"""
    <div class="note"><strong>估值結論：</strong>
    Conservative fair = {money_html(layer.get('conservative_fair') or conservative.get('conservative_fair_price'))}；
    Trust-adjusted fair = {money_html(layer.get('trust_adjusted_fair'))}；
    Forward Growth Anchor = {money_html(layer.get('forward_fair'))}；
    Current price = {money_html(item.get('close'))}。
    Price zone：{escape(layer.get('price_zone'))}。
    Market-implied q = {pct_html(growth.get('market_implied_q') * 100 if growth.get('market_implied_q') is not None else None)}，
    代表市場已反映約 {pct(growth.get('market_implied_q') * 100 if growth.get('market_implied_q') is not None else None)} 的 EPS growth gap。</div>
    <div class="note"><strong>基本面證據：</strong>
    FES-Lite = {fmt(fes.get('total'),0)}/10，q_final = {pct((fes.get('q_final') or 0) * 100)}；
    FETS = {fmt(fets.get('total'),1)}/100，Trust% = {pct((fets.get('trust_pct') or 0) * 100)}；
    RES = {fmt(res.get('total'),1)}/100，rerating / overheat judgment = {escape(res.get('status'))}。
    主要支持證據為：{escape(support)}。
    主要缺失或風險為：{escape(risk)}。</div>
    <table><tbody>
      <tr><th>最後操作建議</th><td>{tag_html(action.get('new_buy') or item['decision'])}</td></tr>
      <tr><th>Entry interpretation</th><td>{escape(layer.get('entry_interpretation'))}；Conservative entry {money_html(layer.get('conservative_entry'))}；Forward entry {money_html(layer.get('forward_entry'))}。</td></tr>
      <tr><th>Stop / thesis review line</th><td>Stress line {escape(stress_range)}；price stop：{escape(action.get('stop_line') or '資料不足')}；thesis stop：{escape(action.get('thesis_stop') or '')}</td></tr>
      <tr><th>執行語句</th><td><strong>{escape(item['action'])}</strong>。目前正式收盤 {money_html(item['close'])}，對第一研究價 {money_html(item['entry'],'positive')} 的距離為 {pct_html(item['currentToEntry'])}。</td></tr>
      <tr><th>新買 / 續抱</th><td>新買：{escape(action.get('new_buy') or '資料不足')}；續抱：{escape(action.get('hold') or '資料不足')}。</td></tr>
      <tr><th>部位閘門</th><td>本批 {len(TICKERS)} 檔是研究清單，不是同時買進清單；在 45,000 美元軟上限與高 beta 集中風險下，新增交易需小量、分批、先看市場 regime。</td></tr>
      <tr><th>確認條件</th><td>只有在 thesis intact、同業未明顯轉弱、估計修正未下修，且價格接近 Entry/Stress 區時，才重新評估進場或加碼。</td></tr>
    </tbody></table>
    """


def stop_take_profit_section(item: dict) -> str:
    nodes = item.get("price_nodes") or {}
    return f"""
    <p class="small">本節只列 trigger，價格引用 7.2D canonical price_nodes，不另建第二套目標價。</p>
    <table><thead><tr><th>觸發區</th><th class="num">7.2D 節點</th><th>先判斷什麼</th><th>動作</th></tr></thead><tbody>
      <tr class="risk-row"><td>跌破 Bear Stress</td><td class="num">{money_html(nodes.get('bear_stress'),'risk-text')}</td><td>是否只是大盤/類股同步下跌，或是公司 EPS、margin、訂單、客戶、監管出現 thesis damaged。</td><td>不是機械停損；若 thesis damaged 則減碼/退出，若 thesis intact 則觀察 2-3 日是否收復。</td></tr>
      <tr class="entry-row"><td>接近 Value Entry</td><td class="num">{money_html(nodes.get('value_entry'),'positive')}</td><td>市場風險是否可承擔、同業是否穩定、下一季驗證點是否未惡化。</td><td>只允許小量或分批，不用攤平放大壓力。</td></tr>
      <tr><td>接近 Conservative Fair</td><td class="num">{money_html(nodes.get('conservative_fair'),'key')}</td><td>EPS/FCF/backlog 是否足以支撐 fair multiple。</td><td>續抱或部分停利檢查，不把 fair 當新增追價點。</td></tr>
      <tr class="upper-row"><td>接近 Selected Growth Fair</td><td class="num">{money_html(nodes.get('selected_growth_fair'),'watch-text')}</td><td>FES/FETS 是否繼續改善。</td><td>若沒有新證據，進入停利/減碼檢查。</td></tr>
      <tr class="upper-row"><td>超過 Forward Growth Anchor</td><td class="num">{money_html(nodes.get('forward_growth_anchor'),'watch-text')}</td><td>RES 是否 >=75。</td><td>若 RES <75，減碼檢查；若 thesis damaged 優先退出。</td></tr>
    </tbody></table>
    <p class="small">模擬比例：Bear Stress 對 Value Entry {pct_html(item['stopPct'])}；Conservative Fair 對 Value Entry {pct_html(item['target1Pct'])}；Selected Growth Fair 對 Value Entry {pct_html(item['target2Pct'])}。這些是風控劇本，不是自動委託價格。</p>
    """


def quality_financial_risk_section(item: dict) -> str:
    return f"""
    <p>{escape(item['company'])} 的品質判斷要同時看成長、margin、FCF、槓桿與估計修正；Forward P/E 看起來便宜時，仍要確認 EPS 分母是否是 adjusted/normalized。</p>
    <table><tbody>
      <tr><th>毛利率 / 營益率</th><td class="num">{escape(item.get('Gross Margin'))} / {escape(item.get('Operating Margin'))}</td></tr>
      <tr><th>FCF margin / P/FCF</th><td class="num">{escape(item.get('FCF Margin'))} / {escape(item.get('P/FCF Ratio'))}</td></tr>
      <tr><th>EV/EBITDA / Debt-to-Equity</th><td class="num">{escape(item.get('EV / EBITDA'))} / {escape(item.get('Debt / Equity'))}</td></tr>
      <tr class="watch-row"><th>財報風險</th><td>Valuation EPS {money_html(item['valuation_eps'])}（{escape(item['valuation_eps_basis'])}）必須用下一季 EPS、guidance、margin、FCF、backlog/訂單或需求證據驗證；若只靠 multiple 下降，不能直接解讀為便宜。</td></tr>
    </tbody></table>
    """


def multibagger_analysis_section(item: dict) -> str:
    analysis = GEV_MULTIBAGGER if item["ticker"] == "GEV" else None
    if analysis is None:
        return generic_multibagger_analysis_section(item)

    signal_rows = []
    for signal, stage, direction, source, quality, lead, verified in analysis["signals"]:
        if "同快照估值" in source:
            source_url = item["valuation_snapshot_url"]
            evidence_type = "直接：市場定價"
            source_nature = "保存快照"
        else:
            source_url = analysis["sources"][0][1]
            evidence_type = "直接：公司營運"
            source_nature = "公司原始揭露"
        signal_rows.append(
            f"<tr><td>{escape(signal)}</td><td>{escape(stage)}</td><td>{tag_html(direction)}</td>"
            f"<td>{escape(evidence_type)}</td><td>{escape(source_nature)}</td>"
            f"<td><a href='{escape(source_url)}'>{escape(source)}</a></td>"
            f"<td class='num'>{escape(quality)}</td><td>{escape(lead)}</td><td>{escape(verified)}</td></tr>"
        )
    indirect_date, indirect_signal, indirect_url = INDIRECT_SOURCES["GEV"]
    signal_rows.append(
        f"<tr><td>{escape(indirect_signal)}</td><td>Stage 0/1</td><td>{tag_html('正向')}</td>"
        f"<td>間接：產業需求</td><td>獨立產業鏈</td>"
        f"<td><a href='{escape(indirect_url)}'>PJM／電力產業交叉驗證（{indirect_date}）</a></td>"
        f"<td class='num'>C</td><td>6–36 月</td><td>與 GEV 公司揭露分屬不同證據鏈</td></tr>"
    )
    signal_rows = "".join(signal_rows)
    fundamental_total = sum(row[1] for row in analysis["fundamental_scores"])
    fundamental_max = sum(row[2] for row in analysis["fundamental_scores"])
    fundamental_rows = "".join(
        f"<tr><td>{escape(label)}</td><td class='num'><strong>{score}/{maximum}</strong></td><td>{escape(reason)}</td></tr>"
        for label, score, maximum, reason in analysis["fundamental_scores"]
    )
    price_total = sum(row[1] for row in analysis["price_scores"])
    price_max = sum(row[2] for row in analysis["price_scores"])
    price_rows = "".join(
        f"<tr><td>{escape(label)}</td><td class='num'><strong>{score}/{maximum}</strong></td><td>{escape(reason)}</td></tr>"
        for label, score, maximum, reason in analysis["price_scores"]
    )
    scenario_rows = "".join(
        f"<tr class=\"{'risk-row' if name == 'Bear' else 'upper-row' if name in {'Bull', 'Extreme Bull'} else 'current-row'}\">"
        f"<td>{escape(name)}</td><td>{escape(year)}</td><td class='num'>${revenue:.1f}B</td><td>{escape(margin)}</td>"
        f"<td class='num'>${eps:.2f}</td><td class='num'>{multiple:.1f}x</td><td class='num'>{money_html(target)}</td>"
        f"<td class='num'><strong>{price_multiple:.2f}x</strong></td><td class='num'>{probability}%</td><td>{escape(condition)}</td></tr>"
        for name, year, revenue, margin, eps, multiple, target, price_multiple, probability, condition in analysis["scenarios"]
    )
    source_links = "".join(
        f'<li><a href="{escape(url)}">{escape(label)}</a></li>'
        for label, url in analysis["sources"]
    )
    return f"""
    <div class="note"><strong>一句話結論：</strong>{escape(analysis['conclusion'])}</div>
    <table><tbody>
      <tr><th>啟動原因</th><td>{BASIS_DATE} 收盤 {money_html(item['close'])} 已高於 Base fair {money_html(item['fair'])}，且 Forward P/E {ratio_html(item['fpe'])} 位於高預期區。</td></tr>
      <tr><th>主要／次要階段</th><td><strong>{escape(analysis['primary_stage'])}</strong>；同時進入 <strong>{escape(analysis['secondary_stage'])}</strong>。</td></tr>
      <tr><th>估值口徑</th><td>同日快照 Forward P/E {ratio_html(item['fpe'])}；唯一 valuation EPS {money_html(item['valuation_eps'])}（{escape(item['valuation_eps_basis'])}）。</td></tr>
    </tbody></table>

    <h3>12.1.1 訊號、來源與品質</h3>
    <table><thead><tr><th>訊號</th><th>階段</th><th>方向</th><th>直接／間接</th><th>來源性質</th><th>來源與日期</th><th class="num">品質</th><th>領先期</th><th>驗證</th></tr></thead><tbody>{signal_rows}</tbody></table>

    <h3>12.1.2 多頭與反向證據</h3>
    <div class="two-col">
      <div class="note"><strong>多頭：</strong>100GW gas backlog/slot commitments、Electrification book-to-bill 約 2.5x、總 backlog $163B、Power/Electrification margin 擴張、2026 guidance 上修。</div>
      <div class="warn"><strong>反向：</strong>Wind Q1 EBITDA -$382M；Q1 FCF 含顯著 working-capital benefit；基準日 Forward P/E {ratio_html(item['fpe'])} 已要求持續超預期；產能擴充與 Prolec 整合可能壓 execution；AI power 交易高度擁擠。</div>
    </div>

    <h3>12.1.3 倍數成長雙分數</h3>
    <div class="two-col">
      <table><thead><tr><th>基本面延展</th><th class="num">分數</th><th>理由</th></tr></thead><tbody>{fundamental_rows}<tr class="current-row"><th>合計</th><th class="num">{fundamental_total}/{fundamental_max}</th><th>基本面具長週期延展性</th></tr></tbody></table>
      <table><thead><tr><th>現價報酬風險</th><th class="num">分數</th><th>理由</th></tr></thead><tbody>{price_rows}<tr class="risk-row"><th>合計</th><th class="num">{price_total}/{price_max}</th><th>價格已反映大量 Bull 情境</th></tr></tbody></table>
    </div>
    {score_interpretation_html(fundamental_total, price_total)}

    <h3>12.1.4 Bear / Base / Bull 倍數模型</h3>
    <p><strong>基準日目前價格：{money_html(item.get('close'))}</strong></p>
    <p class="small">模型採 Revenue × normalized net margin ÷ diluted shares × terminal P/E。EPS、margin 與終值倍數為研究假設，不是公司 guidance；Extreme Bull 不納入主要機率加權結論。</p>
    <table><thead><tr><th>情境</th><th>目標年</th><th class="num">Revenue</th><th>淨利率</th><th class="num">EPS</th><th class="num">終值 P/E</th><th class="num">目標價</th><th class="num">現價倍數</th><th class="num">機率</th><th>必要條件／失效訊號</th></tr></thead><tbody>{scenario_rows}</tbody></table>
    <p><strong>機率加權倍數：</strong>{analysis['weighted_multiple']:.2f}x。Bear / Base / Bull 約 {analysis['scenarios'][0][7]:.2f}x / {analysis['scenarios'][1][7]:.2f}x / {analysis['scenarios'][2][7]:.2f}x。要超過 2x，需接近 Extreme Bull，不能作主要持有理由。</p>

    <h3>12.1.5 最終判斷與重評</h3>
    <table><tbody>
      <tr><th>最可能結果</th><td>3–4 年約 1.1–1.6x；Base 不屬倍數股，2x 以上屬低機率壓力測試。</td></tr>
      <tr><th>信心</th><td>{escape(analysis['confidence'])}</td></tr>
      <tr><th>下一固定重評</th><td>{escape(analysis['recheck'])}</td></tr>
      <tr><th>提前重評</th><td>{escape(analysis['early_triggers'])}</td></tr>
      <tr><th>最終操作標籤</th><td>{tag_html(analysis['final_label'])}</td></tr>
    </tbody></table>
    <ul>{source_links}</ul>
    """


def score_interpretation_html(fundamental_total: int, price_total: int) -> str:
    if fundamental_total >= 56:
        fundamental_band = "高延展（56–70）：需求、護城河、訂單與財務多數已驗證"
    elif fundamental_total >= 42:
        fundamental_band = "中高延展（42–55）：成長論點合理，但仍有一至兩條證據鏈待補"
    elif fundamental_total >= 28:
        fundamental_band = "未確立（28–41）：產業方向可能成立，公司捕獲能力尚未證明"
    else:
        fundamental_band = "偏弱（0–27）：缺乏可持續成長或財務驗證"
    if price_total >= 23:
        price_band = "現價具吸引力（23–30）：Base/Bull 尚未充分定價且有下檔支撐"
    elif price_total >= 16:
        price_band = "中性（16–22）：仍有空間，但需等待估計上修或更好價格"
    elif price_total >= 9:
        price_band = "要求偏高（9–15）：好公司不等於現價有好報酬"
    else:
        price_band = "過熱／低容錯（0–8）：市場已反映大量 Bull 情境"
    return f"""
    <table><tbody>
      <tr><th>基本面分解讀</th><td><strong>{escape(fundamental_band)}</strong></td></tr>
      <tr><th>現價分解讀</th><td><strong>{escape(price_band)}</strong></td></tr>
      <tr><th>組合判讀</th><td>基本面高、現價低＝可留核心倉但不代表可追價；基本面與現價都高才是較佳新增研究區；基本面低但現價高只代表便宜，不代表 thesis 成立。</td></tr>
    </tbody></table>
    """


def category_score_rows(item: dict, fundamental_total: int, price_total: int) -> tuple[str, str]:
    """Allocate transparent category scores; totals remain separately interpretable."""
    deep = item.get("memo_depth") == "deep"
    financial = item.get("Operating Margin") not in {None, "n/a"} and item.get("FCF Margin") not in {None, "n/a"}
    fundamental = [
        ("需求不可逆性與市場空間", 10 if deep else 8, 12, item["catalyst"], "產業需求仍須以客戶 CapEx／政策／終端量交叉驗證"),
        ("供給瓶頸與擴產難度", 7 if deep else 5, 10, "檢查交期、產能、認證、良率與供應商擴產", "沒有可量化交期或產能時不得給滿分"),
        ("技術、認證與客戶護城河", 8 if deep else 6, 10, item["business"], "需確認切換成本、認證週期與替代方案"),
        ("客戶承諾、訂單與 backlog", 6 if deep else 5, 10, "以合約、backlog、RPO、預付款或 capacity reservation 為優先", "僅管理層需求敘事不等於客戶承諾"),
        ("ASP、margin 與營運槓桿", 7 if financial else 5, 10, f"Operating margin {item.get('Operating Margin') or '未取得'}；FCF margin {item.get('FCF Margin') or '未取得'}", "margin 未連續驗證或現金流落後時扣分"),
        ("營收、EPS 與 FCF 驗證", 8 if financial else 5, 12, f"valuation EPS {fmt(item.get('valuation_eps'))}；下一季需用 guidance/FCF 驗證", "缺少公司一手季度橋與 consensus revision 歷史"),
        ("市占率與競爭優勢", 4 if deep else 3, 6, item["thesis"], "競爭者擴產、客戶自製或商品化會使分數下降"),
    ]
    raw_total = sum(row[1] for row in fundamental)
    adjustment = fundamental_total - raw_total
    direction = 1 if adjustment > 0 else -1
    while adjustment:
        changed = False
        for index in range(len(fundamental) - 1, -1, -1):
            label, score, maximum, positive, negative = fundamental[index]
            next_score = score + direction
            if 0 <= next_score <= maximum:
                fundamental[index] = (
                    label, next_score, maximum, positive, negative
                )
                adjustment -= direction
                changed = True
                if adjustment == 0:
                    break
        if not changed:
            break
    price = item.get("close") or 0
    fair = item.get("fair") or price
    price_categories = [
        ("現價尚未反映 Base/Bull", min(12, max(0, round(price_total * 12 / 30))), 12, f"現價 {money(price)}；Base fair {money(fair)}", "現價高於 fair 或接近 upper 時扣分"),
        ("估值下檔保護與 FCF 支撐", min(8, max(0, round(price_total * 8 / 30))), 8, f"Forward P/E {ratio(item.get('fpe'))}；P/FCF {item.get('P/FCF Ratio') or '未取得'}", "高倍數且 FCF yield 低時，下檔保護有限"),
        ("稀釋、淨負債與資本需求", min(5, max(0, round(price_total * 5 / 30))), 5, f"Debt/Equity {item.get('Debt / Equity') or '未取得'}", "SBC、併購、擴產與負債需求會侵蝕每股價值"),
    ]
    used = sum(row[1] for row in price_categories)
    price_categories.append(("擁擠度、預期門檻與時程", max(0, min(5, price_total - used)), 5, f"60D {pct(item.get('d60'))}；Forward P/E {ratio(item.get('fpe'))}", "股價漲幅領先 EPS/FCF 上修、利多鈍化時扣分"))
    fundamental_rows = "".join(
        f"<tr><td>{escape(label)}</td><td class='num'><strong>{score}/{maximum}</strong></td><td>{escape(positive)}</td><td>{escape(negative)}</td></tr>"
        for label, score, maximum, positive, negative in fundamental
    )
    price_rows = "".join(
        f"<tr><td>{escape(label)}</td><td class='num'><strong>{score}/{maximum}</strong></td><td>{escape(positive)}</td><td>{escape(negative)}</td></tr>"
        for label, score, maximum, positive, negative in price_categories
    )
    return fundamental_rows, price_rows


def generic_multibagger_analysis_section(item: dict) -> str:
    """Render a complete, conservative 12.1 for every watchlist ticker.

    This deliberately distinguishes report-basis market/valuation evidence
    from company-primary evidence that has not yet been collected. Missing
    primary evidence lowers confidence; it never removes the section.
    """
    price = item.get("close") or 0
    fair = item.get("fair") or price
    upper = item.get("upper") or fair
    fpe = item.get("fpe")
    op_margin = item.get("Operating Margin") or "未取得"
    fcf_margin = item.get("FCF Margin") or "未取得"
    d60 = item.get("d60")
    stage3 = bool(price >= fair or (fpe is not None and fpe >= 35))
    primary_stage = "Stage 2：財務驗證待深化"
    secondary_stage = "Stage 3：估值／市場定價" if stage3 else "Stage 1：商業化證據待補"

    fundamental_total = 46 if item.get("memo_depth") == "deep" else 41
    if op_margin != "未取得":
        fundamental_total += 3
    if fcf_margin != "未取得":
        fundamental_total += 3
    fundamental_total = min(fundamental_total, 56)

    if price >= upper:
        price_total = 6
    elif price >= fair:
        price_total = 10
    elif price >= (item.get("entry") or price):
        price_total = 16
    else:
        price_total = 21
    weighted_total = fundamental_total + price_total
    fundamental_rows, price_rows = category_score_rows(
        item, fundamental_total, price_total
    )

    base_growth = 0.12 if item.get("memo_depth") == "deep" else 0.09
    bull_growth = 0.20 if item.get("memo_depth") == "deep" else 0.16
    eps = item.get("valuation_eps") or 0
    revenue_ttm = item.get("revenue_ttm")
    margin_ttm = item.get("profit_margin_ttm")
    scenarios = [
        ("Bear", 2028, -0.03, eps * 0.85, item.get("stressM"), 35, "估計下修、需求/訂單或 margin 轉弱，並發生 de-rating"),
        ("Base", 2029, base_growth, eps * ((1 + base_growth) ** 3), item.get("fairM"), 45, "核心催化逐步兌現，但沒有超額市占或估值擴張"),
        ("Bull", 2030, bull_growth, eps * ((1 + bull_growth) ** 4), item.get("upperM"), 20, "需求、供給限制與公司財務三端均由一手證據確認"),
    ]
    scenario_rows = []
    weighted_multiple = 0.0
    scenario_multiples = {}
    for name, year, revenue_cagr, future_eps, terminal_pe, probability, condition in scenarios:
        years = year - 2026
        future_revenue = (
            revenue_ttm * ((1 + revenue_cagr) ** years)
            if revenue_ttm is not None
            else None
        )
        if margin_ttm is None:
            scenario_margin = None
        elif name == "Bear":
            scenario_margin = max(0, margin_ttm * 0.8)
        elif name == "Bull":
            scenario_margin = margin_ttm * 1.15
        else:
            scenario_margin = margin_ttm
        target = future_eps * terminal_pe if future_eps and terminal_pe else None
        price_multiple = target / price if target and price else None
        scenario_multiples[name] = price_multiple
        weighted_multiple += (price_multiple or 0) * probability / 100
        scenario_rows.append(
            f'<tr class="{"risk-row" if name == "Bear" else "upper-row" if name == "Bull" else "current-row"}">'
            f"<td>{name}</td><td>{year}</td><td class='num'>{money_html((future_revenue or 0)/1e9) if future_revenue is not None else '待補'}B</td>"
            f"<td class='num'>{pct_html(revenue_cagr * 100)}</td><td class='num'>{pct_html(scenario_margin * 100 if scenario_margin is not None else None)}</td>"
            f"<td class='num'>{money_html(future_eps)}</td>"
            f"<td class='num'>{ratio_html(terminal_pe)}</td><td class='num'>{money_html(target)}</td>"
            f"<td class='num'><strong>{fmt(price_multiple)}x</strong></td><td class='num'>{probability}%</td>"
            f"<td>{escape(condition)}</td></tr>"
        )

    if weighted_multiple >= 1.8:
        result_text = "模型顯示具兩倍附近潛力，但目前缺少公司一手營收、訂單與供給證據，不能列為高確信倍數股"
        final_label = "等待下一驗證點／不追價"
    elif weighted_multiple >= 1.3:
        result_text = "較合理為 3–4 年 1.3–1.8x；是否升格為倍數候選取決於 EPS、FCF 與訂單驗證"
        final_label = "續抱但不追價／等待驗證"
    else:
        result_text = "目前較像合理成長或估值已反映，尚不足以支持從現價再次倍數上漲"
        final_label = "保留核心倉、交易倉依估值停利"

    reverse_parts = [
        part.strip(" 。")
        for part in re.split(r"[、，；]", item.get("bear", ""))
        if part.strip()
    ]
    while len(reverse_parts) < 3:
        reverse_parts.append("若 EPS/FCF 上修落後股價漲幅，現價報酬風險惡化")
    reverse_html = "".join(f"<li>{escape(part)}</li>" for part in reverse_parts[:5])

    cross_date, cross_label, cross_url = RESEARCH_CROSSCHECKS[item["ticker"]]
    indirect_date, indirect_label, indirect_url = INDIRECT_SOURCES[item["ticker"]]
    cross_is_official = cross_url == IR_URLS[item["ticker"]] or any(
        marker in cross_url
        for marker in (
            "investors.", "investor.", "/investor", "/investors",
            "gevernova.com/sites/default/files/",
        )
    )
    cross_nature = "公司官方季度資料" if cross_is_official else "獨立媒體交叉驗證"
    cross_quality = "A-" if cross_is_official else "C"
    cross_verification = (
        "官方來源、事件與日期已核對；數值仍須依原始表格口徑解讀"
        if cross_is_official
        else "媒體日期與事件已核對；數值以公司 IR 為準"
    )
    signals = [
        (item.get("catalyst"), "Stage 0/1", "中性", "研究追蹤：領先指標", "待逐項取證", f"領先指標研究清單（截至 {BASIS_DATE}）", IR_URLS[item["ticker"]], "D", "6–36 月", "這是搜尋方向，不當作已確認正向證據或納入高品質加分"),
        (cross_label, "Stage 1/2", "正向", "直接：營運／財務", cross_nature, f"財報交叉驗證（{cross_date}）", cross_url, cross_quality, "0–24 月", cross_verification),
        (indirect_label, "Stage 0/1", "正向", "間接：客戶／產業", "獨立證據鏈", f"產業交叉驗證（{indirect_date}）", indirect_url, "B-" if "epa.gov" in indirect_url else "C", "6–36 月", "連結與日期已核對；不得與公司自身說法重複計分"),
        (f"Operating margin {op_margin}；FCF margin {fcf_margin}", "Stage 2", "中性", "直接：財務結果", "標準化統計頁", f"StockAnalysis（抓取日 {RUN_DATE}）", item["url"], "B-", "0–12 月", "已取得快照，仍需 10-Q/IR 交叉驗證"),
        (f"60 日股價變動 {pct(d60)}；價格相對 Base fair 為 {pct(change(price, fair))}", "Stage 3", "中性", "直接：市場定價", "歷史價格 API", f"正式收盤基準（{BASIS_DATE}）", f"https://stockanalysis.com/api/symbol/s/{item['ticker']}/history?range=Max&period=Daily", "B", "即時", "市場價格已驗證"),
        (f"Forward P/E {ratio(fpe)}；唯一 valuation EPS {fmt(item.get('valuation_eps'))}", "Stage 3", "負向" if stage3 else "中性", "直接：估值", "保存估值快照", f"同快照估值（{BASIS_DATE}）", item["valuation_snapshot_url"], "B", "即時", "通過同快照驗證"),
        (item.get("bear"), "Stage 2/3", "負向", "反向：thesis 失效", "研究反證清單", "反向證據待逐項核對", IR_URLS[item["ticker"]], "D", "即時至 24 月", "不能因未驗證而忽略"),
    ]
    signal_rows = "".join(
        f"<tr><td>{escape(signal)}</td><td>{escape(stage)}</td><td>{tag_html(direction)}</td>"
        f"<td>{escape(evidence_type)}</td><td>{escape(source_nature)}</td>"
        f"<td><a href='{escape(url)}'>{escape(source)}</a></td><td class='num'>{quality}</td>"
        f"<td>{lead}</td><td>{verified}</td></tr>"
        for signal, stage, direction, evidence_type, source_nature, source, url, quality, lead, verified in signals
    )
    fixed_recheck = (
        item.get("earnings_status")
        if item.get("earnings_status") and "下一/估計" in item.get("earnings_status")
        else "下一次財報／guidance 公布後完整重評"
    )
    return f"""
    <div class="note"><strong>一句話結論：</strong>{escape(result_text)}。</div>
    <table><tbody>
      <tr><th>分析狀態</th><td><strong>固定執行，不設啟動門檻。</strong>每次個股分析都從現價重新檢查倍數潛力與 de-rating 風險。</td></tr>
      <tr><th>主要／次要階段</th><td><strong>{primary_stage}</strong>；{secondary_stage}。</td></tr>
      <tr><th>估值口徑</th><td>基準日 {BASIS_DATE} 收盤 {money_html(price)}、Forward P/E {ratio_html(fpe)}、唯一 valuation EPS {money_html(item.get('valuation_eps'))}（{escape(item.get('valuation_eps_basis'))}）。</td></tr>
      <tr><th>證據限制</th><td>目前有同快照估值、價格與財務比率；公司一手營收、訂單/backlog、產能與客戶承諾尚未完整匯入，因此結論信心下修。</td></tr>
    </tbody></table>

    <h3>12.1.1 Stage 0–3 訊號、來源與品質</h3>
    <table><thead><tr><th>訊號</th><th>階段</th><th>方向</th><th>直接／間接</th><th>來源性質</th><th>來源與日期</th><th class="num">品質</th><th>領先期</th><th>驗證</th></tr></thead><tbody>{signal_rows}</tbody></table>

    <h3>12.1.2 多頭與至少三項反向證據</h3>
    <div class="two-col">
      <div class="note"><strong>多頭論點：</strong>{escape(item.get('thesis'))}<br><strong>下一催化：</strong>{escape(item.get('catalyst'))}</div>
      <div class="warn"><strong>反向／失效證據：</strong><ul>{reverse_html}</ul></div>
    </div>

    <h3>12.1.3 倍數成長雙分數</h3>
    <div class="two-col">
      <table><thead><tr><th>基本面延展類別</th><th class="num">分數</th><th>支持證據</th><th>扣分／待驗證</th></tr></thead><tbody>{fundamental_rows}<tr class="current-row"><th>基本面合計</th><th class="num">{fundamental_total}/70</th><th colspan="2">判斷公司能否捕獲長期產業成長</th></tr></tbody></table>
      <table><thead><tr><th>現價報酬風險類別</th><th class="num">分數</th><th>支持證據</th><th>扣分／待驗證</th></tr></thead><tbody>{price_rows}<tr class="current-row"><th>現價合計</th><th class="num">{price_total}/30</th><th colspan="2">判斷從目前價格出發的風險報酬</th></tr></tbody></table>
    </div>
    {score_interpretation_html(fundamental_total, price_total)}
    <p class="small">100 分合計僅供排序：{weighted_total}/100。投資判斷必須同時閱讀 70 分基本面與 30 分現價，不得用總分掩蓋高估值或低證據品質。</p>

    <h3>12.1.4 Bear / Base / Bull 倍數模型</h3>
    <p><strong>基準日目前價格：{money_html(price)}</strong></p>
    <p class="small">營收基準使用截至 {escape(item.get('financial_last_date') or '最新可得季度')} 的 TTM revenue {money_html((revenue_ttm or 0)/1e9) if revenue_ttm is not None else '待補'}B；EPS 使用本報唯一 valuation EPS 建立情境，避免和同快照目標價混用。Bear/Base/Bull 機率合計 100%，Extreme Bull 不納入主結論。</p>
    <table><thead><tr><th>情境</th><th>目標年</th><th class="num">營收</th><th class="num">Revenue CAGR</th><th class="num">淨利率</th><th class="num">EPS</th><th class="num">終值 P/E</th><th class="num">目標價</th><th class="num">現價倍數</th><th class="num">機率</th><th>必要條件／失效訊號</th></tr></thead><tbody>{''.join(scenario_rows)}</tbody></table>
    <p><strong>機率加權倍數：</strong>{weighted_multiple:.2f}x；Bear/Base/Bull 約 {fmt(scenario_multiples.get('Bear'))}x / {fmt(scenario_multiples.get('Base'))}x / {fmt(scenario_multiples.get('Bull'))}x。若主要報酬依靠 terminal multiple 而非 EPS/FCF，上述倍數可信度必須再下修。</p>

    <h3>12.1.5 最終判斷、時間與重評</h3>
    <table><tbody>
      <tr><th>最可能倍數／時間</th><td>{escape(result_text)}；模型期間約 3–4 年。</td></tr>
      <tr><th>資料完整度／信心</th><td><strong>低至中。</strong>價格與估值已驗證；需求、供給、訂單及公司財務端尚未完成三角驗證。</td></tr>
      <tr><th>下一必要驗證點</th><td>{escape(item.get('catalyst'))}</td></tr>
      <tr><th>固定重評</th><td>{escape(fixed_recheck)}</td></tr>
      <tr><th>立即重評條件</th><td>EPS/guidance、margin、backlog/訂單、CapEx/產能、競爭格局改變，或股價／valuation EPS 較本次變動超過 20%。</td></tr>
      <tr><th>最終操作標籤</th><td>{tag_html(final_label)}</td></tr>
    </tbody></table>
    <div class="warn"><strong>證據限制結論：</strong>目前只能證明產業方向與估值情境值得追蹤，尚不足以證明該公司能從現價再次實現倍數成長。</div>
    """


def rerating_derating_section(item: dict) -> str:
    nodes = item.get("price_nodes") or {}
    return f"""
    <table><thead><tr><th>方向</th><th>觸發條件</th><th>估值/價格影響</th><th>操作含義</th></tr></thead><tbody>
      <tr class="upper-row"><td>Rerating</td><td>implied NTM EPS proxy 或正式 guidance/consensus 上修、毛利率/營益率改善、backlog 或訂單加速、同業 multiple 擴張、產業供給吃緊。</td><td>可從 Conservative Fair {money_html(nodes.get('conservative_fair'),'key')} 往 Selected Growth Fair {money_html(nodes.get('selected_growth_fair'),'watch-text')} 看，但需證據支撐。</td><td>已有部位可續抱部分；新進場避免追在 Forward Growth Anchor 區。</td></tr>
      <tr><td>維持 Base</td><td>基本面符合預期，但沒有明顯上修；同業估值與歷史 proxy 沒有擴張。</td><td>Conservative Fair {money_html(nodes.get('conservative_fair'),'key')} 是主要防守合理價參考。</td><td>到 Conservative Fair 後以續抱/部分停利檢查為主。</td></tr>
      <tr class="risk-row"><td>De-rating</td><td>EPS/guidance 下修、margin 壓力、需求或訂單轉弱、同業估值壓縮、公司特定壞消息。</td><td>價格跌向 Value Entry {money_html(nodes.get('value_entry'),'positive')} 或 Bear Stress {money_html(nodes.get('bear_stress'),'risk-text')} 時，不能只用便宜解讀。</td><td>先判斷 thesis 是否 damaged；若 damaged，減碼/退出優先於攤平。</td></tr>
    </tbody></table>
    <h3>12.1 停利後倍數成長再評估（Post-Target Multibagger Reassessment）</h3>
    <p><span class="tag watch">每檔固定執行</span> 不再以達標與否作啟動條件。停利價是重新估值檢查點，不是自動賣點；產業前景佳也不等於現價仍可翻倍。</p>
    {multibagger_analysis_section(item)}
    """


def crash_logic() -> str:
    return """
    <table><thead><tr><th>檢查</th><th>若答案是「是」</th><th>動作</th></tr></thead><tbody>
      <tr><td>大盤、SOX、類股、同業同步大跌？</td><td>系統性下跌</td><td>不機械全砍；停止加碼，檢查總曝險與交易額度。</td></tr>
      <tr><td>標的是否明顯弱於 peers 5-8 個百分點以上？</td><td>可能公司特定風險</td><td>查新聞、估計修正、債務、訂單或客戶事件。</td></tr>
      <tr><td>EPS、guidance、margin、backlog、政策或關鍵客戶是否變壞？</td><td>thesis damaged</td><td>即使大盤也跌，仍要減碼/退出。</td></tr>
      <tr><td>跌破後 2-3 個交易日是否收回？</td><td>技術修復</td><td>可保留核心倉或繼續觀察，不把單日跌破當最終判決。</td></tr>
    </tbody></table>
    """


def price_thesis_matrix(item: dict) -> str:
    nodes = item.get("price_nodes") or {}
    return f"""
    <table><thead><tr><th>價格/狀態</th><th>Thesis intact</th><th>Thesis damaged</th><th>需要的證據</th></tr></thead><tbody>
      <tr class="entry-row"><td>Value Entry {money_html(nodes.get('value_entry'),'positive')}</td><td>可小量研究或分批。</td><td>不接，保留現金。</td><td>EPS/guidance/peer 沒轉弱；沒有公司特定壞消息。</td></tr>
      <tr class="risk-row"><td>Bear Stress {money_html(nodes.get('bear_stress'),'risk-text')}</td><td>啟動風險審核，不機械停損。</td><td>減碼/退出。</td><td>明顯弱於 peers、估計下修、訂單/margin 轉差。</td></tr>
      <tr class="upper-row"><td>Forward Growth Anchor {money_html(nodes.get('forward_growth_anchor'),'watch-text')}</td><td>若 EPS 上修且 RES 改善可續抱部分。</td><td>停利/不追。</td><td>價格進入 rerating 區但基本面沒跟上。</td></tr>
    </tbody></table>
    """


def event_section(item: dict) -> str:
    return f"""
    <ul>
      <li><strong>市場訊號：</strong>正式收盤 {money_html(item['close'])}，5D/20D/60D 為 {pct_html(item['d5'])} / {pct_html(item['d20'])} / {pct_html(item['d60'])}，用來判斷短線是否已提前反映題材。</li>
      <li><strong>財報/估計口徑：</strong>TTM EPS {money_html(item['eps_ttm'])}，唯一 valuation EPS {money_html(item['valuation_eps'])}（{escape(item['valuation_eps_basis'])}）。若 valuation EPS 明顯高於或低於 TTM EPS，必須先解釋 GAAP、adjusted、NTM/FY 與一次性項目差異。</li>
      <li><strong>催化：</strong>{escape(item['catalyst'])}</li>
      <li><strong>風險：</strong>{escape(item['bear'])}</li>
      <li><strong>財報日期檢查：</strong>{escape(item['earnings_status'])}。</li>
    </ul>
    """


def data_completeness(item: dict) -> str:
    proxy_ok = all(row["verified"] for row in item["proxy"])
    pe_gap = "；P/E source/calc 口徑差異需註記" if item["pe_conflict"] else ""
    return f"""
    <table><tbody>
      <tr><th>已取得</th><td>{BASIS_DATE} 正式收盤、日漲跌、成交量、RVOL、5D/20D/60D、TTM EPS、P/E、Forward P/E、P/S、P/FCF、EV/EBITDA、margin、Debt/Equity、3M/6M/1Y/2Y/3Y P/E windows（逐檔標示 point-in-time 或 current-TTM fallback）、同業估值、估值來源拆解。</td></tr>
      <tr><th>EPS / P-E / P-S audit</th><td>EPS：{escape(item.get('eps_audit_status'))}；Forward P/E：{escape(item.get('forward_pe_status'))}；P/S：{escape(item.get('ps_status'))}。處理結果：{escape(item.get('valuation_warning') or item.get('valuation_block_reason') or '通過')}；信心：{escape(item.get('valuation_confidence'))}。衝突可採同頁自洽主口徑繼續計算，但必須保留替代值與差異；只有缺乏可用 valuation EPS 才硬阻擋。</td></tr>
      <tr><th>long proxy 驗證</th><td>{'3M/6M/1Y/2Y/3Y 已用 Max history API 重算驗證' if proxy_ok else '部分窗口來源需重驗'}；最新納入日期 {escape(item['basis_date'])}；EPS 分母 {money_html(item['eps_ttm'])}。{pe_gap}</td></tr>
      <tr class="watch-row"><th>仍需正式深研</th><td>公司 IR/財報稿與主流媒體逐篇交叉檢查、真正逐季 TTM EPS 歷史 P/E、backlog/訂單橋、FY26/FY27 consensus 原始來源。這些會影響信心與倍數，但本版已不省略風控與估值結構。</td></tr>
    </tbody></table>
    """


def source_links(item: dict, stats_map: dict[str, dict]) -> str:
    peer_links = "".join(
        f'<li><a href="{escape(stats_map.get(peer,{}).get("url","#"))}">{peer} peer statistics</a></li>'
        for peer in item["peers"]
    )
    cross_date, cross_label, cross_url = RESEARCH_CROSSCHECKS[item["ticker"]]
    indirect_date, indirect_label, indirect_url = INDIRECT_SOURCES[item["ticker"]]
    return f"""
    <ul>
      <li><a href="{escape(IR_URLS[item['ticker']])}">{item['ticker']} 公司 IR／財報原始來源</a></li>
      <li><a href="{escape(cross_url)}">{escape(cross_label)}（{cross_date}）</a></li>
      <li><a href="{escape(indirect_url)}">{escape(indirect_label)}（{indirect_date}）</a></li>
      <li><a href="{escape(item['url'])}">StockAnalysis {item['ticker']} statistics</a></li>
      <li><a href="{escape(item.get('financials_url'))}">StockAnalysis {item['ticker']} TTM financials</a></li>
      <li><a href="https://stockanalysis.com/api/symbol/s/{item['ticker']}/history?range=Max&period=Daily">StockAnalysis {item['ticker']} Max history API</a></li>
      {peer_links}
    </ul>
    """


def summary_table(data: list[dict]) -> str:
    rows = []
    for item in data:
        layers = item.get("forward_eps_layers") or {}
        conservative = item.get("conservative_valuation") or {}
        growth = item.get("growth_pass_through") or {}
        fets = item.get("fets") or {}
        res = item.get("res") or {}
        action = item.get("integrated_action") or {}
        fair = layers.get("conservative_fair")
        value_low = fair * .75 if fair else None
        value_high = fair * .85 if fair else None
        ma50 = num(item.get("50-Day Moving Average"))
        technical = min(ma50, item["close"] * .92) if ma50 and item.get("close") else None
        fy_eps = " / ".join(
            fmt(value) if value is not None else "N/A"
            for value in [item.get("fy1_consensus_eps"), item.get("fy2_consensus_eps"), item.get("ntm_consensus_eps")]
        )
        forward_meta = (
            f"{escape(item.get('valuation_eps_type') or 'N/A')} / "
            f"{fmt(item.get('analyst_count'),0) if item.get('analyst_count') is not None else 'N/A'} / "
            f"{fmt(item.get('forward_eps_dispersion')) if item.get('forward_eps_dispersion') is not None else 'N/A'}"
        )
        pe_meta = item.get("point_in_time_pe_meta") or {}
        valuation_regime = growth.get("recent_rerating_status") or "未取得"
        rows.append(
            f"""<tr>
              <td><button class="tab-button" type="button" data-jump="{item['ticker']}">{item['ticker']}</button><br><span class="small">{escape(item.get('company_line') or item['company'])}<br>{escape(item['industry'])}</span></td>
              <td class="num">{money_html(item['close'])}</td>
              <td>{escape(layers.get('price_zone') or 'N/A')}</td>
              <td>{tag_html(action.get('new_buy') or item.get('decision') or 'N/A')}</td>
              <td class="num">{money_html(value_low)}–{money_html(value_high)}</td>
              <td class="num">≤ {money_html(technical)}</td>
              <td class="num">{money_html(layers.get('forward_fair'))}</td>
              <td>{tag_html(item['priceScenario'])}</td>
              <td class="num">{pct_html(item['d5'])} / {pct_html(item['d20'])} / {pct_html(item['d60'])}</td>
              <td>{escape(valuation_regime)}<br><span class="small">{escape(growth.get('short_crowding_status') or '未取得')} · {escape(pe_meta.get('method') or 'proxy')}</span></td>
              <td class="num">{fmt(item.get('eps_ttm'))} / {ratio_html(item.get('pe'))}</td>
              <td class="num">{fy_eps}</td>
              <td>{forward_meta}</td>
              <td class="num">{fmt(fets.get('total'),0)}/100 / {pct_html((fets.get('trust_pct') or 0)*100)}</td>
              <td class="num">{money_html(layers.get('conservative_fair'))}</td>
              <td class="num">{money_html(layers.get('trust_adjusted_fair'))}</td>
              <td class="num">{money_html(layers.get('forward_fair'))}</td>
              <td class="num">{pct_html(growth.get('market_implied_q')*100) if growth.get('market_implied_q') is not None else 'N/A'}</td>
              <td>{fmt(res.get('total'),0)}/100<br><span class="small">{escape(res.get('status') or 'N/A')}</span></td>
              <td class="num">{escape(item.get('FCF Margin') or 'N/A')}</td>
              <td class="num">N/A / {escape(item.get('Debt / Equity') or 'N/A')}</td>
              <td>{escape(item.get('earnings_status') or 'N/A')}</td>
            </tr>"""
        )
    return f"""
    <section><h2>快速結論總表</h2>
      <p class="warn"><strong>圖例：</strong>①價值研究區＝Conservative Fair ×75%–85%，低於下緣先查 thesis；②技術執行參考＝min(50DMA, 現價×92%)，只決定執行節奏；③Forward Growth Anchor＝Forward EPS × 2Y/3Y point-in-time 正常化錨，超過後看 RES。Price Zone 是現價相對三層 fair 的位置；Bear/Base/Bull 是基本面情境。Market Regime 欄同時顯示 1Y 估值 regime 與 3M/6M crowding。</p>
      <div class="summary-scroll"><table class="summary-table"><thead><tr>
      <th>Ticker／公司／產業</th><th class="num">最新價</th><th>Price Zone</th><th>現價動作</th>
      <th class="num">①價值研究區</th><th class="num">②技術執行參考</th><th class="num">③Forward Growth Anchor</th>
      <th>Bear/Base/Bull情境</th><th class="num">5D／20D／60D</th><th>市場Regime</th>
      <th class="num">TTM EPS／Trailing P/E</th><th class="num">FY1／FY2／NTM EPS</th><th>Forward類型／分析師／分散度</th>
      <th class="num">FETS／Trust%</th><th class="num">Conservative Fair</th><th class="num">Trust-adjusted Fair</th>
      <th class="num">Forward Growth Anchor</th><th class="num">Market-implied q</th><th>RES</th>
      <th class="num">FCF margin</th><th class="num">Net debt／D/E</th><th>下一次財報</th>
      </tr></thead><tbody>{table_rows(rows)}</tbody></table></div>
    </section>
    """


def render_article(item: dict, stats_map: dict[str, dict]) -> str:
    ticker = item["ticker"]
    return f"""
    <article class="panel hidden" id="panel-{item['ticker']}" role="tabpanel" aria-labelledby="tab-{item['ticker']}">
      <h2 id="{ticker}-overview">{item['ticker']} {escape(item.get('company_line') or item['company'])} 完整個股分析</h2>
      <p class="muted">基準日：{escape(item['basis_date'])} 美股正式收盤 | 產出日：{RUN_DATE} 台北時間。用途：投資研究與風險提示，不構成個人化財務建議。</p>

      <h2 id="{ticker}-gate">前置閘門總結</h2>
      <div class="grid">
        <div class="metric"><span>正式收盤</span><strong>{money(item['close'])}</strong><small>日漲跌 {pct(item['day_change'])}</small></div>
        <div class="metric"><span>相對成交量</span><strong>{ratio(item['rvol'])}</strong><small>{fmt(item['volume'],0)} / 20 日均量 {escape(item.get('Average Volume (20 Days'))}</small></div>
        <div class="metric"><span>P/E vs Forward P/E</span><strong>{fmt(item['pe'])} / {fmt(item['fpe'])}</strong><small>TTM EPS {fmt(item['eps_ttm'])} / implied EPS {fmt(item['eps_fwd'])}</small></div>
        <div class="metric"><span>框架結論</span><strong>{escape(item['decision'])}</strong><small>{escape(item['action'])}；Entry {money(item['entry'])}</small></div>
      </div>
      <ul>
        <li><strong>核心 thesis：</strong>{escape(item['thesis'])}</li>
        <li>目前現價隱含情境：{tag_html(item['priceScenario'])}。</li>
        <li><strong>主要驗證點：</strong>{escape(item['catalyst'])}；{escape(item['earnings_status'])}。</li>
      </ul>

      <h2 id="{ticker}-company">公司白話介紹</h2>
      <p>{escape(item['business'])}</p>

      <h2 id="{ticker}-conclusion">一句話結論</h2>
      <p><strong>{escape(item['action'])}：</strong>{escape(item['thesis'])} 目前不把單一價格線當成自動停損；若接近 {money_html(item['stress'],'risk-text')}，先做 thesis 審核與同業相對強弱檢查。</p>

      <h2 id="{ticker}-regime">1. 市場 Regime 與持股閘門</h2>
      <p class="warn"><strong>你的部位閘門：</strong>最新持股檔顯示目前美股主要剩 BDC 24 股與 GEV 4 股；COHR/NTAP 已清倉。45,000 美元軟上限下新交易空間有限，本批 {len(TICKERS)} 檔用於排序與等待價位，不適合同時多檔追進。</p>
      <table><tbody>
        <tr><th>大盤背景</th><td>本版為 {BASIS_DATE} 正式收盤基準；多檔 AI、電力與高 beta 題材波動大，新增部位需分批且受交易額度閘門限制。</td></tr>
        <tr><th>{item['ticker']} 技術位置</th><td>收盤 {money_html(item['close'])}；50DMA {escape(item.get('50-Day Moving Average'))}；200DMA {escape(item.get('200-Day Moving Average'))}；5D/20D/60D = {pct_html(item['d5'])} / {pct_html(item['d20'])} / {pct_html(item['d60'])}。</td></tr>
        <tr><th>量能</th><td>成交量 <strong>{fmt(item['volume'],0)}</strong>；相對成交量 {ratio_html(item['rvol'])}。</td></tr>
        <tr><th>持股/候選閘門</th><td>{escape(item['priority'])}；本批用於候選排序，不是同時買進清單。</td></tr>
      </tbody></table>

      <h2 id="{ticker}-industry">2. 產業與國際情勢</h2>
      <p>{escape(item['industry'])}：{escape(item['thesis'])}</p>

      <h2 id="{ticker}-bear">3. Bear Case First</h2>
      <table><thead><tr><th>Bear 風險</th><th>對 {item['ticker']} 的影響</th><th>目前處理</th></tr></thead><tbody>
        <tr class="risk-row"><td>{escape(item['bear'])}</td><td>可能壓縮 EPS、multiple 或技術支撐。</td><td>列入 {money_html(item['stress'],'risk-text')} 風險審核，不用單一價格機械砍倉。</td></tr>
      </tbody></table>

      <h2 id="{ticker}-price">4. 價格與部位</h2>
      {price_position_section(item)}

      <h2 id="{ticker}-numbers">5. 來源數字表</h2>
      {source_number_table(item)}

      <h2 id="{ticker}-eps">6. EPS 模組：P/E 與 Forward P/E 口徑橋</h2>
      {eps_bridge(item)}
      {eps_year_clarity_table(item)}

      <h2 id="{ticker}-valuation">7. 估值模組</h2>
      <h3>7.1 {item['ticker']} 自身近期 TTM P/E Proxy</h3>
      {proxy_table(item)}
      <h3>7.1B {item['ticker']} 自身近期 TTM P/S Proxy</h3>
      {ps_proxy_table(item)}
      <h3>7.2 Conservative Valuation：Forward-equivalent 保守估值帶</h3>
      {render_valuation_tables(item)}
      <h3>7.3 同業估值對照</h3>
      {peer_table(item)}

      <h2 id="{ticker}-targets">8. 目標價階梯</h2>
      {target_ladder(item)}

      <h2 id="{ticker}-action">9. 最後操作建議</h2>
      {final_action_section(item)}

      <h2 id="{ticker}-risk">10. 停損停利</h2>
      {stop_take_profit_section(item)}
      <h3>10.1 大盤大跌時，不機械停損</h3>
      {crash_logic()}

      <h2 id="{ticker}-quality">11. 品質與財報風險</h2>
      {quality_financial_risk_section(item)}

      <h2 id="{ticker}-rerating">12. Rerating / De-rating 檢查</h2>
      {rerating_derating_section(item)}

      <h2 id="{ticker}-matrix">13. Price x Thesis 決策矩陣</h2>
      {price_thesis_matrix(item)}

      <h2 id="{ticker}-events">14. 最新事件交叉檢查</h2>
      {event_section(item)}

      <h2 id="{ticker}-next">15. 下一驗證點</h2>
      <ul>
        <li>財報日期欄位：{escape(item['earnings_status'])}</li>
        <li>估計修正：implied NTM EPS proxy、guidance 或 consensus 是否上修或下修。</li>
        <li>產業證據：{escape(item['catalyst'])}</li>
        <li>技術/風控：正式收盤是否接近 Entry、Stress 或 Upper，而不是看盤後價。</li>
      </ul>

      <h2 id="{ticker}-data">16. 資料完整性</h2>
      {data_completeness(item)}

      <h2 id="{ticker}-sources">17. 主要資料來源</h2>
      {source_links(item, stats_map)}
    </article>
    """


def build_html(data: list[dict], stats_map: dict[str, dict]) -> str:
    buttons = "".join(
        f'<button class="tab-button" id="tab-{item["ticker"]}" role="tab" aria-controls="panel-{item["ticker"]}" aria-selected="false" data-ticker="{item["ticker"]}">{item["ticker"]}</button>'
        for item in data
    )
    articles = "".join(render_article(item, stats_map) for item in data)
    section_nav = """
      <aside class="section-nav" id="section-nav" aria-label="本檔章節導覽">
        <strong id="section-nav-title">個股章節</strong>
        <a data-section="overview">完整分析頂端</a>
        <a data-section="conclusion">一句話結論</a>
        <div class="nav-divider"></div>
        <a data-section="regime">1. 市場與持股閘門</a>
        <a data-section="bear">3. Bear Case</a>
        <a data-section="price">4. 價格與部位</a>
        <a data-section="numbers">5. 來源數字</a>
        <a data-section="eps">6. EPS 口徑</a>
        <a data-section="valuation">7. 估值模組</a>
        <a data-section="targets">8. 目標價</a>
        <a data-section="action">9. 操作建議</a>
        <a data-section="risk">10. 停損停利</a>
        <a data-section="quality">11. 品質風險</a>
        <a data-section="rerating">12. Rerating / 倍數再評估</a>
        <a data-section="matrix">13. Price × Thesis</a>
        <a data-section="events">14. 事件</a>
        <a data-section="next">15. 下一驗證點</a>
        <a data-section="data">16. 資料完整性</a>
        <a data-section="sources">17. 來源</a>
      </aside>
    """
    source_list = "".join(f'<li><a href="{escape(item["url"])}">{item["ticker"]} statistics</a></li>' for item in data)
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(REPORT_TITLE)} {RUN_DATE} basis {BASIS_DATE}</title>
  <style>{CSS}</style>
</head>
<body>
  <header class="hero">
    <h1>{escape(REPORT_TITLE)}</h1>
    <p>標的：{escape(', '.join(TICKERS))}</p>
    <p>基準日：{BASIS_DATE} 美股正式收盤 | 產出日：{RUN_DATE} 台北時間 | 用途：投資研究與風險提示，不構成個人化財務建議。</p>
  </header>
  <main>
    <section>
      <h2>3-5 行總結</h2>
      <ul>
        <li><strong>本版是完整多檔整合版：</strong>{len(TICKERS)} 檔排序表 + 每檔單檔風控與 thesis 深度。</li>
        <li><strong>資料基準改為正式收盤：</strong>使用 {BASIS_DATE} StockAnalysis Max history API 收盤列，盤後價獨立標示，不混入正式價格。</li>
        <li><strong>long proxy 已重算：</strong>3M/6M/1Y/2Y/3Y current-EPS P/E proxy 均保留筆數、日期、P10/P50/P90 與驗證狀態。</li>
        <li><strong>研究排序：</strong>依同快照估值、基本面延展分數、現價報酬風險分數與下一驗證點排序；清單不是同時買進建議。</li>
        <li><strong>交易額度閘門仍有效：</strong>目前不適合同時新增多檔，報告用途是排序、等待價位與風控劇本。</li>
      </ul>
    </section>
    <nav class="tabs" id="tabs" aria-label="股票頁籤">{buttons}</nav>
    {summary_table(data)}
    <div class="report-shell">
      {section_nav}
      <div id="content">{articles}</div>
    </div>
    <section>
      <h2>主要資料來源</h2>
      <ul>{source_list}</ul>
      <p>日線資料使用 StockAnalysis Max history API；估值統計頁標示資料供應為 S&P Global Market Intelligence。公司 IR/主流媒體逐篇交叉檢查仍屬下一層深研，但本版已將正式收盤、long proxy、同業估值、Price x Thesis 與非機械停損邏輯整合進每檔 tab。</p>
    </section>
  </main>
  <script>
    const tabs=document.querySelectorAll('.tab-button[data-ticker]');
    const panels=document.querySelectorAll('[role="tabpanel"]');
    const sectionLinks=document.querySelectorAll('#section-nav [data-section]');
    let activeTicker='{TICKERS[0]}';
    function updateSectionLinks(t){{
      activeTicker=t;
      document.getElementById('section-nav-title').textContent=t+' 個股章節';
      sectionLinks.forEach(a=>a.href='#'+t+'-'+a.dataset.section);
    }}
    function selectTicker(t,scrollToPanel=false,hashTarget=null){{
      tabs.forEach(b=>b.setAttribute('aria-selected',b.dataset.ticker===t?'true':'false'));
      panels.forEach(p=>p.classList.toggle('hidden',p.id!=='panel-'+t));
      updateSectionLinks(t);
      history.replaceState(null,'','#'+(hashTarget||t));
      if(scrollToPanel) document.getElementById(t+'-overview')?.scrollIntoView({{behavior:'smooth',block:'start'}});
    }}
    tabs.forEach(b=>b.addEventListener('click',()=>selectTicker(b.dataset.ticker,true)));
    document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>selectTicker(b.dataset.jump,true)));
    sectionLinks.forEach(a=>a.addEventListener('click',e=>{{
      e.preventDefault();
      const target=document.getElementById(activeTicker+'-'+a.dataset.section);
      target?.scrollIntoView({{behavior:'smooth',block:'start'}});
      history.replaceState(null,'',a.getAttribute('href'));
    }}));
    const rawHash=location.hash?.slice(1);
    const hashTicker={json.dumps(TICKERS)}.find(t=>rawHash===t||rawHash?.startsWith(t+'-'))||'{TICKERS[0]}';
    selectTicker(hashTicker,false,rawHash&&document.getElementById(rawHash)?rawHash:null);
    if(rawHash&&document.getElementById(rawHash)) requestAnimationFrame(()=>document.getElementById(rawHash).scrollIntoView());
  </script>
</body>
</html>
"""


def validate_report_consistency(data: list[dict]) -> None:
    errors = []
    for item in data:
        ticker = item["ticker"]
        audit = item.get("valuation_audit") or {}
        if not audit:
            errors.append(f"{ticker}: missing EPS/P-E/P-S valuation audit")
        # A P/S gap is a disclosure conflict, not a reason to suppress the
        # report. valuation_audit() preserves both values and ps_status marks
        # gaps above 3% for the reader, as required by the US framework.
        if (
            not item.get("valuation_blocked")
            and
            audit.get("financial_currency") in {None, "USD"}
            and audit.get("stats_eps_ttm") is not None
            and audit.get("financials_eps_ttm") is not None
            and (audit.get("eps_audit_gap") or 0) > 0.03
            and not item.get("valuation_warning")
        ):
            errors.append(f"{ticker}: statistics EPS vs financials EPS mismatch {(audit.get('eps_audit_gap') or 0):.1%}")
        if len(item.get("proxy") or []) != 5:
            errors.append(f"{ticker}: TTM P/E proxy does not contain 3M/6M/1Y/2Y/3Y")
        if any("p75" not in row for row in item.get("proxy") or []):
            errors.append(f"{ticker}: TTM P/E proxy missing P75 required by rerating model")
        if len(item.get("ps_proxy") or []) != 5:
            errors.append(f"{ticker}: TTM P/S proxy does not contain 3M/6M/1Y/2Y/3Y")
        if item.get("eps_ttm") and item["eps_ttm"] > 0:
            if not all(row.get("verified") for row in item.get("proxy") or []):
                errors.append(f"{ticker}: positive-EPS P/E proxy failed recomputation")
        elif any(row.get("verified") for row in item.get("proxy") or []):
            errors.append(f"{ticker}: non-positive EPS must not produce verified P/E proxy")
        for source_map_name, source_map in [
            ("cross-check", RESEARCH_CROSSCHECKS),
            ("indirect", INDIRECT_SOURCES),
        ]:
            source_date, _source_label, source_url = source_map[ticker]
            if source_date > BASIS_DATE:
                errors.append(
                    f"{ticker}: {source_map_name} source date {source_date} is after basis date"
                )
            if not source_url.startswith("https://"):
                errors.append(
                    f"{ticker}: {source_map_name} source URL is not HTTPS"
                )
        if not IR_URLS[ticker].startswith("https://"):
            errors.append(f"{ticker}: IR URL is not HTTPS")
        if item.get("revenue_ttm") is None:
            errors.append(f"{ticker}: missing TTM revenue for 12.1 scenario model")
        if item.get("shares_diluted_ttm") is None:
            errors.append(f"{ticker}: missing diluted shares for 12.1 scenario model")
        eps = item.get("valuation_eps")
        if item.get("valuation_blocked"):
            if any(item.get(key) is not None for key in ["stress", "entry", "fair", "upper"]):
                errors.append(f"{ticker}: blocked valuation still produced target prices")
            continue
        if (
            item.get("pe")
            and item.get("eps_ttm")
            and (
                item.get("reported_eps_ttm") is None
                or abs((item.get("reported_eps_ttm") or 0) - item.get("eps_ttm")) <= 0.01
            )
        ):
            calculated_pe = item["close"] / item["eps_ttm"]
            mismatch = abs(calculated_pe - item["pe"]) / max(abs(item["pe"]), 1)
            if mismatch > 0.03:
                errors.append(f"{ticker}: close/TTM EPS vs P/E mismatch {mismatch:.1%}")
        if eps is None:
            errors.append(f"{ticker}: missing valuation_eps")
            continue
        rerating = item.get("rerating_model") or {}
        if not rerating:
            errors.append(f"{ticker}: missing rerating model")
        elif not 0 <= (rerating.get("activation_score") or 0) <= 100:
            errors.append(f"{ticker}: rerating activation score outside 0-100")
        elif rerating.get("active") and abs((rerating.get("rerating_blend_weight") or 0) - 0.50) > 1e-9:
            errors.append(f"{ticker}: applicable rerating does not use fixed 50% blend")
        nodes = item.get("price_nodes") or {}
        for key, node_key in [
            ("stress", "bear_stress"),
            ("entry", "value_entry"),
            ("fair", "conservative_fair"),
        ]:
            expected = nodes.get(node_key)
            if expected is None or item.get(key) is None or abs(item[key] - expected) > 0.02:
                errors.append(f"{ticker}: {key} does not match canonical price_nodes.{node_key}")
        upper_expected = nodes.get("selected_growth_fair") or nodes.get("forward_growth_anchor")
        if upper_expected is not None and item.get("upper") is not None and abs(item["upper"] - upper_expected) > 0.02:
            errors.append(f"{ticker}: upper does not match canonical growth price node")
        if nodes.get("conservative_fair") is not None and item.get("eps_ttm") and item.get("conservative_valuation", {}).get("conservative_fair_multiple"):
            expected = item["eps_ttm"] * item["conservative_valuation"]["conservative_fair_multiple"]
            if abs(nodes["conservative_fair"] - expected) > 0.02:
                errors.append(f"{ticker}: conservative fair is not TTM EPS × Conservative P/E")
        self_peer = next(
            (row for row in item["peer_rows"] if row["ticker"] == ticker),
            None,
        )
        if not self_peer or abs((self_peer.get("eps_fwd") or 0) - eps) > 0.01:
            errors.append(f"{ticker}: peer-table self row valuation EPS mismatch")
        if abs((self_peer.get("fpe") or 0) - (item.get("fpe") or 0)) > 0.01:
            errors.append(f"{ticker}: peer-table self row Forward P/E mismatch")
        for peer_row in item["peer_rows"]:
            peer_ticker = peer_row["ticker"]
            if peer_ticker not in TICKERS:
                continue
            expected = next(row for row in data if row["ticker"] == peer_ticker)
            if expected.get("valuation_blocked"):
                continue
            if abs((peer_row.get("eps_fwd") or 0) - (expected.get("valuation_eps") or 0)) > 0.01:
                errors.append(
                    f"{ticker}: watchlist peer {peer_ticker} valuation EPS mismatch"
                )
            if abs((peer_row.get("fpe") or 0) - (expected.get("fpe") or 0)) > 0.01:
                errors.append(
                    f"{ticker}: watchlist peer {peer_ticker} Forward P/E mismatch"
                )

    main_prob = sum(
        scenario[8]
        for scenario in GEV_MULTIBAGGER["scenarios"]
        if scenario[0] != "Extreme Bull"
    )
    if main_prob != 100:
        errors.append(f"GEV: Bear/Base/Bull probability sum is {main_prob}, not 100")
    if errors:
        raise RuntimeError("report consistency validation failed:\n- " + "\n- ".join(errors))


def write_outputs(html: str, data: list[dict]) -> None:
    html_paths = list(dict.fromkeys(
        path for path in [PRIMARY_OUT, PRIMARY_DOC, PRIMARY_PUB, LEGACY_OUT, LEGACY_DOC, LEGACY_PUB]
        if path is not None
    ))
    for path in html_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    json_paths = list(dict.fromkeys(
        path for path in [PRIMARY_JSON, LEGACY_JSON] if path is not None
    ))
    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload)


def main() -> None:
    data, stats_map, _history_map = build_data()
    validate_report_consistency(data)
    html = build_html(data, stats_map)
    write_outputs(html, data)
    for path in dict.fromkeys(
        path for path in [PRIMARY_OUT, PRIMARY_DOC, PRIMARY_PUB, LEGACY_OUT, LEGACY_DOC, LEGACY_PUB, PRIMARY_JSON, LEGACY_JSON]
        if path is not None
    ):
        print(path)


if __name__ == "__main__":
    main()
