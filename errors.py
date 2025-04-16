'''
Manejo de errores del compilador

'''

from rich import print

_errors_detected=0

def error(message,lineno=None):
    global _errors_detected
    if lineno:
        print(f'{lineno}: [red]Error:[/red] {message}')
    else:
        print(f'[red]Error:[/red] {message}')
    _errors_detected+=1

def errors_detected():
    return _errors_detected

def clear_errors():
    global _errors_detected
    _errors_detected=0