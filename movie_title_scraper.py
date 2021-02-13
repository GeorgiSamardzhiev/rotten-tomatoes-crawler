import datetime
import re
import requests
from bs4 import BeautifulSoup
from requests import TooManyRedirects

class MovieTitleScraper:
   
    WIKIPEDIA_BASE_URL = 'https://en.wikipedia.org/wiki/'
    CURRENT_YEAR = datetime.datetime.now().year
    MOVIE_TITLE_PATTERN = re.compile(r'<i><a href=\"/wiki/[\w\(\)\%.\,\_\:\;\"]+\stitle=\"[\w\s\(\)\%.\,\_\:\;\'\"\-]+\"')

    def _wikipedia_page_movie_titles_in_year(self, year):
        if year < 1899 or year > self.CURRENT_YEAR:
            raise Exception(f'Year should be between 1899 and {self.CURRENT_YEAR}')
        return f'{self.WIKIPEDIA_BASE_URL}{str(year)}_in_film'
    
    def _get_movie_name_from_title_html_list_element(self, html_list_element_title):
        html_list_element_title = html_list_element_title.split('title=')[1].replace('"','')
        html_list_element_title = re.sub(r'Category\:\d+','', html_list_element_title)
        html_list_element_title = re.sub(r'\s\((\d+\s)?([\w\s]+)?film\)','', html_list_element_title)
        return html_list_element_title
    
    def scrape_movie_name_for_year(self, year):
        wikipedia_page_url = self._wikipedia_page_movie_titles_in_year(year)
        soup = ''
        try:
            res = requests.get(wikipedia_page_url)
            soup = BeautifulSoup(res.content, 'html.parser')
        except TooManyRedirects:
            soup = ''
        
        movie_titles = list(
                            filter(lambda movie_title: movie_title != '', 
                                   map(self._get_movie_name_from_title_html_list_element,
                                       re.findall(self.MOVIE_TITLE_PATTERN, str(soup)))))
        movie_titles.pop(0)
        return movie_titles
