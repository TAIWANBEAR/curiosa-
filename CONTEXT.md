# CONTEXT — 怪奇檔案 CURIOSA / blackmaoeye.com

> 這份檔案是本專案的「共用領域語言」。任何 agent 或協作者在動手前先讀它,
> 之後對話與程式都沿用這裡的詞彙與規則,不要自行發明說法或偏離定位。

## 這是什麼

一個**廣告變現的內容策展網站**:蒐集世界各地真實卻難以置信的奇聞,
由一位虛構的中年黑貓總編「**貓編**」以幽默、略帶吐槽的視角撰寫、查證、配上原創插圖。

- 正式站名：**怪奇檔案 CURIOSA**
- 網域：**https://blackmaoeye.com**（Namecheap 自訂網域）
- 標語：世界各地真實卻難以置信的事物 — 由一隻中年黑貓精選、查證、順便吐槽。
- 部署：GitHub Pages，repo `TAIWANBEAR/curiosa-`，Deploy from branch `main` / root，CNAME 已接。

## 定位與品質基準（最重要，別踩線）

- **走「B 精緻路線」**：每篇都**實際查證**、寫出帶入感與敘事。
- **嚴禁淺薄拼湊**：不准把幾則網路傳聞湊一湊充數。使用者對這點態度強硬——寧可少寫，不要爛寫。
- 每篇都要有**可查證的來源**（`sources` 欄），並在正文中呈現前因後果,不是條列冷知識。

## 角色：貓編（Mao-bian）

- 設定 = 使用者自己養的一隻**綠眼、耳朵不太尖的中年黑貓**。
- 語氣：幽默、慵懶、世故，愛用「能量管理」「本編」自稱，句尾常有輕吐槽。
- 每篇文章結尾的 `mao` 欄 = **貓評**,用貓編口吻對該則奇聞下一句評論。
- 另有「貓編夜話」= 無厘頭極短篇小說(獨立單元)。

## 內容結構

三大類內容:
1. **世界奇聞**(預設) — 真實的世界各地怪事。
2. **動漫怪談・冷知識** — 文章 dict 加 `section="anime"` 會進首頁「動漫專區」。
   - ⚠️ 動漫劇照有版權 → **不得放劇照**,一律用原創「貓編看電視」插圖(`sym="il-anime..."`,`img` 省略)。
3. **貓編夜話** — 極短篇小說單元。

## 技術架構

純靜態多頁站,由單一 Python 產生器建置。**沒有前端框架、沒有 build 工具鏈,就是 Python 產字串。**

- 產生器:`build.py`（+ 共用 SVG `_defs.svg`）→ 輸出到 `./site/`。
- 加新文章:在 `build.py` 的 `ARTICLES` 清單加一個 dict → 重跑 `python build.py`。
- `BASE`(第 14 行)= 網域,影響 canonical / sitemap / OG / CNAME。換網域時只改這行重生成。
- SEO 已內建:每篇獨立網址 + 獨立 title/description + JSON-LD + OG 卡 + sitemap.xml + robots.txt。
- AdSense:拿到發布商 ID 填 `ADSENSE_PUB`(第 21 行)即自動注入。

### 文章 dict 的欄位(schema)

| 欄位 | 必填 | 說明 |
|------|------|------|
| `slug` | ✔ | 網址片段,產生 `/curiosa/<slug>.html` |
| `title` | ✔ | 文章標題(也是 SEO title） |
| `cat` | ✔ | 分類標籤字串,例 `"動漫冷知識 · Animation"` |
| `deck` | ✔ | 導言/摘要(也用作 meta description） |
| `keywords` | ✔ | SEO 關鍵字,逗號分隔 |
| `meta` | ✔ | 資訊卡,tuple 清單 `[("技法","..."),...]` |
| `sym` | ✔ | 要用的 SVG symbol id(來自 `_defs.svg`） |
| `body` | ✔ | 正文 HTML(`<h2>`/`<p>`/`<blockquote>`） |
| `mao` | ✔ | 貓評(貓編口吻一句話） |
| `sources` | ✔ | 查證來源(以 `·` 分隔） |
| `section` | 選填 | 填 `"anime"` 進動漫專區;省略 = 世界奇聞 |
| `img` | 選填 | 真實照片外連;動漫類**省略**(改用插圖) |

### 真實照片規則(踩過雷)

- 真實照片走 **Wikimedia Commons `Special:FilePath`** 外連,載入失敗會自動退回 SVG 插圖。
- **加圖務必先用 Commons API 查真實檔名並實測載入**(曾經 7 張錯 3 張)。

## 部署流程(已打通,可自動)

repo 已 clone 在 `./repo`,git + GCM 憑證現成,可直接推送,**不必叫使用者手動拖檔案**。

1. 改 `build.py` → `python build.py`(輸出 `./site/`）
2. 把 `site/*` 覆蓋到 `./repo`
3. 於 `./repo`:`git add` → commit(署名 **TAIWANBEAR** + `Co-Authored-By: Claude`）→ `git push origin main`
4. 約 60 秒後 Pages 生效。

## 現況與期望值(已對齊)

- 已上線:20 篇世界奇聞 + 10 篇動漫 + 35 篇夜話。
- **變現預期務實**:靠 SEO 第一個月幾乎賺不到 500 台幣;AdSense 需累積 US$100 才撥款,新站自然流量要 3–6 個月。月初想有現金流只能靠社群自導流量(Threads / Dcard)。

## 待辦(roadmap）

1. Google AdSense 前置(驗證碼位置 → 填 `ADSENSE_PUB`）
2. Search Console 提交 sitemap
3. 續寫內容(維持 B 精緻路線）
4. 社群導流貼文衝月初流量
