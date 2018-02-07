#=========================================================================
# sll
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x80008000
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sll x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00040000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [
    gen_rr_dest_dep_test( 5, "sll", 5, 2, 20 ),
    gen_rr_dest_dep_test( 4, "sll", 7, 1, 14 ),
    gen_rr_dest_dep_test( 3, "sll", 9, 2, 36 ),
    gen_rr_dest_dep_test( 2, "sll", 8, 5, 256 ),
    gen_rr_dest_dep_test( 1, "sll", 2, 1, 4 ),
    gen_rr_dest_dep_test( 0, "sll", 3, 1, 6 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sll",  4,  3, 32 ),
    gen_rr_src0_dep_test( 4, "sll",  11, 2, 44 ),
    gen_rr_src0_dep_test( 3, "sll",  13, 2, 52 ),
    gen_rr_src0_dep_test( 2, "sll",  16, 2, 64 ),
    gen_rr_src0_dep_test( 1, "sll",  15, 1, 30 ),
    gen_rr_src0_dep_test( 0, "sll",  19, 1, 38 ),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sll",  21, 4, 336 ),
    gen_rr_src1_dep_test( 4, "sll",  32, 4, 512 ),
    gen_rr_src1_dep_test( 3, "sll",  150,500, 0 ),
    gen_rr_src1_dep_test( 2, "sll",  231, 4, 3696 ),
    gen_rr_src1_dep_test( 1, "sll",  4, 18, 1048576 ),
    gen_rr_src1_dep_test( 0, "sll",  200, 6, 12800),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sll",  9, 3, 72 ),
    gen_rr_srcs_dep_test( 4, "sll",  8, 5, 256 ),
    gen_rr_srcs_dep_test( 3, "sll",  35, 1, 70 ),
    gen_rr_srcs_dep_test( 2, "sll",  500, 4, 8000 ),
    gen_rr_srcs_dep_test( 1, "sll",  330, 5, 10560 ),
    gen_rr_srcs_dep_test( 0, "sll",  720, 3, 5760 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sll", 25, 1, 50 ),
    gen_rr_src1_eq_dest_test( "sll", 260, 1, 520 ),
    gen_rr_src0_eq_src1_test( "sll", 27, 3623878656 ),
    gen_rr_srcs_eq_dest_test( "sll", 1, 2 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sll", 0x00000000, 0x00000003, 0x00000000 ),
    gen_rr_value_test( "sll", 0x00000005, 0x00000001, 0x0000000a ),
    gen_rr_value_test( "sll", 0x00000008, 0x00000002, 0x00000020 ),

    gen_rr_value_test( "sll", 0xffff8000, 0x00000004, 0xfff80000 ),
    gen_rr_value_test( "sll", 0x80000000, 0x0000000a, 0x00000000 ),
    gen_rr_value_test( "sll", 0x80000000, 0x00000032, 0x00000000 ),

    gen_rr_value_test( "sll", 0xffffffff, 0x00000001, 0xfffffffe ),
    gen_rr_value_test( "sll", 0x7fffffff, 0x00000040, 0x00000000 ),
    gen_rr_value_test( "sll", 0x7fffffff, 0x0000000a, 0xfffffc00 ),

    gen_rr_value_test( "sll", 0x00007fff, 0x00000003, 0x0003fff8 ),
    gen_rr_value_test( "sll", 0x7fffffff, 0x0000001e, 0xc0000000 ),

    gen_rr_value_test( "sll", 0x000003e8, 0x00000004, 0x00003e80 ),
    gen_rr_value_test( "sll", 0xffffffff, 0x00000002, 0xfffffffc ),
    gen_rr_value_test( "sll", 0xffffffff, 0x0000001f, 0x80000000 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    dest = src0 << src1
    asm_code.append( gen_rr_value_test( "sll", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code
''''''''''''''''''''''''''''''''''''
