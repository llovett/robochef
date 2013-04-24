#!/usr/bin/env python
import scraper.scraper as scraper


######################
#  helper functions  #
######################

def choose_parents(population, fitness_func):
    """Chooses the two most fit individuals from <table> based on
    <fitness_func>

    :population: recipe dictionary - maps recipe names to list of ingredients
    :fitness_func: a function returning the fittest individual from a
    population
    :returns: a list of the two fittest individuals in <table>

    """
    # assume fitness_func returns the recipe name
    parent1 = fitness_func(population)
    parent2 = fitness_func(dict((recipe_name, population[recipe_name])
        for recipe_name in population.keys() if recipe_name != parent1))
    return [parent1, parent2]


def main():
    # table = scraper.load_associations("associations.dat")
    # ingredients = scraper.load_recipes("ingredients_list.dat")
    # print table
    # print ingredients
    # print ingredients
    # print "balsamic vinegar: " + str(table["balsamic vinegar"])
    # print "... occurs with salt %d times" % scraper.count_appearances("balsamic vinegar", "salt", table)


if __name__ == '__main__':
    main()
