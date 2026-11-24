import asyncio, sys, uuid
sys.path.insert(0, "/home/claude/github-pages/test")
from mock import Mock
from flow2 import ctx, page, signin
from playwright.async_api import async_playwright
async def main():
    mock = Mock(teachers=set()); mock.users["x.y@schools.vic.edu.au"] = {"id": str(uuid.uuid4()), "pw": "pw123456"}
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); c = await ctx(b, mock)
        p, errs = await page(c); await signin(p, "x.y@schools.vic.edu.au", "pw123456")
        await p.click("#ngSave"); await p.click("#ngYes"); await p.wait_for_timeout(2500)
        print("signed in, row:", len(mock.rows))
        mock.users.pop("x.y@schools.vic.edu.au"); mock.rows.clear()   # teacher deletes it
        # A: still on page, answers a question -> push fails -> signed out
        await p.click("[data-gp='10A']"); await p.wait_for_timeout(300)
        inp = p.locator("#quiz input:visible").first; await inp.fill("1"); await inp.press("Enter"); await p.wait_for_timeout(3500)
        print("A after push: login shown:", await p.is_visible(".au-box"), "| msg:", (await p.inner_text(".au-note") if await p.locator(".au-note").count() else "none"), "| local:", await p.evaluate("() => localStorage.getItem('tt50-v2')"))
        # B: another device opening the app later
        mock.users["z.w@schools.vic.edu.au"] = {"id": str(uuid.uuid4()), "pw": "pw123456"}
        q, _ = await page(await ctx(b, mock)); await signin(q, "z.w@schools.vic.edu.au", "pw123456")
        mock.users.pop("z.w@schools.vic.edu.au"); await q.reload(); await q.wait_for_timeout(1200)
        print("B on reopen: login shown:", await q.is_visible(".au-box"))
        print("errs", errs); await b.close()
asyncio.run(main())
