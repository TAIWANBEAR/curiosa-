# 怪奇檔案 CURIOSA — 上線說明書

這是一個**靜態網站**(純 HTML/CSS/JS,無需後端),SEO 就緒,可直接部署。

## 📁 檔案結構
```
site/
├─ index.html          首頁(精選奇聞 + 夜話小說)
├─ curiosa/            7 篇文章,各自獨立網址(SEO 關鍵)
│   ├─ whittier.html
│   ├─ immortal-jellyfish.html
│   └─ … 共 7 篇
├─ about.html          關於頁(AdSense 審核需要)
├─ privacy.html        隱私權頁(AdSense 審核需要)
├─ styles.css / app.js 共用樣式與腳本
├─ sitemap.xml         給 Google 的網站地圖
└─ robots.txt
```

## 🚀 上線三步(約 20 分鐘,近乎零成本)

### 1. 買網域
到 Cloudflare / Gandi / Namecheap 買一個網域(約 NT$300–500/年)。

### 2. 部署(擇一,都免費)
- **Cloudflare Pages**(推薦):登入 → Workers & Pages → Create → 上傳 `site/` 資料夾 → 完成。
- **Netlify**:直接把 `site/` 資料夾拖到 https://app.netlify.com/drop 。

### 3. 改網域設定
把 `build.py` 最上面的 `BASE` 改成你的網域,重跑 `python build.py`,再重新部署。這會讓 canonical、sitemap、OG 分享卡指向正確網址。

## 🔎 已內建的 SEO(不用你動手)
- ✅ 每篇文章**獨立網址** + **獨立 title / description**
- ✅ **JSON-LD** 結構化資料(Article schema)
- ✅ **Open Graph / Twitter 分享卡**(貼到社群會有大圖標題)
- ✅ **sitemap.xml + robots.txt**
- ✅ 語意化標題階層、內部連結(延伸閱讀)、手機自適應、深淺色

### 上線後要做的:
1. 到 **Google Search Console** 驗證網域,提交 `sitemap.xml`。
2. 每篇文章的目標長尾關鍵字已寫在 `build.py` 各篇的 `keywords`。

## 🖼️ 關於照片
文章照片來自 **Wikimedia Commons**(合法授權,已於圖說標註作者/授權)。
- 圖片以 `Special:FilePath` 直接引用,**7 張已實測可正常載入**。
- 若想更快、更穩,可把圖片下載到 `site/curiosa/img/` 自行託管(記得保留出處標註)。
- 若哪張圖失效,版面會**自動退回本編的手繪插畫**,不會破圖。

## 💰 接 Google AdSense
1. 內容先**灌到 20–30 篇**再申請(目前 7 篇,審核容易被打回「內容不足」)。
2. 到 https://adsense.google.com 申請,綁你的網域與收款帳戶(**這一步只能你本人做**)。
3. 過審後,把廣告碼貼到各頁 `<!-- AD SLOT -->` 的位置(index 與文章頁都有預留)。
4. 提醒:累積 **US$100** 才會撥款;新站自然流量通常要 **3–6 個月**才起得來。

## ✍️ 怎麼新增文章
打開 `build.py`,在 `ARTICLES` 清單複製一個 `dict`、填好 slug/標題/內文/圖片,存檔後重跑:
```bash
python build.py
```
新文章會自動生成獨立頁面、加進首頁卡片與 sitemap。

—— 貓編 🐈‍⬛
