import urllib2, codecs, Queue, sys
from threading import Thread
from bs4 import BeautifulSoup

# All the ingredients we've found while crawling
INGREDIENTS = set()
# Number of pages to search through for each recipe category
MAX_PAGES = 10
# Shows a page of salad recipes
URL = "http://allrecipes.com/recipes/salad/ViewAll.aspx?SortBy=Rating&Direction=Descending&Page=%d"
# Number of threads
THREAD_COUNT = 50

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
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        ingredients_html = soup.find_all(id='liIngredient')
        ingredients = []
        for ingredient in ingredients_html:
            ing_amnt = float(ingredient.get('data-grams'))
            # Ignore "empty" ingredients (no amount)
            if ing_amnt <= 0:
                continue
            ing_name = ingredient.find(class_='ingredient-name').string.strip()
            # Get rid of "to taste" in recipe names
            if 'to taste' in ing_name:
                ing_name = ','.join(ing_name.split(',')[:-1])
            # Ignore "empty" ingredients (no name)
            if len(ing_name) < 1:
                continue
            ingredients.append((ing_name,ing_amnt))
            _ingredients.put((ing_name,ing_amnt))
        # Add ingredients to Recipe
        _recipes.put(ingredients)
        # Log this URL as scraped
        _log.put("> %s"%url)

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
        items = sorted([v for v in val.items() if v[1] > 0],
                       cmp=lambda x,y:int(y[1])-int(x[1]))
        if len(items) > 0:
            associated = ["%s (%d)"%(v[0],v[1]) for v in items]
            print key.upper()
            for a in associated:
                print " "*10,a
            print
                
def load_associations(filename):
    '''Loads a table of ingredient associations from a file.

    Returns the table in the following format:
    {'A':
      {'B': number_of_times_B_appears_with_A,
       'C': number_of_times_C_appears_with_A,
       'D': number_of_times_D_appears_with_A,
       ... },
     'B':
      {'E': number_of_times_E_appears_with_B,
       'F': number_of_times_F_appears_with_B,
       ... },
     ...
    }

    Where A-F are names of ingredients, and appearance counts are ints.
    '''
    associations = {}
    # Dump associations table into a file
    with codecs.open(filename,"r","utf-8") as f:
        # Get list of ingredients
        ingredients = ["%s"%s for s in f.readline().split("###")]
        for i in ingredients:
            associations[i] = {}
            counts = []
            for index,number in enumerate(f.readline().split("#")):
                count = int(number)
                if count > 0:
                    associations[i][ingredients[index]] = count
    return associations

def count_appearances(a, b, associations):
    '''Returns the number of times ingredient <a> appears with ingredient <b>,
    accordint to the associations table <associations>.
    
    a, b are both strings.
    Returns an int.
    '''
    return associations[a].get(b) or 0

def _test_associations(filename):
    a = load_associations(filename)
    ingredients = a.keys()
    for i in ingredients:
        for j in ingredients:
            print "%s with %s = %d"%(i,j,count_appearances(i,j,a))

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
    with codecs.open("ingredients_list.dat","w","utf-8") as f:
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

    # Dump associations table into a file
    with codecs.open("associations.dat","w","utf-8") as f:
        ingredients = associations.keys()
        # Header: contains all ingredients as list delimited by "###"
        f.write("%s\n"%("###".join(ingredients)))
        for i in ingredients:
            counts = []
            for j in ingredients:
                count = associations[i].get(j)
                counts.append(str(count) if count else "0")
            # Associations counts
            f.write("%s\n"%("#".join(counts)))
