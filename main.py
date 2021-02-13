from movie_title_scraper import MovieTitleScraper
from rotten_tomatoes_scraper import RottenTomatoesMovieScrapper
import json
import os  

fileDir = os.path.dirname(os.path.realpath('__file__'))

if __name__ == "__main__":
    movie_title_scraper = MovieTitleScraper()
    movie_info_scraper = RottenTomatoesMovieScrapper()
    years = [1989, 1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020]

    for year in years:
        try:
            os.mkdir(f'{year}')
        except:
            print('Could not create folder')

    for year in years:
        names = movie_title_scraper.scrape_movie_name_for_year(year)
        for name in names:
            try:
                info = movie_info_scraper.get_movie_info(name)
                f = open(os.path.join(fileDir, f'{year}\\{name}.json'), "w+")
                f.write(json.dumps(info))
                f.close()
            except:
                print(f'no such film: {name}')
