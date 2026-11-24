import asyncio, collections
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
LET = {"m10B": "P", "m10C": "C", "m10D": "P", "m10E": "A", "m10F": "A", "m10G": "A", "m10H": "A", "m10I": "V", "m10J": "V", "m10K": "V", "m10A": "L", "m10L": "M"}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        res = await pg.evaluate("""(LET) => { const out = [];
          for (const t of Object.keys(LET)) for (let k = 0; k < 40; k++) for (const q of window.__tt.take(t, 20)) {
            if (!q.mwork || !q.model) continue;
            const fm = /Find (?:its|the) (width|diameter|radius|base|height|length|side)/i.exec(q.sub || ""), L = fm ? ({ width: "w", diameter: "d", radius: "r", base: "b", height: "h", length: "l", side: "s" })[fm[1].toLowerCase()] : LET[t], m0 = q.model[0], fin = q.model[q.model.length - 1];
            const plain = window.__tt.judgeLine(m0, q, []), lab = window.__tt.judgeLine(L + " = " + m0, q, []);
            const finL = window.__tt.judgeLine(L + " = " + String(fin).replace(/^[$]/, ""), q, [m0]);
            const key = t + " | " + q.html.replace(/<[^>]+>/g, " ").replace(/\\d+(\\.\\d+)?/g, "#").slice(0, 60) + " | " + (q.sub || "").replace(/\\d+/g, "#").slice(0, 40);
            if (plain.kind !== "wrong" && plain.kind !== "say" && (lab.kind === "wrong" || lab.kind === "say")) out.push(["lab", key, L + " = " + m0, lab.kind + " " + (lab.msg || "")]);
            if (finL.kind !== "final") out.push(["fin", key, L + " = " + fin, finL.kind + " " + (finL.msg || "")]);
          } return out; }""", LET)
        c = collections.OrderedDict()
        for kind, key, ln, r in res: c.setdefault((kind, key), []).append((ln, r))
        for (kind, key), v in c.items(): print(f"{kind} {len(v):3}x {key}\n      e.g. {v[0][0]!r} -> {v[0][1]}")
        print("total", len(res)); await b.close()
asyncio.run(main())
