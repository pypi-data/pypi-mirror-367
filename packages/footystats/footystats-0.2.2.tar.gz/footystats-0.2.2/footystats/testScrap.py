import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape(url:str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent="Mozilla/5.0")
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        print(soup.prettify()[:1000])
        await browser.close()
        return soup

# awaits scrap()
toto=asyncio.run(scrape())

print(toto)
