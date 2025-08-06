from footystats.leagues import *
from footystats.webscrapping import *
from footystats.utils import sortURLbyDate, reduceDataFromStartDate
from footystats.utils import argsort_dates
#
from playwright.async_api import async_playwright
import asyncio
#
from pathlib import Path
import json
import time
from datetime import datetime, timezone, timedelta

utc_plus_2 = timezone(timedelta(hours=2))

def sortDictFromDates(data:dict)->None:
    """
        sort all entries in a dictionary of lists according to 
    the chronological order of the dates provided under the 
    "date" key. the sorting is done in-place and affects 
    all keys in the dictionary.

    the expected date format is "%d/%m/%Y" (e.g., "24/07/2025"). 
    the function assumes that each list under a given key is 
    of the same length and aligned by index.

    :param data: dictionary where each value is a list and one 
    of the keys is "date" containing date strings in the format 
    day/month/year
    :type data: dict
    """
    indexes = argsort_dates(data['date'],"%d/%m/%Y")
    for k in data.keys():
        n = [data[k][i] for i in indexes]
        data[k] = n

async def clickTeamsButton(page:object)->None:
    """
        locate and click the "Teams" button on the page using a 
    human-like mouse movement. the function first moves the 
    mouse to the element containing the text "Teams" and 
    then simulates a click on it.

    the movement is done in a natural manner using randomized 
    steps to mimic real user behavior. the button is located 
    by iterating over all list items ("li") and matching the 
    exact text content.

    :param page: the Playwright page instance where the 
    "Teams" button should be located and clicked
    :type page: object
    """
    # await page.goto(url)
    command:str="li:has-text('Teams')"
    await move_mouse_human_like(page, command)
    # print("===================================")
    # print(command)
    # print("===================================")
    buttons = await page.locator("li").all()
    for btn in buttons:
        text = await btn.text_content()
        if text.strip() == "Teams":
            await btn.click()
            break

async def clickFixturesButton(page:object)->None:
    """
        locate and click the "Fixtures & Results" button on the 
    page using a human-like mouse movement. the function first 
    moves the mouse toward the list item containing the target 
    text, then iterates through all "li" elements to find the 
    exact match and perform the click.

    the simulated mouse motion adds randomness to mimic human 
    behavior and reduce detection by automation filters.

    :param page: the Playwright page instance where the 
    "Fixtures & Results" button should be located and clicked
    :type page: object
    """
    # await page.goto(url)
    command:str="li:has-text('Fixtures & Results')"
    await move_mouse_human_like(page, command)
    # print("===================================")
    # print(command)
    # print("===================================")
    buttons = await page.locator("li").all()
    for btn in buttons:
        text = await btn.text_content()
        if text.strip() == "Fixtures & Results":
            await btn.click()
            break

async def buildSourceFile(x:League, path:str, update=False):
    """
        build sources for the given League by automated web scraping.
    the scraping simulates human-like interactions using Playwright 
    in a persistent browser context. this operation can take 
    several minutes per league, depending on the number of seasons 
    and teams.

    the scraping navigates to the Teams page, iterates over all 
    teams in each season, loads their fixture data, and extracts 
    structured information. the mouse motion, ad blocking, and 
    stealth techniques are used to mimic a human user and reduce 
    detection.

    at the end, a nested dictionary of the structure:
    data[season][teamName] = fixtures
    is saved as a JSON file at the path: 
    "path"/"{league_name}_sources.json"

    :param x: the League enum specifying which league to scrape 
    data for
    :type x: League
    :param path: the root directory where the generated JSON 
    file should be saved
    :type path: str
    :param update: when set to True, only the most recent season 
    is scraped and previous data for that season is overwritten
    :type update: bool

    """
    #
    cLeague     = leagues[x.value]
    filename    = x.name.lower()+"_sources.json"
    savepath    = Path(path).joinpath(filename)
    #
    data={}
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
        await block_ads(page)
        await page.goto(cLeague.base_url)
        await accept_cookies(page)
        await page.wait_for_selector("table")
        await page.mouse.wheel(random.uniform(100, 550), random.uniform(900, 1500))
        await asyncio.sleep(1)
        # ==================================================================
        # (1) GO TO TEAMS BUTTON
        # ==================================================================
        await clickTeamsButton(page)
        await page.mouse.wheel(100, 400)
        # ==================================================================
        # (2) GET SEASONS URLS
        # ==================================================================
        await asyncio.sleep(1)
        seasons_urls = await getURLfromForm(page)
        reduceDataFromStartDate(seasons_urls=seasons_urls, startDate=cLeague.start_date)
        if update:
            seasons_urls['label']=[seasons_urls['label'][-1]]
            seasons_urls['urls']=[seasons_urls['urls'][-1]]
        # ==================================================================
        # (3) LOOP SEASONS
        # ==================================================================
        for id_season,season in enumerate(seasons_urls['label']):
            data[season]={}
            await page.select_option('select[name="saison"]', season)
            # await page.wait_for_load_state("networkidle")
            # await page.wait_for_load_state("load")
            await page.wait_for_selector("table")
            # await page.mouse.wheel(50, 450)
            teamsOfSeason:dict = await getTeamsFromSeason(page)
            for idx,turl in enumerate(teamsOfSeason['urls']):
                teamName:str=teamsOfSeason['label'][idx]
                print(teamName)
                data[season][teamName]={}
                await page.goto(turl)
                await page.wait_for_selector("table")
                # await asyncio.sleep(2)
                # await asyncio.sleep(0.1)
                await clickFixturesButton(page)
                # await asyncio.sleep(5)
                # await asyncio.sleep(0.1)
                await page.select_option('select[name="jahr"]', season)
                await page.wait_for_selector("table")
                # await asyncio.sleep(2)
                # await asyncio.sleep(0.1)
                await page.mouse.wheel(random.uniform(50, 417), random.uniform(900, 1900))
                fixtures = await getFixtures(page,season)
                sortDictFromDates(fixtures)
                await page.wait_for_selector("table")
                # await asyncio.sleep(5)
                # await asyncio.sleep(0.1)
                # await page.go_back()
                #
                data[season][teamName]=fixtures
                #
            await page.goto(seasons_urls['urls'][id_season])
            await page.wait_for_selector("table")
            await page.mouse.wheel(random.uniform(20, 601), random.uniform(700, 1700))
        #
        await browser.close()
        with open(savepath,"w") as f:
            json.dump(data,f)
        f.close()
        print(''.join(('=') for i in range(59)))
        mess:str='{:^59}'.format(f"CREATED SOURCES FOR {x.name.upper()}")
        print(mess)
        print(''.join(('=') for i in range(59)))

async def makeSources(x:Leagues, path:str="")->None:
    """
        build source files for one or all leagues depending on the 
    given league value. if the input is Leagues.ALL, source files 
    are generated for all leagues except the one with value 12 
    (excluded manually).

    this function acts as a wrapper around `buildSourceFile` 
    and delegates the scraping and saving process per league.

    :param x: a specific league to process, or Leagues.ALL to 
    process all leagues
    :type x: Leagues (Enum)
    :param path: root directory where generated JSON files are 
    saved; defaults to the current directory
    :type path: str
    """
    if not isinstance(x,Leagues):
        raise TypeError("Expected instance Leagues(Enum)")

    if x==Leagues.ALL:
        for league in list(filter(lambda x : x.value != 12, Leagues)):
            await buildSourceFile(league,path)
    else:
        await buildSourceFile(x,path)

async def updateSources(x:Leagues, pathroot:str="")->None:
    """
        update existing source files for one or all leagues by 
    scraping only the most recent season data. this function 
    behaves like `makeSources` but activates the update mode 
    in `buildSourceFile`, which restricts the scraping to the 
    latest season only.

    if Leagues.ALL is passed, all leagues except the one with 
    value 12 are updated.

    :param x: the league to update, or Leagues.ALL to update 
    all leagues
    :type x: Leagues (Enum)
    :param pathroot: root directory where the updated JSON files 
    will be saved; defaults to the current directory
    :type pathroot: str

    """
    if not isinstance(x,Leagues):
        raise TypeError("Expected instance Leagues(Enum)")

    if x==Leagues.ALL:
        for lo in list(filter(lambda x : x.value != 12, Leagues)):
            await buildSourceFile(lo,pathroot,update=True)
    else:
        await buildSourceFile(x,pathroot,update=True)

async def getURLfromForm(page:Page)->dict:
    """
        extract URLs and their labels from select option elements 
    found inside form tags on the given page. the function 
    parses the current HTML content with BeautifulSoup, collects 
    option values that contain slashes ("/"), validates them as 
    URLs relative to a root URL, and returns a dictionary with 
    sorted lists of URLs and labels.

    the data returned has the form:
    {
        "urls": [...],
        "label": [...]
    }
    where both lists are sorted by date extracted from the labels.

    :param page: the Playwright page instance from which the 
    form content is parsed
    :type page: playwright.async_api.Page
    :raises ValueError: if any of the returned lists is empty
    :return: a dictionary containing sorted 'urls' and 'label' lists
    :rtype: dict

    """ 
    html_page = await page.content()
    await asyncio.sleep(1)
    # html_page=my_requests.content.decode('utf-8')
    soup = BeautifulSoup(html_page, "html.parser")
    data = {"urls":[],"label" : []}
    for form in soup.find_all('form'):
        if form:
            for select in form.find_all('select'):
                if select:
                    options = select.find_all('option')
                    for option in options:
                        value   = option.get('value')
                        text    = option.get_text()
                        if(value.find("/")!=-1):
                            iurl = rooturl+value
                            if valid_url(iurl):
                                data['urls'].append(rooturl+value)
                                data['label'].append(text)
    sizes = [len(data[k]) for k in data.keys()]
    if 0 in sizes:
        raise ValueError("Expected a non-empty list")
    sortURLbyDate(data)
    return dict(data)

async def getTeamsFromSeason(page:Page)->dict:
    """
        extract team URLs, names, and associated images from the 
    season page by parsing the HTML content. the function looks 
    for a table with class 'standard_tabelle', then collects 
    data from each row excluding teams listed in 
    `teams_to_exclude`.

    the returned dictionary contains lists of:
    - 'urls': full URLs to team pages
    - 'label': team names extracted from URLs
    - 'img': image sources related to each team

    :param page: the Playwright page instance containing the 
    season's team data
    :type page: playwright.async_api.Page
    :raises ValueError: if any of the returned lists is empty
    :return: dictionary with keys 'urls', 'label', and 'img' 
    containing lists of team information
    :rtype: dict

    """
    html_page = await page.content()
    # html_page=my_requests.content.decode('utf-8')
    soup = BeautifulSoup(html_page, "html.parser")
    data = {"urls":[],"label" : [],'img':[]}
    
    table = soup.find('table', class_='standard_tabelle')
    if table:
        for tr in table.find_all('tr'):
            if tr:
                tds         = tr.find_all('td')
                target      = tds[1].get_text()
                target_link = rooturl+tds[1].find('a')['href']
                target_name = target_link.split("/")[-2]
                if target_name not in teams_to_exclude:
                    data['urls'].append(target_link)
                    data['label'].append(target_name)
                #
                img = tds[0].find('a').find('img')['src']
                data['img'].append(img)
                
    sizes = [len(data[k]) for k in data.keys()]
    if 0 in sizes:
        raise ValueError("Expected a non-empty list")
    return dict(data)

def loadSources(x:Leagues, pathroot:str="")->dict:
    """
        load source data for a given league from a JSON file stored 
    in the specified directory. the function verifies the path 
    existence and input type before reading and returning the data.

    :param x: the league enum identifying which league's sources 
    to load
    :type x: Leagues (Enum)
    :param pathroot: root directory where the JSON source file 
    is located
    :type pathroot: str
    :raises FileNotFoundError: if the given path does not exist
    :raises TypeError: if the input x is not an instance of Leagues
    :return: the loaded source data as a dictionary
    :rtype: dict

    """
    if not Path(pathroot).exists():
        raise FileNotFoundError(f"Path does not exist: {pathroot}")
    if not isinstance(x,Leagues):
        raise TypeError(f"Expected an Enum Leagues instead of {type(x)}")
    cLeague     = leagues[x.value]
    filename    = x.name.lower()+"_sources.json"
    dest        = Path(pathroot).joinpath(filename)
    with open(dest,"r") as f:
        data=json.load(f)
    f.close()
    print(''.join(('=') for i in range(59)))
    print('{:^55}'.format("LOADED "+x.name.upper()+" SOURCES"))
    print(''.join(('=') for i in range(59)))
    return dict(data)

async def getFixtures(page:Page,seasonlabel:str)->dict:
    """
        extract fixtures data from the given page for a specified season. 
    the function parses a table with class 'standard_tabelle', 
    determines the number of columns, and collects fixture details 
    such as round, date, hour, venue, opponent, score, and week number.

    if a date cell is empty, it increments the previous date by one day. 
    only rows matching the correct season and containing 'spieltag' in 
    the URL are considered for week extraction.

    :param page: the Playwright page instance containing fixture data
    :type page: playwright.async_api.Page
    :param seasonlabel: the season label used to verify fixture relevance
    :type seasonlabel: str
    :raises ValueError: if any returned list is empty or if lists differ in size
    :return: a dictionary with keys 'round', 'date', 'hour', 'venue', 
    'opponent', 'score', and 'week' each mapping to lists of fixture info
    :rtype: dict
    """
    html_page = await page.content()
    #
    data = {"round":[],
            "date":[],
            "hour":[],
            "venue":[],
            "opponent":[],
            "score":[],
            "week":[]}
    #
    soup = BeautifulSoup(html_page, "html.parser")
    table = soup.find('table', class_='standard_tabelle')
    # =========================================================================
    # 1. Know how many data columns in table
    # =========================================================================
    nb_column:int = 0
    if table:
        for tr in table.find_all('tr'):
            if tr:
                for th in tr.find_all('th'):
                    if th:
                        if th.get('colspan')!=None:
                            nb_column += int(th.get('colspan'))
                        else:
                            nb_column+= 1
                if nb_column!=0:
                    break
    # =========================================================================
    # 2. parse / store data from table
    # =========================================================================
        for tr in table.find_all('tr'):
            if tr:
                if tr.find('td'):
                    tds = tr.find_all('td')
                    if len(tds)>1:
                        #
                        nweek           = -1
                        weekUrl:str     = tds[0].find('a')['href']
                        findSpieltag    = weekUrl.find('spieltag')!=-1
                        findRightSeason = verifyRoundWithRightSeason(seasonlabel,weekUrl)
                        if findSpieltag and findRightSeason:
                            items = tds[0].find('a')['href'].split('/')
                            items = list(filter(lambda x : x != "", items))
                            nweek = int(items[-1])
                        #
                        round_      = tds[0].get_text().lower()
                        date        = tds[1].get_text().lower()
                        if date =="":
                            previousdate    = data["date"][-1]
                            date = incrementDate(previousdate,1)

                        hour        = tds[2].get_text().lower()
                        venue       = tds[3].get_text().lower()
                        try:
                            opponent    = tds[5].find('a')['href'].split('/')[2]
                        except TypeError:
                            opponent    ="undefined"
                        score       = tds[6].get_text().lower()
                        #
                        data["week"].append(nweek)
                        data["round"].append(round_)
                        data["date"].append(date)
                        data["hour"].append(hour)
                        data["venue"].append(venue)
                        data["opponent"].append(opponent)
                        data["score"].append(score.strip())
    #
    sizes = [len(data[k]) for k in data.keys()]
    if 0 in sizes:
        raise ValueError("Expected a non-empty list")
    if len(set(sizes))>1:
        raise ValueError("Some lists do not have the same size")
    return dict(data)