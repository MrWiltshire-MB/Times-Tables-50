import asyncio, datetime
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
exec(open(S+"/run40.py").read().split("async def main")[0].split("TZ=")[1].split("\n",1)[1])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1366,"height":1000}); errs=[]
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,19,16,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
        tiles = await pg.locator("#topicTiles h3").all_text_contents(); print("student tiles:", tiles, "| tick btn hidden:", await pg.is_hidden("[data-tick]"))
        # put an equations tricky question in, check it's hidden
        await pg.evaluate("() => { const q = window.__tt.take('eq9A', 1)[0]; window.__tt.P().tricky['x'] = { q, streak: 0, misses: 1 }; window.__tt.save(); }")
        await pg.reload(); await pg.wait_for_timeout(300); print("tricky chip hidden (only eq):", await pg.is_hidden("#trickyChip"))
        # student does 10A for real
        await pg.click("[data-gp='10A']"); await pg.wait_for_timeout(150)
        for i in range(20): await answer(pg)
        await pg.click("#toHome"); await pg.wait_for_timeout(150)
        # teacher mode
        await pg.evaluate("() => { window.__tt.store().settings.teacher = true; window.__tt.save(); }"); await pg.reload(); await pg.wait_for_timeout(300)
        print("teacher tiles:", await pg.locator("#topicTiles h3").all_text_contents(), "| tick btns:", await pg.locator("[data-tick]:visible").count())
        await pg.locator("[data-tick]").first.click(); await pg.wait_for_timeout(150)
        print("panel parts:", await pg.locator("[data-tk^='p:']").all_text_contents())
        print("10A real:", await pg.get_attribute("[data-tk='p:10A']", "class"))
        await pg.click("[data-tk='p:10A']"); await pg.wait_for_timeout(50); print("10A still on after tap:", "on" in await pg.get_attribute("[data-tk='p:10A']", "class"))
        for x in ["10B","10C","10D","10E","10F"]: await pg.click(f"[data-tk='p:{x}']"); await pg.wait_for_timeout(30)
        print("GP offer:", await pg.locator(".tk-gp").all_text_contents())
        await pg.click("[data-tk='p:10C']"); await pg.wait_for_timeout(30); print("untick 10C -> offer gone:", await pg.locator(".tk-gp").count())
        await pg.click("[data-tk='p:10C']"); await pg.wait_for_timeout(30)
        await pg.click("[data-tkgp='set:10A-10F:1']"); await pg.wait_for_timeout(50)
        print("after 'already had it': offer:", await pg.locator(".tk-gp").count(), "| vouchers:", await pg.evaluate("() => window.__tt.P().vouchers.map(v => [v.grp, v.used])"))
        for w in ["hw1","hw2"]: await pg.click(f"[data-tk='h:{w}']"); await pg.wait_for_timeout(30)
        print("hw offer:", await pg.locator(".tk-gp").all_text_contents())
        await pg.click("[data-tkgp='hw:hw2:0']"); await pg.wait_for_timeout(50)
        await pg.screenshot(path=S+"/tick.png")
        await pg.click("#bkBox [data-bk-close]"); await pg.wait_for_timeout(200)
        print("home GP chips:", await pg.text_content("#gpParts"))
        print("hw weeks:", await pg.text_content("#hwWeeks"))
        print("rewards waiting:", await pg.evaluate("() => window.__tt.P().vouchers.filter(v => !v.used).map(v => v.grpLabel)"), "| points:", await pg.evaluate("() => window.__tt.P().points"))
        # back to student: equations hidden, ticks persist
        await pg.evaluate("() => { window.__tt.store().settings.teacher = false; window.__tt.save(); }"); await pg.reload(); await pg.wait_for_timeout(300)
        print("student again tiles:", await pg.locator("#topicTiles h3").all_text_contents(), "| GP after ticks (new cycle needs 100%):", await pg.text_content("#gpParts"))
        print("errors", errs); await b.close()
asyncio.run(main())
