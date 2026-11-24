import asyncio
from playwright.async_api import async_playwright
S="/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+S+"/harness.html"); await pg.wait_for_timeout(300)
        await pg.fill("#ngName","Ava Smith"); await pg.click("#ngSave"); await pg.click("#ngYes")
        vis = lambda: pg.evaluate("() => ['homeView','topicView','quiz','leaveModal'].filter(i => !document.getElementById(i).hidden)")
        await pg.click("[data-open='topic:ch10']"); print("topic:", await vis())
        await pg.click("#logo"); await pg.wait_for_timeout(200); print("after logo:", await vis())
        await pg.click("[data-gp='10A']"); await pg.wait_for_timeout(300)
        inp = pg.locator("#quiz input:visible").first; await inp.fill("1"); await inp.press("Enter"); await pg.wait_for_timeout(200)
        await pg.click("#logo"); await pg.wait_for_timeout(200); print("logo mid-round:", await vis())
        await pg.click("#lvStay"); await pg.click("#logo"); await pg.click("#lvDrop"); await pg.wait_for_timeout(200); print("exit:", await vis())
        await pg.click("#logo"); print("logo on home:", await vis(), errs); await b.close()
asyncio.run(main())
