class graph_container:
    next_edge_id = None
    next_node_id = None
    nodes        = None
    edges        = None
    hidden_edges = None
    hidden_nodes = None
    edge_types   = None
    types        = None
    node_number  = None
    
    def __init__(self):
        self.next_edge_id = 0
        self.next_node_id = 0
        self.nodes        = {}
        self.edges        = {}
        self.hidden_edges = {}
        self.hidden_nodes = {}
        self.edge_types   = []
        self.types        = {}
        self.node_number  = {}
