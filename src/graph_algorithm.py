class algorithm_mixin:
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

    def incidenceList(self):
        wholeList = []
        ## |V| = nodeCount
        nodeCount = self.number_of_nodes()+1
        ## |E| = edgeCount
        edgeCount = self.number_of_edges()+1
        allNodes = self.node_list()
        
        for node in allNodes:
            vertex = self.node(node)[3]
            for arc in self.out_arcs(node):
                wholeList.append([arc, vertex])
                
        return wholeList


    
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
