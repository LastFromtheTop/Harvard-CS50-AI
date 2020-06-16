import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    #corpus = crawl('corpus2')
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    #print(f'\n\n prob sum is {sum(ranks.values())}\n')
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    #print(f'\n\n prob sum is {sum(ranks.values())}\n')


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    
    oneminusd = (1-damping_factor) / len(corpus.keys())
    if len(corpus[page]) == 0:
        page_prob = damping_factor / len(corpus.keys())
    else:
        page_prob = damping_factor / len(corpus[page])
    prob_dist = {}
    for key in corpus.keys():
        if key == page:
            prob_dist[key] = oneminusd + page_prob
        else:
            prob_dist[key] = oneminusd
                    
    return prob_dist

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    for key in corpus.keys():
        if(len(corpus[key]) == 0):
            corpus[key] = set(corpus.keys())

    samples = {}
    no_of_links = len(corpus.keys()) - 1
    if(no_of_links == -1): no_of_links = len(corpus.keys()) - 1
    links = [*corpus.keys()]
    sample_count = n
    while (sample_count > 0):
        page = random.randint(0, no_of_links)
        transition_model(corpus, links[page], damping_factor)
        
        if(links[page] not in samples):
            samples[links[page]] = 0
        
        samples[links[page]] += 1
        
        no_of_links = len(corpus[links[page]]) - 1
        if(no_of_links == -1): 
            no_of_links = len(corpus.keys()) - 1
            links = [*corpus.keys()]
        else:
            links = [*corpus[links[page]]]
        sample_count -= 1
        
    for key in samples.keys():
        samples[key] = samples[key] / n
    
    return samples


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    converged = False
    N = len(corpus)
    d = damping_factor
    
    for key in corpus.keys():
        if(len(corpus[key]) == 0):
            corpus[key] = set(corpus.keys())
    
    inward_info = {}
    for page, links in corpus.items():
        for link in links:
            if link not in inward_info:
                inward_info[link] = []                    
            inward_info[link].append(page)
            
        
    page_ranks = {}
    for k in corpus.keys():
        page_ranks[k] = 1/N 
        
    # Calculate 1-d/N
    part1 = (1-d) / N
    
    prev_vals = []
    while (converged != True):
        curr_page_ranks = copy.deepcopy(page_ranks)
        for page,links in corpus.items():
            
            #Calculate SIGMA(PR(i) / Numlinks(i))
            part2 = 0
            for link in inward_info.get(page, {}):
                if(len(corpus[link]) == 0):
                    part2 += curr_page_ranks[link]/len(corpus.keys())
                else:
                    part2 += curr_page_ranks[link]/len(corpus[link])

            page_ranks[page] = part1 + (d * part2)
            
        if(len(prev_vals) != 0):
            change = [abs(page_ranks[key] - prev_vals[key]) < 0.001 for key in page_ranks.keys()]
                
            #change = [x1 - x2 < 0.001 for (x1, x2) in zip(page_ranks, prev_vals)]
            converged = all(change)
            
        prev_vals = copy.deepcopy(page_ranks)
        #print(f'scores are {page_ranks.values()}')
               
    return page_ranks

if __name__ == "__main__":
    main()
