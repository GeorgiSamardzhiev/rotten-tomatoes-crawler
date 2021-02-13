import re
import requests
from bs4 import BeautifulSoup
from requests import TooManyRedirects

class RottenTomatoesMovieScrapper:

    ROTTEN_TOMATOES_BASE_URL = 'https://www.rottentomatoes.com/'

    MOVIE_SYNOPSIS_PATTERN = re.compile(r'data-qa="movie-info-synopsis">.+?<', re.DOTALL)
    RATING_PATTERN = re.compile(r'ratingValue":"[0-9]*')
    GENRE_PATTERN = re.compile(r'MovieGenres":".*"')
    DIRECTOR_PATTERN = re.compile(r'Director:</div>.+?</div>', re.DOTALL)
    THEATER_DATE_PATTERN = re.compile(r'\(Theaters.+?<div class="meta-value" data-qa="movie-info-item-value">.+?<time datetime=.+?</time>', re.DOTALL)
    DVD_DATE_PATTERN = re.compile(r'\(Streaming.+?<div class="meta-value" data-qa="movie-info-item-value">.+?<time datetime=.+?</time>', re.DOTALL)
    BOX_OFFICE_PATTERN =  re.compile(r'data-qa="movie-info-item-label">Box Office.+?<div class="meta-value" data-qa="movie-info-item-value">.+?</div>', re.DOTALL)
    RUNTIME_PATTERN = re.compile(r'Runtime.+?class="meta-value" data-qa="movie-info-item-value">.+?</time>', re.DOTALL)
    STUDIO_PATTERN = re.compile(r'Production Co:</div>.+?<div class="meta-value" data-qa="movie-info-item-value">.+?</div>', re.DOTALL)   

    PAGE_PATTERN = re.compile(r'Page 1 of \d+')
    REVIEW_PATTERN = re.compile(r'<div class="the_review" data-qa="review-text">[^<]*<\/div>')
    REVIEW_RATING_PATTERN = re.compile(r'Original Score:\s([A-Z](\+|-)?|\d(.\d)?(\/\d)?)')
    FRESH_PATTERN = re.compile(r'small\s(fresh|rotten)\"')
    CRITIC_PATTERN = re.compile(r'data-qa="review-critic-link">.+?</a>')
    PUBLISHER_PATTERN = re.compile(r'data-qa="review-critic-publication">.+?</em>')
    DATE_PATTERN = re.compile(r'[a-zA-Z]+\s\d+,\s\d+')

    def to_snake_case(self, s):
        s = s.lower()
        remove_items = "'-:,"
        for i in remove_items:
            if i in s:
                s = s.replace(i,'')
        s = s.strip('"')
        return s.replace(' ', '_')

    def _get_rotten_tomatoes_page_from_movie_title(self, title, reviews = False):
        return f'{self.ROTTEN_TOMATOES_BASE_URL}m/{self.to_snake_case(title)}{"/reviews" if reviews else ""}' 

    def _get_movie_html_page(self, movie_title):
        movie_url = self._get_rotten_tomatoes_page_from_movie_title(movie_title)
        try:
            res = requests.get(movie_url)
            return res.text
        except TooManyRedirects:
            return ''

    def _get_movie_reviews_html_page(self, movie_title, reviews = False):
        movie_url = self._get_rotten_tomatoes_page_from_movie_title(movie_title, reviews)
        try:
            res = requests.get(movie_url)
            return res.text
        except TooManyRedirects:
            return ''
    
    def _is_page_not_found(self, html_page):
        return '<h1>404 - Not Found</h1>' in html_page

    def _get_synopsis(self, movie_html_page):
        synopsis = re.findall(self.MOVIE_SYNOPSIS_PATTERN, movie_html_page)
        if len(synopsis) == 0:
            return ''
        return synopsis[0].split('>')[-1].replace('<', '').strip()

    def _get_rating(self, movie_html_page):
        rating = re.findall(self.RATING_PATTERN, movie_html_page)
        if len(rating) == 0:
            return ''
        return rating[0].split('"')[-1].strip()

    def _get_genre(self, movie_html_page):
        genres = re.findall(self.GENRE_PATTERN, movie_html_page)
        if len(genres) == 0:
            return ''
        return genres[0].split('"')[-2].strip().replace('\\u002F', '/')
    
    def _get_runtime(self, movie_html_page):
        runtime = re.findall(self.RUNTIME_PATTERN, movie_html_page)
        if len(runtime) == 0:
            return ''
        return runtime[0].split('<')[-2].strip().split('\n')[1].strip()

    def _get_director(self, movie_html_page):
        directors = re.findall(self.DIRECTOR_PATTERN, movie_html_page)
        if len(directors) == 0:
            return ''
        directors = directors[0].replace('&amp;','and').split('>')
        res = list()
        for director in directors:
            if '</a' in director:
                res.append(director.replace('</a',''))
        return ', '.join(res)

    def _get_studio(self, movie_html_page):
        studio = re.findall(self.STUDIO_PATTERN, movie_html_page)
        if len(studio) == 0:
            return ''
        return re.sub(r'\s', r'', studio[0].split('<')[-2].strip().split('>')[-1]).strip()

    def _get_dates(self, movie_html_page):
        theater_date = re.findall(self.THEATER_DATE_PATTERN, movie_html_page)
        dvd_date = re.findall(self.DVD_DATE_PATTERN, movie_html_page)
        res_theater_date = ''
        res_dvd_date = ''
        if len(theater_date) != 0:
            res_theater_date = theater_date[0].split('>')[-2].split('<')[0].strip()
        if len(dvd_date) != 0:
            res_dvd_date = dvd_date[0].split('>')[-2].split('<')[0].strip()
        return res_theater_date, res_dvd_date
        

    def _get_box_office(self, movie_html_page):
        box_office = re.findall(self.BOX_OFFICE_PATTERN, movie_html_page)
        if len(box_office) == 0:
            return ''
        res_box_office = box_office[0].split('>')[-2].split('<')[0].strip()
        return res_box_office

    def _get_review_rating(self, review_soup):
        rating = re.findall(self.REVIEW_RATING_PATTERN, review_soup)
        if len(rating) == 0:
            return ''
        r = rating[0][0]
        if '/1' in r:
            r_split = r.split('/')
            if r_split[-1] == '1':
                r_split[-1] = '10'
            r = '/'.join(r_split)
        return r

    def _get_review_freshness(self, review_soup):
        fresh = re.findall(self.FRESH_PATTERN, review_soup)
        if len(fresh) == 0:
            return ''
        return fresh[0]

    def _get_review_critic(self, review_soup):
        critic = re.findall(self.CRITIC_PATTERN, review_soup)
        if len(critic) == 0:
            return ''
        return critic[0].split('>')[-2].replace('</a', '').strip()

    def _get_review_publisher(self, review_soup):
        publishers = re.findall(self.PUBLISHER_PATTERN, review_soup)
        if len(publishers) == 0:
            return ''

        publisher = publishers[0]
        publisher = publisher.replace('"subtle">', '')
        publisher = publisher.replace('</em>','')
        return publisher

    def _get_review_date(self, review_soup):
        date = re.findall(self.DATE_PATTERN, review_soup)
        if len(date) == 0:
            return ''
        return date[0].strip('"')

    def _get_reviews(self, movie_html_page):
        reviews = dict()
        reviews['reviews'] = list()
        reviews['rating'] = list()
        reviews['fresh'] = list()
        reviews['critic'] = list()
        reviews['publisher'] = list()
        reviews['date'] = list()

        reviews_soup = movie_html_page.split('="review_table')[1].split('row review_table_row')
        reviews_soup.pop(0)

        for review_soup in reviews_soup:
            review = re.findall(self.REVIEW_PATTERN, review_soup)
            if len(review) > 0:
                r = review[0]
                for iden in ['<div class="the_review" data-qa="review-text">','</div>']:
                    r = r.replace(iden,'')
                reviews['reviews'].append(r.strip())
                reviews['rating'].append(self._get_review_rating(review_soup))
                reviews['fresh'].append(self._get_review_freshness(review_soup))
                reviews['critic'].append(self._get_review_critic(review_soup))
                reviews['publisher'].append(self._get_review_publisher(review_soup))
                reviews['date'].append(self._get_review_date(review_soup))

        return reviews

    def _get_movie_metadata(self, movie_html_page):
        metadata = dict()
        metadata['synopsis'] = self._get_synopsis(movie_html_page)
        metadata['rating'] = self._get_rating(movie_html_page)
        metadata['genre'] = self._get_genre(movie_html_page)
        metadata['runtime'] = self._get_runtime(movie_html_page)
        metadata['director'] = self._get_director(movie_html_page)
        metadata['studio'] = self._get_studio(movie_html_page)
        metadata['theater_date'], metadata['dvd_date'] = self._get_dates(movie_html_page)
        metadata['box_office'] = self._get_box_office(movie_html_page)
        return metadata


    def get_movie_info(self, movie_title):
        info = dict()
        movie_html_page = self._get_movie_html_page(movie_title)
        if self._is_page_not_found(movie_html_page):
            return None
        info['metadata'] = self._get_movie_metadata(movie_html_page)
        movie_html_page = self._get_movie_reviews_html_page(movie_title, reviews = True)
        if not self._is_page_not_found(movie_html_page):
            info['reviews'] = self._get_reviews(movie_html_page)
        return info
