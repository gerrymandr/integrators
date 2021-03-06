"""
Created on Mon Sep  3 19:14:25 2018

@author: Lorenzo Najt
"""

''' 

Inspired by Brendan McKays answer to math overflow: "How to sample a uniform random polyomino" https://mathoverflow.net/a/244536/41873

This uses importance sampling to estimate the integral of a function over the space of partitions of a torus into two connected subgraphs.

To run it, write a function your_function as in example functions

Then call         

torus = create_torus(n)
size = n**2/2
num_samples = 10
samples = make_samples(torus, size, num_samples)
integrate_from_samples(your_function, samples)

Proof of correctness : (Placeholder for overleaf document)

Sanity_check uses this method to integrate the constant funtion 1 and so estimate the number of pentominos.
'''
import networkx as nx
import random
import copy
import numpy as np
import scipy.linalg
from scipy.sparse import csc_matrix
import scipy
from scipy import array, linalg, dot
from aux_tools import log_number_trees, cut_edges, nw_most

class pentomino_object:
    def __init__(self, torus, root = False):
        self.torus = torus
        self.node_history = []
        self.degree_history = []
        self.stuck = False
        self.power = 1
        if root == False:
            self.degree_history.append(torus.graph["size"]**2)
            self.initialize_root()
        else:
            self.root = root
        
        self.nodes = {self.root}


    def initialize_root(self):
        n = self.torus.graph["size"]
        root = (random.choice(range(n)), random.choice(range(n)))
        self.root = root
    
    def get_candidates(self):
        '''returns the set of blocks that make pentomino when added, so that the parent of that pentomino is  the current pentomino '''
        #TODO: This can be sped up by just looking at adding blocks on the top two levels.
        balls = { frozenset({ (x[0] - 1, x[1]), (x[0] + 1, x[1]), (x[0], x[1]-1), (x[0], x[1] +1)}) for x in self.nodes }
        ball = set().union(*balls)
        boundary = ball.difference(self.nodes)
        candidates = []
        for node in boundary:
            self.nodes.add(node)
            if node == self.get_northwestmost_legal():
                candidates.append(node)
            self.nodes.remove(node)
        return candidates
    
    def get_admissible_nodes(self):
        #returns the nodes in the pentomino that can be removed without disconnecting it
        admissible = []
        for node in self.nodes:
            self.nodes.remove(node)
            n = self.torus.graph["size"]
            block_A = { covering_map(p, n) for p in self.nodes}
            G_A = nx.subgraph(self.torus,block_A)
            if nx.is_connected(G_A):
                admissible.append(node)
            self.nodes.add(node)
        return admissible
    
    def get_northwestmost_legal(self):
        #TODO This can be sped up by iterating through the nodes from in nw order, and checking along the way if it is admissible
        admissible = self.get_admissible_nodes()
        return nw_most(admissible)
    

    
    def valid_candidates(self):
        '''eliminates the blocks that would make the child no longer valid'''
        candidates = self.get_candidates()
        valid_candidates = []
        for candidate in candidates:
            self.nodes.add( candidate)
            n = self.torus.graph["size"]
            block_A = { covering_map(p, n) for p in self.nodes}
            block_B = set(self.torus.nodes).difference(block_A)
            G_B = nx.subgraph(self.torus, block_B)
            if nx.is_connected(G_B):
                valid_candidates.append(candidate)
            self.nodes.remove(candidate)
        self.degree = len(valid_candidates)
        return valid_candidates
    
    def grow(self):
        if self.stuck == True:
            return
        valid_candidates = self.valid_candidates()
        if len(valid_candidates) == 0:
            self.stuck = True
            return
        choice = random.choice(valid_candidates)
        
        #self.node_history.append(copy.deepcopy(self.nodes))
        self.degree_history.append(self.degree)
        self.nodes.add(choice)
        
    def likelihood(self):
        product = 1
        for d in self.degree_history:
moments(log_tree_compactness, 4, 3, 8, 3000,3)
            product = product * d
        return 1 / product
        

def covering_map(point, n):
    #Sends a point in the lattice to the corresponding point in the n by n discrete torus
    return (point[0] % n, point[1] % n)

def test_validity(pentomino_nodes, G):
    '''
    G: The nxn torus graph
    
    pentomino is in the lattice. We check if the image in the torus graph is a block of a connected partition.
    '''
    n = G.graph["size"] 
    
    block_A = { covering_map(p, n) for p in pentomino_nodes}
    block_B = [p for p in G.nodes() if p not in block_A]
    G_A = nx.subgraph(G,block_A)
    G_B = nx.subgraph(G,block_B)
    
    if not nx.is_connected(G_A):
        return False
    if not nx.is_connected(G_B):
        return False
    return True

def create_torus(n):
    C = nx.cycle_graph(n)
    torus = nx.cartesian_product(C,C)
    torus.graph["size"] = n
    return torus

def generate_tiling(torus, size):
    
    pentomino = pentomino_object(torus)
    i = 1
    while i < size:
        i += 1
        pentomino.grow()
    #Necessary to stop it regardless of whether the pentomino got stuck or not
    return pentomino

def integrate_from_samples(function, samples):
    '''samples is a collection of pentominos'''
    sum = 0
    for pentomino in samples:
        sum += function(pentomino)**pentomino.power / pentomino.likelihood()
    return sum / len(samples)

def make_samples(torus, size, num_samples = 10):
    samples = []
    i = 0
    while i < num_samples:
        pentomino = generate_tiling(torus, size)
        if pentomino.stuck == False:
            samples.append(pentomino)
            i += 1
        else:
            print("got stuck")
    return samples

def integrate(function, torus, size, trials = 10):
    return integrate_from_samples(function, make_samples(torus, size, trials))

###Example functions:
    
def constant_one(pentomino):
    return 1

def cut(pentomino):
    block = { covering_map(p, pentomino.torus.graph["size"]) for p in pentomino.nodes}
    return nx.cut_size(pentomino.torus, block)**pentomino.power

    
def tree_compactness(pentomino):
    block = { covering_map(p, pentomino.torus.graph["size"]) for p in pentomino.nodes}
    complementary_block = set(pentomino.torus.nodes).difference(block)
    G_A = nx.subgraph(pentomino.torus, block)
    G_B = nx.subgraph(pentomino.torus, complementary_block)
    T_A = log_number_trees(G_A)
    T_B = log_number_trees(G_B)
    cutsize = len(cut_edges(pentomino.torus, block, complementary_block))
    return np.exp(T_A + T_B)*cutsize

def log_tree_compactness(pentomino):
    block = { covering_map(p, pentomino.torus.graph["size"]) for p in pentomino.nodes}
    complementary_block = set(pentomino.torus.nodes).difference(block)
    G_A = nx.subgraph(pentomino.torus, block)
    G_B = nx.subgraph(pentomino.torus, complementary_block)
    T_A = log_number_trees(G_A)
    T_B = log_number_trees(G_B)
    cutsize = len(cut_edges(pentomino.torus, block, complementary_block))
    return T_A + T_B + np.log(cutsize)

#Tests

def sanity_check(n = 10, size = 5, num_samples = 1000):
    '''This is a good debugger, because this counts the number of tetrominos. The correct answer is 19.
    For size= 5, the correct answer is 63'''
    torus = create_torus(n)
    tests = []
    for i in range(1):
        samples = make_samples(torus, size, num_samples)
        tests.append(integrate_from_samples(constant_one, samples))
    print([test / (n**2) for test in tests])
    
    counter = {}
    for pentomino in samples:
        counter[pentomino.likelihood()] = 0
    for pentomino in samples:
        counter[pentomino.likelihood()] += 1
    counter


def cutsize(n = 10, power = 1,size = "half", num_samples = 100, trials = 3):
    if size == "half":
        size = n**2 / 2
    torus = create_torus(n)
    tests = []
    for i in range(trials):
        samples = make_samples(torus, size, num_samples)
        for p in samples:
            p.power = power
            print(p.likelihood)
        print( " Succesfully built ", len(samples), "Pentominos")
        print( "Warn that unless this is the same this might introduce some bias - so make it the same...")
        tests.append(integrate_from_samples(cut, samples) / integrate_from_samples(constant_one, samples))
    print(tests)
    
def estimate_expectation(function, n = 10, power = 1,size = "half", num_samples = 100, trials = 3):
    
    '''
    Estimate E[ function^power]
    
    '''
    if size == "half":
        size = n**2 / 2
    torus = create_torus(n)
    tests = []
    all_samples = []
    samples_set = []
    likelihoods = []
    for i in range(trials):
        samples = make_samples(torus, size, num_samples)
        samples_set.append(samples)
        for p in samples:
            p.power = power
            likelihoods.append(p.likelihood())
            all_samples.append(p)
        print( " Succesfully built ", len(samples), "Pentominos")
    estimated_sample_space_size = integrate_from_samples(constant_one, all_samples)
    print("space estimate at size: ", estimated_sample_space_size)
    print("add something here that uses the entropy likelihoods to guess at accuracy...")
    for samples in samples_set:
        tests.append(integrate_from_samples(function, samples) /estimated_sample_space_size)
    print(tests)
    
estimate_expectation(log_tree_compactness, 4, 1, 8, 150,2)
    
#cutsize(4,2)
#m =6 
#pents = make_samples(create_torus(m), (m**2)/2,1)
#[p.stuck for p in pents]
#
#p = generate_tiling(create_torus(6), 18)
#tree_compactness(p)

###Moments:
    
'''The purpose of the code here is to estimate a distribution by computing the moments'''

def moments(function, n = 10, power = 1,size = "half", num_samples = 100, trials = 3):
    
    '''
    Return estimates of E[ function^powr] for powr in range(1, power + 1)
    
    '''
    if size == "half":
        size = n**2 / 2
    torus = create_torus(n)
    moments = []
    all_samples = []
    samples_set = []
    likelihoods = []
    for i in range(trials):
        samples = make_samples(torus, size, num_samples)
        samples_set.append(samples)
        for p in samples:
            p.power = power
            likelihoods.append(p.likelihood())
            all_samples.append(p)
        print( " Succesfully built ", len(samples), "Pentominos")
    estimated_sample_space_size = integrate_from_samples(constant_one, all_samples)
    print("space estimate at size: ", estimated_sample_space_size)
    print("add something here that uses the entropy likelihoods to guess at accuracy...")
    for powr in range(1,power+1):
        tests = []
        for samples in samples_set:
            for p in samples:
                p.power = powr
            tests.append(integrate_from_samples(function, samples) /estimated_sample_space_size)
        moments.append(tests)
    print(moments)
    return moments

moments(log_tree_compactness, 4, 3, 8, 100,2)
    
