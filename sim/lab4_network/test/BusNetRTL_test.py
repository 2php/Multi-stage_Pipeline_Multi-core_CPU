#=========================================================================
# BusNetRTL_test.py
#=========================================================================

import pytest

from lab4_network.BusNetRTL import BusNetRTL

#-------------------------------------------------------------------------
# Reuse tests from FL model
#-------------------------------------------------------------------------

from NetFL_test import run_net_test, test_case_table

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  run_net_test( BusNetRTL(), test_params.src_delay, test_params.sink_delay,
                test_params.msgs, dump_vcd, test_verilog )
