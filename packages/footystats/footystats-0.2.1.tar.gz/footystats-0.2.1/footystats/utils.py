#utils.py
import re
from datetime import datetime

def removeDigits(text:str)->str:
    return re.sub(r'[0-9/]', '', text)

def argsort_dates(array:list, datefmt:str)->list:
    """
        returns the list of sorted index in the growing order
        computed from a list of dates
        
        :param array: the list containing the dates
        :type array: list
        :param datefmt: the date format ("%d/%m/%Y") for example
        :type datefmt: str
        :return: the list of the sorted index
        :raises ValueError if the date format or the list is invalid
    """
    try:
        test = datetime.strptime(array[0],datefmt)
    except ValueError:
        print(f"the given datefmt setting is invalid: {datefmt}")
    a       = [(i,datetime.strptime(d,datefmt)) for i,d in enumerate(array)]
    dates   = sorted(a, key = lambda x : x[1])
    indexes = [i[0] for i in dates]
    return indexes
    

# def makeSeasonPair(starting:str='2020',ending:str='2021')->list:
    # """
    # Parameters
    # ----------
    # starting : str, optional
        # Year in the format 20XX
        # Format: 20XX
    # ending : str, optional
        # Year of second football season start

    # Returns binded years defining a season i.e. 20XX-20XX+1
    # -------
    # a list containing the season years in the format 20XX-20XX+1
    # EXAMPLE: for season 2020-2021, startYear=2020, endYear=2021
    # if you enter startYear=2019, endYear=2022 then it returns such a list:
    # [2019-2020,2020-2021,2021-2022]
    # if you want the CURRENT season, type "0" for each year: startYear=0, endYear=0
    # """
    # s:int=int(starting); e:int=int(ending)
    # seasonList:list=[]
    # if s==0 or e==0:
        # seasonList.append('')
    # else:
        # [seasonList.append(f'{year}-{year+1}')for year in range(s,e,1)]
    # return list(seasonList)

def sortURLbyDate(form:dict)->None:
    """
    This function is intended for post treatment in function
    getURLfromForm (webscrapping.py) to sort urls from the
    oldest to the most recent (growing order relative to years)
    
    :param form: dict build in the function getURLfromForm
    :type form: dict
    :return: None, it only updates data built in getURLfromForm
    :rtype: None
    """
    if not isinstance(form,dict):
        raise TypeError("the given arg in not a dict")

    years = [int(label.split('/')[0]) for label in form["label"]]

    s = lambda x : sorted(range(len(x)), key=x.__getitem__)

    for k in form.keys():
        n = [form[k][i] for i in s(years)]
        form[k] = n

def reduceDataFromStartDate(seasons_urls:dict,startDate:int)->None:
    """
    Modify a pre-existing dict (urls of seasons) to keep
    only seasons where the first year is higher or equal
    to the start_date defined in leagues.py (League obj attr)
    
    :param seasons_url: dict generated using getURLfromForm
    :type seasons_url: dict
    :return: None
    :rtype: None
    """
    indexKeep:list=[]
    for i,season in enumerate(seasons_urls["label"]):
        year:int = int(season.split('/')[0])
        if year>=int(startDate):
            indexKeep.append(i)
    for k in seasons_urls.keys():
        seasons_urls[k] = [seasons_urls[k][x] for x in indexKeep]

def verifyRoundWithRightSeason(seasonlabel:str,url:str)->bool:
    """
    func. to be used in webscrapping.py
    when getFixtures(). Sometimes, some rounds
    of the preceeding season are reported in the current
    season. Hence, for some teams, it may happen that
    the Fixture page contains not only the number of matches 
    of the considered season, but also some additional
    matches from the previous season.
    This function returns True if the url of the week
    matches the current season label, else False
    
    :param seasonlabel: considered season (20XX/20XX+1)
    :type seasonlabel: str
    :param url: the week url scrapped from fixtures table
    :type url: str
    """
    y1:str      = seasonlabel.split('/')[0]
    y2:str      = seasonlabel.split('/')[1]
    hasY1:bool  = url.find(y1)!=-1
    hasY2:bool  = url.find(y2)!=-1
    if hasY1 and hasY2:
        return True
    return False

def incrementDate(date:str, offset:int)->str:
    """
    returns an incremented date by +offset
    
    :param date: the date in format (d/m/Y)
    :type date: str
    :param offset: the number of day to add
    :type offset: int
    :return: incremented day by offset value
    :rtype: str
    :raise ValueError: if the date given does not work
    """
    try:
        datetime.strptime(date, "%d/%m/%Y")
    except ValueError:
        raise ValueError(f"Invalid date format: '{date}'. Expected format is DD/MM/YYYY.")
    cdate = datetime.strptime(date, "%d/%m/%Y")
    next_day = date_obj + timedelta(days=offset)
    next_day_str = next_day.strftime("%d/%m/%Y")
    return str(next_day_str)

def mergeDict(d1: dict, d2: dict) -> None:
    """
    Merge d2 into d1 by extending the lists of matching keys.

    :param d1: Dict receiving the new data (values must be lists)
    :type d1: dict
    :param d2: Dict providing data (values must be lists)
    :type d2: dict
    :raises KeyError: If d1 and d2 do not have exactly the same keys
    :raises TypeError: If values are not lists
    """
    if set(d1.keys()) != set(d2.keys()):
        raise KeyError("Keys are not identical between dicts")

    for key in d1:
        if not isinstance(d1[key], list) or not isinstance(d2[key], list):
            raise TypeError(f"Values for key '{key}' must be lists")
        d1[key].extend(d2[key])