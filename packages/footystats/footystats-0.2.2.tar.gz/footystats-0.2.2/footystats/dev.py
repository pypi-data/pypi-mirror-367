from footystats.leagues import Leagues
from footystats.sources import makeSources
from footystats.sources import updateSources
from footystats.database import makeDatabase
from footystats.database import loadDatabase
from footystats.nextmatches import getMatches
from footystats.nextmatches import exportMatches
# from footystats.nextmatches import buildMatches
from footystats.sofascore import makeMatchRegister
from pathlib import Path
import asyncio


if __name__ == '__main__':
    sourcesroot     =Path(r"D:\FOOTBALL\sources")
    databaseroot    =Path(r"D:\FOOTBALL\databases")
    sofaroot_past   =Path(r"D:\FOOTBALL\teams\past")
    sofaroot_now    =Path(r"D:\FOOTBALL\teams\current")
    #
    # asyncio.run(makeSources(Leagues.ALL, sourcesroot))
    # asyncio.run(updateSources(Leagues.LIGUE1,sourcesroot))
    #
    # makeDatabase(Leagues.LALIGA, sourcesroot, databaseroot,debug=False,debugYear="2024")
    # database = loadDatabase(Leagues.LALIGA,databaseroot)
    #
    # listMatches:dict = asyncio.run((getMatches(Leagues.ALL, date="")))
    # exportMatches(Path.cwd(),listMatches)
    # buildMatches(listMatches,databaseroot)
    #
    #asyncio.run(makeMatchRegister(Leagues.ALL,sofaroot_past,False))   # False = for 5 previous seasons
    asyncio.run(makeMatchRegister(Leagues.ALL,sofaroot_now,True))      # True = for current season
