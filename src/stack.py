class stack:
    def __init__(self):
        self.s = []

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
