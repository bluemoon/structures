
class linked_list:
    next = None
    def __init__(self, payload=None, next=None):
        self.payload = payload
        self.next  = next
        
    def print_backward(self):
        if self.next != None:
            tail = self.next
            tail.print_backward()
        print self.payload

    
    def return_list(self):
        L = []
        node = self
        while node:
            L.append(node)
            node = self.next
        return L
    
    def __str__(self):
        return str(self.payload)
    
    def __repr__(self):
        return self.return_list()
