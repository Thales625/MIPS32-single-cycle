library IEEE;
use IEEE.std_logic_1164.all;

entity ULA_Operation is
    port (
        funct  : in std_logic_vector(5 downto 0);
        ula_op : in std_logic_vector(5 downto 0);
        GS     : out std_logic_vector(5 downto 0)
    );
end ULA_Operation;

architecture arch of ULA_Operation is
begin
    process(ula_op, funct)
    begin
        GS <= "000000"; -- default value
        
        case ula_op is
            when "000000" => GS <= funct;
            when others   => GS <= ula_op;
        end case;
    end process;
end arch;
