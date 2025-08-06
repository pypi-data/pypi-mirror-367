#sofascore.py
from footystats.leagues import *
from footystats.webscrapping import *
from playwright.async_api import async_playwright
from playwright.async_api import Page
from footystats.webscrapping import LOCATIONS
import asyncio
#
from pathlib import Path
import json, pickle
import time
from datetime import datetime, timezone, timedelta

sofaroot:str="https://www.sofascore.com"

async def makeMatchRegister(x: League, path: str, current: bool) -> None:
    """
    Scrape match information for one or more leagues from Sofascore and
    save the results to disk as pickle files.

    Behavior:
      - Validates that `x` is an instance of the `Leagues` enum.
      - Ensures that the output directory `path` exists.
      - If `x == Leagues.ALL`, iterates through all available leagues 
        except the one with value 12.
      - For each target league:
          * Uses either `makeLeagueCurrentSeasonRegister` (if 
            `current=True`) or `makeLeaguePastSeasonRegister` (if 
            `current=False`) to gather match data.
          * Serializes the resulting dictionary into a `.pkl` file 
            named `<league>_match_register.pkl` inside the given path.

    Data organization in each pickle file:
      {
        "<league_name>": {
          "<season_name>": {
            "<round_name>": {
              ... match data from getMatchLinks() ...
            }
          }
        }
      }

    ⚠️ Notes:
      - Persistent browsing and random geolocation are applied inside
        the delegated league functions.
      - The `.pkl` files must be read with `pickle.load` when consumed.

    :param x: Target league enum. Use `Leagues.ALL` to scrape multiple 
              leagues in one run.
    :type x: League
    :param path: Filesystem path where results will be saved.
    :type path: str
    :param current: If True, scrape the current season. If False, scrape 
                    past seasons.
    :type current: bool

    :raises TypeError: If `x` is not an instance of `Leagues`.
    :raises FileNotFoundError: If the given `path` does not exist.

    :return: None. Results are saved to pickle files.
    :rtype: None
    """
    if not isinstance(x,Leagues):
        raise TypeError("Expected instance Leagues(Enum)")
    if not Path(path).exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    if x==Leagues.ALL:
        for league in list(filter(lambda x : x.value != 12, Leagues)):
            if current:
                data = await makeLeagueCurrentSeasonRegister(league)
            else:
                data = await makeLeaguePastSeasonRegister(league)
            leagueName:str=league.name.lower()
            filename = leagueName+'_match_register.pkl'
            p=Path(path).joinpath(path,filename)
            with open(p,"wb") as f:
                pickle.dump(data,f)
            f.close()
    else:
        if current:
            data = await makeLeagueCurrentSeasonRegister(league)
        else:
            data = await makeLeaguePastSeasonRegister(league)
        leagueName:str=x.name.lower()
        filename = leagueName+'_match_register.pkl'
        p=Path(path).joinpath(path,filename)
        print(p)
        with open(p,"wb") as f:
            pickle.dump(data,f)
        f.close()
        
async def makeLeaguePastSeasonRegister(x:League)->dict:
    """
    Scrape match information for past seasons of a given league from 
    its Sofascore page.

    The function:
      - Simulates browsing from a randomly chosen world city 
        (via spoofed geolocation and locale).
      - Opens the Sofascore league page.
      - Iterates through a set of past seasons (currently the 2 most 
        recent ones, excluding the current).
      - For each season:
          * Detects whether a "rounds" dropdown exists.
          * If rounds exist, iterates through all available rounds.
          * Filters out non-standard competitions 
            (qualification, relegation, playoff).
          * Collects match URLs for valid rounds using `getMatchLinks`.

    Data is structured hierarchically in a nested dictionary, grouped by:
      - league name
      - season
      - round

    ⚠️ Notes:
      - Only rounds explicitly containing the word "round" are included.
      - Seasons are currently restricted to indices 1 and 2 
        (`range(1, 3)`), meaning the function processes the two most 
        recent past seasons. Adjust the loop to cover more if needed.
      - Uses a persistent browser profile (`./my_profile`) so cookies 
        and settings are retained across runs.
      - If dropdown elements cannot be found or interacted with, 
        the function skips them and continues gracefully.

    :param x: Enum value representing the league whose matches 
              should be scraped.
    :type x: League

    :raises RuntimeError: if critical dropdowns (season or round) 
                          cannot be located or interacted with.

    :return: Nested dictionary of scraped match URLs and metadata.
             Example:
             {
               "bundesliga": {
                 "2022/2023": {
                   "Round 1": {
                     ... match data from getMatchLinks() ...
                   },
                   "Round 2": { ... },
                   ...
                 },
                 "2021/2022": { ... }
               }
             }
    :rtype: dict
    """
    #
    cLeague     = leagues[x.value]
    # filename    = x.name.lower()+"_sources.json"
    # savepath    = Path(path).joinpath(filename)
    city = random.choice(list(LOCATIONS.keys()))  # Randomly pick a city each run
    location = LOCATIONS[city]
    print(f"[+] Simulating location: {city}")
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
        locale=location["locale"],  # default
        geolocation={"latitude": location["latitude"], "longitude": location["longitude"]},
        permissions=["geolocation"],
        
        )
        page = await browser.new_page()
        # await rotate_locations(browser, page, delay=90)

        # ➤ Stealth: remove webdriver flag
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        catalog:dict={}
        # ==================================================================
        # (0) LOAD MAIN PAGE
        # ==================================================================
        await block_ads(page)
        await page.goto(cLeague.sofa_url)
        # await page.mouse.wheel(random.uniform(100, 550), random.uniform(900, 1500))
        #
        # ==================================================================
        # SELECT SEASON
        # ==================================================================
        # 1. Locate the seasons dropdown container and open its combobox
        season_dropdown = page.locator('div.Dropdown.kdhXwd')
        season_combobox = season_dropdown.locator('button[role="combobox"]')
        await season_combobox.click()
        # 2. Get all season options inside that container
        season_options = season_dropdown.locator('ul[role="listbox"] li')
        season_count = await season_options.count()
        # ==================================================================
        # FOR EACH SEASON...
        # ==================================================================
        for i in range(1,6):
            # await asyncio.sleep(100)
            season_text = await season_options.nth(i).inner_text()
            if i==1:
                catalog[cLeague.name.lower()]={}
            catalog[cLeague.name.lower()][season_text]={}
            print(f"Clicking season {i+1}: {season_text}")
            await season_options.nth(i).click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1.0)
            await page.evaluate("window.scrollTo(0, 0)")
            # ===============================================================
            # DETECTION OF ROUNDS
            # ===============================================================
            round_dropdown = page.locator('div[data-panelid="round"] div.Dropdown.gSFIyj')
            if await round_dropdown.count() > 0:
                # ===========================================================
                # ROUNDS FOUND, LETS GO...
                # ===========================================================
                await round_dropdown.wait_for(state="attached")
                # Open the round combobox
                round_combobox = round_dropdown.locator('button[role="combobox"]').first
                await round_combobox.wait_for(state="attached")
                await round_combobox.click()
                await page.wait_for_load_state("networkidle")
                # Get round options
                round_options = round_dropdown.locator('ul[role="listbox"] li')
                await round_options.first.wait_for(state='attached')
                round_count = await round_options.count()
                for j in range(round_count):
                    round_combobox = round_dropdown.locator('button[role="combobox"]').first
                    await round_combobox.wait_for(state="attached")
                    round_text = await round_options.nth(j).inner_text()
                    print(f"   Clicking round {j+1}: {round_text}")
                    
                    await round_options.nth(j).click()
                    # await page.wait_for_load_state("networkidle")
                    print("      ✅ Round clicked")
                    await round_combobox.click()
                    # ======================================================
                    # GRAB MATCHES URLS
                    # ======================================================
                    isRound = round_text.lower().find('round')!=-1
                    isQualification = round_text.lower().find('qualification')!=-1
                    isRelegation = round_text.lower().find('relegation')!=-1
                    isPlayoff = round_text.lower().find('playoff')!=-1
                    if isRound and not isQualification and not isRelegation and not isPlayoff:
                        data:dict = await getMatchLinks(page)
                        catalog[cLeague.name.lower()][season_text][round_text]=data
                    
            # ==============================================================
            # NO ROUNDS BUTTON THEN SKIP
            # ==============================================================
            else:
                print(f"   NO ROUNDS: SKIP SEASON {season_text}")
            # ==============================================================
            # SEASON COMPLETE
            # ==============================================================
            if i < season_count - 1:
                season_dropdown = page.locator('div.Dropdown.kdhXwd')
                season_combobox = season_dropdown.locator('button[role="combobox"]')
                await season_combobox.wait_for(state="visible")
                await season_combobox.click()
            await asyncio.sleep(1.0)
        await browser.close()
        return dict(catalog)

async def makeLeagueCurrentSeasonRegister(x:League)->dict:
    """
    Scrape match information for the current season of a given league 
    from its Sofascore page.

    The function:
      - Simulates browsing from a randomly chosen world city 
        (using spoofed geolocation and locale).
      - Navigates to the league's Sofascore page.
      - Iterates through available seasons (currently limited to the most 
        recent one).
      - For each season:
          * Detects whether a "rounds" dropdown exists.
          * If rounds exist, iterates through all available rounds.
          * Filters out non-standard competitions 
            (e.g. qualification, relegation, playoff).
          * Collects match URLs for valid rounds via `getMatchLinks`.

    Data is structured hierarchically in a nested dictionary, grouped by:
      - league name
      - season
      - round

    ⚠️ Notes:
      - Only rounds explicitly containing the word "round" are included.
      - The browser is launched in persistent mode with a dedicated 
        profile folder, so cookies and browsing data persist across runs.
      - If dropdown elements cannot be found or interacted with, the 
        function skips them and continues.

    :param x: Enum value representing the league whose matches 
              should be scraped.
    :type x: League

    :raises RuntimeError: if critical dropdowns (season or round) 
                          cannot be located or interacted with.

    :return: Nested dictionary of scraped match URLs and metadata.
             Example:
             {
               "premier_league": {
                 "2023/2024": {
                   "Round 1": {
                     ... match data from getMatchLinks() ...
                   },
                   "Round 2": { ... },
                   ...
                 }
               }
             }
    :rtype: dict
    """
    #
    cLeague     = leagues[x.value]
    # filename    = x.name.lower()+"_sources.json"
    # savepath    = Path(path).joinpath(filename)
    city = random.choice(list(LOCATIONS.keys()))  # Randomly pick a city each run
    location = LOCATIONS[city]
    print(f"[+] Simulating location: {city}")
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
        locale=location["locale"],  # default
        geolocation={"latitude": location["latitude"], "longitude": location["longitude"]},
        permissions=["geolocation"],
        
        )
        page = await browser.new_page()
        # await rotate_locations(browser, page, delay=90)

        # ➤ Stealth: remove webdriver flag
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        catalog:dict={}
        # ==================================================================
        # (0) LOAD MAIN PAGE
        # ==================================================================
        await block_ads(page)
        await page.goto(cLeague.sofa_url)
        # await page.mouse.wheel(random.uniform(100, 550), random.uniform(900, 1500))
        #
        # ==================================================================
        # SELECT SEASON
        # ==================================================================
        # 1. Locate the seasons dropdown container and open its combobox
        season_dropdown = page.locator('div.Dropdown.kdhXwd')
        season_combobox = season_dropdown.locator('button[role="combobox"]')
        await season_combobox.click()
        # 2. Get all season options inside that container
        season_options = season_dropdown.locator('ul[role="listbox"] li')
        season_count = await season_options.count()
        # ==================================================================
        # FOR EACH SEASON...
        # ==================================================================
        for i in range(0,1):
            # await asyncio.sleep(100)
            season_text = await season_options.nth(i).inner_text()
            catalog[cLeague.name.lower()]={}
            catalog[cLeague.name.lower()][season_text]={}
            print(f"Clicking season {i+1}: {season_text}")
            await season_options.nth(i).click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1.0)
            await page.evaluate("window.scrollTo(0, 0)")
            # ===============================================================
            # DETECTION OF ROUNDS
            # ===============================================================
            round_dropdown = page.locator('div[data-panelid="round"] div.Dropdown.gSFIyj')
            if await round_dropdown.count() > 0:
                # ===========================================================
                # ROUNDS FOUND, LETS GO...
                # ===========================================================
                await round_dropdown.wait_for(state="attached")
                # Open the round combobox
                round_combobox = round_dropdown.locator('button[role="combobox"]').first
                await round_combobox.wait_for(state="attached")
                await round_combobox.click()
                await page.wait_for_load_state("networkidle")
                # Get round options
                round_options = round_dropdown.locator('ul[role="listbox"] li')
                await round_options.first.wait_for(state='attached')
                round_count = await round_options.count()
                for j in range(round_count):
                    round_combobox = round_dropdown.locator('button[role="combobox"]').first
                    await round_combobox.wait_for(state="attached")
                    round_text = await round_options.nth(j).inner_text()
                    print(f"   Clicking round {j+1}: {round_text}")
                    
                    await round_options.nth(j).click()
                    # await page.wait_for_load_state("networkidle")
                    print("      ✅ Round clicked")
                    await round_combobox.click()
                    # ======================================================
                    # GRAB MATCHES URLS
                    # ======================================================
                    isRound = round_text.lower().find('round')!=-1
                    isQualification = round_text.lower().find('qualification')!=-1
                    isRelegation = round_text.lower().find('relegation')!=-1
                    isPlayoff = round_text.lower().find('playoff')!=-1
                    if isRound and not isQualification and not isRelegation and not isPlayoff:
                        data:dict = await getMatchLinks(page)
                        catalog[cLeague.name.lower()][season_text][round_text]=data
                    
            # ==============================================================
            # NO ROUNDS BUTTON THEN SKIP
            # ==============================================================
            else:
                print(f"   NO ROUNDS: SKIP SEASON {season_text}")
            # ==============================================================
            # SEASON COMPLETE
            # ==============================================================
            if i < season_count - 1:
                season_dropdown = page.locator('div.Dropdown.kdhXwd')
                season_combobox = season_dropdown.locator('button[role="combobox"]')
                await season_combobox.wait_for(state="visible")
                await season_combobox.click()
            await asyncio.sleep(1.0)

        await browser.close()
        return dict(catalog)

async def getMatchLinks(page:Page)->dict:
    """
    scrape match information from a Sofascore page. the function 
    extracts home and away team names, final scores, match URLs, 
    and results (win/loss/draw), and returns them as a dictionary.

    if a team name is not found, the function raises an error. 
    only matches with available scores and status information 
    are included in the output.

    :param page: playwright Page object of the Sofascore webpage 
                 being scraped
    :type page: Page

    :raises EmptyTextError: if the home or away team label cannot 
                            be found on the page

    :return: dictionary containing lists of scraped match data with:
             - 'hometeam': list of home team names
             - 'awayteam': list of away team names
             - 'url': list of Sofascore match URLs
             - 'result': list of results ('W', 'L', or 'D')
    :rtype: dict
    """
    data={}
    data['hometeam']=[]
    data['awayteam']=[]
    data['url']=[]
    data['result']=[]
    #
    matches_box = page.locator("div.Box.kiSsvW")
    await matches_box.wait_for(state="attached")
    links = matches_box.locator("a")
    link_count = await links.count()
    for i in range(link_count):
        href = await links.nth(i).get_attribute("href")
        print(sofaroot+href)
        #
        trueMatch = href.find('tournament')==-1
        if trueMatch:
            hometeam=""
            awayteam=""
            hometeamLabelLocator = links.nth(i).locator("div.Box.Flex.khxXvq.jLRkRA")
            awayteamLabelLocator = links.nth(i).locator("div.Box.Flex.ggRYVx.jLRkRA")
            # ==============================================================
            # get HOMETEAM LABEL
            # ==============================================================
            bdi_home = hometeamLabelLocator.nth(0).locator("bdi.Text.ezSveL")
            bdi_home_count = await bdi_home.count()
            if bdi_home_count:
                hometeam = await bdi_home.nth(0).inner_text()
            else:
                bdi_home = hometeamLabelLocator.nth(0).locator("bdi.Text.kwIkWN")
                hometeam = await bdi_home.nth(0).inner_text()
            # ==============================================================
            # get AWAYTEAM LABEL
            # ==============================================================                
            bdi_away = awayteamLabelLocator.nth(1).locator("bdi.Text.ezSveL")
            bdi_away_count = await bdi_away.count()
            if bdi_away_count:
                awayteam = await bdi_away.nth(0).inner_text()
            else:
                bdi_away = awayteamLabelLocator.nth(1).locator("bdi.Text.kwIkWN")
                awayteam = await bdi_away.nth(0).inner_text()
            # ===================================================
            if hometeam =="": 
                raise EmptyTextError(f"ERROR SCRAPPING MATCH:\n{href}\n HOME team is not foun")
            if awayteam =="": 
                raise EmptyTextError(f"ERROR SCRAPPING MATCH:\n{href}\n AWAY team is not found")
            # ==============================================================
            # get SCORES
            # ==============================================================                        
            score_box_locator = links.nth(i).locator("div.Box.Flex.btcITE.yaNbA")
            inner_score_box = score_box_locator.locator("div.Box.Flex.jTiCHC.MkeW.sc-37b4466f-2.fUqQjG.score-box")
            
            homescore=""
            awayscore=""
            
            forbiddens = ['\n0','\n1','\n2','\n3','\n4','\n5','\n6','\n7','\n8']
            replacement = lambda text: (lambda t: [t := t.replace(f, '') for f in forbiddens] and t)(text)

            if await inner_score_box.count():
                nb_score_box=await inner_score_box.count()
                homescore = await inner_score_box.nth(0).inner_text()
                awayscore = await inner_score_box.nth(1).inner_text()
                homescore=replacement(homescore)
                awayscore=replacement(awayscore)
            # ==============================================================
            # get MATCH STATUS
            # ============================================================== 
            ft_locator = links.nth(i).locator("span.Text.fjeMtb.currentScore bdi.Text.kkVniA")
            ft_text="None"
            if await ft_locator.count():
                ft_text = await ft_locator.inner_text()
            print(f"Match status: {ft_text}")
            if homescore!="" and awayscore!="" and ft_text!="None":
                data['hometeam'].append(hometeam)
                data['awayteam'].append(awayteam)
                data['url'].append(sofaroot+href)
                if int(homescore)>int(awayscore):
                    data['result'].append('W')
                if int(awayscore)>int(homescore):
                    data['result'].append('L')
                if int(awayscore)==int(homescore):
                    data['result'].append('D')
                # dictToUpdate[
            print(f"HOMETEAM: {hometeam} {homescore}")
            print(f"AWAYTEAM: {awayteam} {awayscore}")
    return dict(data)

async def parseMatch(matchurl:str):
    """
    """
    pass
    

class EmptyTextError(Exception):
    """Raised when a locator returns empty text unexpectedly."""
    pass