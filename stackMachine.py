import struct
import math

class StackMachine:
    def __init__(self):
        # Componentes principales
        self.stack = []                       # Pila de operandos
        self.memory = bytearray(1024)          # Memoria lineal byte-addressable
        self.globals = {}                      # Variables globales
        self.locals_stack = []                 # Stack de variables locales
        self.call_stack = []                   # Stack de llamadas (para CALL/RET)
        self.functions = {}                    # Funciones definidas
        self.pc = 0                            # Contador de programa
        self.program = []                      # Programa IR cargado
        self.running = False
        self.labels = {}                       # Etiquetas para saltos
        
        # Registros especiales
        self.sp = 0                            # Stack pointer (para memoria)
        self.fp = 0                            # Frame pointer (para llamadas)

    def load_program(self, program):
        """Carga un programa IR y prepara las etiquetas"""
        self.program = program
        self._parse_labels()
        
    def _parse_labels(self):
        """Preprocesa el programa para encontrar etiquetas"""
        self.labels = {}
        for pc, instr in enumerate(self.program):
            if instr[0] == 'LABEL':
                self.labels[instr[1]] = pc

    def run(self):
        """Ejecuta el programa cargado"""
        self.pc = 0
        self.running = True
        while self.running and self.pc < len(self.program):
            instr = self.program[self.pc]
            opname = instr[0]
            args = instr[1:] if len(instr) > 1 else []
            
            # Busca el método correspondiente a la operación
            method = getattr(self, f"op_{opname}", None)
            if method:
                method(*args)
            else:
                raise RuntimeError(f"Instrucción desconocida: {opname}")
            
            # Avanza el contador de programa (a menos que la instrucción lo haya modificado)
            if self.running and (opname not in ['CALL', 'IF', 'LOOP', 'CBREAK']):
                self.pc += 1

    # =============================================
    # Operaciones básicas y manipulación de la pila
    # =============================================
    
    def op_CONSTI(self, value):
        """Empuja un entero a la pila"""
        self.stack.append(('int', value))
        
    def op_CONSTF(self, value):
        """Empuja un float a la pila"""
        self.stack.append(('float', value))
        
    def op_CONSTB(self, value):
        """Empuja un booleano a la pila"""
        self.stack.append(('bool', value))
        
    def op_CONSTC(self, value):
        """Empuja un carácter a la pila"""
        self.stack.append(('char', value))
        
    def op_POP(self):
        """Elimina el elemento superior de la pila"""
        self.stack.pop()
    
    # =============================================
    # Operaciones aritméticas
    # =============================================
    
    def op_ADDI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('int', a + b))
        else:
            raise TypeError("ADDI requiere dos enteros")
            
    def op_SUBI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('int', a - b))
        else:
            raise TypeError("SUBI requiere dos enteros")
            
    def op_MULI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('int', a * b))
        else:
            raise TypeError("MULI requiere dos enteros")
            
    def op_DIVI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'int' and b_type == 'int':
            if b == 0:
                raise ZeroDivisionError("División por cero")
            self.stack.append(('int', a // b))
        else:
            raise TypeError("DIVI requiere dos enteros")
            
    def op_ADDF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'float' and b_type == 'float':
            self.stack.append(('float', a + b))
        else:
            raise TypeError("ADDF requiere dos flotantes")
            
    def op_SUBF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'float' and b_type == 'float':
            self.stack.append(('float', a - b))
        else:
            raise TypeError("SUBF requiere dos flotantes")
            
    def op_MULF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'float' and b_type == 'float':
            self.stack.append(('float', a * b))
        else:
            raise TypeError("MULF requiere dos flotantes")
            
    def op_DIVF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'float' and b_type == 'float':
            if math.isclose(b, 0.0, abs_tol=1e-12):
                raise ZeroDivisionError("División por cero")
            self.stack.append(('float', a / b))
        else:
            raise TypeError("DIVF requiere dos flotantes")
    
    # =============================================
    # Operaciones lógicas y de comparación
    # =============================================
    
    def op_ANDI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'bool' and b_type == 'bool':
            self.stack.append(('bool', a and b))
        else:
            raise TypeError("ANDI requiere dos booleanos")
            
    def op_ORI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'bool' and b_type == 'bool':
            self.stack.append(('bool', a or b))
        else:
            raise TypeError("ORI requiere dos booleanos")
            
    def op_NOTI(self):
        val_type, val = self.stack.pop()
        if val_type == 'bool':
            self.stack.append(('bool', not val))
        else:
            raise TypeError("NOTI requiere un booleano")
            
    def op_EQI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type:
            self.stack.append(('bool', a == b))
        else:
            raise TypeError("EQI requiere tipos compatibles")
            
    def op_NEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type:
            self.stack.append(('bool', a != b))
        else:
            raise TypeError("NEI requiere tipos compatibles")
            
    def op_LTI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('bool', a < b))
        else:
            raise TypeError("LTI requiere dos enteros")
            
    def op_LEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('bool', a <= b))
        else:
            raise TypeError("LEI requiere dos enteros")
            
    def op_GTI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('bool', a > b))
        else:
            raise TypeError("GTI requiere dos enteros")
            
    def op_GEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('bool', a >= b))
        else:
            raise TypeError("GEI requiere dos enteros")
            
    def op_EQF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'float' and b_type == 'float':
            self.stack.append(('bool', math.isclose(a, b)))
        else:
            raise TypeError("EQF requiere dos flotantes")
            
    def op_NEF(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == 'float' and b_type == 'float':
            self.stack.append(('bool', not math.isclose(a, b)))
        else:
            raise TypeError("NEF requiere dos flotantes")
    
    # =============================================
    # Conversión de tipos
    # =============================================
    
    def op_ITOF(self):
        val_type, val = self.stack.pop()
        if val_type == 'int':
            self.stack.append(('float', float(val)))
        else:
            raise TypeError("ITOF requiere un entero")
            
    def op_FTOI(self):
        val_type, val = self.stack.pop()
        if val_type == 'float':
            self.stack.append(('int', int(val)))
        else:
            raise TypeError("FTOI requiere un flotante")
    
    # =============================================
    # Acceso a memoria
    # =============================================
    
    def op_PEEKI(self, offset=0):
        """Lee un entero de 4 bytes de la memoria"""
        addr = self.sp + offset
        if addr + 4 > len(self.memory):
            raise MemoryError("Acceso a memoria fuera de límites")
        value = struct.unpack('<i', self.memory[addr:addr+4])[0]
        self.stack.append(('int', value))
        
    def op_POKEI(self, offset=0):
        """Escribe un entero de 4 bytes en la memoria"""
        val_type, value = self.stack.pop()
        if val_type != 'int':
            raise TypeError("POKEI requiere un entero")
        addr = self.sp + offset
        if addr + 4 > len(self.memory):
            self._grow_memory(addr + 4 - len(self.memory))
        self.memory[addr:addr+4] = struct.pack('<i', value)
        
    def op_PEEKF(self, offset=0):
        """Lee un flotante de 4 bytes de la memoria"""
        addr = self.sp + offset
        if addr + 4 > len(self.memory):
            raise MemoryError("Acceso a memoria fuera de límites")
        value = struct.unpack('<f', self.memory[addr:addr+4])[0]
        self.stack.append(('float', value))
        
    def op_POKEF(self, offset=0):
        """Escribe un flotante de 4 bytes en la memoria"""
        val_type, value = self.stack.pop()
        if val_type != 'float':
            raise TypeError("POKEF requiere un flotante")
        addr = self.sp + offset
        if addr + 4 > len(self.memory):
            self._grow_memory(addr + 4 - len(self.memory))
        self.memory[addr:addr+4] = struct.pack('<f', value)
        
    def op_PEEKB(self, offset=0):
        """Lee un byte de la memoria"""
        addr = self.sp + offset
        if addr >= len(self.memory):
            raise MemoryError("Acceso a memoria fuera de límites")
        value = self.memory[addr]
        self.stack.append(('int', value))  # Tratamos bytes como enteros
        
    def op_POKEB(self, offset=0):
        """Escribe un byte en la memoria"""
        val_type, value = self.stack.pop()
        if val_type != 'int' or value < 0 or value > 255:
            raise TypeError("POKEB requiere un entero entre 0-255")
        addr = self.sp + offset
        if addr >= len(self.memory):
            self._grow_memory(addr - len(self.memory) + 1)
        self.memory[addr] = value
        
    def _grow_memory(self, amount):
        """Expande la memoria en la cantidad especificada"""
        self.memory.extend(bytearray(amount))
    
    def op_GROW(self, amount):
        """Expande la memoria"""
        self._grow_memory(amount)
    
    # =============================================
    # Variables globales y locales
    # =============================================
    
    def op_GLOBAL_GET(self, name):
        """Obtiene el valor de una variable global"""
        if name in self.globals:
            self.stack.append(self.globals[name])
        else:
            raise NameError(f"Variable global no definida: {name}")
            
    def op_GLOBAL_SET(self, name):
        """Establece el valor de una variable global"""
        value = self.stack.pop()
        self.globals[name] = value
        
    def op_LOCAL_GET(self, index):
        """Obtiene el valor de una variable local"""
        if self.locals_stack and index < len(self.locals_stack[-1]):
            self.stack.append(self.locals_stack[-1][index])
        else:
            raise IndexError("Índice de variable local inválido")
            
    def op_LOCAL_SET(self, index):
        """Establece el valor de una variable local"""
        if self.locals_stack and index < len(self.locals_stack[-1]):
            value = self.stack.pop()
            self.locals_stack[-1][index] = value
        else:
            raise IndexError("Índice de variable local inválido")
    
    # =============================================
    # Control de flujo
    # =============================================
    
    def op_IF(self, label):
        """Salto condicional si el tope de la pila es falso"""
        val_type, val = self.stack.pop()
        if val_type != 'bool':
            raise TypeError("IF requiere un booleano")
        if not val:
            if label in self.labels:
                self.pc = self.labels[label]
            else:
                raise NameError(f"Etiqueta no definida: {label}")
                
    def op_ELSE(self, label):
        """Salto incondicional (para el else)"""
        if label in self.labels:
            self.pc = self.labels[label]
        else:
            raise NameError(f"Etiqueta no definida: {label}")
            
    def op_ENDIF(self):
        """Fin del bloque condicional (no hace nada)"""
        pass
        
    def op_LOOP(self, label):
        """Inicio de un bucle (no hace nada, la etiqueta marca el inicio)"""
        pass
        
    def op_CBREAK(self, label):
        """Salto condicional para break (si el tope es verdadero)"""
        val_type, val = self.stack.pop()
        if val_type != 'bool':
            raise TypeError("CBREAK requiere un booleano")
        if val:
            if label in self.labels:
                self.pc = self.labels[label]
            else:
                raise NameError(f"Etiqueta no definida: {label}")
                
    def op_ENDLOOP(self, label):
        """Fin del bucle (salto incondicional al inicio)"""
        if label in self.labels:
            self.pc = self.labels[label]
        else:
            raise NameError(f"Etiqueta no definida: {label}")
    
    # =============================================
    # Funciones
    # =============================================
    
    def op_CALL(self, func_name):
        """Llama a una función"""
        if func_name in self.functions:
            # Guarda el estado actual
            self.call_stack.append({
                'pc': self.pc + 1,  # Retornar a la siguiente instrucción
                'locals': self.locals_stack[-1] if self.locals_stack else None,
                'fp': self.fp
            })
            
            # Configura el nuevo entorno
            self.locals_stack.append([None] * self.functions[func_name]['num_locals'])
            self.fp = len(self.stack)  # Frame pointer apunta a la base de los argumentos
            self.pc = self.functions[func_name]['address']
        else:
            raise NameError(f"Función no definida: {func_name}")
            
    def op_RET(self):
        """Retorna de una función"""
        if not self.call_stack:
            self.running = False
            return
            
        # Restaura el estado anterior
        call_info = self.call_stack.pop()
        self.pc = call_info['pc']
        
        # Elimina las variables locales
        if self.locals_stack:
            self.locals_stack.pop()
            
        # Restaura el frame pointer
        self.fp = call_info['fp']
    
    def op_DEF_FUNC(self, func_name, num_locals):
        """Define una función (preprocesada en load_program)"""
        # Esta instrucción es manejada durante el preprocesamiento
        pass
    
    # =============================================
    # Entrada/salida
    # =============================================
    
    def op_PRINTI(self):
        """Imprime un entero"""
        val_type, val = self.stack.pop()
        if val_type == 'int':
            print(val, end='')
        else:
            raise TypeError("PRINTI requiere un entero")
            
    def op_PRINTF(self):
        """Imprime un flotante"""
        val_type, val = self.stack.pop()
        if val_type == 'float':
            print(val, end='')
        else:
            raise TypeError("PRINTF requiere un flotante")
            
    def op_PRINTB(self):
        """Imprime un booleano"""
        val_type, val = self.stack.pop()
        if val_type == 'bool':
            print("true" if val else "false", end='')
        else:
            raise TypeError("PRINTB requiere un booleano")
            
    def op_PRINTC(self):
        """Imprime un carácter"""
        val_type, val = self.stack.pop()
        if val_type == 'char':
            print(chr(val), end='')
        else:
            raise TypeError("PRINTC requiere un carácter")
            
    def op_PRINTS(self):
        """Imprime una cadena (dirección en memoria)"""
        addr_type, addr = self.stack.pop()
        if addr_type != 'int':
            raise TypeError("PRINTS requiere una dirección entera")
            
        # Leemos la cadena de la memoria (terminada en null)
        s = []
        i = 0
        while True:
            if addr + i >= len(self.memory):
                raise MemoryError("Acceso a memoria fuera de límites")
            byte = self.memory[addr + i]
            if byte == 0:
                break
            s.append(chr(byte))
            i += 1
        print(''.join(s), end='')