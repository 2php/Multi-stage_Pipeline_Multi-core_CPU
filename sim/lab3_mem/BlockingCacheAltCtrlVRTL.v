//=========================================================================
// Alternative Blocking Cache Control Unit
//=========================================================================

`ifndef LAB3_MEM_BLOCKING_CACHE_ALT_CTRL_V
`define LAB3_MEM_BLOCKING_CACHE_ALT_CTRL_V

`include "vc/mem-msgs.v"
`include "vc/assert.v"
`include "vc/regfiles.v"

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// LAB TASK: Include necessary files
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

module lab3_mem_BlockingCacheAltCtrlVRTL
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
  output logic                        val_cache1,
  output logic                        val_cache2,
  input  logic                        which_cache,
  output logic			                  DAR_sel,
  output logic [size-1:0]             idx,

  output logic                        tag_array_ren,
  output logic                        tag_array_wen1,
  output logic                        tag_array_wen2,
  output logic                        data_array_ren,
  output logic                        data_array_wen1,
  output logic[15:0]                  data_array_wben1,
  output logic                        data_array_wen2,
  output logic[15:0]                  data_array_wben2,
  

  output logic                        read_data_reg_en,
  output logic                        evict_addr_reg_en,
  output logic[2:0]                   read_word_mux_sel,
  output logic                        memreq_addr_mux_sel,

  output logic[1:0]                   hit,
  output logic[2:0]                   memreq_type,
  output logic[2:0]                   cacheresp_type  

 );

  logic dir1,dir2;
  localparam size = 3-p_idx_shamt;
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
  assign idx = cachereq_addr[6:4+p_idx_shamt];
  
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

  always_comb begin
      case(state)
        st_i: if (cachereq_val == 1'b1) next_state = st_tc;
              else next_state = st_i; 
        st_tc: begin
	        if (cachereq_type == ca_init)                        //// init
	          next_state = st_in;
	        else if ((cachereq_type == ca_read)&&(tag_match))    //// read hit
	          next_state = st_rd;
	        else if ((cachereq_type == ca_writ)&&(tag_match))    //// write hit
	          next_state = st_wd;
	        else if (!tag_match&&!dir_cache1&&!dir_cache2)       //// miss and both clean
	          next_state = st_rr;
	        else if (!tag_match&&!MRU&&!dir_cache2)              //// miss and LRU clean
	          next_state = st_rr;
	        else if (!tag_match&& MRU&&!dir_cache1)              //// miss and LRU clean
	          next_state = st_rr;
	        else if (!tag_match&&dir_cache1&&dir_cache2)         //// miss and both dirty
	          next_state = st_ep;
	        else if (!tag_match&&!MRU&&dir_cache2)               //// miss and LRU dirty
	          next_state = st_ep;
	        else if (!tag_match&& MRU&&dir_cache1)               //// miss and LRU dirty
	          next_state = st_ep;
		else
		  next_state = error;
          end

        st_in: next_state = st_w;
        st_rd: next_state = st_w;
        st_wd: next_state = st_w;
        st_ep: next_state = st_er;
        st_er: if (memreq_rdy)  next_state = st_ew;
	       else next_state = st_er;
        st_ew: if (memresp_val) next_state = st_rr;
	       else next_state = st_ew;
        st_rr: if (memreq_rdy)  next_state = st_rw;
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
        default: next_state = st_i;
      endcase
  end 

  
  //cache/memory ainteraction 
  // signals in each state
  always_comb begin
    case(cachereq_addr[3:2])
      2'b00: data_array_wben1 = 16'h000f;
      2'b01: data_array_wben1 = 16'h00f0;
      2'b10: data_array_wben1 = 16'h0f00;
      2'b11: data_array_wben1 = 16'hf000;
    endcase
    case(cachereq_addr[3:2])
      2'b00: data_array_wben2 = 16'h000f;
      2'b01: data_array_wben2 = 16'h00f0;
      2'b10: data_array_wben2 = 16'h0f00;
      2'b11: data_array_wben2 = 16'hf000;
    endcase
    case (state)         
      st_i: begin
        most_en = 1'b0;
        evict_addr_reg_en = 1'b0;
        hit = 2'b1;
        cacheresp_val = 1'b0;
        cachereq_rdy = 1'b1;
        cachereq_en = 1'b1;
        tag_array_wen1 = 1'b0;
        tag_array_wen2 = 1'b0;
        data_array_wen1 = 1'b0;
        data_array_wen2 = 1'b0;
        memreq_val = 1'b0;
        memresp_rdy = 1'b0;
        evict_addr_reg_en = 1'b1;
        most_en = 1'b0;
        dir_en1 = 1'b0;
        dir_en2 = 1'b0;
        tag_array_ren = 1'b1;
      end

      st_tc: begin
        most_en = tag_match;
        most_data = which_cache;
        cachereq_rdy = 1'b0;
        cachereq_en = 1'b0;
        tag_array_ren = 1'b1;
        data_array_ren = 1'b1;
      end

      st_in: begin
        hit = 2'b0;
        tag_array_wen1 = 1'b1;
        tag_array_wen2 = 1'b1;
        data_array_wen1 = 1'b1;
        data_array_wen2 = 1'b1;
        write_data_mux_sel = 1'b0;        
        tag_array_ren = 1'b0;
        most_en = 1'b0;
      end

      st_rd: begin
        read_data_reg_en = 1'b1;
        data_array_wen1 = 1'b0;
        data_array_wben1 = 16'h0000;
        tag_array_wen1 = 1'b0;             /////disable write for array1
        data_array_wen2 = 1'b0;
        data_array_wben2 = 16'h0000;
        tag_array_wen2 = 1'b0;             /////disable write for array2
        tag_array_ren = 1'b0;	           ///// no need to check tag again
        DAR_sel = most_data;
        read_word_mux_sel = 3'b1 + cachereq_addr[3:2];
        most_en = 1'b0;
        dir_en1 = 1'b0;
        dir_en2 = 1'b0;
      end
     
      st_wd: begin
        write_data_mux_sel = 1'b0;
        dir1 = 1'b1;
        dir2 = 1'b1;
        dir_en1 = 1'b0;
        dir_en2 = 1'b0;
        if (MRU == 0) begin
          tag_array_wen1 = 1'b1;
          data_array_wen1 = 1'b1;
          dir_en1 = 1'b1;
        end
        else begin
          tag_array_wen2 = 1'b1;
          data_array_wen2 = 1'b1;
          dir_en2 = 1'b1;
        end
        most_en = 1'b0;	  
	    end
      st_rr: begin
        tag_array_ren = 1'b0;
        hit = 2'b0; 
        memreq_val = 1'b1;
        memresp_rdy = 1'b0;
        memreq_addr_mux_sel = 1'b1;
        memreq_type = ca_read;
        most_en = 1'b0;
      end

      st_rw: begin
        memreq_val = 1'b0;
        memresp_rdy = 1'b1;  
      end
      
      st_ru: begin
        most_en = 1'b1;
        memresp_rdy = 1'b0;
        write_data_mux_sel = 1'b1;    
        dir1 = 1'b0;
        dir2 = 1'b0;
        if (!val_cache1) begin             ////  if cache1 is empty
          data_array_wen1 = 1'b1;
          data_array_wben1 = 16'hffff;
          tag_array_wen1 = 1'b1;
          most_data = 1'b0;
          dir_en1= 1'b1;
        end
        else if (!val_cache2) begin        ////  if cache2 is empty
          data_array_wen2 = 1'b1;
          data_array_wben2 = 16'hffff;
          tag_array_wen2 = 1'b1;
          most_data = 1'b1;
          dir_en2 = 1'b1;
        end
        else if (MRU==1'b0) begin
          data_array_wen2 = 1'b1;
          data_array_wben2 = 16'hffff;
          tag_array_wen2 = 1'b1;
          most_data = 1'b1;
          dir_en2 = 1'b1;
        end
        else begin
          data_array_wen1 = 1'b1;
          data_array_wben1 = 16'hffff;
          tag_array_wen1 = 1'b1;
          most_data = 1'b0;
          dir_en1 = 1'b1;
          end
      end

      st_ep: begin
        read_data_reg_en = 1'b1;
        tag_array_ren = 1'b1;
        evict_addr_reg_en = 1'b1;
        tag_array_wen1 = 1'b0;
        tag_array_wen2 = 1'b0;
        data_array_wen1 = 1'b0;
        data_array_wen2 = 1'b0;
        data_array_wben1 = 16'd0;
        data_array_wben2 = 16'd0;
        memreq_addr_mux_sel = 1'b0;
        DAR_sel = !MRU;
        most_en = 1'b0;
      end

      st_er: begin
        memreq_val = 1'b1;
        memreq_type = ca_writ;
      end

      st_ew: begin
        memreq_val = 1'b0;
        memresp_rdy = 1'b1;
        evict_addr_reg_en = 1'b1;
        read_data_reg_en = 1'b0;
      end

      st_w: begin
        data_array_wen1 = 1'b0;
        data_array_wen2 = 1'b0;
        tag_array_ren = 1'b0;     
        cacheresp_val = 1'b1;
        dir_en1 = 1'b0;
        dir_en2 = 1'b0;
        read_data_reg_en = 1'b0;
      end
      
      default: begin
      end
    endcase
  end 

  logic [7:0] com;

  always_ff @(posedge clk) begin 
     if (reset) com = 8'b0;
     else if (state == 4'b0) com = com+1'b1;
  end
  assign cacheresp_type = cachereq_type;
  assign memresp_en = 1'b1;


  logic MRU;
  logic most_en, most_data;
  vc_ResetRegfile_1r1w #(1,2**size,0,size) Most_recent_used_cache
  (
    .clk       (clk),
    .reset     (reset),
    .read_addr (idx),
    .read_data (MRU),
    .write_en  (most_en),
    .write_addr(idx),
    .write_data(most_data)
  );
  vc_ResetRegfile_1r1w #(1,2**size,0,size) Valid_RFile1
  (
    .clk       (clk),
    .reset     (reset),
    .read_addr (idx),
    .read_data (val_cache1),
    .write_en  (tag_array_wen1),
    .write_addr(idx),
    .write_data(1'b1)  // whenever I write to cache, data becomes valid
  );
  vc_ResetRegfile_1r1w #(1,2**size,0,size) Valid_RFile2
  (
    .clk       (clk),
    .reset     (reset),
    .read_addr (idx),
    .read_data (val_cache2),
    .write_en  (tag_array_wen2),
    .write_addr(idx),
    .write_data(1'b1)  // whenever I write to cache, data becomes valid
  );

  logic dir_cache1,dir_cache2;
  logic dir_en1, dir_en2;								  
  vc_ResetRegfile_1r1w #(1,2**size,0,size) Dirty_RFile1
  (
    .clk       (clk),
    .reset     (reset),
    .read_addr (idx),
    .read_data (dir_cache1),
    .write_en  (dir_en1),
    .write_addr(idx),
    .write_data(dir1)  //   different logic from base design
  );
  vc_ResetRegfile_1r1w #(1,2**size,0,size) Dirty_RFile2
  (
    .clk       (clk),
    .reset     (reset),
    .read_addr (idx),
    .read_data (dir_cache2),
    .write_en  (dir_en2),
    .write_addr(idx),
    .write_data(dir2)  
  );


endmodule

`endif
