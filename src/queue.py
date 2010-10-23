# -*- coding: utf-8 -*-
from collections import deque

class queue:
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