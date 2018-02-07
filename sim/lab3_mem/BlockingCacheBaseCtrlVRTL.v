//=========================================================================
// Baseline Blocking Cache Control
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_BASE_CTRL_V
`define LAB3_MEM_BLOCKING_CACHE_BASE_CTRL_V

`include "vc/mem-msgs.v"
`include "vc/assert.v"
`include "vc/regfiles.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab3_mem_BlockingCacheBaseCtrlVRTL
#(
  parameter p_idx_shamt    = 0
)
(
  input  logic                        clk,
  input  logic                        reset,

  // Cache Request
  input  logic                        cachereq_val,
  output logic                        cachereq_rdy,
  input  logic[2:0]                   cachereq_type,
  input  logic[31:0]                  cachereq_addr,
  
  // Cache Response
  output logic                        cacheresp_val,
  input  logic                        cacheresp_rdy,

  // Memory Request
  output logic                        memreq_val,
  input  logic                        memreq_rdy,

  // Memory Response
  input  logic                        memresp_val,
  output logic                        memresp_rdy,

  //Dpath logic 
  input  logic                        tag_match,
  output logic                        write_data_mux_sel,
  output logic                        cachereq_en,
  output logic                        memresp_en,
  output logic                        val_cache,

  output logic                        tag_array_ren,
  output logic                        tag_array_wen,
  output logic                        data_array_ren,
  output logic                        data_array_wen,
  output logic[15:0]                  data_array_wben,
  

  output logic                        read_data_reg_en,
  output logic                        evict_addr_reg_en,
  output logic[2:0]                   read_word_mux_sel,
  output logic                        memreq_addr_mux_sel,

  output logic[1:0]                   hit,
  output logic[2:0]                   memreq_type,
  output logic[2:0]                   cacheresp_type  

 );

  // local parameters not meant to be set from outside

  // In this lab, to simplify things, we always use all bits except for the
  // offset in the tag, rather than storing the "normal" 24 bits. This way,
  // when implementing a multi-banked cache, we don't need to worry about
  // re-inserting the bank id into the address of a cacheline.
  localparam size = 4-p_idx_shamt;
  // cache type
  localparam ca_init = 3'd2;
  localparam ca_read = 3'd0;
  localparam ca_writ = 3'd1;
  localparam ca_wrtb = 3'd4;

  //STATES
  localparam st_i  = 4'd0;
  localparam st_tc = 4'd1;
  localparam st_in = 4'd2;
  localparam st_rd = 4'd3;
  localparam st_wd = 4'd4;  
  localparam st_ep = 4'd5;
  localparam st_er = 4'd6;
  localparam st_ew = 4'd7;
  localparam st_rr = 4'd8;
  localparam st_rw = 4'd9;
  localparam st_ru = 4'd10;
  localparam st_w  = 4'd11;
  localparam error = 4'd12;

  logic [size-1:0] idx;
  assign idx = cachereq_addr[7:4+p_idx_shamt];
  
  logic [3:0] next_state;
  logic [3:0] state;
  logic       error_flag;  

  // State Transition Control  

  always_ff @( posedge clk ) begin
    if (reset == 1'b1) begin
      state <= 4'd0;
      end
    else state<=next_state;
  end

  logic[6:0] abc;
  logic[1:0] efg;
  always_ff @(posedge clk) begin
    if (state == 0) abc <= abc + 1'b1;
  end
  //always_comb begin 
  //  case(abc)
  //    2'b00: if (memreq_rdy) efg = 2'b10;
  //           else efg = 2'b00;
  //    2'b01: if (memreq_rdy) efg = 2'b11;
  //           else efg = 2'b00;
  //    2'b10: if (memreq_rdy) efg = 2'b00;
  //          else efg = 2'b00;
  //    2'b11: if (memreq_rdy) efg = 2'b01;
  //           else efg = 2'b00;
  //  endcase
  //end  
  always_comb begin
      case(state)
        st_i: if (cachereq_val) next_state = st_tc;
              else next_state = st_i; 
        st_tc: begin
	        if (cachereq_type == ca_init)                        //// init
	          next_state = st_in;
	        else if ((cachereq_type == ca_read)&&tag_match)    //// read hit
	          next_state = st_rd;
	        else if ((cachereq_type == ca_writ)&&tag_match)    //// write hit
	          next_state = st_wd;
	        //else if ((cachereq_type == ca_wrtb)&&(tag_match))    //// write byte hit
	        //  next_state = st_wd;
	        else if (!tag_match&&!dir_cache)                     //// miss and not dirty
	          next_state = st_rr;
	        else if (!tag_match&& dir_cache)                     //// miss and dirty
	          next_state = st_ep;
          end

        st_in: next_state = st_w;
        st_rd: next_state = st_w;
        st_wd: next_state = st_w;
        st_ep: next_state = st_er;
        st_er: if (memreq_rdy)  next_state = st_ew;
               else next_state = st_er;
        st_ew: if (memresp_val) next_state = st_rr;
               else next_state = st_ew;
        st_rr: if (memreq_rdy) next_state = st_rw;
               else next_state = st_rr;
        st_rw: if (memresp_val) next_state = st_ru;
               else next_state = st_rw;
        st_ru: begin
        	  if (cachereq_type == ca_read)              ////  read
        	    next_state = st_rd;
        	  else if (cachereq_type == ca_writ)         ////  write
        	    next_state = st_wd;
          end

        st_w: if (cacheresp_rdy) next_state = st_i;
              else next_state = st_w;
        default: next_state = st_i;
      endcase
  end 
  
  //cache/memory ainteraction 
  // signals in each state
  assign memreq_addr_mux_sel = (state == st_er);
  always_comb begin
    if (state == st_wd||state == st_in) begin
      case(cachereq_addr[3:2])
        2'b00: data_array_wben = 16'h000f;
        2'b01: data_array_wben = 16'h00f0;
        2'b10: data_array_wben = 16'h0f00;
        2'b11: data_array_wben = 16'hf000;
      endcase    
    end
    else data_array_wben = 16'hffff;
    case (state)                
      st_i: begin
        hit = 2'b1;
        write_data_mux_sel = 1'b0;
    	  cacheresp_val = 1'b0;
    	  cachereq_rdy = 1'b1;
    	  cachereq_en = 1'b1;
    	  tag_array_wen = 1'b0;
    	  data_array_wen = 1'b0;
        data_array_ren = 1'b0;
    	  memreq_val = 1'b0;
      end

      st_tc: begin
    	  cachereq_rdy = 1'b0;
        cachereq_en = 1'b0;
    	  tag_array_ren = 1'b1;
      end

      st_in: begin
        hit = 2'b0;
        tag_array_wen = 1'b1;
        data_array_wen = 1'b1;      
    	  tag_array_ren = 1'b0;
      end

      st_rd: begin
    	  tag_array_ren = 1'b1;
    	  data_array_ren = 1'b1;
        read_data_reg_en = 1'b1;
    	  read_word_mux_sel = 3'b1 + cachereq_addr[3:2];
      end
     
      st_wd: begin
        write_data_mux_sel = 1'b0;
        data_array_wen = 1'b1;
    	  data_array_ren = 1'b0;
    	  data_array_wen = 1'b1;
      end
      
      st_rr: begin 
        write_data_mux_sel = 1'b1;     
        memresp_en = 1'b1;
        memreq_type = ca_read;
        memresp_rdy = 1'b1;
        hit = 2'b0; 
        memreq_val = 1'b1;
        tag_array_ren = 1'b0;
        tag_array_wen = 1'b1;
      end

      st_rw: begin
        data_array_wen = 1'b0;
        memreq_val = 1'b0;
        memresp_en = 1'b1;
        tag_array_wen = 1'b0;        
      end
      
      st_ru: begin
        memresp_rdy = 1'b0;
        data_array_wen = 1'b1;
      end

      st_ep: begin
        tag_array_ren = 1'b1;
        memreq_addr_mux_sel = 1'b1;
        data_array_ren = 1'b1;
        read_data_reg_en = 1'b1;
        memreq_type = ca_writ;
        evict_addr_reg_en = 1'b1;
      end

      st_er: begin
        memreq_val = 1'b1;
        end

      st_ew: begin
        tag_array_ren = 1'b0;
        data_array_ren = 1'b0;
        read_data_reg_en = 1'b0;
        memreq_val = 1'b0;
        end

      st_w: begin
        read_data_reg_en = 1'b0;
        data_array_wen = 1'b0;
        tag_array_ren = 1'b0;
        data_array_ren = 1'b0;       
        cacheresp_val = 1'b1;
      end
      
      default: begin
	      end
      endcase       
  end 

  //assign 
  assign cacheresp_type = cachereq_type;
  assign read_data_reg_en = 1'b1;
  assign memresp_en = 1'b1;
  assign evict_addr_reg_en = 1'b1;


  vc_ResetRegfile_1r1w #(1,2**size,0,size) Valid_RFile
  (
    .clk       (clk),
    .reset     (reset),
    .read_addr (idx),
    .read_data (val_cache),
    .write_en  (tag_array_wen),
    .write_addr(idx),
    .write_data(1'b1)  // whenever I write to cache, data becomes valid
  );

  logic dir_cache;
  vc_ResetRegfile_1r1w #(1,2**size,0,size) Dirty_RFile
  (
    .clk       (clk),
    .reset     (reset),
    .read_addr (idx),
    .read_data (dir_cache),
    .write_en  (state == st_wd || state == st_ew),
    .write_addr(idx),
    .write_data(state == st_wd)  // whenever operation is "write", data becomes dirty
  );

endmodule

`endif
