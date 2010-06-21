class NDPDA_FSM:
    def __init__(self, initial_state, memory=[]):
        self.feature_path = feature_path(fsm=self)
        self.state_transitions = {}

        self.input_symbol = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.next_state = None
        self.action = None
        self.memory = memory
        self.output = []
        self.registers = {}
        self.counter = 0
        self.words = {}
        self.frame_memory = {}
        self.frames = []
        
        
    def reset (self):
        self.current_state = self.initial_state
        self.input_symbol = None
        
    
    def match_register_state(self, in_state):
        if len(in_state.items()) < 1:
            return True
        
        head = in_state.keys()[0] 
        state = in_state[head]
        output = None
        match_value = None
            
        for cur_state in state:
            if 'str' in cur_state[0]:
                self.feature_path.resolve_words(cur_state, self.words)
                words_to_match = cur_state[2][0].split('|')
                debug(words_to_match)
                if cur_state[0] in words_to_match:
                    return True
            
            match = self.feature_path.match_action(cur_state, self.words)
            if not match_value:
                match_value = match
            else:
                if match_value:
                    match_value = match
                    
                    
        return match_value
                    
                
    def set_register_state(self, in_state):
        if len(in_state.items()) < 1:
            return

        head = in_state.keys()[0]
        state = in_state[head]
        #debug(state)
        for cur_state in state:
            self.feature_path.do_action(cur_state, self.words)
    
    def add_transition(self, input_symbol, state, next_state=None, name=None, action=None):
        if next_state is None:
            next_state = state
            
        self.state_transitions[input_symbol] = (state, action, next_state, name)
        
    def get_transition(self, input_symbol):
        for regex_transitions in self.state_transitions:
            regex = regex_transitions
            regex.replace('\.', '[a-z]')
            if regex[0] == ' ':
                regex = regex[1:]
                
            if regex[0] != '(':
                to_compile = '(%s)' % regex
            else:
                to_compile = regex
                
            re_to_match = re.compile(to_compile)
            re_search = re_to_match.match(input_symbol)
            if re_search:
                yield self.state_transitions[regex_transitions]


    def process(self, input_symbol):
        output = None
        self.input_symbol = input_symbol
        for transitions in self.get_transition(self.input_symbol):
            self.state, self.action, self.next_state, self.name = transitions
            if self.match_register_state(self.state):
                self.set_register_state(self.next_state)
                break
            

            #output = {self.name:{'set_state':self.next_state}}

        self.frames.append((self.counter, self.frame_memory))
        self.frame_memory = {}
        self.current_state = self.next_state
        self.next_state = None
        self.counter += 1
        if output:
            return output
        
        
        
    def process_list (self, input_symbols):
        debug(input_symbols)
        output = []
        current_item = 0
        for s in input_symbols:
            #debug(s)
            runner = self.process(s)
            output.append((current_item, runner))
                
            current_item += 1
            
        return self.words

