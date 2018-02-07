#=========================================================================
# srai
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
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    srai x3, x1, 0x03
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
    gen_rimm_dest_dep_test( 5, "srai", 5, 0x002, 1 ),
    gen_rimm_dest_dep_test( 4, "srai", 7, 0x001, 3 ),
    gen_rimm_dest_dep_test( 3, "srai", 9, 0x002, 2 ),
    gen_rimm_dest_dep_test( 2, "srai", 8, 0x005, 0 ),
    gen_rimm_dest_dep_test( 1, "srai", 2, 0x001, 1 ),
    gen_rimm_dest_dep_test( 0, "srai", 3, 0x001, 1 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "srai",  4,  0x003, 0 ),
    gen_rimm_src_dep_test( 4, "srai",  11, 0x002, 2 ),
    gen_rimm_src_dep_test( 3, "srai",  13, 0x002, 3 ),
    gen_rimm_src_dep_test( 2, "srai",  16, 0x002, 4 ),
    gen_rimm_src_dep_test( 1, "srai",  15, 0x001, 7 ),
    gen_rimm_src_dep_test( 0, "srai",  19, 0x001, 9),
  ]


#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "srai", 25, 0x001, 12 ),
    gen_rimm_src_eq_dest_test( "srai", 260, 0x0001, 130 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rimm_value_test( "srai", 0x00000000, 0x003, 0x00000000 ),
    gen_rimm_value_test( "srai", 0x00000005, 0x001, 0x00000002 ),
    gen_rimm_value_test( "srai", 0x00000008, 0x002, 0x00000002 ),

    gen_rimm_value_test( "srai", 0xffff8000, 0x004, 0xfffff800 ),
    gen_rimm_value_test( "srai", 0x80000000, 0x00a, 0xffe00000 ),
    gen_rimm_value_test( "srai", 0x80000000, 0x010, 0xffff8000 ),

    gen_rimm_value_test( "srai", 0x00000000, 0x011, 0x00000000 ),
    gen_rimm_value_test( "srai", 0x7fffffff, 0x014, 0x000007ff ),
    gen_rimm_value_test( "srai", 0x7fffffff, 0x00a, 0x001fffff ),

    gen_rimm_value_test( "srai", 0x00007fff, 0x003, 0x00000fff ),
    gen_rimm_value_test( "srai", 0x7fffffff, 0x01e, 0x00000001 ),

    gen_rimm_value_test( "srai", 0x000003e8, 0x004, 0x0000003e ),
    gen_rimm_value_test( "srai", 0xffffffff, 0x002, 0xffffffff ),
    gen_rimm_value_test( "srai", 0xffffffff, 0x01f, 0xffffffff ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def arith_shift(A, B):
  if (A[A.nbits-1] == 0):
    return A>>B
  else :
    if (B.uint() > 32):
      return 0xffffffff
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