import os  # teacher code comes from the TT_CODE environment variable (never stored in the repo)
import asyncio, datetime
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
TZ=datetime.timezone(datetime.timedelta(hours=11))
exec(open(S+"/run40.py").read().split("async def main")[0].split("TZ=")[1].split("\n",1)[1])
async def tb(pg): return (await pg.text_content("#todayBox")).split()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs=[]
        pg = await b.new_page(viewport={"width":1366,"height":850}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,11,10,0,tzinfo=TZ)); await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes"); await pg.wait_for_timeout(150)
        print("home: box hidden:", await pg.is_hidden("#todayBox"))
        await pg.click("[data-gp='10A']"); await pg.wait_for_timeout(150)
        for i in range(3): await answer(pg)
        await answer(pg, wrong=True); await answer(pg)   # wrong then corrected: 1 tried, 0 right
        await answer(pg)
        print("after 5 (1 wrong):", await tb(pg))
        await pg.screenshot(path=S+"/today-wide.png")
        # restart: throw away
        await pg.click("#home"); await pg.click("#lvDrop"); await pg.wait_for_timeout(100)
        await pg.click("[data-gp='10A']"); await pg.wait_for_timeout(150)
        print("after restart, still counted:", await tb(pg))
        for i in range(2): await answer(pg)
        print("after 2 more:", await tb(pg))
        await pg.reload(); await pg.wait_for_timeout(300)
        await pg.click("#resumeGo") if await pg.is_visible("#resumeGo") else None
        await pg.wait_for_timeout(150); print("after reload:", await tb(pg))
        # next day resets
        await pg.clock.set_fixed_time(datetime.datetime(2026,11,12,10,0,tzinfo=TZ)); await pg.reload(); await pg.wait_for_timeout(300)
        await pg.click("#resumeGo") if await pg.is_visible("#resumeGo") else await pg.click("[data-gp='10A']")
        await pg.wait_for_timeout(150); print("next day:", await tb(pg))
        # narrow screen
        await pg.set_viewport_size({"width":800,"height":900}); await pg.wait_for_timeout(100)
        await pg.screenshot(path=S+"/today-narrow.png")
        # name change
        await pg.click("#home"); await pg.click("#lvSave") if await pg.is_visible("#lvSave") else None; await pg.wait_for_timeout(150)
        print("name readonly:", await pg.get_attribute("#stuName", "readonly") is not None, "| change link:", await pg.is_visible("#nameChange"))
        await pg.click("#nameChange"); await pg.fill("#ulPin", "1111"); await pg.click("#ulGo"); await pg.wait_for_timeout(1500)
        print("wrong code:", await pg.text_content("#bkMsg"), "| still readonly:", await pg.get_attribute("#stuName", "readonly") is not None)
        await pg.fill("#ulPin", os.environ["TT_CODE"]); await pg.click("#ulGo"); await pg.wait_for_timeout(1500)
        print("right code -> editable:", await pg.get_attribute("#stuName", "readonly") is None, "| focused:", await pg.evaluate("() => document.activeElement.id"))
        await pg.fill("#stuName", "Ava Smith-Jones"); await pg.press("#stuName", "Enter"); await pg.wait_for_timeout(100)
        print("saved name:", await pg.evaluate("() => window.__tt.P().name"), "| locked again:", await pg.get_attribute("#stuName", "readonly") is not None)
        await pg.reload(); await pg.wait_for_timeout(300); print("after reload:", await pg.input_value("#stuName"))
        print("errors", errs); await b.close()
asyncio.run(main())
