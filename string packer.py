# -*- coding: utf-8 -*-
"""
Created on Thu May 28 18:07:11 2020

@author: User
"""

# In Python, isalpha() is a built-in method used for string handling. 
# The isalpha() methods returns “True” if all characters in the string are alphabets,
# Otherwise, It returns “False”.
# This function is used to check if the argument includes only alphabet characters 
#(mentioned below).

def packer(s):
    if s.isalpha():        # Defines if unpacked
        result = []
        for i in s:
            if s.count(i) > 1:
                if (i + str(s.count(i))) not in result:
                    result.append(i + str(s.count(i)))
            else:
                result.append(i)
        print(result)
    else:
        print('Somethings went wrong..')
    return False

def packer_toString(s):
    if s.isalpha():        # Defines if unpacked
        result = ''
        prev = ''
        counter = 0
        for i in s:
            if prev != i:
                if counter > 0: 
                    result = result + prev + str(counter)
                prev = i
                counter = 1
            else:
                counter = counter + 1
        if counter > 0: 
            result = result + prev + str(counter)
    else:
        print('Somethings went wrong..')
    return result

testStr = "aaaaaaaaaaaabbbccccdaaaaaaa"
packer(testStr)
print(packer_toString(testStr))

li = list(testStr)