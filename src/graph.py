# -*- coding: utf-8 -*-
from collections import deque
from graph_container import graph_container
from graph_modifier  import modifier_mixin
from graph_create    import create_mixin
from graph_delete    import delete_mixin

from queue import queue
from stack import stack

import numpy

## Original: http://www.ece.arizona.edu/~denny/python_nest/graph_lib_1.0.1.html
## Modifications: Alex Toney
class graphException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)


class graph(graph_container, modifier_mixin, delete_mixin, create_mixin):
    """ A graph with edges, nodes, and edge types """
    
    def __init__(self):
        graph_container.__init__(self)
        #modifier_mixin.__init__(self)
        #delete_mixin.__init__(self)   
        #create_mixin.__init__(self)

    def has_node(self, node_id):
        """ Returns 1 if the node_id is in the graph and 0 otherwise. """
        return node_id in self.nodes

    def node(self, node):
        """ Returns a singular node that you specify """
        if not self.has_node(node):
            return False
        else:
            return self.nodes[node]
            
    def node_list(self):
        """ Return node list."""
        return list(self.nodes.keys())   
        
    def edge(self, head_id, tail_id):
        """ returns the edge that connects (head_id,tail_id) """
        if not self.has_node(head_id):
            return False
        
        out_edges = self.out_arcs(head_id)
        for edge in out_edges:
            if self.tail(edge) == tail_id:
                return edge
        
    
        return False
    
        
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
        if node_id in self.nodes:
            mapped_data = map(None, self.nodes[node_id])
            return mapped_data[0][:]
        else:
            return False

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

