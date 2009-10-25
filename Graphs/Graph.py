# -*- coding: utf-8 -*-
from utils.debug import *

from collections import deque

import numpy
from scipy import linalg
from scipy import dot
import scipy


## Original: http://www.ece.arizona.edu/~denny/python_nest/graph_lib_1.0.1.html
## Modifications: Alex Toney
class Queue:
    def __init__(self):
        self.queue = deque()

    def empty(self):
        if(len(self.queue) > 0):
            return False
        else:
            return True

    def count(self):
        return len(self.queue)

    def add(self, item):
        self.queue.append(item)	

    def remove(self):
        item = self.queue[0]
        self.queue = self.queue[1:]
        return item

class Stack:
    def __init__(self):
        self.s=[]

    def empty(self):
        if(len(self.s) > 0):
            return 0
        else:
            return 1

    def count(self):
        return len(self.s)

    def push(self, item):
        ts=[item]
        for i in self.s:
            ts.append(i)
        self.s=ts

    def pop(self):
        item=self.s[0]
        self.s=self.s[1:]
        return item


class GraphException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Graph:
    """ A graph with edges, nodes, and edge types """
    def __init__(self):
        self.next_edge_id = 0
        self.next_node_id = 0
        self.nodes = {}
        self.edges = {}
        self.hidden_edges = {}
        self.hidden_nodes = {}
        self.edge_types = []
        self.types = {}
        self.node_number = {}

    
    def copy(self, G):
        """ Performs a copy of the graph, G, into self.
        hidden edges and hidden nodes are not copied.
        node_id's remain consistent across self and G, 
        however edge_id's do not remain consistent.
        Need to implement copy operator on node_data
        and edge data.

        :param G: Hypergraph instance

        """
        
        self.nodes = {}
        self.edges = {}
        self.hidden_edges = {}
        self.hidden_nodes = {}
        self.next_edge_id = 0
        
        ## Copy nodes.
        G_node_list = G.node_list()
        for G_node in G_node_list:
            self.add_node(G_node,G.node_data(G_node))
            
        ## Copy edges.
        for G_node in G_node_list:
            out_edges = G.out_arcs(G_node)
            for edge in out_edges:
                tail_id=G.tail(edge)
                self.add_edge(G_node, tail_id, G.edge_data(edge))


    def add_node(self, node_id, node_data=None, ignore_dupes=True):
        """ Creates a new node with id node_id.  Arbitrary data can be attached
        to the node via the node_data parameter.

        :param node_id: the node's id can be any hashable type
        :param node_data: associated data

        """
        if (not self.nodes.has_key(node_id)) and (not self.hidden_nodes.has_key(node_id)):
            self.nodes[node_id]=([],[],node_data, self.next_node_id)
            self.node_number[self.next_node_id] = node_id
            
            self.next_node_id += 1
        else:
            if not ignore_dupes:
                raise GraphException('Duplicate Node: %s', node_id)


    
    def delete_node(self, node_id):
        """ Deletes the node and all in and out arcs. """
        
        #--Remove fanin connections.
        in_edges=self.in_arcs(node_id)
        for edge in in_edges:
            self.delete_edge(edge)
            
        #--Remove fanout connections.
        out_edges = self.out_arcs(node_id)
        for edge in out_edges:
            self.delete_edge(edge)
            
        #--Delete node.
        del self.nodes[node_id]


    
    def delete_edge(self, edge_id):
        """ Deletes the edge. """
        head_id = self.head(edge_id)
        tail_id = self.tail(edge_id)
        head_data = map(None, self.nodes[head_id])
        tail_data = map(None, self.nodes[tail_id])
        head_data[1].remove(edge_id)
        tail_data[0].remove(edge_id)
        del self.edges[edge_id]
        
    def delete_edge_by_type(self, edge_type):
        if edge_type in self.types:
            del self.types[edge_type]
            
    def with_merge(self, head_id, tail_id, edge_data, edge_type):
         edge = self.edge(head_id, tail_id)
         if edge != False:
             cEdge_type = self.edges[edge][3]
             if edge_type != edge_type:
                 return
             
             current_edge_data = self.edges[edge][2]
             if isinstance(current_edge_data, list):
                 if isinstance(edge_data, list):
                     for item in edge_data:
                         current_edge_data.append(item)
                 else:
                     current_edge_data.append(item)
             else:
                 raise GraphException('ListError: no list found')
             
             return edge

         else:
             return False
                     
                         
    def add_edge(self, head_id, tail_id, edge_data=None, head_data=None,
                 tail_data=None, edge_type=None, with_merge=False):
        """ adds an edge (head_id, tail_id).
        arbitrary data can be attached to the edge via edge_data
        with_merge will merge the edge with another of of the same nodes and only add the data"""
        
        edge_id = self.next_edge_id
        self.next_edge_id = self.next_edge_id + 1
        
        if with_merge and edge_data:
           merged = self.with_merge(head_id, tail_id, edge_data, edge_type)
           if merged != False:
               return merged

        if edge_type not in self.edge_types:
            self.edge_types.append(edge_type)    
            self.types[edge_type] = []

        self.types[edge_type].append((head_id, edge_data, tail_id))
            
            
        self.edges[edge_id] = [head_id, tail_id, edge_data, edge_type]

        
        if not self.nodes.has_key(head_id):
            self.add_node(head_id, node_data=head_data)
            
        if not self.nodes.has_key(tail_id):
            self.add_node(tail_id, node_data=tail_data)
        
        try:
            mapped_head_data = map(None, self.nodes[head_id])
            mapped_head_data[1].append(edge_id)
            mapped_tail_data = map(None, self.nodes[tail_id])
            mapped_tail_data[0].append(edge_id)
        except Exception, E:
            raise GraphException('Exception %s nodes: %s' % (E, self.nodes))
        
        return edge_id

    
    def hide_edge(self, edge_id):
        """ Removes the edge from the normal graph, but does not delete
        its information.  The edge is held in a separate structure
        and can be unhidden at some later time.
        """
        self.hidden_edges[edge_id] = self.edges[edge_id]
        ed = map(None, self.edges[edge_id])
        head_id = ed[0]
        tail_id = ed[1]
        hd = map(None, self.nodes[head_id])
        td = map(None, self.nodes[tail_id])
        hd[1].remove(edge_id)
        td[0].remove(edge_id)
        del self.edges[edge_id]

    
    def hide_node(self, node_id):	    
        """ Similar to above.
        Stores a tuple of the node data, and the edges that are incident to and from
        the node.  It also hides the incident edges."""
        
        degree_list = self.arc_list(node_id)
        self.hidden_nodes[node_id] = (self.nodes[node_id],degree_list)
        for edge in degree_list:
            self.hide_edge(edge)
            
        del self.nodes[node_id]

    
    def restore_edge(self, edge_id):
        ## Restores a previously hidden edge back into the graph.
        self.edges[edge_id] = self.hidden_edges[edge_id]
        ed = map(None,self.hidden_edges[edge_id])
        
        head_id = ed[0]
        tail_id = ed[1]
        
        hd=map(None,self.nodes[head_id])
        td=map(None,self.nodes[tail_id])

        hd[1].append(edge_id)
        td[0].append(edge_id)
        del self.hidden_edges[edge_id]

    #--Restores all hidden edges.
    def restore_all_edges(self):
        hidden_edge_list=self.hidden_edges.keys()
        for edge in hidden_edge_list:
            self.restore_edge(edge)

    #--Restores a previously hidden node back into the graph
    #--and restores all of the hidden incident edges, too.	
    def restore_node(self, node_id):
        hidden_node_data=map(None,self.hidden_nodes[node_id])
        self.nodes[node_id]=hidden_node_data[0]
        degree_list=hidden_node_data[1]
        for edge in degree_list:
            self.restore_edge(edge)
        del self.hidden_nodes[node_id]

    #--Restores all hidden nodes.
    def restore_all_nodes(self):
        hidden_node_list=self.nodes.keys()
        for node in hidden_node_list:
            self.nodes[node]=self.hidden_nodes[node]
            del self.hidden_nodes[node]

    #--Returns 1 if the node_id is in the graph and 0 otherwise.
    def has_node(self, node_id):
        if self.nodes.has_key(node_id):
            return True
        else:
            return False

    def node(self, node):
        if not self.has_node(node):
            return False
        else:
            return self.nodes[node]
            
    def edge(self, head_id, tail_id):
        ## returns the edge that connects (head_id,tail_id)
        if not self.has_node(head_id):
            return False
        
        out_edges = self.out_arcs(head_id)
        for edge in out_edges:
            if self.tail(edge) == tail_id:
                return edge
        
        #raise 'Graph_no_edge', (head_id, tail_id)
        return False
        #print "WARNING: No edge to return."
        
    def neighbors(self, node_id):
        return self.out_arcs(node_id)
        
    def number_of_nodes(self):
        return len(self.nodes.keys())

    def number_of_edges(self):
        return len(self.edges.keys())

    #--Return a list of the node id's of all visible nodes in the graph.
    def node_list(self):
        nl = self.nodes.keys()
        return nl[:]

    #--Similar to above.
    def edge_list(self):
        el = self.edges.keys()
        return el[:]

    def number_of_hidden_edges(self):
        return len(self.hidden_edges.keys())

    def number_of_hidden_nodes(self):
        return len(self.hidden_nodes.keys())

    def hidden_node_list(self):
        hnl=self.hidden_nodes.keys()
        return hnl[:]

    def hidden_edge_list(self):
        hel=self.hidden_edges.keys()
        return hel[:]

    def nodeByNodeNum(self, number):
        if self.node_number.has_key(number):
            return self.node_number[number]
        else:
            return False
        
    def node_out_edges(self, node):
        if self.has_node(node):
            out_arcs = self.out_arcs(node)
            for arc in out_arcs:
                edge_data = self.edge_data(arc)
                edge_type = self.edge_type(arc)
                head = self.head(arc)
                tail = self.tail(arc)
                yield (arc, edge_data, head, tail, edge_type)

    def node_in_edges(self, node):
        if self.has_node(node):
            in_arcs = self.in_arcs(node)
            for arc in in_arcs:
                edge_data = self.edge_data(arc)
                head = self.head(arc)
                tail = self.tail(arc)
                yield (arc, edge_data, head, tail)

            
    #--Returns a reference to the data attached to a node.
    def node_data(self, node_id):
        if self.has_node(node_id):
            mapped_data=map(None, self.nodes[node_id])
            return mapped_data[2]
        else:
            return False
        
    def delete_edge_type(self, Type):
        if Type in self.types:
            for edge in self.edges:
                if self.edges[edge][3] == Type:
                    self.edges[edge][3] = None
        else:
            return False
        
    def has_edge_type(self, Type):
        if Type in self.types:
            return True
        else:
            return False
        
    def edge_data(self, edge_id):
        ## Returns a reference to the data attached to an edge.
        mapped_data = map(None, self.edges[edge_id])
        return mapped_data[2]
    
    def edge_type(self, edge_id):
        mapped_data = map(None, self.edges[edge_id])
        return mapped_data[3]
    
    def edge_by_type(self, cType):
        if cType in self.types:
            for eachType in self.types[cType]:
                yield eachType
                

    #--Returns a reference to the head of the edge.  (A reference to the head id)
    def head(self, edge):
        mapped_data = map(None, self.edges[edge])
        return mapped_data[0]

    #--Similar to above.
    def tail(self, edge):
        mapped_data = map(None, self.edges[edge])
        return mapped_data[1]

    #--Returns a copy of the list of edges of the node's out arcs.
    def out_arcs(self, node_id):
        mapped_data = map(None, self.nodes[node_id])
        return mapped_data[1][:]

    #--Similar to above.
    def in_arcs(self, node_id):
        mapped_data = map(None, self.nodes[node_id])
        return mapped_data[0][:]

    def arc_pairs(self, node_id):
        for x in self.in_arcs(node_id):
            for y in self.out_arcs(node_id):
                yield (x,y)
        
    
    def arc_list(self, node_id):
        ## Returns a list of in and out arcs.
        in_list  = self.in_arcs(node_id)
        out_list = self.out_arcs(node_id)
        deg_list = []
        
        for arc in in_list:
            deg_list.append(arc)
        for arc in out_list:
            deg_list.append(arc)
        return deg_list


    def out_degree(self, node_id):
        mapped_data = map(None, self.nodes[node_id])
        return len(mapped_data[1])

    def in_degree(self, node_id):
        mapped_data = map(None, self.nodes[node_id])
        return len(mapped_data[0])

    def degree(self, node_id):
        mapped_data=map(None, self.nodes[node_id])
        return len(mapped_data[0])+len(mapped_data[1])	

    def is_cyclic(self):
        pass

    def find_between(self, head, tail, edge_type=None):
        nodes_already_queued={head:0}
        bfs_list  = []
        bfs_queue = deque()
        bfs_queue.append(head)	
        
        while bfs_queue:
            current_node = bfs_queue.popleft()
            bfs_list.append(current_node)
            out_edges = self.out_arcs(current_node)
            for edge in out_edges:
                if edge_type:
                    if self.edges[edge][3] != edge_type:
                        continue
                        
                if tail == self.tail(edge):
                    break
                
                if not nodes_already_queued.has_key(self.tail(edge)):
                    nodes_already_queued[self.tail(edge)]=0
                    bfs_queue.append(self.tail(edge))
                    
        return bfs_list
        
    # --- Traversals ---

    #--Performs a topological sort of the nodes by "removing" nodes with indegree 0.
    #--If the graph has a cycle, the Graph_topological_error is thrown with the
    #--list of successfully ordered nodes.
    def topological_sort(self):
        topological_list  = []
        topological_queue = Queue()
        indeg_nodes = {}
        node_list=self.nodes.keys()
        for node in node_list:
            indeg = self.in_degree(node)
            if indeg == 0:
                topological_queue.add(node)
            else:
                indeg_nodes[node] = indeg
        while not topological_queue.empty():
            current_node = topological_queue.remove()
            topological_list.append(current_node)
            out_edges = self.out_arcs(current_node)
            for edge in out_edges:
                tail = self.tail(edge)
                indeg_nodes[tail] = indeg_nodes[tail]-1
                if indeg_nodes[tail] == 0:
                    topological_queue.add(tail)
        #--Check to see if all nodes were covered.
        if len(topological_list) != len(node_list):
            raise GraphException(topological_list)
        return topological_list

    #--Performs a reverse topological sort by iteratively "removing" nodes with out_degree=0
    #--If the graph is cyclic, this method throws Graph_topological_error with the list of
    #--successfully ordered nodes.
    def reverse_topological_sort(self):
        topological_list  = []
        topological_queue = Queue()
        outdeg_nodes = {}
        node_list = self.nodes.keys()
        for node in node_list:
            outdeg = self.out_degree(node)
            if outdeg == 0:
                topological_queue.add(node)
            else:
                outdeg_nodes[node] = outdeg
        while not topological_queue.empty():
            current_node = topological_queue.remove()
            topological_list.append(current_node)			
            in_edges = self.in_arcs(current_node)
            for edge in in_edges:
                head_id = self.head(edge)
                outdeg_nodes[head_id] = outdeg_nodes[head_id]-1
                if outdeg_nodes[head_id] == 0:
                    topological_queue.add(head_id)
        #--Sanity check.
        if len(topological_list) != len(node_list):
            raise Graph_topological_error, topological_list
        return topological_list

    #--Returns a list of nodes in some DFS order.
    def dfs(self, source_id):
        nodes_already_stacked = {source_id:0}
        dfs_list  = []		
        dfs_stack = Stack()

        dfs_stack.push(source_id)

        while not dfs_stack.empty():
            current_node = dfs_stack.pop()
            dfs_list.append(current_node)
            out_edges = self.out_arcs(current_node)
            for edge in out_edges:
                if not nodes_already_stacked.has_key(self.tail(edge)):
                    nodes_already_stacked[self.tail(edge)] = 0
                    dfs_stack.push(self.tail(edge))
                    
        return dfs_list

    #--Returns a list of nodes in some BFS order.
    def bfs(self, source_id):
        nodes_already_queued={source_id:0}
        bfs_list  = []
        bfs_queue = Queue()
        bfs_queue.add(source_id)	

        while not bfs_queue.empty():
            current_node = bfs_queue.remove()
            bfs_list.append(current_node)
            out_edges = self.out_arcs(current_node)
            for edge in out_edges:
                if not nodes_already_queued.has_key(self.tail(edge)):
                    nodes_already_queued[self.tail(edge)]=0
                    bfs_queue.add(self.tail(edge))
                    
        return bfs_list



    
    def back_bfs(self, source_id):
        """
        Returns a list of nodes in some BACKWARDS BFS order.
        Starting from the source node, BFS proceeds along back edges.
        """
        nodes_already_queued = {source_id:0}
        bfs_list  = []
        bfs_queue = Queue()
        bfs_queue.add(source_id)

        while not bfs_queue.empty():
            current_node = bfs_queue.remove()
            bfs_list.append(current_node)
            in_edges = self.in_arcs(current_node)
            for edge in in_edges:
                if not nodes_already_queued.has_key(self.head(edge)):
                    nodes_already_queued[self.head(edge)]=0
                    bfs_queue.add(self.head(edge))

        return bfs_list


    def adjacencyList(self):
        wholeList = []
        allEdges = self.edge_list()        
        for edge in allEdges:
            head = self.head(edge)
            tail = self.tail(edge)
            
            L = self.nodes[head][3]
            R = self.nodes[tail][3]
            
            wholeList.append((L, R))
            
        return wholeList
    
    def adjacencyMatrix(self):
        wholeList = []
        nodeCount = self.number_of_nodes()
        adjMatrix = numpy.mat(numpy.zeros((nodeCount, nodeCount)))
        allEdges = self.edge_list()
        
        for edge in allEdges:
            head = self.head(edge)
            tail = self.tail(edge)
            
            L = self.nodes[head][3]
            R = self.nodes[tail][3]
            
            adjMatrix[L, R] += 1
            
        return adjMatrix
    
    def incidenceOfNode(self, Node, edgeCount):
        nodeCount = 1
        vertex = 0

        if len(self.out_arcs(Node)) < 1:
            return
        
        incidMatrix = numpy.zeros((edgeCount, nodeCount))
        for arc in self.out_arcs(Node):
            incidMatrix[arc, vertex] = 1
        
        return incidMatrix
    
    def incidenceMatrix(self):
        wholeList = []
        ## |V| = nodeCount
        nodeCount = self.number_of_nodes()+1
        ## |E| = edgeCount
        edgeCount = self.number_of_edges()+1
        incidMatrix = numpy.zeros((edgeCount, nodeCount), int)
        allNodes = self.node_list()
        
        for node in allNodes:
            vertex = self.node(node)[3]
            for arc in self.out_arcs(node):
                if arc < edgeCount:
                    incidMatrix[arc, vertex] += 1
                
        return incidMatrix
    
    def _gMatrix(self, alpha=0.85, nodelist=None):
        M = self.adjacencyMatrix()
        (n,m) = M.shape
        
        Danglers = numpy.where(M.sum(axis=1)==0)
        
        for d in Danglers[0]:
            M[d]=1.0/n
        
        M=M/M.sum(axis=1)
        
        P = alpha * M + (1 - alpha) * numpy.ones((n,n)) / n
        return P
    
    def pageRank(self, alpha=0.85, max_iter=100, Tolerance=1.0e-6, nodelist=None):
        M = self._gMatrix(alpha, nodelist)   
        (n,m) = M.shape
        ## should be square
        x = numpy.ones((n))/n
        for i in range(max_iter):
            xlast = x
            x = numpy.dot(x,M) 
            ## check convergence, L1 norm            
            err=numpy.abs(x-xlast).sum()
            if err < n*Tolerance:
                return numpy.asarray(x).flatten()

    def SVD(self, Node, dropAlpha=0.90):
        """
        Singular value decomposition for *Node*
        
        :param Node: the node you want to run SVD on.
        :param dropAlpha: the cosine similiarity limit.
        """

        incidMatrix = self.incidenceMatrix()
        ## |V| = nodeCount
        nodeCount = self.number_of_nodes()
        ## |E| = edgeCount
        edgeCount = self.number_of_edges()+1
        
        ## dont run if it will just fail;
        if nodeCount < 3 and edgeCount < 3:
            return
        
        ## As you know the SVD will give you a product A = U∑V*,
        ## where the columns of U consists of left singular vectors
        ## for each respective singular value σ.
        
        ## Create the edge incidence matrix
        U, S, Vh = linalg.svd(incidMatrix)
        Vt = Vh.T

        diagMatrix = linalg.diagsvd(S,len(incidMatrix),len(Vh))

        nSigma = diagMatrix
        U2   = numpy.mat(U)
        V2   = numpy.mat(Vh)
        Eig2 = numpy.mat(nSigma)

        if not Node:
            nodeList = self.nodes.items()
            curNode = nodeList.pop(0)[0]
        else:
            curNode = Node
            
        newNode = self.incidenceOfNode(curNode, edgeCount)
        if newNode == None:
            return
        
        if Eig2.shape[0] == Eig2.shape[1]:
            ## this shape is useless to us, singular matrix
            return
        
        U    = U2.T
        Eig  = Eig2.I.T
        node = newNode.T

        ## debug(U.shape, prefix="U")
        ## debug(Eig2.shape, prefix="Eig")
        ## debug(node.shape, prefix="node")
        ## debug(incidMatrix.shape, prefix="IncidenceMatrix")
        
        node = node * U * Eig2
        
        each = {}
        count = 0
        
        for x in V2:
            cosineSim = (node * x.T) / (linalg.norm(x) * linalg.norm(node))
            if cosineSim > dropAlpha:
                each[self.nodeByNodeNum(count)] = cosineSim.A.tolist()[0][0]

            count += 1
            
        return each
            
    def SVD_each(self):
        """ run SVD on every item in the graph return
        a list which corresponds to a dict of each SVD """
        nodeList = self.nodes.items()
        each = []
        
        while nodeList:
            curNode = nodeList.pop(0)[0]
            currentSVD = self.SVD(Node=curNode)
            each.append({curNode:currentSVD})

        return each
        
    def to_dot_file(self, primary_type=None, exclude_filter=None):
        import pydot
        import time
        import cPickle
        import hashlib
        import os
        
        self_hash = hashlib.sha224(cPickle.dumps(self)).hexdigest()

        unique_colors = ['skyblue1','maroon1','yellowgreen','olivedrab3','red3','royalblue3',]
        unique_color_dict = {}
        
        callgraph = pydot.Dot(graph_type='digraph', fontname="Verdana", fontsize="9")
        node_list = self.nodes.keys()

        for types in self.edge_types:
            if types != None:
                color = unique_colors.pop()
                unique_color_dict[types] = color
            
        for node in node_list:
            for edge in self.node_out_edges(node):
                edge_type = edge[4]
                
                if unique_color_dict.has_key(edge_type):
                    color = unique_color_dict[edge_type]
                else:
                    color = 'black'
                
                if len(edge[1]) == 1:
                    label = str(edge[1][0])
                else:
                    label = ','.join(map(str, edge[1]))
                        
                if primary_type != None and edge_type == primary_type:
                    head = pydot.Node(edge[2], shape='doublecircle')
                    tail = pydot.Node(edge[3], shape='doublecircle')
                    callgraph.add_node(head)
                    callgraph.add_node(tail)
                        
                    current_edge = pydot.Edge(edge[2], edge[3], label=label, color=color, weight="3", fontsize="8")
                else:
                    current_edge = pydot.Edge(edge[2], edge[3], label=label, color=color, fontsize="8")

                callgraph.add_edge(current_edge)

        if primary_type and primary_type in self.types:
            heads = []
            for x in self.types[primary_type]:
                heads.append(x[0])
            sentence = '-'.join(heads)
            file_name = '%s-%s' % (sentence, self_hash)
        else:
            file_name = self_hash
            
        file = os.path.join('data/graphs', '%s-map.svg' % file_name.strip().replace('/','')[:100])
        if not os.path.exists(file):
            callgraph.write_svg(file)

        print 'Graph: %s' % (file)

