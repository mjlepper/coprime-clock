# coprime-clock
Utility for calculating clock gear trains using coprime pairs

This utility is inteded to find coprime pairs of numbers that may be
used as a gear train to acheive a desired ratio.

Two common gear train ratios for clocks are 60:1 for the
seconds:minutes relationship, and 12:1 for the minutes:hours
relationship.  When attempting to fit both these reductions onto two
shafts, and maintain a single module throughout the gear train, the
allowed values may be readily determined.

For example the 12:1 relationship is factored into 4:1 and 3:1 reductions:

    m1 = 4   m2 = 3
(1) --   -,  --   _
    n1 = 1   n2 = 1

To construct the gears using the same module:

(2) m1 + n1 = m2 + n2

From (1), write m1 and m2 in terms of n1 and n2:

(3) m1 = 4 * n1, m2 = 3 * n2

Substituting m1 and m2 from (3) into (2):

(4) 4 * n1 + n1 = 3 * n2 + n2
(5) 5 * n1 = 4 * n2

For n1 & n2, (5) is equal to the LCM of the coefficients of each term:

(6) LCM(4,5) = 20

So n1 & n2 can be determined:

(7) n1 = 4, n2 = 5

And m1 and m2 can be determined:

(8) m1 = 16, m2 = 15

From here, all the terms m1, n1, m2, n2 may be multipled by any
integer to fit the dimensions and technology be used.

This algorithm may be extended to additional gear pairs, for example
if a 60:1 reduction is desired in addition to 12:1, gears of either:
(10:1, 6:1), (12:1, 5:1), (15:1, 4:1) might be considered.

R1   R2   R3   R4   LCM  G1       G2       G3       G4
3:1  4:1  6:1  10:1 1540 1155:385 1232:308 1320:220 1400:140
3:1  4:1  5:1  12:1  780  585:195  624:156  650:130  720: 60
3:1  4:1  4:1  15:1   80   60: 20   64: 16   64: 16   75:  5

This last set is clearly superior in terms of minimum tooth counts;
however, the large 15:1 reduction increases the overall size of the
gear train.  The most compact gear train would occur when each pair of
gears provides and equal amount of reduction, which for a gear train
of 's' stages overall ratio 'r', is simply the 's'th root of 'r'.
Since this is frequently an irrational number, careful selection of
gear ratios may be used to balance the overall ratio, while keeping
the individual gear ratios close to the irrational target.

In powertrain gearing, when possible individual gear sets are choosen
to have coprime tooth counts.  A set of numbers are coprime when the
greatest common divisor (GCD) of all the numbers is 1.  A coprime
relationship between two gears ensures all teeth of each gear
eventually touch, the intent being to even out wear across the teeth.

The goal is to find compact gear sets that use coprime relationships
and provide the required overall ratio.

One strategy is to start with a simple factorization of the desired ratio:

    3   4   12
(9) - * - = --
    1   1    1

and then choose two prime numbers such as 13 and 17, and augment (9) as:

     17   3   13   4   12
(10) -- * - * -- * - = --
     13   1   17   1    1

and then:

     51   52   12
(11) -- * -- = --
     13   17    1

This also slightly reduces the size of the gear train, since 51/13 <
4/1 and 52/17 > 3/1.  This may be continued until a desireable set of
gears is found.

Based upon space available and tooling technology, the designer can
place a reasonable upper bound on the sum of the largest and smallest
gears of each gear pair (mn_max), and the smallest pinion desired
(n_min).  With these bounds, the search algorithm is:

0) Find r_target = s'th root of r
1) Find all coprime pairs (m,n) where m+n <= mn_max
2) Filter coprime pair list for all pairs where n >= n_min
3) Score each pair by the magnitude of the geometric error from r_target (*)
4) Sort the scored list in increasing order of geometric error
5) Iterate through all 's' combinations from the scored list, starting
   with combinations closest to r_target (**)
6) For each combination, calculated the overall gear ratio, only
   accept combinations exactly matching 'r'

(*) Geometric error is defined as max((m/n)/r_target,r_target/(m/n).
    As an example, if r_target = 4, m/n = 2 and m/n = 8 both have a
    geometric error of 2.0

(**) The normal order lexicographical order of a list ABCDE choosing 2
     values is: AB AC AD AE BC BD BE CD CE DE, we desire an order: AB
     AC BC AD BD CD AE BE CE DE

Example output:
$ ./coprime.py --ratio 12 --stages 2 --mn_max 200 --n_min 13 -d
# r_target=3.464102
# m=12: [2, 2, 3]
# n=1: [1]
# testing 4711 out of 6115 coprimes
# ./coprime.py --ratio 12 --stages 2 --mn_max 200 --n_min 13 -d
r_dev, m_dev, m1, n1, m2, n2
# Testing 11094405 combinations
1.000740, 9, 52, 15, 45, 13
1.001342, 22, 111, 32, 128, 37
1.004087, 14, 80, 23, 69, 20
1.004589, 17, 87, 25, 100, 29
...

All lines starting with '#' are informational, the remaining lines are
intended to be used as a .csv file to be read into a spreadsheet.

--ratio may be a single integer or a ratio separated by ':'
--stages are pairs in the gear train
--mn_max is the largest m+n value to search through
--n_min is the smallest n value to consider

For this example, mn_max was calculated assuming a shaft center
distance of 50 mm and a minimum module of 0.5.  n_min was choosen as
13, though the targeted gear tooth profile may warrant increasing or
decreasing this value.  The first two values on each line are 'r_dev':
the largest geometric error from r_target for all the pairs in the
set; and 'm_dev': the difference between the largest and smallest m+n
values for all the pairs in the set.  Producing a scatter plot of
r_dev and m_dev may provide insight of the best choice for a
particular application.

The program will continue searching through all combinations.  Since
later results will always have a larger r_dev value, these are likely
to be less appealing.  If the '-d' option has been specified, a status
update will be printed every minute with a % completion value, and an
estimated time for completion.  For particularly large searches, the
time required to search through all combinations may need to be
described on geologic or astronomic time scales.  In these cases, it
is best to kill the program after a reasonable number of results have
been found.  If no results are found within 10 minutes, it may be
necessary to increase mn_max.  If (mn_max-n_min)/n_min is only
slightly greater than r_target, there may not be a solution.

The m= and n= lines are printed when the '-d' option is specified.
These are the reduced numerator and denominator of the '--ratio'
argument, along with the prime factorization of these numbers.
