
class modifier_mixin:
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
            
    def _with_merge(self, head_id, tail_id, edge_data, edge_type):
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


    