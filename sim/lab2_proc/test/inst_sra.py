#=========================================================================
# sra
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x00008000
    csrr x2, mngr2proc < 0x00000003
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sra x3, x1, x2
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 0x00001000
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
    gen_rr_dest_dep_test( 5, "sra", 5, 2, 1 ),
    gen_rr_dest_dep_test( 4, "sra", 7, 1, 3 ),
    gen_rr_dest_dep_test( 3, "sra", 9, 2, 2 ),
    gen_rr_dest_dep_test( 2, "sra", 8, 5, 0 ),
    gen_rr_dest_dep_test( 1, "sra", 2, 1, 1 ),
    gen_rr_dest_dep_test( 0, "sra", 3, 1, 1 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src0_dep_test():
  return [
    gen_rr_src0_dep_test( 5, "sra",  4,  3, 0 ),
    gen_rr_src0_dep_test( 4, "sra",  11, 2, 2 ),
    gen_rr_src0_dep_test( 3, "sra",  13, 2, 3 ),
    gen_rr_src0_dep_test( 2, "sra",  16, 2, 4 ),
    gen_rr_src0_dep_test( 1, "sra",  15, 1, 7 ),
    gen_rr_src0_dep_test( 0, "sra",  19, 1, 9),
  ]

#-------------------------------------------------------------------------
# gen_src1_dep_test
#-------------------------------------------------------------------------

def gen_src1_dep_test():
  return [
    gen_rr_src1_dep_test( 5, "sra",  21, 4, 1 ),
    gen_rr_src1_dep_test( 4, "sra",  32, 4, 2 ),
    gen_rr_src1_dep_test( 3, "sra",  150, 500, 0 ),
    gen_rr_src1_dep_test( 2, "sra",  231, 4, 14 ),
    gen_rr_src1_dep_test( 1, "sra",  4, 18, 0 ),
    gen_rr_src1_dep_test( 0, "sra",  200, 6, 3 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [
    gen_rr_srcs_dep_test( 5, "sra",  9, 3, 1 ),
    gen_rr_srcs_dep_test( 4, "sra",  8, 5, 0 ),
    gen_rr_srcs_dep_test( 3, "sra",  35, 1, 17 ),
    gen_rr_srcs_dep_test( 2, "sra",  500, 4, 31 ),
    gen_rr_srcs_dep_test( 1, "sra",  330, 5, 10 ),
    gen_rr_srcs_dep_test( 0, "sra",  720, 3, 90 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rr_src0_eq_dest_test( "sra", 25, 1, 12 ),
    gen_rr_src1_eq_dest_test( "sra", 260, 1, 130 ),
    gen_rr_src0_eq_src1_test( "sra", 27, 0 ),
    gen_rr_srcs_eq_dest_test( "sra", 1, 0 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rr_value_test( "sra", 0x00000000, 0x00000003, 0x00000000 ),
    gen_rr_value_test( "sra", 0x00000005, 0x00000001, 0x00000002 ),
    gen_rr_value_test( "sra", 0x00000008, 0x00000002, 0x00000002 ),

    gen_rr_value_test( "sra", 0xffff8000, 0x00000004, 0xfffff800 ),
    gen_rr_value_test( "sra", 0x80000000, 0x0000000a, 0xffe00000 ),
    gen_rr_value_test( "sra", 0x80000000, 0x00000032, 0xffffffff ),

    gen_rr_value_test( "sra", 0xffffffff, 0x00000001, 0xffffffff ),
    gen_rr_value_test( "sra", 0x7fffffff, 0x00000040, 0x00000000 ),
    gen_rr_value_test( "sra", 0x7fffffff, 0x0000000a, 0x001fffff ),

    gen_rr_value_test( "sra", 0x00007fff, 0x00000003, 0x00000fff ),
    gen_rr_value_test( "sra", 0x7fffffff, 0x0000001e, 0x00000001 ),

    gen_rr_value_test( "sra", 0x000003e8, 0x00000004, 0x0000003e ),
    gen_rr_value_test( "sra", 0xffffffff, 0x00000002, 0xffffffff ),
    gen_rr_value_test( "sra", 0xffffffff, 0x0000001f, 0xffffffff ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def arith_shift(A, B):
  if (A[A.nbits-1] == 0):
    return A>>B
  else :
    for i in range(B.uint()):
        A = concat(Bits(1, 1), (A>>1)[0:30])
  print(A)
  return A

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 32, random.randint(0,0xffffffff) )
    print(src0, src1)
    dest = arith_shift (src0, src1) 
    print("")
    asm_code.append( gen_rr_value_test( "sra", src0.uint(), src1.uint(), dest.uint() ) )
    return asm_code
''''''''''''''''''''''''''''''''''''
