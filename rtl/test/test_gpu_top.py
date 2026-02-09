import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_gpu_top_sanity(dut):
    """
    Basic sanity check for gpu_top.
    Verifies reset behavior and simple host register write.
    """
    
    # 1. Start Clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # 2. Reset
    dut.rst_n.value = 0
    dut.host_awvalid.value = 0
    dut.host_wvalid.value = 0
    await Timer(20, units="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # 3. Check Initial State
    # (Assuming internal signal visibility or output behavior)
    assert dut.video_b.value == 0, "Video Blue channel should be 0 after reset"

    # 4. Perform Host Write to Scratchpad
    # This controls the blue channel in our stub
    dut.host_awaddr.value = 0x0
    dut.host_wdata.value = 0xAA # Pattern
    dut.host_awvalid.value = 1
    dut.host_wvalid.value = 1
    
    await RisingEdge(dut.clk)
    
    # Wait for handshake (stub is 0-wait state)
    dut.host_awvalid.value = 0
    dut.host_wvalid.value = 0

    await RisingEdge(dut.clk)

    # 5. Verify Effect
    assert dut.video_b.value == 0xAA, f"Video Blue should be 0xAA, got {dut.video_b.value}"
    
    dut._log.info("Sanity check passed!")
