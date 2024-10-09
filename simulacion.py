import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random

class PaginacionSimulacionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Paginación - Sistemas Operativos")
        self.root.geometry("800x600")

        self.label_titulo = tk.Label(self.root, text="Simulador de paginación", font=('Arial', 18))
        self.label_titulo.pack(padx=20, pady=10)
        
        # Variables para los parámetros
        self.seed_var = tk.StringVar()
        self.algorithm_var = tk.StringVar()
        self.process_count_var = tk.IntVar(value=10)
        self.operations_count_var = tk.IntVar(value=500)
        self.file_path_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Semilla para random
        tk.Label(self.root, text="Semilla para random:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.seed_var).pack(pady=5)
        
        # Selección de algoritmo
        tk.Label(self.root, text="Algoritmo de paginación:").pack(pady=5)
        algorithms = ["FIFO", "SC", "MRU", "RND"]
        ttk.Combobox(self.root, textvariable=self.algorithm_var, values=algorithms).pack(pady=5)

        # Archivo para simular
        tk.Label(self.root, text="Archivo de operaciones (opcional):").pack(pady=5)
        tk.Entry(self.root, textvariable=self.file_path_var).pack(padx=5)
        tk.Button(self.root, text="Seleccionar archivo", command=self.select_file).pack(pady=5)
        
        # Número de procesos a simular
        tk.Label(self.root, text="Número de procesos a simular P:").pack(pady=5)
        tk.Label(self.root, text="Se espera un valor de 10, 50 o 100").pack(pady=5)
        num_procesos = [10, 50, 100]
        ttk.Combobox(self.root, textvariable=self.process_count_var, values=num_procesos).pack(pady=5)

        # Número de operaciones a simular
        tk.Label(self.root, text="Cantidad de operaciones N:").pack(pady=5)
        tk.Label(self.root, text="Se espera un valor de 500, 1000 o 5000").pack(pady=5)
        num_operaciones = [500, 1000, 5000]
        ttk.Combobox(self.root, textvariable=self.operations_count_var, values=num_operaciones).pack(pady=5)

        # Botón para iniciar la simulación
        tk.Button(self.root, text="Iniciar Simulación", command=self.start_simulation).pack(pady=20)

    def select_file(self):
        # Permite seleccionar un archivo de operaciones
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if file_path:
            self.file_path_var.set(file_path)

    def start_simulation(self):
        # Verifica los parámetros antes de iniciar la simulación
        if not self.seed_var.get():
            messagebox.showwarning("Advertencia", "Por favor, ingrese una semilla para random.")
            return
        if not self.algorithm_var.get():
            messagebox.showwarning("Advertencia", "Por favor, seleccione un algoritmo de paginación.")
            return
        
        try:
            seed = int(self.seed_var.get())
            random.seed(seed)
        except ValueError:
            messagebox.showerror("Error", "La semilla debe ser un número entero.")
            return

        algorithm = self.algorithm_var.get()
        process_count = self.process_count_var.get()
        operations_count = self.operations_count_var.get()
        file_path = self.file_path_var.get()

       
        messagebox.showinfo("Simulación iniciada", f"Simulación iniciada con el algoritmo {algorithm}.\nProcesos: {process_count}\nOperaciones: {operations_count}")
        

        self.run_simulation(algorithm, process_count, operations_count, file_path)

    def run_simulation(self, algorithm, process_count, operations_count, file_path):

        print(f"Iniciando simulación con {algorithm}, {process_count} procesos, {operations_count} operaciones.")
        if file_path:
            print(f"Usando archivo de operaciones: {file_path}")
        else:
            print("Generando operaciones aleatoriamente.")
        
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PaginacionSimulacionApp(root)
    root.mainloop()
