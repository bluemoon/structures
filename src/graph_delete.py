     
class delete_mixin:
    def delete_node(self, node_id):
        """ Deletes the node and all in and out arcs. """
        
        ## Remove fanin connections.
        in_edges=self.in_arcs(node_id)
        for edge in in_edges:
            self.delete_edge(edge)
            
        ## Remove fanout connections.
        out_edges = self.out_arcs(node_id)
        for edge in out_edges:
            self.delete_edge(edge)
            
        ## Delete node.
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