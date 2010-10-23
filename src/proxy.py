#!/usr/bin/env python
# encoding: utf-8
"""
proxy.py

Created by Bradford A Toney on 2010-07-01.
"""



class ObjectProxy(object):
    def __init__(self, dictionary=None):
        if dictionary:
            for a, b in dictionary.items():
                if isinstance(b, (list, tuple)):
                    setattr(self, a, [ObjectProxy(x)\
                     if isinstance(x, dict) else x for x in b])
                else:
                    setattr(self, a, ObjectProxy(b)\
                     if isinstance(b, dict) else b)

    def __repr__(self):
        return '<ObjectProxy [%s]>' % ', '.join(self.__dict__.keys())
    
    def __getattr__(self, attr):
        try:
            return dict.__getattr__(self, attr)
        except:
            if not self.__dict__.has_key(attr):
                self.__dict__[attr] = ObjectProxy()
            return self.__dict__[attr]
        
    def __setattr__(self, attr, value):
        if self.__dict__.has_key(attr) or '__' in attr:
            dict.__setattr__(self, attr, value)
        else:
            self.__dict__[attr] =  value


if __name__ == '__main__':
	main()

