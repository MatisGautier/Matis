import json,sys,re
def esc(t): 
    t=t.replace("<","&lt;").replace(">","&gt;")
    return t
d=json.load(open(sys.argv[1])); slides_id=sys.argv[2]
out=[]
titre1=[b["t"] for b in d[0]["blocs"] if "t" in b]
out+=['<callout icon="🎓" color="purple_bg">',f"<b>{esc(titre1[-1])}</b>\\",esc(titre1[1])+"\\" if len(titre1)>2 else "","\\" if False else "",f"Version du {esc(titre1[2])}" if len(titre1)>3 else "","</callout>",""]
out=[l for l in out if l!=""]+[""]
out+=['<toggle heading="h3">',"🖥️ Voir le diaporama","",f'<embed source="https://docs.google.com/presentation/d/{slides_id}/embed">Diaporama du cours</embed>',"</toggle>","","<table-of-contents />",""]
prof=False; corr=False; surtitres=set()
def close():
    global prof,corr
    if prof or corr: out.extend(["</toggle>",""])
    prof=corr=False
for s in d[1:]:
    txt=[b for b in s["blocs"] if "image" not in b]
    texts=[b["t"] for b in txt if "t" in b]
    texts=[t for t in texts if not re.fullmatch(r"\d{1,3}",t)]
    if not texts and not any("table" in b for b in txt): continue
    if len(texts)==1 and not any("table" in b for b in txt):
        t=texts[0]
        close()
        if "profondeur" in t.lower():
            out+=['<toggle heading="h2">',"🔬 Pour aller plus en profondeur",""]; prof=True
        else:
            out+=["---",f"## {esc(t)}",""]; surtitres.add(t.lstrip("0123456789. ").strip())
        continue
    # retirer le surtitre (répétition du nom de section)
    if texts and (texts[0] in surtitres or texts[0].lower().startswith("pour aller plus")): texts=texts[1:]
    if not texts: continue
    if texts[0].upper()==texts[0] and texts[0] not in ("PLAN",):
        titre=texts[0][0]+texts[0][1:].lower(); body=texts[1:]
    else:
        titre=texts[0]; body=texts[1:]
    if titre.strip().upper()=="PLAN": continue
    T=titre.upper()
    if T.startswith("CORRIG") and not corr:
        close(); out+=['<toggle heading="h3">',"✅ Corrigé (cliquer pour afficher)",""]; corr=True
    elif corr and not T.startswith("CORRIG"): close()
    if prof and (T.startswith(("TESTEZ","LIENS","NOUVEAUT","RÉFÉRENCES","HISTORIQUE","ARTICLES PHARES"))): close()
    sources=[]; concl=[]; lignes=[]
    for t in body:
        for l in t.split("\n"):
            l=l.strip()
            if not l or re.fullmatch(r"\d{1,3}",l): continue
            if l.startswith("Sources"): sources.append(l)
            elif l.startswith(">"): concl.append(l.lstrip("> "))
            else: lignes.append(l)
    tables=[b["table"] for b in txt if "table" in b]
    ref = T.startswith("RÉFÉRENCES")
    phares = T.startswith("ARTICLES PHARES")
    retenir = T.startswith("À RETENIR")
    def rouge(x): return f'<span color="red"><b>{x}</b></span>'
    def src(l):
        pre=""
        if l.startswith("Sources :"): pre,l="Sources : ",l[len("Sources :"):].strip()
        parts=l.split(" ; ")
        return pre+" ; ".join(rouge(esc(p)) if "★" in p else esc(p) for p in parts)
    if phares:
        out+=['<callout icon="⭐" color="red_bg">',rouge(esc(titre)),""]+["- "+rouge(esc(l)) for l in lignes]+["</callout>",""]; continue
    if ref:
        out+=['<toggle heading="h3">',f"📚 {esc(titre)}",""]+["- "+(rouge(esc(l)) if "★" in l else esc(l)) for l in lignes]+["</toggle>",""]; continue
    if retenir:
        out+=['<callout icon="📌" color="green_bg">',f"<b>{esc(titre)}</b>",""]
        if lignes: out+=[esc(lignes[0]),""]+["- "+esc(l) for l in lignes[1:]]
        out+=["</callout>"]
    else:
        out.append(f"### {esc(titre)}")
        for tb in tables:
            out.append("| "+" | ".join(esc(c).replace("|","\\|") for c in tb[0])+" |")
            out.append("| "+" | ".join("---" for _ in tb[0])+" |")
            for r in tb[1:]: out.append("| "+" | ".join(esc(c).replace("|","\\|") for c in r)+" |")
        for l in lignes:
            out.append(esc(l) if re.match(r"^\d+\. ",l) else "- "+esc(l))
        for c in concl: out+=['<callout icon="👉" color="yellow_bg">',esc(c),"</callout>"]
    for l in sources: out.append(f'<p color="gray">{src(l)}</p>')
    out.append("")
close()
sys.stdout.write("\n".join(out))
