#whoscored.py
import asyncio
from pathlib import Path
import random
from playwright.async_api import async_playwright
import json
import time
from datetime import datetime, timezone, timedelta
from footystats.leagues import *
from footystats.webscrapping import block_ads

async def goToLeague(x:League, path:str):
    """
    """
    #
    cLeague     = leagues[x.value]
    filename    = x.name.lower()+"_sources.json"
    savepath    = Path(path).joinpath(filename)
    #
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
        user_data_dir="./my_profile",
        headless=False,
        args=["--start-maximized",
        # f"--disable-extensions-except={path_to_extension}",
        # f"--load-extension={path_to_extension}"
        ],
        viewport=None,  # Forces full screen
        )
        page = await browser.new_page()

        # ➤ Stealth: remove webdriver flag
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # ==================================================================
        # (0) LOAD MAIN PAGE
        # ==================================================================
        # await block_ads(page)
        await page.goto(cLeague.ws_url)
        # await page.mouse.wheel(random.uniform(100, 550), random.uniform(900, 1500))
        
        html_content = await page.content()
        listbox = soup.find("ul", {"role": "listbox", "class" : "Box klGMtt"})
        
        for ul in soup.find_all('ul' , {"role": "listbox"}):
            print('toto')

        # if listbox:
            # print("Found listbox:")
            # print(listbox.prettify())
        # else:
            # print("No listbox found.")
            
        # if listbox:
        # # Find all <li> inside with role="option"
            # options = listbox.find_all("li", {"role": "option"})
            
            # for opt in options:
                print("Value:", opt.get("value"), "| Text:", opt.get_text(strip=True))
        
        await asyncio.sleep(20)