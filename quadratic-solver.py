import cmath
import matplotlib.pyplot as plt
import numpy as np

#a = float(input("Input leading co-efficient: "))
#b = float(input("Input linear co-efficient: "))
#c = float(input("Input constant term: "))

a = 1
b = 1
c = 1

d = b**2-(4*a*c)

if d < 0:
    print("Complex solutions found")
else:
    print("Real solutions found")

x1 = (-b+cmath.sqrt(d))/(2*a)
x2 = (-b-cmath.sqrt(d))/(2*a)
print("Solutions are x1 = ", x1, " and x2 = ", x2)

# generate domain on graph based on roots +- 5
if x1.real < x2.real:
    x = np.linspace(x1-5,x2+5,100)
else:
    x = np.linspace(x2-5,x1+5,100)

# graph standard form quadratic
y = a*x**2+b*x+c

# setting the axes at the centre
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.spines['left'].set_position('center')
ax.spines['bottom'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

# plot the function with title
title = 'Graph of f(x) = ' + str(a) + 'x^2 + ' + str(b) + 'x + ' + str(c)
plt.title(title)
plt.plot(x,y, 'r')

# show the plot
plt.show()
