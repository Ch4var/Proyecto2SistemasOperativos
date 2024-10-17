import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random, colorsys 
from algoritmos2 import procesar_archivo_o_generar_procesos, ejecutar_simulacion

class PaginacionSimulacionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Paginación")
        width = self.root.winfo_screenwidth()               
        height = self.root.winfo_screenheight() 
        #self.root.geometry("1200x1000")
        self.root.geometry("%dx%d" % (width, height))

        self.label_titulo = tk.Label(self.root, text="Simulador de paginación", font=('Arial', 18))
        self.label_titulo.pack(padx=20, pady=10)

        self.seed_var = tk.StringVar()
        self.algorithm_var = tk.StringVar()
        self.process_count_var = tk.IntVar(value=10)
        self.operations_count_var = tk.IntVar(value=500)
        self.file_path_var = tk.StringVar()

        self.simulation_running = False
        self.simulation_paused = False

        self.pagina_inicial()

    def pagina_inicial(self):

        tk.Label(self.root, text="Semilla para random:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.seed_var).pack(pady=5)

        tk.Label(self.root, text="Algoritmo de paginación:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.algorithm_var, values=["FIFO", "SC", "MRU", "RND"]).pack(pady=5)

        tk.Label(self.root, text="Archivo de operaciones (opcional):").pack(pady=5)
        tk.Entry(self.root, textvariable=self.file_path_var).pack(padx=5)
        tk.Button(self.root, text="Seleccionar archivo", command=self.select_file).pack(pady=5)

        tk.Label(self.root, text="Número de procesos a simular P:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.process_count_var, values=[10, 50, 100]).pack(pady=5)

        tk.Label(self.root, text="Cantidad de operaciones N:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.operations_count_var, values=[500, 1000, 5000]).pack(pady=5)

        self.descargar_bandera = 0

        tk.Button(self.root, text="Descargar archivo", command=self.descargar_archivo).pack(pady=20)

        tk.Button(self.root, text="Iniciar Simulación", command=self.iniciar_simulacion).pack(pady=20)

    def descargar_archivo(self): 

        self.descargar_bandera = 1
        self.operaciones = procesar_archivo_o_generar_procesos(None, self.process_count_var.get(), self.operations_count_var.get())

        with open("archivo_salida.txt", 'w') as f:
            for operacion in self.operaciones:
                f.write(f"{operacion}\n")
    
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if file_path:
            self.file_path_var.set(file_path)
    
    def generate_distinct_colors(self):
        colors_hex = [] 
        for i in range(self.tamcolores):
            # Generar un color en HSL
            hue = i / self.tamcolores  # matices espaciados uniformemente
            lightness = 0.8  # brillo fijo
            saturation = 1.0  # saturación total
            rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
            rgb = tuple(int(c * 255) for c in rgb)
            
            # Convertir el RGB en formato hexadecimal
            hex_color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
            
            colors_hex.append(hex_color)
    
        return colors_hex
    
    def create_simulation_widgets(self, algoritmo):

        self.visual_frame = tk.Frame(self.sim_window)
        self.visual_frame.pack(padx=10, pady=10, fill="both", expand=True)
 
        self.tamcolores = 100 
        distinct_colors = self.generate_distinct_colors()

        self.proceso_colores = {}
        for pid in range(self.tamcolores):
            self.proceso_colores[pid] = distinct_colors[pid]

        ram_label_opt = ttk.Label(self.visual_frame, text="RAM - OPT", font=('Arial', 10, 'bold'))
        ram_label_opt.pack(pady=5)

        self.ram_canvas_opt = tk.Canvas(self.visual_frame, width=700, height=15)
        self.ram_canvas_opt.pack(pady=5)
        
        for i in range(100): 
            color = "white" 
            self.ram_canvas_opt.create_rectangle(i*7, 0, (i+1)*7, 20, fill=color, outline="black")

        if algoritmo == "FIFO":
            texto = "RAM - [FIFO]"
        elif algoritmo == "MRU":
            texto = "RAM - [MRU]"
        elif algoritmo == "SC":
            texto = "RAM - [SC]" 
        elif algoritmo == "RND":
            texto = "RAM - [RND]"

        ram_label_alg = ttk.Label(self.visual_frame, text=texto, font=('Arial', 10, 'bold'))
        ram_label_alg.pack(pady=5)

        self.ram_canvas_alg = tk.Canvas(self.visual_frame, width=700, height=15)
        self.ram_canvas_alg.pack(pady=5)
        
        for i in range(100):
            color = "white"
            self.ram_canvas_alg.create_rectangle(i*7, 0, (i+1)*7, 20, fill=color, outline="black")

        buttons_frame = tk.Frame(self.sim_window)
        buttons_frame.pack(pady=2)

        self.pause_button = tk.Button(buttons_frame, text="Pausar", command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=10)  

        self.tabla_opt = self.create_mmu_table("OPT")
        self.tabla_alg = self.create_mmu_table(algoritmo)

        self.create_statistics_widgets()

    def actualizar_canvas_ram_opt(self, ram_state):
        num_blocks = len(self.ram_canvas_opt.find_all()) 
        num_pages = len(ram_state) 

        for i in range(num_blocks):
            if i < num_pages and ram_state[i] is not None:
                pid = ram_state[i].pid 
                color = self.proceso_colores.get(pid % self.tamcolores, "white")  
            else:
                color = "white" 

            self.ram_canvas_opt.itemconfig(i + 1, fill=color)  

    def update_mmu_table_opt(self, ram_state, virtual_state):
        for item in self.tabla_opt.get_children():
            self.tabla_opt.delete(item)

        combined_state = ram_state + virtual_state
        combined_state.sort(key=lambda page: page.pid)

        for page in combined_state:
            _, page_num = map(int, page.page_id.split('-'))
            page_id = page_num
            pid = page.pid
            in_ram = "X" if page.in_ram else ""
            l_addr = page.l_addr
            m_addr = page.m_addr
            d_addr = page.d_addr
            l_time = page.l_time
            flag = "X" if page.flag else ""

            row_id = self.tabla_opt.insert('', tk.END, values=(page_id, pid, in_ram, l_addr, m_addr, d_addr, l_time, flag))
            color = self.proceso_colores.get(pid % self.tamcolores, "white")
            self.tabla_opt.item(row_id, tags=(pid,))
            self.tabla_opt.tag_configure(pid, background=color)

    def actualizar_canvas_ram(self, ram_state):
        num_blocks = len(self.ram_canvas_alg.find_all()) 
        num_pages = len(ram_state) 

        for i in range(num_blocks):
            if i < num_pages and ram_state[i] is not None:
                pid = ram_state[i].pid 
                color = self.proceso_colores.get(pid % self.tamcolores, "white")  
            else:
                color = "white" 

            self.ram_canvas_alg.itemconfig(i + 1, fill=color)  

    def update_mmu_table(self, ram_state, virtual_state):
        for item in self.tabla_alg.get_children():
            self.tabla_alg.delete(item)

        combined_state = ram_state + virtual_state
        combined_state.sort(key=lambda page: page.pid)

        for page in combined_state:
            _, page_num = map(int, page.page_id.split('-'))
            page_id = page_num
            pid = page.pid
            in_ram = "X" if page.in_ram else ""
            l_addr = page.l_addr
            m_addr = page.m_addr
            d_addr = page.d_addr
            l_time = page.l_time
            flag = "X" if page.flag else ""

            row_id = self.tabla_alg.insert('', tk.END, values=(page_id, pid, in_ram, l_addr, m_addr, d_addr, l_time, flag))
            color = self.proceso_colores.get(pid % self.tamcolores, "white")
            self.tabla_alg.item(row_id, tags=(pid,))
            self.tabla_alg.tag_configure(pid, background=color)

    def create_mmu_table(self, alg_name):

        table_frame = tk.Frame(self.visual_frame)
        table_frame.pack(side="left", padx=10, pady=5)

        table_label = tk.Label(table_frame, text=f"MMU - {alg_name}", font=('Arial', 12, 'bold'))
        table_label.pack()

        # Frame contenedor para la tabla y el scrollbar
        table_container = tk.Frame(table_frame)
        table_container.pack(fill="both", expand=True)

        columns = ("PAGE ID", "PID", "LOADED", "L-ADDR", "M-ADDR", "D-ADDR", "LOADED-T", "MARK")
        table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        table.pack(fill="both", expand=True)

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=80)

        return table

    def create_statistics_widgets(self):
        stats_frame = tk.Frame(self.sim_window)
        stats_frame.pack(padx=10, pady=5, fill="x")

        # Sección de estadísticas del algoritmo óptimo
        optimal_algo_frame = tk.Frame(stats_frame)
        optimal_algo_frame.grid(row=0, column=0, padx=10, pady=2)

        tk.Label(optimal_algo_frame, text="Algoritmo Óptimo").grid(row=0, column=0, padx=5, pady=2, columnspan=4)

        # Tabla de estadísticas del algoritmo óptimo
        opt_stats_frame = tk.Frame(optimal_algo_frame)
        opt_stats_frame.grid(row=1, column=0, padx=10, pady=2)

        tk.Label(opt_stats_frame, text="Processes").grid(row=0, column=0, padx=5, pady=2)
        tk.Label(opt_stats_frame, text="Sim-Time").grid(row=0, column=1, padx=5, pady=2)

        self.opt_processes_label = tk.Label(opt_stats_frame, text="0")
        self.opt_processes_label.grid(row=1, column=0, padx=5, pady=2)
        
        self.opt_sim_time_label = tk.Label(opt_stats_frame, text="0s")
        self.opt_sim_time_label.grid(row=1, column=1, padx=5, pady=2)

        # Tabla de RAM y V-RAM del algoritmo óptimo
        self.opt_memory_frame = tk.Frame(optimal_algo_frame)
        self.opt_memory_frame.grid(row=2, column=0, padx=10, pady=2)

        tk.Label(self.opt_memory_frame, text="RAM KB").grid(row=0, column=0, padx=5, pady=2)
        tk.Label(self.opt_memory_frame, text="RAM %").grid(row=0, column=1, padx=5, pady=2)
        tk.Label(self.opt_memory_frame, text="V-RAM KB").grid(row=0, column=2, padx=5, pady=2)
        tk.Label(self.opt_memory_frame, text="V-RAM %").grid(row=0, column=3, padx=5, pady=2)

        self.opt_ram_kb_label = tk.Label(self.opt_memory_frame, text="0 KB")
        self.opt_ram_kb_label.grid(row=1, column=0, padx=5, pady=2)

        self.opt_ram_percent_label = tk.Label(self.opt_memory_frame, text="0%")
        self.opt_ram_percent_label.grid(row=1, column=1, padx=5, pady=2)

        self.opt_vram_kb_label = tk.Label(self.opt_memory_frame, text="0 KB")
        self.opt_vram_kb_label.grid(row=1, column=2, padx=5, pady=2)

        self.opt_vram_percent_label = tk.Label(self.opt_memory_frame, text="0%")
        self.opt_vram_percent_label.grid(row=1, column=3, padx=5, pady=2)

        # Tabla de páginas, thrashing y fragmentación del algoritmo seleccionado
        opt_pages_frame = tk.Frame(optimal_algo_frame)
        opt_pages_frame.grid(row=3, column=0, padx=10, pady=2)

        tk.Label(opt_pages_frame, text="PAGES").grid(row=0, column=0, padx=5, pady=2)
        tk.Label(opt_pages_frame, text="Thrashing").grid(row=0, column=2, padx=5, pady=2)
        tk.Label(opt_pages_frame, text="Fragmentación").grid(row=0, column=3, padx=5, pady=2)

        tk.Label(opt_pages_frame, text="LOADED").grid(row=1, column=0, padx=5, pady=2)
        tk.Label(opt_pages_frame, text="UNLOADED").grid(row=1, column=1, padx=5, pady=2)

        self.opt_pages_loaded_label = tk.Label(opt_pages_frame, text="0")
        self.opt_pages_loaded_label.grid(row=2, column=0, padx=5, pady=2)

        self.opt_pages_unloaded_label = tk.Label(opt_pages_frame, text="0")
        self.opt_pages_unloaded_label.grid(row=2, column=1, padx=5, pady=2)

        self.opt_thrashing_label = tk.Label(opt_pages_frame, text="0s (0%)", bg="white")
        self.opt_thrashing_label.grid(row=2, column=2, padx=5, pady=2)

        self.opt_fragmentation_label = tk.Label(opt_pages_frame, text="0 KB")
        self.opt_fragmentation_label.grid(row=2, column=3, padx=5, pady=2)

        # Sección de estadísticas del algoritmo seleccionado
        selected_algo_frame = tk.Frame(stats_frame)
        selected_algo_frame.grid(row=0, column=1, padx=10, pady=2)

        tk.Label(selected_algo_frame, text=f"Algoritmo {self.algorithm_var.get()}").grid(row=0, column=0, padx=5, pady=2, columnspan=4)

        # Tabla de procesos y tiempo de simulación del algoritmo seleccionado
        processes_frame = tk.Frame(selected_algo_frame)
        processes_frame.grid(row=1, column=0, padx=10, pady=2)

        tk.Label(processes_frame, text="Processes").grid(row=0, column=0, padx=5, pady=2)
        tk.Label(processes_frame, text="Sim-Time").grid(row=0, column=1, padx=5, pady=2)

        self.processes_label = tk.Label(processes_frame, text="0")
        self.processes_label.grid(row=1, column=0, padx=5, pady=2)
        
        self.sim_time_label = tk.Label(processes_frame, text="0s")
        self.sim_time_label.grid(row=1, column=1, padx=5, pady=2)

        # Tabla de RAM y V-RAM del algoritmo seleccionado
        memory_frame = tk.Frame(selected_algo_frame)
        memory_frame.grid(row=2, column=0, padx=10, pady=2)

        tk.Label(memory_frame, text="RAM KB").grid(row=0, column=0, padx=5, pady=2)
        tk.Label(memory_frame, text="RAM %").grid(row=0, column=1, padx=5, pady=2)
        tk.Label(memory_frame, text="V-RAM KB").grid(row=0, column=2, padx=5, pady=2)
        tk.Label(memory_frame, text="V-RAM %").grid(row=0, column=3, padx=5, pady=2)

        self.ram_kb_label = tk.Label(memory_frame, text="0 KB")
        self.ram_kb_label.grid(row=1, column=0, padx=5, pady=2)

        self.ram_percent_label = tk.Label(memory_frame, text="0%")
        self.ram_percent_label.grid(row=1, column=1, padx=5, pady=2)

        self.vram_kb_label = tk.Label(memory_frame, text="0 KB")
        self.vram_kb_label.grid(row=1, column=2, padx=5, pady=2)

        self.vram_percent_label = tk.Label(memory_frame, text="0%")
        self.vram_percent_label.grid(row=1, column=3, padx=5, pady=2)

        # Tabla de páginas, thrashing y fragmentación del algoritmo seleccionado
        pages_frame = tk.Frame(selected_algo_frame)
        pages_frame.grid(row=3, column=0, padx=10, pady=2)

        tk.Label(pages_frame, text="PAGES").grid(row=0, column=0, padx=5, pady=2)
        tk.Label(pages_frame, text="Thrashing").grid(row=0, column=2, padx=5, pady=2)
        tk.Label(pages_frame, text="Fragmentación").grid(row=0, column=3, padx=5, pady=2)

        tk.Label(pages_frame, text="LOADED").grid(row=1, column=0, padx=5, pady=2)
        tk.Label(pages_frame, text="UNLOADED").grid(row=1, column=1, padx=5, pady=2)

        self.pages_loaded_label = tk.Label(pages_frame, text="0")
        self.pages_loaded_label.grid(row=2, column=0, padx=5, pady=2)

        self.pages_unloaded_label = tk.Label(pages_frame, text="0")
        self.pages_unloaded_label.grid(row=2, column=1, padx=5, pady=2)

        self.thrashing_label = tk.Label(pages_frame, text="0s (0%)", bg="white")
        self.thrashing_label.grid(row=2, column=2, padx=5, pady=2)

        self.fragmentation_label = tk.Label(pages_frame, text="0 KB")
        self.fragmentation_label.grid(row=2, column=3, padx=5, pady=2)

    def toggle_pause(self):
        if self.simulation_paused:
            self.simulation_paused = False
            self.pause_button.config(text="Pausar")
        else:
            self.simulation_paused = True
            self.pause_button.config(text="Reanudar")

    def stop_simulation(self):
        self.simulation_running = False

    def iniciar_simulacion(self):
        if not self.seed_var.get().isdigit() or self.algorithm_var.get() not in ["FIFO", "SC", "MRU", "RND"]:
            messagebox.showerror("Error", "Valores de entrada inválidos")
            return

        semilla = int(self.seed_var.get())
        random.seed(semilla)

        algoritmo = self.algorithm_var.get()

        if self.descargar_bandera == 0:
            if self.file_path_var.get():
                self.operaciones = procesar_archivo_o_generar_procesos(self.file_path_var.get(), self.process_count_var.get(), self.operations_count_var.get())
            else:
                self.operaciones = procesar_archivo_o_generar_procesos(None, self.process_count_var.get(), self.operations_count_var.get())

        self.sim_window = tk.Toplevel(self.root)
        self.sim_window.title("Simulación en Progreso")
        width = self.sim_window.winfo_screenwidth()               
        height = self.sim_window.winfo_screenheight() 
        self.sim_window.geometry("%dx%d" % (width, height))

        self.simulation_running = True
        self.simulation_paused = False

        self.create_simulation_widgets(algoritmo)

        self.simulation_data = {
            "algoritmo": algoritmo,
            "operaciones": self.operaciones,
            "sim_step": ejecutar_simulacion(algoritmo, self.operaciones) 
        }

        # Iniciar el bucle de simulación usando after()
        self.run_simulation_step()

    def run_simulation_step(self):
        if not self.simulation_running:
            return  # Si se ha detenido la simulación, salimos de la función

        if self.simulation_paused:
            # Si está pausado, programamos la función para que se ejecute de nuevo después de 100 ms
            self.sim_window.after(100, self.run_simulation_step)
            return

        try:
            # Obtener el siguiente paso de la simulación
            step_data, estado_simulacion_opt  = next(self.simulation_data['sim_step'])
        except StopIteration:
            # La simulación ha terminado
            self.simulation_running = False
            return

        self.processes_label.config(text=f"{step_data['processes_running']}")
        self.sim_time_label.config(text=f"{step_data['total_simulation_time']}s")

        self.ram_kb_label.config(text=f"{step_data['ram_usage'] / 1000:.2f} KB")
        self.ram_percent_label.config(text=f"{step_data['ram_usage'] / 400000 * 100:.2f}%")

        self.vram_kb_label.config(text=f"{step_data['vram_usage'] / 1000:.2f} KB")
        self.vram_percent_label.config(text=f"{step_data['vram_usage'] / 400000 * 100:.2f}%")

        self.pages_loaded_label.config(text=f"{step_data['pages_loaded']}")
        self.pages_unloaded_label.config(text=f"{step_data['pages_unloaded']}")

        thrashing_percentage = (step_data['thrashing_time'] / step_data['total_simulation_time'] * 100) if step_data['total_simulation_time'] > 0 else 0
        self.thrashing_label.config(text=f"{step_data['thrashing_time']}s ({thrashing_percentage:.2f}%)")
        if thrashing_percentage > 50:
            self.thrashing_label.config(bg="red")
        else:
            self.thrashing_label.config(bg="white")

        self.fragmentation_label.config(text=f"{step_data['fragmentation'] / 1000:.2f} KB")

        self.actualizar_canvas_ram(step_data['ram_state'])

        self.update_mmu_table(step_data['ram_state'], step_data['virtual_state'])

        self.opt_processes_label.config(text=f"{estado_simulacion_opt['processes_running']}")
        self.opt_sim_time_label.config(text=f"{estado_simulacion_opt['total_simulation_time']}s")

        self.opt_ram_kb_label.config(text=f"{estado_simulacion_opt['ram_usage'] / 1000:.2f} KB")
        self.opt_ram_percent_label.config(text=f"{estado_simulacion_opt['ram_usage'] / 400000 * 100:.2f}%")

        self.opt_vram_kb_label.config(text=f"{estado_simulacion_opt['vram_usage'] / 1000:.2f} KB")
        self.opt_vram_percent_label.config(text=f"{estado_simulacion_opt['vram_usage'] / 400000 * 100:.2f}%")

        self.opt_pages_loaded_label.config(text=f"{estado_simulacion_opt['pages_loaded']}")
        self.opt_pages_unloaded_label.config(text=f"{estado_simulacion_opt['pages_unloaded']}")

        thrashing_percentage_opt = (estado_simulacion_opt['thrashing_time'] / estado_simulacion_opt['total_simulation_time'] * 100) if estado_simulacion_opt['total_simulation_time'] > 0 else 0
        self.opt_thrashing_label.config(text=f"{estado_simulacion_opt['thrashing_time']}s ({thrashing_percentage_opt:.2f}%)")
        if thrashing_percentage_opt > 50:
            self.opt_thrashing_label.config(bg="red")
        else:
            self.opt_thrashing_label.config(bg="white")

        self.opt_fragmentation_label.config(text=f"{estado_simulacion_opt['fragmentation'] / 1000:.2f} KB")

        # Actualizar el estado de RAM y la tabla MMU del algoritmo óptimo
        self.actualizar_canvas_ram_opt(estado_simulacion_opt['ram_state'])
        self.update_mmu_table_opt(estado_simulacion_opt['ram_state'], estado_simulacion_opt['virtual_state'])

        self.sim_window.after(100, self.run_simulation_step)

    def pause_simulation(self):
        self.simulation_paused = True

    def resume_simulation(self):
        self.simulation_paused = False
        self.run_simulation_step()

if __name__ == "__main__":
    root = tk.Tk()
    app = PaginacionSimulacionApp(root)
    root.mainloop()