import cocotb
from cocotb.triggers import Timer

from visualizer import Window

# cpu coroutine
async def cpu_runner(dut):
    cycle = 0
    dut.clock.value = 0
    
    while True:
        if Window.is_running or Window.step_requested:
            dut.clock.value = 0
            await Timer(10, unit="ns")
            dut.clock.value = 1
            await Timer(10, unit="ns")
            dut.clock.value = 0

            await Timer(10, unit="ns")
            
            # Window.log(f"A={dut.ULA.MULTIPLIER.A} | B={dut.ULA.MULTIPLIER.B} | S={dut.ULA.MULTIPLIER.S}")

            cycle += 1

            Window.update(cycle)
            Window.step_requested = False
        else:
            await Timer(1, unit="ns")

@cocotb.test()
async def testbench(dut):
    # init DPG Window
    Window.init(dut)

    # init CPU coroutine
    Window.log("Starting simulation...")
    cocotb.start_soon(cpu_runner(dut))

    # apply reset
    Window.log("Applying reset...")
    dut.reset.value = 1
    await Timer(20, unit="ns")
    dut.reset.value = 0
    Window.log("CPU reseted.")
    
    Window.log("Simulation started.")
    while Window.running():
        Window.render()
        await Timer(10, unit="ns") 
        
    Window.destroy()
