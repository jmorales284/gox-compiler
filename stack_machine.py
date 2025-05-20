class StackMachine:
  def __init__(self,memory_size=1024):
    self.stack = [] #Pila Principal
    self.memory = [0] * memory_size #Memoria lineal
    self.globals = {} #Variables globales
    self.locals_stack = [] #Stack de variables locales
    self.call_stack = [] #Stack de retorno de funciones
    self.functions = {} #Diccionario de funciones
    self.pc = 0 #Contador de programa
    self.program = [] #Programa IR Cargado
    self.running = False

  def load_program(self, program):
    self.program = program
  
  def run(self):
    self.pc = 0
    self.running = True
    while self.running and self.pc < len(self.program):
      instr = self.program[self.pc]
      opname = instr[0]
      args = instr[1:] if len(instr) > 1 else []
      method = getattr(self, f"op_{opname}", None)
      if method:
        method(*args)
      else:
        raise RuntimeError(f"Instruccion desconocida: {opname}")
      self.pc += 1



  # Operaciones de pila y aritmética
  def op_CONSTI(self, value):
    self.stack.append(('int', value))

  def op_CONSTF(self, value):
    self.stack.append(('float', value))

  def op_ADDI(self):
    b_type, b_value = self.stack.pop()
    a_type, a_value = self.stack.pop()
    if a_type == b_type == 'int':
      self.stack.append(('int', a_value + b_value))
    else:
      raise TypeError(f"Tipo de dato no soportado para ADDI: {a_type}, {b_type}")
  
  def op_SUBI(self):
    b_type, b_value = self.stack.pop()
    a_type, a_value = self.stack.pop()
    if a_type == b_type == 'int':
      self.stack.append(('int', a_value - b_value))
    else:
      raise TypeError(f"Tipo de dato no soportado para SUBI: {a_type}, {b_type}")
    
  def op_MULI(self):
    b_type, b_value = self.stack.pop()
    a_type, a_value = self.stack.pop()
    if a_type == b_type == 'int':
      self.stack.append(('int', a_value * b_value))
    else:
      raise TypeError(f"Tipo de dato no soportado para MULI: {a_type}, {b_type}")
    
  def op_DIVI(self):
    b_type, b_value = self.stack.pop()
    a_type, a_value = self.stack.pop()
    if a_type == b_type == 'int':
      if b_value == 0:
        raise ZeroDivisionError("Division por cero")
      self.stack.append(('int', a_value // b_value))
    else:
      raise TypeError(f"Tipo de dato no soportado para DIVI: {a_type}, {b_type}")
    
  # Operaciones de impresion

  def op_PRINTI(self):
    value_type, value = self.stack.pop()
    if value_type == 'int':
      print(value)
    else:
      raise TypeError(f"Tipo de dato no soportado para PRINTI: {value_type}")
    

  # Operaciones de control de flujo
  def op_RET(self):
    if self.call_stack:
      self.pc = self.call_stack.pop()
    else:
      self.running = False

  # Acceso a memoria lineal

  def op_PEEKI(self):
    addr_type, addr_value = self.stack.pop()
    if addr_type == 'int':
      if 0 <= addr_value < len(self.memory):
        self.stack.append(('int', self.memory[addr_value]))
      else:
        raise IndexError("Direccion fuera de rango")
    else:
      raise TypeError(f"Tipo de dato no soportado para PEEKI: {addr_type}")
    
  def op_POKEI(self):
    value_type, value = self.stack.pop()
    addr_type, addr_value = self.stack.pop()
    if addr_type == 'int' and value_type == 'int':
      if 0 <= addr_value < len(self.memory):
        self.memory[addr_value] = value
      else:
        raise IndexError("Direccion fuera de rango")
    else:
      raise TypeError(f"Tipo de dato no soportado para POKEI: {addr_type}, {value_type}")
    
  def op_GLOBAL_SET(self, name):
    """"Guarda el valor de la cima de la pila en una variable global"""
    value_type, value = self.stack.pop()
    if name in self.globals:
      if self.globals[name][0] == value_type:
        self.globals[name] = (value_type, value)
      else:
        raise TypeError(f"Tipo de dato no soportado para GLOBAL_SET: {self.globals[name][0]}, {value_type}")
    else:
      self.globals[name] = (value_type, value)

  def op_GLOBAL_GET(self, name):
    """Carga el valor de una variable global en la cima de la pila"""
    if name in self.globals:
      value_type, value = self.globals[name]
      self.stack.append((value_type, value))
    else:
      raise NameError(f"Variable global no definida: {name}")
  

if __name__ == "__main__":
  import sys
  from errors import error, errors_detected
  from glexer import Lexer
  from gparser import Parser
  from checkNew import Checker
  from ircode import IRCode

  if len(sys.argv) != 2:
    print("Uso: python stack_machine.py <archivo>")
    sys.exit(1)

  filename = sys.argv[1]
  with open(filename, 'r',encoding='utf-8') as f:
    source_code = f.read()
  lexer = Lexer(source_code)
  tokens = list(lexer.tokenize())
  parser = Parser(tokens)
  top= parser.parse()
  print("AST generado:", top)
  env = Checker.check(top)

  if not errors_detected():
    module = IRCode.gencode(top)
    module.dump()
    #Extraccion del IR de la funcion main
    program_code = module.functions['main'].code
    vm = StackMachine()
    vm.load_program(program_code)
    vm.run()
