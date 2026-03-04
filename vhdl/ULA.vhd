library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity ULA is
    generic (N : integer := 32);
    port (
        A, B : in std_logic_vector(N-1 downto 0);
        GS   : in std_logic_vector(5 downto 0);
        Z    : out std_logic; -- zero
        S    : out std_logic_vector(N-1 downto 0)
    );
end ULA;

architecture arch of ULA is
    signal A_int, B_int : std_logic_vector(N-1 downto 0);
    signal soma_out : std_logic_vector(N-1 downto 0);
    signal mult_out : std_logic_vector((2*N)-1 downto 0);
    signal result : std_logic_vector(N-1 downto 0);

begin
    ADDER : entity work.Adder
        generic map (N => N)
        port map (
            A => A_int,
            B => B_int,
            S => soma_out,
            Cout => open
        );

    MULTIPLIER : entity work.MultMatricial
        generic map (N => N)
        port map (
            A => A_int,
            B => B_int,
            S => mult_out
        );

    -- CONTROL UNIT
    process(A, B, GS, soma_out, mult_out)
    begin
        -- default values
        A_int <= (others => '0');
        B_int <= (others => '0');
        result <= (others => '0');

        case GS is
            -- MOV A
            when "000000" =>
                result <= A;

            -- MOV B
            when "000001" =>
                result <= B;

            -- ADD | A + B
            when "000010" =>
                A_int <= A;
                B_int <= B;
                result <= soma_out;

            -- SUB | A - B  → A + (~B + 1)
            when "000011" =>
                A_int <= A;
                B_int <= std_logic_vector(not unsigned(B) + 1);
                result <= soma_out;

            -- INC | A + 1
            when "000100" =>
                A_int <= A;
                B_int <= (others => '0');
                B_int(0) <= '1';
                result <= soma_out;

            -- DEC | A - 1
            when "000101" =>
                A_int <= A;
                B_int <= (others => '1');
                result <= soma_out;

            -- Logic:
            when "000110" => result <= not A;   -- NOT A
            when "000111" => result <= A and B; -- A AND B
            when "001000" => result <= A or B;  -- A OR B
            when "001001" => result <= A xor B; -- A XOR B

            -- Shift
            when "001010" => result <= B(N-2 downto 0) & '0'; -- SLL B
            when "001011" => result <= '0' & B(N-1 downto 1); -- SRL B

            -- MUL | A * B
            when "001100" =>
                A_int <= A;
                B_int <= B;
                result <= mult_out(N-1 downto 0);

            when others => result <= (others => '0');
        end case;
    end process;
    
    -- OUT
    S <= result;
    
    -- FLAGS
    Z <= '1' when unsigned(result) = 0 else '0';
    
end arch;
