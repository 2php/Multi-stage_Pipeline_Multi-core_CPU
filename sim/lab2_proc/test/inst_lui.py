#=========================================================================
# lui
#=========================================================================

import random

from pymtl import *
from inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    lui x1, 0x0001
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x1 > 0x00001000
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
    gen_imm_template( 5, "lui", 0x000ff, 0x000ff000 ),
    gen_imm_template( 4, "lui", 0xf00f0, 0xf00f0000 ),
    gen_imm_template( 3, "lui", 0xf0000, 0xf0000000 ),
    gen_imm_template( 2, "lui", 0x0000f, 0x0000f000 ),
    gen_imm_template( 1, "lui", 0xfff00, 0xfff00000 ),
    gen_imm_template( 0, "lui", 0x0f000, 0x0f000000 ),
  ]

#-------------------------------------------------------------------------
# gen_imm_dest_dep_test
#-------------------------------------------------------------------------

def gen_imm_dest_dep_test():
  return [
    gen_imm_template( 5, "lui", 0x0f63f, 0x0f63f000 ),
    gen_imm_template( 4, "lui", 0xff720, 0xff720000 ),
    gen_imm_template( 3, "lui", 0xf03d0, 0xf03d0000 ),
    gen_imm_template( 2, "lui", 0x0a05f, 0x0a05f000 ),
    gen_imm_template( 1, "lui", 0xffaaf, 0xffaaf000 ),
    gen_imm_template( 0, "lui", 0x0bcf0, 0x0bcf0000 ),
  ]

#-------------------------------------------------------------------------
# gen_imm_value_test
#-------------------------------------------------------------------------

def gen_imm_value_test():
  return [
    gen_imm_template( 8, "lui", 0x44400, 0x44400000 ),
    gen_imm_template( 1, "lui", 0x5f03f, 0x5f03f000 ),
    gen_imm_template( 2, "lui", 0x0f110, 0x0f110000 ),
    gen_imm_template( 3, "lui", 0x00fdf, 0x00fdf000 ),
    gen_imm_template( 6, "lui", 0xff4d0, 0xff4d0000 ),
  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():
  asm_code = []
  for i in xrange(100):
    imm  = Bits( 20, random.randint(0,0xfffff) )
    dest = Bits( 32, 0x00000000 )
    dest = dest | imm 
    dest = dest << 12 
    asm_code.append( gen_imm_template( random.randint(0,8), "lui", imm.uint(), dest.uint() ) )
  return asm_code
