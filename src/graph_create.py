class create_mixin:
    def new_node(self, node_id, node_data=None, ignore_dupes=True):
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

    def new_edge(self, head_id, tail_id, edge_data=None, head_data=None,
                 tail_data=None, edge_type=None, with_merge=False):
        """ adds an edge (head_id, tail_id).
        arbitrary data can be attached to the edge via edge_data
        with_merge will merge the edge with another of of the same nodes and only add the data"""
        
        #head_id = str(head_id)
        #tail_id = str(tail_id)
        
        edge_id = self.next_edge_id
        self.next_edge_id = self.next_edge_id + 1
                
        if with_merge and edge_data:
           merged = self._with_merge(head_id, tail_id, edge_data, edge_type)
           if merged != False:
               return merged

        if edge_type not in self.edge_types:
            self.edge_types.append(edge_type)    
            self.types[edge_type] = []

        self.types[edge_type].append((head_id, edge_data, tail_id))
        self.edges[edge_id] = [head_id, tail_id, edge_data, edge_type]

        
        if head_id not in self.nodes:
            self.new_node(head_id, node_data=head_data)
            
        if tail_id not in self.nodes:
            self.new_node(tail_id, node_data=tail_data)
        
        try:
            mapped_head_data = map(None, self.nodes[head_id])
            mapped_head_data[1].append(edge_id)
            mapped_tail_data = map(None, self.nodes[tail_id])
            mapped_tail_data[0].append(edge_id)
        except Exception, E:
            raise graphException('Exception %s nodes: %s' % (E, self.nodes))
        
        return edge_id
    def new_link(self):
        pass
    def new_type(self):
        pass