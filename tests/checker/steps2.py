import asyncio, datetime
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,11,16,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
        res = await pg.evaluate("""async () => {
          const fails = [], junkPass = [], n = { q: 0 };
          const run = async (q, lines) => { window.__tt.showQ(q); const out = [];
            for (const ln of lines) { const inp = document.getElementById('wInput'); if (!inp) { out.push('done'); break; }
              inp.value = ln; document.getElementById('wForm').requestSubmit(); const fb = document.getElementById('feedback'); out.push(fb.className + '|' + fb.textContent.slice(0, 30)); }
            return out; };
          for (const k of Object.keys(window.__tt.T).filter(k => k[0] === 'm')) {
            for (const q of window.__tt.take(k, 30)) {
              if (!q.mwork) continue; n.q++;
              const a = await run(q, q.model);
              if (!/Correct/.test(a[a.length - 1])) fails.push(k + ' model: ' + q.calc + ' -> ' + a.join(' / '));
              const j = await run(q, ['1+1']);
              if (!/bad/.test(j[0])) junkPass.push(k + ' ' + q.calc + ' -> ' + j[0]);
              const j2 = await run(q, [String(q.ans + 7) + '+0']);
              if (!/bad/.test(j2[0])) junkPass.push(k + ' ' + q.calc + ' ans+7 -> ' + j2[0]);
            }
          }
          // leaf rule and radius
          let lq = null; for (let r = 0; r < 300 && !lq; r++) lq = window.__tt.take('m10B', 40).find(q => /perimeter of 3\\d cm and a length of 1[1-9] cm/.test(q.html));
          const leaf = lq ? await run(lq, [String(lq.html.match(/perimeter of (\\d+)/)[1])]) : ['none'];
          let rq = null; for (let r = 0; r < 300 && !rq; r++) rq = window.__tt.take('m10C', 40).find(q => q.mwork && /radius/.test(q.sub) && /circumference of/.test(q.html));
          const C = rq && +rq.html.match(/circumference of ([\\d.]+)/)[1];
          const rad = rq ? await run(rq, ['2×π', C + ' ÷ 6.28', String(rq.ans)]) : ['none'];
          return { n: n.q, fails: fails.slice(0, 10), nf: fails.length, junkPass: junkPass.slice(0, 40), nj: junkPass.length, leaf: (lq ? lq.html : '') + ' -> ' + leaf, rad: (rq ? rq.html + ' ans ' + rq.ans : '') + ' -> ' + rad.join(' / ') };
        }""")
        for k, v in res.items(): print(k, v)
        print("errors", errs[:3]); await b.close()
asyncio.run(main())
