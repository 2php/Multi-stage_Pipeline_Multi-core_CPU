#=========================================================================
# addii
#=========================================================================

import random

from pymtl                import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    csrr x1, mngr2proc, < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    addi x3, x1, 0x004
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 9
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
    gen_rimm_dest_dep_test( 5, "addi", 1, 0x001, 2 ),
    gen_rimm_dest_dep_test( 4, "addi", 2, 0x001, 3 ),
    gen_rimm_dest_dep_test( 3, "addi", 3 ,0x001, 4 ),
    gen_rimm_dest_dep_test( 2, "addi", 4, 0x001, 5 ),
    gen_rimm_dest_dep_test( 1, "addi", 5, 0x001, 6 ),
    gen_rimm_dest_dep_test( 0, "addi", 6, 0x001, 7 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "addi", 10, 0x002, 12 ),
    gen_rimm_src_dep_test( 4, "addi", 10, 0x003, 13 ),
    gen_rimm_src_dep_test( 3, "addi", 10, 0x004, 14 ),
    gen_rimm_src_dep_test( 2, "addi", 10, 0x005, 15 ),
    gen_rimm_src_dep_test( 1, "addi", 10, 0x006, 16 ),
    gen_rimm_src_dep_test( 0, "addi", 10, 0x007, 17 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "addi", 25, 1, 26 ),
    gen_rimm_src_eq_dest_test( "addi", 26, 1, 27 ),
  ]


def gen_value_test():
  return [

    gen_rimm_value_test( "addi", 0x00000000, 0x000, 0x00000000 ),
    gen_rimm_value_test( "addi", 0x00000001, 0x001, 0x00000002 ),
    gen_rimm_value_test( "addi", 0x00000003, 0x007, 0x0000000a ),

    gen_rimm_value_test( "addi", 0x00000000, 0x0ff, 0x000000ff ),
    gen_rimm_value_test( "addi", 0xffffffff, 0x002, 0x00000001 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 12, random.randint(0,0x7ff) )
    dest = src0 + src1
    asm_code.append( gen_rimm_value_test( "addi", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code

