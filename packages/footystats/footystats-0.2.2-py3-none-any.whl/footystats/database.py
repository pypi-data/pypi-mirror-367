#database.py
import re
from datetime import datetime
from pathlib import Path
from footystats.leagues import *
from footystats.sources import loadSources
from footystats.debug import debugDatabase
import json

def makeDatabase(x:Leagues=None,sourcesRep:str="",saveRep:str="", debug:bool=False, debugYear:str="2000")->dict:
    """
        create and save a season-long database for a specific league or for all leagues.
    the function loads match sources, initializes and populates the database with
    computed fields such as goals, points, ladder rankings, forms, and opponent stats.

    the result is saved to a JSON file per league in the provided save directory.
    supports debugging mode for printing detailed outputs related to a specific year.

    :param x: league enum to process; can be a specific league or Leagues.ALL
    :type x: Leagues
    :param sourcesRep: path to the folder containing *_sources.json files
    :type sourcesRep: str
    :param saveRep: path where the output database JSON files will be saved
    :type saveRep: str
    :param debug: optional; whether to enable debug mode for one season (default is False)
    :type debug: bool
    :param debugYear: optional; year string used when debug mode is active
    :type debugYear: str
    :raises FileNotFoundError: if any of the input paths do not exist
    :raises TypeError: if x is not an instance of the Leagues Enum
    :return: the last computed database dictionary (or None if Leagues.ALL)
    :rtype: dict
    """
    if not Path(sourcesRep).exists():
        raise FileNotFoundError(f"Path to sources does not exist: {sourcesRep}")
    if not Path(saveRep).exists():
        raise FileNotFoundError(f"Path to save databases does not exist: {saveRep}")
    if not isinstance(x,Leagues):
        raise TypeError(f"Expected an Enum Leagues instead of {type(x)}")
    if x.name != "ALL":
        sources:dict = loadSources(x,sourcesRep)
        database:dict= {}
        #
        initializeDatabase(sources,database)
        addWeekVenueOpponent(sources,database)
        #
        computeGoalsAndResults(sources,database)
        computeCumulatedGoals(database)
        computePoints(database)
        computeGeneralLadder(database)
        computeHomeLadder(database)
        computeAwayLadder(database)
        computeForms(database,8)
        computeOpponentInfos(database)
        if debug:
            debugDatabase(x,database,debugYear)
        # SAVE DATABASE
        fname:str = "database_"+x.name.lower()+".json"
        sp = Path(saveRep).joinpath(fname)
        with open(sp,"w") as f:
            json.dump(database,f)
        f.close()
        print(''.join(('=') for i in range(59)))
        print('{:^59}'.format(f"ACHIEVED DATABASE FOR {x.name.upper()}"))
        print(''.join(('=') for i in range(59)))
    else:
        for l in Leagues:
            if l.name!="ALL":
                sources:dict = loadSources(l,sourcesRep)
                database:dict= {}
                #
                initializeDatabase(sources,database)
                addWeekVenueOpponent(sources,database)
                #
                # prepareDatabaseFile()
                computeGoalsAndResults(sources,database)
                computeCumulatedGoals(database)
                computePoints(database)
                computeGeneralLadder(database)
                computeHomeLadder(database)
                computeAwayLadder(database)
                computeForms(database,8)
                computeOpponentInfos(database)
                if debug:
                    debugDatabase(l,database,debugYear)
                # SAVE DATABASE
                fname:str = "database_"+l.name.lower()+".json"
                sp = Path(saveRep).joinpath(fname)
                with open(sp,"w") as f:
                    json.dump(database,f)
                f.close()
                print(''.join(('=') for i in range(59)))
                print('{:^59}'.format(f"ACHIEVED DATABASE FOR {l.name.upper()}"))
                print(''.join(('=') for i in range(59)))

def initializeDatabase(sources:dict,database:dict)->None:
    """
        initialize the structure of the database using the sources dictionary.
    creates a nested dictionary where each season maps to its teams, each
    initialized as an empty dictionary.

    this structure prepares the database for further population with match
    and statistical data.

    :param sources: dictionary containing match sources grouped by season and team
    :type sources: dict
    :param database: empty dictionary that will be populated with the structure
    :type database: dict
    :return: None
    :rtype: None

    """
    for s in sources.keys():
        database.update((s,{}) for i in range(1))
        for t in sources[s].keys():
            database[s][t]={}

def addWeekVenueOpponent(sources:dict,databaseToUpdate:dict)->None:
    """
        populate each team's entry in the database with core match metadata
    such as week number, venue, date, hour, day, month, and opponent.

    this function processes the raw source data and extracts meaningful
    features for each match, storing them in the target database structure.

    :param sources: dictionary of match data grouped by season and team
    :type sources: dict
    :param databaseToUpdate: target database dictionary to populate with parsed metadata
    :type databaseToUpdate: dict
    :return: None
    :rtype: None
    """
    d:dict={}
    for s in sources.keys():
        for t in sources[s].keys():
            _ = {"week":[],"venue":[],"date":[],"hour":[],
            "month":[],"day":[],"opponent":[]}
            for idx,week in enumerate(sources[s][t]['week']):
                if week != -1:
                    date = sources[s][t]['date'][idx]
                    hour = sources[s][t]['hour'][idx]
                    if hour=="":
                        hour="-:-"
                    venue = sources[s][t]['venue'][idx]
                    day  = str(datetime.strptime(date,"%d/%m/%Y").strftime("%A")).lower()
                    month = str(datetime.strptime(date,"%d/%m/%Y").strftime("%B")).lower()
                    opp = sources[s][t]['opponent'][idx]
                    _["week"].append(str(week))
                    _["venue"].append(venue)
                    _["date"].append(date)
                    _["hour"].append(hour)
                    _["day"].append(day)
                    _["month"].append(month)
                    _["opponent"].append(opp)
            databaseToUpdate[s][t].update((k,_[k]) for k in _.keys())

def computeGoalsAndResults(sources:dict, databaseToUpdate:dict)->None:
    """
        parse and compute goal-related statistics and match results from raw score data,
    and populate the database with full-time and half-time scores and outcomes.

    this function processes each match entry, extracts full-time and half-time
    goal counts, and determines match results as win ("W"), draw ("D"), or loss ("L").

    forbidden or unavailable scores are handled and marked with "-:-".

    :param sources: dictionary containing score strings and match metadata per season/team
    :type sources: dict
    :param databaseToUpdate: the database dictionary to populate with goal and result data
    :type databaseToUpdate: dict
    :return: None
    :rtype: None
    """
    forbiddens=["-:-","dnp","abor."]
    d:dict={}
    for s in sources.keys():
        for t in sources[s].keys():
            _ = {"result":[],"gf":[],"ga":[],"htgf":[],"htga":[]}
            for idx,week in enumerate(sources[s][t]['week']):
                if week != -1:
                    score_data = sources[s][t]['score'][idx]
                    result     = "-:-"
                    if score_data not in forbiddens:
                        scores:list = score_data.split()
                        gf:int = int(scores[0].split(':')[0])
                        ga:int = int(scores[0].split(':')[1])
                        if gf>ga:
                            result = "W"
                        elif gf==ga:
                            result="D"
                        else:
                            result="L"
                        
                        if len(scores)>1:
                            scoreHT=re.sub(r'[()]', '', scores[1])
                            
                            htgf = "-:-"
                            htga = "-:-"
                            if scoreHT.find('dec.')==-1 and scoreHT!="":
                                htgf:int = int(scoreHT.split(':')[0])
                                htga:int = int(scoreHT.split(':')[1])
                        else:
                            htgf="-:-"
                            htga="-:-"
                        _["result"].append(result)
                        _["gf"].append(gf)
                        _["ga"].append(ga)
                        _["htgf"].append(htgf)
                        _["htga"].append(htga)
                    else:
                        _["result"].append("-:-")
                        _["gf"].append("-:-")
                        _["ga"].append("-:-")
                        _["htgf"].append("-:-")
                        _["htga"].append("-:-")
            databaseToUpdate[s][t].update((k,_[k]) for k in _.keys())

def computeCumulatedGoals(databaseToUpdate:dict)->None:
    """
        compute cumulative full-season and venue-specific goal statistics for each team.

    this function iterates over match data in the database, extracts goals scored (gf),
    goals conceded (ga), and computes goal difference (gd) for each match.
    values are accumulated over the season for:
    - total goals (cgf, cga, cgd)
    - home matches (cgf_home, cga_home, cgd_home)
    - away matches (cgf_away, cga_away, cgd_away)

    invalid or missing score entries are treated as zero.

    :param databaseToUpdate: the database dictionary to populate with cumulative goal data
    :type databaseToUpdate: dict
    :return: None
    :rtype: None
    """
    accumulate = lambda x : [sum(x[0:i+1]) if i>0 
                        else x[0] for i in range(len(x))]
    for s in databaseToUpdate.keys():
        for t in databaseToUpdate[s].keys():
            cgf, cgf_home, cgf_away = ([] for i in range(3))
            cga, cga_home, cga_away = ([] for i in range(3))
            cgd, cgd_home, cgd_away = ([] for i in range(3))
            for w in range(len(databaseToUpdate[s][t]['week'])):
                venue = databaseToUpdate[s][t]['venue'][w]
                try:
                    gf = int(databaseToUpdate[s][t]['gf'][w])
                    ga = int(databaseToUpdate[s][t]['ga'][w])
                    gd = gf-ga
                except ValueError:
                    gf = 0
                    ga = 0
                    gd = 0
                #
                cgf.append(gf)
                cga.append(ga)
                cgd.append(gd)
                #
                if venue=="h":
                    cgf_home.append(gf)
                    cga_home.append(ga)
                    cgd_home.append(gd)
                    cgf_away.append(0)
                    cga_away.append(0)
                    cgd_away.append(0)
                else:
                    cgf_home.append(0)
                    cga_home.append(0)
                    cgd_home.append(0)
                    cgf_away.append(gf)
                    cga_away.append(ga)
                    cgd_away.append(gd)
            #
            cgf=accumulate(cgf)
            cga=accumulate(cga)
            cgd=accumulate(cgd)
            cgf_home = accumulate(cgf_home)
            cga_home = accumulate(cga_home)
            cgd_home = accumulate(cgd_home)
            cgf_away = accumulate(cgf_away)
            cga_away = accumulate(cga_away)
            cgd_away = accumulate(cgd_away)
            #
            databaseToUpdate[s][t]["cgf"]=cgf
            databaseToUpdate[s][t]["cga"]=cga
            databaseToUpdate[s][t]["cgd"]=cgd
            databaseToUpdate[s][t]["cgf_home"]=cgf_home
            databaseToUpdate[s][t]["cga_home"]=cga_home
            databaseToUpdate[s][t]["cgd_home"]=cgd_home
            databaseToUpdate[s][t]["cgf_away"]=cgf_away
            databaseToUpdate[s][t]["cga_away"]=cga_away
            databaseToUpdate[s][t]["cgd_away"]=cgd_away

def computePoints(databaseToUpdate:dict)->None:
    """
            compute cumulative points earned by each team over the season.

    this function assigns match points based on results:
    - 3 for a win (W)
    - 1 for a draw (D)
    - 0 for a loss or unplayed match

    it calculates cumulative points for:
    - all matches ("points")
    - home matches only ("homepoints")
    - away matches only ("awaypoints")

    results are stored in-place in the database.

    :param databaseToUpdate: the database dictionary to update with point data
    :type databaseToUpdate: dict
    :return: None
    :rtype: None
    """
    accumulate = lambda x : [sum(x[0:i+1]) if i>0 
                        else x[0] for i in range(len(x))]
    for s in databaseToUpdate.keys():
        for t in databaseToUpdate[s].keys():
            generalPts,homePts,awayPts = ([] for i in range(3))
            for w in range(len(databaseToUpdate[s][t]['week'])):
                venue   = databaseToUpdate[s][t]['venue'][w]
                result  = databaseToUpdate[s][t]['result'][w]
                if result=="W":
                    generalPts.append(3)
                    if venue=="h":
                        homePts.append(3)
                        awayPts.append(0)
                    else:
                        homePts.append(0)
                        awayPts.append(3)
                elif result=="D":
                    generalPts.append(1)
                    if venue=="h":
                        homePts.append(1)
                        awayPts.append(0)
                    else:
                        homePts.append(0)
                        awayPts.append(1)
                else:
                    generalPts.append(0)
                    homePts.append(0)
                    awayPts.append(0)
            databaseToUpdate[s][t]["points"]=accumulate(generalPts)
            databaseToUpdate[s][t]["homepoints"]=accumulate(homePts)
            databaseToUpdate[s][t]["awaypoints"]=accumulate(awayPts)

def computeGeneralLadder(databaseToUpdate:dict)->None:
    """
        compute general ladder (ranking) of all teams week by week.

    this function calculates the ladder based on cumulative points (primary),
    goal difference (secondary), and goals for (tertiary). each team is assigned
    a ladder position at each week in the season.

    scoring formula for sorting:
        score = 10000 * points + 100 * goal_difference + 10 * goals_for

    the result is stored in-place under the key "ladder" for each team.

    :param databaseToUpdate: the database dictionary to update with ladder info
    :type databaseToUpdate: dict
    :return: None
    :rtype: None
    """
    sort = lambda x : sorted(range(len(x)),key = x.__getitem__)
    for s in databaseToUpdate.keys():
        nbw = len(databaseToUpdate[s][next(iter(databaseToUpdate[s].keys()))]['week'])
        teams=list(databaseToUpdate[s].keys())
        for t in databaseToUpdate[s].keys():
            databaseToUpdate[s][t]["ladder"]=[]
        for i in range(nbw):
            scores=[]
            for t in databaseToUpdate[s].keys():
                pts=databaseToUpdate[s][t]['points'][i]
                iscore  = 10000*pts
                iscore += 100*databaseToUpdate[s][t]['cgd'][i]
                iscore += 10 * databaseToUpdate[s][t]['cgf'][i]
                scores.append(iscore)
            sortedIndex=sort(scores)
            sortedTeams=[teams[i] for i in sortedIndex][::-1]
            [databaseToUpdate[s][tt]['ladder'].append(idx+1) for idx,tt in enumerate(sortedTeams)]
            
def computeHomeLadder(databaseToUpdate:dict)->None:
    """
        Compute the home ladder (ranking) of all teams week by week.

    This function ranks teams based on their home performance each week,
    using cumulative home points, home goal difference, and home goals scored.
    
    The sorting score for each team is computed as:
        score = 10000 * home_points + 100 * home_goal_difference + 10 * home_goals_for

    The ladder positions are stored in-place under the key "homeladder" for each team.

    :param databaseToUpdate: The database dictionary to update with home ladder info.
    :type databaseToUpdate: dict
    :return: None
    """
    sort = lambda x : sorted(range(len(x)),key = x.__getitem__)
    for s in databaseToUpdate.keys():
        nbw = len(databaseToUpdate[s][next(iter(databaseToUpdate[s].keys()))]['week'])
        teams=list(databaseToUpdate[s].keys())
        for t in databaseToUpdate[s].keys():
            databaseToUpdate[s][t]["homeladder"]=[]
        for i in range(nbw):
            scores=[]
            for t in databaseToUpdate[s].keys():
                pts=databaseToUpdate[s][t]['homepoints'][i]
                iscore  = 10000*pts
                iscore += 100*databaseToUpdate[s][t]['cgd_home'][i]
                iscore += 10 * databaseToUpdate[s][t]['cgf_home'][i]
                scores.append(iscore)
            sortedIndex=sort(scores)
            sortedTeams=[teams[i] for i in sortedIndex][::-1]
            [databaseToUpdate[s][tt]['homeladder'].append(idx+1) for idx,tt in enumerate(sortedTeams)]

def computeAwayLadder(databaseToUpdate:dict)->None:
    """
        Compute the away ladder (ranking) of all teams week by week.

    This function ranks teams based on their away performance each week,
    using cumulative away points, away goal difference, and away goals scored.

    The sorting score for each team is computed as:
        score = 10000 * away_points + 100 * away_goal_difference + 10 * away_goals_for

    The ladder positions are stored in-place under the key "awayladder" for each team.

    :param databaseToUpdate: The database dictionary to update with away ladder info.
    :type databaseToUpdate: dict
    :return: None
    """
    sort = lambda x : sorted(range(len(x)),key = x.__getitem__)
    for s in databaseToUpdate.keys():
        nbw = len(databaseToUpdate[s][next(iter(databaseToUpdate[s].keys()))]['week'])
        teams=list(databaseToUpdate[s].keys())
        for t in databaseToUpdate[s].keys():
            databaseToUpdate[s][t]["awayladder"]=[]
        for i in range(nbw):
            scores=[]
            for t in databaseToUpdate[s].keys():
                pts=databaseToUpdate[s][t]['awaypoints'][i]
                iscore  = 10000*pts
                iscore += 100*databaseToUpdate[s][t]['cgd_away'][i]
                iscore += 10 * databaseToUpdate[s][t]['cgf_away'][i]
                scores.append(iscore)
            sortedIndex=sort(scores)
            sortedTeams=[teams[i] for i in sortedIndex][::-1]
            [databaseToUpdate[s][tt]['awayladder'].append(idx+1) for idx,tt in enumerate(sortedTeams)]

def computeForms(databaseToUpdate:dict,period:int)->None:
    """
    Compute the form ranking of all teams over a given rolling period (number of matches).

    The form is based on the sum of points earned (3 for win, 1 for draw),
    goal difference, and goals scored during the specified period.

    The score for each team is computed as:
        score = 10000 * points + 100 * goal_difference + 10 * goals_for

    Teams are ranked week by week based on their form scores, and the positions
    are stored in-place under the key "form" for each team.

    :param databaseToUpdate: The database dictionary containing teams' match data.
    :type databaseToUpdate: dict
    :param period: Number of recent matches to consider for form calculation.
    :type period: int
    :return: None
    """
    sort = lambda x : sorted(range(len(x)),key = x.__getitem__)
    accumulate = lambda x : [sum(x[0:i+1]) if i>0 
                        else x[0] for i in range(len(x))]
    for s in databaseToUpdate.keys():
        nbw = len(databaseToUpdate[s][next(iter(databaseToUpdate[s].keys()))]['week'])
        teams=list(databaseToUpdate[s].keys())
        for t in databaseToUpdate[s].keys():
            databaseToUpdate[s][t]["form"]=[]
        for i in range(nbw):
            tableScore:list=[]
            for t in databaseToUpdate[s].keys():
                min_index = max(0,i-period)
                # GOALS
                gf = databaseToUpdate[s][t]['gf'][min_index:min_index+period]
                ga = databaseToUpdate[s][t]['ga'][min_index:min_index+period]
                array_a, array_f = [],[]
                for f,a in zip(gf,ga):
                    try:
                        array_f.append(int(f))
                        array_a.append(int(a))
                    except ValueError:
                        array_f.append(0)
                        array_a.append(0)
                array_f=accumulate(array_f)
                array_a=accumulate(array_a)
                
                total_gf = array_f[-1]
                total_ga = array_a[-1]
                total_gd = total_gf-total_ga
                # PTS
                pts=0
                for r in databaseToUpdate[s][t]['result'][min_index:min_index+period]:
                    if r=="W":
                        pts+=3
                    if r=="D":
                        pts+=1
                iscore = 10000*pts+100*total_gd+10*total_gf
                tableScore.append(iscore)
                #
            sortedIndex=sort(tableScore)
            sortedTeams=[teams[i] for i in sortedIndex][::-1]
            [databaseToUpdate[s][tt]['form'].append(idx+1) for idx,tt in enumerate(sortedTeams)]

def computeOpponentInfos(databaseToUpdate:dict)->None:
    """
    For each team and each match, compute the opponent's ladder positions
    (general, home, away) and form based on the previous week, and store them.

    The first match for each team gets -1 for all opponent stats, as no prior data exists.

    The opponent's stats are taken from their ladder and form rankings one week before
    the current match index.

    Updates the database in-place, adding the following keys for each team:
    - 'opponent_ladder': opponent's general ladder position before the match
    - 'opponent_homeladder': opponent's home ladder position before the match
    - 'opponent_awayladder': opponent's away ladder position before the match
    - 'opponent_form': opponent's form ranking before the match

    :param databaseToUpdate: The database dictionary containing team and match data.
    :type databaseToUpdate: dict
    :return: None
    """
    for s in databaseToUpdate.keys():
        for t in databaseToUpdate[s].keys():
            databaseToUpdate[s][t]['opponent_ladder']=[]
            databaseToUpdate[s][t]['opponent_homeladder']=[]
            databaseToUpdate[s][t]['opponent_awayladder']=[]
            databaseToUpdate[s][t]['opponent_form']=[]
            for idx,week in enumerate(databaseToUpdate[s][t]['week']):
                if idx==0:
                    databaseToUpdate[s][t]['opponent_ladder'].append(-1)
                    databaseToUpdate[s][t]['opponent_homeladder'].append(-1)
                    databaseToUpdate[s][t]['opponent_awayladder'].append(-1)
                    databaseToUpdate[s][t]['opponent_form'].append(-1)
                else:
                    opp = databaseToUpdate[s][t]['opponent'][idx]
                    opp_ladder = databaseToUpdate[s][opp]['ladder'][idx-1]
                    opp_homeladder = databaseToUpdate[s][opp]['homeladder'][idx-1]
                    opp_awayladder = databaseToUpdate[s][opp]['awayladder'][idx-1]
                    opp_form = databaseToUpdate[s][opp]['form'][idx-1]
                    #
                    databaseToUpdate[s][t]['opponent_ladder'].append(opp_ladder)
                    databaseToUpdate[s][t]['opponent_homeladder'].append(opp_homeladder)
                    databaseToUpdate[s][t]['opponent_awayladder'].append(opp_awayladder)
                    databaseToUpdate[s][t]['opponent_form'].append(opp_form)

def loadDatabase(x: Leagues, pathToDatabase: str) -> dict:
    """
    Load the database JSON file corresponding to the specified league.

    :param x: An Enum member of Leagues specifying which database to load.
    :param pathToDatabase: Path to the directory containing the database JSON files.
    :return: The loaded database as a dictionary.
    :raises FileNotFoundError: If the path or the database file does not exist.
    :raises TypeError: If x is not an instance of Leagues.
    """
    if not Path(pathToDatabase).exists():
        raise FileNotFoundError(f"Path to database does not exist: {pathToDatabase}")
    if not isinstance(x, Leagues):
        raise TypeError(f"Expected an Enum Leagues instead of {type(x)}")

    fname = f"database_{x.name.lower()}.json"
    p = Path(pathToDatabase).joinpath(fname)
    if not p.exists():
        raise FileNotFoundError(f"Database not found: {fname}")

    with open(p, "r") as f:
        data = json.load(f)

    return dict(data)
