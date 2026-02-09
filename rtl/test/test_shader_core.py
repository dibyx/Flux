import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import struct

@cocotb.test()
async def test_instruction_decoder(dut):
    """Test instruction decoder with various instruction types"""
    
    # Test ADD R3, R1, R2
    # opcode=0x33, rd=3, rs1=1, rs2=2, funct3=0, funct7=0
    # Binary: 0000000_00010_00001_000_00011_0110011
    add_instr = 0x002081B3
    
    dut.instruction.value = add_instr
    await Timer(1, units='ns')
    
    assert dut.opcode.value == 0x33, f"Opcode mismatch: {dut.opcode.value:02x}"
    assert dut.rd.value == 3
    assert dut.rs1.value == 1
    assert dut.rs2.value == 2
    assert dut.alu_enable.value == 1
    assert dut.reg_write.value ==1
    
    dut._log.info("✓ ADD instruction decoded correctly")
    
    # Test ADDI R7, R6, 100
    # opcode=0x13, rd=7, rs1=6, imm=100
    addi_instr = 0x06430393
    
    dut.instruction.value = addi_instr
    await Timer(1, units='ns')
    
    assert dut.opcode.value == 0x13
    assert dut.rd.value == 7
    assert dut.rs1.value == 6
    assert dut.use_immediate.value == 1
    assert dut.immediate.value == 100
    
    dut._log.info("✓ ADDI instruction decoded correctly")
    
    # Test HALT
    halt_instr = 0x7F
    dut.instruction.value = halt_instr
    await Timer(1, units='ns')
    
    assert dut.is_halt.value == 1
    dut._log.info("✓ HALT instruction decoded correctly")


@cocotb.test()
async def test_simd_alu_add(dut):
    """Test SIMD ALU addition"""
    
    # Start clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # Reset
    dut.rst_n.value = 0
    dut.enable.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Prepare operands: [1.0, 2.0, 3.0, 4.0] + [5.0, 6.0, 7.0, 8.0]
    a = [1.0, 2.0, 3.0, 4.0]
    b = [5.0, 6.0, 7.0, 8.0]
    
    # Pack into 128-bit value
    a_packed = 0
    b_packed = 0
    for i in range(4):
        a_bits = struct.unpack('I', struct.pack('f', a[i]))[0]
        b_bits = struct.unpack('I', struct.pack('f', b[i]))[0]
        a_packed |= (a_bits << (32 * i))
        b_packed |= (b_bits << (32 * i))
    
    dut.operand_a.value = a_packed
    dut.operand_b.value = b_packed
    dut.alu_op.value = 0  # ALU_ADD
    dut.enable.value = 1
    
    await RisingEdge(dut.clk)
    dut.enable.value = 0
    await RisingEdge(dut.clk)
    
    # Check result: [6.0, 8.0, 10.0, 12.0]
    result_val = int(dut.result.value)
    result = []
    for i in range(4):
        bits = (result_val >> (32 * i)) & 0xFFFFFFFF
        f = struct.unpack('f', struct.pack('I', bits))[0]
        result.append(f)
    
    expected = [6.0, 8.0, 10.0, 12.0]
    for i in range(4):
        assert abs(result[i] - expected[i]) < 0.001, f"Lane {i}: {result[i]} != {expected[i]}"
    
    dut._log.info(f"✓ SIMD ADD result: {result}")


@cocotb.test()
async def test_register_file(dut):
    """Test register file read/write"""
    
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    
    # Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    
    # Write value 0xDEADBEEF to R5 of thread 0
    dut.wr_thread_id.value = 0
    dut.wr_addr.value = 5
    dut.wr_data.value = 0xDEADBEEFDEADBEEFDEADBEEFDEADBEEF
    dut.wr_enable.value = 1
    
    await RisingEdge(dut.clk)
    dut.wr_enable.value = 0
    
    # Read back from R5
    dut.rd_thread_id_a.value = 0
    dut.rd_addr_a.value = 5
    await Timer(1, units='ns')
    
    assert dut.rd_data_a.value == 0xDEADBEEFDEADBEEFDEADBEEFDEADBEEF
    dut._log.info("✓ Register write/read successful")
    
    # Test R0 hardwired to 0
    dut.rd_addr_a.value = 0
    await Timer(1, units='ns')
    assert dut.rd_data_a.value == 0, "R0 should always read 0"
    dut._log.info("✓ R0 hardwired to zero")
