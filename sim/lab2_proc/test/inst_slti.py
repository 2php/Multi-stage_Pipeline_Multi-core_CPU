#=========================================================================
# slti
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 5
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    slti x3, x1, 6
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x3 > 1
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
    gen_rimm_dest_dep_test( 5, "slti", 0x00000f0f, 0x0ff, 0x00000000 ),
    gen_rimm_dest_dep_test( 4, "slti", 0x0000f0f0, 0xff0, 0x00000000 ),
    gen_rimm_dest_dep_test( 3, "slti", 0x00000f0f, 0xf00, 0x00000000 ),
    gen_rimm_dest_dep_test( 2, "slti", 0x0000f0f0, 0x00f, 0x00000000 ),
    gen_rimm_dest_dep_test( 1, "slti", 0x00000f0f, 0xfff, 0x00000000 ),
    gen_rimm_dest_dep_test( 0, "slti", 0x0000f0f0, 0x0f0, 0x00000000 ),
  ]

#-------------------------------------------------------------------------
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [
    gen_rimm_src_dep_test( 5, "slti", 0x0000000f, 0x0ff, 0x00000001 ),
    gen_rimm_src_dep_test( 4, "slti", 0x000000f0, 0xff0, 0x00000000 ),
    gen_rimm_src_dep_test( 3, "slti", 0x0000000f, 0xf00, 0x00000000 ),
    gen_rimm_src_dep_test( 2, "slti", 0x0000000e, 0x00f, 0x00000001 ),
    gen_rimm_src_dep_test( 1, "slti", 0xf000000f, 0xfff, 0x00000001 ),
    gen_rimm_src_dep_test( 0, "slti", 0x000000f0, 0x0f0, 0x00000000 ),
  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_rimm_src_eq_dest_test( "slti", 0xffffff0f, 0x400, 0x00000001 ),
  ]

#-------------------------------------------------------------------------
# gen_value_test
#-------------------------------------------------------------------------

def gen_value_test():
  return [
    gen_rimm_value_test( "slti", 0xff00ff00, 0xf0f, 0x00000001 ),
    gen_rimm_value_test( "slti", 0x0ff00ff0, 0x0f0, 0x00000000 ),
    gen_rimm_value_test( "slti", 0x00ff00ff, 0x00f, 0x00000000 ),
    gen_rimm_value_test( "slti", 0xf00ff00f, 0xff0, 0x00000001 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    src0 = Bits( 32, random.randint(0,0xffffffff) )
    imm  = Bits( 12, random.randint(0,0xfff) )
    src1 = sext(imm,32)
    if (src0[31] == 1):
      if (src1[31] == 0):
        dest = Bits(32, 0x00000001)
      else:
        src0 = ~src0 + 1
        src1 = ~src1 + 1
        if (src0 < src1):
          dest = Bits(32, 0x00000001)
        else:
          dest = Bits(32, 0x00000000) 
    else:
      if (src1[31] == 0):
        if (src0 < src1):
          dest = Bits(32, 0x00000001)
        else:
          dest = Bits(32, 0x00000000)
      else:
        dest = Bits(32, 0x00000000)
    asm_code.append( gen_rimm_value_test( "slti", src0.uint(), imm.uint(), dest.uint() ) )
  return asm_code


