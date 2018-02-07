#=========================================================================
# slli
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
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slli x3, x1, 0x03
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
    gen_rimm_dest_dep_test( 5, "slli", 5, 0x002, 20 ),
    gen_rimm_dest_dep_test( 4, "slli", 7, 0x001, 14 ),
    gen_rimm_dest_dep_test( 3, "slli", 9, 0x002, 36 ),
    gen_rimm_dest_dep_test( 2, "slli", 8, 0x005, 256 ),
    gen_rimm_dest_dep_test( 1, "slli", 2, 0x001, 4 ),
    gen_rimm_dest_dep_test( 0, "slli", 3, 0x001, 6 ),
  ]

#-------------------------------------------------------------------------
# gen_src0_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "slli",  0x004, 3, 32 ),
    gen_rimm_src_dep_test( 4, "slli",  0x00b, 2, 44 ),
    gen_rimm_src_dep_test( 3, "slli",  0x00d, 2, 52 ),
    gen_rimm_src_dep_test( 2, "slli",  0x010, 2, 64 ),
    gen_rimm_src_dep_test( 1, "slli",  0x00f, 1, 30 ),
    gen_rimm_src_dep_test( 0, "slli",  0x013, 1, 38 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "slli", 25, 0x001, 50 ),
    gen_rimm_src_eq_dest_test( "slli", 260, 0x001, 520 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [

    gen_rimm_value_test( "slli", 0x00000000, 0x003, 0x00000000 ),
    gen_rimm_value_test( "slli", 0x00000005, 0x001, 0x0000000a ),
    gen_rimm_value_test( "slli", 0x00000008, 0x002, 0x00000020 ),

    gen_rimm_value_test( "slli", 0xffff8000, 0x004, 0xfff80000 ),
    gen_rimm_value_test( "slli", 0x80000000, 0x00a, 0x00000000 ),
    gen_rimm_value_test( "slli", 0x80000000, 0x010, 0x00000000 ),

    gen_rimm_value_test( "slli", 0xffffffff, 0x001, 0xfffffffe ),
    gen_rimm_value_test( "slli", 0x7fffffff, 0x014, 0xfff00000 ),
    gen_rimm_value_test( "slli", 0x7fffffff, 0x00a, 0xfffffc00 ),

    gen_rimm_value_test( "slli", 0x00007fff, 0x003, 0x0003fff8 ),
    gen_rimm_value_test( "slli", 0x7fffffff, 0x01e, 0xc0000000 ),

    gen_rimm_value_test( "slli", 0x000003e8, 0x004, 0x00003e80 ),
    gen_rimm_value_test( "slli", 0xffffffff, 0x002, 0xfffffffc ),
    gen_rimm_value_test( "slli", 0xffffffff, 0x01f, 0x80000000 ),

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    src1 = Bits( 12, random.randint(0,0x01f) )
    dest = src0 << src1
    asm_code.append( gen_rimm_value_test( "slli", src0.uint(), src1.uint(), dest.uint() ) )
  return asm_code
''''''''''''''''''''''''''''''''''''
