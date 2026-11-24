import asyncio, sys, uuid
sys.path.insert(0, "/home/claude/github-pages/test")
from mock import Mock
from flow2 import ctx, page, signin
from playwright.async_api import async_playwright
async def main():
    mock = Mock(teachers={"sam.wiltshire@education.vic.gov.au"}); mock.users["sam.wiltshire@education.vic.gov.au"] = {"id": str(uuid.uuid4()), "pw": "teacherpass1"}
    for e in ["a.one@schools.vic.edu.au", "b.two@schools.vic.edu.au", "c.three@schools.vic.edu.au"]: mock.users[e] = {"id": str(uuid.uuid4()), "pw": "pw123456"}
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        s, _ = await page(await ctx(b, mock)); await signin(s, "a.one@schools.vic.edu.au", "pw123456")
        print("a.one has progress row:", len(mock.rows))
        t, errs = await page(await ctx(b, mock), "teacher.html"); await signin(t, "sam.wiltshire@education.vic.gov.au", "teacherpass1")
        print("before:", sorted(e for e in mock.users if "schools" in e))
        await t.click("tr[data-e='a.one@schools.vic.edu.au']"); await t.click("[data-del]"); await t.wait_for_timeout(600)
        print("after one:", sorted(e for e in mock.users if "schools" in e), "rows:", len(mock.rows), "| table:", (await t.inner_text("#rows")).count("@schools"))
        await t.click("#delAll"); await t.wait_for_timeout(1000)
        print("after all:", sorted(e for e in mock.users if "schools" in e), "teacher kept:", "sam.wiltshire@education.vic.gov.au" in mock.users, "| table:", (await t.inner_text("#rows")).strip()[:40])
        print("errs", errs); await b.close()
asyncio.run(main())
