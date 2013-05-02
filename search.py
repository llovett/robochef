#!/usr/bin/env python
import codecs
from fitness import *
import random
import scraper.scraper as scraper
import sys

######################
#  helper functions  #
######################

def generate_population(size):
    """Generates a random population of size :size: from ingredients
    in :table:"""
    ingredients = []
    recipes = []
    # fill ingredients list
    with codecs.open("ingredients_list.dat", "rb", "utf-8") as f:
        ingredients += [ingr.rstrip() for line in f for ingr in line.split("###")]

    while len(recipes) < size:
        recipe = set()
        # for now, all recipes of length 10
        while len(recipe) < 10:
            recipe.add(random.choice(ingredients))
        recipes.append(recipe)
    return recipes

def choose_parents(population, fitness_func):
    """Chooses the two most fit individuals from <table> based on
    <fitness_func>

    :population: list of recipes, which are lists of ingredients
    :fitness_func: a function returning the fittest individual from a
    population
    :returns: a list of the two fittest recipes

    THIS CAN BE A BOTTLENECK

    """
    parent1 = max( population, key = lambda x : fitness_func(x) )
    parent2 = max( [recipe for recipe in population if recipe != parent1],
                   key = lambda x : fitness_func(x) )
    # parent1 = random.choice(population)
    # parent2 = random.choice(population)
    # while parent1 == parent2:
    #     parent2 = random.choice(population)
    # print "Chose some parents."
    return (parent1, parent2)


def cross(recip1, recip2):
    """Crosses :recip1: with :recip2:, returning the resulting recipe.
    Currently using arbitrary crossover point."""

    # cross_point = len(recip1) / 2
    # return recip1[:cross_point] + recip2[cross_point:]

    # print "received recip1, recip2 from run_genetic():\n"
    # print recip1
    # print recip2
    ret = set()
    while len(ret) < len(recip1):
        if random.randint(0, 1) == 0:
            ret.add(random.sample(recip1, 1)[0])           
        else:
            ret.add(random.sample(recip2, 1)[0])
    # print "returning %s from cross()" % str(ret)
    return ret

def mutate(recipe):
    """Mutates :recipe: by grabbing a random ingredient, and adding to the
    recipe the ingredient which occurs most often with the randomly selected
    ingredient.

    :recipe: list of ingredients
    :table: association table
    :returns: new recipe

    """
    rand_ingr = random.choice(table.keys())
    while rand_ingr in recipe:
        rand_ingr = random.choice(table.keys())
    ret = set(random.sample(recipe, len(recipe) - 1))
    ret.add(rand_ingr)
    return ret
    # ingr_chosen = False
    # ingr1 = ""
    # ingr2 = ""
    # for ingr1 in recipe:  # try until we've entirely failed
    #     ingr2 = max( table[ingr1].items(), key = lambda x : x[1] )[0]
    #     if ingr2 is not None and ingr2 not in recipe:
    #         ret = set([ingr for ingr in recipe if ingr != ingr1])
    #         ret.add(ingr2)
    #         return ret
    # # otherwise, just choose a random recipe from the table
    # return set([ingr for ingr in recipe if ingr != ingr1].append(random.choice(table.keys())))
    


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
        # print "size of current population: %d" % len(population)
        # if i % 20 == 0:
        print "...iteration %d" % i
        C = []  # child population
        for x in xrange(len(population)):
            p1, p2 = choose_parents(population, fitness_func)
            child = cross(p1, p2)

            if random.random() < mutation_prob:
                child = mutate(child)
            if fitness_func(child) >= fitness_thresh:
                individual_found = True

            C.append(child)
        # print "size of child population: %d" % len(C)
        population = C
        i += 1
    the_one = most_fit(population, fitness_func)
    print "Returning most fit (%f) individual" % fitness_func(the_one)
    return the_one

def main():
    if len(sys.argv) < 4:
        print "USAGE: python search.py <population size> <iterations> <balanced|dank|healthy> [mutation prob]"
        exit(0)
    pop_sz = int(sys.argv[1])
    iterations = int(sys.argv[2])
    fit_func = sys.argv[3]
    mut_prob = 0.01
    if len(sys.argv) == 5:
        mut_prob = float(sys.argv[4])

    fitnesses = {'balanced':balanced,
                 'dank':dank,
                 'healthy':healthy}

    most_fit = run_genetic(generate_population(pop_sz),
                           iterations,
                           fitnesses[fit_func],
                           100, # Ignoring fitness threshold argument
                           mut_prob)

    print "Bon Apetit! --- "
    print most_fit
    
if __name__ == '__main__':
    main()
