library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

Entity Processor is
    generic (
        N : integer := 32; -- data size
        ADDR_WIDTH : integer := 5
    );
    port (
        clock : in std_logic;
        reset : in std_logic
    );
end Processor;

architecture arch of Processor is
    signal PC_IN, PC_OUT, PC_plus4, PC_BRANCH : std_logic_vector(N-1 downto 0);
    signal Instruction : std_logic_vector(31 downto 0);
    signal BusB, BusD : std_logic_vector(N-1 downto 0);
    signal RF_A_OUT, RF_B_OUT : std_logic_vector(N-1 downto 0);
    signal RF_SEL_D_IN : std_logic_vector(ADDR_WIDTH-1 downto 0);
    signal ULA_OUT : std_logic_vector(N-1 downto 0);
    signal ULA_GS : std_logic_vector(5 downto 0);
    signal ULA_Z : std_logic;
    signal MEM_D_OUT : std_logic_vector(N-1 downto 0);
    signal PC_SRC : std_logic;
    signal PC_SRC_OUT : std_logic_vector(N-1 downto 0);    

    -- immediate
    signal imm16 : std_logic_vector(15 downto 0);
    signal imm32 : std_logic_vector(N-1 downto 0);
    signal imm32_sl2 : std_logic_vector(N-1 downto 0);

    -- jump
    signal jmp_address : std_logic_vector(N-1 downto 0);
    
    -- control-flags
    signal jump, branch_eq, branch_ne : std_logic;
    signal mem_read, mem_write : std_logic;
    signal reg_dst, reg_write : std_logic;
    signal mem_to_reg : std_logic;
    signal ula_src : std_logic;
    signal ula_op : std_logic_vector(5 downto 0);
begin
    CONTROL_UNIT : entity work.ControlUnit
        port map (
            opcode     => Instruction(31 downto 26),
            jump       => jump,
            branch_eq  => branch_eq,
            branch_ne  => branch_ne,
            mem_read   => mem_read,
            mem_write  => mem_write,
            reg_dst    => reg_dst,
            reg_write  => reg_write,
            mem_to_reg => mem_to_reg,
            ula_src    => ula_src,
            ula_op     => ula_op
        );

    MUX_JMP : entity work.Mux2_1
        generic map (N => N)
        port map (
            A   => PC_SRC_OUT,
            B   => jmp_address,
            sel => jump,
            Y   => PC_IN
        );
        
    MUX_PC_SRC : entity work.Mux2_1
        generic map (N => N)
        port map (
            A   => PC_plus4,
            B   => PC_BRANCH,
            sel => PC_SRC,
            Y   => PC_SRC_OUT
        );
        
    PC_ADDER_BRANCH : entity work.Adder
        generic map (N => N)
        port map (
            A => PC_plus4,
            B => imm32_sl2,
            S => PC_BRANCH
            -- Cout => ignore
        );
        
    PC : entity work.Reg
        generic map (N => 32)
        port map (
            clock => clock,
            load  => '1',
            reset => reset,
            D     => PC_IN,
            Q     => PC_OUT
        );
        
    MEM_INST : entity work.Memoria_Instrucoes
        generic map (ADDR_WIDTH => 8)
        port map (
            endereco  => PC_OUT,
            instrucao => Instruction
        );
    
    MEM_DATA : entity work.Memoria_Dados
        generic map (ADDR_WIDTH => 9)
        port map (
            clk      => clock,
            EscMem   => mem_write,
            LerMem   => mem_read,
            endereco => ULA_OUT,
            dado_in  => RF_B_OUT,
            dado_out => MEM_D_OUT
        );
        
    MUX_D : entity work.Mux2_1
        generic map (N => N)
        port map (
            A   => ULA_OUT,
            B   => MEM_D_OUT,
            sel => mem_to_reg,
            Y   => BusD
        );
    
    MUX_B : entity work.Mux2_1
        generic map (N => N)
        port map (
            A   => RF_B_OUT,
            B   => imm32,
            sel => ula_src,
            Y   => BusB
        );

    MUX_RF_DST : entity work.Mux2_1
        generic map (N => ADDR_WIDTH)
        port map (
            A   => Instruction(20 downto 16),
            B   => Instruction(15 downto 11),
            sel => reg_dst,
            Y   => RF_SEL_D_IN
        );
        
    RF : entity work.RegFile
        generic map (
            N => N,
            ADDR_WIDTH => ADDR_WIDTH
        )
        port map (
            clock   => clock,
            load_en => reg_write,
            D_in    => BusD,
            
            D_sel => RF_SEL_D_IN,
            A_sel => Instruction(25 downto 21),
            B_sel => Instruction(20 downto 16),
            
            A => RF_A_OUT,
            B => RF_B_OUT
        );
        
    ULA_OPERATION : entity work.ULA_Operation
        port map (
            funct  => Instruction(5 downto 0),
            ula_op => ula_op,
            GS     => ULA_GS
        );

    ULA : entity work.ULA
        generic map (N => N)
        port map (
            A  => RF_A_OUT,
            B  => BusB,
            GS => ULA_GS,
            
            Z  => ULA_Z,
            S  => ULA_OUT
        );
     
    -- PC + 4
    PC_plus4 <= std_logic_vector(unsigned(PC_OUT) + 4);

    -- sign extend: 16 to 32 bits
    imm16 <= Instruction(15 downto 0); -- raw immediate (16 bits)
    imm32 <= (31 downto 16 => imm16(15)) & imm16; -- expanded immediate (32 bits)
    imm32_sl2 <= imm32(29 downto 0) & "00"; -- immediate << 2
    
    -- PC SOURCE
    jmp_address <= PC_plus4(31 downto 28) & Instruction(25 downto 0) & "00";
    PC_SRC <= (branch_eq and ULA_Z) or (branch_ne and (not ULA_Z));
end arch;
