import urllib2
import codecs
from threading import Thread
from Queue import Queue
from bs4 import BeautifulSoup

# All the ingredients we've found while crawling
INGREDIENTS = set()
# Number of pages to search through for each recipe category
MAX_PAGES = 10
# Shows a page of salad recipes
URL = "http://allrecipes.com/recipes/salad/ViewAll.aspx?SortBy=Rating&Direction=Descending&Page=%d"

def parseRecipe(url):
    '''Parses the recipe on the page <url>
    Returns the list of ingredients in the format:
    [ (quantity1, ingredient1),
      (quantity2, ingredient2),
      ... ]
    '''
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
        INGREDIENTS.add(ing_name)
        # Assume if there is no ingredient amount that the amount is very small
        ingredients.append( (ing_amnt, ing_name) )
    return ingredients

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
        print '>',rlink
        parseRecipe(rlink)

if __name__ == '__main__':
    for i in xrange(1,MAX_PAGES+1):
        print "Examining page %d"%i
        parseListing(URL, i)

    # Save the list of ingredients
    f = codecs.open("ingredients_list.dat","w","utf-8")
    for ingredient in INGREDIENTS:
        f.write(ingredient+"\n")
    f.close()
