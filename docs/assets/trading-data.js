window.TRADING_DASHBOARD = {
  "version": 1,
  "updatedAt": "2026-07-08",
  "sourceNote": "User-provided ChatGPT整理交易紀錄; dashboard validation checks internal reconciliation only, not broker screenshot fidelity.",
  "markets": {
    "tw": {
      "market": "tw",
      "label": "台股",
      "currency": "TWD",
      "currencyLabel": "台幣",
      "initialCapital": 2000000,
      "currentDate": "2026-07-08",
      "currentTimestamp": "2026-07-08 使用者截圖",
      "orderLogComplete": false,
      "dataQuality": [
        "舊交易紀錄、2026/06/18 新增交易、2026/06/22 鴻海賣出與 2026/07/08 昇佳電子庫存截圖已合併累計。",
        "2026/07/08 持倉快照新增 6732 昇佳電子；截圖未列投入成本，成本由損益與報酬率回推。",
        "成交/委託紀錄不是完整台帳；資產曲線採已實現損益事件 + 最新未實現庫存快照，不代表完整逐日市值曲線。"
      ],
      "summary": {
        "realizedPnl": 205711,
        "unrealizedPnl": 205589,
        "totalPnl": 411300,
        "currentAssets": 2411300,
        "totalReturnPct": 20.57,
        "cash": 1215071,
        "marketValue": 1196229,
        "brokerGrossMarketValue": 1196229,
        "brokerPositionReturnPct": 20.75
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
          "returnPct": 29.18,
          "strategyTag": "長期投資"
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
        },
        {
          "symbol": "6732",
          "name": "昇佳電子",
          "shares": 400,
          "averagePrice": 176.58,
          "currentPrice": 200.07,
          "marketValue": 80026,
          "cost": 70632,
          "unrealizedPnl": 9394,
          "returnPct": 13.3,
          "source": "2026/07/08 使用者截圖"
        },
        {
          "symbol": "6732",
          "name": "昇佳電子",
          "shares": 205,
          "averagePrice": 174.26,
          "currentPrice": 200.17,
          "marketValue": 41035,
          "cost": 35723,
          "unrealizedPnl": 5312,
          "returnPct": 14.87,
          "source": "2026/07/08 使用者截圖"
        },
        {
          "symbol": "6732",
          "name": "昇佳電子",
          "shares": 399,
          "averagePrice": 171.76,
          "currentPrice": 195.15,
          "marketValue": 77866,
          "cost": 68532,
          "unrealizedPnl": 9334,
          "returnPct": 13.62,
          "source": "2026/07/08 使用者截圖"
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
          "sellDate": "2026-06-22",
          "symbol": "2317",
          "name": "鴻海",
          "shares": 300,
          "estimatedBuyPrice": 268.89,
          "sellPrice": 275,
          "investmentCost": 80667,
          "realizedPnl": 1573,
          "returnPct": 1.95,
          "source": "2026/07/08 使用者提供"
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
        },
        {
          "date": "2026-06-22",
          "symbol": "2317",
          "name": "鴻海",
          "action": "sell",
          "price": 275,
          "shares": 300,
          "status": "2026/07/08 使用者提供"
        }
      ],
      "computed": {
        "positionCost": 990640.0,
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
          },
          {
            "date": "2026-06-22",
            "realizedPnl": 1573.0
          }
        ],
        "equitySeries": [
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
            "date": "2026-06-22",
            "realizedPnl": 205711.0,
            "unrealizedPnl": 0.0,
            "equity": 2205711.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-07-08",
            "realizedPnl": 205711.0,
            "unrealizedPnl": 205589.0,
            "equity": 2411300.0,
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
            "symbol": "6732",
            "name": "昇佳電子",
            "realizedPnl": 0.0,
            "unrealizedPnl": 24040.0,
            "realizedCost": 0.0,
            "positionCost": 174887.0,
            "totalPnl": 24040.0,
            "totalCost": 174887.0,
            "returnPct": 13.746018857891096
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
            "symbol": "2317",
            "name": "鴻海",
            "realizedPnl": 1401.0,
            "unrealizedPnl": 0.0,
            "realizedCost": 162571.7619047619,
            "positionCost": 0.0,
            "totalPnl": 1401.0,
            "totalCost": 162571.7619047619,
            "returnPct": 0.861773276973363
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
          "tradeCount": 24,
          "winCount": 21,
          "lossCount": 3,
          "winRatePct": 87.5,
          "avgWin": 10538.666666666666,
          "avgLoss": -5200.333333333333,
          "profitFactor": 14.18575732324851,
          "bestTrade": 101915.0,
          "worstTrade": -15111.0,
          "maxDrawdown": -155.0,
          "maxDrawdownPct": -0.0070778776595696105
        },
        "postSaleAnalysis": [
          {
            "eventId": "2026-04-08-00830-1",
            "sellDate": "2026-04-08",
            "symbol": "00830",
            "name": "國泰費城半導體",
            "shares": 1000.0,
            "sellPrice": 58.65,
            "observedTradingDays": 50,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-09",
                "price": 59.35,
                "returnPct": 1.193520886615529
              },
              "3": {
                "date": "2026-04-13",
                "price": 61.65,
                "returnPct": 5.115089514066495
              },
              "5": {
                "date": "2026-04-15",
                "price": 64.45,
                "returnPct": 9.889173060528567
              },
              "10": {
                "date": "2026-04-22",
                "price": 68.05,
                "returnPct": 16.027280477408357
              },
              "20": {
                "date": "2026-05-07",
                "price": 79.55,
                "returnPct": 35.63512361466326
              }
            },
            "mfePct": 35.80562659846549,
            "maePct": 0.8525149190110826,
            "latestDate": "2026-06-18",
            "latestPrice": 97.0,
            "latestReturnPct": 65.38789428815004
          },
          {
            "eventId": "2026-04-08-00830-2",
            "sellDate": "2026-04-08",
            "symbol": "00830",
            "name": "國泰費城半導體",
            "shares": 845.0,
            "sellPrice": 58.55,
            "observedTradingDays": 50,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-09",
                "price": 59.35,
                "returnPct": 1.366353543979515
              },
              "3": {
                "date": "2026-04-13",
                "price": 61.65,
                "returnPct": 5.294619982920579
              },
              "5": {
                "date": "2026-04-15",
                "price": 64.45,
                "returnPct": 10.076857386848847
              },
              "10": {
                "date": "2026-04-22",
                "price": 68.05,
                "returnPct": 16.22544833475661
              },
              "20": {
                "date": "2026-05-07",
                "price": 79.55,
                "returnPct": 35.86678052946199
              }
            },
            "mfePct": 36.03757472245945,
            "maePct": 1.0247651579846417,
            "latestDate": "2026-06-18",
            "latestPrice": 97.0,
            "latestReturnPct": 65.67036720751496
          },
          {
            "eventId": "2026-04-08-2353-3",
            "sellDate": "2026-04-08",
            "symbol": "2353",
            "name": "宏碁",
            "shares": 2000.0,
            "sellPrice": 27.35,
            "observedTradingDays": 50,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-09",
                "price": 27.1,
                "returnPct": -0.9140767824497242
              },
              "3": {
                "date": "2026-04-13",
                "price": 27.1,
                "returnPct": -0.9140767824497242
              },
              "5": {
                "date": "2026-04-15",
                "price": 27.5,
                "returnPct": 0.5484460694698212
              },
              "10": {
                "date": "2026-04-22",
                "price": 28.3,
                "returnPct": 3.4734917733089565
              },
              "20": {
                "date": "2026-05-07",
                "price": 28.1,
                "returnPct": 2.7422303473491727
              }
            },
            "mfePct": 6.764168190127973,
            "maePct": -1.2797074954296161,
            "latestDate": "2026-06-18",
            "latestPrice": 34.4,
            "latestReturnPct": 25.776965265082264
          },
          {
            "eventId": "2026-04-08-2353-4",
            "sellDate": "2026-04-08",
            "symbol": "2353",
            "name": "宏碁",
            "shares": 2000.0,
            "sellPrice": 27.35,
            "observedTradingDays": 50,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-09",
                "price": 27.1,
                "returnPct": -0.9140767824497242
              },
              "3": {
                "date": "2026-04-13",
                "price": 27.1,
                "returnPct": -0.9140767824497242
              },
              "5": {
                "date": "2026-04-15",
                "price": 27.5,
                "returnPct": 0.5484460694698212
              },
              "10": {
                "date": "2026-04-22",
                "price": 28.3,
                "returnPct": 3.4734917733089565
              },
              "20": {
                "date": "2026-05-07",
                "price": 28.1,
                "returnPct": 2.7422303473491727
              }
            },
            "mfePct": 6.764168190127973,
            "maePct": -1.2797074954296161,
            "latestDate": "2026-06-18",
            "latestPrice": 34.4,
            "latestReturnPct": 25.776965265082264
          },
          {
            "eventId": "2026-04-10-6488-5",
            "sellDate": "2026-04-10",
            "symbol": "6488",
            "name": "環球晶",
            "shares": 250.0,
            "sellPrice": 486.0,
            "observedTradingDays": 48,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-13",
                "price": 499.5,
                "returnPct": 2.777777777777768
              },
              "3": {
                "date": "2026-04-15",
                "price": 516.0,
                "returnPct": 6.172839506172845
              },
              "5": {
                "date": "2026-04-17",
                "price": 505.0,
                "returnPct": 3.9094650205761416
              },
              "10": {
                "date": "2026-04-24",
                "price": 582.0,
                "returnPct": 19.753086419753085
              },
              "20": {
                "date": "2026-05-11",
                "price": 835.0,
                "returnPct": 71.81069958847736
              }
            },
            "mfePct": 74.69135802469135,
            "maePct": -0.8230452674897082,
            "latestDate": "2026-06-18",
            "latestPrice": 1110.0,
            "latestReturnPct": 128.39506172839506
          },
          {
            "eventId": "2026-04-24-00830-6",
            "sellDate": "2026-04-24",
            "symbol": "00830",
            "name": "國泰費城半導體",
            "shares": 309.0,
            "sellPrice": 71.55,
            "observedTradingDays": 38,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-27",
                "price": 73.7,
                "returnPct": 3.004891684136979
              },
              "3": {
                "date": "2026-04-29",
                "price": 71.05,
                "returnPct": -0.6988120195667413
              },
              "5": {
                "date": "2026-05-04",
                "price": 75.1,
                "returnPct": 4.9615653389238235
              },
              "10": {
                "date": "2026-05-11",
                "price": 82.3,
                "returnPct": 15.024458420684827
              },
              "20": {
                "date": "2026-05-25",
                "price": 87.8,
                "returnPct": 22.71139063591894
              }
            },
            "mfePct": 22.781271837875614,
            "maePct": -1.607267645003485,
            "latestDate": "2026-06-18",
            "latestPrice": 97.0,
            "latestReturnPct": 35.56953179594689
          },
          {
            "eventId": "2026-04-29-00757-7",
            "sellDate": "2026-04-29",
            "symbol": "00757",
            "name": "統一 FANG+",
            "shares": 2000.0,
            "sellPrice": 120.9,
            "observedTradingDays": 35,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-30",
                "price": 120.8,
                "returnPct": -0.08271298593880427
              },
              "3": {
                "date": "2026-05-05",
                "price": 122.85,
                "returnPct": 1.6129032258064502
              },
              "5": {
                "date": "2026-05-07",
                "price": 124.45,
                "returnPct": 2.9363110008271187
              },
              "10": {
                "date": "2026-05-14",
                "price": 129.05,
                "returnPct": 6.741108354011582
              },
              "20": {
                "date": "2026-05-28",
                "price": 130.55,
                "returnPct": 7.981803143093469
              }
            },
            "mfePct": 9.181141439205941,
            "maePct": -0.20678246484697738,
            "latestDate": "2026-06-18",
            "latestPrice": 128.9,
            "latestReturnPct": 6.617038875103387
          },
          {
            "eventId": "2026-04-29-2377-8",
            "sellDate": "2026-04-29",
            "symbol": "2377",
            "name": "微星",
            "shares": 500.0,
            "sellPrice": 100.0,
            "observedTradingDays": 35,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-30",
                "price": 97.7,
                "returnPct": -2.300000000000002
              },
              "3": {
                "date": "2026-05-05",
                "price": 95.7,
                "returnPct": -4.299999999999993
              },
              "5": {
                "date": "2026-05-07",
                "price": 101.0,
                "returnPct": 1.0000000000000009
              },
              "10": {
                "date": "2026-05-14",
                "price": 117.0,
                "returnPct": 16.999999999999993
              },
              "20": {
                "date": "2026-05-28",
                "price": 123.5,
                "returnPct": 23.50000000000001
              }
            },
            "mfePct": 36.00000000000001,
            "maePct": -5.500000000000005,
            "latestDate": "2026-06-18",
            "latestPrice": 138.5,
            "latestReturnPct": 38.5
          },
          {
            "eventId": "2026-05-13-2377-9",
            "sellDate": "2026-05-13",
            "symbol": "2377",
            "name": "微星",
            "shares": 500.0,
            "sellPrice": 113.0,
            "observedTradingDays": 26,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-05-14",
                "price": 117.0,
                "returnPct": 3.539823008849563
              },
              "3": {
                "date": "2026-05-18",
                "price": 113.0,
                "returnPct": 0.0
              },
              "5": {
                "date": "2026-05-20",
                "price": 109.5,
                "returnPct": -3.0973451327433676
              },
              "10": {
                "date": "2026-05-27",
                "price": 126.5,
                "returnPct": 11.946902654867264
              },
              "20": {
                "date": "2026-06-10",
                "price": 132.0,
                "returnPct": 16.814159292035402
              }
            },
            "mfePct": 34.95575221238938,
            "maePct": -4.424778761061942,
            "latestDate": "2026-06-18",
            "latestPrice": 138.5,
            "latestReturnPct": 22.56637168141593
          },
          {
            "eventId": "2026-05-22-6907-10",
            "sellDate": "2026-05-22",
            "symbol": "6907",
            "name": "雅特力-KY",
            "shares": 1000.0,
            "sellPrice": 119.5,
            "observedTradingDays": 19,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-05-25",
                "price": 123.0,
                "returnPct": 2.9288702928870203
              },
              "3": {
                "date": "2026-05-27",
                "price": 117.0,
                "returnPct": -2.092050209205021
              },
              "5": {
                "date": "2026-05-29",
                "price": 121.5,
                "returnPct": 1.673640167364021
              },
              "10": {
                "date": "2026-06-05",
                "price": 169.0,
                "returnPct": 41.42259414225941
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 47.28033472803348,
            "maePct": -3.347280334728031,
            "latestDate": "2026-06-18",
            "latestPrice": 135.5,
            "latestReturnPct": 13.389121338912124
          },
          {
            "eventId": "2026-05-28-6143-11",
            "sellDate": "2026-05-28",
            "symbol": "6143",
            "name": "振曜",
            "shares": 1000.0,
            "sellPrice": 102.5,
            "observedTradingDays": 15,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-05-29",
                "price": 99.8,
                "returnPct": -2.634146341463417
              },
              "3": {
                "date": "2026-06-02",
                "price": 100.0,
                "returnPct": -2.4390243902439046
              },
              "5": {
                "date": "2026-06-04",
                "price": 96.6,
                "returnPct": -5.756097560975615
              },
              "10": {
                "date": "2026-06-11",
                "price": 88.7,
                "returnPct": -13.463414634146343
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 0.4878048780487809,
            "maePct": -14.634146341463417,
            "latestDate": "2026-06-18",
            "latestPrice": 89.2,
            "latestReturnPct": -12.975609756097562
          },
          {
            "eventId": "2026-06-08-3141-12",
            "sellDate": "2026-06-08",
            "symbol": "3141",
            "name": "晶宏",
            "shares": 1000.0,
            "sellPrice": 66.9,
            "observedTradingDays": 8,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-09",
                "price": 73.9,
                "returnPct": 10.463378176382655
              },
              "3": {
                "date": "2026-06-11",
                "price": 71.3,
                "returnPct": 6.5769805680119475
              },
              "5": {
                "date": "2026-06-15",
                "price": 71.5,
                "returnPct": 6.875934230194303
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 16.591928251121058,
            "maePct": 2.9895366218236186,
            "latestDate": "2026-06-18",
            "latestPrice": 74.0,
            "latestReturnPct": 10.612855007473843
          },
          {
            "eventId": "2026-06-08-4739-13",
            "sellDate": "2026-06-08",
            "symbol": "4739",
            "name": "康普",
            "shares": 1000.0,
            "sellPrice": 115.0,
            "observedTradingDays": 7,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-09",
                "price": 130.0,
                "returnPct": 13.043478260869556
              },
              "3": {
                "date": "2026-06-11",
                "price": 123.5,
                "returnPct": 7.391304347826089
              },
              "5": {
                "date": "2026-06-15",
                "price": 122.5,
                "returnPct": 6.521739130434789
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 16.956521739130427,
            "maePct": 0.0,
            "latestDate": "2026-06-17",
            "latestPrice": 123.0,
            "latestReturnPct": 6.956521739130439
          },
          {
            "eventId": "2026-06-09-2379-14",
            "sellDate": "2026-06-09",
            "symbol": "2379",
            "name": "瑞昱",
            "shares": 55.0,
            "sellPrice": 631.0,
            "observedTradingDays": 7,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-10",
                "price": 645.0,
                "returnPct": 2.2187004754358197
              },
              "3": {
                "date": "2026-06-12",
                "price": 618.0,
                "returnPct": -2.0602218700475405
              },
              "5": {
                "date": "2026-06-16",
                "price": 678.0,
                "returnPct": 7.448494453248822
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 29.793977812995244,
            "maePct": -4.5958795562599075,
            "latestDate": "2026-06-18",
            "latestPrice": 819.0,
            "latestReturnPct": 29.793977812995244
          },
          {
            "eventId": "2026-06-12-6907-15",
            "sellDate": "2026-06-12",
            "symbol": "6907",
            "name": "雅特力-KY",
            "shares": 50.0,
            "sellPrice": 142.5,
            "observedTradingDays": 4,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-15",
                "price": 141.5,
                "returnPct": -0.7017543859649145
              },
              "3": {
                "date": "2026-06-17",
                "price": 132.0,
                "returnPct": -7.36842105263158
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 3.8596491228070073,
            "maePct": -8.070175438596493,
            "latestDate": "2026-06-18",
            "latestPrice": 135.5,
            "latestReturnPct": -4.912280701754391
          },
          {
            "eventId": "2026-06-15-00830-16",
            "sellDate": "2026-06-15",
            "symbol": "00830",
            "name": "國泰費城半導體",
            "shares": 673.0,
            "sellPrice": 97.6,
            "observedTradingDays": 3,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-16",
                "price": 98.45,
                "returnPct": 0.8709016393442681
              },
              "3": {
                "date": "2026-06-18",
                "price": 97.0,
                "returnPct": -0.6147540983606481
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 0.9733606557376984,
            "maePct": -3.3299180327868827,
            "latestDate": "2026-06-18",
            "latestPrice": 97.0,
            "latestReturnPct": -0.6147540983606481
          },
          {
            "eventId": "2026-06-16-00830-17",
            "sellDate": "2026-06-16",
            "symbol": "00830",
            "name": "國泰費城半導體",
            "shares": 41.0,
            "sellPrice": 98.15,
            "observedTradingDays": 2,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-17",
                "price": 95.6,
                "returnPct": -2.5980641874681742
              },
              "3": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": -1.0697911360163181,
            "maePct": -3.8716250636780525,
            "latestDate": "2026-06-18",
            "latestPrice": 97.0,
            "latestReturnPct": -1.1716760061130982
          },
          {
            "eventId": "2026-06-16-2317-18",
            "sellDate": "2026-06-16",
            "symbol": "2317",
            "name": "鴻海",
            "shares": 300.0,
            "sellPrice": 270.0,
            "observedTradingDays": 2,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-17",
                "price": 272.0,
                "returnPct": 0.7407407407407307
              },
              "3": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 0.7407407407407307,
            "maePct": -2.2222222222222254,
            "latestDate": "2026-06-18",
            "latestPrice": 268.5,
            "latestReturnPct": -0.5555555555555536
          },
          {
            "eventId": "2026-06-17-4739-19",
            "sellDate": "2026-06-17",
            "symbol": "4739",
            "name": "康普",
            "shares": 500.0,
            "sellPrice": 120.5,
            "observedTradingDays": 0,
            "status": "observing",
            "returns": {
              "1": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "3": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": null,
            "maePct": null,
            "latestDate": "2026-06-17",
            "latestPrice": 123.0,
            "latestReturnPct": 2.0746887966804906
          },
          {
            "eventId": "2026-06-22-2317-20",
            "sellDate": "2026-06-22",
            "symbol": "2317",
            "name": "鴻海",
            "shares": 300.0,
            "sellPrice": 275.0,
            "observedTradingDays": 0,
            "status": "observing",
            "returns": {
              "1": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "3": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": null,
            "maePct": null,
            "latestDate": "2026-06-18",
            "latestPrice": 268.5,
            "latestReturnPct": -2.3636363636363678
          },
          {
            "eventId": "2026-06-15-00830-21",
            "sellDate": "2026-06-15",
            "symbol": "00830",
            "name": "國泰費城半導體",
            "shares": 561.0,
            "sellPrice": 97.65,
            "observedTradingDays": 3,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-16",
                "price": 98.45,
                "returnPct": 0.8192524321556593
              },
              "3": {
                "date": "2026-06-18",
                "price": 97.0,
                "returnPct": -0.6656426011264815
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 0.9216589861751112,
            "maePct": -3.3794162826421004,
            "latestDate": "2026-06-18",
            "latestPrice": 97.0,
            "latestReturnPct": -0.6656426011264815
          },
          {
            "eventId": "2026-04-24-00830-22",
            "sellDate": "2026-04-24",
            "symbol": "00830",
            "name": "國泰費城半導體",
            "shares": 363.0,
            "sellPrice": 71.55,
            "observedTradingDays": 38,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-27",
                "price": 73.7,
                "returnPct": 3.004891684136979
              },
              "3": {
                "date": "2026-04-29",
                "price": 71.05,
                "returnPct": -0.6988120195667413
              },
              "5": {
                "date": "2026-05-04",
                "price": 75.1,
                "returnPct": 4.9615653389238235
              },
              "10": {
                "date": "2026-05-11",
                "price": 82.3,
                "returnPct": 15.024458420684827
              },
              "20": {
                "date": "2026-05-25",
                "price": 87.8,
                "returnPct": 22.71139063591894
              }
            },
            "mfePct": 22.781271837875614,
            "maePct": -1.607267645003485,
            "latestDate": "2026-06-18",
            "latestPrice": 97.0,
            "latestReturnPct": 35.56953179594689
          },
          {
            "eventId": "2026-04-08-00830-23",
            "sellDate": "2026-04-08",
            "symbol": "00830",
            "name": "國泰費城半導體",
            "shares": 1396.0,
            "sellPrice": 58.69,
            "observedTradingDays": 50,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-09",
                "price": 59.35,
                "returnPct": 1.1245527347077955
              },
              "3": {
                "date": "2026-04-13",
                "price": 61.65,
                "returnPct": 5.043448628386438
              },
              "5": {
                "date": "2026-04-15",
                "price": 64.45,
                "returnPct": 9.814278411995247
              },
              "10": {
                "date": "2026-04-22",
                "price": 68.05,
                "returnPct": 15.94820241949224
              },
              "20": {
                "date": "2026-05-07",
                "price": 79.55,
                "returnPct": 35.54268188788549
              }
            },
            "mfePct": 35.71306866587154,
            "maePct": 0.7837791787357329,
            "latestDate": "2026-06-18",
            "latestPrice": 97.0,
            "latestReturnPct": 65.27517464644743
          },
          {
            "eventId": "2026-03-25-6907-24",
            "sellDate": "2026-03-25",
            "symbol": "6907",
            "name": "雅特力-KY",
            "shares": 1000.0,
            "sellPrice": 132.5,
            "observedTradingDays": 58,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-03-26",
                "price": 124.0,
                "returnPct": -6.41509433962264
              },
              "3": {
                "date": "2026-03-30",
                "price": 118.0,
                "returnPct": -10.943396226415093
              },
              "5": {
                "date": "2026-04-01",
                "price": 109.0,
                "returnPct": -17.73584905660377
              },
              "10": {
                "date": "2026-04-10",
                "price": 121.5,
                "returnPct": -8.301886792452828
              },
              "20": {
                "date": "2026-04-24",
                "price": 131.5,
                "returnPct": -0.7547169811320753
              }
            },
            "mfePct": 15.849056603773581,
            "maePct": -25.962264150943405,
            "latestDate": "2026-06-18",
            "latestPrice": 135.5,
            "latestReturnPct": 2.264150943396226
          }
        ],
        "postSalePriceThrough": "2026-06-18"
      },
      "validation": {
        "status": "warning",
        "checks": [
          {
            "label": "已實現損益合計",
            "ok": true,
            "actual": 205711.0,
            "expected": 205711.0,
            "diff": 0.0
          },
          {
            "label": "未實現損益合計",
            "ok": true,
            "actual": 205589.0,
            "expected": 205589.0,
            "diff": 0.0
          },
          {
            "label": "股票庫存市值合計",
            "ok": true,
            "actual": 1196229.0,
            "expected": 1196229.0,
            "diff": 0.0
          },
          {
            "label": "總損益",
            "ok": true,
            "actual": 411300.0,
            "expected": 411300.0,
            "diff": 0.0
          },
          {
            "label": "目前推估總資產",
            "ok": true,
            "actual": 2411300.0,
            "expected": 2411300.0,
            "diff": 0.0
          },
          {
            "label": "推估現金",
            "ok": true,
            "actual": 1215071.0,
            "expected": 1215071.0,
            "diff": 0.0
          },
          {
            "label": "總報酬率",
            "ok": true,
            "actual": 20.565,
            "expected": 20.57,
            "diff": -0.005
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
          },
          {
            "label": "6732 庫存損益",
            "ok": true,
            "actual": 9394.0,
            "expected": 9394.0,
            "diff": 0.0
          },
          {
            "label": "6732 庫存損益",
            "ok": true,
            "actual": 5312.0,
            "expected": 5312.0,
            "diff": 0.0
          },
          {
            "label": "6732 庫存損益",
            "ok": true,
            "actual": 9334.0,
            "expected": 9334.0,
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
      "currentDate": "2026-07-08",
      "orderLogComplete": false,
      "dataQuality": [
        "總覽、庫存合計、已實現損益合計可內部驗算。",
        "2026/06/18 GEV 賣出 1 股後，目前庫存為 BDC 24 股、GEV 0 股。",
        "2026/06/20 與 2026/07/08 依使用者截圖補入 TSM、UNH 已實現賣出紀錄；截圖僅提供賣出資料，委託流水不再標記為完整。",
        "美股庫存仍沿用前次 BDC 快照；需另補最新庫存截圖才能更新未實現損益。",
        "COHR 2026-06-05/2026-06-06 日期需確認是美股交易日或台灣券商顯示日；績效表採 2026-06-05。"
      ],
      "summary": {
        "realizedPnl": 2959.64,
        "unrealizedPnl": 321.25,
        "totalPnl": 3280.89,
        "currentAssets": 33280.89,
        "totalReturnPct": 10.94,
        "cash": 30347.85,
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
          "sellDate": "2026-04-08",
          "symbol": "TSM",
          "name": "TSMC(ADR)",
          "shares": 20.48,
          "sellPrice": 365.48,
          "realizedPnl": 873.12,
          "returnPct": 13.23,
          "source": "2026/06/20 使用者截圖"
        },
        {
          "sellDate": "2026-04-21",
          "symbol": "UNH",
          "name": "UnitedHealth",
          "shares": 35.5498,
          "sellPrice": 353.62,
          "realizedPnl": 557.72,
          "returnPct": 4.65,
          "source": "2026/06/20 使用者截圖"
        },
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
          "sellDate": "2026-06-03",
          "symbol": "UNH",
          "name": "UnitedHealth",
          "shares": 5.23211,
          "sellPrice": 385.3,
          "realizedPnl": 12.17,
          "returnPct": 0.61,
          "source": "2026/06/20 使用者截圖"
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
        },
        {
          "sellDate": "2026-06-22",
          "symbol": "TSM",
          "name": "TSMC(ADR)",
          "shares": 3.48626,
          "estimatedBuyPrice": 433.7,
          "sellPrice": 471.0,
          "investmentCost": 1512.03,
          "realizedPnl": 126.95,
          "returnPct": 8.4,
          "source": "2026/07/08 使用者截圖"
        },
        {
          "sellDate": "2026-06-30",
          "symbol": "TSM",
          "name": "TSMC(ADR)",
          "shares": 0.52487,
          "estimatedBuyPrice": 476.32,
          "sellPrice": 471.11,
          "investmentCost": 250.01,
          "realizedPnl": -5.76,
          "returnPct": -2.3,
          "source": "2026/07/08 使用者截圖"
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
        },
        {
          "date": "2026-06-22",
          "symbol": "TSM",
          "name": "TSMC(ADR)",
          "action": "sell",
          "orderPrice": 471.0,
          "fillPrice": 471.0,
          "shares": 3.48626,
          "status": "2026/07/08 使用者截圖"
        },
        {
          "date": "2026-06-30",
          "symbol": "TSM",
          "name": "TSMC(ADR)",
          "action": "sell",
          "orderPrice": 471.11,
          "fillPrice": 471.11,
          "shares": 0.52487,
          "status": "2026/07/08 使用者截圖"
        }
      ],
      "computed": {
        "positionCost": 2611.79,
        "realizedByDate": [
          {
            "date": "2026-04-08",
            "realizedPnl": 873.12
          },
          {
            "date": "2026-04-21",
            "realizedPnl": 557.72
          },
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
            "realizedPnl": 92.81
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
          },
          {
            "date": "2026-06-22",
            "realizedPnl": 126.95
          },
          {
            "date": "2026-06-30",
            "realizedPnl": -5.76
          }
        ],
        "equitySeries": [
          {
            "date": "2026-04-08",
            "realizedPnl": 873.12,
            "unrealizedPnl": 0.0,
            "equity": 30873.12,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-21",
            "realizedPnl": 1430.8400000000001,
            "unrealizedPnl": 0.0,
            "equity": 31430.84,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-29",
            "realizedPnl": 2093.0,
            "unrealizedPnl": 0.0,
            "equity": 32093.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-01",
            "realizedPnl": 2285.68,
            "unrealizedPnl": 0.0,
            "equity": 32285.68,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-02",
            "realizedPnl": 2536.2799999999997,
            "unrealizedPnl": 0.0,
            "equity": 32536.28,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-03",
            "realizedPnl": 2629.0899999999997,
            "unrealizedPnl": 0.0,
            "equity": 32629.09,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-05",
            "realizedPnl": 2634.3199999999997,
            "unrealizedPnl": 0.0,
            "equity": 32634.32,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-08",
            "realizedPnl": 2620.4999999999995,
            "unrealizedPnl": 0.0,
            "equity": 32620.5,
            "drawdown": -13.819999999999709,
            "drawdownPct": -0.04234805566654892
          },
          {
            "date": "2026-06-11",
            "realizedPnl": 2541.6299999999997,
            "unrealizedPnl": 0.0,
            "equity": 32541.63,
            "drawdown": -92.68999999999869,
            "drawdownPct": -0.2840261418040844
          },
          {
            "date": "2026-06-15",
            "realizedPnl": 2553.0999999999995,
            "unrealizedPnl": 0.0,
            "equity": 32553.1,
            "drawdown": -81.22000000000116,
            "drawdownPct": -0.24887909415609444
          },
          {
            "date": "2026-06-16",
            "realizedPnl": 2648.0099999999993,
            "unrealizedPnl": 0.0,
            "equity": 32648.01,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-18",
            "realizedPnl": 2838.4499999999994,
            "unrealizedPnl": 0.0,
            "equity": 32838.45,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-22",
            "realizedPnl": 2965.399999999999,
            "unrealizedPnl": 0.0,
            "equity": 32965.4,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-30",
            "realizedPnl": 2959.639999999999,
            "unrealizedPnl": 0.0,
            "equity": 32959.64,
            "drawdown": -5.760000000002037,
            "drawdownPct": -0.017472865489276748
          },
          {
            "date": "2026-07-08",
            "realizedPnl": 2959.64,
            "unrealizedPnl": 321.25,
            "equity": 33280.89,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          }
        ],
        "contributions": [
          {
            "symbol": "TSM",
            "name": "TSMC(ADR)",
            "realizedPnl": 994.3100000000001,
            "unrealizedPnl": 0.0,
            "realizedCost": 8361.58648526077,
            "positionCost": 0.0,
            "totalPnl": 994.3100000000001,
            "totalCost": 8361.58648526077,
            "returnPct": 11.891403643946056
          },
          {
            "symbol": "UNH",
            "name": "UnitedHealth",
            "realizedPnl": 569.89,
            "unrealizedPnl": 0.0,
            "realizedCost": 13989.060461836769,
            "positionCost": 0.0,
            "totalPnl": 569.89,
            "totalCost": 13989.060461836769,
            "returnPct": 4.073826126884673
          },
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
          "tradeCount": 23,
          "winCount": 18,
          "lossCount": 5,
          "winRatePct": 78.26086956521739,
          "avgWin": 176.96666666666667,
          "avgLoss": -45.152,
          "profitFactor": 14.10967399007796,
          "bestTrade": 873.12,
          "worstTrade": -95.0,
          "maxDrawdown": -92.68999999999869,
          "maxDrawdownPct": -0.2840261418040844
        },
        "postSaleAnalysis": [
          {
            "eventId": "2026-04-08-TSM-1",
            "sellDate": "2026-04-08",
            "symbol": "TSM",
            "name": "TSMC(ADR)",
            "shares": 20.48,
            "sellPrice": 365.48,
            "observedTradingDays": 50,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-09",
                "price": 365.49,
                "returnPct": 0.0027361278318815963
              },
              "3": {
                "date": "2026-04-13",
                "price": 369.57,
                "returnPct": 1.1190762832439471
              },
              "5": {
                "date": "2026-04-15",
                "price": 375.1,
                "returnPct": 2.6321549742803985
              },
              "10": {
                "date": "2026-04-22",
                "price": 387.44,
                "returnPct": 6.0085367188355
              },
              "20": {
                "date": "2026-05-06",
                "price": 419.5,
                "returnPct": 14.780562547882226
              }
            },
            "mfePct": 14.835285104520079,
            "maePct": -1.3489110211229116,
            "latestDate": "2026-06-18",
            "latestPrice": 462.12,
            "latestReturnPct": 26.44193936740724
          },
          {
            "eventId": "2026-04-21-UNH-2",
            "sellDate": "2026-04-21",
            "symbol": "UNH",
            "name": "UnitedHealth",
            "shares": 35.5498,
            "sellPrice": 353.62,
            "observedTradingDays": 41,
            "status": "complete",
            "returns": {
              "1": {
                "date": "2026-04-22",
                "price": 353.52,
                "returnPct": -0.028278943498671882
              },
              "3": {
                "date": "2026-04-24",
                "price": 354.92,
                "returnPct": 0.36762626548272337
              },
              "5": {
                "date": "2026-04-28",
                "price": 366.77,
                "returnPct": 3.718681070075225
              },
              "10": {
                "date": "2026-05-05",
                "price": 363.87,
                "returnPct": 2.8985917086137736
              },
              "20": {
                "date": "2026-05-19",
                "price": 389.24,
                "returnPct": 10.072959674226567
              }
            },
            "mfePct": 14.289350149878398,
            "maePct": -1.3206266613879358,
            "latestDate": "2026-06-18",
            "latestPrice": 400.96,
            "latestReturnPct": 13.387251852270786
          },
          {
            "eventId": "2026-05-29-NTAP-3",
            "sellDate": "2026-05-29",
            "symbol": "NTAP",
            "name": "NetApp",
            "shares": 15.0,
            "sellPrice": 183.236,
            "observedTradingDays": 14,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-01",
                "price": 179.7,
                "returnPct": -1.929751795498702
              },
              "3": {
                "date": "2026-06-03",
                "price": 181.08,
                "returnPct": -1.1766246807395797
              },
              "5": {
                "date": "2026-06-05",
                "price": 167.04,
                "returnPct": -8.838874456984435
              },
              "10": {
                "date": "2026-06-12",
                "price": 161.61,
                "returnPct": -11.802265930275702
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 1.7976816782728333,
            "maePct": -16.321028618830347,
            "latestDate": "2026-06-18",
            "latestPrice": 159.71,
            "latestReturnPct": -12.839180073784618
          },
          {
            "eventId": "2026-06-01-HPE-4",
            "sellDate": "2026-06-01",
            "symbol": "HPE",
            "name": "HP Enterprise",
            "shares": 30.0,
            "sellPrice": 44.4,
            "observedTradingDays": 13,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-02",
                "price": 56.15,
                "returnPct": 26.463963963963955
              },
              "3": {
                "date": "2026-06-04",
                "price": 53.69,
                "returnPct": 20.923423423423415
              },
              "5": {
                "date": "2026-06-08",
                "price": 49.87,
                "returnPct": 12.319819819819822
              },
              "10": {
                "date": "2026-06-15",
                "price": 49.02,
                "returnPct": 10.405405405405421
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 44.70720720720722,
            "maePct": 0.765765765765769,
            "latestDate": "2026-06-18",
            "latestPrice": 47.41,
            "latestReturnPct": 6.779279279279282
          },
          {
            "eventId": "2026-06-02-COHR-5",
            "sellDate": "2026-06-02",
            "symbol": "COHR",
            "name": "Coherent",
            "shares": 5.0,
            "sellPrice": 396.16,
            "observedTradingDays": 12,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-03",
                "price": 417.43,
                "returnPct": 5.369042810985447
              },
              "3": {
                "date": "2026-06-05",
                "price": 376.99,
                "returnPct": -4.838953957996772
              },
              "5": {
                "date": "2026-06-09",
                "price": 355.94,
                "returnPct": -10.152463651050091
              },
              "10": {
                "date": "2026-06-16",
                "price": 382.81,
                "returnPct": -3.369850565428112
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 11.066235864297248,
            "maePct": -15.3170436187399,
            "latestDate": "2026-06-18",
            "latestPrice": 389.57,
            "latestReturnPct": -1.6634693053311889
          },
          {
            "eventId": "2026-06-02-QCOM-6",
            "sellDate": "2026-06-02",
            "symbol": "QCOM",
            "name": "Qualcomm",
            "shares": 5.0,
            "sellPrice": 240.487,
            "observedTradingDays": 12,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-03",
                "price": 250.01,
                "returnPct": 3.9598814073110056
              },
              "3": {
                "date": "2026-06-05",
                "price": 215.94,
                "returnPct": -10.207204547439153
              },
              "5": {
                "date": "2026-06-09",
                "price": 205.42,
                "returnPct": -14.58166137878555
              },
              "10": {
                "date": "2026-06-16",
                "price": 214.07,
                "returnPct": -10.984793356813471
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 6.072261702295756,
            "maePct": -20.952068095156907,
            "latestDate": "2026-06-18",
            "latestPrice": 226.11,
            "latestReturnPct": -5.978285728542487
          },
          {
            "eventId": "2026-06-02-QCOM-7",
            "sellDate": "2026-06-02",
            "symbol": "QCOM",
            "name": "Qualcomm",
            "shares": 5.0,
            "sellPrice": 234.5,
            "observedTradingDays": 12,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-03",
                "price": 250.01,
                "returnPct": 6.614072494669498
              },
              "3": {
                "date": "2026-06-05",
                "price": 215.94,
                "returnPct": -7.914712153518122
              },
              "5": {
                "date": "2026-06-09",
                "price": 205.42,
                "returnPct": -12.400852878464818
              },
              "10": {
                "date": "2026-06-16",
                "price": 214.07,
                "returnPct": -8.712153518123667
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 8.780383795309167,
            "maePct": -18.93390191897655,
            "latestDate": "2026-06-18",
            "latestPrice": 226.11,
            "latestReturnPct": -3.577825159914705
          },
          {
            "eventId": "2026-06-03-GEV-8",
            "sellDate": "2026-06-03",
            "symbol": "GEV",
            "name": "GE Vernova",
            "shares": 2.0,
            "sellPrice": 987.4,
            "observedTradingDays": 11,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-04",
                "price": 963.33,
                "returnPct": -2.437715211667002
              },
              "3": {
                "date": "2026-06-08",
                "price": 933.85,
                "returnPct": -5.423334008507186
              },
              "5": {
                "date": "2026-06-10",
                "price": 867.09,
                "returnPct": -12.184525015191404
              },
              "10": {
                "date": "2026-06-17",
                "price": 1048.86,
                "returnPct": 6.224427790155951
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 13.222604820741356,
            "maePct": -13.306663965971232,
            "latestDate": "2026-06-18",
            "latestPrice": 1109.73,
            "latestReturnPct": 12.389102693943688
          },
          {
            "eventId": "2026-06-03-GEV-9",
            "sellDate": "2026-06-03",
            "symbol": "GEV",
            "name": "GE Vernova",
            "shares": 1.0,
            "sellPrice": 985.0,
            "observedTradingDays": 11,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-04",
                "price": 963.33,
                "returnPct": -2.199999999999991
              },
              "3": {
                "date": "2026-06-08",
                "price": 933.85,
                "returnPct": -5.192893401015231
              },
              "5": {
                "date": "2026-06-10",
                "price": 867.09,
                "returnPct": -11.97055837563451
              },
              "10": {
                "date": "2026-06-17",
                "price": 1048.86,
                "returnPct": 6.483248730964464
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 13.498477157360412,
            "maePct": -13.09543147208122,
            "latestDate": "2026-06-18",
            "latestPrice": 1109.73,
            "latestReturnPct": 12.66294416243654
          },
          {
            "eventId": "2026-06-03-UNH-10",
            "sellDate": "2026-06-03",
            "symbol": "UNH",
            "name": "UnitedHealth",
            "shares": 5.23211,
            "sellPrice": 385.3,
            "observedTradingDays": 11,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-04",
                "price": 396.47,
                "returnPct": 2.899039709317419
              },
              "3": {
                "date": "2026-06-08",
                "price": 406.57,
                "returnPct": 5.5203737347521376
              },
              "5": {
                "date": "2026-06-10",
                "price": 407.46,
                "returnPct": 5.751362574617169
              },
              "10": {
                "date": "2026-06-17",
                "price": 399.53,
                "returnPct": 3.693226057617438
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 7.962626524785876,
            "maePct": 1.1731118608876212,
            "latestDate": "2026-06-18",
            "latestPrice": 400.96,
            "latestReturnPct": 4.06436542953541
          },
          {
            "eventId": "2026-06-05-NTAP-11",
            "sellDate": "2026-06-05",
            "symbol": "NTAP",
            "name": "NetApp",
            "shares": 6.0,
            "sellPrice": 169.65,
            "observedTradingDays": 9,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-08",
                "price": 170.31,
                "returnPct": 0.38903625110522366
              },
              "3": {
                "date": "2026-06-10",
                "price": 160.66,
                "returnPct": -5.2991452991453025
              },
              "5": {
                "date": "2026-06-12",
                "price": 161.61,
                "returnPct": -4.7391688770999085
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 1.4146772767462457,
            "maePct": -9.619805481874444,
            "latestDate": "2026-06-18",
            "latestPrice": 159.71,
            "latestReturnPct": -5.859121721190686
          },
          {
            "eventId": "2026-06-05-COHR-12",
            "sellDate": "2026-06-05",
            "symbol": "COHR",
            "name": "Coherent",
            "shares": 3.0,
            "sellPrice": 401.5,
            "observedTradingDays": 9,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-08",
                "price": 401.93,
                "returnPct": 0.10709838107099134
              },
              "3": {
                "date": "2026-06-10",
                "price": 354.77,
                "returnPct": -11.638854296388546
              },
              "5": {
                "date": "2026-06-12",
                "price": 385.03,
                "returnPct": -4.102117061021183
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 5.603985056039851,
            "maePct": -16.443337484433375,
            "latestDate": "2026-06-18",
            "latestPrice": 389.57,
            "latestReturnPct": -2.971357409713571
          },
          {
            "eventId": "2026-06-05-COHR-13",
            "sellDate": "2026-06-05",
            "symbol": "COHR",
            "name": "Coherent",
            "shares": 3.0,
            "sellPrice": 403.2,
            "observedTradingDays": 9,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-08",
                "price": 401.93,
                "returnPct": -0.3149801587301493
              },
              "3": {
                "date": "2026-06-10",
                "price": 354.77,
                "returnPct": -12.011408730158735
              },
              "5": {
                "date": "2026-06-12",
                "price": 385.03,
                "returnPct": -4.506448412698417
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 5.158730158730163,
            "maePct": -16.795634920634917,
            "latestDate": "2026-06-18",
            "latestPrice": 389.57,
            "latestReturnPct": -3.380456349206351
          },
          {
            "eventId": "2026-06-08-ETN-14",
            "sellDate": "2026-06-08",
            "symbol": "ETN",
            "name": "Eaton",
            "shares": 4.0,
            "sellPrice": 405.171,
            "observedTradingDays": 8,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-09",
                "price": 401.72,
                "returnPct": -0.8517391422387055
              },
              "3": {
                "date": "2026-06-11",
                "price": 393.64,
                "returnPct": -2.845958866750087
              },
              "5": {
                "date": "2026-06-15",
                "price": 407.06,
                "returnPct": 0.4662229034160914
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 5.121047656421607,
            "maePct": -7.43661318307578,
            "latestDate": "2026-06-18",
            "latestPrice": 421.77,
            "latestReturnPct": 4.096788763262915
          },
          {
            "eventId": "2026-06-08-ETN-15",
            "sellDate": "2026-06-08",
            "symbol": "ETN",
            "name": "Eaton",
            "shares": 4.0,
            "sellPrice": 405.1,
            "observedTradingDays": 8,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-09",
                "price": 401.72,
                "returnPct": -0.8343618859540824
              },
              "3": {
                "date": "2026-06-11",
                "price": 393.64,
                "returnPct": -2.8289311281165186
              },
              "5": {
                "date": "2026-06-15",
                "price": 407.06,
                "returnPct": 0.48383115280177247
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 5.1394717353739905,
            "maePct": -7.42039002715379,
            "latestDate": "2026-06-18",
            "latestPrice": 421.77,
            "latestReturnPct": 4.1150333251049
          },
          {
            "eventId": "2026-06-11-COHR-16",
            "sellDate": "2026-06-11",
            "symbol": "COHR",
            "name": "Coherent",
            "shares": 4.0,
            "sellPrice": 365.8,
            "observedTradingDays": 5,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-12",
                "price": 385.03,
                "returnPct": 5.256971022416601
              },
              "3": {
                "date": "2026-06-16",
                "price": 382.81,
                "returnPct": 4.650082012028434
              },
              "5": {
                "date": "2026-06-18",
                "price": 389.57,
                "returnPct": 6.498086386003266
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 15.910333515582288,
            "maePct": -3.173865500273376,
            "latestDate": "2026-06-18",
            "latestPrice": 389.57,
            "latestReturnPct": 6.498086386003266
          },
          {
            "eventId": "2026-06-11-COHR-17",
            "sellDate": "2026-06-11",
            "symbol": "COHR",
            "name": "Coherent",
            "shares": 4.0,
            "sellPrice": 365.08,
            "observedTradingDays": 5,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-12",
                "price": 385.03,
                "returnPct": 5.464555713816144
              },
              "3": {
                "date": "2026-06-16",
                "price": 382.81,
                "returnPct": 4.856469814835118
              },
              "5": {
                "date": "2026-06-18",
                "price": 389.57,
                "returnPct": 6.708118768489091
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 16.138928454037483,
            "maePct": -2.9829078558124222,
            "latestDate": "2026-06-18",
            "latestPrice": 389.57,
            "latestReturnPct": 6.708118768489091
          },
          {
            "eventId": "2026-06-11-NTAP-18",
            "sellDate": "2026-06-11",
            "symbol": "NTAP",
            "name": "NetApp",
            "shares": 5.0,
            "sellPrice": 157.7,
            "observedTradingDays": 5,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-12",
                "price": 161.61,
                "returnPct": 2.4793912492073744
              },
              "3": {
                "date": "2026-06-16",
                "price": 161.26,
                "returnPct": 2.257450856055798
              },
              "5": {
                "date": "2026-06-18",
                "price": 159.71,
                "returnPct": 1.2745719720989257
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 4.090044388078651,
            "maePct": -2.771084337349383,
            "latestDate": "2026-06-18",
            "latestPrice": 159.71,
            "latestReturnPct": 1.2745719720989257
          },
          {
            "eventId": "2026-06-15-GEV-19",
            "sellDate": "2026-06-15",
            "symbol": "GEV",
            "name": "GE Vernova",
            "shares": 2.0,
            "sellPrice": 969.73,
            "observedTradingDays": 3,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-16",
                "price": 982.35,
                "returnPct": 1.3013931712950955
              },
              "3": {
                "date": "2026-06-18",
                "price": 1109.73,
                "returnPct": 14.437008239406834
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 15.285698080909116,
            "maePct": 1.1343363616676871,
            "latestDate": "2026-06-18",
            "latestPrice": 1109.73,
            "latestReturnPct": 14.437008239406834
          },
          {
            "eventId": "2026-06-16-GEV-20",
            "sellDate": "2026-06-16",
            "symbol": "GEV",
            "name": "GE Vernova",
            "shares": 1.0,
            "sellPrice": 1001.0,
            "observedTradingDays": 2,
            "status": "observing",
            "returns": {
              "1": {
                "date": "2026-06-17",
                "price": 1048.86,
                "returnPct": 4.781218781218777
              },
              "3": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": 11.684315684315694,
            "maePct": -0.899100899100902,
            "latestDate": "2026-06-18",
            "latestPrice": 1109.73,
            "latestReturnPct": 10.862137862137855
          },
          {
            "eventId": "2026-06-18-GEV-21",
            "sellDate": "2026-06-18",
            "symbol": "GEV",
            "name": "GE Vernova",
            "shares": 1.0,
            "sellPrice": 1093.0,
            "observedTradingDays": 0,
            "status": "observing",
            "returns": {
              "1": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "3": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": null,
            "maePct": null,
            "latestDate": "2026-06-18",
            "latestPrice": 1109.73,
            "latestReturnPct": 1.5306495882891236
          },
          {
            "eventId": "2026-06-22-TSM-22",
            "sellDate": "2026-06-22",
            "symbol": "TSM",
            "name": "TSMC(ADR)",
            "shares": 3.48626,
            "sellPrice": 471.0,
            "observedTradingDays": 0,
            "status": "observing",
            "returns": {
              "1": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "3": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": null,
            "maePct": null,
            "latestDate": "2026-06-18",
            "latestPrice": 462.12,
            "latestReturnPct": -1.885350318471335
          },
          {
            "eventId": "2026-06-30-TSM-23",
            "sellDate": "2026-06-30",
            "symbol": "TSM",
            "name": "TSMC(ADR)",
            "shares": 0.52487,
            "sellPrice": 471.11,
            "observedTradingDays": 0,
            "status": "observing",
            "returns": {
              "1": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "3": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "5": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "10": {
                "date": null,
                "price": null,
                "returnPct": null
              },
              "20": {
                "date": null,
                "price": null,
                "returnPct": null
              }
            },
            "mfePct": null,
            "maePct": null,
            "latestDate": "2026-06-18",
            "latestPrice": 462.12,
            "latestReturnPct": -1.9082592175925006
          }
        ],
        "postSalePriceThrough": "2026-06-18"
      },
      "validation": {
        "status": "warning",
        "checks": [
          {
            "label": "已實現損益合計",
            "ok": true,
            "actual": 2959.64,
            "expected": 2959.64,
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
            "actual": 3280.89,
            "expected": 3280.89,
            "diff": 0.0
          },
          {
            "label": "目前推估總資產",
            "ok": true,
            "actual": 33280.89,
            "expected": 33280.89,
            "diff": 0.0
          },
          {
            "label": "推估現金",
            "ok": true,
            "actual": 30347.85,
            "expected": 30347.85,
            "diff": 0.0
          },
          {
            "label": "總報酬率",
            "ok": true,
            "actual": 10.9363,
            "expected": 10.94,
            "diff": -0.0037
          },
          {
            "label": "BDC 庫存損益",
            "ok": true,
            "actual": 321.25,
            "expected": 321.25,
            "diff": 0.0
          }
        ],
        "warnings": [
          "成交/委託紀錄標記為不完整；不以流水股數反推目前庫存。",
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
          "actual": 205711.0,
          "expected": 205711.0,
          "diff": 0.0
        },
        {
          "label": "未實現損益合計",
          "ok": true,
          "actual": 205589.0,
          "expected": 205589.0,
          "diff": 0.0
        },
        {
          "label": "股票庫存市值合計",
          "ok": true,
          "actual": 1196229.0,
          "expected": 1196229.0,
          "diff": 0.0
        },
        {
          "label": "總損益",
          "ok": true,
          "actual": 411300.0,
          "expected": 411300.0,
          "diff": 0.0
        },
        {
          "label": "目前推估總資產",
          "ok": true,
          "actual": 2411300.0,
          "expected": 2411300.0,
          "diff": 0.0
        },
        {
          "label": "推估現金",
          "ok": true,
          "actual": 1215071.0,
          "expected": 1215071.0,
          "diff": 0.0
        },
        {
          "label": "總報酬率",
          "ok": true,
          "actual": 20.565,
          "expected": 20.57,
          "diff": -0.005
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
        },
        {
          "label": "6732 庫存損益",
          "ok": true,
          "actual": 9394.0,
          "expected": 9394.0,
          "diff": 0.0
        },
        {
          "label": "6732 庫存損益",
          "ok": true,
          "actual": 5312.0,
          "expected": 5312.0,
          "diff": 0.0
        },
        {
          "label": "6732 庫存損益",
          "ok": true,
          "actual": 9334.0,
          "expected": 9334.0,
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
          "actual": 2959.64,
          "expected": 2959.64,
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
          "actual": 3280.89,
          "expected": 3280.89,
          "diff": 0.0
        },
        {
          "label": "目前推估總資產",
          "ok": true,
          "actual": 33280.89,
          "expected": 33280.89,
          "diff": 0.0
        },
        {
          "label": "推估現金",
          "ok": true,
          "actual": 30347.85,
          "expected": 30347.85,
          "diff": 0.0
        },
        {
          "label": "總報酬率",
          "ok": true,
          "actual": 10.9363,
          "expected": 10.94,
          "diff": -0.0037
        },
        {
          "label": "BDC 庫存損益",
          "ok": true,
          "actual": 321.25,
          "expected": 321.25,
          "diff": 0.0
        }
      ],
      "warnings": [
        "成交/委託紀錄標記為不完整；不以流水股數反推目前庫存。",
        "COHR 2026-06-05 已實現日期與成交紀錄日期不同；成交紀錄日期: 2026-06-06"
      ]
    }
  }
};
