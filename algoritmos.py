import random

global_counter = 0

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
                page.d_addr = None
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
                page.d_addr = None
                page.in_ram = True
                page.m_addr = self.real_memory.index(page)
                page.l_time = self.total_time

                self.virtual_memory = [vp for vp in self.virtual_memory if vp.page_id != page.page_id]

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
                page.d_addr = None
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
                front_page.d_addr = None
                front_page.m_addr = self.real_memory.index(front_page)
            else:
                front_page.in_ram = False
                front_page.m_addr = None
                front_page.l_time = None
                self.virtual_memory.append(front_page) 
                front_page.d_addr = self.virtual_memory.index(front_page)

                new_page.in_ram = True
                self.real_memory.append(new_page)
                new_page.d_addr = None
                new_page.m_addr = self.real_memory.index(new_page)
                new_page.l_time = self.total_time
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
                else:
                    page.in_ram = True
                    self.real_memory.append(page)
                    page.m_addr = self.real_memory.index(page)
                    page.d_addr = None

                page.flag = True

                self.virtual_memory = [vp for vp in self.virtual_memory if vp.page_id != page.page_id]
    
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
                page.d_addr = None

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
                page.d_addr = None
                page.in_ram = True
                page.m_addr = self.real_memory.index(page)
                page.l_time = self.total_time

                self.virtual_memory = [vp for vp in self.virtual_memory if vp.page_id != page.page_id]
        
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

                page.in_ram = True
                self.real_memory.append(page)
                page.m_addr = self.real_memory.index(page)
                page.d_addr = None

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
                page.d_addr = None
                page.in_ram = True
                page.m_addr = self.real_memory.index(page)
                page.l_time = self.total_time

                self.virtual_memory = [vp for vp in self.virtual_memory if vp.page_id != page.page_id]

        
class OPT(MMU):
    def __init__(self, future_ops):
        super().__init__()
        self.future_ops = future_ops

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
                self.total_time += 5
                self.total_thrashing += 5

            pages.append(page)
            self.total_frag += frag

        self.page_table[ptr] = pages
        return ptr

    def replace_page(self, page):
        future_uses = self.get_future_uses()
        farthest_page_index = self.get_farthest_page_index(future_uses)
        
        if farthest_page_index is not None:
            replaced_page = self.real_memory.pop(farthest_page_index)
            replaced_page.in_ram = False
            replaced_page.m_addr = None
            replaced_page.l_time = None 
            self.virtual_memory.append(replaced_page)
            replaced_page.d_addr = self.virtual_memory.index(replaced_page) 

            self.real_memory.append(page)
            replaced_page.in_ram = True
            page.m_addr = self.real_memory.index(page)
            page.d_addr = None
        else:
            replaced_page = self.real_memory.pop(0)
            replaced_page.in_ram = False
            replaced_page.m_addr = None
            replaced_page.l_time = None
            self.virtual_memory.append(replaced_page)
            replaced_page.d_addr = self.virtual_memory.index(replaced_page)
            
            self.real_memory.append(page)
            page.in_ram = True
            page.m_addr = self.real_memory.index(page)
            page.l_time = self.total_time
            page.d_addr = None

    def get_future_uses(self):
        future_uses = {}
        for idx, operation in enumerate(self.future_ops):
            if "use" in operation:
                ptr = int(operation[4:-1])
                if ptr in future_uses:
                    future_uses[ptr].append(idx)
                else:
                    future_uses[ptr] = [idx]
        return future_uses
    

    def get_farthest_page_index(self, future_uses):
        farthest_use = global_counter + 1
        farthest_page_index = None
        for index, page in enumerate(self.real_memory):
            pid, page_num = map(int, page.page_id.split('-'))
            ptr = [ptr for ptr, pages in self.page_table.items() if pages and pages[0].pid == pid]
            if ptr and ptr[0] not in future_uses:
                return index
            
            if ptr and ptr[0] in future_uses:
                next_use = future_uses[ptr[0]][0]
                if next_use > farthest_use:
                    farthest_use = next_use
                    farthest_page_index = index
            else:
                return None
        return farthest_page_index

    def use(self, ptr):
        if ptr not in self.page_table:
            raise ValueError(f"Pointer {ptr} does not exist in page table.")

        pages = self.page_table[ptr]

        for page in pages:
            if page.in_ram:
                self.total_time += 1
            else:
                future_uses = self.get_future_uses()
                farthest_page_index = self.get_farthest_page_index(future_uses)
                
                if len(self.real_memory) >= NUM_PAGES:
                    if farthest_page_index is not None:
                        replaced_page = self.real_memory.pop(farthest_page_index)
                    else:
                        replaced_page = self.real_memory.pop(0)

                    replaced_page.in_ram = False
                    replaced_page.m_addr = None
                    replaced_page.l_time = None
                    self.virtual_memory.append(replaced_page)
                    replaced_page.d_addr = self.virtual_memory.index(replaced_page)

                self.real_memory.append(page)
                page.d_addr = None
                page.in_ram = True
                page.m_addr = self.real_memory.index(page)
                page.l_time = self.total_time
                self.virtual_memory = [vp for vp in self.virtual_memory if vp.page_id != page.page_id]

                self.total_time += 5
                self.total_thrashing += 5 
    
def generar_procesos_y_operaciones(P, N):
    procesos = []
    total_ops = 0
    ptr_counter = 0
    ptr_array = []
    max_ops = 5
    while total_ops < N:
        pid = random.randint(0, P) 
        num_ops = random.randint(1, N - total_ops) % max_ops
        nuevas_operaciones, ptr_counter, ptr_array = generar_operaciones_para_proceso(pid, num_ops, ptr_counter, ptr_array)
        procesos += nuevas_operaciones
        total_ops += len(nuevas_operaciones)
        
    return procesos

def generar_operaciones_para_proceso(pid, num_ops, ptr_counter, ptr_array):
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
                ptr_array.append((pid, ptr_counter))
                operaciones.append(f"new({pid}, {size})")
                tiene_ptr = True
        
        elif operacion == "use":
            if tiene_ptr and not kill_realizado:
                index = random.randint(0, len(ptr_array) - 1)
                _, ptr = ptr_array[index]
                operaciones.append(f"use({ptr})")
        
        elif operacion == "delete":
            if tiene_ptr and not kill_realizado:
                index = random.randint(0, len(ptr_array) - 1)
                _, ptr = ptr_array.pop(index)
                operaciones.append(f"delete({ptr})")
        
        elif operacion == "kill":
            if tiene_ptr and not kill_realizado:
                remove_ptrs = [(p, ptr) for p, ptr in ptr_array if p == pid] 

                for item in remove_ptrs:
                    ptr_array.remove(item)

                operaciones.append(f"kill({pid})")
                kill_realizado = True
        i += 1
    return operaciones, ptr_counter, ptr_array

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

    # Crear la instancia de mmu_opt (OPT)
    mmu_opt = OPT(operaciones)

    # Seleccionar el algoritmo para mmu
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
    punteros_opt = {}
    
    global_counter = 0

    # Ejecutar las operaciones
    for operacion in operaciones:
        if "new" in operacion:
            # new(pid, size)
            pid, size = map(int, operacion[4:-1].split(","))

            # Ejecutar en mmu y mmu_opt
            ptr = mmu.allocate(pid, size)
            ptr_opt = mmu_opt.allocate(pid, size)
            
            punteros[ptr] = pid
            punteros_opt[ptr_opt] = pid

            global_counter += 1

        elif "use" in operacion:
            # use(ptr)
            
            ptr = int(operacion[4:-1])
            if ptr in punteros:
                tiempo = mmu.use(ptr)
                tiempo_opt = mmu_opt.use(ptr)

                global_counter += 1
            else:
                print(f"Error: puntero {ptr} no existe")

        elif "delete" in operacion:
            # delete(ptr)
            ptr = int(operacion[7:-1])
            if ptr in punteros:
                mmu.delete(ptr)
                mmu_opt.delete(ptr)

                global_counter += 1

                del punteros[ptr]
                del punteros_opt[ptr]
            else:
                print(f"Error: puntero {ptr} no existe o ya ha sido eliminado")

        elif "kill" in operacion:
            # kill(pid)
            pid = int(operacion[5:-1])
            mmu.kill(pid)
            mmu_opt.kill(pid)

            global_counter += 1

            punteros = {ptr: p for ptr, p in punteros.items() if p != pid}
            punteros_opt = {ptr: p for ptr, p in punteros_opt.items() if p != pid}

        # Crear el estado de simulación para mmu (algoritmo seleccionado)
        estado_simulacion = {
            "ram_usage": len(mmu.real_memory) * PAGE_SIZE,
            "vram_usage": len(mmu.virtual_memory) * PAGE_SIZE,
            "thrashing_time": mmu.total_thrashing,
            "total_simulation_time": mmu.total_time,
            "processes_running": len(punteros),
            "fragmentation": mmu.total_frag,
            "ram_state": mmu.real_memory,
            "virtual_state": mmu.virtual_memory,
            "pages_loaded": 0,
            "pages_unloaded": 0
        }

        # Contar las páginas cargadas y descargadas en mmu
        for page in mmu.real_memory:
            estado_simulacion["pages_loaded"] += 1  # Páginas cargadas en RAM

        for page in mmu.virtual_memory:
            estado_simulacion["pages_unloaded"] += 1  # Páginas no cargadas en RAM (memoria virtual)

        # Crear el estado de simulación para mmu_opt (OPT)
        estado_simulacion_opt = {
            "ram_usage": len(mmu_opt.real_memory) * PAGE_SIZE,
            "vram_usage": len(mmu_opt.virtual_memory) * PAGE_SIZE,
            "thrashing_time": mmu_opt.total_thrashing,
            "total_simulation_time": mmu_opt.total_time,
            "processes_running": len(punteros_opt),  # Asumimos que los mismos procesos están corriendo
            "fragmentation": mmu_opt.total_frag,
            "ram_state": mmu_opt.real_memory,
            "virtual_state": mmu_opt.virtual_memory,
            "pages_loaded": 0,
            "pages_unloaded": 0
        }

        # Contar las páginas cargadas y descargadas en mmu_opt
        for page in mmu_opt.real_memory:
            estado_simulacion_opt["pages_loaded"] += 1  # Páginas cargadas en RAM para OPT

        for page in mmu_opt.virtual_memory:
            estado_simulacion_opt["pages_unloaded"] += 1  # Páginas no cargadas en RAM (memoria virtual) para OPT

        # Retornar ambos estados
        yield estado_simulacion, estado_simulacion_opt
