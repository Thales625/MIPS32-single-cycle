import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

@cocotb.test()
async def test_processor_execution(dut):
    # set clock
    cocotb.start_soon(Clock(dut.clock, 10, unit="ns").start())

    # apply reset
    cocotb.log.info("applying Reset...")
    dut.reset.value = 1
    await RisingEdge(dut.clock)
    dut.reset.value = 0
    
    # monitor ports
    cocotb.log.info("initializing CPU...")
    
    for cycle in range(10):
        # wait clock rising edge
        await RisingEdge(dut.clock)
        
        # read ports
        current_pc = dut.debug_pc.value
        current_inst = dut.data_out.value
        
        # logging
        cocotb.log.info(f"CYCLE {cycle}: PC = {current_pc.to_unsigned():<4} | INSTRUCTION = {current_inst}")
