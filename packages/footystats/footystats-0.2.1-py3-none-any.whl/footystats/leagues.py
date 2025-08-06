from dataclasses import dataclass
from typing import List
from enum import Enum

#error direct at the sources: these teams have no data
teams_to_exclude:list=[
    "troyes-af"
] 

class Leagues(Enum):
    PREMIERLEAGUE = 0
    LALIGA = 1
    LIGUE1 = 2
    BUNDESLIGA = 3
    SERIEA = 4
    CHAMPIONSHIP = 5
    LALIGA2 = 6
    LIGUE2 = 7
    BUNDESLIGA2 = 8
    SERIEB = 9
    PRIMEIRALIGA = 10
    EREDIVISIE = 11
    ALL = 12

@dataclass
class League:
    name: str
    start_date:int
    base_url:str
    sofa_url:str
    ws_url:str

leagues: List[League] = [
    League(
    name        = "PremierLeague", 
    # start_date  =2025,
    start_date  = 1950,
    base_url    = "https://www.worldfootball.net/competition/eng-premier-league/",
    sofa_url    = "https://www.sofascore.com/tournament/football/england/premier-league/17",
    ws_url      = "https://www.whoscored.com/regions/252/tournaments/2/england-premier-league"
    ),   # 0
    League(
    name        = "LaLiga", 
    # start_date  =2025,
    start_date  = 1950,
    base_url    = "https://www.worldfootball.net/competition/esp-primera-division/",
    sofa_url    = "https://www.sofascore.com/tournament/football/spain/laliga/8",
    ws_url      = "https://www.whoscored.com/regions/206/tournaments/4/spain-laliga"
    ),   # 1
    League(
    name        = "Ligue1",
    start_date  =1950,    
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/fra-ligue-1/",
    sofa_url    = "https://www.sofascore.com/tournament/football/france/ligue-1/34",
    ws_url      = "https://www.whoscored.com/regions/74/tournaments/22/france-ligue-1"
    ),   # 2
    League(
    name        = "Bundesliga", 
    # start_date  =2025,
    start_date  = 1969,
    base_url    = "https://www.worldfootball.net/competition/bundesliga/",
    sofa_url    = "https://www.sofascore.com/tournament/football/germany/bundesliga/35",
    ws_url      = "https://www.whoscored.com/regions/81/tournaments/3/germany-bundesliga"
    ),   # 3
    League(
    name        = "SerieA",
    start_date  = 1950,
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/ita-serie-a/",
    sofa_url    = "https://www.sofascore.com/tournament/football/italy/serie-a/23",
    ws_url      = "https://www.whoscored.com/regions/108/tournaments/5/italy-serie-a"
    ),   # 4
    League(
    name        = "Championship", 
    start_date  = 1950,
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/eng-championship/",
    sofa_url    = "https://www.sofascore.com/tournament/football/england/championship/18",
    ws_url      = "https://www.whoscored.com/regions/252/tournaments/7/england-championship"
    ),    # 5
    League(
    name        = "SegundaLiga", 
    start_date  = 1969,
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/esp-segunda-division/",
    sofa_url    = "https://www.sofascore.com/tournament/football/spain/laliga-2/54",
    ws_url      = "https://www.whoscored.com/regions/206/tournaments/63/spain-segunda-divisi%C3%B3n"
    ),     # 6
    League(
    name        = "Ligue2", 
    start_date  = 1993,
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/fra-ligue-2/",
    sofa_url    = "https://www.sofascore.com/tournament/football/france/ligue-2/182",
    ws_url      = "https://www.whoscored.com/regions/74/tournaments/37/france-ligue-2"
    ),          # 7
    League(
    name        = "Bundesliga2", 
    start_date  = 1993,
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/2-bundesliga/",
    sofa_url    = "https://www.sofascore.com/tournament/football/germany/2-bundesliga/44",
    ws_url      = "https://www.whoscored.com/regions/81/tournaments/6/germany-2-bundesliga"
    ),     # 8
    League(
    name        = "SerieB",
    start_date  = 1994,
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/ita-serie-b/",
    sofa_url    = "https://www.sofascore.com/tournament/football/italy/serie-b/53",
    ws_url      = ""
    ),          # 9
    League(
    name        = "PrimeraLiga", 
    start_date  = 1969,
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/por-primeira-liga/",
    sofa_url    = "https://www.sofascore.com/tournament/football/portugal/liga-portugal-betclic/238",
    ws_url      = "https://www.whoscored.com/regions/177/tournaments/21/portugal-liga-portugal"
    ),     # 10
    League(
    name        = "Eredivisie",
    start_date  = 1960,
    # start_date  =2025,
    base_url    = "https://www.worldfootball.net/competition/ned-eredivisie/",
    sofa_url    = "https://www.sofascore.com/tournament/football/netherlands/eredivisie/37",
    ws_url      = "https://www.whoscored.com/regions/155/tournaments/13/netherlands-eredivisie"
    )       # 11
    ]