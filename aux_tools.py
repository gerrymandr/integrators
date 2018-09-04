# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 14:55:37 2018

@author: Temporary
"""

import networkx as nx
import random
import copy
import numpy as np
import scipy.linalg
from scipy.sparse import csc_matrix
import scipy
from scipy import array, linalg, dot



######Tree counting

def log_number_trees(graph, weight = False):
    '''Computes the log of the number of trees, weighted or unweighted. 
    
    :graph: The input graph
    :weight: the edge variable name that describes the edge weights
    
    '''
    #Kirkoffs is the determinant of the minor..
    #at some point this should be replaced with a Cholesky decomposition based algorithm, which is supposedly faster. 
    if weight == False:
        m = nx.laplacian_matrix(graph)[1:,1:]
    if weight == True:
        m = nx.laplacian_matrix(graph, weight = "weight")[1:,1:]
    m = csc_matrix(m)
    splumatrix = scipy.sparse.linalg.splu(m)
    diag_L = np.diag(splumatrix.L.A)
    diag_U = np.diag(splumatrix.U.A)
    S_log_L = [np.log(np.abs(s)) for s in diag_L]
    S_log_U = [np.log(np.abs(s)) for s in diag_U]
    LU_prod = np.sum(S_log_U) + np.sum(S_log_L)
    return  LU_prod

def cut_edges(graph, subgraph_1, subgraph_2):
    '''Finds the edges in graph from 
    subgraph_1 to subgraph_2
    
    :graph: The ambient graph
    :subgraph_1: 
    :subgraph_2:
        

    '''
    edges_of_graph = list(graph.edges())

    list_of_cut_edges = []
    for e in edges_of_graph:
        if e[0] in subgraph_1 and e[1] in subgraph_2:
            list_of_cut_edges.append(e)
        if e[0] in subgraph_2 and e[1] in subgraph_1:
            list_of_cut_edges.append(e)
    return list_of_cut_edges

#Geometry:
    
def nw_most(nodes):
#returns the nw_most from among the nodes; that is,the element which is largest in the North/South x West/East lexicographic order.
    y_max = max( [node[1] for node in nodes])
    y_maximizers = [ node for node in nodes if node[1] == y_max]
    west_most = y_maximizers[0][0]
    for node in y_maximizers:
        if node[0] < west_most:
            west_most = node[0]
    return (west_most, y_max)