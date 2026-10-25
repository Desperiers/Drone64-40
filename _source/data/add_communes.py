"""Ajoute des communes des Landes et des Pyrénées-Atlantiques à cities.json."""
import json, math, re, unicodedata, hashlib, sys
sys.path.insert(0, 'data')
from territoires import T, PB_POLES
S = '/tmp/claude-0/-home-claude/904700ec-aa8a-5918-be9a-68b5f05adc89/scratchpad'
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 410
cen = json.load(open(S + '/geo/centres.json'))
com = {c['code']: c for c in json.load(open(S + '/npmtest/package/data/communes.json')) if c['type'] == 'commune-actuelle'}
epci = {}
for e in json.load(open(S + '/npmtest/package/data/epci.json')):
    for m in e.get('membres', []): epci.setdefault(m['code'], e['nom'])
cities = json.load(open('cities.json'))
cities = [c for c in cities if not c.get('auto')]  # repartir propre
def norm(s):
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')
def km(a, b):
    R = 6371; la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(h))
# enrichir les fiches existantes
for c in cities:
    if c['dep'] in ('40', '64') and c['code'] in epci: c['epci'] = epci[c['code']]
have_codes = {c['code'] for c in cities}; have_slugs = {c['slug'] for c in cities}
cur = sum(1 for c in cities if c['dep'] in ('40', '64'))
need = TARGET - cur
pool = sorted([c for c in com.values() if c['departement'] in ('40', '64') and c['code'] not in have_codes and c['code'] in cen],
              key=lambda c: -(c.get('population') or 0))
hubs = [c for c in cities if (c.get('pop') or 0) >= 4000 and c['dep'] in ('40', '64')]
def pole(lat, lon):
    return min(PB_POLES, key=lambda k: km((lat, lon), PB_POLES[k][:2]))
def de(n):
    return "d'" + n if n[0].lower() in 'aeiouyhéèêâîôû' else 'de ' + n
def fmt(n): return f"{n:,}".replace(',', '\u202f')
def size(p):
    return 'petit village' if p < 500 else 'village' if p < 2000 else 'bourg' if p < 5000 else 'ville'
added = 0
for c in pool[:need]:
    lat, lon, _ = cen[c['code']]
    e = epci.get(c['code'], '')
    if e == 'CA du Pays Basque':
        p = pole(lat, lon); terr, phrases, typ = p, PB_POLES[p][2], PB_POLES[p][3]
    elif e in T:
        terr, phrases, typ = T[e]
    else:
        continue
    h = int(hashlib.md5(c['code'].encode()).hexdigest(), 16)
    near = min((x for x in hubs if x['code'] != c['code']), key=lambda x: km((lat, lon), (x['lat'], x['lon'])))
    dn = round(km((lat, lon), (near['lat'], near['lon'])) * 1.25)
    pop = c.get('population') or 0
    art = 'une' if size(pop) == 'ville' else 'un'; dem = 'cette' if size(pop) == 'ville' else 'ce'
    loin = f"à une dizaine de minutes {de(near['nom'])}" if dn <= 12 else f"à environ {dn} km {de(near['nom'])}"
    s2 = [f"{c['nom']} est {art} {size(pop)} de {fmt(pop)} habitants, {loin}.",
          f"Avec ses {fmt(pop)} habitants, {dem} {size(pop)} se situe {loin}."][h % 2]
    ph = phrases[h % len(phrases)]
    lead = ph if not ph.startswith('Ce') else phrases[0] + ' ' + ph
    txt = lead + ' ' + s2
    slug = norm(c['nom'])
    if slug in have_slugs: slug = slug + '-' + c['departement']
    have_slugs.add(slug)
    cities.append({'slug': slug, 'code': c['code'], 'nom': c['nom'], 'dep': c['departement'], 'lat': lat, 'lon': lon,
                   'pop': pop, 'cp': (c.get('codesPostaux') or [''])[0], 'txt': txt,
                   'spots': [terr, f"À {'quelques minutes' if dn <= 12 else f'{dn} km'} {de(near['nom'])}", e.replace('CC ', 'Communauté de communes ').replace('CA ', 'Agglomération ')],
                   'type': typ, 'new': True, 'auto': True, 'epci': e, 'territoire': terr})
    added += 1
for c in cities:
    if not c.get('auto'): continue
    v = sorted((x for x in cities if x['code'] != c['code']), key=lambda x: km((c['lat'], c['lon']), (x['lat'], x['lon'])))[:3]
    c['txt'] += f" Ses communes voisines sont {v[0]['nom']}, {v[1]['nom']} et {v[2]['nom']}."
json.dump(cities, open('cities.json', 'w'), ensure_ascii=False, indent=0)
from collections import Counter
print('ajoutées', added, 'total', len(cities), Counter(c['dep'] for c in cities if c['dep'] in ('40', '64')), 'pop min ajoutée', pool[need-1].get('population'))
