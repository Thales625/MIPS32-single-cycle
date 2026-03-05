# MIPS32 Interactive Co-Simulation

A single-cycle MIPS32 processor implemented in VHDL, featuring a custom Python assembler and a real-time, GPU-accelerated graphical monitor. 

## 🛠️ Features
* **Hardware:** Single-cycle MIPS-like datapath in VHDL.
* **Assembler:** Custom Python script to compile `.asm` instructions into machine code.
* **Interactive GUI:** Real-time visualization of the Register File, Data Memory and a mapped Bitmap Display.
* **Memory-Mapped I/O:** Interactive keyboard input and Bitmap Display mapped directly to memory.
* **Simulation Control:** Play/Pause, Step and Reset functionalities.

## 📋 Prerequisites
Ensure you have the following installed:
* **Questa Intel Starter FPGA Edition**. Make sure the `vsim` command is available in your system's PATH.
* **Python 3.13**
* **GCC** (for VPI compilation)

Install the required Python libraries:
```bash
pip install cocotb dearpygui
```

## 🚀 How to Use

### 1. Write and Assemble Code

Write your MIPS assembly code and compile it into machine code.

```bash
cd assembler/
# Edit your code in code.asm
python main.py
```

### 2. Run the Simulation

Start the hardware simulation and the interactive GUI.

```bash
cd sim/
python main.py
```

*Note: If you only changed the assembly code and didn't modify the VHDL files, you can skip the logical synthesis step by running: `python main.py --skip-build`
