import asyncio, re, sys, uuid
sys.path.insert(0, "/home/claude/github-pages/test")
from mock import Mock
from flow2 import ctx, page, signin
from playwright.async_api import async_playwright
SS = "/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad/"
async def main():
    mock = Mock(teachers={"sam.wiltshire@education.vic.gov.au"}); mock.users["sam.wiltshire@education.vic.gov.au"] = {"id": str(uuid.uuid4()), "pw": "teacherpass1"}
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        t, eT = await page(await ctx(b, mock), "teacher.html"); await signin(t, "sam.wiltshire@education.vic.gov.au", "teacherpass1")
        await t.click("#addOpen"); await t.fill("#addList", "tiger482\nAva.S\nbad name here\nliam.nguyen3@schools.vic.edu.au\n\nTiger482")
        await t.click("#addGo"); await t.wait_for_timeout(1200)
        res = await t.inner_text("#addRes"); print(res)
        pws = dict(re.findall(r"\((\S+)\): (\S+)", res)); print(pws)
        print("users:", sorted(mock.users))
        await t.click("#reload"); await t.wait_for_timeout(400); print("table:", (await t.inner_text("#rows")).replace("\n", " | ")[:220])
        s, eS = await page(await ctx(b, mock)); await signin(s, "TIGER482 ", pws["tiger482"])
        print("in:", not await s.is_visible(".au-box"), "| gate prefill:", repr(await s.input_value("#ngName")), "| bar:", (await s.inner_text(".cl-bar")).replace("\n", " "))
        await s.screenshot(path=SS + "un_app.png")
        l, eL = await page(await ctx(b, mock)); await signin(l, "liam.nguyen3@schools.vic.edu.au", pws["liam.nguyen3@schools.vic.edu.au"]); print("email still works:", not await l.is_visible(".au-box"))
        x, _ = await page(await ctx(b, mock)); await signin(x, "no such", "x"); print("bad:", await x.inner_text(".au-msg"))
        await x.screenshot(path=SS + "un_login.png")
        print("errs", eT, eS, eL); await b.close()
asyncio.run(main())
