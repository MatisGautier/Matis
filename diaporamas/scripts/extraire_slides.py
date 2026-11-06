import json,sys
d=json.load(open(sys.argv[1]))["content"]
out=[]
for i,s in enumerate(d["slides"],1):
    blocs=[]
    def walk(els):
        for e in els:
            if "elementGroup" in e: walk(e["elementGroup"].get("children",[]))
            sh=e.get("shape")
            if sh and "text" in sh:
                t="".join(te.get("textRun",{}).get("content","") for te in sh["text"].get("textElements",[]))
                t=t.strip()
                if t:
                    tr=e.get("transform",{}); 
                    blocs.append({"y":tr.get("translateY",0),"x":tr.get("translateX",0),"t":t})
            tb=e.get("table")
            if tb:
                rows=[]
                for r in tb.get("tableRows",[]):
                    cells=[]
                    for c in r.get("tableCells",[]):
                        t="".join(te.get("textRun",{}).get("content","") for te in c.get("text",{}).get("textElements",[]))
                        cells.append(t.strip().replace("\n"," "))
                    rows.append(cells)
                tr=e.get("transform",{})
                blocs.append({"y":tr.get("translateY",0),"x":tr.get("translateX",0),"table":rows})
            if "image" in e:
                tr=e.get("transform",{})
                blocs.append({"y":tr.get("translateY",0),"x":tr.get("translateX",0),"image":1})
    walk(s.get("pageElements",[]))
    blocs.sort(key=lambda b:(round(b["y"]/200000),b["x"]))
    out.append({"n":i,"blocs":blocs})
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)
print(len(out))
