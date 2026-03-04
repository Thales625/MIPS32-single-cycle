import dearpygui.dearpygui as dpg

def format_hex(value):
    return f"0x{value:08X}"

def format_bin(value):
    return f"0b{value:032b}"

def read_signal(signal, signed=False):
    # prevent error when value = 'U' or 'X'
    if signal.value.is_resolvable:
        return signal.value.to_signed() if signed else signal.value.to_unsigned()
    return 0

class Window:
    is_running = False
    step_requested = False

    # bitmap display
    BM_border = True
    BM_p_size = 20
    BM_grid_w = 16
    BM_grid_h = 16

    # memory dump
    MDMP_size = 16

    # variable
    dut = None

    @classmethod
    def init(cls, dut):
        cls.dut = dut

        dpg.create_context()
        dpg.create_viewport(title='MIPS32 - Monitor', width=1024, height=768)
        dpg.setup_dearpygui()

        # control panel
        with dpg.window(label="Control Panel", width=550, height=130, no_resize=True, no_close=True):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Play", tag="btn_play", width=80, height=30, callback=cls.btn_play_pause)
                dpg.add_button(label="Step", width=80, height=30, callback=cls.btn_step)

            dpg.add_spacer(height=10)
            dpg.add_text("Cycle: 0 | PC: 0x00000000 | Instruction: 0b00000000000000000000000000000000", tag="cpu_info", color=[0, 255, 0])
            dpg.add_spacer(height=10)

        # register file
        with dpg.window(label="Register File", width=270, height=520, pos=(0, 140), no_close=True):
            with dpg.table(header_row=True, borders_innerH=True, borders_innerV=True):
                dpg.add_table_column(label="Reg")
                dpg.add_table_column(label="Value (Hex)")
                for i in range(32):
                    with dpg.table_row():
                        dpg.add_text(f"${i}")
                        dpg.add_text("0x00000000 (0)", tag=f"reg_{i}", color=[155, 165, 0])

        # memory dump
        with dpg.window(label="Memory dump", width=270, height=520, pos=(280, 140), no_close=True):
            dpg.add_input_int(label="Base Addr", tag="mem_base_addr", default_value=0, step=cls.MDMP_size, callback=cls.update_mem_dmp)
            with dpg.table(header_row=True, borders_innerH=True, borders_innerV=True):
                dpg.add_table_column(label="Address")
                dpg.add_table_column(label="Value (Hex)")
                for i in range(cls.MDMP_size):
                    with dpg.table_row():
                        dpg.add_text(f"[{i:04d}]", tag=f"mem_p_{i}")
                        dpg.add_text("0x00000000 (0)", tag=f"mem_{i}", color=[0, 255, 255])

        # bitmap display
        with dpg.window(label="Bitmap Display", width=cls.BM_p_size*cls.BM_grid_w+20, height=cls.BM_p_size*cls.BM_grid_h+120, pos=(560, 0), no_resize=True, no_close=True):
            dpg.add_input_int(label="Base Addr", tag="BM_base_addr", default_value=0, step=cls.MDMP_size, callback=cls.update_bitmap)

            dpg.add_spacer(height=10)

            with dpg.drawlist(width=cls.BM_grid_w * cls.BM_p_size, height=cls.BM_grid_h * cls.BM_p_size):
                for y in range(cls.BM_grid_h):
                    for x in range(cls.BM_grid_w):
                        p1 = (x * cls.BM_p_size, y * cls.BM_p_size)
                        p2 = ((x + 1) * cls.BM_p_size, (y + 1) * cls.BM_p_size)
                        
                        dpg.draw_rectangle(pmin=p1, pmax=p2, fill=(0, 0, 0, 255), color=(40, 40, 40, 125 if cls.BM_border else 0), tag=f"px_{x}_{y}")

        # init data
        cls.update_reg_file()
        cls.update_mem_dmp()
        cls.update_bitmap()

        # show window
        dpg.show_viewport()

    @classmethod
    def btn_play_pause(cls):
        cls.is_running = not cls.is_running
        dpg.configure_item("btn_play", label="Pause" if cls.is_running else "Play")

    @classmethod
    def btn_step(cls):
        cls.step_requested = True

    @classmethod
    def update_reg_file(cls):
        for i in range(32):
            val = read_signal(cls.dut.RF.s_Reg[i], signed=True) 
            dpg.set_value(f"reg_{i}", format_hex(val) + f" ({val})")

    @classmethod
    def update_mem_dmp(cls):
        base_addr = dpg.get_value("mem_base_addr")
        if base_addr < 0:
            base_addr = 0
            dpg.set_value("mem_base_addr", base_addr)

        for i in range(16):
            addr = i + base_addr

            val = read_signal(cls.dut.MEM_DATA.ram[addr], signed=True)
            dpg.set_value(f"mem_p_{i}", f"[{addr:04d}]")
            dpg.set_value(f"mem_{i}", format_hex(val) + f" ({val})")

    @classmethod
    def update_bitmap(cls):
        base_addr = dpg.get_value("BM_base_addr")

        if base_addr < 0:
            base_addr = 0
            dpg.set_value("BM_base_addr", base_addr)

        for y in range(cls.BM_grid_h):
            for x in range(cls.BM_grid_w):
                addr = base_addr + (y * cls.BM_grid_w + x)
                
                val = read_signal(cls.dut.MEM_DATA.ram[addr])
                
                r = (val >> 16) & 0xFF
                g = (val >> 8) & 0xFF
                b = val & 0xFF
                
                dpg.configure_item(f"px_{x}_{y}", fill=[r, g, b, 255])

    @classmethod
    def update(cls, cycle):
        pc_val = read_signal(cls.dut.PC.Q)
        inst_val = read_signal(cls.dut.Instruction)
        dpg.set_value("cpu_info", f"Cycle: {cycle} | PC: {format_hex(pc_val)} | Instruction: {format_bin(inst_val)}")

        # update reg file
        cls.update_reg_file()

        # update mem data
        cls.update_mem_dmp()

        # update bitmap display
        cls.update_bitmap()

    @staticmethod
    def render():
        dpg.render_dearpygui_frame()

    @staticmethod
    def destroy():
        dpg.destroy_context()

    @staticmethod
    def running():
        return dpg.is_dearpygui_running()
