library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity MultMatricial is
    generic (N : integer := 32);
    port (
        A, B : in std_logic_vector(N-1 downto 0);
        S    : out std_logic_vector((2*N)-1 downto 0)
    );
end MultMatricial;

architecture arch of MultMatricial is
    type matriz is array(0 to N-1) of std_logic_vector(N-1 downto 0);
    signal pp : matriz;

    type matriz_soma is array(0 to N-2) of unsigned(N downto 0);
    signal ss : matriz_soma;
begin
    -- gerador dos produtos parciais
    G0: for i in 0 to N-1 generate
        G1: for j in 0 to N-1 generate 
               pp(i)(j) <= A(i) and B(j);
        end generate;
    end generate;

    -- primeiro estagio de soma
    ss(0) <= resize(unsigned('0' & pp(0)(N-1 downto 1)), N+1) + resize(unsigned(pp(1)), N+1);

    -- soma em cascata
    G2: for i in 0 to N-3 generate
        ss(i+1) <= resize(unsigned(ss(i)(N) & ss(i)(N-1 downto 1)), N+1) + resize(unsigned(pp(i+2)), N+1);
    end generate;

    -- roteamento
    S(0) <= pp(0)(0);

    G3: for i in 0 to N-2 generate
        S(i+1) <= std_logic(ss(i)(0));
    end generate;

    G4: for i in 1 to N generate
        S((N-1) + i) <= std_logic(ss(N-2)(i)); 
    end generate;

end arch;
