def sumar(a, b):
    return a + b

def restar(a, b):
    return a - b

def multiplicar(a, b):
    return a * b

def dividir(a, b):
    if b == 0:
        return "Error: División por cero"
    return a / b

if __name__ == '__main__':
    print(sumar(4, 2))         # 6
    print(restar(4, 2))        # 2
    print(multiplicar(4, 2))   # 8
    print(dividir(4, 2))       # 2.0
    print(dividir(4, 0))       # Error: División por cero
