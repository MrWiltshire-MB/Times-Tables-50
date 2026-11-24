import asyncio, re, sys, uuid
sys.path.insert(0, "/home/claude/github-pages/test")
from mock import Mock
from playwright.async_api import async_playwright
OUT = "/home/claude/github-pages/out"; SS = "/tmp/claude-0/-home-claude/f078b626-45d1-5efe-90ef-0b98a47fb3b1/scratchpad/"
async def ctx(b, mock):
    c = await b.new_context(viewport={"width": 1280, "height": 850}, timezone_id="Australia/Melbourne")
    await c.route("https://xovilczevfaqwhtuxsnw.supabase.co/**", mock.handle); await c.route("https://fonts.googleapis.com/**", lambda r: r.abort())
    await c.route("https://mrwiltshire-mb.github.io/**", lambda r: r.fulfill(path=OUT + "/" + (r.request.url.split("/Times-Tables-50/")[1].split("?")[0] or "index.html"), content_type="text/html"))
    return c
async def page(c, f="index.html"):
    p = await c.new_page(); errs = []; p.on("pageerror", lambda e: errs.append(str(e))); p.on("dialog", lambda d: asyncio.ensure_future(d.accept("DELETE") if d.type == "prompt" else d.accept()))
    await p.goto("https://mrwiltshire-mb.github.io/Times-Tables-50/" + f); await p.wait_for_timeout(400); return p, errs
async def signin(p, e, pw):
    await p.fill("[name=em]", e); await p.fill("[name=pw]", pw); await p.click(".au-go"); await p.wait_for_timeout(700)
async def main():
    mock = Mock(teachers={"sam.wiltshire@education.vic.gov.au"})
    mock.users["sam.wiltshire@education.vic.gov.au"] = {"id": str(uuid.uuid4()), "pw": "teacherpass1"}
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        t, eT = await page(await ctx(b, mock), "teacher.html")
        await signin(t, "sam.wiltshire@education.vic.gov.au", "teacherpass1")
        await t.click("#addOpen")
        await t.fill("#addList", "Ava Smith <ava.smith@schools.vic.edu.au>; liam.nguyen3@schools.vic.edu.au\nAnthony.Chui@education.vic.gov.au\nbad@gmail.com\nava.smith@schools.vic.edu.au")
        await t.click("#addGo"); await t.wait_for_timeout(1200)
        res = await t.inner_text("#addRes"); print(res)
        pws = dict(re.findall(r"\((\S+@schools\.vic\.edu\.au)\): (\S+)", res))
        await t.screenshot(path=SS + "cl_add.png", full_page=True)
        print("table:", (await t.inner_text("#rows")).replace("\n", " | ")[:200])
        # student signs in with slip password
        s, eS = await page(await ctx(b, mock))
        await signin(s, "ava.smith@schools.vic.edu.au", "nope"); print("wrong:", await s.inner_text(".au-msg"))
        await signin(s, "ava.smith@schools.vic.edu.au", pws["ava.smith@schools.vic.edu.au"])
        print("student in, gate prefill:", await s.input_value("#ngName"), "| bar:", (await s.inner_text(".cl-bar")).replace("\n", " "))
        await s.screenshot(path=SS + "cl_login2.png")
        # teacher resets Liam's password
        await t.click("#reload"); await t.wait_for_timeout(400)
        await t.click("tr[data-e='liam.nguyen3@schools.vic.edu.au']"); await t.wait_for_timeout(200)
        await t.click("[data-reset]"); await t.wait_for_timeout(500)
        newpw = (await t.inner_text(".det .pw")).strip(); print("reset pw:", newpw, mock.users["liam.nguyen3@schools.vic.edu.au"]["pw"] == newpw)
        await t.screenshot(path=SS + "cl_reset.png", full_page=True)
        l, eL = await page(await ctx(b, mock)); await signin(l, "liam.nguyen3@schools.vic.edu.au", newpw)
        print("liam in:", not await l.is_visible(".au-box"))
        print("errors:", eT, eS, eL); await b.close()
if __name__ == "__main__": asyncio.run(main())
