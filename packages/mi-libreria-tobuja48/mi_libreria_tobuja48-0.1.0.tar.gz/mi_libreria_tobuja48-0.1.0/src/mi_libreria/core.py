"""Funciones principales de la librería."""

def saludar(nombre: str) -> str:
    """
    Saluda a una persona.
    
    Args:
        nombre: El nombre de la persona a saludar
        
    Returns:
        Un mensaje de saludo
    """
    return f"¡Hola, {nombre}!"

def calcular(a: float, b: float, operacion: str = "suma") -> float:
    """
    Realiza operaciones matemáticas básicas.
    
    Args:
        a: Primer número
        b: Segundo número  
        operacion: Tipo de operación (suma, resta, multiplicacion, division)
        
    Returns:
        El resultado de la operación
        
    Raises:
        ValueError: Si la operación no es válida
        ZeroDivisionError: Si se intenta dividir por cero
    """
    if operacion == "suma":
        return a + b
    elif operacion == "resta":
        return a - b
    elif operacion == "multiplicacion":
        return a * b
    elif operacion == "division":
        if b == 0:
            raise ZeroDivisionError("No se puede dividir por cero")
        return a / b
    else:
        raise ValueError(f"Operación '{operacion}' no válida")