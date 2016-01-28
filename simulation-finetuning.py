#! /bin/env python2
# coding: utf-8

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random as rd
import os
from pickle import dump, load

class Data:
    def __init__(self):
        self.m_list1 = []
        self.m_list2 = []

N = 100
M = 100
MAX = N + M + 1
MAX_EDGE = 380
MAX_DEG = 450
ITERATIONS = 50000
S1 = 0.
T1 = 1.
S2 = 0.
T2 = 1.
beta = 0.5
NUMGRAPH = 10
NSIM = 10
NAME = "finetuning"

# initial fraction of cooperators
p1, p2 = .5, .5
# number of cooperators
cc1, cc2 = 0, 0
# fraction of cooperators
r1, r2 = np.zeros(ITERATIONS + 1, dtype=np.float), np.zeros(ITERATIONS + 1, dtype=np.float)

payoff = np.array(
        [
            [1, S1],
            [T1, 0]
        ]
        , dtype=np.float, ndmin=2)

payoff2 = np.array(
        [
            [1, S2],
            [T2, 0]
        ]
        , dtype=np.float, ndmin=2)


def interaction(x, y):
    if x < N:
        return payoff[g.node[x]['strategy']][g.node[y]['strategy']]
    else:
        return payoff2[g.node[x]['strategy']][g.node[y]['strategy']]

def change_prob(x, y):
    return 1. / (1 + np.exp(-beta * (y - x)))

def complete():
    return nx.complete_bipartite_graph(N, M)

def random():
    g = nx.Graph()
    g.add_nodes_from(np.arange(0, N + M, 1, dtype=np.int))
    while g.number_of_edges() < MAX_EDGE:
        a, b = rd.randint(0, N - 1), rd.randint(N, N + M - 1)
        if b not in g[a]:
            g.add_edge(a, b)

    return g

def set_initial_strategy(g):
    global cc1, cc2
    coop = range(0, int(p1 * N), 1) + range(N, int(p2 * M) + N, 1)
    cc1 = int(p1 * N)
    defect = set(range(0, N + M, 1)) - set(coop)
    cc2 = int(p2 * M)
    coop = dict(zip(coop, len(coop) * [0]))
    defect = dict(zip(defect, len(defect) * [1]))
    nx.set_node_attributes(g, 'strategy', coop)
    nx.set_node_attributes(g, 'strategy', defect)

def fitness(x):
    ret = 0
    for i in g.neighbors(x):
        ret += interaction(x, i)
    return ret

def simulate():
    global cc1, cc2
    it = 0
    while it < ITERATIONS:
        it += 1
        if it % 2:
            a = rd.randint(0, N - 1)
        else:
            a = rd.randint(N, N + M - 1)
        if len(g.neighbors(a)) == 0:
            it -= 1
            continue
        b = g.neighbors(a)[rd.randint(0, len(g.neighbors(a)) - 1)]
        b = g.neighbors(b)[rd.randint(0, len(g.neighbors(b)) - 1)]
        if a == b:
            it -= 1
            continue

        assert (a < N and b < N) or (a >= N and b >= N)
        if g.node[a]['strategy'] != g.node[b]['strategy']:
            fa, fb = fitness(a), fitness(b)
            l = np.random.random()
            p = change_prob(fa, fb)
            if l <= p:
                if a < N:
                    if g.node[a]['strategy'] == 0:
                        cc1 -= 1
                    else:
                        cc1 += 1
                else:
                    if g.node[a]['strategy'] == 0:
                        cc2 -= 1
                    else:
                        cc2 += 1
                nx.set_node_attributes(g, 'strategy', { a:g.node[b]['strategy'] })

        r1[it] = float(cc1) / N
        r2[it] = float(cc2) / M


nbins = 21
Trange = np.linspace(1,2,nbins)
Srange = np.linspace(-1,0,nbins)
mag1 = np.zeros((nbins, nbins), dtype=np.float)
mag2 = np.zeros((nbins, nbins), dtype=np.float)

for G in xrange(NUMGRAPH):
    g = random()
    i = 0
    data = Data()

    for S1 in Srange:
        S2 = S1
        j = 0
        for T1 in Trange:
            global payoff, payoff2
            T2 = T1
            payoff = np.array([
                [1, S1],
                [T1, 0]], dtype=np.float, ndmin=2)
    
            payoff2 = np.array([
                [1, S2],
                [T2, 0]], dtype=np.float, ndmin=2)
        
            for SS in xrange(NSIM):
                mag1 = np.zeros((nbins, nbins), dtype=np.float)
                mag2 = np.zeros((nbins, nbins), dtype=np.float)

                set_initial_strategy(g)
                simulate()
                
                mag1[i][j] = np.mean(r1[-1000:])
                mag2[i][j] = np.mean(r2[-1000:])
                data.m_list1.append((S1, T1, S2, T2, mag1))
                data.m_list2.append((S1, T1, S2, T2, mag2))

            j += 1
        i += 1
    f = open('random graph {1} {0}.grph'.format(G, NAME), 'w')
    dump(data,f,2)
    f.close()
    
    print("Finished Graph {0}".format(G))

g = complete()
i = 0
data = Data()
for S1 in Srange:
    j = 0
    for T1 in Trange:
        global payoff, payoff2
        payoff = np.array([
            [1, S1],
            [T1, 0]], dtype=np.float, ndmin=2)

        payoff2 = np.array([
            [1, S2],
            [T2, 0]], dtype=np.float, ndmin=2)
    
        for SS in xrange(NSIM):
            mag1 = np.zeros((nbins, nbins), dtype=np.float)
            mag2 = np.zeros((nbins, nbins), dtype=np.float)

            set_initial_strategy(g)
            simulate()
            
            mag1[i][j] = np.mean(r1[-1000:])
            mag2[i][j] = np.mean(r2[-1000:])
            data.m_list1.append((S1, T1, S2, T2, mag1))
            data.m_list2.append((S1, T1, S2, T2, mag2))

        j += 1
    i += 1
f = open('complete graph {1} {0}.grph'.format(G, NAME), 'w')
dump(data,f,2)
f.close()

print("Finished Graph {0}".format(G))

p = './graphs/'
sc_graphs = []
for _,_,c in os.walk(p):
    for a,x in enumerate(c):
        pp = os.path.join(p,x)
        f = open(pp, 'rb')
        g = load(f)
        sc_graphs.append(g)

for G, g in sc_graphs:
    i = 0
    data = Data()

    for S1 in S1range:
        j = 0
        for T1 in T1range:
            global payoff, payoff2
            for S2 in S2range:
                for T2 in T2range:
                    payoff = np.array([
                        [1, S1],
                        [T1, 0]], dtype=np.float, ndmin=2)
            
                    payoff2 = np.array([
                        [1, S2],
                        [T2, 0]], dtype=np.float, ndmin=2)
                
                    for SS in xrange(NSIM):
                        mag1 = np.zeros((nbins, nbins), dtype=np.float)
                        mag2 = np.zeros((nbins, nbins), dtype=np.float)
        
                        set_initial_strategy(g)
                        simulate()
                        
                        mag1[i][j] = np.mean(r1[-1000:])
                        mag2[i][j] = np.mean(r2[-1000:])
                        data.m_list1.append((S1, T1, S2, T2, mag1))
                        data.m_list2.append((S1, T1, S2, T2, mag2))

            j += 1
        i += 1
    f = open('scalefree graph {1} {0}.grph'.format(G, NAME), 'w')
    dump(data,f,2)
    f.close()
    
    print("Finished Graph {0}".format(G))