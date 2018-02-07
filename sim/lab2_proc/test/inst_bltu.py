#=========================================================================
# bltu
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
    bltu   x1, x2, label_a
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
    bltu   x1, x2, label_a
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
    gen_br2_src0_dep_test( 5, "bltu", 1, 7,  True ),
    gen_br2_src0_dep_test( 4, "bltu", 2, 7,  True ),
    gen_br2_src0_dep_test( 3, "bltu", 3, 7,  True ),
    gen_br2_src0_dep_test( 2, "bltu", 12,-4, True ),
    gen_br2_src0_dep_test( 1, "bltu", 11,-5, True ),
    gen_br2_src0_dep_test( 0, "bltu", 10,-6, True ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_src0_dep_nottaken_test():
  return [
    gen_br2_src0_dep_test( 5, "bltu", 15, 1, False ),
    gen_br2_src0_dep_test( 4, "bltu", 14, 2, False ),
    gen_br2_src0_dep_test( 3, "bltu", 13, 3, False ),
    gen_br2_src0_dep_test( 2, "bltu", -4, 7, False ),
    gen_br2_src0_dep_test( 1, "bltu", -5, 7, False ),
    gen_br2_src0_dep_test( 0, "bltu", -6, 7, False ),    
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_taken_test
#-------------------------------------------------------------------------

def gen_src1_dep_taken_test():
  return [
    gen_br2_src1_dep_test( 5, "bltu", 7, 10, True ),
    gen_br2_src1_dep_test( 4, "bltu", 7, 11, True ),
    gen_br2_src1_dep_test( 3, "bltu", 7, 12, True ),
    gen_br2_src1_dep_test( 2, "bltu", 7,-13, True ),
    gen_br2_src1_dep_test( 1, "bltu", 7,-14, True ),
    gen_br2_src1_dep_test( 0, "bltu", 7,-15, True ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_src1_dep_nottaken_test():
  return [
    gen_br2_src1_dep_test( 5, "bltu",-1, 1, False ),
    gen_br2_src1_dep_test( 4, "bltu",-2, 2, False ),
    gen_br2_src1_dep_test( 3, "bltu",-3, 3, False ),
    gen_br2_src1_dep_test( 2, "bltu", 4, 4, False ),
    gen_br2_src1_dep_test( 1, "bltu", 5, 5, False ),
    gen_br2_src1_dep_test( 0, "bltu", 6, 6, False ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_taken_test
#-------------------------------------------------------------------------

def gen_srcs_dep_taken_test():
  return [
    gen_br2_srcs_dep_test( 5, "bltu", 1, 2, True ),
    gen_br2_srcs_dep_test( 4, "bltu", 2, 3, True ),
    gen_br2_srcs_dep_test( 3, "bltu", 3, 4, True ),
    gen_br2_srcs_dep_test( 2, "bltu", 4,-5, True ),
    gen_br2_srcs_dep_test( 1, "bltu", 5,-6, True ),
    gen_br2_srcs_dep_test( 0, "bltu", 6,-7, True ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_nottaken_test
#-------------------------------------------------------------------------

def gen_srcs_dep_nottaken_test():
  return [
    gen_br2_srcs_dep_test( 5, "bltu", 2, 1, False ),
    gen_br2_srcs_dep_test( 4, "bltu", 3, 2, False ),
    gen_br2_srcs_dep_test( 3, "bltu", 4, 3, False ),
    gen_br2_srcs_dep_test( 2, "bltu",-5, 4, False ),
    gen_br2_srcs_dep_test( 1, "bltu",-6, 5, False ),
    gen_br2_srcs_dep_test( 0, "bltu",-7, 6, False ),
  ]

#-------------------------------------------------------------------------
# gen_src0_eq_src1_nottaken_test
#-------------------------------------------------------------------------

def gen_src0_eq_src1_test():
  return [
    gen_br2_src0_eq_src1_test( "bltu", 1, False ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_br2_value_test( "bltu", -1, -1, False ),
    gen_br2_value_test( "bltu", -1,  0, False  ),
    gen_br2_value_test( "bltu", -1,  1, False  ),

    gen_br2_value_test( "bltu",  0, -1, True  ),
    gen_br2_value_test( "bltu",  0,  0, False ),
    gen_br2_value_test( "bltu",  0,  1, True  ),

    gen_br2_value_test( "bltu",  1, -1, True  ),
    gen_br2_value_test( "bltu",  1,  0, False  ),
    gen_br2_value_test( "bltu",  1,  1, False ),

    gen_br2_value_test( "bltu", 0xfffffff7, 0xfffffff7, False ),
    gen_br2_value_test( "bltu", 0x7fffffff, 0x7fffffff, False ),
    gen_br2_value_test( "bltu", 0xfffffff7, 0x7fffffff, False ),
    gen_br2_value_test( "bltu", 0x7fffffff, 0xfffffff7, True  ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(25):
    taken = random.choice([True, False])
    src0  = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    if taken:
      if src0 >= src1:
        src1 = src0 + 1
    else:
      if src0 < src1:
        src0 = src1 + 1
    asm_code.append( gen_br2_value_test( "bltu", src0.uint(), src1.uint(), taken ) )
  return asm_code

