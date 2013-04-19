import urllib2, codecs, Queue, sys
from threading import Thread
from bs4 import BeautifulSoup

# All the ingredients we've found while crawling
INGREDIENTS = set()
# Number of pages to search through for each recipe category
MAX_PAGES = 1
# Shows a page of salad recipes
URL = "http://allrecipes.com/recipes/salad/ViewAll.aspx?SortBy=Rating&Direction=Descending&Page=%d"
# Number of threads
THREAD_COUNT = 20

# Input queue -- contains recipe URLs to be scraped
_urls = Queue.Queue()
# Output queue - contains ingredient listings scraped from recipes
_recipes = Queue.Queue()
# Output queue - contains all ingredients found
_ingredients = Queue.Queue()
# The log
_log = Queue.Queue()
LOGGING = False
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
        _log.put("> %s"%url)
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        ingredients_html = soup.find_all(id='liIngredient')
        ingredients = []
        for ingredient in ingredients_html:
            ing_amnt = float(ingredient.get('data-grams'))
            # Ignore "empty" ingredients... don't know why these are in the HTML.
            if ing_amnt <= 0:
                continue
            ing_name = ingredient.find(class_='ingredient-name').string.strip()
            # Get rid of "to taste" in recipe names
            if 'to taste' in ing_name:
                ing_name = ','.join(ing_name.split(',')[:-1])
            if len(ing_name) < 1:
                continue
            ingredients.append((ing_name,ing_amnt))
            _ingredients.put((ing_name,ing_amnt))
        # Add ingredients to Recipe
        _recipes.put(ingredients)

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
        _urls.put(rlink)

def startThreads():
    for i in xrange(THREAD_COUNT):
        t = Thread(target=parseRecipe)
        t.start()
        Pool.append(t)

def logging():
    while LOGGING:
        try:
            msg = _log.get_nowait()
            sys.stdout.write(msg+"\n")
            sys.stdout.flush()
        except Queue.Empty:
            pass
        
def startLogging():
    global LOGGING
    LOGGING = True
    logger = Thread(target=logging)
    logger.start()
    return logger

def stopLogging(logger):
    global LOGGING
    LOGGING = False
    logger.join()

def allObject(q):
    def allQ():
        try:
            while True:
                yield q.get_nowait()
        except Queue.Empty:
            pass
    return allQ

def print_associations(assoc):
    '''Prints an associations table. Useful for debugging.'''
    for key,val in assoc.iteritems():
        associated = ["%s (%d)"%(v[0],v[1]) for v in val.items() if v[1] > 0]
        if len(associated) > 0:
            print key.upper()
            for a in associated:
                print " "*10,a
            print
                
if __name__ == '__main__':
    for i in xrange(1,MAX_PAGES+1):
        print "Examining page %d"%i
        parseListing(URL, i)
    startThreads()
    logger = startLogging()
    # Wait for threads to die
    print "Waiting for scraping to finish... (this may take awhile)"
    for t in Pool:
        t.join()
    stopLogging(logger)

    # Write the table of ingredient associations
    allIngredients = allObject(_ingredients)
    associations = {}
    for ing in allIngredients():
        # Make a map for each ingredient
        associations[ing[0]] = {}
    # Iterate over all ingredients:
    # Use utf-8 to preserve hilarious brand-name references and trademarks in
    # the ingredients listing
    f = codecs.open("ingredients_list.dat","w","utf-8")
    allRecipes = allObject(_recipes)
    for recipe in allRecipes():
        f.write("%s\n"%("###".join(ingredient[0] for ingredient in recipe)))
        for ingredient in recipe:
            for other_ingredient in recipe:
                if other_ingredient == ingredient:
                    continue
                if not other_ingredient[0] in associations[ingredient[0]].keys():
                    associations[ingredient[0]][other_ingredient[0]] = 0
                else:
                    associations[ingredient[0]][other_ingredient[0]] += 1

    f.close()

    print_associations(associations)
