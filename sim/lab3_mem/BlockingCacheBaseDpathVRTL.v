//=========================================================================
// Baseline Blocking Cache Datapath
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_BASE_DPATH_V
`define LAB3_MEM_BLOCKING_CACHE_BASE_DPATH_V

`include "vc/mem-msgs.v"
`include "vc/srams.v"


//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab3_mem_BlockingCacheBaseDpathVRTL
#(
  parameter p_idx_shamt    = 0
)
(
  input  logic                        clk,
  input  logic                        reset,

  // Cache Request

  input  mem_req_4B_t                 cachereq_msg,

  // Cache Response

  output mem_resp_4B_t                cacheresp_msg,

  // Memory Request

  output mem_req_16B_t                memreq_msg,

  // Memory Response

  input  mem_resp_16B_t               memresp_msg,
  
  output logic[2:0]                   cachereq_type,
  output logic[31:0]                  cachereq_addr,
  output logic                        tag_match,
  //Controls
  input logic                         write_data_mux_sel,
  input logic                         cachereq_en,
  input logic                         memresp_en,
  input logic                         val_cache,

  input logic                         tag_array_ren,
  input logic                         tag_array_wen,
  input logic                         data_array_ren,
  input logic                         data_array_wen,
  input logic[15:0]                   data_array_wben,
  

  input logic                         read_data_reg_en,
  input logic                         evict_addr_reg_en,
  input logic[2:0]                    read_word_mux_sel,
  input logic                         memreq_addr_mux_sel,

  input logic[1:0]                    hit,
  input logic[2:0]                    memreq_type,
  input logic[2:0]                    cacheresp_type
);

  localparam size = 4-p_idx_shamt;
  
  logic[7:0]  opaque;
  logic[31:0] addr;
  logic[31:0] in_data;

  vc_EnResetReg #(8) cachereq_opaque_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cachereq_en),
    .d      (cachereq_msg[73:66]),
    .q      (opaque)
  );

  vc_EnResetReg #(3) cachereq_type_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cachereq_en),
    .d      (cachereq_msg[76:74]),
    .q      (cachereq_type)
  );

  vc_EnResetReg #(32) cachereq_addr_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cachereq_en),
    .d      (cachereq_msg[65:34]),
    .q      (addr)
  );

  logic [size-1:0] idx;
  assign idx = addr[7:p_idx_shamt+4];

  vc_EnResetReg #(32) cachereq_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (cachereq_en),
    .d      (cachereq_msg[31:0]),
    .q      (in_data)
  );     
  
  logic[127:0]    memresp_data;

  vc_EnResetReg #(128) memresp_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (memresp_en),
    .d      (memresp_msg[127:0]),
    .q      (memresp_data)
  ); 


  logic[127:0]    repl_data;
  logic[127:0]    dataAr_write_data; 
  logic[127:0]    dataAr_read_data; 
  assign repl_data = {4{in_data}};

  vc_Mux2 #(128) write_data_mux
  (
    .in0  (repl_data),
    .in1  (memresp_data),
    .sel  (write_data_mux_sel),
    .out  (dataAr_write_data)
  );
    
 
  
  logic[27:0]   tagAr_read_data;
  logic[27:0]   tagAr_write_data;  

  vc_CombinationalBitSRAM_1rw #(28,2**size) Tag_Array
  ( 
    .clk            (clk),
    .reset          (reset),
    .read_en        (tag_array_ren),
    .read_addr      (idx),
    .read_data      (tagAr_read_data),
    .write_en       (tag_array_wen),
    .write_addr     (idx),
    .write_data     (addr[31:4])
  );
  
  vc_CombinationalSRAM_1rw #(128,2**size) Data_Array
  ( 
    .clk            (clk),
    .reset          (reset),
    .read_en        (data_array_ren),
    .read_addr      (idx),
    .read_data      (dataAr_read_data),
    .write_en       (data_array_wen),
    .write_byte_en  (data_array_wben),
    .write_addr     (idx),
    .write_data     (dataAr_write_data)
  );

  assign cachereq_addr = addr;
  always_comb begin
    if (addr[31:4] == tagAr_read_data && val_cache)
      tag_match = 1'b1;
    else
      tag_match = 1'b0;
  end

  logic[31:0]    evict_addr;
  logic[127:0]   read_data;
  logic[31:0]    memreq_addr;
  logic[31:0]    cacheresp_data;
  
  vc_EnResetReg #(32) evict_addr_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (evict_addr_reg_en),
    .d      ({tagAr_read_data, 4'b0000}),
    .q      (evict_addr)
  ); 

  vc_EnResetReg #(128) read_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (read_data_reg_en),
    .d      (dataAr_read_data),
    .q      (read_data)
  ); 

  vc_Mux2 #(32) memreq_addr_mux
  (
    .in0  ({addr[31:4], 4'b0}),
    .in1  (evict_addr),
    .sel  (memreq_addr_mux_sel),
    .out  (memreq_addr)
  );
  
  logic[31:0] data_mux_out;
  vc_Mux5 #(32) read_word_mux
  (
    .in0  (32'b0), 
    .in1  (read_data[31:0]),
    .in2  (read_data[63:32]),
    .in3  (read_data[95:64]),
    .in4  (read_data[127:96]),    
    .sel  (read_word_mux_sel),
    .out  (data_mux_out)
  ); 

  always_comb begin
    if (cachereq_type == 3'b010) cacheresp_data = 32'b0;
    else cacheresp_data = data_mux_out;
  end

  assign cacheresp_msg = {cachereq_type, opaque, hit, 2'b0, cacheresp_data};  
  assign memreq_msg = {memreq_type, 8'b0, memreq_addr, 4'b0, read_data};   
endmodule

`endif