import struct
import math
from collections import defaultdict

class StackMachine:
    def __init__(self):
        # Componentes principales
        self.stack = []                       # Pila de operandos
        self.memory = bytearray(1024)         # Memoria lineal byte-addressable
        self.globals = {}                     # Variables globales
        self.locals_stack = []                # Stack de variables locales
        self.call_stack = []                  # Stack de llamadas (para CALL/RET)
        self.functions = {}                   # Funciones definidas
        self.pc = 0                           # Contador de programa
        self.program = []                     # Programa IR cargado
        self.running = False
        self.labels = {}                      # Etiquetas para saltos
        
        # Registros especiales
        self.sp = 0                           # Stack pointer (para memoria)
        self.fp = 0                           # Frame pointer (para llamadas)

    def load_program(self, program):
        """Carga un programa IR y prepara las etiquetas"""
        self.program = program
        self._parse_labels()
        
    def _parse_labels(self):
        """Preprocesa el programa para encontrar etiquetas"""
        self.labels = {}
        for pc, instr in enumerate(self.program):
            if len(instr) > 0 and instr[0] == 'LABEL':
                self.labels[instr[1]] = pc

    def run(self):
        """Ejecuta el programa cargado"""
        self.pc = 0
        self.running = True
        while self.running and self.pc < len(self.program):
            instr = self.program[self.pc]
            if not instr:  # Instrucción vacía
                self.pc += 1
                continue
                
            opname = instr[0]
            args = instr[1:] if len(instr) > 1 else []
            
            # Busca el método correspondiente a la operación
            method = getattr(self, f"op_{opname}", None)
            if method:
                method(*args)
            else:
                raise RuntimeError(f"Instrucción desconocida: {opname}")
            
            # Avanza el contador de programa (a menos que la instrucción lo haya modificado)
            if self.running and (opname not in ['CALL', 'IF', 'LOOP', 'CBREAK', 'RET']):
                self.pc += 1

    def op_LABEL(self, label):
        """Define una etiqueta (preprocesada en load_program)"""
        # Esta instrucción es manejada durante el preprocesamiento
        pass

    def op_GOTO(self, label):
        """Salto incondicional a una etiqueta"""
        if label in self.labels:
            self.pc = self.labels[label]
        else:
            raise NameError(f"Etiqueta no definida: {label}")

    # =============================================
    # Operaciones básicas y manipulación de la pila
    # =============================================
    
    def op_CONSTI(self, value):
        """Empuja un entero a la pila"""
        self.stack.append(('int', int(value)))
        
    def op_CONSTF(self, value):
        """Empuja un float a la pila"""
        self.stack.append(('float', float(value)))
        
    def op_CONSTB(self, value):
        """Empuja un booleano a la pila"""
        self.stack.append(('bool', bool(value)))
        
    def op_CONSTC(self, value):
        """Empuja un carácter a la pila"""
        self.stack.append(('char', ord(value) if isinstance(value, str) else int(value)))
    
    def op_POP(self):
        """Elimina el elemento superior de la pila"""
        if not self.stack:
            raise RuntimeError("Stack underflow")
        self.stack.pop()
    
    # =============================================
    # Operaciones aritméticas
    # =============================================
    
    def _binary_op(self, op, int_op, float_op):
        """Función auxiliar para operaciones binarias"""
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('int', int_op(a, b)))
        elif a_type == 'float' and b_type == 'float':
            self.stack.append(('float', float_op(a, b)))
        else:
            raise TypeError(f"{op} requiere tipos compatibles")

    def op_ADDI(self):
        self._binary_op('ADDI', lambda a, b: a + b, lambda a, b: a + b)
            
    def op_SUBI(self):
        self._binary_op('SUBI', lambda a, b: a - b, lambda a, b: a - b)
            
    def op_MULI(self):
        self._binary_op('MULI', lambda a, b: a * b, lambda a, b: a * b)
            
    def op_DIVI(self):
        def int_div(a, b):
            if b == 0:
                raise ZeroDivisionError("División por cero")
            return a // b
        self._binary_op('DIVI', int_div, lambda a, b: a / b)
            
    def op_ADDF(self):
        self._binary_op('ADDF', lambda a, b: float(a) + float(b), lambda a, b: a + b)
            
    def op_SUBF(self):
        self._binary_op('SUBF', lambda a, b: float(a) - float(b), lambda a, b: a - b)
            
    def op_MULF(self):
        self._binary_op('MULF', lambda a, b: float(a) * float(b), lambda a, b: a * b)
            
    def op_DIVF(self):
        def float_div(a, b):
            if math.isclose(b, 0.0, abs_tol=1e-12):
                raise ZeroDivisionError("División por cero")
            return a / b
        self._binary_op('DIVF', lambda a, b: float(a) / float(b), float_div)
    
    # =============================================
    # Operaciones lógicas y de comparación
    # =============================================
    
    def op_ANDI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        # Convertimos a booleanos si son enteros
        if a_type == 'int':
            a = bool(a)
            a_type = 'bool'
        if b_type == 'int':
            b = bool(b)
            b_type = 'bool'
        if a_type == 'bool' and b_type == 'bool':
            self.stack.append(('bool', a and b))
        else:
            raise TypeError("ANDI requiere dos booleanos")
            
    def op_ORI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        # Convertimos a booleanos si son enteros
        if a_type == 'int':
            a = bool(a)
            a_type = 'bool'
        if b_type == 'int':
            b = bool(b)
            b_type = 'bool'
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
            
    def _compare_op(self, op, int_op, float_op):
        """Función auxiliar para operaciones de comparación"""
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        
        if a_type == 'int' and b_type == 'int':
            self.stack.append(('bool', int_op(a, b)))
        elif a_type == 'float' and b_type == 'float':
            self.stack.append(('bool', float_op(a, b)))
        else:
            raise TypeError(f"{op} requiere tipos compatibles")

    def op_EQI(self):
        self._compare_op('EQI', lambda a, b: a == b, lambda a, b: math.isclose(a, b))
            
    def op_NEI(self):
        self._compare_op('NEI', lambda a, b: a != b, lambda a, b: not math.isclose(a, b))
            
    def op_LTI(self):
        self._compare_op('LTI', lambda a, b: a < b, lambda a, b: a < b)
            
    def op_LEI(self):
        self._compare_op('LEI', lambda a, b: a <= b, lambda a, b: a <= b)
            
    def op_GTI(self):
        self._compare_op('GTI', lambda a, b: a > b, lambda a, b: a > b)
            
    def op_GEI(self):
        self._compare_op('GEI', lambda a, b: a >= b, lambda a, b: a >= b)

    def op_LTF(self):
        self._compare_op('LTF', lambda a, b: a < b, lambda a, b: a < b)

    def op_LEF(self):
        self._compare_op('LEF', lambda a, b: a <= b, lambda a, b: a <= b)

    def op_GTF(self):
        self._compare_op('GTF', lambda a, b: a > b, lambda a, b: a > b)

    def op_GEF(self):
        self._compare_op('GEF', lambda a, b: a >= b, lambda a, b: a >= b)

    def op_EQF(self):
        self._compare_op('EQF', lambda a, b: math.isclose(a, b), lambda a, b: math.isclose(a, b))

    def op_NEF(self):
        self._compare_op('NEF', lambda a, b: not math.isclose(a, b), lambda a, b: not math.isclose(a, b))
    
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
    
    def _grow_memory(self, amount):
        """Expande la memoria en la cantidad especificada"""
        self.memory.extend(bytearray(amount))
    
    def op_GROW(self):
        """Expande la memoria (tamaño en la pila)"""
        val_type, amount = self.stack.pop()
        if val_type != 'int':
            raise TypeError("GROW requiere un entero")
        self._grow_memory(amount)
        self.stack.append(('int', len(self.memory)))
    
    def _mem_access(self, size, pack_fn, unpack_fn, type_name):
        """Función auxiliar para operaciones de memoria"""
        addr_type, addr = self.stack.pop()
        if addr_type != 'int':
            raise TypeError(f"Dirección debe ser entera para {type_name}")
            
        if addr + size > len(self.memory):
            self._grow_memory(addr + size - len(self.memory))
            
        return addr

    def op_PEEKI(self):
        """Lee un entero de 4 bytes de la memoria"""
        addr = self._mem_access(4, struct.pack, struct.unpack, 'PEEKI')
        value = struct.unpack('<i', self.memory[addr:addr+4])[0]
        self.stack.append(('int', value))
        
    def op_POKEI(self):
        """Escribe un entero de 4 bytes en la memoria"""
        val_type, value = self.stack.pop()
        if val_type != 'int':
            raise TypeError("POKEI requiere un entero")
        addr = self._mem_access(4, struct.pack, struct.unpack, 'POKEI')
        self.memory[addr:addr+4] = struct.pack('<i', value)
        
    def op_PEEKF(self):
        """Lee un flotante de 4 bytes de la memoria"""
        addr = self._mem_access(4, struct.pack, struct.unpack, 'PEEKF')
        value = struct.unpack('<f', self.memory[addr:addr+4])[0]
        self.stack.append(('float', value))
        
    def op_POKEF(self):
        """Escribe un flotante de 4 bytes en la memoria"""
        val_type, value = self.stack.pop()
        if val_type != 'float':
            raise TypeError("POKEF requiere un flotante")
        addr = self._mem_access(4, struct.pack, struct.unpack, 'POKEF')
        self.memory[addr:addr+4] = struct.pack('<f', value)
        
    def op_PEEKB(self):
        """Lee un byte de la memoria"""
        addr = self._mem_access(1, struct.pack, struct.unpack, 'PEEKB')
        value = self.memory[addr]
        self.stack.append(('int', value))  # Tratamos bytes como enteros
        
    def op_POKEB(self):
        """Escribe un byte en la memoria"""
        val_type, value = self.stack.pop()
        if val_type != 'int' or value < 0 or value > 255:
            raise TypeError("POKEB requiere un entero entre 0-255")
        addr = self._mem_access(1, struct.pack, struct.unpack, 'POKEB')
        self.memory[addr] = value
    
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
        if val_type == 'int':
            val_type = 'bool'
            val = bool(val)
        if val_type != 'bool':
            raise TypeError("IF requiere un booleano")
        if not val:
            if label in self.labels:
                self.pc = self.labels[label]
            else:
                raise NameError(f"Etiqueta no definida: {label}")
        else:
            # Si es verdadero, simplemente avanzamos al siguiente manualmente
            self.pc += 1
                
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
        if val_type == 'int':
            val_type = 'bool'
            val = bool(val)
        if val_type != 'bool':
            raise TypeError("CBREAK requiere un booleano")
        if val:
            if label in self.labels:
                self.pc = self.labels[label]
            else:
                raise NameError(f"Etiqueta no definida: {label}")
                
    def op_CONTINUE(self, label):
        """Continúa con la siguiente iteración del bucle"""
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
        if func_name not in self.functions:
            raise NameError(f"Función no definida: {func_name}")
        func_info = self.functions[func_name]
        num_locals = func_info.get('num_locals', 0)
        #Guarda el estado actual
        self.call_stack.append({
            'pc': self.pc + 1,  # Retornar a la siguiente instrucción
            'locals': self.locals_stack[-1] if self.locals_stack else None,
            'fp': self.fp
        })
        #Sacar argumentos de la pila
        args = []
        for _ in range(num_locals):
            if self.stack:
                args.append(self.stack.pop())
            else:
                args.append(('int', 0))  # Valor por defecto si no hay suficientes argumentos
        args= list(reversed(args))  # Invertir para que el primer argumento esté al final de la pila
        self.locals_stack.append(args)  # Crear un nuevo frame de variables locales
        self.fp = len(self.stack)  # Frame pointer apunta a la base de los argumentos
        self.pc = func_info['address']  # Cambia al código de la función
        # if func_name in self.functions:
        #     # Guarda el estado actual
        #     self.call_stack.append({
        #         'pc': self.pc + 1,  # Retornar a la siguiente instrucción
        #         'locals': self.locals_stack[-1] if self.locals_stack else None,
        #         'fp': self.fp
        #     })
            
        #     # Configura el nuevo entorno
        #     num_locals = self.functions[func_name].get('num_locals', 0)
        #     self.locals_stack.append([None] * num_locals)
        #     self.fp = len(self.stack)  # Frame pointer apunta a la base de los argumentos
        #     self.pc = self.functions[func_name]['address']
        # else:
        #     raise NameError(f"Función no definida: {func_name}")
            
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
        """Imprime un entero o boolean como 0/1"""
        val_type, val = self.stack.pop()
        if val_type == 'int':
            print(val, end='')
        elif val_type == 'bool':
            print(1 if val else 0, end='')
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
        """Imprime un booleano o carácter"""
        val_type, val = self.stack.pop()
        if val_type == 'bool':
            print("true" if val else "false", end='')
        elif val_type == 'char':
            print(chr(val), end='')
        elif val_type == 'int' and 0 <= val <= 255:
            print(chr(val), end='')
        elif val_type == 'int':
            print(chr(val & 0xFF), end='') # Imprime el byte menos significativo
        else:
            raise TypeError("PRINTB requiere un booleano o carácter")
            
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


if __name__ == "__main__":
    import sys
	
    from errors import error, errors_detected
    from glexer import Lexer
    from gparser import Parser
    from checkNew import Checker
    from ircode import IRCode

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python stack_machine.py <filename>")

    filename = sys.argv[1]

    with open(filename, "r", encoding="utf-8") as f:
        source_code = f.read()

    lexer = Lexer(source_code)
    tokens = list(lexer.tokenize())
    parser = Parser(tokens)
    top = parser.parse()
    print('Ast generado:')
    print(top)
    env = Checker.check(top)
    if not errors_detected():
        print('Maquina de pila: ')
        module = IRCode.gencode(top)
        module.dump()
        #Construccion del programa completo
        program_code = [] # Es una lista de instrucciones
        func_addresses = {} # es un diccionario que mapea nombres de funciones a sus direcciones
        for fname, func in module.functions.items():
            func_addresses[fname] ={
                'address': len(program_code),
                'num_locals': len(func.locals)
            }
            program_code.extend(func.code)
        print('Ejecutando programa:')
        vm = StackMachine()
        vm.load_program(program_code)
        vm.functions = func_addresses
        vm.run()