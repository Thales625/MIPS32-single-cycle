import os
import sys
import platform
import subprocess
from pathlib import Path
from cocotb_tools.runner import get_runner

if platform.system() == "Linux":
    try:
        lib_path = subprocess.check_output(
            ["gcc", "--print-file-name=libstdc++.so.6"], 
            text=True
        ).strip()
        
        if os.path.isabs(lib_path) and os.path.exists(lib_path):
            os.environ["LD_PRELOAD"] = lib_path
    except FileNotFoundError:
        print("WARNING: GCC not found. Questa might fail when loading the GUI.")

# define simulator
sim = os.getenv("SIM", "questa")

# define path
vhdl_dir = Path(__file__).resolve().parent.parent / "vhdl"

# get cocotb runner
runner = get_runner(sim)

# define vhdl files
vhdl_sources = [
    vhdl_dir / "Adder.vhd",
    vhdl_dir / "MultMatricial.vhd",
    vhdl_dir / "Mux2_1.vhd",
    vhdl_dir / "Reg.vhd",
    vhdl_dir / "RegFile.vhd",
    vhdl_dir / "ULA.vhd",
    vhdl_dir / "ULA_Operation.vhd",
    vhdl_dir / "Shifter.vhd",
    vhdl_dir / "MemInst.vhd",
    vhdl_dir / "MemData.vhd",
    vhdl_dir / "ControlUnit.vhd",
    vhdl_dir / "Processor.vhd"
]

def build():
    runner.build(
        sources=vhdl_sources,
        hdl_toplevel="processor",
        always=True,
        build_dir=".",
    )

def simulate():
    runner.test(
        hdl_toplevel="processor",
        hdl_toplevel_lang="vhdl",
        test_module="simulation",
        build_dir=".",
    )

if __name__ == "__main__":
    if not "--skip-build" in sys.argv:
        print("Building VHDL files...")
        build()

    print("Running simulation...")
    simulate()
