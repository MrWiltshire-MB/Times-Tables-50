import asyncio, sys, uuid
sys.path.insert(0, "/home/claude/github-pages/test")
from mock import Mock
from flow2 import ctx, page, signin
from playwright.async_api import async_playwright
SS = "/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad/"
async def main():
    mock = Mock(teachers=set()); mock.users["anthony.chui@education.vic.gov.au"] = {"id": str(uuid.uuid4()), "pw": "testpass12"}
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        p, errs = await page(await ctx(b, mock))
        msgs = []; p.on("console", lambda m: msgs.append(m.text) if m.type in ("error", "warning") else None)
        await signin(p, "anthony.chui@education.vic.gov.au", "testpass12"); await p.wait_for_timeout(500)
        if await p.is_visible("#ngSave"): await p.click("#ngSave"); await p.click("#ngYes"); await p.wait_for_timeout(300)
        btns = await p.evaluate("() => [...document.querySelectorAll('button')].filter(b => b.offsetParent && /Open/.test(b.textContent)).map(b => b.outerHTML.slice(0,150))")
        print(btns)
        await p.click("[data-gp='10A']"); await p.wait_for_timeout(900)
        print("green post 10A -> quiz visible:", await p.is_visible("#quiz"), "|", (await p.inner_text("#qnum")).strip())
        await p.click("#homeBtn") if await p.is_visible("#homeBtn") else None
        await p.screenshot(path=SS + "open.png")
        print("errs", errs, msgs[:5])
        await b.close()
asyncio.run(main())
