syms th1 th2 th3 th_offset L1 L2 L3 L4 L5
Tabela_Robo = [
    th1,                    pi/2,   0,   L1;
    th2 + th_offset,        pi,     L2,  0;
    th3 + th_offset + th2, -pi,     L3,  0;
    th3,                   -pi/2,   L4,  0;
    0,                      0,      0,  -L5
    ];
Matriz_Transformacao = DH_HTM(Tabela_Robo, 'r');
disp('A Matriz de Transformação Homogénea Final é:');
disp(Matriz_Transformacao);