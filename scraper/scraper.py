import urllib, urllib2
from bs4 import BeautifulSoup

# Number of pages to search through for each recipe category
MAX_PAGES = 1
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
    ingredients_html = soup.find_all(class_='fl-ing')
    ingredients = []
    for ingredient in ingredients_html:
        ing_name = ingredient.find(class_='ingredient-name')
        # This may not exist, for things like "Black pepper to taste"
        ing_amnt = ingredient.find(class_='ingredient-amount')
        # Assume if there is no ingredient amount that the amount is very small
        ingredients.append( (ing_amnt.string if ing_amnt else 'a dash',
                             ing_name.string) )
    return ingredients

if __name__ == '__main__':
    for i in xrange(1,MAX_PAGES+1):
        url = URL%i
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        recipes = soup.find_all('div', class_='recipes')
        for recipe in recipes[:5]:
            # Ignore unrated/low-rated recipes
            rating = recipe.find(itemprop='ratingValue').get('content')
            if not rating or float(rating) < 4.0:
                continue
            rlink = recipe.find('div',class_='rectitlediv').h3.a.get('href')
            print rating, rlink
            print parseRecipe(rlink)

