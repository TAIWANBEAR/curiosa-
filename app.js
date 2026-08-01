
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
