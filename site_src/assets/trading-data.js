window.TRADING_DASHBOARD = {
  "version": 1,
  "updatedAt": "2026-06-17",
  "sourceNote": "User-provided ChatGPT整理交易紀錄; dashboard validation checks internal reconciliation only, not broker screenshot fidelity.",
  "markets": {
    "tw": {
      "market": "tw",
      "label": "台股",
      "currency": "TWD",
      "currencyLabel": "台幣",
      "initialCapital": 1000000,
      "currentDate": "2026-06-17",
      "orderLogComplete": false,
      "dataQuality": [
        "總覽、庫存合計、已實現損益合計可內部驗算。",
        "成交/委託紀錄不是完整台帳；多筆已實現交易的買入日與買入均價是依規則推估。",
        "台股第一版資產曲線採已實現損益事件 + 最新未實現庫存快照，不代表完整逐日市值曲線。"
      ],
      "summary": {
        "realizedPnl": 87053,
        "unrealizedPnl": -107,
        "totalPnl": 86946,
        "currentAssets": 1086946,
        "totalReturnPct": 8.69,
        "cash": 788541,
        "marketValue": 298405
      },
      "positions": [
        {
          "symbol": "2317",
          "name": "鴻海",
          "shares": 300,
          "marketValue": 81241,
          "cost": 80563,
          "unrealizedPnl": 678,
          "returnPct": 0.84
        },
        {
          "symbol": "4739",
          "name": "康普",
          "shares": 500,
          "marketValue": 61229,
          "cost": 43061,
          "unrealizedPnl": 18168,
          "returnPct": 42.19
        },
        {
          "symbol": "6732",
          "name": "昇佳電子",
          "shares": 1004,
          "marketValue": 155935,
          "cost": 174888,
          "unrealizedPnl": -18953,
          "returnPct": -10.84
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
          "source": "推估補入"
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
          "source": "推估補入"
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
          "source": "推估補入"
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
          "source": "推估補入"
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
          "source": "推估補入"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
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
          "source": "已實現損益底稿"
        }
      ],
      "orders": [
        {
          "date": "2026-03-08",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "buy",
          "price": 56.06,
          "shares": 1000,
          "status": "推估補入"
        },
        {
          "date": "2026-03-08",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "buy",
          "price": 55.04,
          "shares": 845,
          "status": "推估補入"
        },
        {
          "date": "2026-03-08",
          "symbol": "2353",
          "name": "宏碁",
          "action": "buy",
          "price": 27.41,
          "shares": 2000,
          "status": "推估補入"
        },
        {
          "date": "2026-03-08",
          "symbol": "2353",
          "name": "宏碁",
          "action": "buy",
          "price": 26.82,
          "shares": 2000,
          "status": "推估補入"
        },
        {
          "date": "2026-03-10",
          "symbol": "6488",
          "name": "環球晶",
          "action": "buy",
          "price": 432.52,
          "shares": 250,
          "status": "推估補入"
        },
        {
          "date": "2026-04-08",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "sell",
          "price": 58.65,
          "shares": 1000,
          "status": "已實現補入"
        },
        {
          "date": "2026-04-08",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "sell",
          "price": 58.55,
          "shares": 845,
          "status": "已實現補入"
        },
        {
          "date": "2026-04-08",
          "symbol": "2353",
          "name": "宏碁",
          "action": "sell",
          "price": 27.35,
          "shares": 2000,
          "status": "已實現補入"
        },
        {
          "date": "2026-04-08",
          "symbol": "2353",
          "name": "宏碁",
          "action": "sell",
          "price": 27.35,
          "shares": 2000,
          "status": "已實現補入"
        },
        {
          "date": "2026-04-10",
          "symbol": "6488",
          "name": "環球晶",
          "action": "sell",
          "price": 486,
          "shares": 250,
          "status": "已實現補入"
        },
        {
          "date": "2026-04-24",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "sell",
          "price": 71.55,
          "shares": 309,
          "status": "截圖可見"
        },
        {
          "date": "2026-04-27",
          "symbol": "00757",
          "name": "統一 FANG+",
          "action": "buy",
          "price": 120.4,
          "shares": 350,
          "status": "截圖可見"
        },
        {
          "date": "2026-04-27",
          "symbol": "00757",
          "name": "統一 FANG+",
          "action": "buy",
          "price": 120.4,
          "shares": 150,
          "status": "截圖可見"
        },
        {
          "date": "2026-04-27",
          "symbol": "00757",
          "name": "統一 FANG+",
          "action": "buy",
          "price": 120.4,
          "shares": 500,
          "status": "截圖可見"
        },
        {
          "date": "2026-04-27",
          "symbol": "00757",
          "name": "統一 FANG+",
          "action": "buy",
          "price": 120.35,
          "shares": 681,
          "status": "截圖可見"
        },
        {
          "date": "2026-04-27",
          "symbol": "4739",
          "name": "康普",
          "action": "buy",
          "price": 83.1,
          "shares": 500,
          "status": "截圖可見"
        },
        {
          "date": "2026-04-27",
          "symbol": "4739",
          "name": "康普",
          "action": "buy",
          "price": 84.1,
          "shares": 500,
          "status": "截圖可見"
        },
        {
          "date": "2026-04-29",
          "symbol": "00757",
          "name": "統一 FANG+",
          "action": "sell",
          "price": 120.9,
          "shares": 2000,
          "status": "截圖可見"
        },
        {
          "date": "2026-04-29",
          "symbol": "2377",
          "name": "微星",
          "action": "sell",
          "price": 100,
          "shares": 500,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-06",
          "symbol": "4739",
          "name": "康普",
          "action": "buy",
          "price": 91.1,
          "shares": 500,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-08",
          "symbol": "4739",
          "name": "康普",
          "action": "buy",
          "price": 86,
          "shares": 500,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-13",
          "symbol": "2377",
          "name": "微星",
          "action": "sell",
          "price": 113,
          "shares": 500,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-14",
          "symbol": "6143",
          "name": "振曜",
          "action": "buy",
          "price": 99,
          "shares": 1000,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-20",
          "symbol": "6907",
          "name": "雅特力-KY",
          "action": "buy",
          "price": 110.5,
          "shares": 1000,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-22",
          "symbol": "6907",
          "name": "雅特力-KY",
          "action": "sell",
          "price": 119.5,
          "shares": 1000,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-26",
          "symbol": "6732",
          "name": "昇佳電子",
          "action": "buy",
          "price": 181.5,
          "shares": 104,
          "status": "部分成交"
        },
        {
          "date": "2026-05-27",
          "symbol": "6732",
          "name": "昇佳電子",
          "action": "buy",
          "price": 182,
          "shares": 400,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-28",
          "symbol": "6732",
          "name": "昇佳電子",
          "action": "buy",
          "price": 171.467,
          "shares": 500,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-28",
          "symbol": "6143",
          "name": "振曜",
          "action": "sell",
          "price": 102.5,
          "shares": 1000,
          "status": "截圖可見"
        },
        {
          "date": "2026-05-28",
          "symbol": "3141",
          "name": "晶宏",
          "action": "buy",
          "price": 81.6,
          "shares": 1000,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-08",
          "symbol": "2317",
          "name": "鴻海",
          "action": "buy",
          "price": 264.5,
          "shares": 100,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-08",
          "symbol": "4739",
          "name": "康普",
          "action": "sell",
          "price": 115,
          "shares": 1000,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-08",
          "symbol": "3141",
          "name": "晶宏",
          "action": "sell",
          "price": 66.9,
          "shares": 1000,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-08",
          "symbol": "2379",
          "name": "瑞昱",
          "action": "buy",
          "price": 594.709,
          "shares": 55,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-09",
          "symbol": "2317",
          "name": "鴻海",
          "action": "buy",
          "price": 272,
          "shares": 150,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-09",
          "symbol": "2379",
          "name": "瑞昱",
          "action": "sell",
          "price": 631,
          "shares": 55,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-10",
          "symbol": "2317",
          "name": "鴻海",
          "action": "buy",
          "price": 266.5,
          "shares": 100,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-10",
          "symbol": "2317",
          "name": "鴻海",
          "action": "buy",
          "price": 269,
          "shares": 250,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-12",
          "symbol": "6907",
          "name": "雅特力-KY",
          "action": "sell",
          "price": 142.5,
          "shares": 50,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-15",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "sell",
          "price": 97.6,
          "shares": 673,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-16",
          "symbol": "00830",
          "name": "國泰費城半導體",
          "action": "sell",
          "price": 98.15,
          "shares": 41,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-16",
          "symbol": "2317",
          "name": "鴻海",
          "action": "sell",
          "price": 270,
          "shares": 300,
          "status": "截圖可見"
        },
        {
          "date": "2026-06-17",
          "symbol": "4739",
          "name": "康普",
          "action": "sell",
          "price": 120.5,
          "shares": 500,
          "status": "截圖可見"
        }
      ],
      "computed": {
        "positionCost": 298512.0,
        "realizedByDate": [
          {
            "date": "2026-04-08",
            "realizedPnl": 5650.0
          },
          {
            "date": "2026-04-10",
            "realizedPnl": 12835.0
          },
          {
            "date": "2026-04-24",
            "realizedPnl": 2238.0
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
            "realizedPnl": 10093.0
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
            "equity": 1000000.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-08",
            "realizedPnl": 5650.0,
            "unrealizedPnl": 0.0,
            "equity": 1005650.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-10",
            "realizedPnl": 18485.0,
            "unrealizedPnl": 0.0,
            "equity": 1018485.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-24",
            "realizedPnl": 20723.0,
            "unrealizedPnl": 0.0,
            "equity": 1020723.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-04-29",
            "realizedPnl": 24042.0,
            "unrealizedPnl": 0.0,
            "equity": 1024042.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-13",
            "realizedPnl": 33577.0,
            "unrealizedPnl": 0.0,
            "equity": 1033577.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-22",
            "realizedPnl": 41892.0,
            "unrealizedPnl": 0.0,
            "equity": 1041892.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-28",
            "realizedPnl": 44798.0,
            "unrealizedPnl": 0.0,
            "equity": 1044798.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-08",
            "realizedPnl": 60461.0,
            "unrealizedPnl": 0.0,
            "equity": 1060461.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-09",
            "realizedPnl": 62259.0,
            "unrealizedPnl": 0.0,
            "equity": 1062259.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-12",
            "realizedPnl": 62744.0,
            "unrealizedPnl": 0.0,
            "equity": 1062744.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-15",
            "realizedPnl": 72837.0,
            "unrealizedPnl": 0.0,
            "equity": 1072837.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-16",
            "realizedPnl": 72682.0,
            "unrealizedPnl": 0.0,
            "equity": 1072682.0,
            "drawdown": -155.0,
            "drawdownPct": -0.014447674716662457
          },
          {
            "date": "2026-06-17",
            "realizedPnl": 87053.0,
            "unrealizedPnl": -107.0,
            "equity": 1086946.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          }
        ],
        "contributions": [
          {
            "symbol": "4739",
            "name": "康普",
            "realizedPnl": 45145.0,
            "unrealizedPnl": 18168.0,
            "totalPnl": 63313.0
          },
          {
            "symbol": "00830",
            "name": "國泰費城半導體",
            "realizedPnl": 17683.0,
            "unrealizedPnl": 0.0,
            "totalPnl": 17683.0
          },
          {
            "symbol": "6488",
            "name": "環球晶",
            "realizedPnl": 12835.0,
            "unrealizedPnl": 0.0,
            "totalPnl": 12835.0
          },
          {
            "symbol": "2377",
            "name": "微星",
            "realizedPnl": 12598.0,
            "unrealizedPnl": 0.0,
            "totalPnl": 12598.0
          },
          {
            "symbol": "6907",
            "name": "雅特力-KY",
            "realizedPnl": 8800.0,
            "unrealizedPnl": 0.0,
            "totalPnl": 8800.0
          },
          {
            "symbol": "6143",
            "name": "振曜",
            "realizedPnl": 2906.0,
            "unrealizedPnl": 0.0,
            "totalPnl": 2906.0
          },
          {
            "symbol": "2379",
            "name": "瑞昱",
            "realizedPnl": 1798.0,
            "unrealizedPnl": 0.0,
            "totalPnl": 1798.0
          },
          {
            "symbol": "2317",
            "name": "鴻海",
            "realizedPnl": -172.0,
            "unrealizedPnl": 678.0,
            "totalPnl": 506.0
          },
          {
            "symbol": "2353",
            "name": "宏碁",
            "realizedPnl": 315.0,
            "unrealizedPnl": 0.0,
            "totalPnl": 315.0
          },
          {
            "symbol": "00757",
            "name": "統一 FANG+",
            "realizedPnl": 256.0,
            "unrealizedPnl": 0.0,
            "totalPnl": 256.0
          },
          {
            "symbol": "3141",
            "name": "晶宏",
            "realizedPnl": -15111.0,
            "unrealizedPnl": 0.0,
            "totalPnl": -15111.0
          },
          {
            "symbol": "6732",
            "name": "昇佳電子",
            "realizedPnl": 0.0,
            "unrealizedPnl": -18953.0,
            "totalPnl": -18953.0
          }
        ],
        "stats": {
          "tradeCount": 19,
          "winCount": 16,
          "lossCount": 3,
          "winRatePct": 84.21052631578947,
          "avgWin": 6415.875,
          "avgLoss": -5200.333333333333,
          "profitFactor": 6.579962822895968,
          "bestTrade": 30774.0,
          "worstTrade": -15111.0,
          "maxDrawdown": -155.0,
          "maxDrawdownPct": -0.014447674716662457
        }
      },
      "validation": {
        "status": "warning",
        "checks": [
          {
            "label": "已實現損益合計",
            "ok": true,
            "actual": 87053.0,
            "expected": 87053.0,
            "diff": 0.0
          },
          {
            "label": "未實現損益合計",
            "ok": true,
            "actual": -107.0,
            "expected": -107.0,
            "diff": 0.0
          },
          {
            "label": "股票庫存市值合計",
            "ok": true,
            "actual": 298405.0,
            "expected": 298405.0,
            "diff": 0.0
          },
          {
            "label": "總損益",
            "ok": true,
            "actual": 86946.0,
            "expected": 86946.0,
            "diff": 0.0
          },
          {
            "label": "目前推估總資產",
            "ok": true,
            "actual": 1086946.0,
            "expected": 1086946.0,
            "diff": 0.0
          },
          {
            "label": "推估現金",
            "ok": true,
            "actual": 788541.0,
            "expected": 788541.0,
            "diff": 0.0
          },
          {
            "label": "總報酬率",
            "ok": true,
            "actual": 8.6946,
            "expected": 8.69,
            "diff": 0.0046
          },
          {
            "label": "2317 庫存損益",
            "ok": true,
            "actual": 678.0,
            "expected": 678.0,
            "diff": 0.0
          },
          {
            "label": "4739 庫存損益",
            "ok": true,
            "actual": 18168.0,
            "expected": 18168.0,
            "diff": 0.0
          },
          {
            "label": "6732 庫存損益",
            "ok": true,
            "actual": -18953.0,
            "expected": -18953.0,
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
      "initialCapital": 20000,
      "currentDate": "2026-06-17",
      "orderLogComplete": true,
      "dataQuality": [
        "總覽、庫存合計、已實現損益合計可內部驗算。",
        "成交/委託紀錄可用完全成交股數重算目前庫存：BDC 24 股、GEV 1 股。",
        "COHR 2026-06-05/2026-06-06 日期需確認是美股交易日或台灣券商顯示日；績效表採 2026-06-05。"
      ],
      "summary": {
        "realizedPnl": 1205,
        "unrealizedPnl": 431.11,
        "totalPnl": 1636.11,
        "currentAssets": 21636.11,
        "totalReturnPct": 8.18,
        "cash": 17691.49,
        "marketValue": 3944.62
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
        },
        {
          "symbol": "GEV",
          "name": "奇異維諾瓦",
          "shares": 1,
          "marketValue": 1011.58,
          "cost": 901.72,
          "unrealizedPnl": 109.86,
          "returnPct": 12.18
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
        }
      ],
      "computed": {
        "positionCost": 3513.51,
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
          }
        ],
        "equitySeries": [
          {
            "date": "2026-05-26",
            "realizedPnl": 0.0,
            "unrealizedPnl": 0.0,
            "equity": 20000.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-05-29",
            "realizedPnl": 662.16,
            "unrealizedPnl": 0.0,
            "equity": 20662.16,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-01",
            "realizedPnl": 854.8399999999999,
            "unrealizedPnl": 0.0,
            "equity": 20854.84,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-02",
            "realizedPnl": 1105.4399999999998,
            "unrealizedPnl": 0.0,
            "equity": 21105.44,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-03",
            "realizedPnl": 1186.08,
            "unrealizedPnl": 0.0,
            "equity": 21186.08,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-05",
            "realizedPnl": 1191.31,
            "unrealizedPnl": 0.0,
            "equity": 21191.31,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-08",
            "realizedPnl": 1177.49,
            "unrealizedPnl": 0.0,
            "equity": 21177.49,
            "drawdown": -13.819999999999709,
            "drawdownPct": -0.06521541141156309
          },
          {
            "date": "2026-06-11",
            "realizedPnl": 1098.62,
            "unrealizedPnl": 0.0,
            "equity": 21098.62,
            "drawdown": -92.69000000000233,
            "drawdownPct": -0.43739627233994655
          },
          {
            "date": "2026-06-15",
            "realizedPnl": 1110.09,
            "unrealizedPnl": 0.0,
            "equity": 21110.09,
            "drawdown": -81.22000000000116,
            "drawdownPct": -0.3832703122176079
          },
          {
            "date": "2026-06-16",
            "realizedPnl": 1205.0,
            "unrealizedPnl": 0.0,
            "equity": 21205.0,
            "drawdown": 0.0,
            "drawdownPct": 0.0
          },
          {
            "date": "2026-06-17",
            "realizedPnl": 1205.0,
            "unrealizedPnl": 431.11,
            "equity": 21636.11,
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
            "totalPnl": 489.13
          },
          {
            "symbol": "BDC",
            "name": "百通",
            "realizedPnl": 0.0,
            "unrealizedPnl": 321.25,
            "totalPnl": 321.25
          },
          {
            "symbol": "GEV",
            "name": "奇異維諾瓦",
            "realizedPnl": 187.01999999999998,
            "unrealizedPnl": 109.86,
            "totalPnl": 296.88
          },
          {
            "symbol": "COHR",
            "name": "Coherent",
            "realizedPnl": 290.08000000000004,
            "unrealizedPnl": 0.0,
            "totalPnl": 290.08000000000004
          },
          {
            "symbol": "HPE",
            "name": "HP Enterprise",
            "realizedPnl": 192.68,
            "unrealizedPnl": 0.0,
            "totalPnl": 192.68
          },
          {
            "symbol": "QCOM",
            "name": "Qualcomm",
            "realizedPnl": 59.91,
            "unrealizedPnl": 0.0,
            "totalPnl": 59.91
          },
          {
            "symbol": "ETN",
            "name": "Eaton",
            "realizedPnl": -13.82,
            "unrealizedPnl": 0.0,
            "totalPnl": -13.82
          }
        ],
        "stats": {
          "tradeCount": 17,
          "winCount": 13,
          "lossCount": 4,
          "winRatePct": 76.47058823529412,
          "avgWin": 109.61538461538461,
          "avgLoss": -55.0,
          "profitFactor": 6.4772727272727275,
          "bestTrade": 662.16,
          "worstTrade": -95.0,
          "maxDrawdown": -92.69000000000233,
          "maxDrawdownPct": -0.43739627233994655
        }
      },
      "validation": {
        "status": "warning",
        "checks": [
          {
            "label": "已實現損益合計",
            "ok": true,
            "actual": 1205.0,
            "expected": 1205.0,
            "diff": 0.0
          },
          {
            "label": "未實現損益合計",
            "ok": true,
            "actual": 431.11,
            "expected": 431.11,
            "diff": 0.0
          },
          {
            "label": "股票庫存市值合計",
            "ok": true,
            "actual": 3944.62,
            "expected": 3944.62,
            "diff": 0.0
          },
          {
            "label": "總損益",
            "ok": true,
            "actual": 1636.11,
            "expected": 1636.11,
            "diff": 0.0
          },
          {
            "label": "目前推估總資產",
            "ok": true,
            "actual": 21636.11,
            "expected": 21636.11,
            "diff": 0.0
          },
          {
            "label": "推估現金",
            "ok": true,
            "actual": 17691.49,
            "expected": 17691.49,
            "diff": 0.0
          },
          {
            "label": "總報酬率",
            "ok": true,
            "actual": 8.1806,
            "expected": 8.18,
            "diff": 0.0006
          },
          {
            "label": "BDC 庫存損益",
            "ok": true,
            "actual": 321.25,
            "expected": 321.25,
            "diff": 0.0
          },
          {
            "label": "GEV 庫存損益",
            "ok": true,
            "actual": 109.86,
            "expected": 109.86,
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
            "actual": 1.0,
            "expected": 1.0,
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
          "actual": 87053.0,
          "expected": 87053.0,
          "diff": 0.0
        },
        {
          "label": "未實現損益合計",
          "ok": true,
          "actual": -107.0,
          "expected": -107.0,
          "diff": 0.0
        },
        {
          "label": "股票庫存市值合計",
          "ok": true,
          "actual": 298405.0,
          "expected": 298405.0,
          "diff": 0.0
        },
        {
          "label": "總損益",
          "ok": true,
          "actual": 86946.0,
          "expected": 86946.0,
          "diff": 0.0
        },
        {
          "label": "目前推估總資產",
          "ok": true,
          "actual": 1086946.0,
          "expected": 1086946.0,
          "diff": 0.0
        },
        {
          "label": "推估現金",
          "ok": true,
          "actual": 788541.0,
          "expected": 788541.0,
          "diff": 0.0
        },
        {
          "label": "總報酬率",
          "ok": true,
          "actual": 8.6946,
          "expected": 8.69,
          "diff": 0.0046
        },
        {
          "label": "2317 庫存損益",
          "ok": true,
          "actual": 678.0,
          "expected": 678.0,
          "diff": 0.0
        },
        {
          "label": "4739 庫存損益",
          "ok": true,
          "actual": 18168.0,
          "expected": 18168.0,
          "diff": 0.0
        },
        {
          "label": "6732 庫存損益",
          "ok": true,
          "actual": -18953.0,
          "expected": -18953.0,
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
          "actual": 1205.0,
          "expected": 1205.0,
          "diff": 0.0
        },
        {
          "label": "未實現損益合計",
          "ok": true,
          "actual": 431.11,
          "expected": 431.11,
          "diff": 0.0
        },
        {
          "label": "股票庫存市值合計",
          "ok": true,
          "actual": 3944.62,
          "expected": 3944.62,
          "diff": 0.0
        },
        {
          "label": "總損益",
          "ok": true,
          "actual": 1636.11,
          "expected": 1636.11,
          "diff": 0.0
        },
        {
          "label": "目前推估總資產",
          "ok": true,
          "actual": 21636.11,
          "expected": 21636.11,
          "diff": 0.0
        },
        {
          "label": "推估現金",
          "ok": true,
          "actual": 17691.49,
          "expected": 17691.49,
          "diff": 0.0
        },
        {
          "label": "總報酬率",
          "ok": true,
          "actual": 8.1806,
          "expected": 8.18,
          "diff": 0.0006
        },
        {
          "label": "BDC 庫存損益",
          "ok": true,
          "actual": 321.25,
          "expected": 321.25,
          "diff": 0.0
        },
        {
          "label": "GEV 庫存損益",
          "ok": true,
          "actual": 109.86,
          "expected": 109.86,
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
          "actual": 1.0,
          "expected": 1.0,
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
