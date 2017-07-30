#!/usr/bin/python

import sys
import itertools
import getopt
import copy
from fractions import gcd
from math import exp,log,sqrt,ceil,factorial
from time import time, gmtime, strftime

# Don't print debug info by default
debug = 0

# Overall reduction ratio
ratio_m = 60
ratio_n = 1

# Number of gear sets
stages = 2

# Upper limit for m+n
mn_max = 200

# Minimum gear count
n_min = 7

# Include reversal of all coprime pairs in search
reverse = 0

def usage():
	print "-h,--help: This help information"
	print "-d,--debug: Print additional information"
	print "-r,--ratio: overall ratio:1 reduction ratio"
	print "-s,--stages: Number of stages"
	print "-m,--mn_max: Maximum m+n limit"
	print "-n,--n_min: Minimum n value"
	print "-v,--reverse: Include reverse ratios"

try:
	opts, args = getopt.getopt(sys.argv[1:], "hdrsmnv:", ["help", "debug", "ratio=", "stages=", "mn_max=", "n_min=", "reverse"])
except	getopt.GetoptError:
	usage()
	sys.exit(2)

for opt,arg in opts:
	if opt in ("-h", "--help"):
		usage()
		sys.exit()
	elif opt in ("-d", "--debug"):
		debug = 1
	elif opt in ("-r", "--ratio"):
		if arg.find(':') != -1:
			a, b = arg.split(':')
			ratio_m = int(a)
			ratio_n = int(b)
		else:
			ratio_m = int(arg)
			ratio_n = 1
	elif opt in ("-s", "--stages"):
		stages = int(arg)
	elif opt in ("-m", "--mn_max"):
		mn_max = int(arg)
	elif opt in ("-n", "--n_min"):
		n_min = int(arg)
	elif opt in ("-v", "--reverse"):
		reverse = 1
	else:
		print "Unrecognized argument: "+opt
		usage()
		sys.exit()

def combinations_x(iterable, r):
	if len(iterable) == r:
		yield(iterable)
	elif r == 1:
		for i in iterable:
			yield( i )
	else:
		for i in range(r-1, len(iterable)):
			for j in combinations_x( range( i ), r-1 ):
				if type(j) is int:
					l = [j]
				else:
					l = list(j)
				l.append(i)
				yield( tuple( iterable[k] for k in l ) )
		
# Derived constants
r_target = exp(log(1.0*ratio_m/ratio_n)/stages)
if debug:
	print "# r_target="+'{0:.6f}'.format(r_target)

# Normalize ratio
while gcd(ratio_m,ratio_n) > 1:
	g = gcd(ratio_m,ratio_n)
	ratio_m /= g
	ratio_n /= g
	
# Input sanity checks
if 1.0*(mn_max - n_min) / n_min < r_target:
	print "Maximum possible ratio: "+str(mn_max - n_min)+':'+str(n_min)+" is less than target ratio "+str(r_target)
	sys.exit(2)

# Find prime factors of ratio_m and ratio_n
# Create a list of primes that could be factors of ratio_m or ratio_n
plimit = max(sqrt(ratio_m),sqrt(ratio_n))
p_list = [2]
for p in range(2,int(ceil(plimit))):
	prime = 1
	for q in p_list:
		if p % q == 0:
			prime = 0
			break
	if prime:
		p_list.append(p)

m_factors = []
n_factors = []
mt = ratio_m
nt = ratio_n
for p in p_list:
	while mt % p == 0:
		mt /= p
		m_factors.append(p)
	while nt % p == 0:
		nt /= p
		n_factors.append(p)
if mt > 1: m_factors.append(mt)
if nt > 1: n_factors.append(nt)
if len(m_factors) == 0: m_factors.append(1)
if len(n_factors) == 0: n_factors.append(1)

if debug:
	print "# m="+str(ratio_m)+": "+str(m_factors)
	print "# n="+str(ratio_n)+": "+str(n_factors)

# Make sure largest prime can be implemented
if max(m_factors+n_factors) > mn_max - n_min:
	print "Unable to implement largest prime factor: "+str(max(m_factors+n_factors))
	sys.exit(2)

# Construct a list of coprime pairs that are m+n <= mn_max
q = [[2,1], [3,1]]
q1 = []
c_list = []

while len(q) + len(q1) > 0:
	if len(q) == 0:
		q = q1[:]
		q1 = []
	m,n = q.pop(0)
	if m+n > mn_max: continue
	c_list.append([m,n])
	q1.append([2*m-n,m])
	q1.append([2*m+n,m])
	q1.append([m+2*n,n])

# Create a list that satifies both the n_min conditon, 
# and is ranked by error from r_target
d_list = []
for i in c_list:
	if i[1] >= n_min:
		d_list.append([max(r_target/(1.0*i[0]/i[1]),(1.0*i[0]/i[1])/r_target), i])
if debug:
	print "# testing "+str(len(d_list))+" out of "+str(len(c_list))+" coprimes"

e_list = []
for i in sorted(d_list):
	e_list.append(i[1])
	if (reverse):
		e_list.append([i[1][1], i[1][0]])

# print CSV header
print "# "+" ".join(sys.argv)
print "r_dev, m_dev,",
for i in range(stages):
	if i == stages - 1:
		print "m"+str(i+1)+", n"+str(i+1)
	else:
		print "m"+str(i+1)+", n"+str(i+1)+",",

results = []
count = 0
final_count = factorial(len(e_list))/(factorial(stages)*factorial(len(e_list)-stages))

if debug:
	print "# Testing "+str(final_count)+" combinations"

start_time = int(time())
target_time = start_time + 60

for i in combinations_x(e_list,stages):
	count += 1
	if debug:
		cur_time = int(time())
		if cur_time >= target_time:
			completion_time = 1.0*(cur_time - start_time)/count*final_count - (cur_time - start_time)
			r_h = int(completion_time / 3600)
			r_m = int((completion_time - r_h * 3600) / 60)
			r_s = int(completion_time - r_h * 3600 - r_m * 60)
			target_time = cur_time + 60
			print "# "+str(100.0*count/final_count)+"% "+'{:02d}'.format(r_h)+':'+'{:02d}'.format(r_m)+':'+'{:02d}'.format(r_s)+' remaining'

	if 1:
		# Older GCD reduction from total products
		mt = 1
		nt = 1
		ratios = []
		for p in i:
			ratios.append(p)
			mt *= p[0]
			nt *= p[1]
		while gcd(mt,nt) > 1:
			g = gcd(mt,nt)
			mt /= g
			nt /= g
	else:
		# Newer GCD reduction
		ic = copy.deepcopy(i)
		for j in range(stages):
			for k in range(stages):
				if j == k: continue
				while gcd(ic[j][0],ic[k][1]) > 1:
					g = gcd(ic[j][0],ic[k][1])
					ic[j][0] /= g
					ic[k][1] /= g
		mt = 1
		nt = 1
		ratios = []
		for q in i:
			ratios.append(q)
		for p in ic:
			mt *= p[0]
			nt *= p[1]
			
	if mt == ratio_m and nt == ratio_n:
		m_max = 0
		m_min = mn_max
		r_dev = 0
		for q in ratios:
			m = q[0] + q[1]
			r = max(r_target/(1.0*q[0]/q[1]),(1.0*q[0]/q[1])/r_target)
			if m < m_min: m_min = m
			if m > m_max: m_max = m
			if r > r_dev: r_dev = r

		m_dev = m_max - m_min

		print '{0:.6f},'.format(r_dev),
		print str(m_dev)+',',

		for j in range(len(ratios)):
			if j == len(ratios) -1:
				print str(ratios[j][0])+', '+str(ratios[j][1])
			else:
				print str(ratios[j][0])+', '+str(ratios[j][1])+',',
