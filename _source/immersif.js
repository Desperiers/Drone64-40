/* Drone 64-40 — mode immersif (accueil + pages métiers). Sans dépendance. */
(function(){
var d=document,R=d.documentElement,W=window;
var calm=W.matchMedia('(prefers-reduced-motion: reduce)').matches;
R.classList.add('imm-js');
var nav=d.querySelector('header.nav');
function navh(){if(nav)R.style.setProperty('--navh',nav.offsetHeight+'px');}
navh();

/* ---- Hero : diaporama, télémétrie, parallaxe ---- */
var hero=d.querySelector('[data-hero]');
if(hero){
  var slides=[].slice.call(hero.querySelectorAll('.slide')),bars=[].slice.call(hero.querySelectorAll('.reel [data-go]'));
  var pp=hero.querySelector('.reel .pp'),tc=hero.querySelector('[data-tc]'),altE=hero.querySelector('[data-alt]'),plE=hero.querySelector('[data-place]'),coE=hero.querySelector('[data-coord]');
  var cur=0,timer=null,paused=calm,DUR=7000,alt=0,altT=0,t0=performance.now();
  function load(s){var i=s.querySelector('img[data-src]');if(i){if(i.dataset.srcset)i.srcset=i.dataset.srcset;i.src=i.dataset.src;i.removeAttribute('data-src');}}
  function show(n){
    if(!slides.length)return;
    n=(n+slides.length)%slides.length;var s=slides[n];load(s);
    slides.forEach(function(x,i){x.classList.toggle('on',i===n);});
    bars.forEach(function(b,i){b.classList.toggle('on',i===n);b.classList.toggle('done',i<n);b.setAttribute('aria-current',i===n?'true':'false');});
    /* relancer l'animation de la barre et du zoom */
    var bi=bars[n]&&bars[n].querySelector('i');if(bi){bi.style.animation='none';bi.offsetWidth;bi.style.animation='';}
    var im=s.querySelector('img');if(im){im.style.animation='none';im.offsetWidth;im.style.animation='';}
    cur=n;altT=+(s.dataset.a||0);
    if(plE){plE.style.opacity=0;setTimeout(function(){plE.textContent=s.dataset.p||'';plE.style.opacity=1;},300);}
    if(coE&&s.dataset.c)coE.textContent=s.dataset.c;
    load(slides[(n+1)%slides.length]);
    clearTimeout(timer);if(!paused&&slides.length>1)timer=setTimeout(function(){show(cur+1);},DUR);
  }
  bars.forEach(function(b){b.addEventListener('click',function(){show(+b.dataset.go);});});
  if(pp)pp.addEventListener('click',function(){
    paused=!paused;hero.classList.toggle('paused',paused);pp.setAttribute('aria-pressed',paused);pp.textContent=paused?'▶ LECTURE':'❚❚ PAUSE';
    clearTimeout(timer);if(!paused)show(cur);
  });
  if(paused){hero.classList.add('paused');if(pp){pp.setAttribute('aria-pressed','true');pp.textContent='▶ LECTURE';}}
  /* précharger les autres vues une fois la page chargée */
  W.addEventListener('load',function(){setTimeout(function(){slides.forEach(load);},1200);});
  altT=+(slides[0]&&slides[0].dataset.a||0);alt=calm?altT:0;
  show(0);
  function pad(n){return(n<10?'0':'')+n;}
  var vis=true,mx=0,my=0,tmx=0,tmy=0;
  if(!calm&&W.matchMedia('(pointer: fine)').matches){
    hero.addEventListener('pointermove',function(e){var r=hero.getBoundingClientRect();tmx=(e.clientX-r.left)/r.width*2-1;tmy=(e.clientY-r.top)/r.height*2-1;});
    hero.addEventListener('pointerleave',function(){tmx=0;tmy=0;});
  }
  if('IntersectionObserver' in W)new IntersectionObserver(function(e){vis=e[0].isIntersecting;}).observe(hero);
  (function tick(now){
    if(vis&&!paused){
      var f=Math.floor((now-t0)/40),fr=f%25,s=Math.floor(f/25);
      if(tc)tc.textContent=pad(Math.floor(s/3600))+':'+pad(Math.floor(s/60)%60)+':'+pad(s%60)+':'+pad(fr);
    }
    mx+=(tmx-mx)*.07;my+=(tmy-my)*.07;
    if(Math.abs(tmx-mx)>.001||Math.abs(tmy-my)>.001){hero.style.setProperty('--mx',mx.toFixed(3));hero.style.setProperty('--my',my.toFixed(3));}
    alt+=(altT-alt)*.06;
    if(altE){var a=Math.round(alt);altE.textContent=altT>0?'ALT '+a+' m':'AU SOL';}
    requestAnimationFrame(tick);
  })(t0);
}

/* ---- Décollage : bouton Passer ---- */
var boot=d.querySelector('.boot');
if(boot){
  var off=function(){R.classList.add('boot-off');};
  boot.addEventListener('click',off);
  d.addEventListener('keydown',function(e){if(e.key==='Escape')off();},{once:true});
  setTimeout(off,2800);
}

/* ---- Apparitions au défilement ---- */
var SEL='main>section:not(.imm):not(.fly) .sec-head,.cards>.card,.sectors>.sector,.steps>li,.about>*,.reviews>figure,.zones>.zone,.faq details,.offers>.offer,main .prose>*,.contact>*,.brandbox,.chips';
var els=[].slice.call(d.querySelectorAll(SEL));
if(!calm&&'IntersectionObserver' in W){
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{rootMargin:'0px 0px -8% 0px',threshold:.08});
  els.forEach(function(el){
    var sib=el.parentNode?[].indexOf.call(el.parentNode.children,el):0;
    el.style.setProperty('--i',Math.min(sib,6));el.classList.add('up');io.observe(el);
  });
}else els=[];
/* filet de sécurité : tout ce qui est déjà au-dessus du bas de l'écran apparaît, même après un défilement très rapide */
function sweep(vh){for(var k=els.length-1;k>=0;k--){var el=els[k];if(el.classList.contains('in')||el.getBoundingClientRect().top<vh){el.classList.add('in');els.splice(k,1);}}}

/* ---- Compteurs d'abonnés ---- */
var counts=[].slice.call(d.querySelectorAll('[data-count]'));
if(!calm&&counts.length&&'IntersectionObserver' in W){
  var fmt=function(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,' ');};
  var co=new IntersectionObserver(function(es){es.forEach(function(e){
    if(!e.isIntersecting)return;co.unobserve(e.target);
    var el=e.target,to=+el.dataset.count,t1=performance.now(),D=1600;
    (function step(t){var k=Math.min(1,(t-t1)/D),v=Math.round(to*(1-Math.pow(1-k,3)));el.textContent=fmt(v);if(k<1)requestAnimationFrame(step);})(t1);
  });},{threshold:.6});
  counts.forEach(function(el){co.observe(el);});
}

/* ---- Survol : galerie horizontale épinglée ---- */
var flys=[].slice.call(d.querySelectorAll('.fly'));
function layoutFly(){
  flys.forEach(function(f){
    var tr=f.querySelector('.track');
    var ok=!calm&&W.innerWidth>=900;
    tr.style.transform='';
    var over=tr.scrollWidth-W.innerWidth;
    if(ok&&over>40){f.classList.add('pinned');f.style.height=(f.querySelector('.pin').offsetHeight+over)+'px';f._over=over;}
    else{f.classList.remove('pinned');f.style.height='';f._over=0;}
  });
}

/* ---- Viseur ---- */
var vfs=[].slice.call(d.querySelectorAll('.vf'));
if(!calm)vfs.forEach(function(v){v.classList.add('pinned');v.style.setProperty('--q',0);});

/* ---- Curseur réticule ---- */
if(!calm&&W.matchMedia('(pointer: fine)').matches){
  var curEl=d.createElement('div');curEl.className='cur';curEl.setAttribute('aria-hidden','true');curEl.innerHTML='<b></b>';d.body.appendChild(curEl);
  var cb=curEl.firstChild,zones='.imm,.fly,.vf';
  [].forEach.call(d.querySelectorAll(zones),function(z){z.classList.add('cur-zone');});
  d.addEventListener('pointermove',function(e){
    var z=e.target.closest&&e.target.closest(zones);
    curEl.classList.toggle('show',!!z);if(!z)return;
    curEl.style.transform='translate3d('+e.clientX+'px,'+e.clientY+'px,0)';
    var ln=e.target.closest('a,button');curEl.classList.toggle('link',!!ln);
    cb.textContent=ln?'OUVRIR':(z.classList.contains('fly')?'SURVOL':'X '+String(Math.round(e.clientX)).padStart(4,'0')+' · Y '+String(Math.round(e.clientY)).padStart(4,'0'));
  },{passive:true});
  d.addEventListener('pointerleave',function(){curEl.classList.remove('show');});
}

/* ---- Altimètre et progression du vol ---- */
var alti=d.querySelector('.alti'),altiV=alti&&alti.querySelector('b'),altiL=alti&&alti.querySelector('span');
var heads=[].slice.call(d.querySelectorAll('main>section'));
function label(sec){var e=sec.querySelector('.eyebrow');return e?e.textContent:'';}

var ticking=false;
function onScroll(){
  if(ticking)return;ticking=true;
  requestAnimationFrame(function(){
    ticking=false;
    var y=W.scrollY,vh=W.innerHeight,max=R.scrollHeight-vh,p=max>0?Math.min(1,y/max):0;
    R.style.setProperty('--prog',p.toFixed(4));
    d.body.classList.toggle('top',!!hero&&y<10);
    vfs.forEach(function(v){
      if(!v.classList.contains('pinned'))return;
      var r=v.getBoundingClientRect(),run=v.offsetHeight-v.querySelector('.vpin').offsetHeight;
      var q=Math.min(1,Math.max(0,-(r.top-(nav?nav.offsetHeight:0))/(run*.72)));
      v.style.setProperty('--q',q.toFixed(3));
    });
    if(els.length)sweep(vh);
    if(hero&&!calm){var hp=Math.min(1,Math.max(0,y/hero.offsetHeight));hero.style.setProperty('--hp',hp.toFixed(3));}
    flys.forEach(function(f){
      if(!f._over)return;
      var r=f.getBoundingClientRect(),run=f.offsetHeight-f.querySelector('.pin').offsetHeight;
      var q=Math.min(1,Math.max(0,-(r.top-(nav?nav.offsetHeight:0))/run));
      f.querySelector('.track').style.transform='translate3d('+(-q*f._over).toFixed(1)+'px,0,0)';
      [].forEach.call(f.querySelectorAll('figure'),function(fg){var b=fg.getBoundingClientRect(),c=(b.left+b.width/2)/W.innerWidth-.5;fg.style.setProperty('--px',(c*-4).toFixed(2)+'%');});
    });
    if(alti){
      altiV.textContent='ALT '+Math.round(120*(1-p))+' m';
      var lab='Décollage';
      for(var i=0;i<heads.length;i++){if(heads[i].getBoundingClientRect().top<vh*.45){var l=label(heads[i]);if(l)lab=l;}}
      if(p>.985)lab='Atterrissage · contact';
      altiL.textContent=lab;
      var mid=d.elementFromPoint(W.innerWidth-40,vh/2),dk=!!(mid&&mid.closest('.band,.fly,.hero,.phero,footer'));
      alti.classList.toggle('dk',dk);
      alti.classList.toggle('off',!!(hero&&y<hero.offsetHeight*.6)||!!(mid&&mid.closest('.fly,.vf')));
    }
  });
}
layoutFly();onScroll();
W.addEventListener('scroll',onScroll,{passive:true});
var rz;W.addEventListener('resize',function(){clearTimeout(rz);rz=setTimeout(function(){navh();layoutFly();onScroll();},150);});
W.addEventListener('load',function(){layoutFly();onScroll();});
})();
