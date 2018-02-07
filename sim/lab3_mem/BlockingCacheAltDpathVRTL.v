//=========================================================================
// Alternative Blocking Cache Datapath
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_ALT_DPATH_V
`define LAB3_MEM_BLOCKING_CACHE_ALT_DPATH_V

`include "vc/mem-msgs.v"
`include "vc/srams.v"

module lab3_mem_BlockingCacheAltDpathVRTL
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
  input logic                         val_cache1,
  input logic                         val_cache2,
  output logic                        which_cache,
  input logic                         DAR_sel,
  input logic [2-p_idx_shamt:0]       idx,

  input logic                         tag_array_ren,
  input logic                         tag_array_wen1,
  input logic                         tag_array_wen2,
  input logic                         data_array_ren,
  input logic                         data_array_wen1,
  input logic[15:0]                   data_array_wben1,
  input logic                         data_array_wen2,
  input logic[15:0]                   data_array_wben2,
  

  input logic                         read_data_reg_en,
  input logic                         evict_addr_reg_en,
  input logic[2:0]                    read_word_mux_sel,
  input logic                         memreq_addr_mux_sel,

  input logic[1:0]                    hit,
  input logic[2:0]                    memreq_type,
  input logic[2:0]                    cacheresp_type
);

  logic[7:0]  opaque;
  logic[31:0] addr;
  logic[31:0] in_data;
  localparam size = 3 - p_idx_shamt;
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

  logic [31:0] cache_req_data;
  assign cache_req_data = cachereq_msg[31:0];
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
  assign repl_data = {4{in_data}};

  vc_Mux2 #(128) write_data_mux
  (
    .in0  (repl_data),
    .in1  (memresp_data),
    .sel  (write_data_mux_sel),
    .out  (dataAr_write_data)
  );
    
 
  
  logic[27:0]   tagAr_read_data1;
  logic[27:0]   tagAr_read_data2;
  logic[size-1:0]    idx2;
  assign idx2 = addr[6:p_idx_shamt+4];

  vc_CombinationalBitSRAM_1rw #(28,2**size) Tag_Array1
  ( 
    .clk            (clk),
    .reset          (reset),
    .read_en        (tag_array_ren),
    .read_addr      (idx2),
    .read_data      (tagAr_read_data1),
    .write_en       (tag_array_wen1),
    .write_addr     (idx2),
    .write_data     (addr[31:4])
  );
  vc_CombinationalBitSRAM_1rw #(28,2**size) Tag_Array2
  ( 
    .clk            (clk),
    .reset          (reset),
    .read_en        (tag_array_ren),
    .read_addr      (idx2),
    .read_data      (tagAr_read_data2),
    .write_en       (tag_array_wen2),
    .write_addr     (idx2),
    .write_data     (addr[31:4])
  );
  
  vc_CombinationalSRAM_1rw #(128,2**size) Data_Array1
  ( 
    .clk            (clk),
    .reset          (reset),
    .read_en        (data_array_ren),
    .read_addr      (idx2),
    .read_data      (dataAr_read_data1),
    .write_en       (data_array_wen1),
    .write_byte_en  (data_array_wben1),
    .write_addr     (idx2),
    .write_data     (dataAr_write_data)
  );
  vc_CombinationalSRAM_1rw #(128,2**size) Data_Array2
  ( 
    .clk            (clk),
    .reset          (reset),
    .read_en        (data_array_ren),
    .read_addr      (idx2),
    .read_data      (dataAr_read_data2),
    .write_en       (data_array_wen2),
    .write_byte_en  (data_array_wben2),
    .write_addr     (idx2),
    .write_data     (dataAr_write_data)
  );

  logic [31:0]  mk_addr;
  logic [127:0] DAR_data; 
  logic [127:0] dataAr_read_data1; 
  logic [127:0] dataAr_read_data2; 

  vc_Mux2 #(128) DataAR_sel_mux
  (
    .in0  (dataAr_read_data1),
    .in1  (dataAr_read_data2),
    .sel  (DAR_sel),
    .out  (DAR_data)
  );
  vc_Mux2 #(32) TagAR_sel_mux
  (
    .in0  ({tagAr_read_data1,4'b0000}),
    .in1  ({tagAr_read_data2,4'b0000}),
    .sel  (DAR_sel),
    .out  (mk_addr)
  );

  assign cachereq_addr = addr;

  always_comb begin
    if ((addr[31:4] == tagAr_read_data1)&&val_cache1) begin
      which_cache = 1'b0;
      tag_match = 1'b1;
      end
    else if ((addr[31:4] == tagAr_read_data2)&&val_cache2) begin
      which_cache = 1'b1;
      tag_match = 1'b1;
      end
    else begin
      tag_match = 1'b0;
      end
  end

  logic[31:0]    evict_addr;
  logic[127:0]   read_data;
  logic[31:0]    memreq_addr;
  logic[31:0]    cacheresp_data;
  logic[31:0]    pre_evict_addr;

  vc_EnResetReg #(32) evict_addr_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (evict_addr_reg_en),
    .d      (mk_addr),
    .q      (evict_addr)
  ); 

  vc_EnResetReg #(128) read_data_reg
  (
    .clk    (clk),
    .reset  (reset),
    .en     (read_data_reg_en),
    .d      (DAR_data),
    .q      (read_data)
  ); 

  vc_Mux2 #(32) memreq_addr_mux
  (
    .in0  (evict_addr),
    .in1  ({addr[31:4],4'b0000}),
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
