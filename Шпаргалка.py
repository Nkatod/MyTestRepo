# -*- coding: utf-8 -*-
"""
Created on Thu May 28 18:48:05 2020

@author: User
"""

def infinite_sequence(_max=1000000):    # бесконечный генератор
    num = 0
    while num <= _max:
        yield num
        num += 1
        
l = {1, 2, 3, 4}

new_l = [i*2 for i in l] # пример итератора
new_gen = (i*2 for i in l) # пример генератора
v = next(new_gen)
#csv_gen = (row for row in open(file_name))

