# Public Reports Folder

這個資料夾是網站唯一的公開報告入口。

## 上架

1. 將要公開的 HTML 報告放在 `published_reports/`。
2. 若報告引用圖片，將圖片放在 `published_reports/charts/`。
3. HTML 內的圖片路徑使用 `charts/檔名.png`。
4. 執行 `python3 scripts/build_public_site.py`。
5. commit 並 push 到 GitHub，GitHub Pages 會自動更新。

## 下架

從 `published_reports/` 刪除對應 HTML，再重新建置、commit、push。

## 注意

`output/` 可以當分析產出或草稿區；只有放進 `published_reports/` 的 HTML 會出現在公開網站。
