#=========================================================================
# BlockingCacheFL_test.py
#=========================================================================

from __future__ import print_function

import pytest
import random
import struct
import math


random.seed(0xdeadbeef)

from pymtl      import *
from pclib.test import mk_test_case_table, run_sim
from pclib.test import TestSource
from pclib.test import TestMemory

from pclib.ifcs import MemMsg,    MemReqMsg,    MemRespMsg
from pclib.ifcs import MemMsg4B,  MemReqMsg4B,  MemRespMsg4B
from pclib.ifcs import MemMsg16B, MemReqMsg16B, MemRespMsg16B

from TestCacheSink   import TestCacheSink
from lab3_mem.BlockingCacheFL import BlockingCacheFL

# We define all test cases here. They will be used to test _both_ FL and
# RTL models.
#
# Notice the difference between the TestHarness instances in FL and RTL.
#
# class TestHarness( Model ):
#   def __init__( s, src_msgs, sink_msgs, stall_prob, latency,
#                 src_delay, sink_delay, CacheModel, check_test, dump_vcd )
#
# The last parameter of TestHarness, check_test is whether or not we
# check the test field in the cacheresp. In FL model we don't care about
# test field and we set cehck_test to be False because FL model is just
# passing through cachereq to mem, so all cachereq sent to the FL model
# will be misses, whereas in RTL model we must set check_test to be True
# so that the test sink will know if we hit the cache properly.

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Model ):

  def __init__( s, src_msgs, sink_msgs, stall_prob, latency,
                src_delay, sink_delay, 
                CacheModel, num_banks, check_test, dump_vcd ):

    # Messge type

    cache_msgs = MemMsg4B()
    mem_msgs   = MemMsg16B()

    # Instantiate models

    s.src   = TestSource   ( cache_msgs.req,  src_msgs,  src_delay  )
    s.cache = CacheModel   ( num_banks = num_banks )
    s.mem   = TestMemory   ( mem_msgs, 1, stall_prob, latency )
    s.sink  = TestCacheSink( cache_msgs.resp, sink_msgs, sink_delay, check_test )

    # Dump VCD

    if dump_vcd:
      s.cache.vcd_file = dump_vcd

    # Connect

    s.connect( s.src.out,       s.cache.cachereq  )
    s.connect( s.sink.in_,      s.cache.cacheresp )

    s.connect( s.cache.memreq,  s.mem.reqs[0]     )
    s.connect( s.cache.memresp, s.mem.resps[0]    )

  def load( s, addrs, data_ints ):
    for addr, data_int in zip( addrs, data_ints ):
      data_bytes_a = bytearray()
      data_bytes_a.extend( struct.pack("<I",data_int) )
      s.mem.write_mem( addr, data_bytes_a )

  def done( s ):
    return s.src.done and s.sink.done

  def line_trace( s ):
    return s.src.line_trace() + " " + s.cache.line_trace() + " " \
         + s.mem.line_trace() + " " + s.sink.line_trace()

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def req( type_, opaque, addr, len, data ):
  msg = MemReqMsg4B()

  if   type_ == 'rd': msg.type_ = MemReqMsg.TYPE_READ
  elif type_ == 'wr': msg.type_ = MemReqMsg.TYPE_WRITE
  elif type_ == 'in': msg.type_ = MemReqMsg.TYPE_WRITE_INIT

  msg.addr   = addr
  msg.opaque = opaque
  msg.len    = len
  msg.data   = data
  return msg

def resp( type_, opaque, test, len, data ):
  msg = MemRespMsg4B()

  if   type_ == 'rd': msg.type_ = MemRespMsg.TYPE_READ
  elif type_ == 'wr': msg.type_ = MemRespMsg.TYPE_WRITE
  elif type_ == 'in': msg.type_ = MemRespMsg.TYPE_WRITE_INIT

  msg.opaque = opaque
  msg.len    = len
  msg.test   = test
  msg.data   = data

  return msg


def rand_numb():
   return (random.randint(0,0xffffffff))

def rand_addr():
   return (random.randint(0,0x000fffff)//4*4)

#smaller address space for more often memory hits
def rand_addr_sm():
   return (random.randint(0,0x00000fff)//4*4)   
#----------------------------------------------------------------------
# Test Case: read hit path
#----------------------------------------------------------------------
# The test field in the response message: 0 == MISS, 1 == HIT

def read_hit_1word_clean( base_addr ):
  a = random.randint(0,0xffffffff)
  return [
    #    type  opq  addr      len data                type  opq  test len data
    req( 'in', 0x0, base_addr, 0, a    ), resp( 'in', 0x0, 0,   0,  0     ),
    req( 'rd', 0x1, base_addr, 0, 0    ), resp( 'rd', 0x1, 1,   0,  a     ),
  ]

#----------------------------------------------------------------------
# Test Case: read hit path -- for set-associative cache
#----------------------------------------------------------------------
# This set of tests designed only for alternative design
# The test field in the response message: 0 == MISS, 1 == HIT

def read_hit_asso( base_addr ):
  a = rand_numb()
  b = rand_numb()
  addr_a = rand_addr()
  addr_b = rand_addr()//(16**3)+addr_a%(16**3) 
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, addr_a, 0, a      ), resp( 'wr', 0x0, 0,   0,  0      ),
    req( 'wr', 0x1, addr_b, 0, b      ), resp( 'wr', 0x1, 0,   0,  0      ),
    req( 'rd', 0x2, addr_a, 0, 0      ), resp( 'rd', 0x2, 1,   0,  a      ),
    req( 'rd', 0x3, addr_b, 0, 0      ), resp( 'rd', 0x3, 1,   0,  b      ),
  ]

#----------------------------------------------------------------------
# Test Case: read hit path -- for direct-mapped cache
#----------------------------------------------------------------------
# This set of tests designed only for baseline design

def read_hit_dmap( base_addr ):
  a = rand_numb()
  b = rand_numb()
  addr_a = rand_addr()
  addr_b = rand_addr()//(16**2)+addr_a%(16**2)
  return [
    #    type  opq  addr       len data                type  opq  test len data
    req( 'wr', 0x0, addr_a, 0, a     ), resp( 'wr', 0x0, 0,   0,  0     ),
    req( 'wr', 0x1, addr_b, 0, b     ), resp( 'wr', 0x1, 0,   0,  0     ),
    req( 'rd', 0x2, addr_a, 0, 0     ), resp( 'rd', 0x2, 1,   0,  a     ),
    req( 'rd', 0x3, addr_b, 0, 0     ), resp( 'rd', 0x3, 1,   0,  b     ),
  ]

#-------------------------------------------------------------------------
# Test Case: write hit path
#-------------------------------------------------------------------------

def write_hit_1word_clean( base_addr ):
  a = rand_numb()
  b = rand_numb()
  addr_a = rand_addr()
  addr_b = rand_addr()
  return [
    #    type  opq   addr      len data               type  opq   test len data
    req( 'in', 0x00, addr_a, 0, a    ), resp('in', 0x00, 0,   0,  0     ), # write word  addr_a
    req( 'wr', 0x01, addr_a, 0, b    ), resp('wr', 0x01, 1,   0,  0     ), # write word  addr_a
    req( 'rd', 0x02, addr_a, 0, 0    ), resp('rd', 0x02, 1,   0,  b     ), # read  word  addr_a
  ]

#-------------------------------------------------------------------------
# Test Case: read miss clean path
#-------------------------------------------------------------------------

def read_miss_1word_msg( base_addr ):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'rd', 0x00, 0x00000000, 0, 0          ), resp('rd', 0x00, 0, 0, 0xdeadbeef ), # read word  0x00000000
    req( 'rd', 0x01, 0x00000004, 0, 0          ), resp('rd', 0x01, 1, 0, 0x00c0ffee ), # read word  0x00000004
  ]

# Data to be loaded into memory before running the test

def read_miss_1word_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000000, 0xdeadbeef,
    0x00000004, 0x00c0ffee,
  ]


#-------------------------------------------------------------------------
# Test Case: read miss dirty path
#-------------------------------------------------------------------------

def read_miss_dirty_msg (base_addr): 
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, 0x00000004, 0, 0xabcd1234 ), resp('wr', 0x00, 0, 0, 0          ), # write word 0x00000004
    req( 'rd', 0x01, 0x00000100, 0, 0          ), resp('rd', 0x01, 0, 0, 0x00c0ffee ), # read word  0x00000010
    req( 'rd', 0x02, 0x00000004, 0, 0          ), resp('rd', 0x02, 0, 0, 0xabcd1234 ), # read word  0x00000000 
  ]    

def read_miss_dirty_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000100, 0x00c0ffee,
  ]

#-------------------------------------------------------------------------
# Test Case: write miss clean path (generic)
#-------------------------------------------------------------------------

def write_miss_1word_clean( base_addr ):
  a = rand_numb()
  addr_a = rand_addr()
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, addr_a, 0, a       ), resp('wr', 0x00, 0, 0, 0      ), # write word 0x00000000
    req( 'rd', 0x03, addr_a, 0, 0       ), resp('wr', 0x03, 1, 0, a      ), # read word 0x00000000
  ]

#-------------------------------------------------------------------------
# Test Case: write hit dirty path (generic)
#-------------------------------------------------------------------------

def write_hit_1word_dirty( base_addr ):
  a = rand_numb()
  b = rand_numb()
  addr_a = rand_addr()
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, addr_a, 0, a       ), resp('wr', 0x00, 0, 0, 0      ), # write word 0x00000000
    req( 'rd', 0x01, addr_a, 0, 0       ), resp('rd', 0x01, 1, 0, a      ), # read word 0x00000000
    req( 'wr', 0x02, addr_a, 0, b       ), resp('wr', 0x02, 1, 0, 0      ), # write word 0x00000000 
    req( 'rd', 0x03, addr_a, 0, 0       ), resp('rd', 0x03, 1, 0, b      ), # read word 0x00000000
  ]

#-------------------------------------------------------------------------
# Test Case: read hit dirty path (generic)
#-------------------------------------------------------------------------

def read_hit_1word_dirty( base_addr ):
  a = rand_numb()
  addr_a = rand_addr() 
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, addr_a, 0, a       ), resp('wr', 0x00, 0, 0, 0      ), # write word 0x00000000   
    req( 'rd', 0x01, addr_a, 0, 0       ), resp('rd', 0x01, 1, 0, a      ), # read word 0x00000000
  ]

#-------------------------------------------------------------------------
# Test Case: write miss dirty path (dmap)
#-------------------------------------------------------------------------

def write_miss_dirty_msg (base_addr):
  return [
    #    type  opq   addr      len  data               type  opq test len  data
    req( 'wr', 0x00, 0x00000000, 0, 0xabcd1234 ), resp('wr', 0x00, 0, 0, 0          ), # write word 0x00000000
    req( 'wr', 0x01, 0x00000100, 0, 0xdeadbeef ), resp('wr', 0x01, 0, 0, 0          ), # write word 0x00000100
    req( 'rd', 0x02, 0x00000104, 0, 0          ), resp('rd', 0x02, 1, 0, 0x00c0ffee ), # read word  0x00000104
    req( 'rd', 0x03, 0x00000100, 0, 0          ), resp('rd', 0x03, 1, 0, 0xdeadbeef ), # read word  0x00000100
    req( 'rd', 0x04, 0x00000000, 0, 0          ), resp('rd', 0x04, 0, 0, 0xabcd1234 ), # read word  0x00000000 
  ]    

def write_miss_dirty_mem( base_addr ):
  return [
    # addr      data (in int)
    0x00000104, 0x00c0ffee,
  ]

##############################################################################
# Random accesses
##############################################################################
#CacheTest was set to FALSE, since I do not track what is in the cache itself. It would not work otherwise (and it should not)
#-------------------------------------------------------------------------
# Random read/writes , no initial info in memory
#-------------------------------------------------------------------------

def find_addr(mem, addr):
   for i in range(len(mem)):
     if mem[i][0] == addr:
        return i
   return None
 
def random_accesses_msg( base_addr ):
  res = []
  mem = []
  l = [['wr', 0x780, 0x996ab63d],['wr', 0x9c8, 0xba43a338],['rd', 0xf70], ['wr', 0x5d4, 0xab1f1cad], ['rd',0xd20]] 
  print()
  for i in range(600):
    #print("memory")
    #print(mem)
    #print()
    type_ = random.choice(['wr', 'rd'])
    #type_ = l[i][0]
    addr = rand_addr_sm();
    #addr = l[i][1]
    print(i, hex(addr), type_)
    if (type_ == 'wr'):
       #data = l[i][2]
       data = rand_numb()
       print(hex(data))
       in_mem = find_addr(mem, addr) 
       if (in_mem == None):
          mem.append([addr,data])
       else:
          mem[in_mem][1] = data;
       res.append(req( 'wr', i%16, addr, 0, data ))
       res.append(resp('wr', i%16, 0, 0, 0))
    else:
       in_mem = find_addr(mem, addr)
       print("in_mem = ", in_mem) 
       if (in_mem == None):       
          data = 0x00000000
       else:
          data = mem[in_mem][1];
       #print(hex(data), i)      
       res.append(req( 'rd', i%16, addr, 0, 0 ))
       res.append(resp('rd', i%16, 0, 0, data))
  print(res)     
  return res

test_case_table_random = mk_test_case_table([
  (                         "msg_func               mem_data_func         nbank stall lat src sink"),
  [ "random_accesses",       random_accesses_msg,   None,                 1,    0.0,  0,  0,  0    ],  
])

#----------------------------------------------------------------------
# Banked cache test
#----------------------------------------------------------------------
# The test field in the response message: 0 == MISS, 1 == HIT

# This test case is to test if the bank offset is implemented correctly.
#
# The idea behind this test case is to differentiate between a cache
# with no bank bits and a design has one/two bank bits by looking at cache
# request hit/miss status.

#-------------------------------------------------------------------------
# Test table for generic test
#-------------------------------------------------------------------------

test_case_table_generic = mk_test_case_table([
  (                         "msg_func               mem_data_func         nbank stall lat src sink"),
  [ "read_hit_1word_clean",  read_hit_1word_clean,  None,                 1,    0.9,  10,  5,  6    ],
  [ "read_miss_1word",       read_miss_1word_msg,   read_miss_1word_mem,  1,    0.9,  10,  5,  6    ],
  [ "write_hit_1word_clean", write_hit_1word_clean, None,                 1,    0.9,  10,  5,  6    ],
  [ "write_miss_1word_clean",write_miss_1word_clean,None,                 1,    0.9,  10,  5,  6    ],
  [ "write_hit_1word_dirty", write_hit_1word_dirty, None,                 1,    0.9,  10,  5,  6    ],
  [ "read_hit_1word_dirty",  read_hit_1word_dirty,  None,                 1,    0.9,  10,  5,  6    ], 

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

test_case_table_generic_4bank = mk_test_case_table([
  (                         "msg_func               mem_data_func         nbank stall lat src sink"),
  [ "read_hit_1word_clean",  read_hit_1word_clean,  None,                 4,    0.9,  10,  5,  6    ],
  [ "read_miss_1word",       read_miss_1word_msg,   read_miss_1word_mem,  4,    0.9,  10,  5,  6    ],
  [ "read_hit_1word_4bank",  read_hit_1word_clean,  None,                 4,    0.9,  10,  5,  6    ],
  [ "write_hit_1word_clean", write_hit_1word_clean, None,                 4,    0.9,  10,  5,  6    ],
  [ "write_miss_1word_clean",write_miss_1word_clean,None,                 4,    0.9,  10,  5,  6    ],
  [ "write_hit_1word_dirty", write_hit_1word_dirty, None,                 4,    0.9,  10,  5,  6    ],
  [ "read_hit_1word_dirty",  read_hit_1word_dirty,  None,                 4,    0.9,  10,  5,  6    ], 

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

@pytest.mark.parametrize( **test_case_table_generic )
def test_generic( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )

#-------------------------------------------------------------------------
# Test table for set-associative cache (alternative design)
#-------------------------------------------------------------------------

test_case_table_set_assoc = mk_test_case_table([
  (                             "msg_func        mem_data_func    nbank stall lat src sink"),
  [ "read_hit_asso",             read_hit_asso,  None,            4,    0.0,  0,  0,  0    ],

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # LAB TASK: Add test cases to this table
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

])

@pytest.mark.parametrize( **test_case_table_set_assoc )
def test_set_assoc( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem  = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )


#-------------------------------------------------------------------------
# Test table for direct-mapped cache (baseline design)
#-------------------------------------------------------------------------

test_case_table_dir_mapped = mk_test_case_table([
  (                                  "msg_func              mem_data_func          nbank stall lat src sink"),
  [ "read_hit_dmap",                  read_hit_dmap,        None,                  0,    0.0,  0,  0,  0    ],
  [ "read_miss_dirty_1word",          read_miss_dirty_msg,  read_miss_dirty_mem,   0,    0.0,  0,  0,  0    ],
  [ "write_miss_dirty_1word",         write_miss_dirty_msg, write_miss_dirty_mem,  0,    0.0,  0,  0,  0    ],
])

@pytest.mark.parametrize( **test_case_table_dir_mapped )
def test_dir_mapped( test_params, dump_vcd ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem  = test_params.mem_data_func( 0 )
  # Instantiate testharness
  harness = TestHarness( msgs[::2], msgs[1::2],
                         test_params.stall, test_params.lat,
                         test_params.src, test_params.sink,
                         BlockingCacheFL, test_params.nbank,
                         False, dump_vcd )
  # Load memory before the test
  if test_params.mem_data_func != None:
    harness.load( mem[::2], mem[1::2] )
  # Run the test
  run_sim( harness, dump_vcd )



