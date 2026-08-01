# -*- coding: utf-8 -*-
"""
怪奇檔案 CURIOSA — 靜態網站產生器
執行:  python build.py
輸出:  ./site/  (可直接拖到 Cloudflare Pages / Netlify 部署)

要新增一篇文章:在 ARTICLES 清單複製一個 dict、填好內容即可,重跑本檔。
"""
import os, html, pathlib, datetime, urllib.parse

# ============================================================
# 0. 設定 —— 上線前把這行換成你的網域(影響 canonical / sitemap / OG)
# ============================================================
BASE = "https://blackmaoeye.com"   # 自訂網域(Namecheap)
SITE = "怪奇檔案 CURIOSA"
TAGLINE = "世界各地真實卻難以置信的事物 — 由一隻中年黑貓精選、查證、順便吐槽。"
OUT = pathlib.Path(__file__).parent / "site"
TODAY = datetime.date.today().isoformat()

# ---- Google AdSense:核准後把發布商 ID 填進 ADSENSE_PUB,重跑 build.py 即全站生效 ----
ADSENSE_PUB = "ca-pub-8009796446380695"   # 已申請的 Google AdSense 發布商 ID
ADSENSE_HEAD = (('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=%s" crossorigin="anonymous"></script>' % ADSENSE_PUB) if ADSENSE_PUB else "")

# ============================================================
# 1. 共用資產:CSS / JS / SVG 貓與插畫定義
# ============================================================
CSS = r"""
:root{--bg:#EAE9E6;--surface:#F6F5F2;--sunk:#E1DFDA;--ink:#1A1714;--muted:#6E655D;
 --rule:#D8D3CC;--faint:#B7B1A9;--accent:#D3382E;--accent-soft:rgba(211,56,46,.12);--eye:#93A83A;
 --night:#14110E;--night-tx:#E9E4DB;--night-mut:#948C81;
 --serif:'Noto Serif TC','Songti TC','Source Han Serif TC',Georgia,serif;
 --sans:'Noto Sans TC','PingFang TC','Microsoft JhengHei',-apple-system,system-ui,sans-serif;
 --mono:ui-monospace,'SF Mono',Menlo,Consolas,monospace;--measure:66ch;}
@media (prefers-color-scheme:dark){:root{--bg:#121110;--surface:#1A1917;--sunk:#221F1C;--ink:#ECE8E2;
 --muted:#9A928A;--rule:#2C2926;--faint:#4A453F;--accent:#F5493C;--accent-soft:rgba(245,73,60,.16);--eye:#B6CB4E;}}
:root[data-theme=light]{--bg:#EAE9E6;--surface:#F6F5F2;--sunk:#E1DFDA;--ink:#1A1714;--muted:#6E655D;
 --rule:#D8D3CC;--faint:#B7B1A9;--accent:#D3382E;--accent-soft:rgba(211,56,46,.12);--eye:#93A83A;}
:root[data-theme=dark]{--bg:#121110;--surface:#1A1917;--sunk:#221F1C;--ink:#ECE8E2;--muted:#9A928A;
 --rule:#2C2926;--faint:#4A453F;--accent:#F5493C;--accent-soft:rgba(245,73,60,.16);--eye:#B6CB4E;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.65;-webkit-font-smoothing:antialiased;overflow-x:hidden}
.wrap{max-width:1240px;margin:0 auto;padding:0 24px}
a{color:inherit;text-decoration:none}
img{max-width:100%;height:auto;display:block}
#motes{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.5}
.page{position:relative;z-index:1}
/* top bar */
.topbar{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--rule)}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 24px}
.brand{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:19px}
.brand svg{width:30px;height:auto;color:var(--ink)}
.brand .eye{fill:var(--eye)}
.tnav{display:flex;align-items:center;gap:22px;font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.tnav a:hover{color:var(--accent)}
.tgl{background:none;border:1px solid var(--rule);color:var(--muted);border-radius:20px;padding:5px 12px;font-family:var(--mono);font-size:11px;cursor:pointer;letter-spacing:.08em}
.tgl:hover{color:var(--ink);border-color:var(--accent)}
@media(max-width:640px){.tnav a{display:none}}
/* masthead */
.masthead{text-align:center;padding:34px 0 26px;border-bottom:2px solid var(--ink)}
.catmark{width:80px;height:auto;color:var(--ink);margin:0 auto 10px;display:block}.catmark .eye{fill:var(--eye)}
.masthead .kick{font-family:var(--mono);font-size:11px;letter-spacing:.38em;text-transform:uppercase;color:var(--muted);margin-bottom:16px;padding-left:.38em}
.masthead h1{font-family:var(--serif);font-weight:700;margin:0;font-size:clamp(52px,12vw,110px);line-height:.9;letter-spacing:.04em}
.masthead .tag{margin-top:18px;color:var(--muted);font-size:15px}.masthead .tag em{color:var(--accent);font-style:normal}
/* ticker */
.ticker{background:var(--ink);color:var(--bg);overflow:hidden}
.ticker .wrap{display:flex;align-items:center;gap:20px;padding:9px 24px}
.ticker .lbl{flex:none;display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600}
.ticker .lbl svg{width:17px;height:auto;color:var(--bg)}.ticker .lbl .eye{fill:var(--eye)}
.ticker .items{display:flex;gap:34px;font-size:13px;white-space:nowrap;animation:slide 36s linear infinite}
.ticker .items span::before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--accent);margin-right:12px;vertical-align:middle}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media(prefers-reduced-motion:reduce){.ticker .items{animation:none;flex-wrap:wrap;white-space:normal}}
/* 貓評 */
.mao{display:flex;gap:12px;align-items:flex-start;background:var(--accent-soft);border-left:3px solid var(--accent);padding:12px 16px}
.mao .who{flex:none;display:flex;align-items:center;gap:7px;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:600;padding-top:3px}
.eyes{display:inline-flex;gap:3px}.eyes i{position:relative;width:7px;height:10px;background:var(--eye);border-radius:50%;display:block}
.eyes i::after{content:"";position:absolute;inset:0;margin:auto;width:1.6px;height:7px;background:#0c0c0c;border-radius:1px;opacity:.85}
.mao p{margin:0;color:var(--ink);font-size:14px;line-height:1.55}
/* cat poses */
.shead{display:flex;align-items:baseline;justify-content:space-between;gap:16px;margin:44px 0 20px;padding-bottom:12px;border-bottom:2px solid var(--ink)}
.shead .htitle{display:flex;align-items:center;gap:12px}.shead-cat{width:56px;height:auto;color:var(--ink)}
.shead h2{font-family:var(--serif);font-weight:700;font-size:24px;margin:0}
.shead .en{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.catplay-band{border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);background:var(--surface)}
.catplay-band .wrap{display:flex;align-items:center;justify-content:center;gap:28px;padding:22px 24px;flex-wrap:wrap}
.catplay{width:118px;height:auto;color:var(--ink)}
.catplay .toy{transform-box:view-box;transform-origin:132px 26px;animation:sway 1.9s ease-in-out infinite}
@keyframes sway{0%,100%{transform:rotate(-12deg)}50%{transform:rotate(15deg)}}
@media(prefers-reduced-motion:reduce){.catplay .toy{animation:none}}
.catplay-band .say{font-family:var(--serif);font-style:italic;color:var(--muted);font-size:15.5px;max-width:30ch}
/* card grid */
main{padding:44px 0 10px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--rule);border:1px solid var(--rule)}
a.card{background:var(--bg);display:flex;flex-direction:column;transition:background .15s}
a.card:hover{background:var(--surface)}
.card .thumb{aspect-ratio:16/10;background:var(--sunk);border-bottom:1px solid var(--rule);overflow:hidden}
.card .thumb svg,.card .thumb img{width:100%;height:100%;object-fit:cover;display:block}
.card .in{padding:22px 24px 24px;display:flex;flex-direction:column;flex:1}
.card .top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:14px}
.card .idx{font-family:var(--serif);font-size:15px;color:var(--faint);font-weight:700}
.card .cat{font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);font-weight:600}
.card h3{font-family:var(--serif);font-weight:700;margin:0 0 12px;font-size:21px;line-height:1.2}
.card p{margin:0 0 16px;color:var(--muted);font-size:14px;line-height:1.6}
.card .more{margin-top:auto;font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.seemore{margin:26px 0 6px;text-align:center}
.seemore a{display:inline-flex;align-items:center;gap:10px;font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink);border:2px solid var(--ink);padding:15px 32px;transition:background .15s,color .15s}
.seemore a:hover{background:var(--ink);color:var(--bg)}
.seemore a span{color:var(--accent);font-size:16px;line-height:1}
.seemore a:hover span{color:var(--bg)}
.arch-intro{color:var(--muted);font-size:15px;line-height:1.7;margin:0 0 22px;max-width:62ch}
/* fiction */
.stories{background:var(--night);color:var(--night-tx);padding:56px 0 60px}
.stories .head{text-align:center;margin-bottom:40px}
.stories .glow{display:inline-flex;gap:12px;margin-bottom:18px}
.stories .glow i{width:16px;height:22px;background:var(--eye);border-radius:50%;position:relative;box-shadow:0 0 18px 3px rgba(147,168,58,.5)}
.stories .glow i::after{content:"";position:absolute;inset:0;margin:auto;width:3px;height:15px;background:#0c0c0c;border-radius:2px}
.stories .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.28em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
.stories h2{font-family:var(--serif);font-weight:700;font-size:clamp(28px,5vw,40px);margin:0 0 12px}
.stories .sub{color:var(--night-mut);font-size:14.5px;max-width:52ch;margin:0 auto}
.story-col{max-width:640px;margin:0 auto}
.story{padding:30px 0;border-top:1px solid rgba(255,255,255,.1)}.story:first-child{border-top:none}
.story .no{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
.story h3{font-family:var(--serif);font-weight:700;font-size:23px;margin:0 0 14px}
.story p{font-family:var(--serif);font-size:17px;line-height:1.95;color:#D6D0C6;margin:0}
.stories .rest{text-align:center;margin-top:36px}.stories .rest svg{width:120px;height:auto;color:#4a443c}
.stories .signoff{max-width:640px;margin:30px auto 0;text-align:right;font-family:var(--serif);font-style:italic;color:var(--night-mut);font-size:15px}
/* ad */
.adslot{margin:40px 0;border:1px dashed var(--faint);background:repeating-linear-gradient(135deg,transparent,transparent 11px,var(--accent-soft) 11px,var(--accent-soft) 12px);text-align:center;padding:34px 20px}
.adslot .k{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}.adslot .k b{color:var(--accent)}
.adslot .s{margin-top:6px;font-size:12.5px;color:var(--faint)}
/* footer */
footer{border-top:2px solid var(--ink);margin-top:20px;padding:38px 0 60px}
.sign{display:flex;align-items:center;gap:16px;margin-bottom:22px}.sign svg{width:56px;height:auto;color:var(--ink)}.sign .eye{fill:var(--eye)}
.sign .by b{display:block;font-size:20px;font-family:var(--serif)}.sign .by span{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.fnote{max-width:var(--measure);color:var(--muted);font-size:14px}.fnote .accent{color:var(--accent);font-weight:600}
.fbar{display:flex;justify-content:space-between;flex-wrap:wrap;gap:16px;margin-top:30px;padding-top:18px;border-top:1px solid var(--rule);font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}
.fbar a:hover{color:var(--accent)}
/* ===== article page ===== */
.post{max-width:760px;margin:0 auto;padding:0 24px 70px}
.crumb{margin:22px 0 6px;font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
.crumb a:hover{color:var(--accent)}
.post .flag{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);font-weight:600;margin:12px 0 16px}
.post .flag::before{content:"";width:22px;height:2px;background:var(--accent)}
.post h1{font-family:var(--serif);font-weight:700;font-size:clamp(30px,5.5vw,50px);line-height:1.08;margin:0 0 18px}
.post .deck{font-size:18px;color:var(--muted);line-height:1.7;margin:0 0 20px;font-family:var(--serif)}
.post .pmeta{display:flex;flex-wrap:wrap;gap:6px 20px;padding:14px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
.post .pmeta b{color:var(--muted);font-weight:600}
figure.photo{margin:28px 0;border:1px solid var(--rule);background:var(--sunk);overflow:hidden}
figure.photo img{width:100%;aspect-ratio:16/9;object-fit:cover}
figure.photo .fallback{display:none}figure.photo.noimg img{display:none}figure.photo.noimg .fallback{display:block}
figure.photo .fallback svg{width:100%;height:auto;aspect-ratio:480/260;display:block;background:var(--sunk)}
figure.photo figcaption{padding:9px 14px;font-family:var(--mono);font-size:10.5px;letter-spacing:.03em;color:var(--faint);line-height:1.7;border-top:1px solid var(--rule)}
figure.photo figcaption b{color:var(--muted)}
.prose{margin-top:26px}.prose p{font-size:17px;line-height:1.9;margin:0 0 20px}
.prose h2{font-family:var(--serif);font-weight:700;font-size:22px;margin:34px 0 14px}
.prose b{color:var(--ink);font-weight:700}
.prose a{color:var(--accent);text-decoration:underline}
blockquote{margin:30px 0;padding:6px 0 6px 24px;border-left:3px solid var(--accent);font-family:var(--serif);font-size:22px;line-height:1.5;font-style:italic}
.post .mao{margin:30px 0}
.sources{margin-top:30px;padding-top:18px;border-top:1px solid var(--rule);font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}.sources b{color:var(--muted)}
.related{margin-top:44px;padding-top:24px;border-top:2px solid var(--ink)}
.related h2{font-family:var(--serif);font-size:20px;margin:0 0 16px}
.related ul{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.related a{color:var(--accent);font-family:var(--serif);font-size:17px}.related a:hover{text-decoration:underline}
@media(max-width:820px){.grid{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.grid{grid-template-columns:1fr}}
/* ---- wide layout + article sidebar ---- */
.layout{max-width:1240px;margin:0 auto;padding:0 24px;display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:50px;align-items:start}
.layout .post{max-width:none;margin:0;padding:0 0 40px}
aside.rail{position:sticky;top:60px;display:flex;flex-direction:column;gap:22px}
.rail .box{border:1px solid var(--rule);background:var(--surface);padding:20px}
.rail .box h3{font-family:var(--serif);font-weight:700;font-size:16px;margin:0 0 14px;padding-bottom:10px;border-bottom:2px solid var(--ink)}
.rail ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:12px;font-size:14px}
.rail ul a{color:var(--ink);line-height:1.45}.rail ul a:hover{color:var(--accent)}
.rail .catcard{text-align:center}
.rail .catcard svg{width:60px;height:auto;color:var(--ink);margin:0 auto 8px;display:block}
.rail .catcard .eye{fill:var(--eye)}
.rail .catcard b{font-family:var(--serif);font-size:19px;display:block}
.rail .catcard span{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.rail .chips{display:flex;flex-wrap:wrap;gap:8px}
.rail .chips a{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border:1px solid var(--rule);padding:5px 11px;border-radius:20px}
.rail .chips a:hover{color:var(--accent);border-color:var(--accent)}
.rail .adbox{border:1px dashed var(--faint);background:repeating-linear-gradient(135deg,transparent,transparent 10px,var(--accent-soft) 10px,var(--accent-soft) 11px);padding:30px 12px;text-align:center;font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);line-height:1.8}
.rail .adbox b{color:var(--accent)}
/* newsletter band */
.news-band{border-top:2px solid var(--ink);background:var(--surface)}
.news-band .wrap{display:flex;align-items:center;justify-content:space-between;gap:30px;padding:36px 24px;flex-wrap:wrap}
.news-band h3{font-family:var(--serif);font-weight:700;font-size:24px;margin:0 0 6px}
.news-band p{margin:0;color:var(--muted);font-size:14.5px}
.news-form{display:flex;gap:10px;flex:1;min-width:280px;max-width:440px}
.news-form input{flex:1;border:1px solid var(--rule);background:var(--bg);color:var(--ink);padding:12px 14px;font-family:var(--sans);font-size:14px}
.news-form button{border:none;background:var(--accent);color:#fff;font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;padding:0 22px;cursor:pointer}
.news-form button:hover{filter:brightness(1.08)}
/* rich footer */
.footer-grid{display:grid;grid-template-columns:1.7fr 1fr 1fr;gap:40px;padding-top:6px}
.footer-grid .fnote{margin-top:16px}
.footer-grid h4{font-family:var(--mono);font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink);margin:0 0 14px}
.footer-grid ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px;font-size:14px}
.footer-grid ul a{color:var(--muted)}.footer-grid ul a:hover{color:var(--accent)}
@media(max-width:960px){.layout{grid-template-columns:1fr}aside.rail{position:static}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.footer-grid{grid-template-columns:1fr}}
"""

JS = r"""
(function(){var b=document.getElementById('themebtn');if(b){var r=document.documentElement;
 var s=localStorage.getItem('theme');if(s)r.setAttribute('data-theme',s);
 b.onclick=function(){var cur=r.getAttribute('data-theme')||
  (matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  var nx=cur==='dark'?'light':'dark';r.setAttribute('data-theme',nx);localStorage.setItem('theme',nx);};}})();
(function(){var t=document.getElementById('tick');if(t)t.innerHTML+=t.innerHTML;})();
(function(){var cv=document.getElementById('motes');if(!cv)return;var ctx=cv.getContext('2d'),W,H,pts;
 var reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
 function col(){return getComputedStyle(document.documentElement).getPropertyValue('--faint').trim()||'#999';}
 function init(){W=cv.width=innerWidth;H=cv.height=innerHeight;pts=[];var n=Math.min(46,Math.round(W*H/26000));
  for(var i=0;i<n;i++)pts.push({x:Math.random()*W,y:Math.random()*H,r:Math.random()*1.6+.4,vx:(Math.random()-.5)*.16,vy:(Math.random()-.5)*.16});}
 function draw(){ctx.clearRect(0,0,W,H);ctx.globalAlpha=.55;ctx.fillStyle=col();
  for(var i=0;i<pts.length;i++){var p=pts[i];p.x+=p.vx;p.y+=p.vy;if(p.x<0)p.x=W;if(p.x>W)p.x=0;if(p.y<0)p.y=H;if(p.y>H)p.y=0;
   ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,6.28);ctx.fill();}if(!reduce)requestAnimationFrame(draw);}
 init();draw();addEventListener('resize',init);})();
"""

# --- SVG 定義(貓 + 姿勢 + 插畫),每頁內嵌 ---
DEFS = open(pathlib.Path(__file__).parent / "_defs.svg", encoding="utf-8").read()

CATPLAY = r"""<svg class="catplay" viewBox="0 0 164 182" aria-label="一隻玩逗貓棒的黑貓">
<path fill="currentColor" d="M44 176 C28 176 22 150 30 128 C36 108 56 100 74 104 L74 146 C74 164 60 176 44 176 Z"/>
<path fill="currentColor" d="M72 124 C72 94 76 76 88 64 L102 72 C94 86 88 104 86 130 C84 148 82 164 74 164 Z"/>
<path fill="currentColor" d="M94 76 C102 58 114 42 126 30 C129 27 135 29 133 35 C128 50 114 72 98 90 Z"/>
<circle fill="currentColor" cx="96" cy="64" r="19"/>
<path fill="currentColor" d="M84 52 L78 34 L94 48 Z"/><path fill="currentColor" d="M98 48 L112 32 L110 52 Z"/>
<path fill="currentColor" d="M44 168 C22 164 14 140 24 124 C18 140 34 152 52 152 Z"/>
<ellipse style="fill:var(--eye)" cx="90" cy="62" rx="2.8" ry="3.8"/>
<line x1="158" y1="8" x2="132" y2="26" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
<g class="toy"><line x1="132" y1="26" x2="116" y2="60" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
<circle cx="114" cy="64" r="6" style="fill:var(--accent)"/>
<path d="M114 64 l-11 -5 M114 64 l-13 1 M114 64 l-9 7" style="fill:none;stroke:var(--accent);stroke-width:2;stroke-linecap:round"/></g></svg>"""

# ============================================================
# 2. 內容
# ============================================================
TICKER = ["章魚有三顆心臟、藍色的血 —— 三倍的心事,本編懶得同情。",
 "玻利維亞烏尤尼鹽沼在雨季化為全世界最大的「天空之鏡」。",
 "納米比亞的「精靈圈」排列整齊,成因至今仍有爭論。",
 "金星上的一天,比它的一年還長 —— 那才叫真正的躺平。"]

STORIES = [
 ("其一","電鍋",["開關跳起來那天,飯並沒有熟。","到了第三天,電鍋忽然開口:「我煮的,是你們的耐心。」","此後全家圍坐至今,誰都不敢先動筷子。"]),
 ("其二","遲到",["他衝進公司,喘著氣道歉。","主管淡淡地說:「不急,這間公司三年前就倒了。」","整棟大樓只剩他一人——一個人,認認真真,打了三年的卡。"]),
 ("其三","金魚看海",["金魚說牠想看海,我便把牠養在海邊。","隔天牠自己游回魚缸,說海太吵。","從此,我對遠方再無幻想。"]),
 ("其四","讀貓機",["人類終於發明了讀懂貓的機器,鄭重對準了本編。","螢幕緩緩浮出一行字:「我早知道你聽不懂,所以我什麼都說了。」","機器隨即冒煙自爆。維修單上只寫四個字:情緒過載。"]),
 ("其五","集點",["店員問我要不要集點,我說好。","二十年後點數集滿,我兌換了一份「當年那個下午」。","盒子拆開,裡面是空的——原來那個下午,我早就用掉了。"]),
 ("其六","影印機",["辦公室的影印機,只在半夜運作。","早上,人們總在紙匣裡發現幾張多出來的紙,印著沒人寫過的字。","後來大家學會了一件事:不要讀。"]),
 ("其七","第十三樓",["那部電梯有一顆第十三樓的按鈕。","按下去,它會帶你回到你最想重來的那一天。","只是回程票,至今沒有人拿到過。"]),
 ("其八","傘",["他撿到一把不會濕的傘,下雨天撐著,雨會繞過他落下。","三年後他才發現,除了雨——","所有想靠近他的人,也一直繞著他落下。"]),
 ("其九","三點十七分",["牆上的時鐘壞了,永遠停在三點十七分。","奇怪的是,每天三點十七分,總有人來敲門。","找的,是一個早已搬走的人。"]),
 ("其十","魚缸",["我買了一個魚缸,沒有養魚,卻每天餵它。","半年後,水面浮起一行字:","「謝謝,但我從來不餓。」"]),
 ("其十一","名片",["他遞來一張名片,上面只印著:「以後你會需要我。」","我隨手把它丟了。","二十年後的某個深夜,我翻遍全家,只為找回那張名片。"]),
 ("其十二","迴聲",["山谷裡,他朝著遠方大喊:「你是誰?」","三天後,回音才姍姍傳回:","「你剛剛,不是問過了嗎?」"]),
 ("其十三","紅鍵",["遙控器多了一顆從沒按過的紅鍵。某天,孩子按了下去。","電視畫面裡,正播著他們明天的晚餐對話。","那頓晚餐,全家吃得很安靜。"]),
 ("其十四","無臉的鏡子",["理髮店的鏡子,照不出人。","但客人照樣來,坐下,理完。","起身,滿意地摸摸那看不見的頭髮,離開。"]),
 ("其十五","別接",["荒野中央有一座電話亭,沒有接線,卻每晚十點準時響起。","接起來的人,聽見的都是自己的聲音。","那聲音只說一句:「別接。」"]),
 ("其十六","番茄",["他種的番茄,成熟時會輕輕嘆氣。","收成那天,整片田此起彼落,像在替誰送行。","他從此,改吃泡麵。"]),
 ("其十七","最後一階",["公寓不知何時多了一階樓梯,沒有人在意。","直到某天,大家發現:無論怎麼爬,都到不了自己的家門口。","總是差,那最後一階。"]),
 ("其十八","收據不留",["小豬存錢筒滿了。敲開那天,裡面沒有硬幣,只有一張紙:","「你存進來的,我都替你花在快樂上了。」","「收據,就不留了。」"]),
 ("其十九","路燈",["那盞路燈,只在沒人看它的時候才亮。","於是整條街的人約好,一起別看它——","好讓某個要回家的人,一路上有光。"]),
 ("其二十","冰箱裡的燈",["冰箱裡的燈,真的只在關門後才熄嗎?","他決定,關在裡面查個清楚。","從此,那盞燈,再也沒有為誰亮過。"]),
 ("其二十一","不寄的信",["老郵筒,吞下了他一封封寄不出去的信。","三十年後,它把信原封不動地還給他,附上一句:","「有些話,不寄出去,才收得住。」"]),
 ("其二十二","貓門",["他替貓裝了一扇貓門。","第二天,推門回來的,是一隻不是他的貓。","第三天,是一個,不是他的自己。"]),
 ("其二十三","翻沙漏的人",["沙漏流完,他翻過來;流完,再翻。","翻著翻著,他忽然明白了——","所謂人生,不過是有人,在替你不停地翻。"]),
 ("其二十四","缺貨",["冰箱上的便條寫著:「牛奶、雞蛋、記得快樂。」","前兩樣,他買齊了。","第三樣,他找了一輩子,超市都說:缺貨。"]),
 ("其二十五","那個抽屜",["鑰匙圈上,多了一把不知開哪的鑰匙。他試過家裡每一扇門。","最後才發現,它開的,","是他一直不敢打開的那個抽屜。"]),
 ("其二十六","晴,偶爾想起",["氣象主播說:「明天,晴,偶爾想起某個人。」","隔天,果然放晴。","而全城的人,都在同一個時刻,悄悄抬起了頭。"]),
 ("其二十七","只往上的電扶梯",["那座電扶梯只往上。人們搭著它,一路上升,升進雲裡也停不下來。","地面的人說,那叫成功。","沒有人問過,上面的人,想不想下來。"]),
 ("其二十八","三秒",["手機跳出一則訊息,來自「未來的你」,只有兩個字:「快跑。」","他猶豫了三秒。","三秒,剛剛好,來不及。"]),
 ("其二十九","觀眾",["博物館新到一具標本,標籤寫著:「觀眾」。","人們圍著它看,它也圍著人們看。","沒人說得清,到底誰,才是被展示的那一個。"]),
 ("其三十","那件雨衣",["媽媽織的雨衣,穿上就不會被雨淋。他長大後嫌它醜,收進了櫃底。","那年之後,他淋過的每一場雨——","都想起了它。"]),
 ("其三十一","悲傷開關",["牆上有個開關,標著「悲傷」。他好奇,按了下去。","燈沒滅,天沒暗。","只是從此,他再也想不起來,自己原本在難過什麼。"]),
 ("其三十二","輪到他時",["他排了一輩子的隊。輪到他時,窗口貼出:「今日已滿。」","他這才回頭。","身後,也排了一輩子的人。"]),
 ("其三十三","慢一點",["生日蠟燭前,他許願:「時間,慢一點。」願望成真了。","他慢慢地吹,慢慢地老。","慢慢地,看著所有人,快步離開。"]),
 ("其三十四","空的目的地",["導航說:「你已抵達目的地。」可他停在一片空地中央,什麼也沒有。","他坐了很久,才終於懂了——","有些目的地,本來就是空的。"]),
 ("其三十五","不敢點開的續集",["他等了二十年的動畫,終於出了續集。","他卻遲遲不敢點開。","因為點開之後,那二十年的等待,就再也沒有地方可去了。"]),
 ("其三十六","充電",["手機說它累了,想休息一晚。","我拔掉線,由它安靜地黑了屏。","隔天再開,通訊錄裡所有人的號碼,都換成了同一個——我自己的。"]),
 ("其三十七","路燈",["巷口那盞路燈,只在我經過時才亮。","我以為它壞了,直到某夜它輕聲說:「我只是想確定,你有平安到家。」","從此我天天繞遠路,只為多陪它站一會兒。"]),
 ("其三十八","排隊",["那家店永遠在排隊,沒人知道它賣什麼。","我排了整整十年,終於輪到我。","店員微笑問:「歡迎光臨——請問您今天,想排的是哪一種隊?」"]),
 ("其三十九","舊地址",["搬家那天,我把舊地址留給了新住戶。","多年後回去,那信箱塞滿了寫給我的信。","每一封的寄件人都是我自己,日期,全在未來。"]),
 ("其四十","時差",["她住在地球另一端,我們的白天與黑夜,永遠錯開。","為了同時醒著,我們各自把時鐘,調成了對方的時間。","如今終於同步,我們卻再也認不得,窗外究竟是幾點。"]),
 ("其四十一","盆栽",["辦公室那盆植物,沒人記得是誰帶來的。","它從不必澆水,卻在每個有人加班的深夜,悄悄長高一寸。","後來公司搬空,只留下它——和一整面,穿過天花板的葉子。"]),
 ("其四十二","離線",["那個群組,已經三年沒人說過話了。","某個深夜,它突然跳出一句:「你們……都還在嗎?」","沒有人回。可那一句,每一個人,都看見了。"]),
 ("其四十三","鑰匙",["我留著一把,不知道開哪扇門的鑰匙。","搬過六次家、丟過無數東西,卻始終沒捨得丟它。","直到某天才懂——它開的,是我一直不肯回去的那扇。"]),
 ("其四十四","代收",["樓下超商,替我代收了一個包裹。","上面沒有寄件人,只寫著:「給十年後的你。」","我這才想起,十年前的我,也曾在同一個櫃台前,笑著寄出過什麼。"]),
 ("其四十五","靜音",["為了專心,我把整個世界調成了靜音。","起初很清淨,後來我發現,連自己心跳的聲音,也一起被關掉了。","如今我到處找那顆開關,只想再,好好地吵一次。"]),
 ("其四十六","備份",["他把每一段回憶都仔細備份,深怕忘記。","硬碟愈存愈滿,他卻愈來愈想不起,任何一個當下。","原來記得太用力,也是一種——好好地,錯過。"]),
 ("其四十七","常客",["那家咖啡館的老闆說,我是他最老的常客。","可我分明,是第一次踏進來。","他笑著端上一杯,說:「你每一世,都是這麼說的。」"]),
 ("其四十八","未接來電",["手機顯示一通未接來電,號碼,是我自己的。","我回撥過去,響了很久,終於有人接起。","那頭的聲音比我老了三十歲,只說:「別擔心,你會撐過去的。」"]),
 ("其四十九","共乘",["深夜的計程車上,司機問我要去哪。","我報了地址,他卻往反方向開。","「這個時間,」他輕聲說,「你真正想回的地方,從來不是那裡。」"]),
 ("其五十","延長線",["為了讓插座夠用,我接了一條又一條延長線。","電器愈接愈多、線愈拉愈長,最後繞了整個房間一圈。","直到某天才發現——最初那個插座,其實從來沒插上牆。"]),
 ("其五十一","發票",["我從不對發票,總把它們塞進抽屜。","十年後抽屜滿了,我一張張攤開對獎。","沒有一張中獎,卻每一張,都印著我早已忘記的那天、去過的地方。"]),
 ("其五十二","隔壁",["隔壁搬來一位鄰居,我們從沒見過面。","可每當我難過,牆的另一頭,總會輕輕敲三下。","搬走那天我才知道:那間房,已經空了很多年。"]),
 ("其五十三","慢遞",["有種郵局專寄「慢遞」——你寫的信,會在很多年後才送到。","我寄了一封給未來的自己。","多年後信到了,信封裡卻是空白的——原來想說的,我早已,活成了。"]),
 ("其五十四","共筆",["我們約好合寫一本日記,一人一天。","輪到我時,昨天那頁,總已寫滿了我還沒經歷的事。","而且每一件,後來都準準地,發生了。"]),
 ("其五十五","回收",["巷口的回收阿婆,收紙、收鐵,也收「後悔」。","我把積了半生的後悔倒給她,輕鬆了好一陣子。","直到某天路過,才看見那些後悔,被她仔細地,一件件還給了更需要的人。"]),
 ("其五十六","導盲",["那隻導盲犬退休了,主人卻仍每天牽著牠散步。","有人問:牠都看不太清了,還帶得了路嗎?","主人笑說:「這些年,一直是牠,在我看不見的地方,替我認路。」"]),
 ("其五十七","時鐘",["家裡那口老鐘,總是慢五分鐘。","我一直懶得調,久了,全家都跟著它過日子。","後來才發現:是它,替我們把每一場離別,都偷偷延後了五分鐘。"]),
 ("其五十八","已送達",["外送員按了門鈴:「您的餐,到了。」","可我今天,什麼也沒點。","他看了看單子,輕聲說:「是三年前的你,點給今天的你的。備註寫著:記得吃飯。」"]),
 ("其五十九","路過",["每天上班,我都會經過同一棵樹。","十年來,我從沒抬頭看它一眼。","它被砍掉那天,我卻在原地站了很久——原來有些陪伴,要等它消失,你才認得出來。"]),
]

# 每篇:slug, cat, title, deck, keywords, meta[(label,val)], sym(插畫id),
#       img{file,alt,by,lic}, body(HTML), mao, sources
ARTICLES = [
 dict(slug="whittier", cat="地方誌 · Alaska", title="一棟樓,就是一整座城鎮",
  deck="要進入這座小鎮,你得先穿過一條四公里長、火車與汽車共用的黑暗隧道。鑽出來,鎮上幾乎所有人,都住在同一棟樓裡。",
  keywords="惠蒂爾,Whittier,阿拉斯加,畢吉奇大廈,一棟樓的城鎮,安東安德森隧道",
  meta=[("座標","60.77°N 148.68°W"),("人口","約 300 人"),("樓層","14 層 · 196 戶")],
  sym="il-whittier",
  img=dict(file="Begich Towers, 2019.jpg", alt="阿拉斯加惠蒂爾的畢吉奇大廈,一棟孤立於雪山與峽灣間的高樓",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>抵達之前:那條吞掉汽車的隧道</h2>
<p>惠蒂爾(Whittier)坐落在阿拉斯加一處被群山與峽灣環抱的角落。它對外的唯一陸路,是一條長約四公里、原本只走火車、後來改成火車與汽車共用的單線隧道。因為只有一線道,車流每十五分鐘才輪一次方向;到了夜裡,隧道會直接關閉,惠蒂爾便與世界斷了聯繫,直到隔天早上。</p>
<p>「你會忍不住想:天啊,這是唯一的出路,萬一出事了怎麼辦?」一位名叫 Lee Shuford 的居民這樣描述剛搬來時的心情。後來他習慣了。在這裡,習慣是必修課——冬天的積雪,平均可以堆到六公尺高。</p>
<h2>一棟樓,收得下一座城</h2>
<p>穿過隧道,你會看見那棟樓:十四層、一百九十六戶,住著這座小鎮八到九成的居民。但它遠不只是公寓——一樓與地下室藏著一整座城鎮該有的東西:一間叫「Kozy Korner」的雜貨店、郵局、洗衣房、診所、警察局、市政府、一間教堂,還有一間民宿。最頂兩層,甚至規劃成旅館。</p>
<p>孩子上學不必踏進暴風雪:一條供暖的地下通道,把大樓和對街的學校直接連起來。全校約五十名學生、從三歲到十八歲都在同一棟校舍;老師常常順手替孩子做早餐。而大人通勤的距離,就是搭一趟電梯。</p>
<h2>當全鎮都是你的鄰居</h2>
<p>把幾百人塞進同一棟樓,會長出很特別的人際關係。老師 Lindsey Erk 說,在這麼小的校園裡「每一個孩子都被看見」;年輕人 Jenessa Dickason 則苦笑,這裡幾乎沒人談戀愛,「因為我們全是從小一起長大的」。你沒辦法在這棟樓裡保有祕密——搭一次電梯,全鎮都知道你今天心情如何。</p>
<h2>冷戰留給小鎮的巨獸</h2>
<p>這一切的源頭,是一場戰爭。二戰期間軍方看中惠蒂爾終年不凍的深水港,把它闢為補給要衝;這棟樓的前身,是 1943 年蓋起的軍用建築。1974 年,它被更名為「畢吉奇大廈」,紀念兩年前死於空難的國會議員 Nick Begich。軍隊撤走後居民留了下來,而鎮上幾乎所有可住的土地至今仍歸阿拉斯加鐵路公司所有——你無法在這裡自己蓋房子。於是「大家住在同一棟樓」這件事,就一年一年地延續了下來。</p>
<blockquote>「這裡沒什麼好玩的。讓人留下來的,是人。」</blockquote>""",
  mao="一棟樓收得下郵局、學校、教堂和一整座城的人情世故,出門最遠不過搭一趟電梯——各位,這正是本編追求了半輩子的居住哲學:世界很大,但沒必要親自去。",
  sources="CBS News · Snopes · All That's Interesting · ETtoday"),

 dict(slug="immortal-jellyfish", cat="科學怪奇 · Biology", title="會「倒帶」回嬰兒的水母",
  deck="一隻比小指甲還小的透明水母,握著地球上最接近「永生」的把戲——當死亡逼近,牠選擇整個重來,一次,又一次。",
  keywords="燈塔水母,Turritopsis dohrnii,不死水母,細胞轉分化,久保田信,生物永生",
  meta=[("物種","Turritopsis dohrnii"),("直徑","約 4.5 mm"),("棲地","全球溫暖海域")],
  sym="il-jelly",
  img=dict(file="Turritopsis dohrnii.jpg", alt="燈塔水母:幾近透明的傘狀身體,中央一團鮮紅的胃",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>比小指甲還小的不死傳說</h2>
<p>在世界各地溫暖的海域裡,漂著一種直徑僅約 4.5 毫米、比你小指甲還小的透明水母:燈塔水母。牠的傘狀身體幾乎全透明,只有正中央那一團鮮紅——那是牠的胃。就是這麼一隻不起眼的小東西,握有整個動物界獨一無二的本事:逆轉自己的生命。</p>
<h2>當死亡逼近,牠決定重來</h2>
<p>一般水母走完成體階段便會邁向死亡。但燈塔水母在受傷、飢餓或環境惡化時,不會坐以待斃:牠會整個塌縮、沉到海底,在接下來幾天裡,把已經成熟的細胞一個個「改寫」成別種細胞,重新組裝成一株水螅體——也就是牠早該長大脫離的幼體型態。然後,再一次長成新的成體。</p>
<p>這個讓成熟細胞改頭換面的過程,叫「細胞轉分化」(transdifferentiation)。理論上,只要不被吃掉、不生病,這個循環可以無限重複——這正是牠被冠上「生物學上不死」之名的原因。</p>
<h2>那個為牠寫卡拉OK的男人</h2>
<p>在日本京都大學的瀨戶臨海實驗所,生物學家久保田信(Shin Kubota)從 1990 年代起就養著一缸燈塔水母,親眼看著同一批水母一次次死去、又一次次「復活」。在某段長達兩年的觀察裡,他缸中的水母自然回春了多達十次,有時前後只隔一個月。看得太著迷,他甚至為這種「打死也不肯好好死去」的小生物,寫起了卡拉OK歌。</p>
<h2>但牠真的長生不老嗎?</h2>
<p>這裡得小心一個美麗的誤會。所謂「不死」,是一種發生在細胞層次的特性,並不是說海裡真有一隻活了幾千年的水母。在真實海洋裡,牠隨時可能被魚吞下、被寄生蟲感染、或死於疾病。牠能繞過的,只是「老死」這一條路而已。</p>
<blockquote>「牠打敗的從來不是死亡,而是衰老。海裡那條餓魚,依然說了算。」</blockquote>""",
  mao="為了不死,得先把自己整個打掉、重練回嬰兒?聽著就累。本編有個更省力的版本,叫午睡:每天死去八小時,隔天準時復活,還不必變回幼貓。",
  sources="Natural History Museum · Smithsonian · Kyoto University(久保田信)· AMNH"),

 dict(slug="tardigrade-in-space", cat="科學怪奇 · Biology", title="連太空都殺不死的牠",
  deck="高溫、酷寒、輻射、真空——把地球上最極端的環境全加起來,也奈何不了這隻不到一毫米的小生物。牠的祕訣,是「先把自己關機」。",
  keywords="水熊蟲,緩步動物,tardigrade,隱生,FOTON-M3,太空實驗,Dsup蛋白",
  meta=[("俗名","水熊蟲／苔蘚小豬"),("體長","< 1 mm · 八足"),("紀錄","首種撐過裸露太空的動物")],
  sym="il-tardi",
  img=dict(file="SEM image of Milnesium tardigradum in active state - journal.pone.0045682.g001-2.png",
           alt="電子顯微鏡下的水熊蟲:圓胖身軀、八條短腿", by="Schokraie E. et al / Wikimedia Commons", lic="CC BY 2.5"),
  body="""<h2>一隻打不死的「苔蘚小豬」</h2>
<p>水熊蟲(緩步動物)身長不到一毫米,有八條短腿,圓滾滾地住在苔蘚、水溝、深海到高山的各個角落——牠憨態可掬的模樣,替牠掙來一個綽號:「苔蘚小豬」。但別被外表騙了,牠是地球上已知最耐命的動物,沒有之一。</p>
<h2>祕訣:把自己曬乾、關機</h2>
<p>當環境乾涸,水熊蟲不會硬撐,而是啟動一種叫「隱生」的絕招:牠把體內高達 <b>99%</b> 的水分排掉,縮成一顆桶狀的乾燥體,把新陳代謝壓到正常值的 <b>0.01% 以下</b>——幾乎等於暫時「關機」。在這狀態下,牠能撐過攝氏一百五十度高溫、接近絕對零度的酷寒,以及數百倍於人類致死劑量的輻射。</p>
<h2>牠上過太空,而且活著回來</h2>
<p>2007 年,歐洲太空總署在 FOTON-M3 任務中,把約 <b>3,000 隻</b>乾燥的水熊蟲送上距地約 260 公里的軌道,打開容器,讓牠們直接曝露在太空的硬真空與輻射中整整 <b>十天</b>。回到地面復水後,約 <b>68%</b> 醒了過來——會動、會吃、會蛻皮,還順利產下正常後代。牠們,成了史上第一種在裸露太空中存活的動物。</p>
<h2>牠到底是怎麼辦到的?</h2>
<p>近年研究逐漸揭曉牠的分子級護身符:名為 <b>Dsup</b> 的蛋白質像盾牌一樣包住 DNA、擋下輻射;CAHS 蛋白在乾燥時形成玻璃般的凝膠,把體內結構穩穩「凝固」保護;某些種類還靠海藻糖與色素中和自由基。等水分回來,再一一解封。</p>
<blockquote>「牠不是打贏了極端,而是在極端面前,先把自己關機。」</blockquote>""",
  mao="遇到打不贏的,就把自己曬乾、關機、對外宣稱不在家——各位,這哪是求生絕技,這分明是本編每個週一早晨的標準作業流程。",
  sources="European Space Agency · Current Biology · Nature · American Scientist"),

 dict(slug="voynich-manuscript", cat="歷史謎團 · Mystery", title="一本沒人讀得懂的書",
  deck="六百年來,最聰明的頭腦一個接一個栽在這本書上——包括二戰破解過敵國密碼的傳奇專家。它至今守口如瓶。",
  keywords="伏尼契手稿,Voynich manuscript,未破譯,MS 408,碳定年,William Friedman",
  meta=[("羊皮紙年代","1404–1438"),("現藏","耶魯 Beinecke MS 408"),("狀態","從未破譯")],
  sym="il-voynich",
  img=dict(file="Voynich Manuscript (32).jpg", alt="伏尼契手稿內頁:繞著怪異植物插圖流動的無人能讀文字",
           by="Beinecke Library / Wikimedia Commons", lic="公有領域"),
  body="""<h2>一本流落人間的怪書</h2>
<p>1912 年,書商威爾弗里德・伏尼契在義大利購得一本奇書,它從此以他為名。全書約 240 頁羊皮紙,寫滿一種被稱為「伏尼契文」的文字——它有字母、有斷詞、看起來煞有其事,卻對應不到地球上任何一種已知語言。文字繞著滿滿的插圖流動,像一本被施了咒的百科全書。</p>
<h2>裡面到底畫了什麼?</h2>
<p>學者依內容把它分成幾部分:「植物」畫著現實中不存在的花草;「天文」是對不上任何已知系統的星盤與同心圓;最詭異的「生物沐浴圖」則是一群裸體小人泡在綠色管道與水池裡,被戲稱「青春之泉」;最後還有像藥方的段落。每一頁都在暗示某種知識,卻沒有一頁肯說清楚。</p>
<h2>連頂尖密碼專家都投降</h2>
<p>破解它的名單星光熠熠。其中最有名的,是二戰時領軍破解日本「紫密」的美國密碼大師威廉・傅利曼(William Friedman)——他與同為密碼專家的妻子窮盡多年心力,最後也只能承認失敗。有人說那是失傳的語言,有人斷言是騙局,也有人猜是私人速記。至今,沒有任何一種解讀被學界普遍接受。</p>
<h2>碳定年,沒有終結謎團</h2>
<p>2011 年,亞利桑那大學團隊為羊皮紙做了碳定年,結果落在 <b>1404 至 1438 年</b>之間,排除了近代偽造的可能。但這裡藏著陷阱:碳定年測的是「羊皮紙的年紀」,不是「上頭字跡的年紀」——用陳年空白羊皮紙寫新東西,歷史上並不罕見。於是連「它何時被寫下」都仍是懸案。更令人不安的是:那些文字呈現出類似真實語言的統計規律,卻死活對不上任何語系。</p>
<blockquote>「碳定年能告訴我們羊皮紙多老,卻無法告訴我們,它想說什麼。」</blockquote>""",
  mao="一本攤開著、沒人讀得懂、還畫滿不存在的植物的書——本編太清楚它的真正用途了。那叫「霸佔你桌面正中央、逼你繞道」的終極神器。每一隻貓的鍵盤上,都供著一本。",
  sources="Yale Beinecke Library · University of Arizona · Wikipedia · Smithsonian"),

 dict(slug="krakatoa-1883", cat="自然異象 · History", title="有紀錄以來最大的一聲巨響",
  deck="上午十點零二分,一座島把自己炸碎。那一聲,近五千公里外的人像聽見砲擊般清晰;它的氣壓波,繞了地球整整四圈。",
  keywords="喀拉喀托,Krakatoa,1883,最大聲音,火山爆發,氣壓波,巽他海峽",
  meta=[("時間","1883.8.27 上午 10:02"),("地點","印尼 Sunda 海峽"),("罹難","逾 36,000 人")],
  sym="il-krakatoa",
  img=dict(file="Krakatoa eruption lithograph.jpg", alt="1888 年描繪 1883 年喀拉喀托火山噴發的石版畫",
           by="Parker & Coward / Wikimedia Commons", lic="公有領域(1888)"),
  body="""<h2>一座島,把自己炸碎</h2>
<p>1883 年 8 月 27 日上午十點零二分,位於印尼巽他海峽的喀拉喀托火山發生了人類史上最劇烈的噴發之一,整座火山島幾乎在瞬間被自己撕裂、崩塌入海。它發出的那一聲,至今仍被認為是有紀錄以來最大的聲音。</p>
<h2>四千八百公里外,像聽見砲擊</h2>
<p>這聲巨響傳得有多遠?在近 <b>4,800 公里</b>外、印度洋中央的羅德里格斯島,居民清楚聽見一陣「像遠方砲火」的隆隆聲;在 <b>3,100 多公里</b>外的澳洲伯斯,人們同樣以為是砲兵演習。地球上再沒有第二個聲音,能在傳了數千公里後仍被人耳直接聽見。至於聲音本身:震源附近估計超過 <b>300 分貝</b>,約 65 公里外船上的水手耳膜當場被震破;而數千公里外的氣壓計,把這道壓力波換算成大約 <b>172 分貝</b>。</p>
<h2>繞地球四圈的餘波</h2>
<p>爆炸產生的氣壓波,被全球各地的氣壓計一一捕捉,並繞行地球足足 <b>四圈</b>才平息。同時掀起的海嘯最高達數十公尺,遠在非洲南端的船隻都被搖晃;這場災難最終奪走超過 <b>36,000 條</b>人命。噴入平流層的火山灰,更讓其後數年全球日落染上異常的血紅——有人認為,孟克名畫《吶喊》裡那片扭曲的紅天,正是它遠渡重洋的餘威。</p>
<blockquote>「那一聲,是地球對著自己,吼出的最大的一句話。」</blockquote>""",
  mao="三百分貝、繞地球四圈——了不起。但本編認真調查過:能穩定吵醒一隻熟睡黑貓的音量,至今地表只有一種達得到,那就是罐頭封膜被撕開的瞬間。",
  sources="Britannica · National Geographic · Nautilus · All That's Interesting"),

 dict(slug="blood-falls", cat="自然異象 · Antarctica", title="南極流出的「血」",
  deck="一道鮮血般的紅,常年從南極潔白的冰壁上滲流而下。那不是誰受了傷——那是一段被冰封了一百五十萬年的海,終於見了光。",
  keywords="血瀑布,Blood Falls,泰勒冰川,南極,鐵氧化,極端微生物,Griffith Taylor",
  meta=[("地點","泰勒冰川"),("發現","1911 年"),("封存","逾 150 萬年")],
  sym="il-blood",
  img=dict(file="Blood Falls by Peter Rejcek.jpg", alt="南極泰勒冰川末端一道刺目的血紅瀑布",
           by="Peter Rejcek, NSF / Wikimedia Commons", lic="公有領域"),
  body="""<h2>1911 年,一個以為看見血的地質學家</h2>
<p>1911 年,英國「新大陸號(Terra Nova)」南極探險期間,澳洲裔地質學家格里菲斯・泰勒(Griffith Taylor)在一道冰川末端撞見駭人的一幕:雪白的冰上竟滲出血一般的紅水。他起初以為是紅藻染的,便替它取名「血瀑布」。後來,那道冰川以他為名,成了泰勒冰川。</p>
<h2>紅色的真相,其實是生鏽</h2>
<p>那抹紅,和生命無關,和「鐵」有關。冰層深處封存著一池比海水更鹹、富含鐵質、且完全無氧的古老鹹水;當它循裂隙流出、接觸空氣的瞬間,水中的鐵便迅速氧化生鏽,把整道水染成血紅。這池水已被囚禁至少 <b>150 萬年</b>——遠古時冰川前進,把一小塊海水封死在底下。極高的鹽度讓它在冰點以下仍不結凍;少數結凍處會放出熱量,反而幫忙把通道維持暢通。</p>
<h2>冰下四百公尺,一個沒見過陽光的世界</h2>
<p>更驚人的是,這池與世隔絕的鹹水裡住著活的東西。科學家在冰下約 400 公尺、無光又無氧的環境中,發現仍在生長的微生物。牠們靠鐵與硫的化學能維生,呼吸方式也很另類:不像一般厭氧菌把硫酸鹽還原成硫化物,而是拿三價鐵當「電子受體」。這使血瀑布成為研究極端生命、乃至冰封星球(如木衛二「歐羅巴」)可能生命樣貌的活教材。</p>
<blockquote>「那不是誰在流血,是一段被冰封了一百五十萬年的海,終於見了光。」</blockquote>""",
  mao="封存一百五十萬年、無光、無氧、還住著東西——講白了,這不就是本編夢寐以求的貓窩規格?安靜、全暗、沒人打擾,還能永久保鮮。唯一的缺點是血色;本編偏好純黑。",
  sources="Johns Hopkins University · ScienceAlert · Wikipedia · Applied and Environmental Microbiology"),

 dict(slug="fairy-circles", cat="未解之謎 · Namibia", title="草原上的完美圓圈",
  deck="數以百萬計、間距整齊的圓圈鋪滿草原,整齊得不像出自大自然之手。爭論了幾十年,它們究竟是誰畫的?",
  keywords="精靈圈,fairy circles,納米比亞,納米布沙漠,圖靈圖案,白蟻,Stephan Getzin",
  meta=[("地點","納米布沙漠"),("直徑","2–10 公尺"),("狀態","成因仍爭論")],
  sym="il-fairy",
  img=dict(file="Aerial view of Fairy circles, Namibia (2017).jpg", alt="納米比亞紅褐草原上鋪滿間距整齊的圓形裸地",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>草原上百萬個完美的圓</h2>
<p>在納米布沙漠的乾草原上,散布著數以百萬計、幾乎完美的圓形裸地:每個圈直徑約 <b>2 到 10 公尺</b>,彼此間隔可達十公尺,圈內寸草不生,邊緣卻圍著一圈格外茂盛的草。從空中俯瞰,像大地長出了無數規律的斑點。</p>
<h2>兩派人,吵了幾十年</h2>
<p>成因之爭分成壁壘分明的兩派。一派主張是地底的「沙白蟻」啃食草根、清出裸地;另一派則認為,是植物在極度缺水下為公平分配水分而「自我組織」,長成規律間距——也就是數學家圖靈預言過的「圖靈圖案」(Turing pattern)。</p>
<h2>一個追了二十年的生態學家</h2>
<p>德國哥廷根大學的生態學家史蒂芬・蓋欽(Stephan Getzin)從 2000 年起緊咬這個謎,發表的相關論文比任何人都多。他的關鍵證據很有說服力:一場雨後第 20 天,圈內的草已全數枯死,圈外的草卻依然青綠;而比對根系,圈內草根一樣長、甚至更長——說明草其實在拼命向下扎根找水,而不是被白蟻啃斷。圈內裸地像海綿,把珍貴雨水導向四周,養肥了外圈的草。</p>
<h2>也許,答案不只一個</h2>
<p>但白蟻說並未出局——近年仍有研究者力挺白蟻才是主因。也有人認為兩者可能同時作用。更耐人尋味的是,類似圓圈後來也在澳洲被發現。大自然,似乎不打算給人類一個乾淨俐落的標準答案。</p>
<blockquote>「幾十年過去了,草原只肯給線索,不肯給答案。」</blockquote>""",
  mao="白蟻?圖靈圖案?各位都想複雜了。完美的圓、精準的間距、圈內寸草不生——本編以二十年臥榻經驗專業判斷:那分明是有貓睡過,入睡前原地轉了三圈壓平的標準弧度。結案,散會。",
  sources="University of Göttingen(Stephan Getzin)· ScienceAlert · CNN · Journal of Ecology"),

 dict(slug="salar-de-uyuni", cat="自然異象 · Bolivia", title="會把天空倒過來的鹽沼",
  deck="雨季一到,全世界最大的鹽沼變成一面完美的鏡子,天與地的界線就此消失,人像走在雲上。",
  keywords="烏尤尼鹽沼,天空之鏡,Salar de Uyuni,玻利維亞,鏡面,鋰礦",
  meta=[("地點","玻利維亞"),("面積","逾 10,000 km²"),("海拔","約 3,656 m")],
  sym="il-blood",
  img=dict(file="Reflection on the Salar de Uyuni, bolivia.jpg", alt="雨季的烏尤尼鹽沼倒映天空,如一面巨大的鏡子",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>一片望不到邊的白</h2>
<p>烏尤尼鹽沼位在玻利維亞海拔約 3,656 公尺的高原,面積超過一萬平方公里,是全世界最大的鹽沼。它是數萬年前一座巨大史前湖泊乾涸後留下的遺產,地表覆著厚達數公尺的鹽層,白得像雪,而且平坦得驚人——整片鹽沼的高低落差不超過一公尺。</p>
<h2>雨季,大地變成鏡子</h2>
<p>每年雨季,一層薄薄的水覆上鹽沼,把整片天空原封不動地倒映下來。天與地的界線消失,雲在腳下流動,人彷彿懸浮在半空。這面「天空之鏡」也因此成了全世界攝影師與旅人朝聖的畫面。</p>
<h2>不只是風景:鋰的寶庫</h2>
<p>鹽沼底下,埋著全世界數一數二豐富的鋰礦——電動車電池的關鍵原料;鹽沼邊緣的鹹水湖,則是紅鶴的繁殖地。它甚至平坦到被科學家拿來校正衛星的測高儀器。</p>
<h2>一座用鹽蓋的旅館</h2>
<p>在這裡,連旅館都是用鹽磚砌成的。在如此極端而純粹的地景裡,人類學會了與鹽共處。</p>
<blockquote>「當天空落到腳下,你會分不清自己是在走路,還是在飛。」</blockquote>""",
  mao="一整面完美的鏡子、平到高低差不到一公尺——本編懂那種執念。那正是本編巡視地盤時,對每一個打算躺上去的平面,最起碼的要求。",
  sources="NASA Earth Observatory · Britannica · UNESCO"),

 dict(slug="octopus-three-hearts", cat="科學怪奇 · Biology", title="三顆心臟、藍色血液的外星人",
  deck="三顆心臟、藍色的血、八條會各自思考的手臂,還能瞬間變色隱形——章魚,幾乎是地球上最接近外星生命的動物。",
  keywords="章魚,三顆心臟,藍色血液,頭足綱,變色,octopus,血藍蛋白",
  meta=[("物種","頭足綱 · 章魚"),("心臟","3 顆"),("血色","藍色")],
  sym="il-jelly",
  img=dict(file="Octopus vulgaris 03.jpg", alt="一隻普通章魚,八腕與圓潤的外套膜",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>三顆心臟,藍色的血</h2>
<p>章魚有三顆心臟:兩顆負責把血送到鰓、一顆送往全身。牠的血液不靠鐵、而靠含銅的「血藍蛋白」運氧,所以呈藍色——這在低溫缺氧的深海裡效率更高。有趣的是,當牠游泳時,那顆主心臟會暫停跳動,所以章魚其實不太愛游泳,寧可用爬的。</p>
<h2>九個腦,八條會思考的手臂</h2>
<p>章魚約有五億個神經元,但其中約六成不在腦裡,而分布在八條腕足上。也就是說,每條手臂都能在某種程度上「自己思考」、自己嚐味道、自己做決定——可說是「一個中央大腦,加上八個分腦」。</p>
<h2>頂尖的變裝大師</h2>
<p>章魚皮膚裡藏著數以百萬計的色素細胞,能在不到一秒內改變顏色與質地,融入珊瑚、岩石甚至海藻。諷刺的是,牠們很可能是色盲——科學家至今仍在研究,牠們究竟怎麼「看」到自己要模仿的顏色。</p>
<h2>聰明,但短命</h2>
<p>章魚會開罐、會用椰子殼當盾牌、會惡作劇,聰明得驚人。但牠們大多只活一到兩年;母章魚產卵後守著卵、不吃不喝,直到死去。</p>
<blockquote>「牠有三顆心、藍色的血、八條會思考的手——若這不算外星人,什麼才算?」</blockquote>""",
  mao="八條手臂各自思考、各自行動、彼此互不通報——本編太熟悉這種生物了。那就是本編半夜在你家四處推倒東西時,四隻腳與那條尾巴的協作模式。",
  sources="Smithsonian · Natural History Museum · Scientific American"),

 dict(slug="door-to-hell-darvaza", cat="地方誌 · Turkmenistan", title="燒了半個世紀的「地獄之門」",
  deck="土庫曼沙漠中央,一個直徑七十公尺的坑洞已經熊熊燃燒了半個世紀——而它,可能只是一場失手的意外。",
  keywords="地獄之門,達瓦札,Darvaza,土庫曼,天然氣坑,永不熄滅的火",
  meta=[("地點","土庫曼 達瓦札"),("直徑","約 70 m"),("燃燒","逾 50 年")],
  sym="il-krakatoa",
  img=dict(file="Darvasa gas crater panorama.jpg", alt="土庫曼沙漠中終年燃燒的達瓦札天然氣坑「地獄之門」",
           by="Tormod Sandtorv / Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>沙漠正中央的一團火</h2>
<p>在土庫曼卡拉庫姆沙漠的達瓦札村附近,有一個直徑約 70 公尺、深約 20 公尺的大坑,坑底火焰終年不熄,夜裡遠遠就能看見一團橘紅的光——當地人叫它「地獄之門」。</p>
<h2>一場失手的意外?</h2>
<p>最廣為流傳的說法是:1971 年,蘇聯地質隊在此鑽探天然氣,地面突然塌陷成坑,大量甲烷外洩。為了不讓有毒氣體擴散,他們決定點火燒掉,原以為幾週就會燒完——沒想到一燒,就是半個世紀,至今未熄。(附帶一提:確切年份與細節,學界其實仍有爭議。)</p>
<h2>它會熄嗎?</h2>
<p>土庫曼政府近年多次表示希望把它撲滅:一來白白燒掉珍貴的天然氣,二來影響環境與居民健康。但要如何安全地關掉一扇燒了五十年的「地獄之門」,至今仍是難題。</p>
<blockquote>「他們想燒掉一個坑,結果點亮了一座燒了半世紀的地獄。」</blockquote>""",
  mao="一個溫暖、明亮、永不熄滅、還沒別的動物敢靠近的角落——各位,若不是那點硫磺味,本編早就把它列進理想過冬地點的口袋名單了。",
  sources="National Geographic · BBC · Smithsonian"),

 dict(slug="nazca-lines", cat="歷史謎團 · Peru", title="只有從天上才看得懂的巨畫",
  deck="只有從幾百公尺高空,才看得出它們是蜂鳥、猴子與蜘蛛。兩千年前的人,是為了誰畫下這些看不見全貌的巨圖?",
  keywords="納斯卡線,Nazca Lines,秘魯,地畫,蜂鳥,史前謎團",
  meta=[("地點","秘魯 納斯卡"),("年代","約 BC500–AD500"),("規模","逾 300 個圖形")],
  sym="il-fairy",
  img=dict(file="Nazca Lines Hummingbird (cropped).jpg", alt="秘魯納斯卡高原上巨大的蜂鳥地畫",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>只有從天上才看得懂的畫</h2>
<p>在秘魯南部乾燥的納斯卡高原上,刻著數百個巨大的圖案:蜂鳥、猴子、蜘蛛、鯨魚,以及大量筆直的長線與幾何圖形。它們大到——站在地面上,你只會覺得是一道道淺溝;唯有升上幾百公尺高空,完整的圖形才會浮現。</p>
<h2>是怎麼畫出來的?</h2>
<p>做法其實不難。納斯卡人只是把地表深紅的礫石移開,露出底下顏色較淺的地面,線條便顯現出來。這片高原極度乾燥、幾乎無風,才讓這些淺淺的線,保存了兩千年。</p>
<h2>究竟為了誰而畫?</h2>
<p>真正的謎,是「為什麼」。有人認為是獻給天上神祇的祭祀圖案,有人認為與地下水源、天文曆法有關,也有人主張那是宗教遊行的路線。畫給看不見全貌的地面人,顯然不合理——那麼,他們心中真正的觀眾,究竟是誰?</p>
<h2>脆弱的世界遺產</h2>
<p>這些線條至今仍受氣候變遷與人為破壞的威脅。它們熬過了兩千年的乾旱,卻未必熬得過現代。</p>
<blockquote>「他們把畫,獻給了一個當時沒有人能抵達的視角。」</blockquote>""",
  mao="費盡力氣畫一幅只有從高處才看得懂的巨作——本編完全理解。這正是本編為何總要爬上最高的櫃頂:有些傑作,注定只獻給居高臨下的那一雙眼睛。",
  sources="UNESCO · National Geographic · Smithsonian"),

 dict(slug="sailing-stones", cat="未解之謎 · USA", title="會自己走路的石頭",
  deck="在美國死亡谷一片乾涸的湖床上,幾百公斤的石頭會自己滑行,在地上拖出長長的軌跡——卻從沒有人親眼看過它們移動。",
  keywords="會走路的石頭,帆石,sailing stones,Racetrack Playa,死亡谷,冰推",
  meta=[("地點","死亡谷 Racetrack Playa"),("重量","可達數百公斤"),("謎團","2014 年解開")],
  sym="il-fairy",
  img=dict(file="Sailing Stones (3992378748).jpg", alt="死亡谷乾涸湖床上一顆石頭與它身後長長的滑行軌跡",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>自己走路的石頭</h2>
<p>在美國加州死亡谷一處叫「跑道乾湖」(Racetrack Playa)的乾涸湖床上,散落著一顆顆石頭,有的重達數百公斤。詭異的是,每顆石頭後面都拖著一道長長的軌跡,彷彿它們曾在地上滑行了幾十、甚至上百公尺——卻從來沒有人親眼看過它們移動。</p>
<h2>困惑了近一個世紀</h2>
<p>這個現象困擾了科學家將近百年。沒有動物、沒有人為介入,石頭卻確實在移動。有人猜是強風、有人猜是地磁,眾說紛紜,誰也無法證實。</p>
<h2>2014 年,謎底揭曉</h2>
<p>直到 2014 年,科學家用 GPS 與縮時攝影,終於當場「抓到」了兇手:冬夜裡湖床積起一層薄水並結成薄冰,白天陽光把冰融成大片浮冰;當微風吹來,這些薄冰推著底下的石頭,以每分鐘數公尺的速度極其緩慢地滑行——慢到肉眼幾乎察覺不到。</p>
<h2>需要天時地利的巧合</h2>
<p>這需要水、冰、風與溫度恰到好處地配合,一年難得發生幾回,又發生在杳無人煙的荒漠——難怪百年來無人目擊。</p>
<blockquote>「不是石頭想走,是冰,悄悄推了它一把。」</blockquote>""",
  mao="幾百公斤的石頭趁沒人看的時候偷偷移位、還拖出痕跡卻死不承認——本編對這種行為,只有由衷的敬意。這不就是本編與桌緣那只馬克杯之間,心照不宣的默契?",
  sources="Scripps Institution of Oceanography · NASA · National Park Service"),

 dict(slug="pando-aspen", cat="科學怪奇 · USA", title="一整片森林,其實是一棵樹",
  deck="美國猶他州一整片、超過四萬棵的顫楊森林,其實是同一棵樹——牠們共享一套根系,可能已經活了數千年。",
  keywords="潘多,Pando,顫楊,最重的生物,猶他州,單一生物,無性繁殖",
  meta=[("地點","猶他州"),("重量","約 6,000 公噸"),("樹齡","可能數千年")],
  sym="il-tardi",
  img=dict(file="Pando in the Fall (11937950814).jpg", alt="猶他州潘多顫楊林,秋天一整片金黃",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>一整片森林,其實是一棵樹</h2>
<p>在美國猶他州魚湖旁,有一片占地約 43 公頃、超過四萬棵樹幹的顫楊林,名叫「潘多」(Pando,拉丁文「我擴展」之意)。從地面看,那是一整座森林;但在地底下,這四萬棵「樹」全都連在同一套根系上——牠們是同一個生命體、同一棵樹,基因完全相同。</p>
<h2>地表最重的生物之一</h2>
<p>把所有樹幹與地下根系加起來,潘多重達約 6,000 公噸,被認為是地球上已知最重的單一生物。牠靠著根部不斷冒出新芽來「複製」自己:一根樹幹老死,新的又從同一套根長出來。</p>
<h2>可能比金字塔還老</h2>
<p>也正因為牠不斷自我更新,潘多的實際年齡難以估計——保守估計數千年,也有人推測上萬年。牠或許在人類蓋起金字塔之前,就已經在那裡了。</p>
<h2>正在衰老的巨人</h2>
<p>令人憂心的是,近年研究發現潘多正在萎縮:鹿群啃食嫩芽,加上人類活動,讓牠難以再長出新的樹幹。這位活了數千年的巨人,可能正走向終點。</p>
<blockquote>「牠看起來是一片森林,其實,是一棵樹漫長的孤獨。」</blockquote>""",
  mao="一棵樹活成一整座森林、還是地表最重的生物——本編默默算了一下自己每天掉的毛,覺得若把它們全連起來,大概也稱得上某種意義上「分布最廣的生物」了。",
  sources="US Forest Service · Scientific American · Utah State University"),

 dict(slug="moai-bodies", cat="歷史謎團 · Easter Island", title="復活節島的巨人,其實有身體",
  deck="你以為復活節島的摩艾只是一顆顆巨大的石頭「頭」?其實牠們大多有完整的身體——只是被泥土埋了幾百年。",
  keywords="摩艾,復活節島,拉帕努伊,Moai,Rano Raraku,石像,巨人",
  meta=[("地點","復活節島(拉帕努伊)"),("數量","近 900 尊"),("最高","約 10 m")],
  sym="il-whittier",
  img=dict(file="Moai at Rano Raraku (Easter Island).jpg", alt="復活節島拉諾拉拉庫的摩艾石像群",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>不只是「石頭人頭」</h2>
<p>復活節島的摩艾石像舉世聞名,但多數人腦海裡的印象,是一顆顆立在草原上的巨大石頭頭顱。這其實是誤會——2010 年代的考古挖掘證實,許多看似「只有頭」的摩艾,地底下其實埋著完整的軀幹、手臂與雙手,只是在數百年間被土石逐漸掩埋。</p>
<h2>背上還刻著字</h2>
<p>挖出來的摩艾身體上,考古學家發現了刻紋與圖案,以及疑似儀式留下的紅色顏料痕跡。這些細節,在牠們「沉入土裡」的幾百年間,一直被靜靜保存著,不見天日。</p>
<h2>近 900 尊,是怎麼搬的?</h2>
<p>全島有近 900 尊摩艾,最高的約 10 公尺、重達數十噸。它們大多在拉諾拉拉庫火山口的採石場雕成,再運到島上各處。沒有輪子、沒有大型牲口的拉帕努伊人,究竟怎麼搬動這些巨人?有一派研究認為,他們讓石像「走路」:靠繩索左右搖晃,讓摩艾一步一步地「扭」向目的地。</p>
<h2>一座島的興衰</h2>
<p>摩艾也是一則警世寓言。有學說認為,為了雕鑿與搬運石像而過度砍伐森林,加速了島上生態與社會的崩解——不過近年也有研究,對這個「生態自毀」的敘事提出了修正。</p>
<blockquote>「你以為看見的是全部,其實只是露出土面的、那顆頭。」</blockquote>""",
  mao="一尊尊看似只有頭、身體卻深埋地底的巨人——本編懂。那正是本編縮在紙箱裡、只露出一顆頭盯著你時,刻意營造的效果。看不見的部分,才是重點。",
  sources="National Geographic · Easter Island Statue Project · Smithsonian"),

 dict(slug="pamukkale", cat="地方誌 · Turkey", title="水「長」出來的雪白城堡",
  deck="遠看像一座用棉花與雪堆成的城堡,層層梯田裡盛著溫泉——但它其實,是水一層層「長」出來的石頭。",
  keywords="棉花堡,Pamukkale,土耳其,石灰華,溫泉,梯田,希拉波利斯",
  meta=[("地點","土耳其"),("意為","棉花城堡"),("泉溫","約 35°C")],
  sym="il-blood",
  img=dict(file="The travertine terraces of Pamukkale 4.jpg", alt="土耳其棉花堡雪白的石灰華梯田與溫泉水池",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>水長出來的雪白梯田</h2>
<p>在土耳其西南部,有一整片雪白的階梯狀地形,層層水池沿著山坡而下,盛滿淡藍色的溫泉水,遠看就像一座用棉花砌成的城堡——當地語言就叫它「棉花堡」(Pamukkale)。</p>
<h2>它是石頭,不是雪</h2>
<p>這片白,不是雪也不是棉花,而是石頭。地底湧出的溫泉富含碳酸鈣,當熱水流到地表、二氧化碳逸散,溶解的礦物質便一層層沉澱、結晶,形成白色的「石灰華」。日積月累,水就這樣「長」出了一整座梯田;它至今仍在緩慢生長。</p>
<h2>古人也來泡</h2>
<p>早在兩千年前,古羅馬人就在這片溫泉旁建起了溫泉療養城市希拉波利斯(Hierapolis)。人們相信這裡的泉水能治病,慕名而來。如今,棉花堡與希拉波利斯古城一同被列為世界遺產。</p>
<h2>脆弱的白</h2>
<p>觀光人潮曾一度讓部分梯田變灰、乾涸。為了保護它,如今遊客須赤腳、限制在特定區域行走——這座水做的城堡,遠比看起來脆弱。</p>
<blockquote>「這不是雪,是時間與水,一層一層沉澱出來的耐心。」</blockquote>""",
  mao="一整座雪白、溫熱、還能泡澡的階梯城堡——本編必須承認,這是極少數幾個能讓本編認真考慮「主動碰水」的地方。極少數。",
  sources="UNESCO · Britannica · National Geographic"),

 dict(slug="kola-borehole", cat="歷史謎團 · Russia", title="人類挖過最深的洞",
  deck="冷戰時,蘇聯往地底鑽了一個超過十二公里深的洞,想挖穿地殼。他們沒挖穿——反而挖出一堆沒人料到的怪事。",
  keywords="科拉超深鑽孔,Kola Superdeep Borehole,最深的洞,蘇聯,地殼,冷戰",
  meta=[("地點","俄羅斯 科拉半島"),("深度","12,262 m"),("鑽探","1970–1992")],
  sym="il-whittier",
  img=dict(file="Kola sverhglubokaya 2020.jpg", alt="科拉超深鑽孔遺址,地表焊死的金屬井蓋",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>一場往地心的競賽</h2>
<p>冷戰不只是上太空的競賽,也是往地底鑽的競賽。1970 年,蘇聯在靠近挪威邊界的科拉半島開鑽,目標是盡可能深入地殼、一窺地球內部的祕密。二十多年後,他們鑽到了 <b>12,262 公尺</b>——至今仍是人類鑽入地球最深的紀錄。</p>
<h2>只鑽穿了地殼的一小層</h2>
<p>聽起來很深,但這其實只鑽穿了地殼厚度的一小部分,連底下的地函都還沒碰到。地球之大,由此可見一斑。</p>
<h2>地底的怪事</h2>
<p>越往下,越有意外。他們在好幾公里深處發現了流動的水,那在當時被認為不可能;也在岩芯裡找到二十多億年前的微小浮游生物化石。而最麻煩的是溫度:鑽到底時,岩石高達約攝氏 180 度,遠超預期,鑽頭幾乎像在「軟掉的塑膠」裡打轉——這也是計畫最終喊停的原因之一。</p>
<h2>被封起來的洞</h2>
<p>蘇聯解體後經費斷絕,鑽孔在 1990 年代被封。如今地表只剩一塊焊死的金屬蓋——一扇通往地球深處、卻只走了萬分之一路程的門。(順帶一提:網路上流傳的「鑽出地獄慘叫聲」純屬惡作劇,別當真。)</p>
<blockquote>「人類鑽了二十年、破了世界紀錄,也才勉強劃破了地球的一層皮。」</blockquote>""",
  mao="花二十年往地底鑽一個沒人進得去的洞,最後焊起來、什麼也沒得到——本編凝視這件事良久,竟感到一種熟悉的親切:這不就是本編對待每一個紙箱的態度?",
  sources="BBC · Smithsonian · Scientific American"),

 dict(slug="bioluminescent-sea", cat="自然異象 · Ocean", title="會發光的海",
  deck="有些夜晚的海浪,會在拍岸的瞬間亮起藍色的光。那不是魔法,是幾百萬個小生命,在你腳邊同時亮燈。",
  keywords="生物發光,藍眼淚,螢光海,渦鞭毛藻,bioluminescence,發光的海",
  meta=[("現象","生物發光"),("主角","渦鞭毛藻等"),("顏色","多為藍光")],
  sym="il-jelly",
  img=dict(file="Bioluminescent Handprint (oceanos2024loiacono-5).jpg", alt="手在含發光浮游生物的海水中留下的藍色光痕",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>會發光的浪</h2>
<p>在世界某些海域的夜裡,海浪拍岸、船槳劃過、甚至一隻腳踩進水裡的瞬間,水面會突然亮起一片幽幽的藍光。台灣的「藍眼淚」、各地的「螢光海灘」,說的都是同一件事——生物發光。</p>
<h2>是誰在發光?</h2>
<p>大多數時候,發光的主角是一種叫「渦鞭毛藻」的微小浮游生物。當海水被攪動、受到擾動時,牠們體內的化學反應會在瞬間釋放出冷光。一滴海水裡可能就有成千上萬個,牠們一起亮起,便成了整片發光的海。</p>
<h2>為什麼要發光?</h2>
<p>這道光,可能是一種求生策略。有一說是「防盜警報」:當浮游生物被小型掠食者吞食時發光,反而吸引來更大的掠食者,把小獵食者一起吃掉——用亮光替自己報了仇。</p>
<h2>可遇不可求</h2>
<p>發光需要浮游生物大量聚集,加上合適的季節與水溫,可遇不可求。也正因如此,親眼看見一片發光的海,總讓人終生難忘。</p>
<blockquote>「你踩進海裡的那一步,驚動了幾百萬個提著燈的小生命。」</blockquote>""",
  mao="一被打擾就渾身發光、還順便召來更大的麻煩替自己報仇——本編對這套「你敢碰我試試看」的處世哲學,深表贊同,並已收藏。",
  sources="National Geographic · Smithsonian · NOAA"),

 dict(slug="glass-frog", cat="科學怪奇 · Biology", title="肚皮透明、看得見心跳的青蛙",
  deck="有一種青蛙,肚皮是透明的——你能直接看見牠的心臟在跳動、腸胃在蠕動。而牠隱形的方式,更是不可思議。",
  keywords="玻璃蛙,透明青蛙,glass frog,隱形,紅血球,雨林",
  meta=[("科別","玻璃蛙科"),("分布","中南美洲"),("特徵","透明腹部")],
  sym="il-jelly",
  img=dict(file="Glass frog - Cibelle de Castro Pedroso.jpg", alt="腹部透明、可見內臟的玻璃蛙",
           by="Cibelle de Castro Pedroso / Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>看得見心跳的青蛙</h2>
<p>在中南美洲的雨林裡,住著一群「玻璃蛙」。牠們背部是綠色的,但腹部的皮膚卻是透明的——把牠翻過來,你能直接看見裡頭跳動的心臟、蠕動的腸胃,甚至正在發育的卵。牠像是被大自然做成了一具活生生的解剖模型。</p>
<h2>牠怎麼「隱形」?</h2>
<p>玻璃蛙白天趴在葉片上睡覺,半透明的身體讓陽光穿透、柔化了輪廓,讓掠食者難以發現。但真正驚人的招數,是科學家近年才揭曉的:睡覺時,玻璃蛙會把體內近 <b>九成</b>的紅血球「收納」進肝臟藏起來,讓血液幾乎變透明——於是連血,都不會洩露牠的行蹤。醒來後,再把紅血球放回血液循環。</p>
<h2>把血藏起來,卻不會出事?</h2>
<p>對人類而言,大量紅血球擠在一起會導致致命的凝血;玻璃蛙卻能安然無恙。牠究竟如何辦到,正是醫學研究者極感興趣的謎——這或許能為人類的血栓研究,帶來意想不到的線索。</p>
<blockquote>「牠隱形的方式,是連自己的血,都藏得不留痕跡。」</blockquote>""",
  mao="睡覺時把血都藏起來、好讓自己徹底隱形——本編試過類似的招式:把自己塞進全黑的角落,只留兩顆綠眼睛在外。效果,你懂的。",
  sources="Duke University · Science · Smithsonian"),

 dict(slug="catatumbo-lightning", cat="自然異象 · Venezuela", title="一年閃電兩百六十夜的天空",
  deck="委內瑞拉有一片天空,一年裡有將近三百個夜晚都在打雷閃電,幾乎不曾停歇——當地人叫它「永恆的閃電」。",
  keywords="卡塔通博閃電,永恆閃電,Catatumbo,委內瑞拉,馬拉開波湖,雷暴",
  meta=[("地點","委內瑞拉 卡塔通博河口"),("頻率","約 260 夜/年"),("別稱","永恆閃電")],
  sym="il-krakatoa",
  img=dict(file="Catatumbo Lightning - Rayo del Catatumbo.jpg", alt="委內瑞拉卡塔通博河口夜空中的密集閃電",
           by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>一座幾乎不熄的天然燈塔</h2>
<p>在委內瑞拉,卡塔通博河注入馬拉開波湖的河口上空,有一片幾乎永不安寧的天空:這裡一年之中約有 <b>260 個夜晚</b>雷電交加,一個晚上可以連續閃上好幾個小時、每小時數以千計的閃電。幾世紀以來,水手甚至靠它的亮光在夜裡辨識方向,把它當成一座天然的燈塔。</p>
<h2>為什麼偏偏是這裡?</h2>
<p>這是一場地形與氣候的完美巧合。白天,加勒比海的暖濕空氣被吹向內陸,撞上馬拉開波湖周圍高聳的安地斯山脈、被迫抬升;到了夜裡,山區的冷空氣下沉,與濕熱空氣劇烈碰撞,催生出一場又一場強烈雷暴——夜復一夜,幾乎從不缺席。</p>
<h2>差點消失的閃電</h2>
<p>2010 年,一場嚴重乾旱曾讓卡塔通博閃電罕見地停歇了數週,引發全球關注。所幸不久後,它又回來了,繼續照亮那片夜空。</p>
<blockquote>「有些地方的夜,從來不曾真正黑過。」</blockquote>""",
  mao="一年有兩百六十個晚上都在轟隆作響、卻從沒真的把誰嚇跑——本編勉強承認,這份「持之以恆的吵鬧」,本編在凌晨四點也做得到。",
  sources="NASA · Guinness World Records · National Geographic"),

 dict(slug="lake-hillier", cat="未解之謎 · Australia", title="舀起來也是粉紅色的湖",
  deck="澳洲有一座湖,是不可思議的泡泡糖粉紅色——而且就算你把水舀進瓶子裡,它依然是粉紅的。",
  keywords="粉紅湖,Lake Hillier,澳洲,中島,杜氏鹽藻,嗜鹽微生物",
  meta=[("地點","澳洲 中島"),("顏色","粉紅色"),("長度","約 600 m")],
  sym="il-blood",
  img=dict(file="Pink Lake (Lake Hillier) on Middle Island off the coast of Esperance Western Australia.jpg",
           alt="澳洲中島上鮮豔的粉紅色湖泊,與湛藍海洋僅一沙洲之隔", by="Wikimedia Commons", lic="CC BY-SA"),
  body="""<h2>一座泡泡糖色的湖</h2>
<p>在澳洲西南外海的中島(Middle Island)上,有一座長約 600 公尺的小湖,顏色是飽和到不真實的粉紅色——就像有人把一整湖的草莓奶昔倒進了森林裡。從空中俯瞰,它與一旁湛藍的海洋只隔著一道細細的沙洲,對比強烈得像修過圖。</p>
<h2>連舀起來都是粉紅的</h2>
<p>最奇妙的是,這抹粉紅並非水面反光的錯覺:你把湖水舀進瓶子裡,它依然是粉紅的。這意味著,顏色來自水裡實實在在的東西。</p>
<h2>粉紅從哪來?</h2>
<p>科學家長期認為,兇手是一種能在極鹹環境中生存的藻類「杜氏鹽藻」,牠在高鹽、強光下會製造大量紅色的類胡蘿蔔素;也有嗜鹽的細菌參與其中。2022 年的一項基因研究,進一步盤點出湖中一整群共同「調色」的微生物——但這座湖為何能維持得如此均勻而鮮豔,細節至今仍在研究。</p>
<h2>可以碰嗎?</h2>
<p>可以。這座湖的粉紅無毒,對人體無害——只是它位在受保護的島上,一般人難以親近,大多只能從空中一睹它的芳容。</p>
<blockquote>「有些顏色鮮豔得像假的,偏偏,是千真萬確的真。」</blockquote>""",
  mao="一座無論你怎麼舀、都堅持保持粉紅的湖——本編欣賞這種不因容器而改變、始終如一的堅持。雖然,本編個人堅持的顏色是純黑。",
  sources="ScienceAlert · Britannica · Guinness World Records"),

 dict(slug="naica-crystal-cave", cat="世界奇聞 · Geology", title="世界最大的水晶,長在一個會殺人的洞裡",
  deck="地表下三百公尺,有一個房間美得像假的。裡面躺著地球最大的水晶:比公車還長,比卡車還重。而它同時是個陷阱——走進去的人,身體會在幾分鐘內,失去替自己降溫的能力。",
  keywords="世界最大水晶,水晶洞,Naica,奈卡,墨西哥 巨型水晶,透石膏,Cave of Crystals",
  meta=[("地點","墨西哥 奇瓦瓦州 · 奈卡"),("最大晶體","約 12 公尺 · 55 噸"),("洞內","約 50°C · 濕度逾 90%")], sym="il-naica",
  img={"file":"Cristales cueva de Naica.JPG","alt":"奈卡水晶洞內交錯生長的巨型透石膏晶柱,一旁人影顯出驚人比例","by":"Wikimedia Commons","lic":"CC BY"},
  body="""<h2>比公車還長,比卡車還重</h2>
<p>二〇〇〇年,墨西哥奈卡(Naica)一座銀鉛鋅礦,兩名礦工兄弟為了往更深處開採,鑿穿了一道岩壁。他們以為後面是礦脈,結果是一間躺滿透明巨柱的房間——地表下約三百公尺,一個沒人知道存在的空間。最大的一根透石膏(selenite,一種石膏晶體)長約十二公尺、直徑近四公尺、重達五十五噸:比一輛公車還長,比一輛卡車還重,是人類至今找到最大的天然晶體。站進去,就像站在一顆大教堂那麼大的晶洞裡,水晶像傾倒的樑柱,從頭頂交錯穿過。</p>
<h2>一條窄到殘忍的溫度線</h2>
<p>為什麼這裡長出巨獸,別處只長得出小刀?關鍵是一條窄到殘忍的溫度線。這間洞曾被富含礦物質的地下熱水灌滿幾十萬年,水溫恰好卡在攝氏五十八度——正是硬石膏(anhydrite)開始緩慢轉化成透石膏的臨界點。只要溫度貼著這條線、待在下方、不被打擾,礦物就一個原子一個原子慢慢堆上去,一堆就是五十萬年,於是長成龐然大物。往山上走,還有一座更早發現的「劍之洞」,那裡降溫得快,晶體來不及從容生長,只能匆匆結晶——數量多,卻全長成細劍。同一鍋配方,只差在「耐心」,結果天差地遠。地質學家 García-Ruiz 的團隊甚至去研究晶體內封存的微小水滴,想從那幾滴古水裡,讀出這一切是怎麼發生的。</p>
<h2>美,但會要你的命</h2>
<p>而養大它們的高溫,至今還在:洞內空氣約五十度、濕度超過九成——體感遠遠不只五十度。人靠流汗降溫,可是在近乎飽和的空氣裡,汗根本蒸發不掉,身體唯一的散熱閥門等於被焊死,核心體溫飆升、判斷力跟著模糊。探險者得穿上塞滿冰塊的降溫衣,連呼吸的空氣都要從背後的冰袋打進肺裡;一包融冰大約只換得三十分鐘,而且鐵律是——四十五分鐘內出來,不准通融。有人多待了一會兒,開始神智恍惚、方向感盡失,那是身體在告訴他:你正在輸。</p>
<h2>然後,黑暗把門關上了</h2>
<p>人類能看見它,純粹是因為礦場的抽水機一直把水擋在外面。當採礦停止、抽水機歸於沉默(約二〇一五年),地下水再度爬升,一口把整座洞吞了回去。此刻那些水晶就在下面,泡回溫熱的黑水裡,多半正緩緩地、像沒有人來過之前那樣,繼續生長——而且很可能,再也不會有任何一雙眼睛,見到它了。</p>
<blockquote>「它花了五十萬年,長成沒人看過的樣子;又只用了幾年,把自己收回沒人到得了的地方。」</blockquote>""",
  mao="美到窒息、熱到致命、如今還自願沉回黑暗裡獨處——各位,本編說句公道話:這才叫真正的高冷。相較之下,本編那套「躲上衣櫃頂、誰叫都不理」,不過是業餘等級的模仿。",
  sources="Geology 期刊(García-Ruiz 等) · National Geographic · BBC Earth · Naica Project"),

 dict(slug="socotra-island", cat="世界奇聞 · Nature", title="地球上最像外星的島,和它會流血的樹",
  deck="印度洋上有一座島,和大陸斷了聯繫六百萬年。久到島上三分之一的植物,在地球別處都絕了跡。而它最出名的居民,是一種割開會流血的樹——那血,曾被拿去染羅馬人的衣、上義大利小提琴的漆。",
  keywords="最像外星的島,索科特拉,龍血樹,Socotra,Dracaena cinnabari,葉門,印度洋的加拉巴哥",
  meta=[("地點","葉門 · 印度洋"),("特有種","約 1/3 植物全球獨有"),("身分","UNESCO 世界遺產(2008)")], sym="il-socotra",
  img={"file":"Dragons Blood Tree, Socotra Island (10941931846).jpg","alt":"索科特拉島上傘狀樹冠的龍血樹群,樹形奇特宛如外星地景","by":"Rod Waddington / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>一座斷線六百萬年的島</h2>
<p>索科特拉(Socotra)屬於葉門,孤懸在印度洋、非洲之角外海,與阿拉伯大陸隔絕至少六百萬年。斷得夠久,它就成了一座活生生的演化實驗室:島上約三分之一的植物、超過九成的爬蟲類,在地球任何其他角落都找不到。人們叫它「印度洋的加拉巴哥」——但這稱呼,還低估了它有多像外星。</p>
<h2>那棵會流血的樹</h2>
<p>島上的招牌,是龍血樹(<i>Dracaena cinnabari</i>)。它的樹冠向上撐開成一把倒扣的傘,這造型全是為了活命:密實的冠層替底下的自己遮蔭、在乾旱的島上壓低蒸發,還能攔截飄來的海霧,讓凝結的水珠順著枝幹一路淌回根部。而它真正的名字,來自傷口——割開樹皮,滲出的是暗紅色的樹脂,古人稱之為「龍血」;連學名裡的 <i>cinnabari</i>,都取自那個代表朱紅的礦物名「辰砂」。</p>
<h2>被賣到全世界的一種紅</h2>
<p>那抹紅,走得比你想的遠。沿著古老的乳香貿易路線,龍血樹脂一路被運到地中海;希臘人、羅馬人、阿拉伯人拿它當染料,也當藥。在索科特拉當地,它至今是一味萬用偏方——止血、治濕疹、護皮膚,靠的是它的凝血特性。而幾百年後,同一種樹脂被刷上了十八世紀義大利製琴師的琴身,混進小提琴的亮漆裡。一座孤島上的樹,它的血,同時流進了羅馬人的衣料,和一把名琴的光澤。</p>
<h2>正在消失的紅</h2>
<p>但這片紅正在褪去。龍血樹被 IUCN 列為「易危」。二〇一五年,恰帕拉(Chapala)與梅古(Megh)兩個氣旋在一週之內接連撲上小島,一口氣抹掉了全島約三成的樹——不少是活了五百年、扛過無數場風暴的老樹,成千上萬地被連根拔起。更慢性的殺手是:就算老樹還站著,幾乎沒有小樹接班——外來的山羊,在幼苗長大之前就把它們啃光了。一座撐了六百萬年的孤島森林,很可能撐不過這一個世紀。</p>
<blockquote>「有些紅,是要花六百萬年才調得出來的;一旦從世界上抹掉,就再也補不回那個色號。」</blockquote>""",
  mao="受了傷,流的是能染布、入藥、上琴漆的莊重暗紅;本編受了傷,流的是口水、掉的是毛,還得勞煩你幫本編清。同樣是身上流出來的東西,樹的格局,本編這輩子是追不上了。",
  sources="UNESCO 世界遺產名錄 · IUCN 紅色名錄 · Dragon's blood 民族植物學研究 · National Geographic"),

 dict(slug="danakil-depression", cat="自然異象 · Ethiopia", title="地球上最不像地球的地方",
  deck="地表最低、最熱、最不像地球的角落之一。低於海平面一百多公尺,酸池冒著螢光黃綠、鹽地泛著金屬色——這裡卻住著人,還一刀一刀地挖著鹽。",
  keywords="達納基爾窪地,Danakil,Dallol,衣索比亞,最熱的地方,酸池,阿法爾,地球最像外星",
  meta=[("地點","衣索比亞 · 阿法爾窪地"),("海拔","低於海平面約 125 公尺"),("酸池","pH 近 0 · 冒硫磺")], sym="il-krakatoa",
  img={"file":"Ethiopia - Dallol.jpg","alt":"達納基爾窪地達洛爾一帶的螢光黃綠酸池與鹽結晶地景,宛如外星","by":"Thomas Fuhrmann / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>低於海平面的一座火爐</h2>
<p>衣索比亞東北、緊鄰厄利垂亞的達納基爾(Danakil)窪地,是地球上最熱、最低、最乾的地方之一——最低處低於海平面約一百二十五公尺。它坐落在三塊板塊互相扯開的裂縫上(東非大裂谷),地底的火還沒熄,地面的熱幾乎全年不退。</p>
<h2>螢光色的毒池</h2>
<p>窪地裡的達洛爾(Dallol)最不像地球:岩漿鑽進地底的鹽層,逼出一池池滾燙的酸泉。最酸最熱的池子被硫磺染成刺眼的螢光黃,溫一點的被銅鹽暈成藍綠,四周再鏽出一片鐵紅。有些池子酸鹼值近乎零。科學家把這裡當成火星與早期地球的替身來研究——甚至連「這種極端裡到底還有沒有生命」,都還在爭論。</p>
<h2>還是有人在這裡挖鹽</h2>
<p>而就在這片理應無法居住的地方,阿法爾人至今仍徒手從鹽原上鑿下一塊塊鹽磚,用駱駝商隊一路馱出沙漠。那是一門比記憶還古老的生意,做在一個看起來完全不歡迎人類的星球表面。</p>
<blockquote>「地球從不需要離開太陽系,就能長出一張外星的臉。」</blockquote>""",
  mao="又熱、又酸、又低,還得徒手挖鹽——各位,本編光是聽完就需要躺平三天。有些地方光是存在,就是一種不服輸;而本編的不服輸,是連這種地方都懶得去。",
  sources="NASA Earth Observatory · BBC / CNN 報導 · 東非大裂谷地質研究"),

 dict(slug="boiling-river-amazon", cat="自然異象 · Peru", title="一條會把你煮熟的河,附近卻沒有火山",
  deck="亞馬遜雨林深處,有一條河熱到能把掉進去的動物活活煮熟——最費解的是,方圓七百公里內,沒有任何一座火山。",
  keywords="亞馬遜沸騰河,Boiling River,Shanay-timpishka,秘魯,非火山地熱,Andrés Ruzo",
  meta=[("地點","秘魯 · 亞馬遜"),("水溫","約 80–95°C"),("最近火山","逾 700 公里外")], sym="il-krakatoa",
  body="""<h2>一條會煮熟東西的河</h2>
<p>它的當地名字「Shanay-timpishka」意思是「被太陽的熱煮沸」。這條河有超過六公里的河段,水溫常年落在攝氏八十到九十五度、偶爾逼近沸點。掉進去的小動物幾乎沒有機會——研究者形容,牠們是被由內而外煮熟的,眼睛往往最先燙壞。</p>
<h2>七百公里內,沒有火山</h2>
<p>這才是真正的謎。滾燙的河通常緊挨著火山,這一條卻離最近的火山逾七百公里。秘魯地質學家安德烈斯·魯索(Andrés Ruzo)小時候聽外公講過這條「傳說之河」,長大後所有專家都說不可能。二〇一一年他親自走進雨林,證實它千真萬確,而且與火山無關:很可能是雨水與安地斯融雪滲入極深的地底、被地熱燒熱,再沿著斷層裂隙湧回地表——一條由巨大集水區餵養的天然熱泉。</p>
<h2>一則被當成神話的真相</h2>
<p>當地的薩滿世代敬它為聖,學界卻長年當它是鄉野奇談,直到魯索把它一寸寸量了出來。如今它是有紀錄以來,地球上最大的非火山地熱河。</p>
<blockquote>「有些真相之所以沒被相信,不是因為它太荒謬,而是因為沒有人願意親自走那麼遠去看它一眼。」</blockquote>""",
  mao="一條沒有火山撐腰、卻自己燒到滾燙的河——本編欣賞這種不靠關係、純靠實力發熱的傢伙。至於本編的體溫,一向靠的是趴在你剛離開的鍵盤上。",
  sources="Andrés Ruzo《The Boiling River》(2016) · TED · IFLScience"),

 dict(slug="lake-natron", cat="自然異象 · Tanzania", title="把動物裹成「石像」的血紅之湖",
  deck="坦尚尼亞一座血紅色的湖,鹼性強到能灼傷皮膚。落在岸邊死去的鳥,會被鹽鹼一層層裹成栩栩如生的『石像』——卻也是兩百多萬隻紅鶴唯一的育嬰房。",
  keywords="納特龍湖,Lake Natron,坦尚尼亞,石化動物,蘇打湖,紅鶴,鹼水湖",
  meta=[("地點","坦尚尼亞"),("酸鹼","pH 高達 10.5"),("紅色來源","嗜鹽微生物")], sym="il-blood",
  img={"file":"Lake Natron, Tanzania.jpg","alt":"坦尚尼亞納特龍湖泛著血紅與橙色的鹼性湖面","by":"Christoph Strässler / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>血紅色的鹼水</h2>
<p>納特龍湖由附近的歐多因幽·倫蓋(Ol Doinyo Lengai)火山供給,滿是碳酸鈉與鹽類,酸鹼值高達十點五,足以灼傷不適應的動物皮膚與眼睛。而那攝人的血紅,來自一種嗜鹽的古菌——愈熱、愈鹹、愈紅。</p>
<h2>被鹽裹成「石像」的動物</h2>
<p>傳說它會把動物「變成石頭」,其實沒那麼魔幻,卻同樣驚人:死在岸邊的鳥與蝙蝠,屍體會被碳酸鈉一層層包覆、風乾保存,凝成一尊尊姿態逼真的鹽殼標本。二〇一三年,攝影師 Nick Brandt 把這些遺骸擺成生前的模樣拍成書,才讓全世界記住它們——但要說清楚:牠們不是活著被瞬間石化,而是死後才慢慢被鹽裹住的。</p>
<h2>卻也是紅鶴的天堂</h2>
<p>弔詭的是,這片致命的鹼水,同時是地球上最重要的一處生命搖籃:全球約兩百五十萬隻小紅鶴,幾乎都在這裡繁殖。正因為湖水凶險、天敵不敢靠近,牠們才得以安心產卵。同一座湖,一面是死亡,一面是新生。</p>
<blockquote>「最危險的地方,有時正是最安全的搖籃——端看你,是不是那個受得了它的。」</blockquote>""",
  mao="一座能把人灼傷、卻讓紅鶴安心生小孩的湖——本編懂這種反差:看起來最不好惹的,往往才是把該護的護得最好的。本編凶,也只對逗貓棒凶而已。",
  sources="Live Science · Smithsonian · Africa Check(校正「石化」說法) · NASA Earth Observatory"),

 dict(slug="movile-cave", cat="科學怪奇 · Romania", title="封閉了五百五十萬年的地下世界",
  deck="羅馬尼亞地下一座洞,與陽光、與外界的空氣完全隔絕了五百五十萬年。裡面沒有一絲光,空氣有毒——卻活著三十多種地球別處找不到的生物。",
  keywords="莫維萊洞,Movile Cave,羅馬尼亞,化學合成,無光生態系,特有種,硫化氫",
  meta=[("地點","羅馬尼亞 · 曼加利亞"),("封閉","約 550 萬年"),("特有種","逾 30 種")], sym="il-naica",
  body="""<h2>斷了五百五十萬年的一座洞</h2>
<p>羅馬尼亞曼加利亞附近的莫維萊洞(Movile Cave),在約五百五十萬年前的一場地中海乾涸事件中,被厚厚的黏土與黃土封死,從此與外界斷了聯繫。直到一九八六年,人們才意外把它挖開。</p>
<h2>不靠陽光運轉的生態系</h2>
<p>洞裡沒有一絲光,也就沒有光合作用。整條食物鏈的地基,換成了「化學合成」:細菌靠氧化硫化氫與甲烷取得能量,撐起底層。這裡的空氣對人類是毒的——富含硫化氫、甲烷與二氧化碳,含氧量卻只有地表的一半上下。</p>
<h2>三十多種只屬於黑暗的居民</h2>
<p>就在這樣的條件下,洞裡住著約五十種生物,其中三十多種在地球任何其他角落都找不到:沒有眼睛的白蜘蛛、半透明的蝦、像水蛭的蟲——全都在全然的黑暗裡、靠著一條由毒氣餵養的食物鏈演化而成。一個封在我們腳下、完全自給自足的外星生物圈,如今被科學家當成「沒有太陽,生命能否存在」的活教材。</p>
<blockquote>「把陽光拿走、把毒氣灌滿、再封上五百五十萬年——生命依然找到了活下去的辦法。」</blockquote>""",
  mao="沒有光、沒有好空氣,還被關了五百五十萬年,裡頭照樣熱鬧——各位,這叫生命力。相較之下,本編只要 WiFi 斷三分鐘就開始懷疑貓生。",
  sources="Movile Cave 洞穴生物學研究 · IFLScience · 相關期刊"),

 dict(slug="great-blue-hole", cat="自然異象 · Belize", title="海面上一個太完美的藍色圓洞",
  deck="貝里斯外海,一圈深藍的完美圓,直徑三百公尺、深逾一百二十公尺。它曾是陸地上的一座乾洞——直到海,漫了進來。",
  keywords="大藍洞,Great Blue Hole,貝里斯,海底天坑,鐘乳石,庫斯托,潛水",
  meta=[("地點","貝里斯 · 加勒比海"),("直徑","約 318 公尺"),("深度","約 124 公尺")], sym="il-naica",
  img={"file":"Great Blue Hole.jpg","alt":"貝里斯外海的大藍洞,深藍色的完美圓形天坑鑲在淺色珊瑚礁中","by":"Wikimedia Commons","lic":"公有領域"},
  body="""<h2>海面上一個太藍的圓</h2>
<p>從空中看,貝里斯外海鑲著一枚近乎完美的深藍色圓——直徑約三百一十八公尺、深逾一百二十公尺,在四周淺綠的珊瑚礁裡藍得幾乎不真實。它是同類天坑中,全世界最大的一個。</p>
<h2>它本來是陸地上的乾洞</h2>
<p>而它並非一開始就在海裡。在冰河時期、海平面還很低的年代,這裡是一座石灰岩溶洞,分好幾個階段慢慢長成——最早可追溯到約十五萬年前。等到末次冰期結束、海面上升,洞穴被灌滿、頂部塌陷,就成了今天這個圓形深坑。潛水者至今能在深處找到鐘乳石——那是它曾經站在空氣裡的鐵證。</p>
<h2>庫斯托讓世界看見它</h2>
<p>一九七一年,海洋探險家庫斯托(Jacques Cousteau)開著他的探勘船「卡呂普索號」前來測繪,還取出了洞裡的鐘乳石,證實它的「陸地身世」,並把它列為全球頂尖潛點之一。如今要下潛這裡,得是累積過相當經驗的老手才行。</p>
<blockquote>「有些深藍之所以令人屏息,是因為它記得自己,曾經站在陽光底下。」</blockquote>""",
  mao="一個深到看不見底、藍到不像真的的洞——本編承認,連向來天不怕地不怕的本編,也只想趴在岸邊看看就好。有些深度,是拿來敬畏的,不是拿來跳的。",
  sources="Wikipedia / Great Blue Hole · Forbes · 庫斯托 1971 探勘紀錄"),

 dict(slug="surtsey-island", cat="自然異象 · Iceland", title="一座才六十歲的島,幾乎不准人踏上",
  deck="一九六三年十一月,冰島外海的浪裡冒出了煙與火。隔天,一座全新的島出現了——而人類幾乎不准踏上它,只為看清楚一件事:生命,是怎麼從零開始的。",
  keywords="蘇爾特塞,Surtsey,冰島,新生島,火山島,生態演替,世界遺產",
  meta=[("誕生","1963.11.14"),("面積","曾約 2.7 平方公里"),("身分","UNESCO 世界遺產")], sym="il-krakatoa",
  img={"file":"Surtsey 051007.jpg","alt":"冰島外海因海底火山噴發而誕生的新生島蘇爾特塞","by":"Wikimedia Commons","lic":"公有領域"},
  body="""<h2>從海裡冒出來的新島</h2>
<p>一九六三年十一月十四日,冰島外海、赫馬島西南約十八公里處,浪間突然冒出煙與蒸氣。噴發其實早幾天就在一百三十公尺深的海床上開始,直到滾燙的岩漿撞上冰冷的海水,才在海面堆出看得見的東西。到隔天,一座新島已經站了起來。噴發一路持續到一九六七年,是冰島有紀錄以來最長的一次,堆出約二點七平方公里的陸地。</p>
<h2>一座「從零開始」的活實驗室</h2>
<p>科學家立刻意識到:這是千載難逢的機會——親眼看著生命,降臨在一塊之前根本不存在的土地上。於是冰島把它封了起來:一九六五年起劃為自然保留區,登島要許可,不種一株、不取一物,好讓拓殖與演替自然發生。至今登陸的七十八種植物裡,大多是海鷗帶來的——種子藏在鳥糞或反芻物裡,飄洋過海。先是苔蘚,再是草木、昆蟲,然後是築巢的鳥。</p>
<h2>連科學家都得忍住手</h2>
<p>整件事的重點,就是「不要插手」。一顆隨手丟下的蘋果核、一個沾了種子的腳印,都可能讓這座島長出不該有的東西,所以規矩嚴得近乎苛刻。二〇〇八年,它被列入 UNESCO 世界遺產。這是地球上最年輕的一塊土地,也是我們僅有的、看世界如何從空無填滿生命的窗口。</p>
<blockquote>「要看清生命怎麼開始,你得先學會:把手,收在背後。」</blockquote>""",
  mao="一座島誕生才六十年,人類卻忍著不去打擾它,只為看它慢慢長出苔蘚——本編欣賞這份克制。畢竟連本編都知道,有些東西,一伸爪就毀了。（雖然本編通常還是會伸。）",
  sources="UNESCO · Britannica · NASA Earth Observatory · Surtsey Research Society"),

 dict(slug="fly-geyser", cat="自然異象 · USA", title="人類不小心造出來的一座外星噴泉",
  deck="內華達沙漠裡,一座噴著滾水、五顏六色的地熱泉,看起來像另一顆星球。而它,其實是一場鑽井失誤——人類不小心造出來的。",
  keywords="飛噴泉,Fly Geyser,內華達,人造地熱,嗜熱藻類,Burning Man",
  meta=[("地點","美國 內華達"),("成因","1964 鑽井失誤"),("顏色","嗜熱藻類")], sym="il-krakatoa",
  img={"file":"Fly geyser.jpg","alt":"內華達沙漠中噴著熱水、布滿紅綠橙色藻類的飛噴泉","by":"Wikimedia Commons","lic":"公有領域"},
  body="""<h2>沙漠裡的外星噴泉</h2>
<p>內華達的荒漠中,立著一座不斷噴出滾水的礦物丘,通體被紅、綠、橙的條紋染得像另一顆星球的地表。它叫「飛噴泉」(Fly Geyser),外型奇異到不像地球該有的東西。</p>
<h2>其實是人類的失誤</h2>
<p>但它並非天然:一九六四年,一組工程師在這裡鑽井找地熱,發現約攝氏九十幾度的水對他們的計畫還不夠熱,便放棄了——卻沒把井口好好封住。從此滾燙、富含礦物質的水不停湧出,溶解的碳酸鈣一層層堆積,把礦物丘愈疊愈高,每年還在長高好幾英寸。一個沒關好的洞,長成了一座地標。</p>
<h2>那些顏色是活的</h2>
<p>而最迷人的,是它會動的顏色:嗜熱藻類在超過五十度的熱水裡繁盛,不同種類偏好不同溫度,於是牠們沿著水溫梯度各自站位——把礦物丘依「哪個角落多熱」漆成一圈圈色帶。這片私人牧場後來被 Burning Man 組織買下(二〇一六),二〇一八年起開放導覽。</p>
<blockquote>「最像外星的風景,有時不是大自然的傑作,而是人類一次沒收尾的意外。」</blockquote>""",
  mao="人類鑽井鑽到一半、隨手一放,竟放出一座外星噴泉——各位,這叫因禍得福。本編也常這樣:一個沒關好的抽屜、一件沒收好的毛線,往往就成了本編一整個下午的傑作。",
  sources="Wikipedia / Fly Geyser · Snopes · Atlas Obscura"),

 dict(slug="giants-causeway", cat="自然異象 · N. Ireland", title="四萬根六角石柱,大自然的完美幾何",
  deck="北愛爾蘭海邊,四萬根石柱緊緊相依,一根根幾乎是完美的六邊形。看起來像巨人親手鋪的路——傳說,還真是這麼說的。",
  keywords="巨人堤道,Giant's Causeway,北愛爾蘭,六角形石柱,玄武岩,芬恩,柱狀節理",
  meta=[("地點","北愛爾蘭 · 安特里姆"),("石柱","約 4 萬根"),("成因","熔岩冷卻收縮")], sym="il-krakatoa",
  img={"file":"Basalt Columns at Giant's Causeway in Northern Ireland - geograph 5571889.jpg","alt":"北愛爾蘭巨人堤道緊密相依的六角形玄武岩石柱","by":"David Dixon / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>像被誰精心鋪過的路</h2>
<p>北愛爾蘭安特里姆的海岸邊,約四萬根玄武岩石柱一根挨著一根,拼成一片向海裡延伸的石階。最教人不安的,是它們的形狀——大多是幾乎標準的六邊形,規則得不像天然,倒像被誰用尺量著鋪出來的。</p>
<h2>其實是熔岩冷卻的幾何</h2>
<p>但這確實是大自然的手筆。約六千萬年前,一場火山噴發讓大量熔岩漫流地表;當這層熔岩緩緩冷卻、收縮,內部應力便沿著最省力的方向裂開——而六邊形,正是把平面切割得最均勻、最有效率的形狀。於是石柱多半裂成六角;不過也有四角、五角、七角甚至八角的,真正的六邊形大約占六成。</p>
<h2>巨人鋪的路</h2>
<p>當然,傳說更好聽:愛爾蘭巨人芬恩(Finn McCool)為了跨海去和蘇格蘭巨人單挑,親手鋪了這條堤道;對方落荒而逃時,一路把堤道拆了,只留下今天這一段。一八六年,它被列入 UNESCO 世界遺產。科學與神話,各自替這片六角石陣,給了一個說得通的理由。</p>
<blockquote>「最規矩的圖案,不必出自誰的手;有時候,只是物理在冷卻時,順手畫下的。」</blockquote>""",
  mao="四萬根石柱,根根裂成六角,整齊到逼死強迫症——本編欣賞這種天生的講究。相較之下,本編踏過的每一排書,倒下的角度倒是各有主張,絕不重複。",
  sources="Britannica · UNESCO · British Geological Survey"),

 dict(slug="eye-of-the-sahara", cat="自然異象 · Mauritania", title="撒哈拉沙漠裡,那隻五十公里寬的「眼睛」",
  deck="從太空往下看,撒哈拉沙漠中央睜著一隻巨大的「眼睛」:一圈圈同心圓,直徑五十公里。它曾被當成隕石坑,真相卻更慢、更溫柔。",
  keywords="撒哈拉之眼,Richat,Eye of the Sahara,茅利塔尼亞,同心圓,地質穹丘,侵蝕",
  meta=[("地點","茅利塔尼亞"),("直徑","約 50 公里"),("成因","穹丘隆起 + 侵蝕")], sym="il-naica",
  img={"file":"ASTER Richat.jpg","alt":"從衛星俯瞰撒哈拉之眼,一圈圈同心環狀的地質構造","by":"NASA / Wikimedia Commons","lic":"公有領域"},
  body="""<h2>沙漠中央的一隻眼</h2>
<p>從太空俯瞰,茅利塔尼亞的撒哈拉沙漠中央,睜著一隻巨大的眼睛:一圈圈同心圓,直徑約五十公里,大得只有從高空才看得出全貌。它有個更冷的名字——「里夏特結構」(Richat Structure),但大家更愛叫它「撒哈拉之眼」。</p>
<h2>它不是隕石砸出來的</h2>
<p>因為外圈隆起、中心下凹,它一度被當成隕石撞擊坑。但後來發現不對:這裡沒有撞擊坑該有的中央尖峰,也找不到高溫熔融的痕跡。真正的成因慢得多——地底的岩漿把上方的沉積岩層頂成一個大穹丘,接著風、沙與水花了漫長的時間,一層層剝掉較軟的岩石,只留下較硬的部分,一圈圈裸露出來,成了今天的同心環。</p>
<h2>至少一億歲的耐心</h2>
<p>地質學家推估,這隻「眼睛」至少有一億年歷史。它不是一瞬間被砸出來的傷口,而是大地隆起之後,用上億年時間、被慢慢磨出來的紋路。</p>
<blockquote>「有些壯觀不是撞出來的,而是磨出來的——時間夠久,連沙子都能雕出一隻眼睛。」</blockquote>""",
  mao="一隻花了一億年才磨出來的眼睛,靜靜盯著天空——本編懂這種凝視。本編也常這樣,對著一面空白的牆,一盯就是一下午,深邃、神祕,而且什麼也沒在想。",
  sources="ESA · Live Science · Britannica · USGS"),

 dict(slug="chocolate-hills", cat="自然異象 · Philippines", title="旱季一到就變成巧克力色的一千多座山丘",
  deck="菲律賓薄荷島上,一千多座渾圓的小山鋪滿平原。雨季時青翠一片,一到旱季,它們齊刷刷轉成可可色——像有人在地上撒了一整盒巧克力。",
  keywords="巧克力山,Chocolate Hills,菲律賓,薄荷島,喀斯特,石灰岩,圓丘",
  meta=[("地點","菲律賓 · 薄荷島"),("數量","約 1,268–1,776 座"),("變色","旱季轉可可色")], sym="il-fairy",
  img={"file":"Chocolate Hills Bohol Philippines 2.jpg","alt":"菲律賓薄荷島上成群渾圓、旱季轉為褐色的巧克力山","by":"Philip Nalangan / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>撒了一地的圓丘</h2>
<p>菲律賓薄荷島的平原上,鋪著上千座幾乎一模一樣的圓潤小山——依不同調查,數量約在一千兩百多到一千七百多座之間,高度從三十到一百二十公尺不等。它們渾圓、成群、排列得毫無道理,遠看像有人把一整盒巧克力,倒在了綠色的桌布上。</p>
<h2>它們本來在海底</h2>
<p>這些山丘的身世,要追溯到它們還沉在海裡的年代:海洋生物的殘骸——珊瑚、貝殼——在海底一層層堆成石灰岩;後來地殼抬升,把石灰岩推出海面,再交給風與水去侵蝕、溶蝕,慢慢雕成一顆顆圓丘。這是典型的「喀斯特」地形。</p>
<h2>為什麼叫「巧克力」</h2>
<p>名字則來自它們的變色:雨季(約二到五月)時,山丘覆著青草、一片翠綠;可一到旱季,草枯了,整片山丘齊刷刷轉成可可褐——這才有了「巧克力山」這個甜到不像地質名詞的稱呼。</p>
<blockquote>「同一片風景,換個季節就換一種顏色——大地從不介意,偶爾也任性地,換身衣服。」</blockquote>""",
  mao="上千座山丘,旱季一到集體變巧克力色——本編光是聽到「巧克力」跟「成群」這兩個詞湊在一起,就已經開始盤算,該從哪一顆先開始巡視了。",
  sources="Live Science · GeologyScience · UNESCO Global Geopark"),

 dict(slug="antelope-canyon", cat="自然異象 · USA", title="沒有一盞燈,卻美得像打了光的峽谷",
  deck="亞利桑那沙漠底下,一道窄得側身才過得去的峽谷。陽光從頭頂的裂縫灑落,把砂岩牆染成流動的火焰色——這裡沒有一盞燈,卻美得像特意打過光。",
  keywords="羚羊峽谷,Antelope Canyon,亞利桑那,狹縫峽谷,光束,砂岩,納瓦荷",
  meta=[("地點","美國 亞利桑那 · 納瓦荷"),("成因","暴洪沖刷砂岩"),("光束","4–10 月正午")], sym="il-naica",
  img={"file":"Antelope Canyon, Page, Arizona (7721923070).jpg","alt":"羚羊峽谷內波浪狀的紅色砂岩壁與從頂縫灑下的光束","by":"James Gordon / Wikimedia Commons","lic":"CC BY"},
  body="""<h2>側身才過得去的裂縫</h2>
<p>在亞利桑那佩吉附近、納瓦荷族的土地上,藏著一道狹縫峽谷:窄處得側著身才擠得過。牆面是侏羅紀時期(約一億九千萬年前)的納瓦荷砂岩,被一次次暴洪帶著砂石,花了幾千年沖刷、打磨成如今這副波浪流動的模樣,深達地表下約三十七公尺。</p>
<h2>沒有燈,卻像打了光</h2>
<p>上羚羊峽谷的橫剖面呈「A」字形——底部較寬,頂部收窄成幾公分的細縫。每年四到十月的正午,陽光就從那道細縫直直插下,在沙地上打出一道道銳利的光柱;空氣中的浮塵讓光束變得清晰可見。這裡沒有任何人造光源,那一室瑰麗,全是陽光落在紅砂岩上的傑作。</p>
<h2>它其實很危險</h2>
<p>但這份美,是暴力雕出來的。狹縫峽谷至今仍會突發暴洪——一九九七年,一場山洪就在這裡奪走了多名遊客的性命。而每一次洪水,都在悄悄改寫它的形狀:今天你看到的牆面,已和多年前的老照片不太一樣了。</p>
<blockquote>「最溫柔的光,常常來自一道最不留情的裂縫。」</blockquote>""",
  mao="一道靠暴洪沖出來、靠陽光點亮的峽谷——本編欣賞這種不靠人工、渾然天成的登場方式。就像本編每次現身,也從不需要打光:本編走到哪,哪裡就是主場。",
  sources="Navajo Tours · GeologyScience · Atlas Obscura"),

 dict(slug="marble-caves", cat="自然異象 · Chile", title="一座湖水親手打磨的藍色大教堂",
  deck="智利巴塔哥尼亞一座冰河湖上,漂著幾座純大理石的洞穴。湖水把洞壁映成一圈圈流動的藍——像大自然,親手打磨出的一座藍色大教堂。",
  keywords="大理石洞,Marble Caves,智利,巴塔哥尼亞,將軍卡雷拉湖,大理石教堂,冰河湖",
  meta=[("地點","智利 · 將軍卡雷拉湖"),("材質","純大理石"),("成因","六千年湖浪打磨")], sym="il-naica",
  img={"file":"Catedral de mármol - Chile.jpg","alt":"智利巴塔哥尼亞將軍卡雷拉湖上,藍色紋路流動的大理石洞","by":"Dan Lundberg / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>湖上的大理石洞</h2>
<p>在智利與阿根廷交界、智利最大的將軍卡雷拉湖上,漂著一組被稱為「大理石教堂」的洞穴——洞壁是貨真價實的純大理石(一種以碳酸鈣為主的變質岩),被湖水沖出一道道光滑蜿蜒的曲面。</p>
<h2>六千年的湖浪</h2>
<p>它們是時間與水的合作:約六千年來,湖浪不斷拍打大理石;石頭在水面線附近溶解得最快,滲水把裂縫一點點撐寬,湖浪再把溶掉的部分帶走——就這樣,慢慢掏出一座座渦旋般的洞穴。</p>
<h2>那片藍,是借來的</h2>
<p>而最迷人的藍,其實不是大理石本身的顏色,而是湖水映上去的:洞壁像鏡子,映著湖面那抹隨水位與季節深淺變化的湛藍。湖水之所以那麼藍,是因為冰河融水裡懸浮著極細的岩粉,把陽光中的藍光散射出來。這座由巴塔哥尼亞冰河供水的洞,如今被列為自然保護區。</p>
<blockquote>「最美的顏色,有時不屬於自己——它只是誠實地,映出了身邊那片藍。」</blockquote>""",
  mao="洞壁自己不藍,卻大方地把湖水的藍,整片借來披在身上——本編懂這種借力。就像本編從不自己發熱,卻總有辦法,把你剛坐熱的位子,不著痕跡地,佔為己有。",
  sources="GeologyScience · Geology In · Cascada Travel"),

 dict(slug="zhangye-danxia", cat="自然異象 · China", title="被打翻的調色盤:整座山的彩色條紋",
  deck="中國甘肅張掖,一整片山被染成紅、橙、黃、綠的條紋,像有人打翻了上帝的調色盤。而這些顏色,是花了兩千四百萬年、一層層疊出來的。",
  keywords="張掖丹霞,七彩丹霞,Zhangye Danxia,甘肅,彩虹山,砂岩,世界地質公園",
  meta=[("地點","中國 甘肅 · 張掖"),("色帶","約 2400 萬年沉積"),("身分","UNESCO 世界地質公園")], sym="il-krakatoa",
  body="""<h2>被打翻的調色盤</h2>
<p>中國甘肅張掖,有一整片綿延約五百平方公里的丘陵,被染上紅、橙、黃、綠、藍的條紋,遠看像有人把一整盤顏料,潑在了群山之上。這就是「張掖丹霞」,又叫「七彩丹霞」。</p>
<h2>兩千四百萬年疊出來的顏色</h2>
<p>這些色帶,是時間一層層堆出來的:不同顏色的砂岩與礦物,經過約兩千四百萬年沉積、再被板塊擠壓抬升(這一帶約五億四千萬年前還是海底)。上色的主角是鐵——赤鐵礦鋪出招牌的紅與橙,針鐵礦等鐵礦物給出黃色,含綠泥石的層次或微量的銅,則暈出綠色。</p>
<h2>看起來假,其實是真</h2>
<p>正因為顏色鮮豔得太不真實,很多人第一眼會以為是修圖。但那一條條色帶,是貨真價實的礦物層,雨後色澤更濃。二〇一〇年,它被列入 UNESCO 世界遺產,二〇一九年成為世界地質公園。</p>
<blockquote>「有些風景鮮豔得像假的,偏偏,是大地花了兩千四百萬年,一筆一筆,認真上的色。」</blockquote>""",
  mao="一座山花兩千四百萬年,只為把自己染成彩色——本編佩服這份耐心。本編連把毛順成同一個方向都嫌費事,通常是舔到一半,就決定這樣也挺好。",
  sources="GeologyScience · China Highlights · UNESCO"),

 dict(slug="anime-on-threes", section="anime", cat="動漫冷知識 · Animation", title="日本動畫的「一秒 8 張」省格美學",
  deck="迪士尼一秒畫滿 24 張,日本電視動畫卻常常一秒只畫 8 張——這不是偷懶,而是逼出來的一門藝術。",
  keywords="有限動畫,一拍三,limited animation,手塚治虫,原子小金剛,作畫",
  meta=[("技法","Limited Animation"),("常見","一拍三 · 約 8fps"),("起點","1960 年代")], sym="il-anime-film",
  img={"file":"Zoetrope (AM 2001.6.1-1).jpg","alt":"西洋鏡——靠連續靜止畫面快速輪轉造出動態的早期動畫裝置","by":"Wikimedia Commons","lic":"CC BY"},
  body="""<h2>一秒到底幾張圖?</h2>
<p>我們看到的動畫,是一張張靜止的圖快速播放而成,電影一秒 24 格。迪士尼的黃金年代幾乎每一格都重畫,稱為「full animation」,流暢華麗,但成本驚人。</p>
<h2>日本的選擇:一拍三</h2>
<p>1960 年代,手塚治虫的《原子小金剛》把動畫搬上日本電視,卻面臨預算與時間的殘酷限制。解方是「有限動畫」:同一張圖連續播放三格,等於一秒只有 8 張真正不同的畫面——業界叫它「一拍三」。角色不動時只動嘴、用滑動的背景營造移動感、大量重複使用畫面。</p>
<h2>限制,長成了風格</h2>
<p>少了張數,日本動畫轉而在「一張圖」上下功夫:華麗的定格構圖、戲劇性的光影、留白與靜止的張力。省格,反而磨出了一套獨特的視覺語言——你熟悉的那種「動漫感」,正是從這份拮据裡長出來的。</p>
<blockquote>「不是每一格都要動。真正的重點,是你讓哪一格,靜止。」</blockquote>""",
  mao="一秒只需動 8 下、其餘時間華麗地靜止不動——各位,這不只是動畫技法,這是本編畢生奉行的能量管理哲學。",
  sources="手塚治虫官方 · Anime News Network · 《Anime: A History》(Jonathan Clements)"),

 dict(slug="miyazaki-retirements", section="anime", cat="動漫怪談 · Studio Ghibli", title="宮崎駿到底「退休」過幾次?",
  deck="這位動畫大師鄭重宣布引退的次數,多到成了粉絲之間的溫柔笑話——因為大家都知道,他八成又會回來。",
  keywords="宮崎駿,吉卜力,退休,引退,風起,蒼鷺與少年,神隱少女",
  meta=[("導演","宮崎駿"),("工作室","吉卜力"),("引退宣言","不只一次")], sym="il-anime-manga",
  img={"file":"Hayao Miyazaki.jpg","alt":"動畫導演宮崎駿的肖像","by":"Thomas Schulz / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>一而再的「封筆」</h2>
<p>宮崎駿是吉卜力的靈魂人物,《龍貓》《神隱少女》《霍爾的移動城堡》皆出自他手。但他也以「反覆退休」聞名:早在多部作品之後他就談過收山,2013 年《風起》上映時更召開記者會正式宣布引退,轟動全球。</p>
<h2>然後,他又回來了</h2>
<p>幾年後,閒不下來的他重返工作崗位,交出了 2023 年的《蒼鷺與少年》,還拿下奧斯卡最佳動畫長片。粉絲們早已練就一套心照不宣的默契:宮崎駿說退休,大概等於「休息一下」。</p>
<h2>停不下來的那雙手</h2>
<p>對他而言,畫圖近乎一種呼吸。與其說他戒不掉工作,不如說,創作本身就是他面對世界的方式。所以每一次「最後一部」,大家都笑著,半信半疑地期待著下一部。</p>
<blockquote>「他每一次說再見,我們都當成,下次見。」</blockquote>""",
  mao="鄭重宣布退休、過陣子又若無其事回來上工——本編對這種行為模式瞭若指掌。那正是本編每天對那根逗貓棒發的誓,以及每天親手毀掉的誓。",
  sources="Studio Ghibli · NHK · Anime News Network"),

 dict(slug="mew-secret", section="anime", cat="動漫怪談 · Pokémon", title="夢幻,是工程師偷偷塞進遊戲的",
  deck="初代寶可夢紅綠版裡最神祕的「夢幻」,並不在原本的計畫裡——牠是一位程式設計師,趁著最後一刻偷偷藏進去的。",
  keywords="夢幻,Mew,寶可夢,紅綠版,森本茂樹,幻之寶可夢,彩蛋",
  meta=[("作品","寶可夢 紅·綠(1996)"),("幻之寶可夢","夢幻 / Mew"),("藏匿者","森本茂樹")], sym="il-anime-game",
  body="""<h2>擠出來的一點空間</h2>
<p>1996 年,初代《寶可夢 紅·綠》開發到尾聲。負責程式的森本茂樹,在刪掉除錯用資料後,卡帶裡意外多出了一點點空間——剛好夠塞下一隻寶可夢。於是,他在團隊幾乎不知情的情況下,偷偷把一隻叫「夢幻」的寶可夢藏了進去。</p>
<h2>本來不打算讓人抓到</h2>
<p>夢幻原本沒有正規的取得方式,幾乎像一個埋在遊戲深處、注定沉睡的祕密。沒想到,玩家透過特定的程式錯誤,真的把牠給抓了出來——夢幻,就此成為傳說。</p>
<h2>意外點燃的狂熱</h2>
<p>任天堂順水推舟,後來透過活動正式發放夢幻,掀起全球熱潮。一個工程師一時興起的惡作劇,意外成了寶可夢史上最經典的行銷神話之一。</p>
<blockquote>「最珍貴的祕密,往往是某個人,在最後一刻偷偷藏進去的。」</blockquote>""",
  mao="趁沒人注意時,把一個小東西塞進誰都想不到的縫隙裡——本編對這門技藝,自認略有心得。你家的鑰匙,建議再找找。",
  sources="森本茂樹訪談(Game Informer)· The Pokémon Company · Kotaku"),

 dict(slug="pokemon-shock-1997", section="anime", cat="動漫怪談 · Pokémon", title="讓數百人送醫的那一集寶可夢",
  deck="1997 年,一集寶可夢動畫在日本播出後,數百名孩子被緊急送醫——只因為畫面中,幾秒鐘的紅藍閃光。",
  keywords="3D龍事件,寶可夢休克,Pokémon Shock,光敏性癲癇,1997,ポリゴン",
  meta=[("事件","ポリゴンショック"),("日期","1997.12.16"),("送醫","逾 600 人")], sym="il-anime",
  body="""<h2>幾秒鐘的閃光</h2>
<p>1997 年 12 月 16 日,寶可夢動畫播出一集,劇情裡有一段紅藍交替、高速閃爍的爆炸畫面,持續了數秒。就在那之後,全日本各地陸續有孩子出現頭暈、抽搐甚至昏厥的症狀,超過 <b>600 人</b>被送醫。</p>
<h2>光敏性癲癇</h2>
<p>元凶,是「光敏性癲癇」:高頻率、高對比的閃爍光線,可能誘發部分人的癲癇發作。那段畫面的閃爍頻率,不幸正落在最危險的範圍。事件震驚全國,寶可夢動畫因此停播了數個月。</p>
<h2>從此改變的規則</h2>
<p>這起事件被稱為「3D龍事件」(因那集主角是寶可夢「3D龍」而得名,儘管閃光其實出自另一個攻擊場景)。此後,日本動畫在片頭普遍加上「請在明亮的房間、與電視保持距離觀看」的警語,閃爍畫面的製作規範也全面收緊——這是一整個產業,用一次慘痛換來的教訓。</p>
<blockquote>「有時候,最危險的,不是怪獸,而是那幾秒鐘的光。」</blockquote>""",
  mao="一段幾秒的閃光就能撂倒數百人——本編看著窗外那盞一閃一閃的霓虹燈,第一次覺得,自己每晚盯著它發呆的執著,或許該有個限度。",
  sources="BBC · The Guardian · Wikipedia(Pokémon Shock)"),

 dict(slug="goku-voice-nozawa", section="anime", cat="動漫冷知識 · Dragon Ball", title="一個人,配了三代孫悟空",
  deck="從孫悟空、到他兒子孫悟飯、再到孫子孫悟天——《七龍珠》這祖孫三代的聲音,全出自同一位配音員。",
  keywords="野澤雅子,孫悟空,七龍珠,聲優,一人三役,配音",
  meta=[("作品","七龍珠"),("聲優","野澤雅子"),("一人三角","悟空·悟飯·悟天")], sym="il-anime-mic",
  img={"file":"野沢雅子.png","alt":"為三代孫悟空配音的聲優野澤雅子","by":"Wikimedia Commons","lic":"公有領域"},
  body="""<h2>祖孫三代,同一把嗓子</h2>
<p>在《七龍珠》裡,孫悟空、他的兒子孫悟飯,以及孫子孫悟天,聲音全部來自同一位配音員——野澤雅子。也就是說,當劇中這祖孫同框對話,其實是同一個人,一個人分飾三角、自己跟自己說話。</p>
<h2>從 1980 年代配到今天</h2>
<p>野澤雅子自 1986 年動畫開播起就為悟空配音,數十年來從未換人。即使高齡,她依舊中氣十足地喊出那句招牌台詞,陪著好幾個世代的觀眾一起長大。對無數粉絲而言,悟空的聲音,就是她的聲音,無可取代。</p>
<h2>配音,是一門看不見的演技</h2>
<p>要用聲音區分祖孫三代的性格與年紀,是極高難度的挑戰。這也提醒我們:動畫角色的靈魂,有一半,是聲優給的。</p>
<blockquote>「同一把嗓子,喊出了三個世代的『我還能再變強』。」</blockquote>""",
  mao="一個人分飾三角、自己跟自己對話還毫無破綻——本編每天對著鏡子與窗上的倒影哈氣、對峙、和好,深知這門獨角戲有多不容易。",
  sources="東映動畫 · Anime News Network · Wikipedia"),

 dict(slug="totoro-grave-double-feature", section="anime", cat="動漫怪談 · Studio Ghibli", title="《龍貓》與《螢火蟲之墓》,當年是一起上映的",
  deck="一部是治癒無數人的森林精靈,一部是讓全場哭到虛脫的戰爭悲劇——1988 年,吉卜力把這兩部,放在同一場放映。",
  keywords="龍貓,螢火蟲之墓,吉卜力,雙片同映,1988,高畑勳,宮崎駿",
  meta=[("年份","1988"),("雙片同映","龍貓 + 螢火蟲之墓"),("工作室","吉卜力")], sym="il-anime-masks",
  img={"file":"Firefly glowing on a leaf.jpg","alt":"葉上發光的螢火蟲,呼應《螢火蟲之墓》的意象","by":"Kyu3a / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>史上最殘忍的雙片場</h2>
<p>1988 年,吉卜力同時推出兩部電影:宮崎駿溫暖治癒的《龍貓》,與高畑勳描寫戰時兄妹餓死的《螢火蟲之墓》。而當年,這兩部竟是「雙片同映」——觀眾買一張票,一場看完兩部。</p>
<h2>看的順序,是一種折磨</h2>
<p>據說不同場次的播放順序不一。若先看《龍貓》再看《螢火蟲之墓》,觀眾會從幸福的頂點一路墜入絕望;若倒過來,則是在哭乾眼淚後,才被龍貓輕輕接住。無論哪種,都是情緒的雲霄飛車。</p>
<h2>票房慘澹,卻成永恆</h2>
<p>諷刺的是,這個組合當年票房並不理想——太沉重的題材讓許多家庭卻步。但時間證明,這兩部都成了影史經典。一暖一悲,像硬幣的兩面,共同定義了吉卜力的深度。</p>
<blockquote>「同一場電影,讓你先學會愛,再學會失去。」</blockquote>""",
  mao="先給你一隻毛茸茸的大龍貓、再給你一場心碎——本編嚴正抗議這種安排。情緒的雲霄飛車,本編只坐一種:睡前的、單程向下的那種。",
  sources="Studio Ghibli · The Criterion Collection · Anime News Network"),

 dict(slug="tezuka-god-of-manga", section="anime", cat="動漫冷知識 · Manga", title="「漫畫之神」與那場沒有結論的爭議",
  deck="手塚治虫被尊為「漫畫之神」,幾乎奠定了現代日本漫畫與動畫的樣貌。而他的一部經典,至今仍與迪士尼有一段說不清的糾葛。",
  keywords="手塚治虫,漫畫之神,森林大帝,獅子王,原子小金剛,火之鳥",
  meta=[("人物","手塚治虫"),("稱號","漫畫之神"),("作品","森林大帝(1950)")], sym="il-anime-manga",
  img={"file":"Osamu-Tezuka-1.jpg","alt":"被譽為「漫畫之神」的手塚治虫","by":"Wikimedia Commons","lic":"公有領域"},
  body="""<h2>一個人,撐起一整個產業的地基</h2>
<p>手塚治虫(1928–1989)被譽為「漫畫之神」與「動畫之父」。《原子小金剛》《怪醫黑傑克》《火之鳥》……他不只作品量驚人,更確立了日本漫畫的分鏡語言、把有限動畫帶上電視,深深影響了後來的每一位創作者。</p>
<h2>森林大帝與獅子王的糾葛</h2>
<p>手塚有一部經典《森林大帝》,主角是一頭白獅,1950 年開始連載。1994 年迪士尼《獅子王》上映後,兩者在角色、場景與情節上的相似,引發了長年爭論。迪士尼始終否認參考過手塚的作品,而手塚本人早已離世,無從對證——這樁公案,終究沒有一個明確的結論。</p>
<h2>神,也有謙卑的一面</h2>
<p>有趣的是,手塚生前是不折不扣的迪士尼迷,據說看過《小鹿斑比》數十遍。「漫畫之神」與「動畫王國」之間,或許從來就不是單純的對立,而是一段互相凝視、彼此影響的複雜關係。</p>
<blockquote>「神留下的,不是答案,而是一整個世界的開端。」</blockquote>""",
  mao="一頭白獅的故事,和一樁誰也說不清的公案——本編對這類懸案向來保持中立。畢竟,本編自己深夜打翻的花瓶,也從來查無兇手。",
  sources="手塚プロダクション · The New York Times · Anime News Network"),

 dict(slug="doraemon-endings", section="anime", cat="動漫怪談 · Doraemon", title="哆啦A夢那些「都市傳說結局」",
  deck="「大雄其實是植物人,一切都是他的夢」——這些讓無數人淚崩的哆啦A夢結局,你或許聽過。但它們,全都不是真的。",
  keywords="哆啦A夢,都市傳說,結局,同人誌,藤子不二雄,小叮噹",
  meta=[("作品","哆啦A夢"),("性質","粉絲創作 / 都市傳說"),("官方","從未正式完結")], sym="il-anime-ghost",
  body="""<h2>那些流傳已久的「最終回」</h2>
<p>網路上流傳著好幾個哆啦A夢的「感人結局」:有的說哆啦A夢電池耗盡、大雄發憤圖強長大成為工程師把牠修好;有的說整個故事其實是植物人大雄的夢……它們感人至深,讓一代代讀者潸然淚下。</p>
<h2>但這些,都是粉絲寫的</h2>
<p>真相是:這些結局,沒有一個出自原作者藤子·F·不二雄之手。其中最有名的「大雄長大修好哆啦A夢」版本,是一位同人作者於 2000 年代創作、印成同人誌販售的——因為畫得太好、太動人,一度被誤認為官方結局,銷量驚人,最後甚至驚動了版權方出面處理。</p>
<h2>官方,其實從沒讓它完結</h2>
<p>藤子·F·不二雄於 1996 年辭世,《哆啦A夢》並沒有一個他親筆畫下的正式大結局。也正因如此,這些溫柔的「假結局」才有了生長的縫隙——它們是粉絲們,替自己深愛的故事,補上的一封情書。</p>
<blockquote>「有些結局是假的,但為它落下的眼淚,是真的。」</blockquote>""",
  mao="一個太過動人、以致被當成真的假結局——本編懂這種力量。那正如本編每次裝出的、楚楚可憐的飢餓表情:明明剛吃過,你卻總是信了。",
  sources="朝日新聞 · 小学館 · Anime News Network"),

 dict(slug="eva-last-episodes", section="anime", cat="動漫怪談 · Evangelion", title="《EVA》最後兩集,為什麼變成那樣?",
  deck="一部機器人動畫,最後兩集卻幾乎沒有機器人,只剩角色在意識深處自我對話、線稿與定格。這場爭議背後,有現實的無奈,也有導演的孤注一擲。",
  keywords="新世紀福音戰士,EVA,庵野秀明,最終話,結局爭議,GAINAX",
  meta=[("作品","新世紀福音戰士(1995)"),("爭議","最終兩集"),("導演","庵野秀明")], sym="il-anime-film",
  body="""<h2>期待落空的結局</h2>
<p>1995 年的《新世紀福音戰士》風靡全日本。但當觀眾滿心期待迎接最終決戰時,最後兩集卻轉向了極度抽象、內省的心理獨白:大量的定格、線稿、文字,以及角色在潛意識裡的自我剖析。許多人一頭霧水,甚至憤怒。</p>
<h2>現實的無奈</h2>
<p>背後有很實際的原因:製作進度嚴重落後、預算與時間都已見底。在資源極度緊繃下,團隊難以完成原先設想的宏大結局。但這並非全部——導演庵野秀明當時也深陷低潮,他選擇把鏡頭從外在的戰鬥,轉向角色(也是他自己)內心的掙扎。</p>
<h2>爭議,催生了另一種經典</h2>
<p>這個結局兩極評價至今不休。而庵野後來以劇場版《The End of Evangelion》,給出了另一種更具體、也更殘酷的版本。無論你愛或恨,那兩集都成了動畫史上最被反覆討論的結尾之一——限制與心境,有時會逼出最不像商品、卻最像作品的東西。</p>
<blockquote>「當外面的世界打不下去了,他把鏡頭,轉向了裡面。」</blockquote>""",
  mao="預算燒光、時間見底,乾脆把最終決戰改成一場內心獨白——本編對這種「絕境中的即興」深感敬佩。本編每次把打翻的東西假裝成「本來就想這樣擺」,用的是同一套心法。",
  sources="庵野秀明訪談 · GAINAX · Anime News Network"),

 dict(slug="jojo-stand-names", section="anime", cat="動漫冷知識 · JoJo", title="JOJO 的替身,名字全是西洋音樂梗",
  deck="白金之星、瘋狂鑽石、綠色手指……《JOJO的奇妙冒險》裡那些帥氣的替身名,幾乎全借自西洋搖滾樂——這也讓它在海外,惹上一堆改名的麻煩。",
  keywords="JOJO,替身,荒木飛呂彥,西洋音樂,改名,Stand",
  meta=[("作品","JOJO的奇妙冒險"),("命名來源","西洋音樂"),("作者","荒木飛呂彥")], sym="il-anime-music",
  img={"file":"Vinyl collection at a record store (Unsplash).jpg","alt":"成排的黑膠唱片——JOJO 替身名字的西洋音樂出處","by":"Mr Cup / Fabien Barral","lic":"CC0"},
  body="""<h2>一座行走的音樂圖書館</h2>
<p>《JOJO的奇妙冒險》作者荒木飛呂彥是出了名的音樂迷。漫畫裡的「替身」——那種具象化的超能力——名字幾乎全來自西洋樂團與歌曲:白金之星、瘋狂鑽石(取自 Pink Floyd 的名曲),還有大量取自 Led Zeppelin、Prince、Queen 的名字。連許多角色的本名,也是音樂梗。</p>
<h2>海外只好一路改名</h2>
<p>這份浪漫到了海外卻成了燙手山芋:直接使用這些名字,可能觸及商標與版權。於是在海外的遊戲與正版翻譯裡,大量替身被迫改名,粉絲得同時記住一個角色的好幾個名字。</p>
<h2>藏在細節裡的致敬</h2>
<p>對懂行的樂迷來說,追查每個替身名字的出處,本身就是一場尋寶遊戲。這也是荒木埋在作品裡、對自己所愛之物最直接的告白。</p>
<blockquote>「每一個帥氣的名字背後,都藏著作者深夜裡單曲循環的那首歌。」</blockquote>""",
  mao="把自己最愛的東西,偷偷變成作品裡每一個名字——本編懂這份心意。這正是為什麼,本編巡視地盤時碰倒的每一樣東西,都恰好是你最珍惜的那幾件。那是愛。",
  sources="荒木飛呂彥訪談 · 集英社 · Anime News Network"),

 dict(slug="super-saiyan-blond-reason", section="anime", cat="動漫冷知識 · Dragon Ball", title="超級賽亞人為什麼是金髮?鳥山明的真心話",
  deck="悟空一變身,黑髮就根根倒豎、燒成金色,連瞳孔都轉青綠。粉絲替這頭金髮想過能量、輻射、血統覺醒——各種熱血解釋。但作者鳥山明給的真正答案,樸實到有點好笑:黑色,太費工了。",
  keywords="超級賽亞人 金髮 原因,悟空 金髮 為什麼,鳥山明,Dragon Ball,七龍珠,超級賽亞人 由來",
  meta=[("作者","鳥山明"),("真因","黑髮塗墨太費工"),("附帶","變身一眼可辨")], sym="il-anime",
  body="""<h2>一頭被過度解讀的金髮</h2>
<p>悟空第一次化身超級賽亞人,頭髮根根倒豎、由黑轉金,連眼睛都變成青綠色,氣勢驚人。這麼多年,粉絲替這頭金髮編過各種說法:是能量外洩、是輻射、是賽亞人血統覺醒的印記——一個比一個熱血。</p>
<h2>作者的真心話:黑色太費工</h2>
<p>但鳥山明本人的答案,樸實得有點好笑。在週刊連載的黑白漫畫裡,大面積的純黑是靠人手一筆一筆用墨塗滿的,業界叫這道工序「塗黑」(ベタ)。而悟空那頭又尖又密的黑髮,正是塗黑的惡夢:每一根、每一週,都得在死線前手工填滿。於是變身的那一刻,鳥山明乾脆把頭髮「留白」不塗——省下的上墨工時極為可觀。等動畫替它上色,這頭沒被塗黑的留白,自然就成了金色。</p>
<h2>省下來的,不只時間</h2>
<p>而這個為省工而生的偷懶,順手還賺到一個大好處:留白的髮和四周的黑對比極強,印在報紙般粗糙的紙上,讀者一眼就看得出「他變身了」,連一句台詞都不必。青綠的眼睛再補上臨門一腳。一個「這格能不能少塗一點」的念頭,最後長成了動漫史上最好認的畫面之一——限制,又一次長成了風格。</p>
<blockquote>「史上最強的變身,起點只是某個趕稿的深夜,一個想少塗幾筆墨的念頭。」</blockquote>""",
  mao="為了少塗幾格墨,乾脆讓全宇宙最強的變身變成金色——這哪叫偷懶,這叫把力氣精準砸在刀口上。各位,本編奉行的能量管理最高境界,說穿了就四個字:華麗,擺爛。",
  sources="鳥山明與當時編輯訪談 · 週刊少年 Jump(集英社) · Den of Geek / ComicBook 整理報導"),

 dict(slug="doraemon-no-ears", section="anime", cat="動漫冷知識 · Doraemon", title="哆啦A夢為什麼沒有耳朵、又為什麼是藍的?",
  deck="藍色、圓臉、怕老鼠——哆啦A夢的三個招牌特徵,背後其實是同一場慘劇。牠原本,是黃色的,而且有耳朵。",
  keywords="哆啦A夢 沒有耳朵,哆啦A夢 為什麼藍色,小叮噹 耳朵,Doraemon,藤子不二雄,怕老鼠",
  meta=[("原本","黃色 · 有耳朵"),("失去耳朵","被機器老鼠啃掉"),("變藍","哭到掉漆")], sym="il-anime-manga",
  body="""<h2>牠原本是黃色、有耳朵的</h2>
<p>今天的哆啦A夢圓滾滾、藍汪汪、沒有耳朵。但在官方設定裡,牠出廠時是一隻黃色、有著一對耳朵的機器貓。這三樣後來全變了,而且是同一天、同一場意外造成的。</p>
<h2>耳朵,是被機器老鼠啃掉的</h2>
<p>故事是這樣:主人拿一個二十二世紀的「老鼠造型」工藝機器,本想幫哆啦A夢的模型修耳朵,機器卻聽錯指令,把真正的哆啦A夢的耳朵給啃了。送醫之後,不但沒修好,反而兩隻耳朵都保不住。從此,牠對老鼠怕到骨子裡——招牌的「怕老鼠」,就是這麼來的。</p>
<h2>藍色,是哭出來的</h2>
<p>失去耳朵的哆啦A夢傷心欲絕,想喝「樂觀藥水」振作,卻拿錯了瓶子、灌下「悲傷藥水」,結果哭到整片黃色鍍層都剝落、生鏽——於是變成了藍色。一場烏龍,一次說清了牠最出名的三件事:沒耳朵、藍身體、怕老鼠。</p>
<blockquote>「最惹人喜愛的樣子,有時是從一場最不想提起的意外裡,長出來的。」</blockquote>""",
  mao="被啃掉耳朵、哭到掉色、還怕老鼠怕一輩子——這履歷,本編看了都想遞暖暖包。不過話說回來,一隻怕老鼠的貓型機器人,本編實在是……嗯,不予置評。",
  sources="藤子·F·不二雄 官方設定 · 小學館 · Doraemon 資料"),

 dict(slug="shinchan-usui-death", section="anime", cat="動漫怪談 · Crayon Shin-chan", title="蠟筆小新的作者走了之後,小新為什麼還在?",
  deck="二〇〇九年,蠟筆小新的作者臼井儀人上山拍照,失足墜崖,享年五十一歲。連載戛然而止——但小新,並沒有跟著結束。",
  keywords="蠟筆小新 作者 過世,臼井儀人 墜崖,新蠟筆小新,Crayon Shin-chan,UY Studio",
  meta=[("作者","臼井儀人"),("辭世","2009 · 登山墜崖 · 51 歲"),("之後","《新蠟筆小新》續刊")], sym="il-anime",
  img={"file":"Mt.Arafune.JPG","alt":"臼井儀人拍照時失足墜崖辭世的荒船山","by":"韋駄天狗 / Wikimedia Commons","lic":"公有領域"},
  body="""<h2>一場沒有回來的登山</h2>
<p>二〇〇九年九月十一日,臼井儀人獨自前往群馬與長野交界的荒船山拍照,途中失足墜崖。九天後,人們在山下尋獲他的遺體,享年五十一歲。畫了二十餘年那個屁股外露、天真闖禍的五歲小孩的人,就這樣走了。</p>
<h2>一部沒有結局的漫畫</h2>
<p>連載在故事中途硬生生停下,《蠟筆小新》成了一部未完成的作品。對全世界的讀者來說,那是個措手不及的句點。</p>
<h2>助手們接手,讓小新活下去</h2>
<p>但故事沒有真的結束。二〇一〇年起,幾位曾與臼井並肩工作的助手組成「UY Studio」,由雙葉社以《新蠟筆小新》之名續刊,並始終把臼井儀人列為原作者。那個愛耍寶的小新繼續闖著禍——這是他們讓創作者,以另一種方式留在他最愛的作品裡。</p>
<blockquote>「有些角色一旦被真心愛過,就不會因為畫他的那隻手停下,而跟著停下。」</blockquote>""",
  mao="人走了,筆下的孩子卻被一群捨不得的人接著養大——本編承認,這種事,連向來冷眼的本編都得別過頭去,順便怪罪一下今天的風有點大。",
  sources="自由時報 / Yahoo 新聞報導 · 維基百科 · 雙葉社"),

 dict(slug="tanjiro-earrings-controversy", section="anime", cat="動漫怪談 · Demon Slayer", title="炭治郎的耳飾,為什麼海外版被改掉了?",
  deck="《鬼滅之刃》炭治郎耳上那對花牌耳飾,是全作的招牌。但它原始的『旭日』圖樣,在海外掀起爭議——最後,被改了。",
  keywords="鬼滅之刃 耳飾 爭議,炭治郎 耳環 旭日旗,花牌耳飾,Demon Slayer earrings,海外版 修改",
  meta=[("原始圖樣","紅日放射 + 山"),("爭議","神似旭日旗"),("處理","中韓版改為藍色橫線")], sym="il-anime-masks",
  img={"file":"Hanafuda Koi-Koi Setup 1.jpg","alt":"日本傳統花牌,炭治郎耳飾圖樣的原型","by":"Marcus Richert / Wikimedia Commons","lic":"CC BY"},
  body="""<h2>招牌耳飾的原始圖樣</h2>
<p>炭治郎的花牌耳飾,是《鬼滅之刃》最好認的符號之一。它原始的設計,是一顆紅日、向外放射光芒,下方襯著一座山——而這放射狀的紅日,視覺上,與日本舊時的「旭日旗」相當神似。</p>
<h2>為什麼有人看了不舒服</h2>
<p>旭日旗在曾遭日本戰時佔領的國家——中國、韓國等地——帶著沉重的歷史記憶,讓人聯想到戰爭與傷痛。因此當作品紅遍亞洲,這對耳飾的圖樣,在部分地區(尤其韓國)引發了反彈。</p>
<h2>於是海外版改了設計</h2>
<p>製作方選擇主動處理:在中國與韓國發行的版本裡,把紅日的放射光芒,改成了四條藍色橫線,山的部分維持不變;日本本土與多數市場,則保留原始設計。一件招牌道具,為了歷史的重量而被動了刀——這在動漫界並不常見。</p>
<blockquote>「一枚小小的耳飾,能裝下一整段沒被遺忘的歷史;而願不願意為它改一筆,是另一回事。」</blockquote>""",
  mao="為了一段別人的傷痛,肯把自己招牌的圖樣改掉——這份體貼,本編給過。體貼這種事,從來不是誰欠誰,而是看得見的人,願不願意多走一步。",
  sources="ScreenRant · Bounding Into Comics · 各地媒體報導"),

 dict(slug="lavender-town-syndrome", section="anime", cat="動漫怪談 · Pokémon", title="紫苑鎮的配樂真的害死過小孩嗎?",
  deck="傳說寶可夢紅綠版『紫苑鎮』的配樂,藏著大人聽不見的高頻,害得上百名日本孩童尋短。這故事很有名——也完全是編出來的。",
  keywords="紫苑鎮 配樂,Lavender Town Syndrome,寶可夢 都市傳說,creepypasta,紫苑鎮 真相",
  meta=[("傳說","高頻害死上百孩童"),("真相","2010 年網路杜撰"),("借殼","1997 真實癲癇事件")], sym="il-anime-music",
  img={"file":"Game-Boy-Original.jpg","alt":"初代 Game Boy,寶可夢紅綠版的遊玩主機","by":"Wikimedia Commons","lic":"公有領域"},
  body="""<h2>那則毛骨悚然的傳說</h2>
<p>傳說是這樣的:一九九六年寶可夢紅綠版在日本上市後,「紫苑鎮」那段陰森的配樂裡,藏著只有孩童聽得見的高頻與雙耳節拍,導致上百名日本兒童在那年春天尋短;據說國際版因此把音樂重新編過,「以免再出人命」。</p>
<h2>真相:它是一則網路鬼故事</h2>
<p>這一切,全是虛構的。這故事是二〇一〇年前後,一則匿名貼到 Pastebin、4chan 的「creepypasta」(網路都市傳說),根本沒有什麼兒童死亡潮。唯一沾點邊的事實是:紫苑鎮(遊戲裡的鬼城)的配樂,本來就寫得不和諧、聽著發毛,而它的旋律確實在後續版本裡被調整過——但那是硬體與版本的尋常原因,不是什麼致命頻率。</p>
<h2>它借了一件真事的殼</h2>
<p>這則傳說之所以嚇人,是因為它偷偷借用了一件真事的外殼:一九九七年,寶可夢動畫某一集的強烈閃光,真的讓數百名觀眾癲癇送醫(見〈讓數百人送醫的那一集寶可夢〉)。真實的事件,加上虛構的傳說,被網路縫成了一個看似成立的鬼故事。</p>
<blockquote>「最好騙的謠言,從不是憑空捏造的;而是往一件真事上,輕輕縫一句假話。」</blockquote>""",
  mao="一段音樂被說成能取人性命,傳了十幾年還有人信——各位,這才是真正的恐怖:不是那段旋律,而是人有多想相信一個嚇人的故事。本編聽了,只想再睡一下。",
  sources="Wikipedia / Lavender Town · Creepypasta 考據 · The Gamer"),

 dict(slug="life-size-gundam", section="anime", cat="動漫冷知識 · Gundam", title="日本街頭那尊十八公尺鋼彈,名字到底什麼意思?",
  keywords="實物大鋼彈,Gundam 名字 由來,獨角獸鋼彈,台場,橫濱 會動的鋼彈,Gundam 意思",
  deck="日本先後在橫濱與台場,立起了實物大、甚至會動的鋼彈——高達十八公尺。而「Gundam」這個名字的由來,官方說法居然不只一個。",
  meta=[("實物大","約 18 公尺"),("命名說法","不只一種"),("原企畫名","Freedom Fighter")], sym="il-anime-game",
  img={"file":"Life-Sized Unicorn Gundam Statue.jpg","alt":"矗立在台場的實物大獨角獸鋼彈立像","by":"Wikimedia Commons","lic":"CC0"},
  body="""<h2>一尊會動的十八公尺鋼彈</h2>
<p>動畫裡的巨大機器人,在日本真的被立了出來:橫濱曾有一尊約十八公尺、還會動的實物大鋼彈,台場也矗立過獨角獸鋼彈——都是你能親自站到腳邊、抬頭仰望的鋼鐵巨人。它們早已不只是玩具,而是城市地標。</p>
<h2>「Gundam」到底什麼意思</h2>
<p>而這個名字的由來,官方的說法其實疊了好幾層:一是故事裡,這些機體用一種輕又硬的合金「鋼彈尼姆」(Gundarium)打造,名字取自材料;二是企畫初期,本作曾叫《Freedom Fighter Gunboy》,滿是「自由(freedom)」的字眼——連母艦都叫「自由的堡壘」;三是導演富野由悠季的意象:一具能像水壩(dam)一樣,擋下敵人槍炮(gun)的機器人——gun + dam。你喜歡哪個都行,因為官方三個都講過。</p>
<h2>從玩具,長成一座地標</h2>
<p>一部一九七九年的機器人動畫,四十多年後,它的主角以一比一的姿態,站進了現實的城市天際線。這大概是任何虛構角色,都夢寐以求的成真方式。</p>
<blockquote>「一個好名字,有時不必只有一個由來;它可以同時是材料、是理想,也是一個擋在你面前的溫柔的固執。」</blockquote>""",
  mao="一具十八公尺、還會動的機器人站在街頭給人仰望——本編懂那種存在感。畢竟本編往桌子中央一坐,全家的視線與工作,也都得繞著本編重新規劃。體型不同,道理相通。",
  sources="The Gundam Wiki · 富野由悠季 訪談整理 · 各地實物大鋼彈報導"),

 dict(slug="missingno-glitch", section="anime", cat="動漫冷知識 · Pokémon", title="寶可夢裡那隻不該存在的怪:缺號",
  keywords="缺號,MissingNo,寶可夢 bug,紅綠版 glitch,無限道具,老人 glitch,複製稀有道具",
  deck="寶可夢紅綠版裡,有一隻不該存在的「怪物」:牠叫『缺號』(MissingNo.),是遊戲史上最有名的 bug——而且,還能幫你變出無限稀有道具。",
  meta=[("名稱","MissingNo.(缺號)"),("成因","戰鬥程式沒被重設"),("副作用","第 6 格道具 +128")], sym="il-anime-game",
  img={"file":"Game-Boy-FL.jpg","alt":"初代 Game Boy,缺號 bug 出沒的寶可夢紅綠版主機","by":"Wikimedia Commons","lic":"公有領域"},
  body="""<h2>一隻不該存在的寶可夢</h2>
<p>在寶可夢紅、綠、藍版裡,有一隻叫「MissingNo.」(缺號,意即「缺少編號」)的東西:一團亂碼般的怪物,是電玩史上最出名的 bug。牠本不該存在,卻被無數玩家親眼撞見。</p>
<h2>牠是怎麼跑出來的</h2>
<p>成因藏在一段程式裡:遊戲開頭那位「老人」示範抓寶時,會暫時用他的資料覆蓋你的,並借用亂數遭遇的程式,把你的名字暫存起來。等你之後飛到紅蓮島、沿著海岸衝浪,那段海岸沒有定義該出現哪隻寶可夢——於是戰鬥程式一直沒被重設,遊戲便把殘留在記憶體裡的東西(你名字的字母)硬讀成一隻寶可夢。缺號,就這麼被「叫」了出來。</p>
<h2>還能變出無限道具</h2>
<p>遇到牠會讓畫面花掉,但也會讓你背包裡「第六格道具」的數量,憑空 +128——玩家因此拿它來複製稀有糖果、大師球這類珍稀道具。一個 bug 能被玩家愛成這樣、還幫著把遊戲的傳說愈養愈大,大概也只有牠了。</p>
<blockquote>「有時候,一個系統最迷人的地方,不是它做對的部分,而是它出錯時,不小心露出的那一角。」</blockquote>""",
  mao="一隻因為程式沒收好而蹦出來的亂碼怪,還能生出無限道具——本編對這種「錯誤帶來的意外好處」深有同感。就像本編打翻的每一個杯子,都替你重新定義了一次地心引力。",
  sources="Wikipedia / MissingNo. · IGN · GameFAQs 考據"),

 dict(slug="astro-boy-birthday", section="anime", cat="動漫冷知識 · Astro Boy", title="日本替一個虛構機器人,辦了戶籍",
  keywords="原子小金剛 生日,阿童木 2003年4月7日,手塚治虫,高田馬場,鐵臂阿童木,新座市 戶籍",
  deck="手塚治虫筆下的原子小金剛,在設定裡誕生於二〇〇三年四月七日。而當那一天真的到來,日本是玩真的——真的替一個虛構角色,辦了戶籍。",
  meta=[("角色","原子小金剛(阿童木)"),("設定生日","2003.4.7"),("出生地","高田馬場")], sym="il-anime-manga",
  body="""<h2>一個寫在故事裡的生日</h2>
<p>在手塚治虫的設定裡,原子小金剛(阿童木)「出生」於二〇〇三年四月七日,誕生地是東京的高田馬場。這本來只是漫畫裡的一行設定——直到那個未來的日期,真的走到了眼前。</p>
<h2>那一天,日本玩真的</h2>
<p>二〇〇三年四月七日到來時,日本認真地替他慶生:埼玉縣新座市正式把阿童木登記為市民,發給他一張居民登記卡(監護人欄填的是御茶水博士);東京新宿區聘他當「未來大使」;日本郵政還在高田馬場郵局,推出僅此一天的紀念郵戳。一個虛構角色,就這樣被寫進了真實城市的公文裡。</p>
<h2>連車站都替他響起音樂</h2>
<p>被設定為他「出生地」的 JR 高田馬場站,更把《原子小金剛》的主題曲,設成了電車發車的提示音樂——至今仍在月台上響著。一個手塚筆下的機器少年,就這樣同時活進了一座城市的戶籍簿,和它的聲音裡。</p>
<blockquote>「當一個虛構的角色被愛到這種地步,連現實,都願意挪出一格戶籍,把他當成真的。」</blockquote>""",
  mao="替一個機器人辦戶籍、還讓車站替他放音樂——人類對自己創造、又深愛的東西,總是溫柔得毫無道理。本編懂,因為本編也是被這樣,毫無道理地愛著的。",
  sources="手塚 Production · 新座市 / 新宿區 公告 · 相關報導"),

 dict(slug="ghibli-museum-no-photos", section="anime", cat="動漫怪談 · Studio Ghibli", title="吉卜力美術館裡,為什麼不准拍照?",
  keywords="吉卜力美術館 禁止拍照,三鷹之森,宮崎駿,迷路的孩子,Ghibli Museum,不准拍照 原因",
  deck="東京三鷹的吉卜力美術館,館內全程禁止拍照。這不是小氣,而是宮崎駿的一個心願:他要你當一次「迷路的孩子」。",
  meta=[("地點","東京 · 三鷹之森"),("館內","禁止拍照/錄影"),("標語","一起來當迷路的孩子")], sym="il-anime-masks",
  img={"file":"Ghibli Museum - GhibliMuseum864.jpg","alt":"東京三鷹之森的吉卜力美術館外觀","by":"Wikimedia Commons","lic":"CC0"},
  body="""<h2>一座不准拍照的美術館</h2>
<p>三鷹之森吉卜力美術館,是全世界宮迷的朝聖地。但一走進館內,你會發現一件事:這裡全程禁止拍照與錄影,只有頂樓花園等戶外區域例外。手機得收起來,相機也一樣。</p>
<h2>因為宮崎駿要你「迷路」</h2>
<p>這規矩,直接連著美術館的核心精神。它的標語是「一起來當迷路的孩子吧」(迷子になろうよ,いっしょに)。宮崎駿的想法是:當你忙著隔著鏡頭拍照,就等於把眼前的世界,退到了螢幕後面——你不再真正在場。他要人放下相機,用自己的眼睛、自己的腳步,在館裡自由地迷路、亂走、亂看,親身把這個地方「玩」一遍。</p>
<h2>把體驗,留在心裡而不是相簿</h2>
<p>於是「不准拍照」不是限制,而是一種邀請:別急著把回憶存進手機,先讓它,好好地發生在你身上一次。走出美術館,你帶不走一張照片,卻帶得走一整天,只屬於你的迷路。</p>
<blockquote>「有些地方之所以要你收起相機,是因為它想被你記住的方式,是活過一遍,而不是拍過一張。」</blockquote>""",
  mao="要人放下相機、親自去迷路——這心願,本編舉四隻腳贊成。畢竟本編一輩子都在示範:最好的風景,是你追著本編滿屋子跑時,那些你根本來不及拍下的瞬間。",
  sources="吉卜力美術館官方 · 宮崎駿 相關訪談 · 各地報導"),

 dict(slug="rumiko-takahashi-wealth", section="anime", cat="動漫冷知識 · Manga", title="她靠畫漫畫,成了日本最富有的漫畫家之一",
  keywords="高橋留美子,最富有的漫畫家,漫畫女王,亂馬,犬夜叉,福星小子,身價",
  deck="福星小子、亂馬½、犬夜叉——這些跨越好幾個世代的作品,全出自同一個人的筆。而她,也因此成了日本身價最高的漫畫家之一。",
  meta=[("人物","高橋留美子"),("總銷量","逾 2 億 3 千萬冊"),("身價","估約 6–7 千萬美元")], sym="il-anime-manga",
  img={"file":"Rumiko Takahasi Portrait.png","alt":"被譽為「漫畫女王」的漫畫家高橋留美子","by":"Nino Gutacker / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>你熟的作品,可能都是她畫的</h2>
<p>《福星小子》《相聚一刻》《亂馬½》《犬夜叉》——這些橫跨好幾個世代、你多半聽過甚至看過的作品,其實出自同一個人:高橋留美子。她從一九七八年的《福星小子》開始,一部接一部地量產長紅之作,人稱「漫畫女王」。</p>
<h2>兩億三千萬冊的重量</h2>
<p>她的作品全球流通超過兩億三千萬冊,是史上最暢銷的作者之一;光《福星小子》在日本就賣了約兩千六百萬冊,《亂馬½》與《犬夜叉》也各有五千五百萬、五千萬冊的成績。這樣的銷量,讓她的身價估計落在六千萬到七千萬美元之間——是日本數一數二富有的漫畫家,也是史上最暢銷的女性漫畫家。</p>
<h2>安靜地,坐在金字塔頂端</h2>
<p>比起許多鋒芒外露的名字,高橋留美子低調得多。但只要把銷量攤開來看就會發現:這位「漫畫女王」的稱號,一點都沒有誇張。</p>
<blockquote>「真正的高產不是曇花一現,而是四十年來,一部接著一部,讓好幾代人都在她畫的世界裡,長大過。」</blockquote>""",
  mao="一支筆養活好幾個世代的青春,還順便坐上身價金字塔頂端——本編對這種「安靜地厲害」深表敬意。畢竟本編也一樣:看起來只是在睡,實際上,整個家都是本編在經營。",
  sources="Wikipedia / Rumiko Takahashi · CBR · ScreenRant"),

 dict(slug="pikachu-name-origin", section="anime", cat="動漫冷知識 · Pokémon", title="「皮卡丘」這名字,其實是兩個狀聲詞",
  keywords="皮卡丘 名字 由來,Pikachu 意思,ぴかぴか,ちゅう,狀聲詞,寶可夢 命名",
  deck="皮卡丘紅遍全球,但很少人知道:牠的名字根本不是「取」的,而是「聽」出來的——由兩個日文狀聲詞拼成。",
  meta=[("ピカ","閃電/發光聲"),("チュウ","老鼠叫聲"),("合起來","會放電的老鼠")], sym="il-anime-game",
  body="""<h2>一個聽出來的名字</h2>
<p>皮卡丘(Pikachu)是全世界最有名的寶可夢,但牠的名字其實不是憑空取的,而是由兩個日文狀聲詞拼起來的——一個管「電」,一個管「鼠」。</p>
<h2>ピカ + チュウ</h2>
<p>前半的「ピカ」(pika),是日文裡形容閃電、發光、亮晶晶的狀聲詞,就像中文的「啪」一道電光、或英文的「zap」;後半的「チュウ」(chu),則是日文裡老鼠的叫聲,相當於中文的「吱吱」。兩個一拼,「皮卡丘」直白地說,就是「一隻會啪啪放電的吱吱鼠」——牠的屬性與外型,全寫在名字裡了。</p>
<h2>那隻叫「鼠兔」的動物,只是巧合</h2>
<p>順帶一提:高山上有種毛茸茸的小動物,中文正好叫「鼠兔」、英文叫「pika」,和皮卡丘名字撞得剛好。但據說這純屬巧合——皮卡丘的靈感與命名,走的是狀聲詞這條路,並不是那隻小獸。</p>
<blockquote>「最好記的名字,有時不必有什麼深意——它只要,像它本來的聲音。」</blockquote>""",
  mao="名字直接由「放電聲」加「老鼠叫」組成——本編欣賞這種坦白。若照這規矩替本編命名,大概會叫「呼嚕吼」:一半是滿足的呼嚕,一半是你敢動本編罐罐時的低吼。",
  sources="Behind the Name · 寶可夢命名考據 · Bulbapedia"),

 dict(slug="kitaro-mizuki-road", section="anime", cat="動漫怪談 · GeGeGe no Kitaro", title="日本有一條街,站著一百七十七尊妖怪",
  keywords="水木茂之路,鬼太郎,境港市,妖怪銅像,水木しげる,GeGeGe no Kitaro,鳥取",
  deck="日本鳥取縣境港市,有一條八百公尺長的街,站著一百七十七尊青銅妖怪。這是漫畫家水木茂的故鄉——他把一整條街,還給了妖怪。",
  meta=[("地點","鳥取 · 境港市"),("長度","約 800 公尺"),("妖怪銅像","約 177 尊")], sym="il-anime-ghost",
  body="""<h2>一條住滿妖怪的街</h2>
<p>從 JR 境港站走到水木茂紀念館,是一條約八百公尺長的「水木茂之路」。沿途,一百七十七尊青銅妖怪一字排開——鬼太郎、眼球老爹、貓女……全是從《鬼太郎》裡走出來的日本妖怪,站在街邊,陪你一路走進那個陰森又可愛的世界。</p>
<h2>妖怪漫畫之神的故鄉</h2>
<p>這裡是漫畫家水木茂的出生地。他被尊為「妖怪漫畫的宗師」,一手把《鬼太郎》與滿天神佛般的日本妖怪畫進了大眾記憶。這條路一九九三年開通,二〇一八年大改造後,銅像數量比最初足足多了七倍。</p>
<h2>把故鄉,還給了妖怪</h2>
<p>整座小鎮都跟著入戲:有供奉妖怪的「妖怪神社」、有九尾妖怪出沒的河童泉。一位漫畫家的故鄉,就這樣被改造成一封立體的情書——寫給他畫了一輩子的那些妖怪。</p>
<blockquote>「有些人一生都在畫看不見的東西;而他的故鄉,乾脆把它們,一尊尊立成了看得見的樣子。」</blockquote>""",
  mao="一整條街都是妖怪銅像,入夜想必格外熱鬧——本編倒覺得親切。畢竟本編半夜在家裡橫衝直撞、對著空氣哈氣的模樣,人類八成也當成看見了什麼妖怪。",
  sources="境港市觀光協會 · Fun Japan · Atlas Obscura"),

 dict(slug="spirited-away-oscar", section="anime", cat="動漫冷知識 · Studio Ghibli", title="唯一一部拿下奧斯卡的手繪動畫",
  keywords="神隱少女 奧斯卡,千與千尋 Academy Award,唯一手繪 得獎,宮崎駿,Spirited Away,2003",
  deck="《神隱少女》是史上唯一一部,以純手繪之姿拿下奧斯卡最佳動畫長片的電影。二十多年過去,這個紀錄,至今沒有人打破。",
  meta=[("作品","神隱少女(2001)"),("奧斯卡","2003 最佳動畫長片"),("紀錄","唯一手繪得主")], sym="il-anime-masks",
  body="""<h2>一座至今無人超越的獎</h2>
<p>二〇〇三年第七十五屆奧斯卡,《神隱少女》拿下最佳動畫長片。而直到今天,它仍是唯一一部以純手繪奪下這座獎的作品——在它之後的所有得主,清一色是電腦動畫。它同時也是史上第一部拿下此獎的非美國電影,更是至今唯一一部、由北美與歐洲以外的工作室製作的得主。</p>
<h2>他甚至沒去領獎</h2>
<p>更耐人尋味的是,宮崎駿本人並沒有出席頒獎典禮——據說是為了抗議當時的伊拉克戰爭。他缺席了,獎,卻照樣頒給了他。</p>
<h2>它推開了一扇門</h2>
<p>這部約一千九百萬美元成本的電影(其中一成由負責美國發行與英語配音的迪士尼分攤),全球票房約兩億七千五百萬美元,更蟬聯日本影史票房冠軍近二十年。它的得獎,把日本動畫正式推進了西方主流,也讓全世界開始把「動畫」當成一門正經的藝術看待。</p>
<blockquote>「有些門,是一部作品用實力踹開的;推開之後,後來的人,才走得進去。」</blockquote>""",
  mao="拿了全世界最風光的獎,本人卻為了理念,連去都不去——本編對這種姿態,是真心佩服。畢竟能對著到手的鎂光燈掉頭就走的,除了宮崎駿,大概就只有被叫來拍照的本編了。",
  sources="Hollywood Reporter · Britannica · 奧斯卡官方"),

 dict(slug="anpanman-most-characters", section="anime", cat="動漫冷知識 · Anpanman", title="麵包超人,是登場角色最多的動畫",
  keywords="麵包超人,麵包超人 金氏紀錄,最多角色 動畫,柳瀨嵩,Anpanman,1768",
  deck="麵包超人保持著一項金氏世界紀錄:登場角色最多的動畫。到二〇〇九年統計,已經有一千七百六十八個——而且,還在繼續增加。",
  meta=[("作品","麵包超人"),("金氏紀錄","最多角色動畫"),("數量","1,768(2009)")], sym="il-anime-manga",
  img={"file":"Kami Kochi Yanase Takashi Memorial Hall.jpg","alt":"麵包超人作者柳瀨嵩的紀念館","by":"京浜にけ / Wikimedia Commons","lic":"CC BY-SA"},
  body="""<h2>一千七百六十八個角色</h2>
<p>麵包超人握著一項有點好笑的金氏世界紀錄:登場角色最多的動畫。截至二〇〇九年六月的統計,已經有一千七百六十八個不同角色——這還只是前九百八十集電視動畫,加上前二十部劇場版而已,而且數字至今仍在增加。</p>
<h2>連作者都嚇一跳</h2>
<p>創作者柳瀨嵩從一九六八年開始畫麵包超人(電視動畫則自一九八八年開播)。據說,對這項紀錄最感到吃驚的人,正是他自己。這些角色大多以食物為主題——果醬、奶油、各式各樣的麵包——一個接一個地誕生。</p>
<h2>為什麼要那麼多角色</h2>
<p>麵包超人的觀眾,是年紀很小的孩子;那源源不絕、造型簡單又貼近生活的食物角色,正是它的魅力與長壽的祕訣。柳瀨嵩已於二〇一三年辭世,但他留下的這支龐大隊伍,至今仍在螢幕上,替一代又一代的孩子送去麵包。</p>
<blockquote>「有時候,偉大不是把一個角色畫到極致,而是溫柔到,願意替上千個小東西,都認真取一個名字。」</blockquote>""",
  mao="一千七百多個角色,還大多是食物——本編光是想像那個場面,肚子就先餓了。不過話說回來,把善良畫成一個個能吃的麵包分給孩子,這份溫柔,連本編都不忍心吐槽。",
  sources="Guinness World Records · Anime News Network · Japan Times"),
]

# ============================================================
# 3. 模板
# ============================================================
def esc(s): return html.escape(s, quote=True)

def img_url(file, w=1200):
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + file.replace(" ", "%20") + "?width=%d" % w

# 品牌 favicon:琥珀底 + 黑貓坐姿剪影 + 綠眼(用站內 cat 造型)
FAVICON_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
  "<rect width='100' height='100' rx='22' fill='#F5A623'/>"
  "<g transform='translate(20,16) scale(0.5)'>"
  "<path fill='#141210' d='M30 44 C31 34 32 30 34 27 L30 6 L47 23 C49 22 51 22 53 22 L61 5 L67 25 C71 31 75 41 79 57 C84 81 85 105 83 123 C82 129 81 130 79 130 L46 130 C44 130 44 128 44 122 L44 98 C43 84 40 70 36 58 C33 50 31 47 30 44 Z'/>"
  "<path fill='#141210' d='M74 124 C97 128 109 111 104 95 C101 87 91 88 92 99 C95 109 87 117 73 112 Z'/>"
  "<ellipse fill='#93A83A' cx='38' cy='33' rx='3.4' ry='4.6'/>"
  "</g></svg>")
FAVICON_HREF = "data:image/svg+xml," + urllib.parse.quote(FAVICON_SVG)

def head(title, desc, url, image=None, typ="website", jsonld="", keywords=""):
    og_src = image if image else (BASE + "/og.png")   # 無專屬圖時,退回站級分享卡
    og_img = '<meta property="og:image" content="%s">' % esc(og_src)
    kw = ('<meta name="keywords" content="%s">\n' % esc(keywords)) if keywords else ""
    return f"""<!doctype html><html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{kw}<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="{typ}"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(url)}">
<meta property="og:site_name" content="{esc(SITE)}"><meta property="og:locale" content="zh_TW">{og_img}
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{esc(og_src)}">
<link rel="icon" href="{FAVICON_HREF}">
{ADSENSE_HEAD}
<link rel="stylesheet" href="{{css}}">
{jsonld}
</head><body>
<canvas id="motes"></canvas>
<header class="topbar"><div class="wrap">
<a class="brand" href="{{home}}">{CAT_MINI}怪奇檔案</a>
<nav class="tnav"><a href="{{home}}#curios">奇聞</a><a href="{{home}}#stories">夜話</a><a href="{{about}}">關於</a>
<button class="tgl" id="themebtn">日／夜</button></nav>
</div></header>
<div class="page">"""

FOOT = """</div>
<script src="{js}"></script></body></html>"""

CAT_MINI = '<svg viewBox="0 -4 100 132" aria-hidden="true"><use href="#cat"/></svg>'

def figure(a, big=True):
    if a.get('img'):
        w = 1200 if big else 600
        return f"""<figure class="photo">
<img src="{esc(img_url(a['img']['file'],w))}" alt="{esc(a['img']['alt'])}" loading="lazy"
 onerror="this.closest('figure').classList.add('noimg')">
<div class="fallback"><svg viewBox="0 0 480 260"><use href="#{a['sym']}"/></svg></div>
<figcaption><b>圖 ／</b> {esc(a['img']['alt'])}　·　{esc(a['img']['by'])} / {esc(a['img']['lic'])}</figcaption>
</figure>"""
    return f"""<figure class="photo noimg">
<div class="fallback"><svg viewBox="0 0 480 260"><use href="#{a['sym']}"/></svg></div>
<figcaption><b>插圖 ／</b> 貓編手繪</figcaption>
</figure>"""

def render_page(html_body, **kw):
    return (kw['head'] + DEFS + html_body + FOOT).replace("{css}", kw['css']).replace(
        "{js}", kw['js']).replace("{home}", kw['home']).replace("{about}", kw['about']).replace("{priv}", kw.get('priv', 'privacy.html'))

# ---- index ----
def _thumb(a):
    if a.get('img'):
        return f"""<img src="{esc(img_url(a['img']['file'],600))}" alt="{esc(a['img']['alt'])}" loading="lazy"
 onerror="this.outerHTML='&lt;svg viewBox=\\'0 0 480 260\\'&gt;&lt;use href=\\'#{a['sym']}\\'/&gt;&lt;/svg&gt;'">"""
    return f"""<svg viewBox="0 0 480 260"><use href="#{a['sym']}"/></svg>"""

def _card(a, i):
    cat = a['cat'].partition(" · ")[0]
    return f"""<a class="card" href="curiosa/{a['slug']}.html">
<div class="thumb">{_thumb(a)}</div>
<div class="in"><div class="top"><span class="cat">{esc(cat)}</span><span class="idx">{i:02d}</span></div>
<h3>{esc(a['title'])}</h3><p>{esc(a['deck'][:70])}…</p><span class="more">閱讀全文 →</span></div></a>"""

HOME_CURIOS = 9   # 首頁「本期精選」顯示的世界奇聞篇數,其餘進 all-curios.html
HOME_ANIME = 9    # 首頁動漫區顯示篇數,其餘進 all-anime.html
HOME_STORIES = 8  # 首頁夜話顯示則數,其餘進 all-stories.html

def _stories_html(items):
    out = ""
    for no, t, lines in items:
        ps = "".join("<p>%s</p>" % esc(l) for l in lines)
        out += f'<article class="story"><div class="no">{esc(no)}</div><h3>{esc(t)}</h3>{ps}</article>'
    return out

def _seemore(href, label):
    return f'<div class="seemore"><a href="{href}">{esc(label)} <span>→</span></a></div>'

def build_index():
    ticker = "".join("<span>%s</span>" % esc(t) for t in TICKER)
    curios = [a for a in ARTICLES if a.get('section', 'curio') == 'curio']
    animes = [a for a in ARTICLES if a.get('section') == 'anime']
    curio_cards = "".join(_card(a, i) for i, a in enumerate(curios[:HOME_CURIOS], 1))
    curio_more = _seemore("all-curios.html", f"看更多怪聞(全 {len(curios)} 篇)") if len(curios) > HOME_CURIOS else ""
    anime_cards = "".join(_card(a, i) for i, a in enumerate(animes[:HOME_ANIME], 1))
    anime_more = _seemore("all-anime.html", f"看更多動漫怪談(全 {len(animes)} 篇)") if len(animes) > HOME_ANIME else ""
    anime_section = ("" if not animes else f"""
<div class="shead" id="anime"><div class="htitle"><svg class="shead-cat" viewBox="0 0 158 118"><use href="#cat-roll"/></svg><h2>動漫怪談・冷知識</h2></div><span class="en">Anime Curiosities</span></div>
<section class="grid">{anime_cards}</section>{anime_more}""")
    stories = _stories_html(STORIES[:HOME_STORIES])
    story_more = _seemore("all-stories.html", f"看更多夜話(全 {len(STORIES)} 則)") if len(STORIES) > HOME_STORIES else ""
    jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite",'
              '"name":"%s","url":"%s/"}</script>' % (SITE, BASE))
    h = head(f"{SITE} — 貓眼看世界", TAGLINE, BASE + "/", typ="website", jsonld=jsonld)
    body = f"""
<div class="masthead wrap">
<svg class="catmark" aria-label="怪奇檔案標誌"><use href="#cat"/></svg>
<div class="kick">A Cat's-Eye Field Guide to the Strange</div>
<h1>怪奇檔案</h1>
<div class="tag">世界各地<em>真實</em>卻難以置信的事物 — 由一隻中年黑貓精選、查證、順便吐槽。</div></div>
<div class="ticker"><div class="wrap"><div class="lbl"><svg viewBox="0 -4 100 132"><use href="#cat"/></svg> 貓編速報</div>
<div class="items" id="tick">{ticker}</div></div></div>
<main class="wrap" id="curios">
<div class="shead"><div class="htitle"><svg class="shead-cat" viewBox="0 0 178 118"><use href="#cat-stand"/></svg><h2>本期精選奇聞</h2></div><span class="en">Verified Curiosities</span></div>
<section class="grid">{curio_cards}</section>{curio_more}{anime_section}</main>
<div class="catplay-band"><div class="wrap">{CATPLAY}
<p class="say">翻到這裡,本編陪你玩夠了。接下來這幾則,是寫給睡不著的人看的——</p></div></div>
<section class="stories" id="stories"><div class="wrap">
<div class="head"><div class="glow"><i></i><i></i></div><div class="eyebrow">After-Hours Fiction</div>
<h2>貓編夜話</h2><p class="sub">無厘頭極短篇 —— 趁各位熟睡、鍵盤終於安靜的時候,本編寫下的一些不太合理的故事。</p></div>
<div class="story-col">{stories}</div>{story_more}
<div class="rest"><svg viewBox="0 0 160 96"><use href="#cat-loaf"/></svg></div>
<p class="signoff">—— 以上,寫於各位熟睡之後。　貓編</p></div></section>
<div class="wrap"><div class="adslot"><div class="k">廣告版位 · <b>AD SLOT</b> · 728 × 90</div>
<div class="s">通過 AdSense 審核後,把廣告碼貼在這裡即可</div></div></div>
{FOOTER_HTML}
"""
    page = render_page(body, head=h, css="styles.css", js="app.js", home="index.html", about="about.html", priv="privacy.html")
    (OUT / "index.html").write_text(page, encoding="utf-8")

FOOTER_HTML = """<section class="news-band"><div class="wrap">
<div><h3>訂閱貓編電子報</h3><p>每週三,一則世界奇聞 + 一句只有貓看得出來的觀點,送到你信箱。</p></div>
<form class="news-form" onsubmit="return false"><input type="email" placeholder="you@example.com" aria-label="電子郵件"><button>訂閱</button></form>
</div></section>
<footer><div class="wrap footer-grid">
<div class="fcol"><div class="sign"><svg aria-hidden="true"><use href="#cat"/></svg>
<div class="by"><b>貓編</b><span>總編輯 · 中年黑貓</span></div></div>
<p class="fnote"><span class="accent">原創策展,而非搬運。</span>每一則都經本編親自挑選、查證與撰寫,標明原始出處;插圖為手繪,夜話小說全為原創虛構,照片採用 Wikimedia Commons 合法授權並標註來源。</p></div>
<div class="fcol"><h4>分類</h4><ul>
<li><a href="{home}#curios">自然異象</a></li><li><a href="{home}#curios">歷史謎團</a></li>
<li><a href="{home}#curios">科學怪奇</a></li><li><a href="{home}#curios">未解之謎</a></li>
<li><a href="{home}#anime">動漫怪談</a></li><li><a href="{home}#stories">貓編夜話</a></li></ul></div>
<div class="fcol"><h4>關於本刊</h4><ul>
<li><a href="{about}">關於怪奇檔案</a></li><li><a href="{about}">投稿與聯絡</a></li>
<li><a href="{priv}">隱私權政策</a></li></ul></div>
</div>
<div class="wrap fbar"><span>© 2026 怪奇檔案 CURIOSA</span><span>由一隻中年黑貓主編</span></div></footer>"""

# ---- article pages ----
def sidebar(a):
    sec = a.get('section', 'curio')
    more = [x for x in ARTICLES if x['slug'] != a['slug'] and x.get('section', 'curio') == sec]
    more += [x for x in ARTICLES if x['slug'] != a['slug'] and x.get('section', 'curio') != sec]
    lis = "".join('<li><a href="%s.html">%s</a></li>' % (esc(m['slug']), esc(m['title'])) for m in more[:6])
    return f"""<aside class="rail">
<div class="box catcard"><svg aria-hidden="true"><use href="#cat"/></svg><b>貓編</b><span>總編輯 · 中年黑貓</span></div>
<div class="box"><h3>更多怪奇</h3><ul>{lis}</ul></div>
<div class="box"><h3>逛逛分類</h3><div class="chips"><a href="../index.html#curios">自然異象</a><a href="../index.html#curios">科學怪奇</a><a href="../index.html#curios">未解之謎</a><a href="../index.html#anime">動漫怪談</a><a href="../index.html#stories">貓編夜話</a></div></div>
<div class="box adbox">廣告版位<br><b>AD · 300×250</b></div>
</aside>"""

def build_articles():
    (OUT / "curiosa").mkdir(exist_ok=True)
    for i, a in enumerate(ARTICLES):
        url = f"{BASE}/curiosa/{a['slug']}.html"
        img = img_url(a['img']['file']) if a.get('img') else None
        meta = "".join("<span><b>%s</b> %s</span>" % (esc(l), esc(v)) for l, v in a['meta'])
        sec = a.get('section', 'curio')
        pool = [x for x in ARTICLES if x['slug'] != a['slug'] and x.get('section', 'curio') == sec]
        pool += [x for x in ARTICLES if x['slug'] != a['slug'] and x.get('section', 'curio') != sec]
        related = pool[:3]
        rel = "".join('<li><a href="%s.html">%s</a></li>' % (esc(r['slug']), esc(r['title'])) for r in related)
        img_ld = ('"image":"%s",' % esc(img)) if img else ('"image":"%s/og.png",' % BASE)
        jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article",'
                  '"headline":"%s","description":"%s",%s"inLanguage":"zh-Hant",'
                  '"author":{"@type":"Person","name":"貓編","url":"%s/about.html"},'
                  '"publisher":{"@type":"Organization","name":"%s","logo":{"@type":"ImageObject","url":"%s/og.png"}},'
                  '"datePublished":"%s","dateModified":"%s","mainEntityOfPage":"%s"}</script>'
                  % (esc(a['title']), esc(a['deck']), img_ld, BASE, SITE, BASE, TODAY, TODAY, esc(url)))
        crumb_name = "動漫怪談・冷知識" if sec == 'anime' else "本期精選奇聞"
        crumb_url = BASE + ("/all-anime.html" if sec == 'anime' else "/all-curios.html")
        jsonld += ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList",'
                   '"itemListElement":['
                   '{"@type":"ListItem","position":1,"name":"%s","item":"%s/"},'
                   '{"@type":"ListItem","position":2,"name":"%s","item":"%s"},'
                   '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}</script>'
                   % (esc(SITE), BASE, esc(crumb_name), crumb_url, esc(a['title']), esc(url)))
        h = head(f"{a['title']}｜{SITE}", a['deck'][:150], url, image=img, typ="article", jsonld=jsonld, keywords=a.get('keywords', ''))
        cat = esc(a['cat'])
        crumb2 = '<a href="../index.html#anime">動漫怪談</a>' if sec == 'anime' else '<a href="../index.html#curios">本期精選</a>'
        body = f"""<div class="layout">
<article class="post">
<nav class="crumb"><a href="../index.html">怪奇檔案</a> ／ {crumb2} ／ {esc(a['title'])}</nav>
<span class="flag">{cat}</span>
<h1>{esc(a['title'])}</h1>
<p class="deck">{esc(a['deck'])}</p>
<div class="pmeta">{meta}</div>
{figure(a)}
<div class="prose">{a['body']}</div>
<div class="mao"><span class="who"><span class="eyes"><i></i><i></i></span> 貓評</span><p>{esc(a['mao'])}</p></div>
<div class="sources"><b>來源 ／</b> {esc(a['sources'])}</div>
</article>
{sidebar(a)}
</div>
{FOOTER_HTML}"""
        page = (h + DEFS + body + FOOT).replace("{css}", "../styles.css").replace("{js}", "../app.js").replace("{home}", "../index.html").replace("{about}", "../about.html").replace("{priv}", "../privacy.html")
        (OUT / "curiosa" / f"{a['slug']}.html").write_text(page, encoding="utf-8")

# ---- 歸檔頁(看更多)----
def build_archive(fname, section, title, en, intro):
    arts = [a for a in ARTICLES if a.get('section', 'curio') == section]
    cards = "".join(_card(a, i) for i, a in enumerate(arts, 1))
    jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"CollectionPage",'
              '"name":"%s","url":"%s/%s"}</script>' % (esc(title), BASE, fname))
    h = head(f"{title}｜{SITE}", intro, f"{BASE}/{fname}", jsonld=jsonld)
    body = f"""<main class="wrap">
<nav class="crumb" style="margin-top:26px"><a href="index.html">怪奇檔案</a> ／ {esc(title)}</nav>
<div class="shead"><div class="htitle"><svg class="shead-cat" viewBox="0 0 178 118"><use href="#cat-stand"/></svg><h2>{esc(title)}</h2></div><span class="en">{esc(en)}</span></div>
<p class="arch-intro">{esc(intro)}</p>
<section class="grid">{cards}</section>
<div class="seemore"><a href="index.html"><span>←</span> 回首頁</a></div>
</main>
{FOOTER_HTML}"""
    page = render_page(body, head=h, css="styles.css", js="app.js", home="index.html", about="about.html", priv="privacy.html")
    (OUT / fname).write_text(page, encoding="utf-8")

def build_stories_archive():
    total = len(STORIES)
    jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"CollectionPage",'
              '"name":"貓編夜話","inLanguage":"zh-Hant","url":"%s/all-stories.html"}</script>' % BASE)
    intro = "貓編趁各位熟睡、鍵盤終於安靜的時候寫下的無厘頭極短篇,全部收錄於此。"
    h = head(f"貓編夜話 · 全部極短篇｜{SITE}", intro, f"{BASE}/all-stories.html", jsonld=jsonld,
             keywords="貓編夜話,極短篇,微小說,無厘頭,怪奇檔案")
    body = f"""<section class="stories" style="padding-top:18px"><div class="wrap">
<nav class="crumb" style="margin-bottom:6px"><a href="index.html">怪奇檔案</a> ／ 貓編夜話</nav>
<div class="head"><div class="glow"><i></i><i></i></div><div class="eyebrow">After-Hours Fiction</div>
<h2>貓編夜話</h2><p class="sub">{esc(intro)}目前共 {total} 則。</p></div>
<div class="story-col">{_stories_html(STORIES)}</div>
<div class="rest"><svg viewBox="0 0 160 96"><use href="#cat-loaf"/></svg></div>
<div class="seemore"><a href="index.html"><span>←</span> 回首頁</a></div>
</div></section>
{FOOTER_HTML}"""
    page = render_page(body, head=h, css="styles.css", js="app.js", home="index.html", about="about.html", priv="privacy.html")
    (OUT / "all-stories.html").write_text(page, encoding="utf-8")

# ---- 404 ----
def build_404():
    h = head(f"找不到這一頁 · 404｜{SITE}", "貓編也找不到這一頁——不如回頭看看那些確實存在卻難以置信的事。", BASE + "/404.html")
    body = f"""<main class="wrap" style="text-align:center;padding:86px 0 60px">
<svg viewBox="0 0 130 130" style="width:150px;height:auto;color:var(--ink);margin:0 auto;display:block"><use href="#cat-roll"/></svg>
<div style="font-family:var(--mono);letter-spacing:.3em;text-transform:uppercase;color:var(--accent);margin-top:24px;font-size:13px">Error 404</div>
<h1 style="font-family:var(--serif);font-weight:700;font-size:clamp(32px,7vw,58px);margin:12px 0 10px">這一頁,貓編也找不到</h1>
<p style="color:var(--muted);max-width:46ch;margin:0 auto 32px;line-height:1.7">也許它被歸檔進了某個睡著的抽屜,也許它從來就不存在。不如回頭,看看那些<em style="color:var(--accent);font-style:normal">確實存在、卻難以置信</em>的事。</p>
<div class="seemore"><a href="/index.html"><span>&larr;</span> 回首頁</a></div>
</main>
{FOOTER_HTML}"""
    page = (h + DEFS + body + FOOT).replace("{css}","/styles.css").replace("{js}","/app.js").replace("{home}","/index.html").replace("{about}","/about.html").replace("{priv}","/privacy.html")
    (OUT / "404.html").write_text(page, encoding="utf-8")

# ---- about / privacy ----
def simple_page(fname, title, body_html):
    url = f"{BASE}/{fname}"
    h = head(f"{title}｜{SITE}", title, url)
    body = f'<main class="wrap"><div class="post" style="padding-top:30px">{body_html}</div></main>{FOOTER_HTML}'
    page = (h + DEFS + body + FOOT).replace("{css}","styles.css").replace("{js}","app.js").replace("{home}","index.html").replace("{about}","about.html").replace("{priv}","privacy.html")
    (OUT / fname).write_text(page, encoding="utf-8")

# ---- sitemap / robots ----
def build_meta():
    urls = [(BASE + "/", "1.0", "daily"),
            (BASE + "/all-curios.html", "0.7", "weekly"),
            (BASE + "/all-anime.html", "0.7", "weekly"),
            (BASE + "/all-stories.html", "0.7", "weekly"),
            (BASE + "/about.html", "0.4", "monthly"),
            (BASE + "/privacy.html", "0.2", "yearly")]
    urls += [(f"{BASE}/curiosa/{a['slug']}.html", "0.8", "monthly") for a in ARTICLES]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u, pri, freq in urls:
        sm += f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{freq}</changefreq><priority>{pri}</priority></url>\n"
    sm += "</urlset>\n"
    (OUT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    if ADSENSE_PUB:
        (OUT / "ads.txt").write_text("google.com, %s, DIRECT, f08c47fec0942fa0\n" % ADSENSE_PUB.replace("ca-", ""), encoding="utf-8")

# ============================================================
# 4. 執行
# ============================================================
OUT.mkdir(exist_ok=True)
(OUT / "styles.css").write_text(CSS, encoding="utf-8")
(OUT / "app.js").write_text(JS, encoding="utf-8")
(OUT / "og.png").write_bytes((pathlib.Path(__file__).parent / "assets" / "og.png").read_bytes())  # 站級分享卡
# Google Search Console 網站擁有權驗證檔(驗證後仍需保留)
(OUT / "google041712966e26603e.html").write_text("google-site-verification: google041712966e26603e.html\n", encoding="utf-8")
build_index()
build_404()
build_articles()
build_archive("all-curios.html", "curio", "全部怪聞", "All Curiosities",
  "貓編至今蒐集、查證的世界奇聞,全在這裡——真實卻難以置信的事物,一次看個夠。")
build_stories_archive()
build_archive("all-anime.html", "anime", "全部動漫怪談・冷知識", "All Anime Curiosities",
  "動漫的都市傳說、幕後怪談與冷知識,由本編看電視看出來的門道。")
simple_page("about.html", "關於怪奇檔案",
  """<h1>關於怪奇檔案</h1><p class="deck">世界很大,但沒必要親自去。</p>
<div class="prose"><p>《怪奇檔案》蒐集世界各地真實卻難以置信的事物,由總編輯「貓編」——一隻中年黑貓——親自挑選、查證、撰寫,並附上一句只有貓看得出來的觀點。</p>
<p><b>我們的原則:</b>原創策展,而非搬運。每一篇都重新查證與撰寫,標明原始出處;插圖為手繪,夜話小說全為原創虛構,照片採用 Wikimedia Commons 等合法授權來源並標註作者。我們不整篇轉貼、不機器洗稿。</p>
<p><b>聯絡:</b>投稿、勘誤或合作,歡迎來信 <a href="mailto:saeg300155@gmail.com">saeg300155@gmail.com</a>。</p></div>""")
simple_page("privacy.html", "隱私權政策",
  """<h1>隱私權政策</h1><div class="prose">
<p>本網站尊重您的隱私。以下說明我們如何處理資料(上線前請依實際使用的服務調整)。</p>
<h2>Cookie 與第三方廣告</h2><p>本站可能使用 Google AdSense 等第三方廣告服務。這些服務可能使用 Cookie,依據您的造訪紀錄放送個人化廣告。您可至 Google 廣告設定停用個人化廣告。</p>
<h2>分析工具</h2><p>本站可能使用 Google Analytics 等工具了解流量,資料以匿名彙總形式呈現。</p>
<h2>聯絡我們</h2><p>如對本政策有任何疑問,請來信 <a href="mailto:saeg300155@gmail.com">saeg300155@gmail.com</a>。</p></div>""")
build_meta()
(OUT / "CNAME").write_text(BASE.split("//", 1)[1].rstrip("/") + "\n", encoding="utf-8")  # GitHub Pages 自訂網域
print("OK  ->", OUT)
print("頁面數:", 3 + len(ARTICLES), " (index + about + privacy +", len(ARTICLES), "篇文章)")
