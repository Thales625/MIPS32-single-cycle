library IEEE;
use IEEE.std_logic_1164.all;

entity Reg is
    generic (N : integer := 16);
    port(
        clock, load, reset : in std_logic;
        D : in std_logic_vector(N-1 downto 0);
        Q : out std_logic_vector(N-1 downto 0) := (others => '0')
    );
end Reg;

architecture arch of Reg is
begin
    process(clock, reset)
    begin
        if reset = '1' then
            Q <= (others => '0');
        elsif rising_edge(clock) then
            if load = '1' then
                Q <= D;
            end if;
        end if;
    end process;
end arch;
