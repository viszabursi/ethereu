from opcodes import SGT, SLT, ADD, XOR
from rule import Rule
from util import BVSignedMax, BVSignedMin, BVSignedUpCast
from z3 import BitVec, BVAddNoOverflow, BVAddNoUnderflow, Not, Or

"""
Overflow checked signed integer addition.
"""

n_bits = 256
type_bits = 8

while type_bits <= n_bits:

	rule = Rule()

	# Input vars
	X_short = BitVec('X', type_bits)
	Y_short = BitVec('Y', type_bits)

	# Z3's overflow and underflow conditions
	actual_overflow = Not(BVAddNoOverflow(X_short, Y_short, True))
	actual_underflow = Not(BVAddNoUnderflow(X_short, Y_short))

	# cast to full n_bits values
	X = BVSignedUpCast(X_short, n_bits)
	Y = BVSignedUpCast(Y_short, n_bits)
	sum_ = ADD(X, Y)

	# Constants
	maxValue = BVSignedMax(type_bits, n_bits)
	minValue = BVSignedMin(type_bits, n_bits)

	# Overflow and underflow checks in YulUtilFunction::overflowCheckedIntAddFunction
	if type_bits == 256:
		actual_overflow_or_underflow = Or(actual_overflow, actual_underflow)

		overflow_or_underflow_check = XOR(SLT(X, 0), SLT(sum_, Y))

		rule.check(actual_overflow_or_underflow,
				   overflow_or_underflow_check != 0)
	else:
		overflow_check = SGT(sum_, maxValue)
		underflow_check = SLT(sum_, minValue)

		rule.check(actual_overflow, overflow_check != 0)
		rule.check(actual_underflow, underflow_check != 0)

	type_bits += 8
