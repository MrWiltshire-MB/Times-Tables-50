import asyncio, datetime
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
exec(open(S+"/run40.py").read().split("async def main")[0].split("TZ=")[1].split("\n",1)[1])
async def lock(pg): return (await pg.text_content("#lockText"))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1366,"height":1000}); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,19,10,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
        print("start:", await lock(pg))
        await pg.click("#lockText [data-req='10A']"); await pg.wait_for_timeout(150)
        for i in range(20): await answer(pg)
        print("results msg hidden after first 10A:", await pg.is_hidden("#lockMsg"))
        await pg.click("#toHome"); await pg.wait_for_timeout(150)
        print("after 10A:", await lock(pg))
        print("10A disabled:", await pg.is_disabled("#lockText button:has-text('10A')"))
        # 10A again via the green post chip
        await pg.click("[data-gp='10A']"); await pg.wait_for_timeout(150)
        for i in range(20): await answer(pg)
        print("results msg:", await pg.text_content("#lockMsg"))
        await pg.click("#toHome"); await pg.wait_for_timeout(150)
        print("after 10A again:", (await lock(pg))[:70])
        # mixed round 10A+10B: only 10B questions count
        await pg.evaluate("() => { const s = window.__tt.store().settings; s.me = ['10A','10B']; s.len = 20; window.__tt.save(); }")
        await pg.locator(".tile button[data-open^='topic']").first.click(); await pg.wait_for_timeout(150)
        await pg.click("#topicStart"); await pg.wait_for_timeout(150)
        for i in range(20): await answer(pg)
        print("mixed results msg:", await pg.text_content("#lockMsg"))
        await pg.click("#toHome"); await pg.wait_for_timeout(150)
        print("after mix:", (await lock(pg))[:70])
        await pg.locator("#lockNote").screenshot(path=S+"/locknote.png") if await pg.is_visible("#lockNote") else None
        # all parts done -> everything counts
        await pg.evaluate("""() => { const p = window.__tt.P(), d = Date.parse('2026-11-18T01:00:00Z');
          ['10B','10C','10D','10E','10F','10G','10H','10I','10J','10K','10L'].forEach((x, i) => p.history.push({ d: d + i, m: 'measurement', s: 20, n: 20, ms: 1, missed: [], parts: { ['m' + x]: [20, 20] }, lc: 20 })); window.__tt.save(); }""")
        await pg.reload(); await pg.wait_for_timeout(300); print("all done:", (await lock(pg))[:160])
        print("errors", errs); await b.close()
asyncio.run(main())
