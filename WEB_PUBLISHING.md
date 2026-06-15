# 股票分析網站發布流程

這個專案的公開網站採用靜態網站架構：報告來源放在 `output/`，網站輸出放在 `docs/`。

## 本機更新

1. 將新的 HTML 報告放進 `output/`。
2. 如果報告有圖片，放在 `output/charts/`，並在 HTML 裡使用 `charts/檔名.png`。
3. 執行：

```bash
python3 scripts/build_public_site.py
```

4. 打開 `docs/index.html` 檢查首頁。

## 排除不想公開的報告

全公開網站代表任何知道網址的人都可能看見內容。若某些報告含有持股、均價、券商資訊或你不想公開的資料，請在 `site.config.json` 的 `excludeHtml` 加入檔名，例如：

```json
"excludeHtml": [
  "us_bdc_stock_analysis_framework_20260614.html"
]
```

更新設定後再執行建站腳本。

## GitHub Pages 免費網址

1. 在 GitHub 建立一個 public repository。
2. 將此資料夾 push 到 GitHub。
3. 到 repository 的 `Settings > Pages`。
4. Source 選 `GitHub Actions`。
5. 之後每次 push 新報告到 `output/`，GitHub Actions 會自動發布。

發布成功後，網址通常會是：

```text
https://你的帳號.github.io/你的repo名稱/
```

## 手動發布

如果暫時不想使用 GitHub Actions，也可以只把 `docs/` 這個資料夾上傳到 Netlify Drop、Cloudflare Pages 或其他靜態網站服務。
