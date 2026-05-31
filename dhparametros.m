L1 = 10; L2 = 15; L3 = 16; L4 = 3; L5 = 3;
theta_offset = deg2rad(11);
theta1_star = deg2rad(0);
theta2_star = deg2rad(30);
theta3_star = deg2rad(-180);
q1 = theta1_star;
q2 = theta2_star + theta_offset;
q3 = theta3_star + theta_offset + theta2_star;
q4 = theta3_star;
q5 = 0;
theta = [q1, q2, q3, q4, q5];
d     = [L1,  0,  0,  0, -L5];
a     = [0,  L2, L3, L4,  0];
alpha = [pi/2, pi, -pi, -pi/2, 0];
figure('Name', 'DH', 'Color', [0.15 0.15 0.15]);
hold on; grid on; axis equal; view(3);
xlabel('Eixo X', 'Color', 'w'); ylabel('Eixo Y', 'Color', 'w'); zlabel('Eixo Z', 'Color', 'w');
title('Visualização DH', 'Color', 'w');
axis([-15 25 -15 15 0 30]);
set(gca, 'Color', [0.1 0.1 0.1], 'XColor', 'w', 'YColor', 'w', 'ZColor', 'w', 'GridColor', 'w', 'GridAlpha', 0.3);
T_atual = eye(4);     
pos_anterior = [0;0;0]; 
plot3(pos_anterior(1), pos_anterior(2), pos_anterior(3), 'ws', 'MarkerSize', 12, 'MarkerFaceColor', 'w');
escala = 2.5;

for i = 1:5
    th = theta(i); 
    di = d(i); 
    ai = a(i); 
    al = alpha(i);
    T_link = [cos(th), -sin(th)*cos(al),  sin(th)*sin(al), ai*cos(th);
              sin(th),  cos(th)*cos(al), -cos(th)*sin(al), ai*sin(th);
              0,        sin(al),          cos(al),         di;
              0,        0,                0,               1];
    T_atual = T_atual * T_link;
    pos_nova = T_atual(1:3, 4);
    R = T_atual(1:3, 1:3);
    
    plot3([pos_anterior(1) pos_nova(1)], ...
          [pos_anterior(2) pos_nova(2)], ...
          [pos_anterior(3) pos_nova(3)], '-c', 'LineWidth', 5);
          
    plot3(pos_nova(1), pos_nova(2), pos_nova(3), 'o', 'MarkerSize', 8, 'MarkerFaceColor', 'y', 'MarkerEdgeColor', 'w');
    
    quiver3(pos_nova(1), pos_nova(2), pos_nova(3), R(1,1)*escala, R(2,1)*escala, R(3,1)*escala, 'r', 'LineWidth', 2.5, 'MaxHeadSize', 0.5);
    quiver3(pos_nova(1), pos_nova(2), pos_nova(3), R(1,2)*escala, R(2,2)*escala, R(3,2)*escala, 'g', 'LineWidth', 2.5, 'MaxHeadSize', 0.5);
    quiver3(pos_nova(1), pos_nova(2), pos_nova(3), R(1,3)*escala, R(2,3)*escala, R(3,3)*escala, 'b', 'LineWidth', 2.5, 'MaxHeadSize', 0.5);
    
    pos_anterior = pos_nova;
end