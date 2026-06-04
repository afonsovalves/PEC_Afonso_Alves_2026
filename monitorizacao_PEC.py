import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import re
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
MAX_SAMPLES = 100
BAUD_RATE = 9600
x_data = deque(maxlen=MAX_SAMPLES)
y1_data = deque(maxlen=MAX_SAMPLES)
y2_data = deque(maxlen=MAX_SAMPLES)
y3_data = deque(maxlen=MAX_SAMPLES)
for _ in range(MAX_SAMPLES):
    x_data.append(0)
    y1_data.append(0)
    y2_data.append(0)
    y3_data.append(0)
amostra_atual = 0
peso_total_atual = "--"
porta_serial = None
a_ler = False
def procurar_portas():
    """Atualiza a combobox com as portas COM disponíveis."""
    portas = [port.device for port in serial.tools.list_ports.comports()]
    combo_portas['values'] = portas
    if portas:
        combo_portas.current(0)
    else:
        combo_portas.set("Nenhuma porta encontrada")
def alternar_conexao():
    """Liga ou desliga a conexão Serial com o Arduino."""
    global porta_serial, a_ler
    if btn_conectar["text"] == "► Conectar":
        porta_selecionada = combo_portas.get()
        if not porta_selecionada or porta_selecionada == "Nenhuma porta encontrada":
            messagebox.showwarning("Aviso", "Selecione uma porta COM válida.")
            return 
        try:
            porta_serial = serial.Serial(porta_selecionada, BAUD_RATE, timeout=1)
            a_ler = True
            btn_conectar.config(text="■ Desconectar")
            combo_portas.config(state="disabled")
            btn_atualizar.config(state="disabled")
            thread = threading.Thread(target=ler_dados_serial, daemon=True)
            thread.start()
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível abrir a porta {porta_selecionada}.\n{e}")
    else:
        a_ler = False
        if porta_serial and porta_serial.is_open:
            porta_serial.close()
        btn_conectar.config(text="► Conectar")
        combo_portas.config(state="readonly")
        btn_atualizar.config(state="normal")
def ler_dados_serial():
    """Lê os dados da porta serial continuamente (executado numa Thread separada)."""
    global amostra_atual, peso_total_atual
    padrao = re.compile(r"C1:\s*([-\d.]+)\s*\|\s*C2:\s*([-\d.]+)\s*\|\s*C3:\s*([-\d.]+)\s*\|\|\s*TOTAL:\s*([-\d.]+)")
    while a_ler and porta_serial.is_open:
        try:
            linha = porta_serial.readline().decode('utf-8', errors='ignore').strip()
            if linha:
                match = padrao.search(linha)
                if match:
                    c1 = float(match.group(1)) 
                    c2 = float(match.group(2)) 
                    c3 = float(match.group(3))
                    total = match.group(4)
                    amostra_atual += 1
                    x_data.append(amostra_atual)
                    y1_data.append(c1)
                    y2_data.append(c2)
                    y3_data.append(c3)
                    peso_total_atual = total
        except Exception as e:
            print(f"Erro na leitura: {e}")
            break
def atualizar_interface(frame):
    """Função chamada pelo FuncAnimation para atualizar o gráfico e as labels."""
    linha_c1.set_data(range(MAX_SAMPLES), list(y1_data))
    linha_c2.set_data(range(MAX_SAMPLES), list(y2_data))
    linha_c3.set_data(range(MAX_SAMPLES), list(y3_data))
    todos_y = list(y1_data) + list(y2_data) + list(y3_data)
    min_y = min(todos_y)
    max_y = max(todos_y)  
    if max_y < 50 and min_y > -10:
        ax.set_ylim(-10, 50)
    else:
        ax.set_ylim(min_y - 10, max_y + 10)
    lbl_peso.config(text=f"Peso do Objeto: {peso_total_atual} unidades")  
    return linha_c1, linha_c2, linha_c3
root = tk.Tk()
root.title("Dashboard - Manipulador Hipersensorizado")
root.geometry("1200x800")
root.configure(bg="#F0F0F0")
frame_top = tk.Frame(root, bg="#F0F0F0", pady=10, padx=10)
frame_top.pack(fill=tk.X)
tk.Label(frame_top, text="Porta COM:", bg="#F0F0F0").pack(side=tk.LEFT, padx=(0, 5))
combo_portas = ttk.Combobox(frame_top, state="readonly", width=15)
combo_portas.pack(side=tk.LEFT, padx=5)
btn_atualizar = ttk.Button(frame_top, text="↻ Atualizar Portas", command=procurar_portas)
btn_atualizar.pack(side=tk.LEFT, padx=5)
btn_conectar = ttk.Button(frame_top, text="► Conectar", command=alternar_conexao)
btn_conectar.pack(side=tk.LEFT, padx=10)
frame_info = tk.Frame(root, bg="#F0F0F0", pady=10, padx=20)
frame_info.pack(fill=tk.X)
lbl_peso = tk.Label(frame_info, text="Peso do Objeto: -- unidades", fg="red", font=("Arial", 12, "bold"), bg="#F0F0F0")
lbl_peso.pack(side=tk.RIGHT) # Podes mudar para tk.LEFT se preferires o peso à esquerda
fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
fig.patch.set_facecolor('#F0F0F0')
ax.set_title("Deformação das Células de Carga em Tempo Real")
ax.set_xlabel("Amostras")
ax.set_ylabel("Torque / Força Lida")
ax.set_xlim(0, MAX_SAMPLES)
ax.set_ylim(-10, 50)
ax.grid(True)
linha_c1, = ax.plot([], [], 'r-', label="Célula 1 (T1)")
linha_c2, = ax.plot([], [], 'g-', label="Célula 2 (T2)")
linha_c3, = ax.plot([], [], 'b-', label="Célula 3 (T3)")
ax.legend(loc="upper left")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
ani = animation.FuncAnimation(fig, atualizar_interface, interval=100, blit=False, save_count=MAX_SAMPLES)
procurar_portas()
def ao_fechar():
    global a_ler
    a_ler = False
    if porta_serial and porta_serial.is_open:
        porta_serial.close()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", ao_fechar)
root.mainloop()