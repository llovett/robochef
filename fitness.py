#!/usr/bin/env python
import scraper.scraper as scraper
table = scraper.load_associations("associations.dat")
ingredients = table.keys()
healthlist = file("healthy.txt")
danklist = file("danklist.txt")
dank_string = danklist.read()
healthy_string = healthlist.read()

def balanced(recipe):
    """Returns a value describing how balanced a given recipe is. Balance
    corresponds to how often ingredients in the recipe occur with each other.
    This function is O(nN) where n is len(recipe) and N is number of
    ingredients in our association dict since we can have up to N entries in
    each bucket in our association dict. In practice this doesn't happen, so it's
    n^2.

    :recipe: list of ingredients
    :returns: integer value

    """
    balance = 0.0
    # max. is every ingredient appears w/ every other ingredient in every recipe
    max_balance = float( len(recipe) * len(recipe) * len(ingredients) ) 
    # table = scraper.load_associations("associations.dat")
    for ingr1 in recipe:
        for ingr2 in recipe:
            if ingr1 != ingr2:
                balance = balance + scraper.count_appearances(ingr1, ingr2, table)
    return balance / max_balance  # normalize


def most_fit(population, fitness_func):
    """Returns the most fit recipe in :population: according to :fitness_func:

    :population: list of recipes
    :fitness_func: function from recipes -> value
    :returns: most fit recipe in <population>

    """
    return max(population, key=fitness_func)

def healthy(recip):
    """Returns a number between 0 and 1 with the percentage of healthy ingredients in input recipe."""
    health_count = 0
    for ingred in recip:
        if ingred in healthy_string:
            health_count += 1
        return float(health_count)/len(recip)

def dank (recip):
    """Returns a number between 0 and 1 with the percentage of dank  ingredients in input recipe."""
    dank_count  = 0
    for ingred  in recip:
        if ingred in dank_string:
            dank_count  += 1
    return float(dank_count)/len(recip)
