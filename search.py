#!/usr/bin/env python
# import fitness
import random
import scraper.scraper as scraper


######################
#  helper functions  #
######################

def choose_parents(population, fitness_func):
    """Chooses the two most fit individuals from <table> based on
    <fitness_func>

    :population: list of recipes, which are lists of ingredients
    :fitness_func: a function returning the fittest individual from a
    population
    :returns: a list of the two fittest recipes

    """
    # assume fitness_func returns the correct list
    parent1 = fitness_func(population)
    parent2 = fitness_func(recipe for recipe in population if recipe != parent1)
    return (parent1, parent2)


def run_genetic(population, timeout, fitness_func, fitness_thresh, mutation_prob):
    """Runs a genetic algorithm on :population: of recipes until a fit enough
    recipe is created or :timeout: is reached
    :population: list of recipes
    :timeout: max. number of generations
    :fitness_func: function to evaluate fitness of a recipe
    :fitness_thresh: min. fitness value required to return an individual
    :returns: the fittest recipe
    """
    individual_found = False
    i = 0

    while not individual_found and i < timeout:
        C = []  # child population
        for x in xrange(len(population)):
            p1, p2 = choose_parents(population, fitness_func)
            child = cross(p1, p2)

            if random.random() < mutation_prob:
                child = mutate(child)
            if fitness_func(child) >= fitness_thresh:
                individual_found = True

            C.append(child)
            population = C
            i = i + 1
    return most_fit(population, fitness_func)



def main():
    table = scraper.load_associations("associations.dat")
    # ingredients = scraper.load_recipes("ingredients_list.dat")
    # print table
    # print ingredients
    print "balsamic vinegar: " + str(table["balsamic vinegar"])
    print "... occurs with salt %d times" % scraper.count_appearances("balsamic vinegar", "salt", table)
    print "... occurs with itself %d times" % scraper.count_appearances("balsamic vinegar", "balsamic vinegar", table)


if __name__ == '__main__':
    main()
