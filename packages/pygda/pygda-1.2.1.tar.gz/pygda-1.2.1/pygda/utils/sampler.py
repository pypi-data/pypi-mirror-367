import itertools
import math
import random

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import trange
from random import randrange
import random

from collections import deque
import networkx as nx


class RandomWalker:
    """
    Random walk generator for graph sampling with node2vec strategy.

    Parameters
    ----------
    G : networkx.Graph
        Input graph for random walks
    p : float, optional
        Return parameter controlling likelihood of revisiting nodes. Default: 1
    q : float, optional
        In-out parameter for differentiating between inward and outward nodes. Default: 1
    use_rejection_sampling : int, optional
        Whether to use rejection sampling strategy. Default: 0

    Notes
    -----
    Features:

    - Biased random walks
    - Flexible walk strategies
    - Efficient sampling
    - Parallel processing support
    """

    def __init__(self, G, p=1, q=1, use_rejection_sampling=0):
        """
        :param G:
        :param p: Return parameter,controls the likelihood of immediately revisiting a node in the walk.
        :param q: In-out parameter,allows the search to differentiate between "inward" and "outward" nodes
        :param use_rejection_sampling: Whether to use the rejection sampling strategy in node2vec.
        """
        self.G = G
        self.p = p
        self.q = q
        self.use_rejection_sampling = use_rejection_sampling

    def node2vec_walk(self, walk_length, start_node):
        """
        Generate node2vec walk using alias sampling.

        Parameters
        ----------
        walk_length : int
            Length of random walk
        start_node : int
            Starting node for walk

        Returns
        -------
        list
            Sequence of nodes in walk

        Notes
        -----
        Processing Steps:

        - Initialize walk from start node
        - Sample neighbors using alias tables
        - Handle transition probabilities
        - Build walk sequence
        """

        G = self.G
        alias_nodes = self.alias_nodes
        alias_edges = self.alias_edges

        walk = [start_node]

        while len(walk) < walk_length:
            cur = walk[-1]
            cur_nbrs = list(G.neighbors(cur))
            if len(cur_nbrs) > 0:
                if len(walk) == 1:
                    walk.append(
                        cur_nbrs[alias_sample(alias_nodes[cur][0], alias_nodes[cur][1])])
                else:
                    prev = walk[-2]
                    edge = (prev, cur)
                    next_node = cur_nbrs[alias_sample(alias_edges[edge][0],
                                                      alias_edges[edge][1])]
                    walk.append(next_node)
            else:
                break

        return walk

    def node2vec_walk2(self, walk_length, start_node):
        """
        Generate node2vec walk using rejection sampling.

        Parameters
        ----------
        walk_length : int
            Length of random walk
        start_node : int
            Starting node for walk

        Returns
        -------
        list
            Sequence of nodes in walk

        Notes
        -----
        Processing Steps:

        - Calculate rejection bounds
        - Sample transitions
        - Apply rejection criteria
        - Build walk sequence
        """

        def rejection_sample(inv_p, inv_q, nbrs_num):
            upper_bound = max(1.0, max(inv_p, inv_q))
            lower_bound = min(1.0, min(inv_p, inv_q))
            shatter = 0
            second_upper_bound = max(1.0, inv_q)
            if (inv_p > second_upper_bound):
                shatter = second_upper_bound / nbrs_num
                upper_bound = second_upper_bound + shatter
            return upper_bound, lower_bound, shatter

        G = self.G
        alias_nodes = self.alias_nodes
        inv_p = 1.0 / self.p
        inv_q = 1.0 / self.q
        walk = [start_node]
        while len(walk) < walk_length:
            cur = walk[-1]
            cur_nbrs = list(G.neighbors(cur))
            if len(cur_nbrs) > 0:
                if len(walk) == 1:
                    walk.append(
                        cur_nbrs[alias_sample(alias_nodes[cur][0], alias_nodes[cur][1])])
                else:
                    upper_bound, lower_bound, shatter = rejection_sample(
                        inv_p, inv_q, len(cur_nbrs))
                    prev = walk[-2]
                    prev_nbrs = set(G.neighbors(prev))
                    while True:
                        prob = random.random() * upper_bound
                        if (prob + shatter >= upper_bound):
                            next_node = prev
                            break
                        next_node = cur_nbrs[alias_sample(
                            alias_nodes[cur][0], alias_nodes[cur][1])]
                        if (prob < lower_bound):
                            break
                        if (prob < inv_p and next_node == prev):
                            break
                        _prob = 1.0 if next_node in prev_nbrs else inv_q
                        if (prob < _prob):
                            break
                    walk.append(next_node)
            else:
                break
        return walk

    def simulate_walks(self, num_walks, walk_length, workers=1, verbose=0):
        """
        Generate multiple random walks.

        Parameters
        ----------
        num_walks : int
            Number of walks per node
        walk_length : int
            Length of each walk
        workers : int, optional
            Number of parallel workers. Default: 1
        verbose : int, optional
            Verbosity level. Default: 0

        Returns
        -------
        list
            List of generated walks

        Notes
        -----
        Processing Steps:

        - Get list of nodes
        - Generate walks for each node
        - Handle parallel processing
        - Collect results
        """

        G = self.G

        nodes = list(G.nodes())
    
        results = self._simulate_walks(nodes, num_walks, walk_length)

        return results

    def _simulate_walks(self, nodes, num_walks, walk_length,):
        walks = []
        for _ in range(num_walks):
            random.shuffle(nodes)
            for v in nodes:
                if self.p == 1 and self.q == 1:
                    walks.append(self.deepwalk_walk(
                        walk_length=walk_length, start_node=v))
                elif self.use_rejection_sampling:
                    walks.append(self.node2vec_walk2(
                        walk_length=walk_length, start_node=v))
                else:
                    walks.append(self.node2vec_walk(
                        walk_length=walk_length, start_node=v))  #[1:]
        return walks

    def get_alias_edge(self, t, v):
        """
        Compute transition probabilities between nodes.

        Parameters
        ----------
        t : int
            Previous node in walk
        v : int
            Current node in walk

        Returns
        -------
        tuple
            Alias table for edge transitions

        Notes
        -----
        Processing Steps:

        - Calculate unnormalized probabilities
        - Apply p,q parameters
        - Normalize probabilities
        - Create alias table
        """
        G = self.G
        p = self.p
        q = self.q

        unnormalized_probs = []
        for x in G.neighbors(v):
            weight = G[v][x].get('weight', 1.0)  # w_vx
            if x == t:  # d_tx == 0
                unnormalized_probs.append(weight/p)
            elif G.has_edge(x, t):  # d_tx == 1
                unnormalized_probs.append(weight)
            else:  # d_tx > 1
                unnormalized_probs.append(weight/q)
        norm_const = sum(unnormalized_probs)
        normalized_probs = [
            float(u_prob)/norm_const for u_prob in unnormalized_probs]

        return create_alias_table(normalized_probs)

    def preprocess_transition_probs(self):
        """
        Preprocessing of transition probabilities for guiding the random walks.
        """
        G = self.G
        alias_nodes = {}
        for node in G.nodes():
            unnormalized_probs = [G[node][nbr].get('weight', 1.0)
                                  for nbr in G.neighbors(node)]
            norm_const = sum(unnormalized_probs)
            normalized_probs = [
                float(u_prob)/norm_const for u_prob in unnormalized_probs]
            alias_nodes[node] = create_alias_table(normalized_probs)

        if not self.use_rejection_sampling:
            alias_edges = {}

            for edge in G.edges():
                alias_edges[edge] = self.get_alias_edge(edge[0], edge[1])
                if not G.is_directed():
                    alias_edges[(edge[1], edge[0])] = self.get_alias_edge(edge[1], edge[0])
                self.alias_edges = alias_edges

        self.alias_nodes = alias_nodes
        return

class Negative_Sampler():
    """
    Negative sample generator using alias method.

    Parameters
    ----------
    G : networkx.Graph
        Input graph for sampling

    Notes
    -----
    Features:

    - Degree-based sampling
    - Efficient alias tables
    - Graph construction
    - Memory efficient
    """

    def __init__(self, G):
        self.G = G
        _probs = [G.degree(i) for i in G.nodes()]
        probs = np.array(_probs, dtype = np.float64)
        self.num = len(_probs)
        probs = probs / np.sum(probs)
        self.probs_table = np.ones(self.num, dtype = np.float64)
        self.bi_table = np.zeros(self.num, dtype = np.int32)
        p = 1.0 / self.num
        L, H= [], []
        for i in range(self.num):
            if probs[i] < p:
                L.append(i)
            else:
                H.append(i)

        while len(L) > 0 and len(H) > 0:
            l = L.pop()
            h = H.pop()
            self.probs_table[l] = probs[l] / p
            self.bi_table[l] = h
            probs[h] = probs[h] - (p - probs[l])
            if probs[h] < p:
                L.append(h)
            else:
                H.append(h)
        del L, H

    def sample(self):
        """
        Generate single negative sample.

        Returns
        -------
        int
            Sampled node index

        Notes
        -----
        Processing Steps:

        - Random index selection
        - Alias table lookup
        - Probability comparison
        - Return sample
        """
        idx  = randrange(self.num)
        if random.random() < self.probs_table[idx]:
            return idx
        else:
            return self.bi_table[idx]

    def construct_graph_origin(self, G):
        """
        Construct new graph from random walks.

        Parameters
        ----------
        G : networkx.Graph
            Input graph

        Returns
        -------
        networkx.Graph
            Constructed graph from walks

        Notes
        -----
        Processing Steps:

        - Initialize new graph
        - Generate random walks
        - Add edges with weights
        - Update node degrees
        """
        new_G = nx.Graph()
        new_G.graph['degree'] = 0
        dq = deque()
        for iter in range(self.num_walks):
            for u in G.nodes():
                dq.clear()
                dq.append(u)
                v = u
                if v not in new_G:
                    new_G.add_node(v)
                    new_G.node[v]['degree'] = 0
                for t in range(self.walk_length):
                    adj = list(G[v])
                    v_id = random.randint(0, len(adj) - 1)
                    v = adj[v_id]
                    if v not in new_G:
                        new_G.add_node(v)
                        new_G.node[v]['degree'] = 0
                    for it in dq:
                        if it in new_G[v]:
                            new_G[v][it]['weight'] += 1
                        else:
                            new_G.add_edge(v, it, weight = 1)
                        new_G.graph['degree'] += 1
                        new_G.node[v]['degree'] += 1
                        new_G.node[it]['degree'] += 1
                    dq.append(v)
                    if len(dq) > self.window_size:
                        dq.popleft()
        return new_G

def create_alias_table(area_ratio):
    """
    Create alias table for efficient sampling.

    Parameters
    ----------
    area_ratio : list
        Probability distribution (must sum to 1)

    Returns
    -------
    tuple
        Accept probabilities and alias indices

    Notes
    -----
    Processing Steps:

    - Initialize tables
    - Split into small/large probabilities
    - Balance probabilities
    - Create lookup tables
    """
    l = len(area_ratio)
    accept, alias = [0] * l, [0] * l
    small, large = [], []
    area_ratio_ = np.array(area_ratio) * l
    for i, prob in enumerate(area_ratio_):
        if prob < 1.0:
            small.append(i)
        else:
            large.append(i)

    while small and large:
        small_idx, large_idx = small.pop(), large.pop()
        accept[small_idx] = area_ratio_[small_idx]
        alias[small_idx] = large_idx
        area_ratio_[large_idx] = area_ratio_[large_idx] - \
            (1 - area_ratio_[small_idx])
        if area_ratio_[large_idx] < 1.0:
            small.append(large_idx)
        else:
            large.append(large_idx)

    while large:
        large_idx = large.pop()
        accept[large_idx] = 1
    while small:
        small_idx = small.pop()
        accept[small_idx] = 1

    return accept, alias

def alias_sample(accept, alias):
    """
    Sample from alias table.

    Parameters
    ----------
    accept : list
        Accept probabilities
    alias : list
        Alias indices

    Returns
    -------
    int
        Sampled index

    Notes
    -----
    Processing Steps:

    - Generate random index
    - Compare with accept probability
    - Return sampled index
    """
    N = len(accept)
    i = int(np.random.random()*N)
    r = np.random.random()
    if r < accept[i]:
        return i
    else:
        return alias[i]

def partition_num(num, workers):
    """
    Partition number for parallel processing.

    Parameters
    ----------
    num : int
        Total number to partition
    workers : int
        Number of workers

    Returns
    -------
    list
        Partitioned numbers per worker

    Notes
    -----
    Processing Steps:

    - Calculate base partition
    - Handle remainder
    - Return distribution
    """
    if num % workers == 0:
        return [num//workers]*workers
    else:
        return [num//workers]*workers + [num % workers]
