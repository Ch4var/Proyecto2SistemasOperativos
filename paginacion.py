import random
import sys

# Parámetros de la simulación
PAGE_SIZE = 4 * 1000  # (4 KB)
RAM_SIZE = 400 * 1000 # (400 KB)
NUM_PAGES = RAM_SIZE // PAGE_SIZE  # Número de páginas en RAM

def print_pages(page_list):
    for page in page_list:
        print(page)

class Page:
    def __init__(self, page_id, pid, frag, l_addr, l_time):
        self.page_id = page_id
        self.pid = pid
        self.in_ram = True  # Indica si la página está en RAM o no
        self.flag = False
        self.frag = frag
        self.l_addr = l_addr
        self.m_addr = None
        self.d_addr = None
        self.l_time = l_time
    
    def __str__(self):
        return f"Page ID: {self.page_id}, Process ID: {self.pid}, In RAM: {self.in_ram}"

class MMU:
    def __init__(self):
        self.real_memory = []  # RAM 
        self.virtual_memory = []  
        self.page_table = {}  
        self.page_counter = 0
        self.ptr_counter = 0
        self.total_frag = 0
        self.total_time = 0
        self.total_thrashing = 0

    def allocate(self, pid, size):
        pass

    def use(self, ptr):
        pass

    def delete(self, ptr):
        if ptr in self.page_table:
            for page in self.page_table[ptr]:
                self.total_frag -= page.frag
                
                if page.in_ram:
                    if page in self.real_memory:
                        self.real_memory.remove(page)
                    
                else:
                    if page in self.virtual_memory:
                        self.virtual_memory.remove(page)

            del self.page_table[ptr]

    def kill(self, pid):
        ptrs_to_remove = [ptr for ptr, pages in self.page_table.items() if pages and pages[0].pid == pid]
        for ptr in ptrs_to_remove:
            self.delete(ptr)

    def status(self):
        # Estado de la memoria
        ram_usage = len(self.real_memory) * PAGE_SIZE
        vram_usage = len(self.virtual_memory) * PAGE_SIZE
        ram_percentage = (ram_usage / RAM_SIZE) * 100
        vram_percentage = (vram_usage / RAM_SIZE) * 100
        print_pages(self.real_memory)
        print(f"RAM: {ram_usage // 1000} KB / {RAM_SIZE // 1000} KB ({ram_percentage:.2f}%)")
        print(f"V-RAM: {vram_usage // 1000} KB ({vram_percentage:.2f}%)")
        print(f"Fragmentación total: {self.total_frag / 1000}KB")
        print(f"Tiempo total de simulacion: {self.total_time} s")
        print(f"Tiempo total de thrashing: {self.total_thrashing} s")

class FIFO(MMU):
    def __init__(self):
        super().__init__()
    
    def allocate(self, pid, size):
        num_pages = (size + PAGE_SIZE - 1) // PAGE_SIZE
        last_page_size = size % PAGE_SIZE if size % PAGE_SIZE != 0 else PAGE_SIZE
        self.ptr_counter += 1
        ptr = self.ptr_counter 
        pages = []

        for i in range(num_pages):
            self.page_counter += 1
            page_id = f"{pid}-{self.page_counter}"
            
            if i == num_pages - 1:
                frag = PAGE_SIZE - last_page_size
            else:
                frag = 0
            
            page = Page(page_id, pid, frag, ptr, self.total_time)
            
            if len(self.real_memory) < NUM_PAGES:
                self.real_memory.append(page)
                page.m_addr = self.real_memory.index(page)
                self.total_time += 1

            else:
                replaced_page = self.real_memory.pop(0)
                replaced_page.in_ram = False
                replaced_page.m_addr = None
                replaced_page.l_time = None
                self.virtual_memory.append(replaced_page)
                replaced_page.d_addr = self.virtual_memory.index(replaced_page)
                self.real_memory.append(page)
                page.m_addr = self.real_memory.index(page)
                self.total_time += 5
                self.total_thrashing += 5

            pages.append(page)

            self.total_frag += frag

        self.page_table[ptr] = pages
        return ptr

    def use(self, ptr):
        if ptr not in self.page_table:
            raise ValueError(f"Pointer {ptr} does not exist in page table.")
        
        pages = self.page_table[ptr]

        for page in pages:
            if page.in_ram:
                self.total_time += 1  # Tiempo de acceso en RAM
            else:
                self.total_time += 5  # Tiempo de acceso en memoria virtual
                self.total_thrashing += 5
                
                if len(self.real_memory) >= NUM_PAGES:
                    evicted_page = self.real_memory.pop(0)
                    evicted_page.in_ram = False
                    evicted_page.m_addr = None
                    evicted_page.l_time = None
                    self.virtual_memory.append(evicted_page)
                    evicted_page.d_addr = self.virtual_memory.index(evicted_page)

                self.real_memory.append(page)
                page.in_ram = True
                page.m_addr = self.real_memory.index(page)
                page.l_time = self.total_time

                for virtual_page in self.virtual_memory:
                    if virtual_page.page_id == page.page_id:
                        self.virtual_memory.remove(virtual_page)
                        break

class SECOND_CHANCE(MMU):
    def __init__(self):
        super().__init__()

    def allocate(self, pid, size):
        num_pages = (size + PAGE_SIZE - 1) // PAGE_SIZE
        last_page_size = size % PAGE_SIZE if size % PAGE_SIZE != 0 else PAGE_SIZE
        self.ptr_counter += 1
        ptr = self.ptr_counter 
        pages = []

        for i in range(num_pages):
            self.page_counter += 1
            page_id = f"{pid}-{self.page_counter}"
            
            if i == num_pages - 1:
                frag = PAGE_SIZE - last_page_size
            else:
                frag = 0
            
            page = Page(page_id, pid, frag, ptr, self.total_time)
            
            if len(self.real_memory) < NUM_PAGES:
                page.in_ram = True
                self.real_memory.append(page)
                page.m_addr = self.real_memory.index(page)
                self.total_time += 1
            else:
                self.replace_page(page)
                page.m_addr = self.real_memory.index(page)
                self.total_time += 5
                self.total_thrashing += 5

            pages.append(page)

            self.total_frag += frag

        self.page_table[ptr] = pages
        return ptr

    def replace_page(self, new_page):
        while True:
            front_page = self.real_memory.pop(0)
            if front_page.flag:  
                front_page.flag = False
                self.real_memory.append(front_page)
                new_page.m_addr = self.real_memory.index(new_page)
            else:
                front_page.in_ram = False
                front_page.m_addr = None
                front_page.l_time = None
                self.virtual_memory.append(front_page) 
                front_page.d_addr = self.virtual_memory.index(front_page)
                new_page.in_ram = True
                self.real_memory.append(new_page)
                new_page.m_addr = self.real_memory.index(new_page)
                break  

    def use(self, ptr):
        if ptr not in self.page_table:
            raise ValueError(f"Pointer {ptr} does not exist in page table.")
        
        pages = self.page_table[ptr]

        for page in pages:
            if page.in_ram:
                self.total_time += 1  
                page.flag = True
            else:
                self.total_time += 5  
                self.total_thrashing += 5
                
                if len(self.real_memory) >= NUM_PAGES:
                    self.replace_page(page)

                page.flag = True
                page.m_addr = self.real_memory.index(page)
                page.l_time = self.total_time

                for virtual_page in self.virtual_memory:
                    if virtual_page.page_id == page.page_id:
                        self.virtual_memory.remove(virtual_page)
                        break

    
class MRU(MMU):
    def __init__(self):
        super().__init__()

    def allocate(self, pid, size):
        num_pages = (size + PAGE_SIZE - 1) // PAGE_SIZE
        last_page_size = size % PAGE_SIZE if size % PAGE_SIZE != 0 else PAGE_SIZE
        self.ptr_counter += 1
        ptr = self.ptr_counter 
        pages = []

        for i in range(num_pages):
            self.page_counter += 1
            page_id = f"{pid}-{self.page_counter}"
            
            if i == num_pages - 1:
                frag = PAGE_SIZE - last_page_size
            else:
                frag = 0
            
            page = Page(page_id, pid, frag, ptr, self.total_time)

            if len(self.real_memory) < NUM_PAGES:
                page.in_ram = True
                self.real_memory.insert(0, page)
                page.m_addr = self.real_memory.index(page)
                self.total_time += 1
            else:
                replaced_page = self.real_memory.pop(0)
                replaced_page.in_ram = False
                replaced_page.m_addr = None
                replaced_page.l_time = None
                self.virtual_memory.append(replaced_page)
                replaced_page.d_addr = self.virtual_memory.index(replaced_page)

                page.in_ram = True
                self.real_memory.insert(0, page)
                page.m_addr = self.real_memory.index(page)

                self.total_time += 5
                self.total_thrashing += 5

            pages.append(page)

            self.total_frag += frag

        self.page_table[ptr] = pages
        return ptr

    def use(self, ptr):
        if ptr not in self.page_table:
            raise ValueError(f"Pointer {ptr} does not exist in page table.")
        
        pages = self.page_table[ptr]

        for page in pages:
            if page.in_ram:
                self.total_time += 1
                self.real_memory.remove(page)
                self.real_memory.insert(0, page)
                page.m_addr = self.real_memory.index(page)
            else:
                self.total_time += 5
                self.total_thrashing += 5

                if len(self.real_memory) >= NUM_PAGES:
                    replaced_page = self.real_memory.pop(0)
                    replaced_page.in_ram = False
                    replaced_page.m_addr = None
                    replaced_page.l_time = None
                    self.virtual_memory.append(replaced_page)
                    replaced_page.d_addr = self.virtual_memory.index(replaced_page)

                self.real_memory.insert(0, page)
                page.in_ram = True
                page.m_addr = self.real_memory.index(page)
                page.l_time = self.total_time

                for virtual_page in self.virtual_memory:
                    if virtual_page.page_id == page.page_id:
                        self.virtual_memory.remove(virtual_page)
                        break
        
    
class RND(MMU):
    def __init__(self):
        super().__init__()

    def allocate(self, pid, size):
        num_pages = (size + PAGE_SIZE - 1) // PAGE_SIZE
        last_page_size = size % PAGE_SIZE if size % PAGE_SIZE != 0 else PAGE_SIZE
        self.ptr_counter += 1
        ptr = self.ptr_counter 
        pages = []

        for i in range(num_pages):
            self.page_counter += 1
            page_id = f"{pid}-{self.page_counter}"
            
            if i == num_pages - 1:
                frag = PAGE_SIZE - last_page_size
            else:
                frag = 0
            
            page = Page(page_id, pid, frag, ptr, self.total_time)

            if len(self.real_memory) < NUM_PAGES:
                page.in_ram = True
                self.real_memory.append(page)
                page.m_addr = self.real_memory.index(page)
                self.total_time += 1
            else:
                replaced_index = random.randint(0, len(self.real_memory) - 1)
                replaced_page = self.real_memory.pop(replaced_index)
                replaced_page.in_ram = False
                replaced_page.m_addr = None
                replaced_page.l_time = None
                self.virtual_memory.append(replaced_page)
                replaced_page.d_addr = self.virtual_memory.index(replaced_page)

                self.real_memory.append(page)
                page.in_ram = True
                page.m_addr = self.real_memory.index(page)

                self.total_time += 5
                self.total_thrashing += 5

            pages.append(page)

            self.total_frag += frag

        self.page_table[ptr] = pages
        return ptr,

    def use(self, ptr):
        if ptr not in self.page_table:
            raise ValueError(f"Pointer {ptr} does not exist in page table.")
        
        pages = self.page_table[ptr]

        for page in pages:
            if page.in_ram:
                self.total_time += 1
            else:
                self.total_time += 5
                self.total_thrashing += 5

                if len(self.real_memory) >= NUM_PAGES:
                    replaced_index = random.randint(0, len(self.real_memory) - 1)
                    replaced_page = self.real_memory.pop(replaced_index)
                    replaced_page.in_ram = False
                    replaced_page.m_addr = None
                    replaced_page.l_time = None
                    self.virtual_memory.append(replaced_page)
                    replaced_page.d_addr = self.virtual_memory.index(replaced_page)

                self.real_memory.append(page)
                page.in_ram = True
                page.m_addr = self.real_memory.index(page)
                page.l_time = self.total_time

                for virtual_page in self.virtual_memory:
                    if virtual_page.page_id == page.page_id:
                        self.virtual_memory.remove(virtual_page)
                        break
        
    
    
def generar_procesos_y_operaciones(P, N):
    procesos = []
    total_ops = 0
    ptr_counter = 0
    while total_ops < N:
        pid = len(procesos) 
        num_ops = random.randint(1, N - total_ops)
        nuevas_operaciones, ptr_counter = generar_operaciones_para_proceso(pid, num_ops, ptr_counter)
        procesos += nuevas_operaciones
        total_ops += len(nuevas_operaciones)
        
    return procesos

def generar_operaciones_para_proceso(pid, num_ops, ptr_counter):
    operaciones = []
    tiene_ptr = False
    kill_realizado = False
    i = 0
    umbral_kill = int(num_ops * 0.8)

    while len(operaciones) < num_ops and not kill_realizado:
        
        if i >= umbral_kill:
            operacion = random.choice(["new", "use", "delete", "kill"])
        else:
            operacion = random.choice(["new", "use"])
        
        if operacion == "new":
            if not kill_realizado:
                size = random.randint(1, 50000)
                ptr_counter += 1
                operaciones.append(f"new({pid}, {size})")
                tiene_ptr = True
        
        elif operacion == "use":
            if tiene_ptr and not kill_realizado:
                ptr = random.randint(1, ptr_counter)
                operaciones.append(f"use({ptr})")
        
        elif operacion == "delete":
            if tiene_ptr and not kill_realizado:
                ptr = random.randint(1, ptr_counter)
                operaciones.append(f"delete({ptr})")
        
        elif operacion == "kill":
            if tiene_ptr and not kill_realizado:
                operaciones.append(f"kill({pid})")
                kill_realizado = True
        i += 1
    return operaciones, ptr_counter

# Función para procesar el archivo de entrada o generar procesos y operaciones
def procesar_archivo_o_generar_procesos(archivo, P, N):
    if archivo:
        with open(archivo, 'r') as f:
            lines = f.readlines()
        operaciones = [line.strip() for line in lines]
        return operaciones
    else:
        return generar_procesos_y_operaciones(P, N)

# Función para ejecutar las operaciones generadas o leídas del archivo
def ejecutar_simulacion(algoritmo, operaciones):
    if algoritmo == "FIFO":
        mmu = FIFO()
    elif algoritmo == "SC":
        mmu = SECOND_CHANCE()
    elif algoritmo == "MRU":
        mmu = MRU()
    elif algoritmo == "RND":
        mmu = RND()
    else:
        raise ValueError("Algoritmo no reconocido")
    
    punteros = {}
    
    
    for operacion in operaciones:
        if "new" in operacion:
            # new(pid, size)
            pid, size = map(int, operacion[4:-1].split(","))
            ptr = mmu.allocate(pid, size)
            punteros[ptr] = pid
            # print(f"Proceso {pid} asignado ptr {ptr} con tamaño {size} KB")

        elif "use" in operacion:
            # use(ptr)
            ptr = int(operacion[4:-1])
            if ptr in punteros:
                mmu.use(ptr)
                # print(f"Usando puntero {ptr}")
            else:
                print(f"Error: puntero {ptr} no existe")

        elif "delete" in operacion:
            # delete(ptr)
            ptr = int(operacion[7:-1])
            if ptr in punteros:
                mmu.delete(ptr)
                # print(f"Eliminado puntero {ptr}")
                del punteros[ptr]
            else:
                print(f"Error: puntero {ptr} no existe o ya ha sido eliminado")

        elif "kill" in operacion:
            # kill(pid)
            pid = int(operacion[5:-1])
            mmu.kill(pid)
            # print(f"Proceso {pid} finalizado")
            punteros = {ptr: p for ptr, p in punteros.items() if p != pid}

    mmu.status()

# Programa principal
def main():
    if len(sys.argv) < 5:
        print("Uso: python main.py <semilla> <algoritmo> <archivo|None> <P> <N>")
        return
    
    # Leer parámetros
    semilla = int(sys.argv[1])
    algoritmo = sys.argv[2]
    archivo = sys.argv[3] if sys.argv[3] != "None" else None
    P = int(sys.argv[4])
    N = int(sys.argv[5])

    archivo_salida = sys.argv[6] if len(sys.argv) > 6 else None

    # Establecer semilla para reproducibilidad
    random.seed(semilla)

    # Obtener la secuencia de operaciones
    operaciones = procesar_archivo_o_generar_procesos(archivo, P, N)

    if archivo_salida:
        with open(archivo_salida, 'w') as f:
            for operacion in operaciones:
                f.write(f"{operacion}\n")
        print(f"Operaciones escritas en {archivo_salida}")

    # print(operaciones)
    # Ejecutar la simulación
    ejecutar_simulacion(algoritmo, operaciones)

if __name__ == "__main__":
    main()