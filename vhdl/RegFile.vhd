library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity RegFile is
    generic (
        N : integer := 32; -- data size
        ADDR_WIDTH : integer := 5  -- address length
    );
    port (
        clock, load_en      : in std_logic;
        D_in                : in std_logic_vector(N-1 downto 0);  -- data in
        A_sel, B_sel, D_sel : in std_logic_vector(ADDR_WIDTH-1 downto 0);  -- register address
        A, B                : out std_logic_vector(N-1 downto 0)  -- data out
    );
end RegFile;

architecture arch of RegFile is
    constant M : integer := 2 ** ADDR_WIDTH;

    type reg_array is array (0 to M-1) of std_logic_vector(N-1 downto 0);
    signal s_Reg : reg_array := (others => (others => '0'));

begin
    -- data out
    A <= s_Reg(to_integer(unsigned(A_sel)));
    B <= s_Reg(to_integer(unsigned(B_sel)));

    -- data in
    process(clock)
    begin
        if rising_edge(clock) then
            if load_en = '1' then
                s_Reg(to_integer(unsigned(D_sel))) <= D_in;
            end if;
        end if;
    end process;

end arch;
