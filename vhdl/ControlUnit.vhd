library IEEE;
use IEEE.std_logic_1164.all;

entity ControlUnit is
    port (
        opcode : in std_logic_vector(5 downto 0);
        
        jump, branch : out std_logic;
        mem_read, mem_write : out std_logic;
        reg_dst, reg_write : out std_logic;
        mem_to_reg : out std_logic;
        ula_src : out std_logic;
        ula_op : out std_logic_vector(5 downto 0)
    );
end ControlUnit;

architecture arch of ControlUnit is
begin
    process(opcode)
    begin
        -- default values
        jump       <= '0';
        branch     <= '0';
        mem_read   <= '0';
        mem_write  <= '0';
        reg_write  <= '0';
        reg_dst    <= '0';
        mem_to_reg <= '0';
        ula_src    <= '0';
        ula_op     <= (others => '0');
        
        case opcode is
            -- R-type
            when "000000" =>
                reg_dst   <= '1';
                reg_write <= '1';
                
            -- I-type
            when "000100" => -- ADDI
                reg_write <= '1';
                ula_src   <= '1';
                ula_op    <= "000010";
                
            when "000101" => -- SUBI
                reg_write <= '1';
                ula_src   <= '1';
                ula_op    <= "000011";
            
            when "000110" => -- LDI
                reg_write <= '1';
                ula_src   <= '1';
                ula_op    <= "000001";

            when "000111" => -- BEQ
                branch <= '1';
                ula_op <= "000011";
            
            when "010000" => -- LW
                mem_read   <= '1';
                reg_write  <= '1';
                mem_to_reg <= '1';
                ula_src    <= '1';
                ula_op     <= "000010";

            when "010001" => -- SW
                mem_write <= '1';
                ula_src   <= '1';
                ula_op    <= "000010";

            when "010010" => -- J
                jump <= '1';

            when others => null;
        end case;
    end process;
end arch;
