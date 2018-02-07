//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================
// base design

`ifndef LAB1_IMUL_INT_MUL_BASE_V
`define LAB1_IMUL_INT_MUL_BASE_V

`include "vc/trace.v"
`include "vc/muxes.v"
`include "vc/regs.v"
`include "vc/arithmetic.v"

// ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
// Define datapath and control unit here.

module Base_Control( 
	input logic clk,
	input logic rst,
	input logic in_val,
	input logic [3:0] b_sig,
	input logic out_rdy,
	output logic b_mux_sel,
	output logic a_mux_sel,
	output logic result_mux_sel,
	output logic result_en,
	output logic add_mux_sel,
	output logic in_rdy,
	output logic out_val,
	output logic [1:0] sh_sel
	);

	logic [1:0] state;
	logic [5:0] counter;
	logic [5:0] counter_add;

	always @(*) begin
		case (state)

			2'd0: begin
				out_val = 1'b0;
				in_rdy = 1'd1;
				b_mux_sel = 1'd1;
				a_mux_sel = 1'd1;
				result_mux_sel = 1'd1;
				result_en = 1'd1;
				add_mux_sel = 1'd0;
				end

			2'd1: begin
				in_rdy = 1'd0;
				b_mux_sel = 1'b0;
				a_mux_sel = 1'b0;
				result_mux_sel = 1'b0;
				result_en = 1'b1;
				if (b_sig[0] == 1'b1)
					add_mux_sel = 1'b0;
				else
					add_mux_sel = 1'b1;
				if (b_sig[3:1] == 3'b000) begin
					sh_sel = 2'd3;
					counter_add = 6'd4;
				   	end
				else if (b_sig[2:1] == 2'b00) begin
					sh_sel = 2'd2;
					counter_add = 6'd3;
				   	end
				else if (b_sig[1] == 1'b0) begin
					sh_sel = 2'd1;
					counter_add = 6'd2;
				   	end
				else begin
					sh_sel = 2'd0;
					counter_add = 6'd1;
					end
				end

			2'd2: begin
				out_val = 1'b1;
				result_en = 1'b0;
				end

			2'd3: begin
				
				end
		endcase
	end

	always @ (posedge clk) begin
		if (rst) begin
			state <= 2'd0;
			counter <= 6'd0;
		end 
		else
			case (state) ////// CHANGE STATES //////
				2'd0:	begin	
					counter <= 6'd0;
					if(in_val == 1'b0)			
						state <= 2'd0;
					else begin
						state <= 2'd1;
						end
					end
				
				2'd1: begin	
					counter <= counter+counter_add;		
					if (counter <= 6'd32) 
						state <= 2'd1;
					else
						state <= 2'd2;
				end
						
				2'd2: begin				
					if (out_rdy == 0)
						state <= 2'd2;
					else			
						state <= 2'd0;
				end
						
				2'd3: begin
					state <= 2'd0;
				end
				
				default: 			
					state <= 2'd0;	
			endcase	
	end
endmodule

// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

//========================================================================
// Integer Multiplier Fixed-Latency Implementation
//========================================================================

module lab1_imul_IntMulAltVRTL
(
  input  logic        clk,
  input  logic        reset,

  input  logic        req_val,
  output logic        req_rdy,
  input  logic [63:0] req_msg,

  output logic        resp_val,
  input  logic        resp_rdy,
  output logic [31:0] resp_msg
);

  // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Instantiate datapath and control models here and then connect them
  // together.
	logic [31:0] bMux_reg, aMux_reg, bReg_shift, aReg_shift;
	logic [31:0] aShift_mux, bShift_mux;
	logic [31:0] bShift_mux0, bShift_mux1, bShift_mux2, bShift_mux3;
	logic [31:0] aShift_mux0, aShift_mux1, aShift_mux2, aShift_mux3;
	logic [31:0] resultMux_resultReg;
	logic [31:0] ALU_addMux, addMux_resultMux;
	logic b_mux_sel, a_mux_sel, result_mux_sel;
	logic result_en, add_mux_sel;
	logic [1:0] sh_sel;

	Base_Control Control (
		.clk(clk),
		.rst(reset),
		.in_val(req_val),
		.b_sig(bReg_shift[3:0]),
		.out_rdy(resp_rdy),
		.b_mux_sel(b_mux_sel),
		.a_mux_sel(a_mux_sel),
		.result_mux_sel(result_mux_sel),
		.result_en(result_en),
		.add_mux_sel(add_mux_sel),
		.in_rdy(req_rdy),
		.out_val(resp_val),
		.sh_sel(sh_sel)
	);

	vc_Mux2 #(32) BMux (
		.in0(bShift_mux),
		.in1(req_msg[63:32]),
		.sel(b_mux_sel),
		.out(bMux_reg)
	);
	vc_Reg #(32) BReg (
		.clk(clk),
		.d(bMux_reg),
		.q(bReg_shift)
	);
	vc_RightLogicalShifter #(32,3) R_Shift1 (
		.in(bReg_shift),
		.out(bShift_mux0),
		.shamt(3'd1)
	);
	vc_RightLogicalShifter #(32,3) R_Shift2 (
		.in(bReg_shift),
		.out(bShift_mux1),
		.shamt(3'd2)
	);
	vc_RightLogicalShifter #(32,3) R_Shift3 (
		.in(bReg_shift),
		.out(bShift_mux2),
		.shamt(3'd3)
	);
	vc_RightLogicalShifter #(32,3) R_Shift4 (
		.in(bReg_shift),
		.out(bShift_mux3),
		.shamt(3'd4)
	);
	vc_Mux4 #(32) BShift_sel (
		.in0(bShift_mux0),
		.in1(bShift_mux1),
		.in2(bShift_mux2),
		.in3(bShift_mux3),
		.sel(sh_sel),
		.out(bShift_mux)
	);

	vc_Mux2 #(32) AMux (
		.in0(aShift_mux),
		.in1(req_msg[31:0]),
		.sel(a_mux_sel),
		.out(aMux_reg)
	);
	vc_Reg #(32) AReg (
		.d(aMux_reg),
		.q(aReg_shift),
		.clk(clk)
	);
	vc_LeftLogicalShifter #(32,3) L_Shift1 (
		.in(aReg_shift),
		.out(aShift_mux0),
		.shamt(3'd1)
	);
	vc_LeftLogicalShifter #(32,3) L_Shift2 (
		.in(aReg_shift),
		.out(aShift_mux1),
		.shamt(3'd2)
	);
	vc_LeftLogicalShifter #(32,3) L_Shift3 (
		.in(aReg_shift),
		.out(aShift_mux2),
		.shamt(3'd3)
	);
	vc_LeftLogicalShifter #(32,3) L_Shift4 (
		.in(aReg_shift),
		.out(aShift_mux3),
		.shamt(3'd4)
	);
	vc_Mux4 #(32) AShift_sel (
		.in0(aShift_mux0),
		.in1(aShift_mux1),
		.in2(aShift_mux2),
		.in3(aShift_mux3),
		.sel(sh_sel),
		.out(aShift_mux)
	);

	vc_Mux2 #(32) ResultMux (
		.in0(addMux_resultMux),
		.in1(32'd0),
		.sel(result_mux_sel),
		.out(resultMux_resultReg)
	);
	vc_EnReg #(32) ResultReg (
		.en(result_en),
		.d(resultMux_resultReg),
		.q(resp_msg),
		.clk(clk),
		.reset(reset)
	);
	vc_SimpleAdder #(32) dumbALU (
		.in0(aReg_shift),
		.in1(resp_msg),
		.out(ALU_addMux)
	);
	vc_Mux2 #(32) AddMux (
		.in0(ALU_addMux),
		.in1(resp_msg),
		.sel(add_mux_sel),
		.out(addMux_resultMux)
	);
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x", req_msg );
    vc_trace.append_val_rdy_str( trace_str, req_val, req_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    // Add additional line tracing using the helper tasks for
    // internal state including the current FSM state.
    // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", resp_msg );
    vc_trace.append_val_rdy_str( trace_str, resp_val, resp_rdy, str );

  end
  `VC_TRACE_END


  `endif /* SYNTHESIS */

endmodule

`endif /* LAB1_IMUL_INT_MUL_BASE_V */

