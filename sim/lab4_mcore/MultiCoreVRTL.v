//========================================================================
// Multi-Core Processor-Cache-Network
//========================================================================

`ifndef LAB4_MCORE_MULTI_CORE_V
`define LAB4_MCORE_MULTI_CORE_V

`include "vc/mem-msgs.v"
`include "vc/trace.v"

`include "lab2_proc/ProcAltVRTL.v"
`include "lab3_mem/BlockingCacheAltVRTL.v"
`include "lab4_mcore/MemNetVRTL.v"
`include "lab4_mcore/CacheNetVRTL.v"
`include "lab4_mcore/McoreDataCacheVRTL.v"

module lab4_mcore_MultiCoreVRTL
(
  input  logic                         clk,           
  input  logic                         reset,         

  input  logic [c_num_cores-1:0][31:0] mngr2proc_msg,
  input  logic [c_num_cores-1:0]       mngr2proc_val,
  output logic [c_num_cores-1:0]       mngr2proc_rdy,

  output logic [c_num_cores-1:0][31:0] proc2mngr_msg,
  output logic [c_num_cores-1:0]       proc2mngr_val,
  input  logic [c_num_cores-1:0]       proc2mngr_rdy,

  output mem_req_16B_t                 imemreq_msg, 
  output logic                         imemreq_val, 
  input  logic                         imemreq_rdy,

  input  mem_resp_16B_t                imemresp_msg,
  input  logic                         imemresp_val,
  output logic                         imemresp_rdy,

  output mem_req_16B_t                 dmemreq_msg,
  output logic                         dmemreq_val,
  input  logic                         dmemreq_rdy,

  input  mem_resp_16B_t                dmemresp_msg,
  input  logic                         dmemresp_val,
  output logic                         dmemresp_rdy,

  //  Only takes Core 0's stats_en to the interface
  output logic                         stats_en, 
  output logic [c_num_cores-1:0]       commit_inst, 
  output logic [c_num_cores-1:0]       icache_miss,  
  output logic [c_num_cores-1:0]       icache_access,
  output logic [c_num_cores-1:0]       dcache_miss,  
  output logic [c_num_cores-1:0]       dcache_access 
);

  localparam c_num_cores = 4;

  mem_req_16B_t    ICMN_req_msg0, ICMN_req_msg1, ICMN_req_msg2, ICMN_req_msg3;
  logic            ICMN_req_val0, ICMN_req_val1, ICMN_req_val2, ICMN_req_val3; 
  logic            ICMN_req_rdy0, ICMN_req_rdy1, ICMN_req_rdy2, ICMN_req_rdy3;

  mem_resp_16B_t   ICMN_resp_msg0, ICMN_resp_msg1, ICMN_resp_msg2, ICMN_resp_msg3; 
  logic            ICMN_resp_val0, ICMN_resp_val1, ICMN_resp_val2, ICMN_resp_val3; 
  logic            ICMN_resp_rdy0, ICMN_resp_rdy1, ICMN_resp_rdy2, ICMN_resp_rdy3;

  mem_req_4B_t     icache_req_msg0, icache_req_msg1, icache_req_msg2, icache_req_msg3;
  logic            icache_req_val0, icache_req_val1, icache_req_val2, icache_req_val3;
  logic            icache_req_rdy0, icache_req_rdy1, icache_req_rdy2, icache_req_rdy3;

  mem_resp_4B_t    icache_resp_msg0, icache_resp_msg1, icache_resp_msg2, icache_resp_msg3;
  logic            icache_resp_val0, icache_resp_val1, icache_resp_val2, icache_resp_val3;
  logic            icache_resp_rdy0, icache_resp_rdy1, icache_resp_rdy2, icache_resp_rdy3;

  mem_req_4B_t     dcache_req_msg0, dcache_req_msg1, dcache_req_msg2, dcache_req_msg3;
  logic            dcache_req_val0, dcache_req_val1, dcache_req_val2, dcache_req_val3;
  logic            dcache_req_rdy0, dcache_req_rdy1, dcache_req_rdy2, dcache_req_rdy3;

  mem_resp_4B_t    dcache_resp_msg0, dcache_resp_msg1, dcache_resp_msg2, dcache_resp_msg3;
  logic            dcache_resp_val0, dcache_resp_val1, dcache_resp_val2, dcache_resp_val3;
  logic            dcache_resp_rdy0, dcache_resp_rdy1, dcache_resp_rdy2, dcache_resp_rdy3;

  logic            proc_commit_inst0, proc_commit_inst1, proc_commit_inst2, proc_commit_inst3;
  assign commit_inst = {proc_commit_inst3, proc_commit_inst2, proc_commit_inst1, proc_commit_inst0};
  
  logic            stats_en0, stats_en1, stats_en2, stats_en3;
  assign stats_en = stats_en0;  //  Only takes Core 0's stats_en to the interface

  logic            icache_miss3, icache_miss2, icache_miss1, icache_miss0;
  assign icache_miss0   = icache_resp_val0 & icache_resp_rdy0 & ~icache_resp_msg0.test[0];
  assign icache_miss1   = icache_resp_val1 & icache_resp_rdy1 & ~icache_resp_msg1.test[0];
  assign icache_miss2   = icache_resp_val2 & icache_resp_rdy2 & ~icache_resp_msg2.test[0];
  assign icache_miss3   = icache_resp_val3 & icache_resp_rdy3 & ~icache_resp_msg3.test[0];
  assign icache_miss    = {icache_miss3, icache_miss2, icache_miss1, icache_miss0};

  logic            icache_access0, icache_access1, icache_access2, icache_access3;
  assign icache_access0 = icache_req_val0  & icache_req_rdy0;
  assign icache_access1 = icache_req_val1  & icache_req_rdy1;
  assign icache_access2 = icache_req_val2  & icache_req_rdy2;
  assign icache_access3 = icache_req_val3  & icache_req_rdy3;
  assign icache_access  = {icache_access3, icache_access2, icache_access1, icache_access0};

  // processor 0

  lab2_proc_ProcAltVRTL proc0
  (
    .clk           (clk),
    .reset         (reset),

    .core_id       (32'd0),

    .imemreq_msg   (icache_req_msg0),//
    .imemreq_val   (icache_req_val0),//
    .imemreq_rdy   (icache_req_rdy0),//

    .imemresp_msg  (icache_resp_msg0),//
    .imemresp_val  (icache_resp_val0),//
    .imemresp_rdy  (icache_resp_rdy0),//

    .dmemreq_msg   (dcache_req_msg0),//
    .dmemreq_val   (dcache_req_val0),//
    .dmemreq_rdy   (dcache_req_rdy0),//

    .dmemresp_msg  (dcache_resp_msg0),//
    .dmemresp_val  (dcache_resp_val0),//
    .dmemresp_rdy  (dcache_resp_rdy0),//

    .mngr2proc_msg (mngr2proc_msg[0][31:0]),//
    .mngr2proc_val (mngr2proc_val[0]),//
    .mngr2proc_rdy (mngr2proc_rdy[0]),//

    .proc2mngr_msg (proc2mngr_msg[0][31:0]),//
    .proc2mngr_val (proc2mngr_val[0]),//
    .proc2mngr_rdy (proc2mngr_rdy[0]),//

    .stats_en      (stats_en0),//
    .commit_inst   (proc_commit_inst0)//
  );

  // processor 1

  lab2_proc_ProcAltVRTL proc1
  (
    .clk           (clk),
    .reset         (reset),

    .core_id       (32'd1),

    .imemreq_msg   (icache_req_msg1),//
    .imemreq_val   (icache_req_val1),//
    .imemreq_rdy   (icache_req_rdy1),//

    .imemresp_msg  (icache_resp_msg1),//
    .imemresp_val  (icache_resp_val1),//
    .imemresp_rdy  (icache_resp_rdy1),//

    .dmemreq_msg   (dcache_req_msg1),//
    .dmemreq_val   (dcache_req_val1),//
    .dmemreq_rdy   (dcache_req_rdy1),//

    .dmemresp_msg  (dcache_resp_msg1),//
    .dmemresp_val  (dcache_resp_val1),//
    .dmemresp_rdy  (dcache_resp_rdy1),//

    .mngr2proc_msg (mngr2proc_msg[1][31:0]),//
    .mngr2proc_val (mngr2proc_val[1]),//
    .mngr2proc_rdy (mngr2proc_rdy[1]),//

    .proc2mngr_msg (proc2mngr_msg[1][31:0]),//
    .proc2mngr_val (proc2mngr_val[1]),//
    .proc2mngr_rdy (proc2mngr_rdy[1]),//

    .stats_en      (stats_en1),//
    .commit_inst   (proc_commit_inst1)//
  );

  // processor 2

  lab2_proc_ProcAltVRTL proc2
  (
    .clk           (clk),
    .reset         (reset),

    .core_id       (32'd2),

    .imemreq_msg   (icache_req_msg2),//
    .imemreq_val   (icache_req_val2),//
    .imemreq_rdy   (icache_req_rdy2),//

    .imemresp_msg  (icache_resp_msg2),//
    .imemresp_val  (icache_resp_val2),//
    .imemresp_rdy  (icache_resp_rdy2),//

    .dmemreq_msg   (dcache_req_msg2),//
    .dmemreq_val   (dcache_req_val2),//
    .dmemreq_rdy   (dcache_req_rdy2),//

    .dmemresp_msg  (dcache_resp_msg2),//
    .dmemresp_val  (dcache_resp_val2),//
    .dmemresp_rdy  (dcache_resp_rdy2),//

    .mngr2proc_msg (mngr2proc_msg[2][31:0]),//
    .mngr2proc_val (mngr2proc_val[2]),//
    .mngr2proc_rdy (mngr2proc_rdy[2]),//

    .proc2mngr_msg (proc2mngr_msg[2][31:0]),//
    .proc2mngr_val (proc2mngr_val[2]),//
    .proc2mngr_rdy (proc2mngr_rdy[2]),//

    .stats_en      (stats_en2),//
    .commit_inst   (proc_commit_inst2)//
  );


  // processor 3

  lab2_proc_ProcAltVRTL proc3
  (
    .clk           (clk),
    .reset         (reset),

    .core_id       (32'd3),

    .imemreq_msg   (icache_req_msg3),//
    .imemreq_val   (icache_req_val3),//
    .imemreq_rdy   (icache_req_rdy3),//

    .imemresp_msg  (icache_resp_msg3),//
    .imemresp_val  (icache_resp_val3),//
    .imemresp_rdy  (icache_resp_rdy3),//

    .dmemreq_msg   (dcache_req_msg3),//
    .dmemreq_val   (dcache_req_val3),//
    .dmemreq_rdy   (dcache_req_rdy3),//

    .dmemresp_msg  (dcache_resp_msg3),//
    .dmemresp_val  (dcache_resp_val3),//
    .dmemresp_rdy  (dcache_resp_rdy3),//

    .mngr2proc_msg (mngr2proc_msg[3][31:0]),//
    .mngr2proc_val (mngr2proc_val[3]),//
    .mngr2proc_rdy (mngr2proc_rdy[3]),//

    .proc2mngr_msg (proc2mngr_msg[3][31:0]),//
    .proc2mngr_val (proc2mngr_val[3]),//
    .proc2mngr_rdy (proc2mngr_rdy[3]),//

    .stats_en      (stats_en3),//
    .commit_inst   (proc_commit_inst3)//
  );


  // instruction cache 0

  lab3_mem_BlockingCacheAltVRTL
  #(
    .p_num_banks   (4)
  )
  icache0
  (
    .clk           (clk),
    .reset         (reset),

    .cachereq_msg  (icache_req_msg0),//
    .cachereq_val  (icache_req_val0),//
    .cachereq_rdy  (icache_req_rdy0),//

    .cacheresp_msg (icache_resp_msg0),//
    .cacheresp_val (icache_resp_val0),//
    .cacheresp_rdy (icache_resp_rdy0),//

    .memreq_msg    (ICMN_req_msg0),//
    .memreq_val    (ICMN_req_val0),//
    .memreq_rdy    (ICMN_req_rdy0),//

    .memresp_msg   (ICMN_resp_msg0),//
    .memresp_val   (ICMN_resp_val0),//
    .memresp_rdy   (ICMN_resp_rdy0)//

  );

  // instruction cache 1

  lab3_mem_BlockingCacheAltVRTL
  #(
    .p_num_banks   (4)
  )
  icache1
  (
    .clk           (clk),
    .reset         (reset),

    .cachereq_msg  (icache_req_msg1),//
    .cachereq_val  (icache_req_val1),//
    .cachereq_rdy  (icache_req_rdy1),//

    .cacheresp_msg (icache_resp_msg1),//
    .cacheresp_val (icache_resp_val1),//
    .cacheresp_rdy (icache_resp_rdy1),//

    .memreq_msg    (ICMN_req_msg1),//
    .memreq_val    (ICMN_req_val1),//
    .memreq_rdy    (ICMN_req_rdy1),//

    .memresp_msg   (ICMN_resp_msg1),//
    .memresp_val   (ICMN_resp_val1),//
    .memresp_rdy   (ICMN_resp_rdy1)//

  );

  // instruction cache 2

  lab3_mem_BlockingCacheAltVRTL
  #(
    .p_num_banks   (4)
  )
  icache2
  (
    .clk           (clk),
    .reset         (reset),

    .cachereq_msg  (icache_req_msg2),//
    .cachereq_val  (icache_req_val2),//
    .cachereq_rdy  (icache_req_rdy2),//

    .cacheresp_msg (icache_resp_msg2),//
    .cacheresp_val (icache_resp_val2),//
    .cacheresp_rdy (icache_resp_rdy2),//

    .memreq_msg    (ICMN_req_msg2),//
    .memreq_val    (ICMN_req_val2),//
    .memreq_rdy    (ICMN_req_rdy2),//

    .memresp_msg   (ICMN_resp_msg2),//
    .memresp_val   (ICMN_resp_val2),//
    .memresp_rdy   (ICMN_resp_rdy2)//

  );

  // instruction cache 3

  lab3_mem_BlockingCacheAltVRTL
  #(
    .p_num_banks   (4)
  )
  icache3
  (
    .clk           (clk),
    .reset         (reset),

    .cachereq_msg  (icache_req_msg3),//
    .cachereq_val  (icache_req_val3),//
    .cachereq_rdy  (icache_req_rdy3),//

    .cacheresp_msg (icache_resp_msg3),//
    .cacheresp_val (icache_resp_val3),//
    .cacheresp_rdy (icache_resp_rdy3),//

    .memreq_msg    (ICMN_req_msg3),//
    .memreq_val    (ICMN_req_val3),//
    .memreq_rdy    (ICMN_req_rdy3),//

    .memresp_msg   (ICMN_resp_msg3),//
    .memresp_val   (ICMN_resp_val3),//
    .memresp_rdy   (ICMN_resp_rdy3)//

  );

  // Instruciton Memory Network
  mem_req_16B_t  [c_num_cores-1:0] icache_MNreq_msg;
  logic          [c_num_cores-1:0] icache_MNreq_val;
  logic          [c_num_cores-1:0] icache_MNreq_rdy;
  assign icache_MNreq_msg = {ICMN_req_msg3, ICMN_req_msg2, ICMN_req_msg1, ICMN_req_msg0};
  assign icache_MNreq_val = {ICMN_req_val3, ICMN_req_val2, ICMN_req_val1, ICMN_req_val0};
  assign icache_MNreq_rdy = {ICMN_req_rdy3, ICMN_req_rdy2, ICMN_req_rdy1, ICMN_req_rdy0}; 

  mem_resp_16B_t [c_num_cores-1:0] icache_MNresp_msg;
  logic          [c_num_cores-1:0] icache_MNresp_val;
  logic          [c_num_cores-1:0] icache_MNresp_rdy;
  assign icache_MNresp_msg = {ICMN_resp_msg3, ICMN_resp_msg2, ICMN_resp_msg1, ICMN_resp_msg0};
  assign icache_MNresp_val = {ICMN_resp_val3, ICMN_resp_val2, ICMN_resp_val1, ICMN_resp_val0};
  assign icache_MNresp_rdy = {ICMN_resp_rdy3, ICMN_resp_rdy2, ICMN_resp_rdy1, ICMN_resp_rdy0};
  
  mem_req_16B_t  [c_num_cores-1:0] full_memreq_msg;
  assign imemreq_msg = full_memreq_msg[0];
  logic          [c_num_cores-1:0] full_memreq_val;
  assign imemreq_val = full_memreq_val[0];
  logic          [c_num_cores-1:0] full_memreq_rdy;
  assign full_memreq_rdy = {imemreq_rdy,imemreq_rdy,imemreq_rdy,imemreq_rdy};

  mem_resp_16B_t [c_num_cores-1:0] full_memresp_msg;
  assign full_memresp_msg = {imemresp_msg,imemresp_msg,imemresp_msg,imemresp_msg};
  logic          [c_num_cores-1:0] full_memresp_val;
  assign full_memresp_val = {imemresp_val,imemresp_val,imemresp_val,imemresp_val};
  logic          [c_num_cores-1:0] full_memresp_rdy;
  assign imemresp_rdy = full_memreq_rdy[0];

  lab4_mcore_MemNetVRTL  MemNet
  (
  .clk              (clk),
  .reset            (reset),

  .memreq_msg       (icache_MNreq_msg),//
  .memreq_val       (icache_MNreq_val),//
  .memreq_rdy       (icache_MNreq_rdy),//

  .memresp_msg      (icache_MNresp_msg),//
  .memresp_val      (icache_MNresp_val),//
  .memresp_rdy      (icache_MNresp_rdy),//

  .mainmemreq_msg   (full_memreq_msg),//
  .mainmemreq_val   (full_memreq_val),//
  .mainmemreq_rdy   (full_memreq_rdy),//

  .mainmemresp_msg  (full_memresp_msg),
  .mainmemresp_val  (full_memresp_val),
  .mainmemresp_rdy  (full_memresp_rdy)

);

  // Multi-core data cache
  mem_req_4B_t   [c_num_cores-1:0] dcache_req_msg;
  logic          [c_num_cores-1:0] dcache_req_val;
  logic          [c_num_cores-1:0] dcache_req_rdy;
  assign dcache_req_msg = {dcache_req_msg3, dcache_req_msg2, dcache_req_msg1, dcache_req_msg0};
  assign dcache_req_val = {dcache_req_val3, dcache_req_val2, dcache_req_val1, dcache_req_val0};
  assign dcache_req_rdy = {dcache_req_rdy3, dcache_req_rdy2, dcache_req_rdy1, dcache_req_rdy0};

  mem_resp_4B_t  [c_num_cores-1:0] dcache_resp_msg;
  logic          [c_num_cores-1:0] dcache_resp_val;
  logic          [c_num_cores-1:0] dcache_resp_rdy;
  assign dcache_resp_msg = {dcache_resp_msg3, dcache_resp_msg2, dcache_resp_msg1, dcache_resp_msg0};
  assign dcache_resp_val = {dcache_resp_val3, dcache_resp_val2, dcache_resp_val1, dcache_resp_val0};
  assign dcache_resp_rdy = {dcache_resp_rdy3, dcache_resp_rdy2, dcache_resp_rdy1, dcache_resp_rdy0};

  lab4_mcore_McoreDataCacheVRTL McoreDataCache
  (
    .clk               (clk),        //
    .reset             (reset),      //

    .procreq_msg       (dcache_req_msg),//
    .procreq_val       (dcache_req_val),//
    .procreq_rdy       (dcache_req_rdy),//

    .procresp_msg      (dcache_resp_msg),//
    .procresp_val      (dcache_resp_val),//
    .procresp_rdy      (dcache_resp_rdy),//

    .mainmemreq_msg    (dmemreq_msg),//
    .mainmemreq_val    (dmemreq_val),//
    .mainmemreq_rdy    (dmemreq_rdy),//

    .mainmemresp_msg   (dmemresp_msg),//
    .mainmemresp_val   (dmemresp_val),//
    .mainmemresp_rdy   (dmemresp_rdy),//

    .dcache_miss       (dcache_miss),//
    .dcache_access     (dcache_access)//

  );

  //`VC_TRACE_BEGIN
  //begin

    // This is staffs' line trace, which assume the processors and icaches
    // are instantiated in using generate statement, and the data cache
    // system is instantiated with the name dcache. You can add net to the
    // line trace.
    // Feel free to revamp it or redo it based on your need.

    //CORES_CACHES[0].icache.line_trace( trace_str );
    //CORES_CACHES[0].proc.line_trace( trace_str );
    //CORES_CACHES[1].icache.line_trace( trace_str );
    //CORES_CACHES[1].proc.line_trace( trace_str );
    //CORES_CACHES[2].icache.line_trace( trace_str );
    //CORES_CACHES[2].proc.line_trace( trace_str );
    //CORES_CACHES[3].icache.line_trace( trace_str );
    //CORES_CACHES[3].proc.line_trace( trace_str );

    //dcache.line_trace( trace_str );
  //end
  //`VC_TRACE_END

endmodule

`endif /* LAB4_MCORE_MULTI_CORE_V */
