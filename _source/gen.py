#!/usr/bin/env python3
"""Générateur du site drone6440.fr — produit des pages HTML statiques dans OUT."""
import json, math, os, re, sys, html, hashlib, shutil, datetime
from content import SERVICES, SECTORS, DEPTS, IDEAS, REVIEWS, HOME_FAQ, DEPT_ECO, SVC_ANGLE, PHOTOS
PH = {p[0]: p for p in PHOTOS}

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
SITE = 'https://drone6440.fr'
TODAY = datetime.date.today().isoformat()
BASE = (43.5586, -1.0681)  # Cauneille
PHONE, PHONE_INTL, EMAIL = '06 71 97 82 98', '+33671978298', 'drone64-40@outlook.fr'
SIRET = '[SIRET à compléter]'
TVA = '[TVA intracom. à compléter]'
CSSV = hashlib.md5(open('site.css','rb').read()).hexdigest()[:8]

cities = json.load(open('cities.json'))
by_slug = {c['slug']: c for c in cities}
pages = []  # (path, priority)

def esc(s): return html.escape(s, quote=True)
def strip(s): return re.sub(r'<[^>]+>', '', s)

def km(a, b):
    R = 6371; la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))

def trip(c):
    d = km(BASE, (c['lat'], c['lon'])) * 1.3
    if d < 4: return 0, 0
    road = int(round(d / 5) * 5) or 5
    mins = int(round((road / 68 * 60 + 5) / 5) * 5)
    return road, mins

def trip_txt(road, mins):
    if road == 0: return "Sur place, c'est ma base"
    if mins < 60: return f"≈ {road} km · environ {mins} min"
    h, m = divmod(mins, 60)
    return f"≈ {road} km · environ {h} h{m:02d}" if m else f"≈ {road} km · environ {h} h"

AIRFIELDS = [
 ("l'aéroport de Biarritz-Pays basque", 43.468, -1.523, 9), ("l'aéroport de Pau-Pyrénées", 43.380, -0.419, 9),
 ("l'aéroport de Bordeaux-Mérignac", 44.828, -0.715, 10), ("la base aérienne de Mont-de-Marsan", 43.912, -0.508, 10),
 ("la base aérienne de Cazaux", 44.533, -1.125, 12), ("l'aérodrome de Dax-Seyresse", 43.689, -1.069, 6),
 ("l'aéroport de Bergerac", 44.825, 0.519, 8), ("l'aéroport de La Rochelle-Île de Ré", 46.179, -1.195, 8),
 ("l'aéroport de Périgueux-Bassillac", 45.198, 0.816, 6), ("l'aérodrome d'Arcachon-La Teste", 44.596, -1.111, 5),
 ("l'aéroport d'Agen-La Garenne", 44.175, 0.591, 7), ("la base aérienne de Rochefort", 45.888, -0.983, 7),
 ("l'aéroport de Limoges-Bellegarde", 45.861, 1.180, 8), ("l'aéroport de Poitiers-Biard", 46.588, 0.307, 8),
 ("l'aéroport de Brive-Vallée de la Dordogne", 45.040, 1.485, 7), ("la base aérienne de Cognac", 45.658, -0.318, 8),
 ("l'aéroport d'Angoulême-Cognac", 45.729, 0.221, 6), ("l'aéroport de Tarbes-Lourdes-Pyrénées", 43.179, -0.006, 9),
]
def airfield(c):
    for n, la, lo, r in AIRFIELDS:
        if km((la, lo), (c['lat'], c['lon'])) <= r: return n
    return None

def pick(slug, options):
    return options[int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(options)]

def nb(n): return f"{n:,}".replace(',', ' ') if n else '—'

# ---------------------------------------------------------------- gabarit
FONTS = 'https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap'

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'

ORG = {"@type": "ProfessionalService", "@id": SITE + "/#entreprise", "name": "Drone 64-40", "url": SITE + "/",
       "image": SITE + "/img/og-drone-64-40.jpg", "logo": SITE + "/img/icon-512.png", "telephone": PHONE_INTL, "email": EMAIL,
       "priceRange": "Sur devis", "founder": {"@type": "Person", "name": "Nicolas Desperiers"},
       "address": {"@type": "PostalAddress", "streetAddress": "1972 Route du Pourtaou", "postalCode": "40300", "addressLocality": "Cauneille", "addressRegion": "Nouvelle-Aquitaine", "addressCountry": "FR"},
       "geo": {"@type": "GeoCoordinates", "latitude": 43.5586, "longitude": -1.0681},
       "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in ["Landes", "Pyrénées-Atlantiques", "Gironde", "Dordogne", "Lot-et-Garonne", "Charente-Maritime", "Charente", "Corrèze", "Creuse", "Deux-Sèvres", "Vienne", "Haute-Vienne", "Nouvelle-Aquitaine"]],
       "brand": [{"@type": "Brand", "name": "Drone 64-40"}, {"@type": "Brand", "name": "Regards 64/40", "logo": SITE + "/img/regards-64-40-logo.png", "url": SITE + "/regards/"}], "knowsAbout": ["Vidéo professionnelle", "Prise de vue aérienne par drone", "Photographie", "Community management", "Marketing digital"],
       "aggregateRating": {"@type": "AggregateRating", "ratingValue": "5", "bestRating": "5", "reviewCount": "4"},
       "sameAs": ["https://www.instagram.com/drone_6440", "https://www.facebook.com/Done6440/", "https://fr.linkedin.com/in/nicolas-desperiers-215817203"]}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i+1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}

def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

NAV = [('/videaste/', 'Vidéo'), ('/drone/', 'Drone'), ('/photographe/', 'Photo'), ('/community-manager/', 'Réseaux sociaux'),
       ('/secteurs/', 'Secteurs'), ('/zones/', 'Zones'), ('/realisations', 'Réalisations'), ('/formation-drone', 'Formation'), ('/boutique', 'Boutique')]

def header(cur):
    def cl(u):
        return ' aria-current="page"' if cur and u != '/' and cur.startswith(u.rstrip('/')) else ''
    items = ''.join(f'<li><a href="{u}"{cl(u)}>{n}</a></li>' for u, n in NAV)
    return f'''<a class="skip" href="#main">Aller au contenu</a>
<header class="nav"><div class="wrap">
<a class="brand" href="/">DRONE <span>64-40</span></a>
<nav aria-label="Navigation principale"><ul class="menu">{items}</ul></nav>
<details class="mob"><summary>MENU</summary><ul>{items}<li><a href="/contact">Contact</a></li></ul></details>
<a class="btn" href="/contact">Devis gratuit</a>
</div></header>'''

def footer():
    top = ['dax', 'bayonne', 'mont-de-marsan', 'biarritz', 'pau', 'hossegor', 'bordeaux', 'peyrehorade']
    dep_links = ''.join(f'<li><a href="/zones/{DEPTS[d][0]}">{DEPTS[d][1]}</a></li>' for d in ['40', '64', '33', '24', '17', '47'])
    return f'''<footer><div class="wrap cols">
<div><a class="brand" href="/">DRONE <span>64-40</span></a><p style="max-width:34ch">Photographe, vidéaste, pilote drone et community manager à Cauneille, dans les Landes. Interventions dans toute la Nouvelle-Aquitaine.</p>
<p><a href="tel:{PHONE_INTL}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<a href="/regards/" style="display:inline-flex;align-items:center;gap:10px;margin-top:6px"><img src="/img/regards-64-40-logo-blanc.png" alt="Regards 64/40" width="64" height="54" loading="lazy"><span>Photos signées Regards 64/40</span></a></div>
<div><h4>Métiers</h4><ul><li><a href="/videaste/">Vidéaste</a></li><li><a href="/photographe/">Photographe</a></li><li><a href="/drone/">Pilote drone</a></li><li><a href="/community-manager/">Community manager</a></li><li><a href="/formation-drone">Formation drone</a></li></ul></div>
<div><h4>Secteurs</h4><ul>{''.join(f'<li><a href="/{k}">{esc(v["name"])}</a></li>' for k, v in SECTORS.items())}</ul></div>
<div><h4>Zones</h4><ul>{dep_links}<li><a href="/zones/">Toute la Nouvelle-Aquitaine</a></li></ul></div>
<div><h4>Infos</h4><ul><li><a href="/a-propos">À propos</a></li><li><a href="/realisations">Réalisations</a></li><li><a href="/faq">FAQ</a></li><li><a href="/contact">Contact</a></li><li><a href="/regards/">Regards 64/40</a></li><li><a href="https://www.instagram.com/drone_6440" rel="noopener">Instagram</a></li></ul></div>
</div><div class="wrap legal">Villes fréquentes : {' · '.join(f'<a href="/drone-{s}">{esc(by_slug[s]["nom"])}</a>' for s in top)}<br>© {datetime.date.today().year} Drone 64-40 · SASU · <a href="/mentions-legales">Mentions légales</a></div></footer>'''

def contact_block(lieu=''):
    return f'''<section class="band" id="contact" aria-labelledby="h-contact"><div class="wrap contact">
<div class="direct"><span class="eyebrow">Contact</span><h2 id="h-contact">Parlons de votre projet{(" à " + esc(lieu)) if lieu else ""}</h2>
<p class="lede">Réponse sous 24 h avec un devis gratuit et sans engagement.</p>
<a class="line" href="tel:{PHONE_INTL}"><small>Téléphone</small><span>{PHONE}</span></a>
<a class="line" href="mailto:{EMAIL}"><small>Email</small><span style="font-size:1.3rem">{EMAIL}</span></a>
<div class="line"><small>Base</small><span style="font-size:1.2rem">1972 route du Pourtaou, 40300 Cauneille</span></div></div>
<form class="devis" data-mail="{EMAIL}">
<div class="row"><label>Nom<input name="nom" autocomplete="name" required></label><label>Téléphone<input name="tel" type="tel" autocomplete="tel"></label></div>
<div class="row"><label>Prestation<select name="type"><option>Vidéo</option><option>Drone</option><option>Photographie</option><option>Community management</option><option>Formation drone</option><option>Plusieurs prestations</option></select></label>
<label>Lieu du projet<input name="lieu" value="{esc(lieu)}"></label></div>
<label>Votre projet<textarea name="msg" required placeholder="Décrivez votre projet, la date souhaitée et l'usage des images."></textarea></label>
<button class="btn" type="submit">Préparer mon email de demande</button>
<p class="small">Le bouton ouvre votre messagerie avec votre demande pré-remplie. Vous pouvez aussi écrire directement à {EMAIL}.</p>
</form></div></section>'''

JS = '''<script>
document.querySelectorAll('form.devis').forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();var d=new FormData(f);
var b='Bonjour Nicolas,%0D%0A%0D%0APrestation : '+encodeURIComponent(d.get('type'))+'%0D%0ALieu : '+encodeURIComponent(d.get('lieu')||'')+'%0D%0ATéléphone : '+encodeURIComponent(d.get('tel')||'')+'%0D%0A%0D%0A'+encodeURIComponent(d.get('msg')||'')+'%0D%0A%0D%0A'+encodeURIComponent(d.get('nom')||'');
location.href='mailto:'+f.dataset.mail+'?subject='+encodeURIComponent('Demande de devis — '+d.get('type'))+'&body='+b;});});
</script>'''

def page(path, title, desc, body, cur=None, schema=None, img='og-drone-64-40.jpg', prio='0.6', robots='index,follow'):
    canon = SITE + path
    schema = [ORG] + (schema or [])
    head = f'''<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:locale" content="fr_FR"><meta property="og:site_name" content="Drone 64-40">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/img/{img}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0f2a24">
<link rel="icon" href="/img/icon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="/img/icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/site.css?v={CSSV}">
{ld({"@context": "https://schema.org", "@graph": schema})}
</head><body>'''
    doc = head + header(cur) + f'<main id="main">{body}</main>' + footer() + JS + '</body></html>'
    fp = OUT + (path + 'index.html' if path.endswith('/') else path + '.html')
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w').write(doc)
    if robots.startswith('index'): pages.append((path, prio))

def pic(name, alt, cls='', eager=False, sizes='(max-width:800px) 100vw, 50vw'):
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<img src="/img/{name}-800.webp" srcset="/img/{name}-800.webp 800w, /img/{name}.webp 1600w" sizes="{sizes}" alt="{esc(alt)}" {load}{(" class=" + chr(34) + cls + chr(34)) if cls else ""}>'

def crumbs_html(items):
    return '<nav class="crumbs" aria-label="Fil d\'Ariane"><ol>' + ''.join(
        (f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(items)-1 else f'<li aria-current="page">{esc(n)}</li>') for i, (n, u) in enumerate(items)) + '</ol></nav>'

def phero(items, h1, intro, img, alt, ctas=True, facts=''):
    c = f'<div class="ctas"><a class="btn" href="#contact">Demander un devis · réponse 24 h</a><a class="btn ghost" href="/realisations">Voir les réalisations</a></div>' if ctas else ''
    return f'<section class="phero">{pic(img, alt, eager=True, sizes="100vw")}<div class="wrap">{crumbs_html(items)}<h1>{h1}</h1><p class="intro">{intro}</p>{c}{facts}</div></section>'

def faq_html(faq, title='Questions fréquentes', hid='h-faq'):
    return f'<section aria-labelledby="{hid}"><div class="wrap"><div class="sec-head"><span class="eyebrow">FAQ</span><h2 id="{hid}">{title}</h2></div><div class="faq">' + \
        ''.join(f'<details{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(faq)) + '</div></div></section>'

GALLERY = [('capbreton-jetee-coucher-soleil', 'Coucher de soleil sur la jetée de Capbreton vue par drone', 'Capbreton (40) · drone'),
           ('estacade-capbreton', 'Estacade de Capbreton depuis la plage', 'Estacade · Capbreton'),
           ('goelands-cote-atlantique', 'Goélands sur un rocher de la côte atlantique', 'Côte atlantique · photo'),
           ('pont-vieux-orthez-drone', "Pont-Vieux d'Orthez vu du ciel", 'Orthez (64) · drone'),
           ('pissenlit-coucher-soleil-chalosse', 'Pissenlit au coucher du soleil dans une prairie landaise', 'Chalosse (40) · photo')]
def gallery():
    return '<div class="grid">' + ''.join(f'<figure class="g{i+1}">{pic(n, a, sizes="(max-width:720px) 50vw, 33vw")}<figcaption>{c}</figcaption></figure>' for i, (n, a, c) in enumerate(GALLERY)) + '</div>'

def pgrid(names):
    return '<div class="pgrid">' + ''.join(f'<figure>{pic(n, PH[n][1], sizes="(max-width:640px) 100vw, 33vw")}<figcaption>{esc(PH[n][2])}</figcaption></figure>' for n in names if n in PH) + '</div>'

def regards_block(lead="Toutes mes photographies au sol sont signées Regards 64/40, ma marque dédiée à la photo. Drone 64-40 réunit les prises de vue aériennes, la vidéo et la communication ; Regards 64/40 porte le regard du photographe : reportages, portraits, nature et traditions du Sud-Ouest."):
    return f'''<section class="tight" aria-labelledby="h-reg"><div class="wrap"><div class="brandbox">
<picture><source srcset="/img/regards-64-40-logo-blanc.png" media="(prefers-color-scheme: dark)"><img src="/img/regards-64-40-logo.png" alt="Logo Regards 64/40 by Drone 64/40" width="247" height="207" loading="lazy"></picture>
<div><span class="eyebrow">Ma marque photo</span><h2 id="h-reg">Les photos signées <em>Regards 64/40</em></h2><p>{lead}</p>
<p class="ctas" style="margin-top:16px"><a class="btn" href="/regards/">Découvrir Regards 64/40</a><a class="btn ghost" href="/boutique">Tirages d'art</a></p></div></div></div></section>'''

def service_cards(exclude=None, c3=False):
    out = []
    for i, (k, s) in enumerate(SERVICES.items()):
        if k == exclude: continue
        out.append(f'<a class="card{" lead" if i == 0 and not exclude else ""}" href="/{k}/">{pic(s["img"], s["short"], sizes="(max-width:620px) 100vw, 25vw")}<div class="in"><span class="tags">{s["tags"]}</span><h3>{esc(s["short"])}</h3><p>{esc(s["card"])}</p><span class="go">En savoir plus →</span></div></a>')
    return f'<div class="cards{" c3" if c3 else ""}">' + ''.join(out) + '</div>'

def sectors_band(title='Une page par métier', lede="Chaque secteur a ses contraintes : un service en cours, une vente à boucler, une foule à survoler. Voici comment je travaille avec le vôtre."):
    return f'<section class="band" aria-labelledby="h-sect"><div class="wrap"><div class="sec-head"><span class="eyebrow">Secteurs</span><h2 id="h-sect">{title}</h2><p class="lede">{lede}</p></div><div class="sectors">' + \
        ''.join(f'<a class="sector" href="/{k}"><strong>{esc(v["name"])}</strong><span>{esc(v["sub"])}</span></a>' for k, v in SECTORS.items()) + '</div></div></section>'

def reviews_html(n=4):
    return '<section aria-labelledby="h-avis"><div class="wrap"><div class="sec-head"><span class="eyebrow">Avis Google</span><div class="score"><b>5,0</b><span class="stars" aria-label="5 étoiles sur 5">★★★★★</span><span class="lede">sur 4 avis Google</span></div><h2 id="h-avis" style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Ce qu\'en disent les clients</h2></div><div class="reviews">' + \
        ''.join(f'<figure class="rv"><blockquote>« {esc(t)} »</blockquote><figcaption>{esc(a)}{(" · " + esc(r)) if r else ""}</figcaption></figure>' for t, a, r in REVIEWS[:n]) + '</div></div></section>'

def dep_cities(dep): return sorted([c for c in cities if c['dep'] == dep], key=lambda c: -(c['pop'] or 0))

def zones_block():
    cols = []
    for d in ['40', '64', '33', '24']:
        top = dep_cities(d)[:8]
        cols.append(f'<div class="zone"><h3><a href="/zones/{DEPTS[d][0]}">{DEPTS[d][1]}</a> <small>{d}</small></h3><ul class="chips">' + ''.join(f'<li><a href="/drone-{c["slug"]}">{esc(c["nom"])}</a></li>' for c in top) + f'<li><a class="all" href="/zones/{DEPTS[d][0]}">Toutes les villes →</a></li></ul></div>')
    others = ' · '.join(f'<a href="/zones/{DEPTS[d][0]}">{DEPTS[d][1]}</a>' for d in ['47', '17', '16', '19', '23', '79', '86', '87'])
    return f'<section aria-labelledby="h-zones" class="tight"><div class="wrap"><div class="sec-head"><span class="eyebrow">Zone d\'intervention</span><h2 id="h-zones">Près de chez vous</h2><p class="lede">Basé à Cauneille, je me déplace dans toute la Nouvelle-Aquitaine pour la photo, la vidéo, le drone et la communication. Chaque ville a sa page.</p></div><div class="zones">{"".join(cols)}</div><p style="margin-top:28px">Aussi en {others}.</p></div></section>'

# ---------------------------------------------------------------- accueil
def build_home():
    body = f'''<section class="hero" aria-labelledby="h1">{pic('capbreton-jetee-coucher-soleil', 'Coucher de soleil sur la jetée de Capbreton filmé par drone', eager=True, sizes='100vw')}
<div class="osd tl" aria-hidden="true"><span class="rec"><i></i>REC</span> &nbsp;4K · 25P · S-LOG3</div>
<div class="osd tr" aria-hidden="true">ALT 87 m · H.S. 6 m/s<br>43.559° N · 1.068° O</div>
<div class="osd br" aria-hidden="true">CAPBRETON (40) · 20:41</div>
<span class="corner a" aria-hidden="true"></span><span class="corner b" aria-hidden="true"></span>
<div class="wrap"><h1 id="h1">Photographe, vidéaste &amp; drone <em>Landes · Pays basque</em></h1>
<p>Je crée vos images au sol et dans les airs, puis je les fais travailler sur vos réseaux. Vidéo, drone, photo et community management pour entreprises, restaurants, immobilier et collectivités, partout en Nouvelle-Aquitaine.</p>
<div class="ctas"><a class="btn" href="#contact">Demander un devis · réponse 24 h</a><a class="btn ghost" href="/realisations">Voir les réalisations</a></div>
<div class="proof"><span><b>★ 5,0</b> · 4 avis Google</span><span><b>Télépilote certifié EU</b> · déclaré DGAC</span><span><b>Certifié marketing digital</b> · RS6710</span><span><b>Assuré</b> RC Pro</span><span><b>5 ans</b> de terrain</span></div></div></section>
<section aria-labelledby="h-services"><div class="wrap"><div class="sec-head"><span class="eyebrow">Prestations</span><h2 id="h-services">Quatre métiers, un seul interlocuteur</h2>
<p class="lede">Vous n'avez pas à coordonner un vidéaste, un pilote, un monteur et une agence. Je tourne, je monte, je publie et je mesure ce que vos contenus rapportent.</p></div>{service_cards()}</div></section>
{sectors_band()}
<section aria-labelledby="h-real"><div class="wrap"><div class="sec-head"><span class="eyebrow">Réalisations</span><h2 id="h-real">Vu d'en haut, entre Adour et océan</h2></div>{gallery()}<p style="margin-top:22px"><a class="btn ghost" href="/realisations">Toutes les réalisations</a></p></div></section>
<section aria-labelledby="h-method" class="tight"><div class="wrap"><div class="sec-head"><span class="eyebrow">Déroulé d'un projet</span><h2 id="h-method">Du devis à la diffusion</h2></div>
<ol class="steps"><li><strong>Devis en 24 h</strong><span>Vous décrivez le projet, je vous envoie un prix ferme.</span></li><li><strong>Repérage &amp; préparation</strong><span>Météo, lumière, zones de vol : je prépare le tournage et les démarches.</span></li><li><strong>Tournage</strong><span>Au sol et en drone, le même jour, avec une seule personne.</span></li><li><strong>Montage &amp; diffusion</strong><span>Étalonnage, formats web et réseaux, puis publication et suivi si vous le souhaitez.</span></li></ol></div></section>
<section class="band" aria-labelledby="h-about"><div class="wrap about">{pic('nicolas-desperiers-portrait', 'Portrait de Nicolas Desperiers avec son appareil photo, son drone et son ordinateur', sizes='(max-width:780px) 100vw, 40vw')}
<div class="txt"><span class="eyebrow">Qui filme</span><h2 id="h-about">Nicolas Desperiers</h2>
<p>Installé à Cauneille, entre Peyrehorade et Dax, je photographie et je filme les Landes et le Pays basque depuis plus de cinq ans. Avant l'image, j'ai été mécanicien automobile : je prépare chaque tournage avec la même rigueur.</p>
<p>Je suis aussi community manager. Je tourne en pensant déjà à la diffusion : formats verticaux, accroches, séries de contenus. Vous avez un interlocuteur unique, du tournage aux statistiques de vos publications.</p>
<dl class="creds"><dt>Drone</dt><dd>Télépilote certifié EU (A1/A3, A2) · déclaré DGAC</dd><dt>Marketing</dt><dd>« Entreprendre et développer sa clientèle grâce au marketing digital » · LearningShelter 2026 · RS6710</dd><dt>Assurance</dt><dd>Responsabilité civile professionnelle</dd><dt>Photo</dt><dd>Photographies signées Regards 64/40</dd><dt>Société</dt><dd>SASU Drone 64-40 · Cauneille (40300)</dd></dl>
<p><a class="btn ghost" href="/a-propos">Mon parcours</a></p></div></div></section>
{reviews_html()}
{zones_block()}
{faq_html(HOME_FAQ, 'Avant de réserver')}
{contact_block()}'''
    page('/', 'Photographe, vidéaste & drone Landes, Pays basque | Drone 64-40',
         "Photographe, vidéaste, pilote drone certifié et community manager à Cauneille (40). Landes, Pays basque, Béarn, Gironde et toute la Nouvelle-Aquitaine. Devis sous 24 h.",
         body, cur='/', schema=[{"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Drone 64-40", "inLanguage": "fr"}, faq_ld(HOME_FAQ)], prio='1.0')

# ---------------------------------------------------------------- services
def build_services():
    for k, s in SERVICES.items():
        path = f'/{k}/'
        items = [('Accueil', '/'), (s['short'], path)]
        offers = '<div class="offers">' + ''.join(f'<div class="offer"><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a, b in s['offers']) + '</div>'
        deps = ' '.join(f'<li><a href="/{k}/{DEPTS[d][0]}">{SVC_ANGLE[k][0]} {prep(d)} {DEPTS[d][1]}</a></li>' for d in DEPTS)
        body = phero(items, s['h1'], s['intro'], s['img'], s['short']) + f'''
<section aria-labelledby="h-off"><div class="wrap"><div class="sec-head"><span class="eyebrow">Ce que je propose</span><h2 id="h-off">{esc(s["short"])}</h2></div>{offers}</div></section>
{regards_block() if k == 'photographe' else ''}<section class="tight"><div class="wrap prose">{s["body"]}</div></section>
{('<section class="tight" aria-labelledby="h-gal"><div class="wrap"><div class="sec-head"><span class="eyebrow">Galerie</span><h2 id="h-gal" style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Quelques photos Regards 64/40</h2></div>' + pgrid([p[0] for p in PHOTOS]) + '</div></section>') if k == 'photographe' else ''}
<section class="tight" aria-labelledby="h-dep"><div class="wrap"><div class="sec-head"><span class="eyebrow">Par département</span><h2 id="h-dep" style="font-size:clamp(1.8rem,3.5vw,2.4rem)">{SVC_ANGLE[k][0]} en Nouvelle-Aquitaine</h2></div><ul class="chips">{deps}</ul></div></section>
{sectors_band('Par secteur', "Des exemples concrets selon votre activité.")}
<section aria-labelledby="h-autres"><div class="wrap"><div class="sec-head"><span class="eyebrow">Aussi</span><h2 id="h-autres" style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Mes autres métiers</h2></div>{service_cards(exclude=k, c3=True)}</div></section>
{faq_html(s["faq"])}{contact_block()}'''
        page(path, s['title'], s['desc'], body, cur=path, img='og-drone-64-40.jpg', prio='0.9',
             schema=[crumbs_ld(items), faq_ld(s['faq']), {"@type": "Service", "name": s['short'], "provider": {"@id": SITE + "/#entreprise"}, "areaServed": "Nouvelle-Aquitaine", "serviceType": s['short']}])

def prep(d):  # « en Gironde », « dans les Landes »
    return {'40': 'dans les', '64': 'dans les', '79': 'dans les', '85': 'en'}.get(d, 'en') if d != '86' else 'dans la'

def build_service_depts():
    for k, s in SERVICES.items():
        T, t, pitch = SVC_ANGLE[k]
        for d, (dslug, dname, dtxt) in DEPTS.items():
            path = f'/{k}/{dslug}'
            loc = f"{prep(d)} {dname}"
            items = [('Accueil', '/'), (s['short'], f'/{k}/'), (dname, path)]
            cs = dep_cities(d)
            pref = cs[0]
            road, mins = trip(pref)
            intro = f"{pitch} J'interviens {loc}, notamment pour {DEPT_ECO[d]}."
            chips = '<ul class="chips">' + ''.join(f'<li><a href="/drone-{c["slug"]}">{esc(c["nom"])}</a></li>' for c in cs) + "</ul>"
            others = ' · '.join(f'<a href="/{o}/{dslug}">{SVC_ANGLE[o][0]} {loc}</a>' for o in SERVICES if o != k)
            offers = '<div class="offers">' + ''.join(f'<div class="offer"><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a, b in s['offers'][:4]) + '</div>'
            faq = [(f"Vous déplacez-vous partout {loc} ?", f"Oui. Ma base est à Cauneille (40). {pref['nom']} est à {trip_txt(road, mins).replace('≈ ', 'environ ').split(' · ')[0]} de route. Le déplacement est indiqué clairement dans le devis, et je regroupe les tournages quand c'est possible."),
                   (f"Quel délai pour un projet {loc} ?", "Je réponds sous 24 h avec un devis. La date de tournage dépend de mon planning et de la météo pour les vols de drone, en général sous une à trois semaines."),
                   (s['faq'][0][0], s['faq'][0][1])]
            body = phero(items, f'{T} <em>{loc}</em>', intro, s['img'], f"{T} {loc}") + f'''
<section aria-labelledby="h-z"><div class="wrap split"><div class="prose"><span class="eyebrow">{dname} ({d})</span><h2 id="h-z" style="margin-top:12px">Mon travail de {t} {loc}</h2><p>{esc(dtxt)}</p><p>{esc(s["card"])} Pour un projet plus complet, je combine {", ".join(SVC_ANGLE[o][1] for o in SERVICES if o != k)} dans un seul devis.</p></div>
<aside class="sheet"><h2>En bref</h2><dl><dt>Métier</dt><dd>{T}</dd><dt>Zone</dt><dd>{dname} ({d})</dd><dt>Base</dt><dd>Cauneille (40)</dd><dt>{esc(pref["nom"])}</dt><dd>{trip_txt(road, mins)}</dd><dt>Devis</dt><dd>Gratuit, sous 24 h</dd></dl></aside></div></section>
<section class="tight" aria-labelledby="h-o"><div class="wrap"><div class="sec-head"><span class="eyebrow">Prestations</span><h2 id="h-o" style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Ce que je propose {loc}</h2></div>{offers}<p style="margin-top:20px"><a href="/{k}/">Tout savoir sur mon offre de {t} →</a></p></div></section>
<section class="tight" aria-labelledby="h-v"><div class="wrap"><div class="sec-head"><span class="eyebrow">Villes</span><h2 id="h-v" style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Les villes où j'interviens {loc}</h2></div>{chips}<p style="margin-top:20px">Aussi {loc} : {others}.</p></div></section>
{faq_html(faq)}{contact_block()}'''
            page(path, f'{T} {loc} ({d}) | Drone 64-40'[:70], f"{T} {loc} : {strip(s['card'])[:90]} Devis gratuit sous 24 h."[:158], body, cur=f'/{k}/', prio='0.7',
                 schema=[crumbs_ld(items), faq_ld(faq), {"@type": "Service", "name": f"{T} {loc}", "serviceType": s['short'], "provider": {"@id": SITE + "/#entreprise"}, "areaServed": {"@type": "AdministrativeArea", "name": dname}}])

# ---------------------------------------------------------------- secteurs
def build_sectors():
    hub_items = [('Accueil', '/'), ('Secteurs', '/secteurs/')]
    for k, s in SECTORS.items():
        path = f'/{k}'
        items = hub_items + [(s['name'], path)]
        pts = '<div class="offers">' + ''.join(f'<div class="offer"><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a, b in s['points']) + '</div>'
        rv = f'<section class="tight"><div class="wrap narrow"><figure class="rv"><blockquote>« {esc(s["review"][0])} »</blockquote><figcaption>{esc(s["review"][1])} · avis Google</figcaption></figure></div></section>' if s['review'] else ''
        others = ''.join(f'<a class="sector" href="/{o}"><strong>{esc(v["name"])}</strong><span>{esc(v["sub"])}</span></a>' for o, v in SECTORS.items() if o != k)
        faq = [("Intervenez-vous partout en Nouvelle-Aquitaine ?", "Oui. Je suis basé à Cauneille, dans le sud des Landes, et j'interviens surtout dans les Landes et les Pyrénées-Atlantiques, mais aussi dans toute la région sur devis."),
               ("Pouvez-vous combiner photo, vidéo et drone ?", "Oui, c'est l'intérêt de travailler avec moi : une seule personne, un seul devis et une seule journée de tournage pour tous vos besoins visuels."),
               ("Comment obtenir un devis ?", "Décrivez votre projet par téléphone, par email ou avec le formulaire. Je vous réponds sous 24 h avec un prix ferme.")]
        body = phero(items, s['h1'], s['intro'], s['img'], s['name']) + f'''
<section aria-labelledby="h-p"><div class="wrap"><div class="sec-head"><span class="eyebrow">{esc(s["name"])}</span><h2 id="h-p">Ce que je réalise</h2></div>{pts}</div></section>
<section class="tight"><div class="wrap prose">{s["body"]}<p>Voir aussi : <a href="/videaste/">vidéo</a> · <a href="/photographe/">photographie</a> · <a href="/drone/">drone</a> · <a href="/community-manager/">community management</a>.</p></div></section>
{('<section class="tight"><div class="wrap">' + pgrid(s['photos']) + '</div></section>') if s.get('photos') else ''}{rv}
<section class="band"><div class="wrap"><div class="sec-head"><span class="eyebrow">Autres secteurs</span><h2 style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Je travaille aussi avec</h2></div><div class="sectors" style="grid-template-columns:repeat(4,1fr)">{others}</div></div></section>
{faq_html(faq)}{contact_block()}'''
        page(path, s['title'], s['desc'], body, cur='/secteurs', prio='0.8', schema=[crumbs_ld(items), faq_ld(faq)])
    body = phero(hub_items, 'Les secteurs <em>que je filme</em>', "Immobilier, restauration et hôtellerie, événements, collectivités et agriculture : chaque métier a ses contraintes et ses codes. Voici comment je travaille avec chacun.", 'drones-dji-fpv', 'Drones prêts au décollage', ctas=False) + \
        '<section><div class="wrap"><div class="cards c3">' + ''.join(f'<a class="card" href="/{k}">{pic(v["img"], v["name"], sizes="(max-width:620px) 100vw, 33vw")}<div class="in"><h3>{esc(v["name"])}</h3><p>{esc(v["intro"])}</p><span class="go">Voir le secteur →</span></div></a>' for k, v in SECTORS.items()) + '</div></div></section>' + contact_block()
    page('/secteurs/', 'Secteurs : immobilier, restaurants, événements, collectivités | Drone 64-40', "Photo, vidéo, drone et community management adaptés à votre secteur : immobilier, restaurants et hôtels, événements, collectivités, agriculture.", body, cur='/secteurs', prio='0.7', schema=[crumbs_ld(hub_items)])

# ---------------------------------------------------------------- villes
def nearest(c, n=8):
    o = sorted((x for x in cities if x['slug'] != c['slug']), key=lambda x: km((c['lat'], c['lon']), (x['lat'], x['lon'])))
    return o[:n]

INTRO_V = [
 "Basé à Cauneille, je me déplace à {nom} pour la photo, la vidéo, les prises de vue par drone et la communication sur les réseaux.",
 "Photographe, vidéaste, télépilote certifié et community manager, j'interviens à {nom} et dans les communes voisines.",
 "Que vous ayez besoin de photos, d'une vidéo, de plans aériens ou d'une présence régulière sur les réseaux, je viens à {nom} avec tout le matériel.",
]
def build_cities():
    for c in cities:
        dslug, dname, _ = DEPTS[c['dep']]
        path = f"/drone-{c['slug']}"
        nom = c['nom']
        road, mins = trip(c)
        af = airfield(c)
        items = [('Accueil', '/'), ('Zones', '/zones/'), (f'{dname} ({c["dep"]})', f'/zones/{dslug}'), (nom, path)]
        ideas = ''.join(f'<a href="/{s}"><strong>{esc(SECTORS[s]["name"]) if s in SECTORS else esc(SERVICES[s]["short"])}</strong><span>{esc(t)}</span></a>' for s, t in IDEAS[c['type']])
        spots = '<ul class="chips">' + ''.join(f'<li><span>{esc(s)}</span></li>' for s in c['spots']) + '</ul>'
        near = nearest(c)
        near_html = '<ul class="chips">' + ''.join(f'<li><a href="/drone-{n["slug"]}">{esc(n["nom"])}</a></li>' for n in near) + f'<li><a class="all" href="/zones/{dslug}">Toutes les villes {prep(c["dep"])} {dname} →</a></li></ul>'
        air = (f"La commune est proche de {af} : l'espace aérien y est réglementé. Je vérifie les restrictions et je fais les démarches avant de confirmer un vol, ou je vous propose des plans au sol si le vol n'est pas possible." if af else
               "Avant chaque vol, je vérifie la carte des restrictions (Géoportail), la météo et le vent. En agglomération, les règles limitent la hauteur et les distances : je vous dis dès le devis ce qui est possible.")
        sheet = f'''<aside class="sheet"><h2>Fiche pratique</h2><dl>
<dt>Commune</dt><dd>{esc(nom)}</dd>{f'<dt>Code postal</dt><dd>{c["cp"]}</dd>' if c.get('cp') else ''}
<dt>Département</dt><dd>{dname} ({c["dep"]})</dd>{f'<dt>Population</dt><dd>{nb(c["pop"])} habitants</dd>' if c.get('pop') and c['nom'] not in ('Contis-Plage', 'Arjuzanx', 'Morcenx') else ''}
<dt>Depuis Cauneille</dt><dd>{trip_txt(road, mins)}</dd><dt>Devis</dt><dd>Gratuit, réponse sous 24 h</dd></dl>
<p class="note">{air}</p></aside>'''
        dist_ans = ("C'est ma commune de base : je peux être sur place très rapidement." if road == 0 else
                    f"{nom} est à {trip_txt(road, mins).replace('≈ ', 'environ ')} de Cauneille, ma base. Le déplacement est indiqué clairement dans le devis.")
        faq = [(f"Vous déplacez-vous à {nom} ?", dist_ans),
               (f"Peut-on faire voler un drone à {nom} ?", air),
               (f"Quelles prestations proposez-vous à {nom} ?", f"Photographie, vidéo, prises de vue par drone et community management. Je peux tout réaliser le même jour à {nom} et vous livrer des contenus pour votre site et vos réseaux."),
               ("Combien coûte une prestation ?", "Le prix dépend de la durée, du montage et des livrables. Je vous envoie un devis ferme sous 24 h après un court échange.")]
        h1 = f'Photographe, vidéaste &amp; drone <em>à {esc(nom)}</em>'
        intro = pick(c['slug'], INTRO_V).format(nom=esc(nom))
        facts = f'<div class="facts"><span><b>{dname}</b> · {c["dep"]}</span><span><b>{trip_txt(road, mins)}</b></span><span><b>★ 5,0</b> · avis Google</span><span><b>Certifié EU</b> · DGAC</span></div>'
        img = {'ocean': 'capbreton-jetee-coucher-soleil', 'pb-cote': 'estacade-capbreton', 'lac': 'lac-ile-sable-landes-drone', 'bearn': 'pont-vieux-orthez-drone', 'chalosse': 'pissenlit-coucher-soleil-chalosse', 'ile': 'goelands-cote-atlantique'}.get(c['type'], 'lac-ile-sable-landes-drone' if c['type'] in ('foret', 'adour') else 'pont-vieux-orthez-drone')
        body = phero(items, h1, intro, img, f'Prise de vue par drone près de {nom}', facts=facts) + f'''
<section aria-labelledby="h-loc"><div class="wrap split"><div><span class="eyebrow">{esc(nom)} vu par l'objectif</span><h2 id="h-loc" style="margin:12px 0 18px">Filmer et photographier {esc(nom)}</h2>
<div class="prose"><p>{esc(c["txt"])}</p></div><h3 style="font-size:1.2rem;margin:22px 0 12px">À voir et à filmer</h3>{spots}
<h3 style="font-size:1.2rem;margin:28px 0 4px">Ce que je réalise à {esc(nom)}</h3><div class="ideas">{ideas}</div></div>{sheet}</div></section>
<section class="tight" aria-labelledby="h-m"><div class="wrap"><div class="sec-head"><span class="eyebrow">Mes métiers</span><h2 id="h-m" style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Photo, vidéo, drone et réseaux sociaux à {esc(nom)}</h2></div>
<div class="offers">
<a class="offer" href="/photographe/{dslug}" style="text-decoration:none"><strong>Photographe à {esc(nom)}</strong><span>Immobilier, restaurant, portrait, événement, produit. Photos retouchées et prêtes à publier.</span></a>
<a class="offer" href="/videaste/{dslug}" style="text-decoration:none"><strong>Vidéaste à {esc(nom)}</strong><span>Film d'entreprise, vidéo de restaurant ou d'hôtel, aftermovie, reels pour les réseaux.</span></a>
<a class="offer" href="/drone/{dslug}" style="text-decoration:none"><strong>Drone à {esc(nom)}</strong><span>Photo et vidéo aérienne 4K, vols FPV, suivi de chantier, dans le respect de la réglementation.</span></a>
<a class="offer" href="/community-manager/{dslug}" style="text-decoration:none"><strong>Community manager à {esc(nom)}</strong><span>Création de contenus, publication, fiche Google et suivi des résultats.</span></a>
</div></div></section>
<section class="tight" aria-labelledby="h-n"><div class="wrap"><div class="sec-head"><span class="eyebrow">Autour de {esc(nom)}</span><h2 id="h-n" style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Communes proches</h2></div>{near_html}</div></section>
{faq_html(faq, f"Questions sur {esc(nom)}")}{contact_block(nom)}'''
        title = f"Photographe, vidéaste & drone à {nom} ({c['dep']}) | Drone 64-40"
        if len(title) > 68: title = f"Photographe, vidéaste & drone {nom} ({c['dep']})"
        first = re.split(r'(?<=[.!?])\s', c['txt'])[0]
        desc = f"Photo, vidéo, drone et community management à {nom}. {first}"
        if len(desc) > 155: desc = desc[:152].rsplit(' ', 1)[0] + '…'
        place = {"@type": "City", "name": nom, "geo": {"@type": "GeoCoordinates", "latitude": c['lat'], "longitude": c['lon']}}
        if c.get('cp'): place["address"] = {"@type": "PostalAddress", "postalCode": c['cp'], "addressCountry": "FR"}
        page(path, title, desc, body, cur='/zones', prio='0.6', schema=[crumbs_ld(items), faq_ld(faq),
             {"@type": "Service", "name": f"Photographe, vidéaste et drone à {nom}", "provider": {"@id": SITE + "/#entreprise"}, "areaServed": place, "serviceType": ["Photographie", "Vidéo", "Prise de vue par drone", "Community management"]}])

# ---------------------------------------------------------------- zones
def build_zones():
    hub = [('Accueil', '/'), ('Zones', '/zones/')]
    blocks = []
    for d, (dslug, dname, dtxt) in DEPTS.items():
        cs = dep_cities(d)
        path = f'/zones/{dslug}'
        items = hub + [(dname, path)]
        lst = '<ul class="citylist">' + ''.join(f'<li><a href="/drone-{c["slug"]}">{esc(c["nom"])}</a><small>{trip_txt(*trip(c)).split(" · ")[0].replace("≈ ", "")}</small></li>' for c in sorted(cs, key=lambda c: c['nom'])) + '</ul>'
        svc = ' · '.join(f'<a href="/{k}/{dslug}">{SVC_ANGLE[k][0]} {prep(d)} {dname}</a>' for k in SERVICES)
        body = phero(items, f'Photo, vidéo &amp; drone <em>{prep(d)} {dname}</em>', dtxt, 'lac-ile-sable-landes-drone', dname, facts=f'<div class="facts"><span><b>{len(cs)} villes</b> avec leur page</span><span><b>Département</b> {d}</span></div>') + f'''
<section aria-labelledby="h-l"><div class="wrap"><div class="sec-head"><span class="eyebrow">{dname} ({d})</span><h2 id="h-l">Toutes les villes</h2><p class="lede">Distances approximatives par la route depuis Cauneille.</p></div>{lst}</div></section>
<section class="tight"><div class="wrap"><div class="sec-head"><span class="eyebrow">Par métier</span><h2 style="font-size:clamp(1.8rem,3.5vw,2.4rem)">Mes métiers {prep(d)} {dname}</h2></div><p>{svc}</p></div></section>{contact_block()}'''
        page(path, f'Photographe, vidéaste & drone {prep(d)} {dname} ({d}) | Drone 64-40'[:75], f"Photo, vidéo, drone et community management {prep(d)} {dname} : {len(cs)} villes desservies depuis Cauneille (40). Devis gratuit sous 24 h.", body, cur='/zones', prio='0.7',
             schema=[crumbs_ld(items), {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i+1, "url": f'{SITE}/drone-{c["slug"]}', "name": c['nom']} for i, c in enumerate(cs)]}])
        blocks.append(f'<div class="zone"><h3><a href="{path}">{dname}</a> <small>{d}</small></h3><ul class="chips">' + ''.join(f'<li><a href="/drone-{c["slug"]}">{esc(c["nom"])}</a></li>' for c in cs[:10]) + f'<li><a class="all" href="{path}">{len(cs)} villes →</a></li></ul></div>')
    body = phero(hub, 'Toute la <em>Nouvelle-Aquitaine</em>', f"Basé à Cauneille, dans le sud des Landes, j'interviens pour la photo, la vidéo, le drone et la communication dans toute la Nouvelle-Aquitaine. {len(cities)} villes ont leur page dédiée.", 'capbreton-jetee-coucher-soleil', 'Côte landaise vue du ciel', ctas=False) + \
        f'<section><div class="wrap"><div class="zones">{"".join(blocks)}</div></div></section>' + contact_block()
    page('/zones/', 'Zones d\'intervention en Nouvelle-Aquitaine | Drone 64-40', f"Photographe, vidéaste, drone et community manager dans toute la Nouvelle-Aquitaine : Landes, Pays basque, Béarn, Gironde, Dordogne et plus. {len(cities)} villes desservies.", body, cur='/zones', prio='0.8', schema=[crumbs_ld(hub)])

# ---------------------------------------------------------------- annexes
def build_misc():
    it = [('Accueil', '/'), ('Réalisations', '/realisations')]
    figs = ''.join(f'<figure class="rv" style="padding:0;overflow:hidden">{pic(n, a, sizes="(max-width:720px) 100vw, 50vw")}<figcaption style="padding:12px 16px">{c}</figcaption></figure>' for n, a, c in GALLERY + [('lac-ile-sable-landes-drone', "Vue aérienne d'un lac et d'une île de sable dans les Landes", 'Landes · drone'), ('drones-dji-fpv', 'Drones DJI et FPV avant un vol à Dax', 'Dax (40) · matériel')])
    body = phero(it, 'Mes <em>réalisations</em>', "Une sélection de photos et de prises de vue aériennes réalisées dans les Landes et au Pays basque. D'autres projets sont visibles sur Instagram @drone_6440.", 'estacade-capbreton', 'Estacade de Capbreton', ctas=False) + \
        f'<section aria-labelledby="h-ph"><div class="wrap"><div class="sec-head"><span class="eyebrow">Photographie · Regards 64/40</span><h2 id="h-ph">Au sol</h2><p class="lede">Mes photographies sont publiées sous ma marque Regards 64/40.</p></div>' + pgrid([p[0] for p in PHOTOS]) + '</div></section>' + regards_block() + f'<section class="tight" aria-labelledby="h-dr"><div class="wrap"><div class="sec-head"><span class="eyebrow">Drone et paysages</span><h2 id="h-dr">Vu du ciel</h2></div><div class="reviews">{figs}</div><p style="margin-top:28px"><a class="btn" href="https://www.instagram.com/drone_6440" rel="noopener">Voir plus sur Instagram</a></p></div></section>{reviews_html()}{contact_block()}'
    page('/realisations', 'Réalisations photo, vidéo et drone | Drone 64-40', "Photos, vidéos et prises de vue aériennes réalisées dans les Landes, au Pays basque et en Béarn par Nicolas Desperiers, Drone 64-40.", body, cur='/realisations', prio='0.7', schema=[crumbs_ld(it)])

    it = [('Accueil', '/'), ('À propos', '/a-propos')]
    body = phero(it, 'Nicolas <em>Desperiers</em>', "Photographe, vidéaste, télépilote certifié et community manager, installé à Cauneille dans le sud des Landes.", 'nicolas-desperiers-portrait', 'Nicolas Desperiers', ctas=False) + f'''
<section><div class="wrap split"><div class="prose"><figure style="margin:0 0 28px">{pic('nicolas-desperiers-portrait', 'Portrait de Nicolas Desperiers, photographe, vidéaste et télépilote', sizes='(max-width:860px) 100vw, 55vw')}</figure><h2 style="margin-top:0">Mon parcours</h2>
<p>J'ai grandi entre l'Adour et l'océan. Avant de faire de l'image mon métier, j'ai travaillé comme mécanicien automobile : j'en ai gardé le goût du travail bien préparé et du matériel entretenu.</p>
<p>Depuis plus de cinq ans, je photographie et je filme les Landes et le Pays basque, d'abord avec un drone puis au sol. J'ai créé Drone 64-40 pour proposer aux entreprises, aux restaurants, aux agences immobilières et aux collectivités une offre complète : la prise de vue, le montage et la diffusion sur les réseaux.</p>
<p>Je suis évaluateur pour des centres de formation de télépilotes depuis 2023, et j'ai obtenu en 2026 une certification en marketing digital enregistrée au Répertoire spécifique de France Compétences (RS6710).</p>
<h2>Deux marques, une même exigence</h2><p><strong>Drone 64-40</strong> réunit les prises de vue aériennes, la vidéo et la communication. <strong>Regards 64/40</strong> est ma marque de photographie : toutes mes photos au sol, reportages, portraits, nature et traditions du Sud-Ouest, sont publiées sous ce nom et proposées en tirages d'art. <a href="/regards/">Découvrir Regards 64/40</a>.</p>
<h2>Mon matériel</h2><p>Hybride Sony α6700 en S-Log3, stabilisateur DJI, micros sans fil, drones DJI et FPV. Montage et étalonnage sur DaVinci Resolve, retouche photo sur Lightroom.</p></div>
<aside class="sheet"><h2>Certifications</h2><dl><dt>Drone</dt><dd>Télépilote certifié EU, compétences A1/A3 et A2, déclaré DGAC</dd><dt>Marketing</dt><dd>Entreprendre et développer sa clientèle grâce au marketing digital, LearningShelter, 2026, RS6710</dd><dt>Formation</dt><dd>Évaluateur pour des centres de formation drone depuis 2023</dd><dt>Assurance</dt><dd>RC professionnelle</dd><dt>Marques</dt><dd>Drone 64-40 (drone, vidéo, communication) · Regards 64/40 (photographie)</dd><dt>Société</dt><dd>SASU Drone 64-40, Cauneille (40300)</dd></dl></aside></div></section>{regards_block()}{reviews_html()}{contact_block()}'''
    page('/a-propos', 'À propos de Nicolas Desperiers | Drone 64-40', "Nicolas Desperiers, photographe, vidéaste, télépilote certifié EU et community manager certifié en marketing digital, basé à Cauneille dans les Landes.", body, cur='/a-propos', prio='0.6',
         schema=[crumbs_ld(it), {"@type": "Person", "name": "Nicolas Desperiers", "jobTitle": "Photographe, vidéaste, télépilote et community manager", "worksFor": {"@id": SITE + "/#entreprise"}, "address": {"@type": "PostalAddress", "addressLocality": "Cauneille", "postalCode": "40300", "addressCountry": "FR"}, "sameAs": ["https://fr.linkedin.com/in/nicolas-desperiers-215817203", "https://www.instagram.com/drone_6440"]}])

    it = [('Accueil', '/'), ('Formation drone', '/formation-drone')]
    ffaq = [("Faut-il une formation pour piloter un drone de loisir ?", "Au-delà de 250 grammes ou avec une caméra, la réglementation européenne impose des formations et des enregistrements selon la catégorie de vol. Je vous explique ce qui s'applique à votre drone."),
            ("La formation est-elle certifiante ?", "La formation prépare aux examens théoriques et vous fait progresser en pilotage. Les examens officiels sont passés selon les modalités prévues par la DGAC."),
            ("Où se déroule la formation ?", "Dans le sud des Landes, sur un terrain adapté, ou chez vous si l'espace le permet. Contactez-moi pour fixer les dates.")]
    body = phero(it, 'Formation <em>pilote drone</em>', "Deux jours pour apprendre à piloter en sécurité et comprendre la réglementation de la catégorie ouverte (A1/A3, A2). Par un télépilote en activité, évaluateur pour des centres de formation depuis 2023.", 'drones-dji-fpv', 'Drones utilisés en formation') + f'''
<section><div class="wrap"><div class="sec-head"><span class="eyebrow">Programme</span><h2>Deux jours, théorie et pratique</h2></div>
<ol class="steps"><li><strong>Réglementation</strong><span>Catégories de vol, A1/A3 et A2, zones interdites, Géoportail, assurances.</span></li><li><strong>Préparation du vol</strong><span>Météo, vent, check-list, analyse du site et des risques.</span></li><li><strong>Pilotage</strong><span>Décollage, maîtrise des axes, trajectoires, retour d'urgence.</span></li><li><strong>Prise de vue</strong><span>Réglages caméra, mouvements cinématographiques, premières images exploitables.</span></li></ol></div></section>
<section class="tight"><div class="wrap prose"><p>La formation s'adresse aux particuliers qui débutent, aux professionnels qui veulent utiliser un drone dans leur activité (immobilier, BTP, agriculture, tourisme) et aux vidéastes qui souhaitent ajouter des plans aériens.</p><p>Je forme en petit groupe ou en individuel pour que chacun pilote réellement. Les dates sont fixées à la demande.</p></div></section>
{faq_html(ffaq)}{contact_block()}'''
    page('/formation-drone', 'Formation pilote drone dans les Landes (A1/A3, A2) | Drone 64-40', "Formation drone de deux jours dans les Landes : réglementation de la catégorie ouverte A1/A3 et A2, préparation du vol, pilotage et prise de vue. Petits groupes.", body, cur='/formation-drone', prio='0.7', schema=[crumbs_ld(it), faq_ld(ffaq)])

    it = [('Accueil', '/'), ('FAQ', '/faq')]
    allfaq = HOME_FAQ + [q for s in SERVICES.values() for q in s['faq'][1:3]]
    body = phero(it, 'Questions <em>fréquentes</em>', "Tarifs, délais, réglementation du drone, réseaux sociaux : les réponses aux questions qu'on me pose le plus souvent.", 'pont-vieux-orthez-drone', 'Pont-Vieux d\'Orthez', ctas=False) + faq_html(allfaq, 'Toutes les réponses') + contact_block()
    page('/faq', 'Questions fréquentes photo, vidéo, drone | Drone 64-40', "Tarifs, délais de livraison, réglementation des vols de drone, community management : les réponses aux questions fréquentes sur les prestations de Drone 64-40.", body, cur='/faq', prio='0.5', schema=[crumbs_ld(it), faq_ld(allfaq)])

    it = [('Accueil', '/'), ('Contact', '/contact')]
    body = phero(it, 'Contact &amp; <em>devis gratuit</em>', "Décrivez votre projet : je vous réponds sous 24 h avec un devis ferme et sans engagement.", 'capbreton-jetee-coucher-soleil', 'Jetée de Capbreton', ctas=False) + contact_block()
    page('/contact', 'Contact et devis gratuit | Drone 64-40', f"Contactez Nicolas Desperiers pour un devis photo, vidéo, drone ou community management : {PHONE}, {EMAIL}. Réponse sous 24 h.", body, cur='/contact', prio='0.6', schema=[crumbs_ld(it)])

    it = [('Accueil', '/'), ('Mentions légales', '/mentions-legales')]
    body = phero(it, 'Mentions <em>légales</em>', "Informations légales sur l'éditeur et l'hébergeur du site drone6440.fr.", 'pont-vieux-orthez-drone', 'Orthez', ctas=False) + f'''<section><div class="wrap prose">
<h2 style="margin-top:0">Éditeur</h2><p>Drone 64-40, SASU<br>1972 route du Pourtaou, 40300 Cauneille<br>Téléphone : {PHONE} · Email : {EMAIL}<br>Directeur de la publication : Nicolas Desperiers</p>
<h2>Hébergement</h2><p>GitHub Pages, GitHub Inc., 88 Colin P Kelly Jr Street, San Francisco, CA 94107, États-Unis.</p>
<h2>Propriété intellectuelle</h2><p>Les photographies, vidéos et textes de ce site sont la propriété de Nicolas Desperiers. Toute reproduction sans autorisation écrite est interdite.</p>
<h2>Données personnelles</h2><p>Ce site ne collecte pas de données via un formulaire en ligne : le formulaire de devis ouvre votre messagerie. Les informations que vous envoyez par email servent uniquement à répondre à votre demande et ne sont pas transmises à des tiers. Vous pouvez demander leur suppression à {EMAIL}.</p>
<h2>Cookies</h2><p>Ce site n'utilise pas de cookies de suivi. Les polices sont chargées depuis Google Fonts.</p></div></section>'''
    page('/mentions-legales', 'Mentions légales | Drone 64-40', "Mentions légales du site drone6440.fr : éditeur, hébergeur, propriété intellectuelle et données personnelles.", body, prio='0.2', schema=[crumbs_ld(it)])

    # 404
    body = phero([('Accueil', '/'), ('Page introuvable', '/404')], 'Page <em>introuvable</em>', "Cette page n'existe pas ou a été déplacée. Voici où aller.", 'capbreton-jetee-coucher-soleil', 'Capbreton', ctas=False) + \
        '<section><div class="wrap"><ul class="chips"><li><a href="/">Accueil</a></li><li><a href="/zones/">Toutes les villes</a></li><li><a href="/videaste/">Vidéo</a></li><li><a href="/photographe/">Photo</a></li><li><a href="/drone/">Drone</a></li><li><a href="/contact">Contact</a></li></ul></div></section>'
    page('/404', 'Page introuvable | Drone 64-40', "Cette page n'existe pas.", body, robots='noindex,follow')

def build_extras():
    # accueil.html : ancienne URL renvoyée vers la racine
    open(OUT + '/accueil.html', 'w').write(f'<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>Drone 64-40</title><link rel="canonical" href="{SITE}/"><meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0; url=/"><script>location.replace("/")</script></head><body><p><a href="/">Aller à l\'accueil de Drone 64-40</a></p></body></html>')
    # sitemap
    urls = ''.join(f'<url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>' for p, pr in pages)
    urls += f'<url><loc>{SITE}/regards/</loc><lastmod>{TODAY}</lastmod><priority>0.6</priority></url><url><loc>{SITE}/boutique</loc><lastmod>{TODAY}</lastmod><priority>0.5</priority></url>'
    open(OUT + '/sitemap.xml', 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(OUT + '/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nDisallow: /admin-boutique.html\n\nSitemap: {SITE}/sitemap.xml\n')
    os.makedirs(OUT + '/assets', exist_ok=True)
    shutil.copy('site.css', OUT + '/assets/site.css')

if __name__ == '__main__':
    build_home(); build_services(); build_service_depts(); build_sectors(); build_cities(); build_zones(); build_misc(); build_extras()
    print(len(pages), 'pages indexables')
