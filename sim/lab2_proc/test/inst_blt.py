#=========================================================================
# blt
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_very_basic_test
#-------------------------------------------------------------------------
# The very basic test uses ADDU which is implemented in the initial
# baseline processor to do a very simple test. This approach requires
# using the test source to get an immediate, which is why we use ADDIU in
# all other control flow tests. We wanted at least one test that works on
# the initial baseline processor.

def gen_very_basic_test():
  return """

    # Use x3 to track the control flow pattern
    csrr  x3, mngr2proc < 0
    csrr  r4, mngr2proc < 1

    csrr  x1, mngr2proc < 1
    csrr  x2, mngr2proc < 2

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    # This branch should be taken
    blt   x1, x2, label_a
    addu  x3, x3, r4

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    addu  x3, x3, r4

    # One and only one of the above two addu instructinos should have
    # been executed which means the result should be exactly one.
    csrw  proc2mngr, x3 > 1

  """

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------
# This test uses addiu to track the control flow for testing purposes.
# This means this test cannot work on the initial baseline processor
# which only implements CSRR, MTC0, ADDU, LW, and BNE. That is why we
# included the above test so we have at least one test that should pass
# on the initial baseline processor for the BNE instruction.

def gen_basic_test():
  return """

    # Use x3 to track the control flow pattern
    addi  x3, x0, 0

    csrr  x1, mngr2proc < 1
    csrr  x2, mngr2proc < 2

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

    # This branch should be taken
    blt   x1, x2, label_a
    addi  x3, x3, 0b01

    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop

  label_a:
    addi  x3, x3, 0b10

    # Only the second bit should be set if branch was taken
    csrw  proc2mngr, x3 > 0b10

  """

#-------------------------------------------------------------------------
# gen_src0_dep_taken_test
#-------------------------------------------------------------------------

def gen_src0_dep_taken_test():
  return [
    gen_br2_src0_dep_test( 5, "blt", 1, 7, True ),
    gen_br2_src0_dep_test( 4, "blt", 2, 7, True ),
    gen_br2_src0_dep_test( 3, "blt", 3, 7, True ),
    gen_br2_src0_dep_test( 2, "blt", 4, 7, True ),
    gen_br2_src0_dep_test( 1, "blt", 5, 7, True ),
    gen_br2_src0_dep_test( 0, "blt", 6, 7, True ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_src0_dep_nottaken_test():
  return [
    gen_br2_src0_dep_test( 5, "blt", 15, 1, False ),
    gen_br2_src0_dep_test( 4, "blt", 14, 2, False ),
    gen_br2_src0_dep_test( 3, "blt", 13, 3, False ),
    gen_br2_src0_dep_test( 2, "blt", 12, 4, False ),
    gen_br2_src0_dep_test( 1, "blt", 11, 5, False ),
    gen_br2_src0_dep_test( 0, "blt", 10, 6, False ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_taken_test
#-------------------------------------------------------------------------

def gen_src1_dep_taken_test():
  return [
    gen_br2_src1_dep_test( 5, "blt", 7, 10, True ),
    gen_br2_src1_dep_test( 4, "blt", 7, 11, True ),
    gen_br2_src1_dep_test( 3, "blt", 7, 12, True ),
    gen_br2_src1_dep_test( 2, "blt", 7, 13, True ),
    gen_br2_src1_dep_test( 1, "blt", 7, 14, True ),
    gen_br2_src1_dep_test( 0, "blt", 7, 15, True ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_src1_dep_nottaken_test():
  return [
    gen_br2_src1_dep_test( 5, "blt", 1, 1, False ),
    gen_br2_src1_dep_test( 4, "blt", 2, 2, False ),
    gen_br2_src1_dep_test( 3, "blt", 3, 3, False ),
    gen_br2_src1_dep_test( 2, "blt", 4, 4, False ),
    gen_br2_src1_dep_test( 1, "blt", 5, 5, False ),
    gen_br2_src1_dep_test( 0, "blt", 6, 6, False ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_taken_test
#-------------------------------------------------------------------------

def gen_srcs_dep_taken_test():
  return [
    gen_br2_srcs_dep_test( 5, "blt", 1, 2, True ),
    gen_br2_srcs_dep_test( 4, "blt", 2, 3, True ),
    gen_br2_srcs_dep_test( 3, "blt", 3, 4, True ),
    gen_br2_srcs_dep_test( 2, "blt", 4, 5, True ),
    gen_br2_srcs_dep_test( 1, "blt", 5, 6, True ),
    gen_br2_srcs_dep_test( 0, "blt", 6, 7, True ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_srcs_dep_nottaken_test():
  return [
    gen_br2_srcs_dep_test( 5, "blt", 2, 1, False ),
    gen_br2_srcs_dep_test( 4, "blt", 3, 2, False ),
    gen_br2_srcs_dep_test( 3, "blt", 4, 3, False ),
    gen_br2_srcs_dep_test( 2, "blt", 5, 4, False ),
    gen_br2_srcs_dep_test( 1, "blt", 6, 5, False ),
    gen_br2_srcs_dep_test( 0, "blt", 7, 6, False ),
  ]

#-------------------------------------------------------------------------
# gen_src0_eq_src1_nottaken_test
#-------------------------------------------------------------------------

def gen_src0_eq_src1_test():
  return [
    gen_br2_src0_eq_src1_test( "blt", 1, False ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_br2_value_test( "blt", -1, -1, False ),
    gen_br2_value_test( "blt", -1,  0, True  ),
    gen_br2_value_test( "blt", -1,  1, True  ),

    gen_br2_value_test( "blt",  0, -1, False  ),
    gen_br2_value_test( "blt",  0,  0, False ),
    gen_br2_value_test( "blt",  0,  1, True  ),

    gen_br2_value_test( "blt", -1,  1, True  ),
    gen_br2_value_test( "blt", -1,  0, True  ),
    gen_br2_value_test( "blt",  1,  0, False ),

    gen_br2_value_test( "blt", 0xfffffff7, 0xfffffff7, False ),
    gen_br2_value_test( "blt", 0x7fffffff, 0x7fffffff, False ),
    gen_br2_value_test( "blt", 0xfffffff7, 0x7fffffff, True ),
    gen_br2_value_test( "blt", 0x7fffffff, 0xfffffff7, False ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def signed_comp(a,b):
  if (a==b):
    return 0;
  n = a.nbits
  if a[n-1] == 0: 
    if b[n-1] == 1:
      return 1
    else:
      if (a<b):
        return -1
      else:
        return 1
  else:
    if b[n-1] == 0:
      return -1
    else: 
      if (a<b):
        return -1
      else:
        return 1


def gen_random_test():
  n = 0  
  asm_code = []
  for i in xrange(25):
    taken = random.choice([True, False])
    src0  = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    print(src0, src1, taken, signed_comp(src0, src1))
    if taken:
      if (signed_comp(src0, src1) == 1)or(signed_comp(src0, src1) == 0):
        src1 = src0 + 1
    else:
      if (signed_comp(src0, src1) == -1):
        src0 = src1 + 1
    n = n + 1
    print("pretest", n, src0, src1, taken)
    print("")
    asm_code.append( gen_br2_value_test( "blt", src0.uint(), src1.uint(), taken ) )
  return asm_code

