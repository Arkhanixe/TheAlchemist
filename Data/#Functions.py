#Functions.py
#imports all but then we have to use it like math.sqrt(25)
import math
#imports function
from math import sqrt
#This makes it so we dont have to do math.sqrt(), now we can just do sqrt()
from math import *
#importing
#from <module> import <function>
"""
def add():
	add = +
	add_1 = +=
def subtract():
	subtract = -
	subtract_1 = -=
def multiplication():
	multiply = *
	power = **

def division():
	divide with decimal = /
	divide = //
	remainder = %
	#You can combine to do 3 // 4 % 5
"""
#The function (def power is funtion ,(n is the number you want, m is the exponent) is parameters)
def power(n,m):
	print(f"{n} to the power of {m} = {n ** m}")
#put the function name plus (n) where n is the number you want squared
power(32,2)

#Lets define a function 1
def func_one(n):
	return n * 5

#Function 2 can pull data or call info from funtion 1
def func_two(m):
	return func_one(m) + 7

#This returns func_one to be 7 * 5 , then it activates it's function of adding 7
print(func_two(7))

#This allows us to detect if someone is shouting
def shout(phrase):
	if phrase == phrase.upper():
		print("YOU'RE SHOUTING!")
	else:
		print("Can you speak up")

shout("I'M INTERESTED IN SHOUTING")
print(f"12 divided by 4 = {12 // 4} remainder {12 % 4}")
print(sqrt(25))

#Built-in Funtions
#String
x = "Lol"
#Numbers
z = 1,2,3
#Negative
y = -5
#Returns in caps
a = x.upper()
#Makes everything lowercase
b = x.lower()
#Makes it a string if it is an int or tuple
c = str(x)
#Returns letter count
d = len(x)
#Returns type, example : String, Int, tuple
e = type(x)
#Returns the maximum value of the numbers
f = max(z)
#Returns the minimum value of the numbers
g = min(z)
#Returns the absolute Value
h = abs(y)
print(a,b,c,d,e,f,g,h)

