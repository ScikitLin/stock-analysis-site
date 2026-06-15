# 股票分析網站發布流程

這個專案的公開網站採用靜態網站架構：

- `published_reports/`：真正公開的 HTML 報告來源。
- `published_reports/charts/`：公開報告會引用到的圖表圖片。
- `docs/`：建置後的網站輸出資料夾，由 GitHub Pages 發布。
- `output/`：可作為分析產出或草稿區，不會直接公開。

## 決定哪些報告要公開

要上架的 HTML 放進 `published_reports/`。

要下架的 HTML 從 `published_reports/` 刪除。

如果報告有圖片，放在 `published_reports/charts/`，並在 HTML 裡使用 `charts/檔名.png`。

## 本機更新

```bash
python3 scripts/build_public_site.py
```

建置完成後檢查 `docs/index.html`，確認首頁、搜尋、分類與報告連結正常。

## GitHub Pages 免費網址

目前網站設定為 GitHub Actions 自動發布。每次 push 到 GitHub 後，只要變更包含以下內容，就會重新建置並更新免費網址：

- `published_reports/**`
- `site_src/**`
- `site.config.json`
- `scripts/build_public_site.py`
- `.github/workflows/pages.yml`

公開網址：

```text
https://scikitlin.github.io/stock-analysis-site/
```

## 留言功能

首頁留言窗會限制 500 字，送出後開啟 GitHub Issue 草稿。這個做法不需要付費後端，也不會在網站本身保存留言資料。使用者若送出 Issue，GitHub 可能顯示其 GitHub 帳號。

## 隱私檢查

全公開網站代表任何知道網址的人都可能看見內容。放進 `published_reports/` 前，請先確認報告不含個人持股、均價、券商資訊、帳戶截圖或其他不想公開的內容。
