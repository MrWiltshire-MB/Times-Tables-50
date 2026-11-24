import os  # teacher code comes from the TT_CODE environment variable (never stored in the repo)
import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes")
        print("footer:", (await pg.inner_text("#tmode")).replace("\n"," | "))
        modal = lambda: pg.evaluate("() => !document.getElementById('bkModal').hidden")
        for i in range(4): await pg.click("#logo span")
        print("after 4 taps:", await modal())
        await pg.click("#logo span"); print("after 5 taps:", await modal())
        await pg.fill("#ulPin", os.environ["TT_CODE"]); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(1500)
        print("teacher footer:", (await pg.inner_text("#tmode")).replace("\n"," | "))
        await pg.click("[data-tmode=off]"); print("back to student:", (await pg.inner_text("#tmode")).replace("\n"," | "))
        for i in range(5): await pg.click("#logo", position={"x": 10, "y": 10})
        print("5 taps on 'Times Tables' words (not 50):", await modal())
        await pg.click("[data-open='topic:ch10']"); await pg.click("#logo span"); await pg.wait_for_timeout(100)
        print("logo from topic page goes home:", await pg.evaluate("() => !document.getElementById('homeView').hidden"), errs)
        await b.close()
asyncio.run(main())
