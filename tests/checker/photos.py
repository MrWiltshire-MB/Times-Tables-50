import asyncio, re
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
# sequences: each line is judged with the accepted (step) lines before it
SEQ = [
 ("container L", "m10K", r"rectangular prism$", "litres", lambda g, q: [], [
   "{d0}×{d1}×{d2}", "{vol}", "{vol} L", "{vol}", "{vol} cm³", "{vol} ÷ 1000", "{ans}", ]),
 ("paper", "m10A", r"pile of (\d+) sheets of paper is (\d+) cm", None, None, ["0.", "0", "0+0", "{b}×10", "20 ÷ {a}", "{ans}"]),
 ("circle C", "m10C", r"The diameter is marked", "circumference", None, ["c = {d} × π", "c = 40.80", "c = 40.80 m", "c = {ansr}", ]),
 ("doorway", "m10A", r"makes a ([\d.]+) m doorway (\d+) mm wider", "cm", None, ["0.9 + 0", "0.", "0+0", "0×0", "0-0", "0-9", "{a}×100", "{b}÷10", "{cm}+{mmcm}", "{ans}", "{ans} cm"]),
]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        for label, t, rx, subrx, _, lines in SEQ:
            q = await pg.evaluate("""([t, rx, subrx]) => { const r = new RegExp(rx), s = subrx && new RegExp(subrx); for (let k = 0; k < 800; k++) for (const q of window.__tt.take(t, 40)) { const h = q.html.replace(/<[^>]+>/g,''); if (q.mwork && r.test(h) && (!s || s.test(q.sub))) return q; } return null; }""", [t, rx, subrx])
            if not q: print("NO Q", label); continue
            h = re.sub(r"<[^>]+>", "", q["html"]); m = re.search(rx, h); g = m.groups() if m else ()
            dia = q.get("dia") or {}
            nums = re.findall(r"[\d.]+", q["calc"])
            sub = {"{ans}": "%g" % q["ans"], "{ansr}": "%.2f" % q["ans"]}
            if label == "container L": sub.update({"{d0}": nums[0], "{d1}": nums[1], "{d2}": nums[2], "{vol}": "%g" % (float(nums[0])*float(nums[1])*float(nums[2]))})
            if label == "paper": sub.update({"{a}": g[0], "{b}": g[1]})
            if label == "circle C": sub.update({"{d}": "%g" % dia.get("v", 0)})
            if label == "doorway": sub.update({"{a}": g[0], "{b}": g[1], "{cm}": "%g" % (float(g[0])*100), "{mmcm}": "%g" % (float(g[1])/10)})
            print(f"== {label}: {h[:60]} | {q['calc']} = {q['ans']} {q.get('suf','')}")
            prev = []
            for ln in lines:
                for k, v in sub.items(): ln = ln.replace(k, v)
                r = await pg.evaluate("([q, l, p]) => window.__tt.judgeLine(l, q, p)", [q, ln, prev])
                print(f"   {ln!r:28} -> {r['kind']:5} {r.get('msg','')[:70]}")
                if r["kind"] == "step": prev.append(ln)
                if r["kind"] == "final": break
        print("errors", errs); await b.close()
asyncio.run(main())
