#nextmatches.py
from playwright.async_api import async_playwright
import asyncio
from footystats.leagues import Leagues, leagues
from footystats.database import loadDatabase
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from footystats.webscrapping import block_ads
from footystats.utils import mergeDict
from footystats.match import Match
from footystats.team import Team
import random

async def getMatches(x:Leagues,date:str="")->dict:
    """
    retrieve match data for a given league and optionally filter by date.
    the function launches a persistent Chromium browser context with stealth 
    settings, blocks ads, navigates to the league's base URL, waits for match 
    tables to load, then extracts match info via getLeaguePageTable. 

    if the league parameter is Leagues.ALL, it collects matches from all leagues
    except the one with value 12, merging their results.

    when a date is provided, the function validates its format (DD/MM/YYYY) and
    filters the matches accordingly. if no matches are found for the date, 
    a ValueError is raised.

    :param x: league enum to get matches for, or Leagues.ALL for all leagues
    :type x: Leagues (Enum)
    :param date: optional date string (format DD/MM/YYYY) to filter matches
    :type date: str
    :raises TypeError: if x is not an instance of Leagues enum
    :raises ValueError: if date format is invalid or no matches found for date
    :return: dictionary of match data with keys like 'date', 'league', etc.
    :rtype: dict

    """
    if not isinstance(x,Leagues):
        raise TypeError(f"Expected an Enum Leagues instead of {type(x)}")
    #
    matchList:dict={}
    if(x.name!="ALL"):
        url = leagues[x.value].base_url
        #async with async_playwright() as p:
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
            await page.goto(url)
            await page.wait_for_selector("table")
            await page.mouse.wheel(random.uniform(100, 550), random.uniform(900, 1500))
            await asyncio.sleep(1)
            matchList:dict = await getLeaguePageTable(page)
            await browser.close()
            #
            size:int = len(matchList[next(iter(matchList.keys()))])
            matchList.update(("league",[x.value for i in range(size)]) for j in range(1))
            if date != "":
                try:
                    datetime.strptime(date, "%d/%m/%Y")
                except ValueError:
                    raise ValueError(f"Invalid date format: '{date}'. Expected format is DD/MM/YYYY.")
                filterByDate(matchList,date)
                #
                if len(matchList['date'])==0:
                    raise ValueError(f"no matches found the given date\
                    {date} for the given league {x.name.upper()}")
    else:
        for lo in list(filter(lambda x : x.value !=12,Leagues)):
            url = leagues[lo.value].base_url
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
                await page.goto(url)
                await page.wait_for_selector("table")
                await page.mouse.wheel(random.uniform(100, 550), random.uniform(900, 1500))
                await asyncio.sleep(1)
                subdict:dict = await getLeaguePageTable(page)
                await browser.close()
                size:int = len(subdict[next(iter(subdict.keys()))])
                subdict.update(("league",[lo.value for i in range(size)]) for j in range(1))
                if matchList=={}:
                    matchList.update((k,[]) for k in subdict.keys())
                mergeDict(matchList,subdict)

                if date != "":
                    try:
                        datetime.strptime(date, "%d/%m/%Y")
                    except ValueError:
                        raise ValueError(f"Invalid date format: '{date}'. Expected format is DD/MM/YYYY.")
                    filterByDate(matchList,date)
                    #
    if len(matchList['date'])==0:
        raise ValueError(f"no matches found the given date {date} for the given league {x.name.upper()}")

def filterByDate(matchlist:dict,date:str)->dict:
    """
    filter the match list dictionary in-place to keep only 
    entries that match the specified date. the filtering is 
    based on exact string comparison with the 'date' field. 
    all columns in the dictionary are updated accordingly 
    to retain aligned data.

    :param matchlist: dictionary containing match data where 
    each key maps to a list of values (including 'date')
    :type matchlist: dict
    :param date: the date string to filter by (must match 
    the format used in matchlist['date'])
    :type date: str
    ```
    """
    li:list=[]
    for i,d in enumerate(matchlist['date']):
        if d==date:
            li.append(i)
    for k in matchlist.keys():
        newColumn = [matchlist[k][i] for i in li]
        matchlist[k]=newColumn

def exportMatches(path:str, listMatches:dict)->None:
    """
    export a dictionary of match data to a plain text file 
    called 'listOfMatches.txt' inside the specified path. 
    the function validates the input structure, ensuring it 
    is a dictionary and includes required keys: 'date', 
    'week', 'hometeam', and 'awayteam'.

    the file is formatted with aligned columns for each key, 
    where each row corresponds to a match entry.

    :param path: the directory path where the text file will be saved
    :type path: str
    :param listMatches: a dictionary containing lists of match details, 
    where each key maps to a column
    :type listMatches: dict
    :raises FileNotFoundError: if the given path does not exist
    :raises TypeError: if listMatches is not a dictionary
    :raises KeyError: if required keys are missing from the input
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"this path {path} is empty or does not exist")
    requiredKeys:list=["date","week","hometeam","awayteam"]
    valid:bool = all(items in listMatches.keys() for items in requiredKeys)
    if not isinstance(listMatches,dict):
        raise TypeError("the given objec (listMatches) is not a dict")
    if not valid:
        raise KeyError(f"given list is not the good object: "\
        +" ".join((k) for k in list(listMatches.keys())))
    #
    fname:str = "listOfMatches.txt"
    sp:str=Path(path).joinpath(fname)
    with open(sp,"w") as f:
        header:str=""
        for k in listMatches.keys():
            header+='{:<24}'.format(k)
        f.write(header+'\n')
        for i in range(len(listMatches[next(iter(listMatches.keys()))])):
            line:str=""
            for k in listMatches.keys():
                line+='{:<24}'.format(str(listMatches[k][i]))
            f.write(line+'\n')
    f.close()

async def getLeaguePageTable(page:object)->dict:
    """
    extract matchday table data from a league page. the function 
    parses a table with class 'standard_tabelle' and collects 
    details for each match, including week number, date, hour, 
    home team, and away team.

    the week number is extracted from a link in the table header, 
    while match rows contain team names and time information. 
    team names are parsed from their corresponding URLs.

    the function validates that all lists are non-empty and of 
    equal length before returning the result.

    :param page: the Playwright page instance currently displaying 
    a league match overview
    :type page: playwright.async_api.Page or similar object
    :raises ValueError: if any list is empty or if list lengths are inconsistent
    :return: dictionary containing parsed match data
    :rtype: dict
    """
    #
    data = {"week":[],
            "date":[],
            "hour":[],
            "hometeam":[],
            "awayteam":[]}
    #
    html_page=await page.content()
    soup = BeautifulSoup(html_page, "html.parser")
    table = soup.find('table', class_='standard_tabelle')
    #
    current_date:str=""
    current_hour:str=""
    current_week:int=0
    for tr in table.find_all('tr'):
            if tr:
                th = tr.find('th')
                if th:
                    localurl:str = th.find('a')['href']
                    current_week = int(list(filter(lambda x : x!="",localurl.split('/')))[-1])
                td=tr.find('td')
                if td:
                    tds = tr.find_all('td')
                    if tds[0].get_text()!= "":
                        current_date = tds[0].get_text()
                    if tds[1].get_text()!= "":
                        current_hour = tds[1].get_text()
                    hometeamurl:str=tds[2].find('a')['href'].split('/')
                    awayteamurl:str=tds[6].find('a')['href'].split('/')
                    hometeam:str = list(filter(lambda x : x!= "", hometeamurl))[-1]
                    awayteam:str = list(filter(lambda x : x!= "", awayteamurl))[-1]
                    #
                    data["week"].append(current_week)
                    data["date"].append(current_date)
                    data["hour"].append(current_hour)
                    data["hometeam"].append(hometeam)
                    data["awayteam"].append(awayteam)
    #
    sizes = [len(data[k]) for k in data.keys()]
    if 0 in sizes:
        raise ValueError("Expected a non-empty list")
    if len(set(sizes))>1:
        raise ValueError("Some lists do not have the same size")
    return dict(data) 