import csv
import itertools
import sys
import copy

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # check for proper usage
    if len(sys.argv) != 2:
        sys.exit("usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    # people = load_data('data/family0.csv')
                       
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                #p = joint_probability(people, {"Harry"}, {"James"}, {"James"})
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def find_prob(people, one_gene, two_genes, parent):
    if one_gene != set() and parent in one_gene:
        return 0.5
    elif two_genes != set() and parent in two_genes:
        return 0.99    
    else:
        return 0.01


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_probability = 1
    genecount = -1
    trait_people = copy.deepcopy(have_trait)
    for person, info in people.items():
        if(person in trait_people) : have_trait = True
        else: have_trait = False

        if one_gene != set() and person in one_gene:
            genecount = 1
        elif two_genes != set() and person in two_genes:
            genecount = 2
        else:
            genecount = 0

        if info['mother'] and info['father']:

            #Find Mother Gene Copies
            mother_prob = find_prob(people, one_gene, two_genes, info['mother'])
            not_mother_prob = 1 - mother_prob

            #Find Father Gene Copies
            father_prob = find_prob(people, one_gene, two_genes, info['father'])
            not_father_prob = 1 - father_prob

            if genecount == 1:
                #Find ((P(A ^ ~B) + P(~A ^ B)) * P(trait) 
                joint_probability *= ((mother_prob * not_father_prob) + (not_mother_prob * father_prob)) * PROBS['trait'][genecount][have_trait]

            elif genecount == 2:
                #Find P(A ^ B) * P(trait) 
                joint_probability *= (mother_prob * father_prob) * PROBS['trait'][genecount][have_trait]

            elif genecount == 0:
                #Find P(~A ^ ~B) * P(trait) 
                joint_probability *= (not_mother_prob * not_father_prob) * PROBS['trait'][genecount][have_trait]

        else:
            joint_probability *= PROBS['gene'][genecount] * PROBS['trait'][genecount][have_trait]

    return joint_probability

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    gene_count = -1

    for name in probabilities.keys():
        if one_gene != set() and name in one_gene:
            gene_count = 1
        elif two_genes != set() and name in two_genes:
            gene_count = 2
        else:
            gene_count = 0

        #print(f'gene count is {gene_count}')
        probabilities[name]['gene'][gene_count] += p
        if name in have_trait:
            probabilities[name]['trait'][True] += p
        else:
            probabilities[name]['trait'][False] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    b_probabilities = copy.deepcopy(probabilities)
    for person, probs in b_probabilities.items():
        for copyg, prob in probs['gene'].items():
            if(sum(probs['gene'].values()) != 0):
                probabilities[person]['gene'][copyg] = prob / sum(probs['gene'].values())
        
        for bol, prob in probs['trait'].items():
            if(sum(probs['trait'].values()) != 0):
                probabilities[person]['trait'][bol] = prob / sum(probs['trait'].values())


if __name__ == "__main__":
    main()
