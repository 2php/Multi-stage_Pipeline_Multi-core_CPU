#=========================================================================
# auipc
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    auipc x1, 0x00010                       # PC=0x200
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw  proc2mngr, x1 > 0x00010200
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
# gen_imm_test
#-------------------------------------------------------------------------

def gen_imm_test():
  return [
    gen_imm_template( 5, "auipc", 0x0000f, 0x0000f200 ),
    gen_imm_template( 4, "auipc", 0x00ee0, 0x00ee021c ),
    gen_imm_template( 3, "auipc", 0xf000f, 0xf000f234 ),
    gen_imm_template( 2, "auipc", 0xd4531, 0xd4531248 ),
    gen_imm_template( 1, "auipc", 0x80001, 0x80001258 ),
    gen_imm_template( 0, "auipc", 0x00000, 0x00000264 ),
  ]

#-------------------------------------------------------------------------
# gen_imm_dest_dep_test
#-------------------------------------------------------------------------

def gen_imm_dest_dep_test():
  return [
    gen_imm_template( 5, "auipc", 0x0f63f, 0x0f63f200 ),
    gen_imm_template( 4, "auipc", 0xff720, 0xff72021c ),
    gen_imm_template( 3, "auipc", 0xf03d0, 0xf03d0234 ),
    gen_imm_template( 2, "auipc", 0x0a05f, 0x0a05f248 ),
    gen_imm_template( 1, "auipc", 0xffaaf, 0xffaaf258 ),
    gen_imm_template( 0, "auipc", 0x0bcf0, 0x0bcf0264 ),
  ]

#-------------------------------------------------------------------------
# gen_imm_value_test
#-------------------------------------------------------------------------

def gen_imm_value_test():
  return [
    gen_imm_template( 8, "auipc", 0x44400, 0x44400200 ),
    gen_imm_template( 1, "auipc", 0x5f03f, 0x5f03f228 ),
    gen_imm_template( 2, "auipc", 0x0f110, 0x0f110234 ),
    gen_imm_template( 3, "auipc", 0x00fdf, 0x00fdf244 ),
    gen_imm_template( 6, "auipc", 0xff4d0, 0xff4d0258 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  inc = Bits( 32, 0x00000200 )
  for i in xrange(100):
    imm  = Bits( 20, random.randint(0,0xfffff) )
    temp = Bits( 32, 0x00000000 )
    temp = temp | imm 
    temp = temp << 12 
    temp = temp + inc
    inc = inc + 16;
    asm_code.append( gen_imm_template( 2 , "auipc", imm.uint(), temp.uint() ) )
  return asm_code
