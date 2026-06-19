window.TRADING_DASHBOARD = {
  "version": 1,
  "updatedAt": "2026-06-18",
  "sourceNote": "User-provided ChatGPT整理交易紀錄; dashboard validation checks internal reconciliation only, not broker screenshot fidelity.",
  "markets": {
    "tw": {
      "market": "tw",
      "label": "台股",
      "currency": "TWD",
      "currencyLabel": "台幣",
      "initialCapital": 2000000,
      "currentDate": "2026-06-18",
      "currentTimestamp": "2026-06-18 10:10",
      "orderLogComplete": false,
      "dataQuality": [
        "舊交易紀錄與 2026/06/18 新增交易已合併累計。",
        "2026/06/18 10:10 持倉快照已排除 2880 華南金與 1904 正隆零股。",
        "成交/委託紀錄不是完整台帳；資產曲線採已實現損益事件 + 最新未實現庫存快照，不代表完整逐日市值曲線。"
      ],
      "summary": {
        "realizedPnl": 204138,
        "unrealizedPnl": 181549,
        "totalPnl": 385687,
        "currentAssets": 2385687,
        "totalReturnPct": 19.28,
        "cash": 1388385,
        "marketValue": 997302,
        "brokerGrossMarketValue": 999883,
        "brokerPositionReturnPct": 22.25
      },
      "positions": [
        {
          "symbol": "00757",
          "name": "統一 FANG+",
          "shares": 7273,
          "averagePrice": 99.68,
          "currentPrice": 129.25,
          "marketValue": 937756,
          "cost": 725915,
          "unrealizedPnl": 211841,
          "returnPct": 29.18
        },
        {
          "symbol": "1760",
          "name": "寶齡富錦",
          "shares": 577,
          "averagePrice": 106.99,
          "currentPrice": 60.5,
          "marketValue": 34755,
          "cost": 61838,
          "unrealizedPnl": -27083,
          "returnPct": -43.8
        },
        {
          "symbol": "4166",
          "name": "友霖",
          "shares": 1000,
          "averagePrice": 28,
          "currentPrice": 24.9,
          "marketValue": 24791,
          "cost": 28000,
          "unrealizedPnl": -3209,
          "returnPct": -11.46
        }
      ],
      "realizedTrades": [
        {
          "buyDate": "2026-03-08",
          "sellDate": "2026-04-08",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "shares": 1000,
          "estimatedBuyPrice": 56.06,
          "sellPrice": 58.65,
          "realizedPnl": 2461,
          "returnPct": 4.39,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-03-08",
          "sellDate": "2026-04-08",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "shares": 845,
          "estimatedBuyPrice": 55.04,
          "sellPrice": 58.55,
          "realizedPnl": 2874,
          "returnPct": 6.18,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-03-08",
          "sellDate": "2026-04-08",
          "symbol": "2353",
          "name": "宏碁",
          "shares": 2000,
          "estimatedBuyPrice": 27.41,
          "sellPrice": 27.35,
          "realizedPnl": -318,
          "returnPct": -0.58,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-03-08",
          "sellDate": "2026-04-08",
          "symbol": "2353",
          "name": "宏碁",
          "shares": 2000,
          "estimatedBuyPrice": 26.82,
          "sellPrice": 27.35,
          "realizedPnl": 633,
          "returnPct": 1.18,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-03-10",
          "sellDate": "2026-04-10",
          "symbol": "6488",
          "name": "環球晶",
          "shares": 250,
          "estimatedBuyPrice": 432.52,
          "sellPrice": 486,
          "realizedPnl": 12835,
          "returnPct": 11.87,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-03-24",
          "sellDate": "2026-04-24",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "shares": 309,
          "estimatedBuyPrice": 64.15,
          "sellPrice": 71.55,
          "realizedPnl": 2238,
          "returnPct": 11.29,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-03-29",
          "sellDate": "2026-04-29",
          "symbol": "00757",
          "name": "統一 FANG+",
          "shares": 2000,
          "estimatedBuyPrice": 116.36,
          "sellPrice": 120.9,
          "realizedPnl": 256,
          "returnPct": 0.11,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-03-29",
          "sellDate": "2026-04-29",
          "symbol": "2377",
          "name": "微星",
          "shares": 500,
          "estimatedBuyPrice": 93.38,
          "sellPrice": 100,
          "realizedPnl": 3063,
          "returnPct": 6.56,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-04-13",
          "sellDate": "2026-05-13",
          "symbol": "2377",
          "name": "微星",
          "shares": 500,
          "estimatedBuyPrice": 93.43,
          "sellPrice": 113,
          "realizedPnl": 9535,
          "returnPct": 20.41,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-04-22",
          "sellDate": "2026-05-22",
          "symbol": "6907",
          "name": "雅特力-KY",
          "shares": 1000,
          "estimatedBuyPrice": 110.72,
          "sellPrice": 119.5,
          "realizedPnl": 8315,
          "returnPct": 7.51,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-04-28",
          "sellDate": "2026-05-28",
          "symbol": "6143",
          "name": "振曜",
          "shares": 1000,
          "estimatedBuyPrice": 99.18,
          "sellPrice": 102.5,
          "realizedPnl": 2906,
          "returnPct": 2.93,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-05-08",
          "sellDate": "2026-06-08",
          "symbol": "3141",
          "name": "晶宏",
          "shares": 1000,
          "estimatedBuyPrice": 81.73,
          "sellPrice": 66.9,
          "realizedPnl": -15111,
          "returnPct": -18.49,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-05-08",
          "sellDate": "2026-06-08",
          "symbol": "4739",
          "name": "康普",
          "shares": 1000,
          "estimatedBuyPrice": 83.72,
          "sellPrice": 115,
          "realizedPnl": 30774,
          "returnPct": 36.76,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-05-09",
          "sellDate": "2026-06-09",
          "symbol": "2379",
          "name": "瑞昱",
          "shares": 55,
          "estimatedBuyPrice": 595.46,
          "sellPrice": 631,
          "realizedPnl": 1798,
          "returnPct": 5.49,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-05-12",
          "sellDate": "2026-06-12",
          "symbol": "6907",
          "name": "雅特力-KY",
          "shares": 50,
          "estimatedBuyPrice": 132.15,
          "sellPrice": 142.5,
          "realizedPnl": 485,
          "returnPct": 7.34,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-05-15",
          "sellDate": "2026-06-15",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "shares": 673,
          "estimatedBuyPrice": 82.36,
          "sellPrice": 97.6,
          "realizedPnl": 10093,
          "returnPct": 18.21,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-05-16",
          "sellDate": "2026-06-16",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "shares": 41,
          "estimatedBuyPrice": 96.43,
          "sellPrice": 98.15,
          "realizedPnl": 17,
          "returnPct": 0.43,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-05-16",
          "sellDate": "2026-06-16",
          "symbol": "2317",
          "name": "鴻海",
          "shares": 300,
          "estimatedBuyPrice": 273.02,
          "sellPrice": 270,
          "realizedPnl": -172,
          "returnPct": -0.21,
          "source": "舊交易紀錄"
        },
        {
          "buyDate": "2026-05-17",
          "sellDate": "2026-06-17",
          "symbol": "4739",
          "name": "康普",
          "shares": 500,
          "estimatedBuyPrice": 91.22,
          "sellPrice": 120.5,
          "realizedPnl": 14371,
          "returnPct": 31.51,
          "source": "舊交易紀錄"
        },
        {
          "sellDate": "2026-06-15",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "shares": 561,
          "estimatedBuyPrice": 81.47,
          "sellPrice": 97.65,
          "investmentCost": 45894,
          "realizedPnl": 8884,
          "returnPct": 19.35,
          "source": "2026/06/18 使用者提供"
        },
        {
          "sellDate": "2026-04-24",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "shares": 363,
          "estimatedBuyPrice": 65.62,
          "sellPrice": 71.55,
          "investmentCost": 23916,
          "realizedPnl": 2056,
          "returnPct": 8.59,
          "source": "2026/06/18 使用者提供"
        },
        {
          "sellDate": "2026-04-08",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "shares": 1396,
          "estimatedBuyPrice": 55.43,
          "sellPrice": 58.69,
          "investmentCost": 77689,
          "realizedPnl": 4230,
          "returnPct": 5.44,
          "source": "2026/06/18 使用者提供"
        },
        {
          "sellDate": "2026-03-25",
          "symbol": "6907",
          "name": "雅特力-KY",
          "shares": 1000,
          "estimatedBuyPrice": 30,
          "sellPrice": 132.5,
          "investmentCost": 30585,
          "realizedPnl": 101915,
          "returnPct": 333.21,
          "source": "2026/06/18 使用者提供"
        }
      ],
      "orders": [
        {
          "date": "2026-03-25",
          "symbol": "6907",
          "name": "雅特力-KY",
          "action": "sell",
          "price": 132.5,
          "shares": 1000,
          "status": "2026/06/18 使用者提供"
        },
        {
          "date": "2026-04-08",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "sell",
          "price": 58.69,
          "shares": 1396,
          "status": "2026/06/18 使用者提供"
        },
        {
          "date": "2026-04-24",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "sell",
          "price": 71.55,
          "shares": 363,
          "status": "2026/06/18 使用者提供"
        },
        {
          "date": "2026-06-15",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "sell",
          "price": 97.65,
          "shares": 561,
          "status": "2026/06/18 使用者提供"
        }
      ],
      "computed": {
        "positionCost": 815753.0,
        "realizedByDate": [
          {
            "date": "2026-03-25",
            "realizedPnl": 101915.0
          },
          {
            "date": "2026-04-08",
            "realizedPnl": 9880.0
          },
          {
            "date": "2026-04-10",
            "realizedPnl": 12835.0
          },
          {
            "date": "2026-04-24",
            "realizedPnl": 4294.0
          },
          {
            "date": "2026-04-29",
            "realizedPnl": 3319.0
          },
          {
            "date": "2026-05-13",
            "realizedPnl": 9535.0
          },
          {
            "date": "2026-05-22",
            "realizedPnl": 8315.0
          },
          {
            "date": "2026-05-28",
            "realizedPnl": 2906.0
          },
          {
            "date": "2026-06-08",
            "realizedPnl": 15663.0
          },
          {
            "date": "2026-06-09",
            "realizedPnl": 1798.0
          },
          {
            "date": "2026-06-12",
            "realizedPnl": 485.0
          },
          {
            "date": "2026-06-15",
            "realizedPnl": 18977.0
          },
          {
            "date": "2026-06-16",
            "realizedPnl": -155.0
          },
          {
            "date": "2026-06-17",
            "realizedPnl": 14371.0
          }
        ],
        "equitySeries": [
          {
            "date": "2026-03-08",
            "realizedPnl": 0.0,
            "unrealizedPnl": 0.0,
            "equity": 2000000.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-03-25",
            "realizedPnl": 101915.0,
            "unrealizedPnl": 0.0,
            "equity": 2101915.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-08",
            "realizedPnl": 111795.0,
            "unrealizedPnl": 0.0,
            "equity": 2111795.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-10",
            "realizedPnl": 124630.0,
            "unrealizedPnl": 0.0,
            "equity": 2124630.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-24",
            "realizedPnl": 128924.0,
            "unrealizedPnl": 0.0,
            "equity": 2128924.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-29",
            "realizedPnl": 132243.0,
            "unrealizedPnl": 0.0,
            "equity": 2132243.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-13",
            "realizedPnl": 141778.0,
            "unrealizedPnl": 0.0,
            "equity": 2141778.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-22",
            "realizedPnl": 150093.0,
            "unrealizedPnl": 0.0,
            "equity": 2150093.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-28",
            "realizedPnl": 152999.0,
            "unrealizedPnl": 0.0,
            "equity": 2152999.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-08",
            "realizedPnl": 168662.0,
            "unrealizedPnl": 0.0,
            "equity": 2168662.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-09",
            "realizedPnl": 170460.0,
            "unrealizedPnl": 0.0,
            "equity": 2170460.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-12",
            "realizedPnl": 170945.0,
            "unrealizedPnl": 0.0,
            "equity": 2170945.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-15",
            "realizedPnl": 189922.0,
            "unrealizedPnl": 0.0,
            "equity": 2189922.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-16",
            "realizedPnl": 189767.0,
            "unrealizedPnl": 0.0,
            "equity": 2189767.0,
            "drawdown": -155.0,
            "drawdownPct": -0.0070778776595696105
          },
          {
            "date": "2026-06-17",
            "realizedPnl": 204138.0,
            "unrealizedPnl": 0.0,
            "equity": 2204138.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-18",
            "realizedPnl": 204138.0,
            "unrealizedPnl": 181549.0,
            "equity": 2385687.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          }
        ],
        "contributions": [
          {
            "symbol": "00757",
            "name": "統一 FANG+",
            "realizedPnl": 256.0,
            "unrealizedPnl": 211841.0,
            "realizedCost": 232727.2727272727,
            "positionCost": 725915.0,
            "totalPnl": 212097.0,
            "totalCost": 958642.2727272727,
            "returnPct": 22.124728486737634
          },
          {
            "symbol": "6907",
            "name": "雅特力-KY",
            "realizedPnl": 110715.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 147911.67070608854,
            "positionCost": 0.0,
            "totalPnl": 110715.0,
            "totalCost": 147911.67070608854,
            "returnPct": 74.85210563269136
          },
          {
            "symbol": "4739",
            "name": "康普",
            "realizedPnl": 45145.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 129323.73922091161,
            "positionCost": 0.0,
            "totalPnl": 45145.0,
            "totalCost": 129323.73922091161,
            "returnPct": 34.90851739361096
          },
          {
            "symbol": "00830",
            "name": "國泰費城半導體",
            "realizedPnl": 32853.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 329265.01067002234,
            "positionCost": 0.0,
            "totalPnl": 32853.0,
            "totalCost": 329265.01067002234,
            "returnPct": 9.977677231220934
          },
          {
            "symbol": "6488",
            "name": "環球晶",
            "realizedPnl": 12835.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 108129.73883740524,
            "positionCost": 0.0,
            "totalPnl": 12835.0,
            "totalCost": 108129.73883740524,
            "returnPct": 11.87
          },
          {
            "symbol": "2377",
            "name": "微星",
            "realizedPnl": 12598.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 93409.3686141418,
            "positionCost": 0.0,
            "totalPnl": 12598.0,
            "totalCost": 93409.3686141418,
            "returnPct": 13.486869879230415
          },
          {
            "symbol": "6143",
            "name": "振曜",
            "realizedPnl": 2906.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 99180.88737201365,
            "positionCost": 0.0,
            "totalPnl": 2906.0,
            "totalCost": 99180.88737201365,
            "returnPct": 2.93
          },
          {
            "symbol": "2379",
            "name": "瑞昱",
            "realizedPnl": 1798.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 32750.455373406192,
            "positionCost": 0.0,
            "totalPnl": 1798.0,
            "totalCost": 32750.455373406192,
            "returnPct": 5.49
          },
          {
            "symbol": "2353",
            "name": "宏碁",
            "realizedPnl": 315.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 108471.65400350673,
            "positionCost": 0.0,
            "totalPnl": 315.0,
            "totalCost": 108471.65400350673,
            "returnPct": 0.29039844823405797
          },
          {
            "symbol": "2317",
            "name": "鴻海",
            "realizedPnl": -172.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 81904.76190476191,
            "positionCost": 0.0,
            "totalPnl": -172.0,
            "totalCost": 81904.76190476191,
            "returnPct": -0.21
          },
          {
            "symbol": "4166",
            "name": "友霖",
            "realizedPnl": 0.0,
            "unrealizedPnl": -3209.0,
            "realizedCost": 0.0,
            "positionCost": 28000.0,
            "totalPnl": -3209.0,
            "totalCost": 28000.0,
            "returnPct": -11.460714285714285
          },
          {
            "symbol": "3141",
            "name": "晶宏",
            "realizedPnl": -15111.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 81725.25689561926,
            "positionCost": 0.0,
            "totalPnl": -15111.0,
            "totalCost": 81725.25689561926,
            "returnPct": -18.490000000000002
          },
          {
            "symbol": "1760",
            "name": "寶齡富錦",
            "realizedPnl": 0.0,
            "unrealizedPnl": -27083.0,
            "realizedCost": 0.0,
            "positionCost": 61838.0,
            "totalPnl": -27083.0,
            "totalCost": 61838.0,
            "returnPct": -43.796694589087615
          }
        ],
        "stats": {
          "tradeCount": 23,
          "winCount": 20,
          "lossCount": 3,
          "winRatePct": 86.95652173913044,
          "avgWin": 10986.95,
          "avgLoss": -5200.333333333333,
          "profitFactor": 14.084930453176078,
          "bestTrade": 101915.0,
          "worstTrade": -15111.0,
          "maxDrawdown": -155.0,
          "maxDrawdownPct": -0.0070778776595696105
        }
      },
      "validation": {
        "status": "warning",
        "checks": [
          {
            "label": "已實現損益合計",
            "ok": true,
            "actual": 204138.0,
            "expected": 204138.0,
            "diff": 0.0
          },
          {
            "label": "未實現損益合計",
            "ok": true,
            "actual": 181549.0,
            "expected": 181549.0,
            "diff": 0.0
          },
          {
            "label": "股票庫存市值合計",
            "ok": true,
            "actual": 997302.0,
            "expected": 997302.0,
            "diff": 0.0
          },
          {
            "label": "總損益",
            "ok": true,
            "actual": 385687.0,
            "expected": 385687.0,
            "diff": 0.0
          },
          {
            "label": "目前推估總資產",
            "ok": true,
            "actual": 2385687.0,
            "expected": 2385687.0,
            "diff": 0.0
          },
          {
            "label": "推估現金",
            "ok": true,
            "actual": 1388385.0,
            "expected": 1388385.0,
            "diff": 0.0
          },
          {
            "label": "總報酬率",
            "ok": true,
            "actual": 19.2843,
            "expected": 19.28,
            "diff": 0.0043
          },
          {
            "label": "00757 庫存損益",
            "ok": true,
            "actual": 211841.0,
            "expected": 211841.0,
            "diff": 0.0
          },
          {
            "label": "1760 庫存損益",
            "ok": true,
            "actual": -27083.0,
            "expected": -27083.0,
            "diff": 0.0
          },
          {
            "label": "4166 庫存損益",
            "ok": true,
            "actual": -3209.0,
            "expected": -3209.0,
            "diff": 0.0
          }
        ],
        "warnings": [
          "成交/委託紀錄標記為不完整；不以流水股數反推目前庫存。"
        ]
      }
    },
    "us": {
      "market": "us",
      "label": "美股",
      "currency": "USD",
      "currencyLabel": "美元",
      "initialCapital": 30000,
      "currentDate": "2026-06-18",
      "orderLogComplete": true,
      "dataQuality": [
        "總覽、庫存合計、已實現損益合計可內部驗算。",
        "2026/06/18 GEV 賣出 1 股後，目前庫存為 BDC 24 股、GEV 0 股。",
        "COHR 2026-06-05/2026-06-06 日期需確認是美股交易日或台灣券商顯示日；績效表採 2026-06-05。"
      ],
      "summary": {
        "realizedPnl": 1395.44,
        "unrealizedPnl": 321.25,
        "totalPnl": 1716.69,
        "currentAssets": 31716.69,
        "totalReturnPct": 5.72,
        "cash": 28783.65,
        "marketValue": 2933.04
      },
      "positions": [
        {
          "symbol": "BDC",
          "name": "百通",
          "shares": 24,
          "marketValue": 2933.04,
          "cost": 2611.79,
          "unrealizedPnl": 321.25,
          "returnPct": 12.3
        }
      ],
      "realizedTrades": [
        {
          "sellDate": "2026-05-29",
          "symbol": "NTAP",
          "name": "NetApp",
          "shares": 15,
          "sellPrice": 183.236,
          "realizedPnl": 662.16,
          "returnPct": 31.77,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-01",
          "symbol": "HPE",
          "name": "HP Enterprise",
          "shares": 30,
          "sellPrice": 44.4,
          "realizedPnl": 192.68,
          "returnPct": 16.93,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-02",
          "symbol": "COHR",
          "name": "Coherent",
          "shares": 5,
          "sellPrice": 396.16,
          "realizedPnl": 190.69,
          "returnPct": 10.66,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-02",
          "symbol": "QCOM",
          "name": "Qualcomm",
          "shares": 5,
          "sellPrice": 240.487,
          "realizedPnl": 45.51,
          "returnPct": 3.94,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-02",
          "symbol": "QCOM",
          "name": "Qualcomm",
          "shares": 5,
          "sellPrice": 234.5,
          "realizedPnl": 14.4,
          "returnPct": 1.24,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-03",
          "symbol": "GEV",
          "name": "GE Vernova",
          "shares": 2,
          "sellPrice": 987.4,
          "realizedPnl": 69.75,
          "returnPct": 3.66,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-03",
          "symbol": "GEV",
          "name": "GE Vernova",
          "shares": 1,
          "sellPrice": 985,
          "realizedPnl": 10.89,
          "returnPct": 1.12,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-05",
          "symbol": "NTAP",
          "name": "NetApp",
          "shares": 6,
          "sellPrice": 169.65,
          "realizedPnl": -78.03,
          "returnPct": -7.13,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-05",
          "symbol": "COHR",
          "name": "Coherent",
          "shares": 3,
          "sellPrice": 401.5,
          "realizedPnl": 41.13,
          "returnPct": 3.54,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-05",
          "symbol": "COHR",
          "name": "Coherent",
          "shares": 3,
          "sellPrice": 403.2,
          "realizedPnl": 42.13,
          "returnPct": 3.61,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-08",
          "symbol": "ETN",
          "name": "Eaton",
          "shares": 4,
          "sellPrice": 405.171,
          "realizedPnl": 2.25,
          "returnPct": 0.14,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-08",
          "symbol": "ETN",
          "name": "Eaton",
          "shares": 4,
          "sellPrice": 405.1,
          "realizedPnl": -16.07,
          "returnPct": -0.98,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-11",
          "symbol": "COHR",
          "name": "Coherent",
          "shares": 4,
          "sellPrice": 365.8,
          "realizedPnl": 47.03,
          "returnPct": 3.32,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-11",
          "symbol": "COHR",
          "name": "Coherent",
          "shares": 4,
          "sellPrice": 365.08,
          "realizedPnl": -30.9,
          "returnPct": -2.07,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-11",
          "symbol": "NTAP",
          "name": "NetApp",
          "shares": 5,
          "sellPrice": 157.7,
          "realizedPnl": -95,
          "returnPct": -10.76,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-15",
          "symbol": "GEV",
          "name": "GE Vernova",
          "shares": 2,
          "sellPrice": 969.73,
          "realizedPnl": 11.47,
          "returnPct": 0.6,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-16",
          "symbol": "GEV",
          "name": "GE Vernova",
          "shares": 1,
          "sellPrice": 1001,
          "realizedPnl": 94.91,
          "returnPct": 10.48,
          "source": "已實現損益底稿"
        },
        {
          "sellDate": "2026-06-18",
          "symbol": "GEV",
          "name": "GE Vernova",
          "shares": 1,
          "sellPrice": 1093,
          "investmentCost": 902.56,
          "realizedPnl": 190.44,
          "returnPct": 21.1,
          "source": "2026/06/18 使用者提供"
        }
      ],
      "orders": [
        {
          "date": "2026-05-26",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "buy",
          "orderPrice": 408.4,
          "fillPrice": 408.4,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-05-26",
          "symbol": "NTAP",
          "name": "NetApp",
          "action": "buy",
          "orderPrice": 138,
          "fillPrice": 138,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-05-26",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "buy",
          "orderPrice": 408.47,
          "fillPrice": 408.47,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-05-26",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "buy",
          "orderPrice": 406.52,
          "fillPrice": 0,
          "shares": 0,
          "status": "刪單成功"
        },
        {
          "date": "2026-05-26",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "buy",
          "orderPrice": 407.4,
          "fillPrice": 0,
          "shares": 0,
          "status": "刪單成功"
        },
        {
          "date": "2026-05-26",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "buy",
          "orderPrice": 407,
          "fillPrice": 0,
          "shares": 0,
          "status": "刪單成功"
        },
        {
          "date": "2026-05-26",
          "symbol": "NTAP",
          "name": "NetApp",
          "action": "buy",
          "orderPrice": 140.45,
          "fillPrice": 139.2446,
          "shares": 10,
          "status": "完全成交"
        },
        {
          "date": "2026-05-26",
          "symbol": "HPE",
          "name": "HP Enterprise",
          "action": "buy",
          "orderPrice": 37.91,
          "fillPrice": 37.91,
          "shares": 30,
          "status": "完全成交"
        },
        {
          "date": "2026-05-29",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "buy",
          "orderPrice": 972.5,
          "fillPrice": 972.5,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-05-29",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "buy",
          "orderPrice": 357.5,
          "fillPrice": 357.4099,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-05-29",
          "symbol": "NTAP",
          "name": "NetApp",
          "action": "sell",
          "orderPrice": 183,
          "fillPrice": 183.2356,
          "shares": 15,
          "status": "完全成交"
        },
        {
          "date": "2026-06-01",
          "symbol": "QCOM",
          "name": "Qualcomm",
          "action": "buy",
          "orderPrice": 231,
          "fillPrice": 231,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-01",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "buy",
          "orderPrice": 399.8,
          "fillPrice": 399.8,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-01",
          "symbol": "HPE",
          "name": "HP Enterprise",
          "action": "sell",
          "orderPrice": 44.4,
          "fillPrice": 44.4,
          "shares": 30,
          "status": "完全成交"
        },
        {
          "date": "2026-06-01",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "buy",
          "orderPrice": 950,
          "fillPrice": 949.09,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-01",
          "symbol": "QCOM",
          "name": "Qualcomm",
          "action": "buy",
          "orderPrice": 231.3,
          "fillPrice": 231.24,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-02",
          "symbol": "QCOM",
          "name": "Qualcomm",
          "action": "sell",
          "orderPrice": 240,
          "fillPrice": 240.487,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-02",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "buy",
          "orderPrice": 952.8,
          "fillPrice": 952.8,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-02",
          "symbol": "QCOM",
          "name": "Qualcomm",
          "action": "sell",
          "orderPrice": 234.5,
          "fillPrice": 234.5,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-02",
          "symbol": "NTAP",
          "name": "NetApp",
          "action": "buy",
          "orderPrice": 183.5,
          "fillPrice": 183.4299,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-02",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "sell",
          "orderPrice": 396,
          "fillPrice": 396.1601,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-03",
          "symbol": "BDC",
          "name": "Belden",
          "action": "buy",
          "orderPrice": 106.72,
          "fillPrice": 0,
          "shares": 0,
          "status": "刪單成功"
        },
        {
          "date": "2026-06-03",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "sell",
          "orderPrice": 987.4,
          "fillPrice": 987.4,
          "shares": 2,
          "status": "完全成交"
        },
        {
          "date": "2026-06-03",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "sell",
          "orderPrice": 985,
          "fillPrice": 985,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-03",
          "symbol": "BDC",
          "name": "Belden",
          "action": "buy",
          "orderPrice": 109.46,
          "fillPrice": 109.46,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-03",
          "symbol": "BDC",
          "name": "Belden",
          "action": "buy",
          "orderPrice": 109.46,
          "fillPrice": 109.46,
          "shares": 10,
          "status": "完全成交"
        },
        {
          "date": "2026-06-03",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "buy",
          "orderPrice": 416.13,
          "fillPrice": 416.0799,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-03",
          "symbol": "BDC",
          "name": "Belden",
          "action": "buy",
          "orderPrice": 105.1,
          "fillPrice": 0,
          "shares": 0,
          "status": "委託成功/未成交"
        },
        {
          "date": "2026-06-04",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "buy",
          "orderPrice": 960.5,
          "fillPrice": 960.5,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-04",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "buy",
          "orderPrice": 964.35,
          "fillPrice": 964.35,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-04",
          "symbol": "NTAP",
          "name": "NetApp",
          "action": "buy",
          "orderPrice": 176,
          "fillPrice": 176,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-06-04",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "buy",
          "orderPrice": 387.55,
          "fillPrice": 387.1486,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-06-04",
          "symbol": "NTAP",
          "name": "NetApp",
          "action": "buy",
          "orderPrice": 177.07,
          "fillPrice": 177.07,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-06-04",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "buy",
          "orderPrice": 388.51,
          "fillPrice": 388.51,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-06-04",
          "symbol": "BDC",
          "name": "Belden",
          "action": "buy",
          "orderPrice": 108.44,
          "fillPrice": 0,
          "shares": 0,
          "status": "刪單成功"
        },
        {
          "date": "2026-06-04",
          "symbol": "BDC",
          "name": "Belden",
          "action": "buy",
          "orderPrice": 109,
          "fillPrice": 109,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-06-05",
          "symbol": "NTAP",
          "name": "NetApp",
          "action": "sell",
          "orderPrice": 169.6,
          "fillPrice": 169.6501,
          "shares": 6,
          "status": "完全成交"
        },
        {
          "date": "2026-06-05",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "buy",
          "orderPrice": 399.96,
          "fillPrice": 399.96,
          "shares": 2,
          "status": "完全成交"
        },
        {
          "date": "2026-06-06",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "sell",
          "orderPrice": 401.5,
          "fillPrice": 401.5,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-06-06",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "sell",
          "orderPrice": 403.2,
          "fillPrice": 403.2,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-06-06",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "sell",
          "orderPrice": 403.2,
          "fillPrice": 0,
          "shares": 0,
          "status": "刪單成功"
        },
        {
          "date": "2026-06-08",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "sell",
          "orderPrice": 405,
          "fillPrice": 405.171,
          "shares": 4,
          "status": "完全成交"
        },
        {
          "date": "2026-06-08",
          "symbol": "ETN",
          "name": "Eaton",
          "action": "sell",
          "orderPrice": 405.1,
          "fillPrice": 405.1,
          "shares": 4,
          "status": "完全成交"
        },
        {
          "date": "2026-06-08",
          "symbol": "BDC",
          "name": "Belden",
          "action": "buy",
          "orderPrice": 106.8,
          "fillPrice": 106.8,
          "shares": 6,
          "status": "完全成交"
        },
        {
          "date": "2026-06-09",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "buy",
          "orderPrice": 901,
          "fillPrice": 901,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-09",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "buy",
          "orderPrice": 904.53,
          "fillPrice": 904.53,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-09",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "buy",
          "orderPrice": 372.2,
          "fillPrice": 372.2,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-10",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "buy",
          "orderPrice": 347.45,
          "fillPrice": 347.213,
          "shares": 3,
          "status": "完全成交"
        },
        {
          "date": "2026-06-11",
          "symbol": "NTAP",
          "name": "NetApp",
          "action": "sell",
          "orderPrice": 157.7,
          "fillPrice": 157.7,
          "shares": 5,
          "status": "完全成交"
        },
        {
          "date": "2026-06-11",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "sell",
          "orderPrice": 365.8,
          "fillPrice": 365.8,
          "shares": 4,
          "status": "完全成交"
        },
        {
          "date": "2026-06-11",
          "symbol": "COHR",
          "name": "Coherent",
          "action": "sell",
          "orderPrice": 365.08,
          "fillPrice": 365.08,
          "shares": 4,
          "status": "完全成交"
        },
        {
          "date": "2026-06-15",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "sell",
          "orderPrice": 969.73,
          "fillPrice": 969.73,
          "shares": 2,
          "status": "完全成交"
        },
        {
          "date": "2026-06-15",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "sell",
          "orderPrice": 969.4,
          "fillPrice": 0,
          "shares": 0,
          "status": "刪單成功"
        },
        {
          "date": "2026-06-15",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "sell",
          "orderPrice": 971.24,
          "fillPrice": 0,
          "shares": 0,
          "status": "刪單成功"
        },
        {
          "date": "2026-06-16",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "sell",
          "orderPrice": 1001,
          "fillPrice": 1001,
          "shares": 1,
          "status": "完全成交"
        },
        {
          "date": "2026-06-18",
          "symbol": "GEV",
          "name": "GE Vernova",
          "action": "sell",
          "orderPrice": 1093,
          "fillPrice": 1093,
          "shares": 1,
          "status": "完全成交"
        }
      ],
      "computed": {
        "positionCost": 2611.79,
        "realizedByDate": [
          {
            "date": "2026-05-29",
            "realizedPnl": 662.16
          },
          {
            "date": "2026-06-01",
            "realizedPnl": 192.68
          },
          {
            "date": "2026-06-02",
            "realizedPnl": 250.6
          },
          {
            "date": "2026-06-03",
            "realizedPnl": 80.64
          },
          {
            "date": "2026-06-05",
            "realizedPnl": 5.230000000000004
          },
          {
            "date": "2026-06-08",
            "realizedPnl": -13.82
          },
          {
            "date": "2026-06-11",
            "realizedPnl": -78.87
          },
          {
            "date": "2026-06-15",
            "realizedPnl": 11.47
          },
          {
            "date": "2026-06-16",
            "realizedPnl": 94.91
          },
          {
            "date": "2026-06-18",
            "realizedPnl": 190.44
          }
        ],
        "equitySeries": [
          {
            "date": "2026-05-26",
            "realizedPnl": 0.0,
            "unrealizedPnl": 0.0,
            "equity": 30000.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-29",
            "realizedPnl": 662.16,
            "unrealizedPnl": 0.0,
            "equity": 30662.16,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-01",
            "realizedPnl": 854.8399999999999,
            "unrealizedPnl": 0.0,
            "equity": 30854.84,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-02",
            "realizedPnl": 1105.4399999999998,
            "unrealizedPnl": 0.0,
            "equity": 31105.44,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-03",
            "realizedPnl": 1186.08,
            "unrealizedPnl": 0.0,
            "equity": 31186.08,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-05",
            "realizedPnl": 1191.31,
            "unrealizedPnl": 0.0,
            "equity": 31191.31,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-08",
            "realizedPnl": 1177.49,
            "unrealizedPnl": 0.0,
            "equity": 31177.49,
            "drawdown": -13.819999999999709,
            "drawdownPct": -0.04430721248963159
          },
          {
            "date": "2026-06-11",
            "realizedPnl": 1098.62,
            "unrealizedPnl": 0.0,
            "equity": 31098.62,
            "drawdown": -92.69000000000233,
            "drawdownPct": -0.2971661017123113
          },
          {
            "date": "2026-06-15",
            "realizedPnl": 1110.09,
            "unrealizedPnl": 0.0,
            "equity": 31110.09,
            "drawdown": -81.22000000000116,
            "drawdownPct": -0.2603930389586111
          },
          {
            "date": "2026-06-16",
            "realizedPnl": 1205.0,
            "unrealizedPnl": 0.0,
            "equity": 31205.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-18",
            "realizedPnl": 1395.44,
            "unrealizedPnl": 321.25,
            "equity": 31716.69,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          }
        ],
        "contributions": [
          {
            "symbol": "NTAP",
            "name": "NetApp",
            "realizedPnl": 489.13,
            "unrealizedPnl": 0.0,
            "realizedCost": 4061.5199361195073,
            "positionCost": 0.0,
            "totalPnl": 489.13,
            "totalCost": 4061.5199361195073,
            "returnPct": 12.043028415301313
          },
          {
            "symbol": "GEV",
            "name": "GE Vernova",
            "realizedPnl": 377.46,
            "unrealizedPnl": 0.0,
            "realizedCost": 6597.915571148495,
            "positionCost": 0.0,
            "totalPnl": 377.46,
            "totalCost": 6597.915571148495,
            "returnPct": 5.720897697608698
          },
          {
            "symbol": "BDC",
            "name": "百通",
            "realizedPnl": 0.0,
            "unrealizedPnl": 321.25,
            "realizedCost": 0.0,
            "positionCost": 2611.79,
            "totalPnl": 321.25,
            "totalCost": 2611.79,
            "returnPct": 12.299993491054028
          },
          {
            "symbol": "COHR",
            "name": "Coherent",
            "realizedPnl": 290.08000000000004,
            "unrealizedPnl": 0.0,
            "realizedCost": 7027.0570790917545,
            "positionCost": 0.0,
            "totalPnl": 290.08000000000004,
            "totalCost": 7027.0570790917545,
            "returnPct": 4.128043884304022
          },
          {
            "symbol": "HPE",
            "name": "HP Enterprise",
            "realizedPnl": 192.68,
            "unrealizedPnl": 0.0,
            "realizedCost": 1138.0980507974011,
            "positionCost": 0.0,
            "totalPnl": 192.68,
            "totalCost": 1138.0980507974011,
            "returnPct": 16.93
          },
          {
            "symbol": "QCOM",
            "name": "Qualcomm",
            "realizedPnl": 59.91,
            "unrealizedPnl": 0.0,
            "realizedCost": 2316.3664647126247,
            "positionCost": 0.0,
            "totalPnl": 59.91,
            "totalCost": 2316.3664647126247,
            "returnPct": 2.5863783176222337
          },
          {
            "symbol": "ETN",
            "name": "Eaton",
            "realizedPnl": -13.82,
            "unrealizedPnl": 0.0,
            "realizedCost": 3246.938775510204,
            "positionCost": 0.0,
            "totalPnl": -13.82,
            "totalCost": 3246.938775510204,
            "returnPct": -0.4256316781898178
          }
        ],
        "stats": {
          "tradeCount": 18,
          "winCount": 14,
          "lossCount": 4,
          "winRatePct": 77.77777777777779,
          "avgWin": 115.38857142857144,
          "avgLoss": -55.0,
          "profitFactor": 7.3429090909090915,
          "bestTrade": 662.16,
          "worstTrade": -95.0,
          "maxDrawdown": -92.69000000000233,
          "maxDrawdownPct": -0.2971661017123113
        }
      },
      "validation": {
        "status": "warning",
        "checks": [
          {
            "label": "已實現損益合計",
            "ok": true,
            "actual": 1395.44,
            "expected": 1395.44,
            "diff": 0.0
          },
          {
            "label": "未實現損益合計",
            "ok": true,
            "actual": 321.25,
            "expected": 321.25,
            "diff": 0.0
          },
          {
            "label": "股票庫存市值合計",
            "ok": true,
            "actual": 2933.04,
            "expected": 2933.04,
            "diff": 0.0
          },
          {
            "label": "總損益",
            "ok": true,
            "actual": 1716.69,
            "expected": 1716.69,
            "diff": 0.0
          },
          {
            "label": "目前推估總資產",
            "ok": true,
            "actual": 31716.69,
            "expected": 31716.69,
            "diff": 0.0
          },
          {
            "label": "推估現金",
            "ok": true,
            "actual": 28783.65,
            "expected": 28783.65,
            "diff": -0.0
          },
          {
            "label": "總報酬率",
            "ok": true,
            "actual": 5.7223,
            "expected": 5.72,
            "diff": 0.0023
          },
          {
            "label": "BDC 庫存損益",
            "ok": true,
            "actual": 321.25,
            "expected": 321.25,
            "diff": 0.0
          },
          {
            "label": "BDC 完全成交股數對庫存",
            "ok": true,
            "actual": 24.0,
            "expected": 24.0,
            "diff": 0.0
          },
          {
            "label": "COHR 完全成交股數對庫存",
            "ok": true,
            "actual": 0.0,
            "expected": 0.0,
            "diff": 0.0
          },
          {
            "label": "ETN 完全成交股數對庫存",
            "ok": true,
            "actual": 0.0,
            "expected": 0.0,
            "diff": 0.0
          },
          {
            "label": "GEV 完全成交股數對庫存",
            "ok": true,
            "actual": 0.0,
            "expected": 0.0,
            "diff": 0.0
          },
          {
            "label": "HPE 完全成交股數對庫存",
            "ok": true,
            "actual": 0.0,
            "expected": 0.0,
            "diff": 0.0
          },
          {
            "label": "NTAP 完全成交股數對庫存",
            "ok": true,
            "actual": 0.0,
            "expected": 0.0,
            "diff": 0.0
          },
          {
            "label": "QCOM 完全成交股數對庫存",
            "ok": true,
            "actual": 0.0,
            "expected": 0.0,
            "diff": 0.0
          }
        ],
        "warnings": [
          "COHR 2026-06-05 已實現日期與成交紀錄日期不同；成交紀錄日期: 2026-06-06"
        ]
      }
    }
  },
  "validation": {
    "tw": {
      "status": "warning",
      "checks": [
        {
          "label": "已實現損益合計",
          "ok": true,
          "actual": 204138.0,
          "expected": 204138.0,
          "diff": 0.0
        },
        {
          "label": "未實現損益合計",
          "ok": true,
          "actual": 181549.0,
          "expected": 181549.0,
          "diff": 0.0
        },
        {
          "label": "股票庫存市值合計",
          "ok": true,
          "actual": 997302.0,
          "expected": 997302.0,
          "diff": 0.0
        },
        {
          "label": "總損益",
          "ok": true,
          "actual": 385687.0,
          "expected": 385687.0,
          "diff": 0.0
        },
        {
          "label": "目前推估總資產",
          "ok": true,
          "actual": 2385687.0,
          "expected": 2385687.0,
          "diff": 0.0
        },
        {
          "label": "推估現金",
          "ok": true,
          "actual": 1388385.0,
          "expected": 1388385.0,
          "diff": 0.0
        },
        {
          "label": "總報酬率",
          "ok": true,
          "actual": 19.2843,
          "expected": 19.28,
          "diff": 0.0043
        },
        {
          "label": "00757 庫存損益",
          "ok": true,
          "actual": 211841.0,
          "expected": 211841.0,
          "diff": 0.0
        },
        {
          "label": "1760 庫存損益",
          "ok": true,
          "actual": -27083.0,
          "expected": -27083.0,
          "diff": 0.0
        },
        {
          "label": "4166 庫存損益",
          "ok": true,
          "actual": -3209.0,
          "expected": -3209.0,
          "diff": 0.0
        }
      ],
      "warnings": [
        "成交/委託紀錄標記為不完整；不以流水股數反推目前庫存。"
      ]
    },
    "us": {
      "status": "warning",
      "checks": [
        {
          "label": "已實現損益合計",
          "ok": true,
          "actual": 1395.44,
          "expected": 1395.44,
          "diff": 0.0
        },
        {
          "label": "未實現損益合計",
          "ok": true,
          "actual": 321.25,
          "expected": 321.25,
          "diff": 0.0
        },
        {
          "label": "股票庫存市值合計",
          "ok": true,
          "actual": 2933.04,
          "expected": 2933.04,
          "diff": 0.0
        },
        {
          "label": "總損益",
          "ok": true,
          "actual": 1716.69,
          "expected": 1716.69,
          "diff": 0.0
        },
        {
          "label": "目前推估總資產",
          "ok": true,
          "actual": 31716.69,
          "expected": 31716.69,
          "diff": 0.0
        },
        {
          "label": "推估現金",
          "ok": true,
          "actual": 28783.65,
          "expected": 28783.65,
          "diff": -0.0
        },
        {
          "label": "總報酬率",
          "ok": true,
          "actual": 5.7223,
          "expected": 5.72,
          "diff": 0.0023
        },
        {
          "label": "BDC 庫存損益",
          "ok": true,
          "actual": 321.25,
          "expected": 321.25,
          "diff": 0.0
        },
        {
          "label": "BDC 完全成交股數對庫存",
          "ok": true,
          "actual": 24.0,
          "expected": 24.0,
          "diff": 0.0
        },
        {
          "label": "COHR 完全成交股數對庫存",
          "ok": true,
          "actual": 0.0,
          "expected": 0.0,
          "diff": 0.0
        },
        {
          "label": "ETN 完全成交股數對庫存",
          "ok": true,
          "actual": 0.0,
          "expected": 0.0,
          "diff": 0.0
        },
        {
          "label": "GEV 完全成交股數對庫存",
          "ok": true,
          "actual": 0.0,
          "expected": 0.0,
          "diff": 0.0
        },
        {
          "label": "HPE 完全成交股數對庫存",
          "ok": true,
          "actual": 0.0,
          "expected": 0.0,
          "diff": 0.0
        },
        {
          "label": "NTAP 完全成交股數對庫存",
          "ok": true,
          "actual": 0.0,
          "expected": 0.0,
          "diff": 0.0
        },
        {
          "label": "QCOM 完全成交股數對庫存",
          "ok": true,
          "actual": 0.0,
          "expected": 0.0,
          "diff": 0.0
        }
      ],
      "warnings": [
        "COHR 2026-06-05 已實現日期與成交紀錄日期不同；成交紀錄日期: 2026-06-06"
      ]
    }
  }
};
