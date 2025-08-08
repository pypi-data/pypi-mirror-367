# Mi Librería

Una librería de ejemplo para demostrar cómo crear y publicar un paquete en PyPI.

## Instalación

```bash
pip install mi-libreria
```

## Uso

```python
from mi_libreria import saludar, calcular

# Saludar
print(saludar("Ana"))  # ¡Hola, Ana!

# Operaciones matemáticas
print(calcular(2, 3))  # 5 (suma por defecto)
print(calcular(10, 4, "resta"))  # 6
print(calcular(3, 7, "multiplicacion"))  # 21
print(calcular(15, 3, "division"))  # 5.0
```

## Funciones disponibles

### `saludar(nombre: str) -> str`
Saluda a una persona por su nombre.

### `calcular(a: float, b: float, operacion: str = "suma") -> float`
Realiza operaciones matemáticas básicas.

**Parámetros:**
- `a`: Primer número
- `b`: Segundo número
- `operacion`: Tipo de operación ("suma", "resta", "multiplicacion", "division")

## Desarrollo

Para instalar en modo desarrollo:

```bash
git clone https://github.com/tu-usuario/mi-libreria
cd mi-libreria
pip install -e .[dev]
```

Para ejecutar tests:

```bash
pytest tests/
```

## Licencia

MIT