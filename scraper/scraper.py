import urllib, urllib2
from bs4 import BeautifulSoup

# Number of pages to search through for each recipe category
MAX_PAGES = 10
# Shows a page of salad recipes
URL = "http://allrecipes.com/recipes/salad/ViewAll.aspx?SortBy=Rating&Direction=Descending&Page=%d"

if __name__ == '__main__':
    for i in xrange(1,MAX_PAGES+1):
        url = URL%i
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        recipes = soup.find_all('div', class_='recipes')
        for recipe in recipes:
            # Ignore unrated/low-rated recipes
            rating = recipe.find(itemprop='ratingValue').get('content')
            if not rating or float(rating) < 4.0:
                continue
            rlink = recipe.find('div',class_='rectitlediv').h3.a.get('href')
            print rating, rlink

