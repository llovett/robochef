import urllib2
import codecs
from threading import Thread
import Queue
from bs4 import BeautifulSoup

# All the ingredients we've found while crawling
INGREDIENTS = set()
# Number of pages to search through for each recipe category
MAX_PAGES = 10
# Shows a page of salad recipes
URL = "http://allrecipes.com/recipes/salad/ViewAll.aspx?SortBy=Rating&Direction=Descending&Page=%d"
# Number of threads
THREAD_COUNT = 10

# Input queue -- contains recipe URLs to be scraped
_urls = Queue.Queue()
# Output queue - contains ingredients scraped from recipes
_ingredients = Queue.Queue()
# Error log
_errors = Queue.Queue()
# Thread pool
Pool = []

def parseRecipe():
    '''Parses the recipe on the page <url>
    Returns the list of ingredients in the format:
    [ (quantity1, ingredient1),
      (quantity2, ingredient2),
      ... ]
    '''
    while True:
        try:
            url = _urls.get_nowait()
        except Queue.Empty:
            exit()
        print ">",url
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        ingredients_html = soup.find_all(id='liIngredient')
        ingredients = []
        for ingredient in ingredients_html:
            ing_amnt = float(ingredient.get('data-grams'))
            # Ignore "empty" ingredients... don't know why these are in the HTML.
            if ing_amnt <= 0:
                continue
            ing_name = ingredient.find(class_='ingredient-name').string
            # Get rid of "to taste" in recipe names
            if 'to taste' in ing_name:
                ing_name = ','.join(ing_name.split(',')[:-1])
            _ingredients.put((ing_name,ing_amnt))

def parseListing(url, pagenum):
    '''Parses a listing of recipes given at a <url> at page <pagenum>'''
    url = URL%pagenum
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    recipes = soup.find_all('div', class_='recipes')
    for recipe in recipes:
        # Ignore unrated/low-rated recipes
        rating = recipe.find(itemprop='ratingValue').get('content')
        if not rating or float(rating) < 4.0:
            continue
        rlink = recipe.find('div',class_='rectitlediv').h3.a.get('href')
        # print '>',rlink
        # parseRecipe(rlink)
        _urls.put(rlink)

def startThreads():
    for i in xrange(THREAD_COUNT):
        t = Thread(target=parseRecipe)
        t.start()
        Pool.append(t)

def allIngredients():
    try:
        while True:
            yield _ingredients.get_nowait()
    except Queue.Empty:
        pass

if __name__ == '__main__':
    for i in xrange(1,MAX_PAGES+1):
        print "Examining page %d"%i
        parseListing(URL, i)
    startThreads()
    # Wait for threads to die
    print "Waiting for scraping to finish... (this may take awhile)"
    for t in Pool:
        t.join()

    # Save the list of ingredients:
    # Use utf-8 to preserve hilarious brand-name references and trademarks in
    # the ingredients listing
    f = codecs.open("ingredients_list.dat","w","utf-8")
    for ingredient in allIngredients():
        f.write("%s::%f\n"%(ingredient[0],ingredient[1]))
    f.close()
