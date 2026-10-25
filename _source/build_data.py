import sys,json
sys.path.insert(0,'data'); sys.path.insert(0,'/tmp/claude-0/-home-claude/904700ec-aa8a-5918-be9a-68b5f05adc89/scratchpad/geo')
from lib import find, rec, S
import c40,c64,cother,cna
C={**c40.C,**c64.C,**cother.C}; NEW={**c40.NEW,**c64.NEW,**cother.NEW}
ex=json.load(open(S+'/existing.json'))
out=[];miss=[]
for r in ex:
    if r['slug'] not in C: miss.append(r['slug']); continue
    t,sp,ty=C[r['slug']]; r.update(txt=t,spots=sp.split('|'),type=ty,new=False); out.append(r)
depmap={'40':'40','64':'64','33':'33','47':'47'}
for slug,(nom,t,sp,ty) in NEW.items():
    dep='64' if slug in c64.NEW else '40' if slug in c40.NEW else ('47' if slug in ('agen','marmande','villeneuve-sur-lot','nerac') else '33')
    c=find(nom,dep)
    if len(c)!=1: miss.append((slug,c)); continue
    r=rec(slug,c[0],nom); r.update(txt=t,spots=sp.split('|'),type=ty,new=True); out.append(r)
for slug,(dep,nom,t,sp,ty) in cna.NEW.items():
    c=find(nom,dep)
    if len(c)!=1: miss.append((slug,c)); continue
    r=rec(slug,c[0],nom); r.update(txt=t,spots=sp.split('|'),type=ty,new=True); out.append(r)
print(len(out),'missing:',miss)
json.dump(out,open('cities.json','w'),ensure_ascii=False,indent=0)
