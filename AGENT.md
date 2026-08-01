# 自動補內容代理指南(怪奇檔案 CURIOSA / blackmaoeye.com)

這個 repo 自給自足:產生器(`build.py` + `_defs.svg` + `assets/`)與產出的 HTML 都在這裡。
GitHub Pages 從 `main` / root 供應,推到 main 約 60 秒生效。

## 動作流程
1. 讀 `CONTEXT.md` 掌握定位、人設、文章 schema、品質基準(**B 精緻:實查證、短句見血、長段見肉,嚴禁淺薄拼湊**)。
2. 平衡加內容:**怪談(世界奇聞)+3、動漫 +3、極短篇(夜話)+6**。避免與現有題目重複(先 `python -c "import build; ..."` 列出各板塊 slug)。
3. 每篇怪談/動漫**先用 WebSearch 查證事實**;查不到可靠來源就換題,**絕不杜撰**(本站命脈是「真實」)。
4. 圖片:世界奇聞用 Wikimedia Commons 自由授權真實照片(查檔名+作者+授權,並確認能載入);動漫**不放版權劇照**,改用「相關」自由授權真圖(作者肖像、公有領域實物、公共雕像)或既有插圖。夜話不用圖。
5. 在 `build.py` 的 `ARTICLES` / `STORIES` 加項目 → `bash deploy.sh`(建置並複製到根)。
6. `git add -A && git commit`(署名 `TAIWANBEAR <s4678000s@gmail.com>` + `Co-Authored-By: Claude`)→ `git push origin main`。若無法直接 push main,改開 PR。
7. 驗證:`curl -s -o /dev/null -w '%{http_code}' https://blackmaoeye.com/curiosa/<slug>.html` 應為 200。
8. **勿刪** `google041712966e26603e.html`(Search Console 驗證檔)。

## 寫作標準(硬性)
- 導言、小標、結尾金句、貓評(mao)都要有記憶點;正文給可查證的機制與細節,不是常識複述。
- 貓評 = 中年黑貓「貓編」口吻,幽默略吐槽。
