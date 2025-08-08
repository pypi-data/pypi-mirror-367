"""Tests para las funciones principales de la librería."""

import pytest
from mi_libreria.core import saludar, calcular


def test_saludar():
    """Test para la función saludar."""
    assert saludar("Ana") == "¡Hola, Ana!"
    assert saludar("Carlos") == "¡Hola, Carlos!"


def test_calcular_suma():
    """Test para la operación suma."""
    assert calcular(2, 3) == 5
    assert calcular(2, 3, "suma") == 5
    assert calcular(0, 0) == 0
    assert calcular(-1, 1) == 0


def test_calcular_resta():
    """Test para la operación resta."""
    assert calcular(5, 3, "resta") == 2
    assert calcular(0, 5, "resta") == -5
    assert calcular(10, 10, "resta") == 0


def test_calcular_multiplicacion():
    """Test para la operación multiplicación."""
    assert calcular(4, 5, "multiplicacion") == 20
    assert calcular(0, 10, "multiplicacion") == 0
    assert calcular(-2, 3, "multiplicacion") == -6


def test_calcular_division():
    """Test para la operación división."""
    assert calcular(10, 2, "division") == 5
    assert calcular(7, 2, "division") == 3.5
    assert calcular(-8, 4, "division") == -2


def test_calcular_division_por_cero():
    """Test para división por cero."""
    with pytest.raises(ZeroDivisionError):
        calcular(5, 0, "division")


def test_calcular_operacion_invalida():
    """Test para operación inválida."""
    with pytest.raises(ValueError):
        calcular(2, 3, "potencia")
    
    with pytest.raises(ValueError):
        calcular(2, 3, "invalida")