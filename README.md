# Simulación Montecarlo - Sistema de Envaso

Proyecto en Python para simular el sistema de traslado de lotes de una fábrica de vasos.

## Instalación

Desde la carpeta del proyecto:

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requisitos.txt
```

## Ejecución

```bash
streamlit run app.py
```

Si Streamlit no se reconoce:

```bash
python -m streamlit run app.py
```

## Qué muestra

- Resultados solicitados por el enunciado.
- Tres variables adicionales propuestas.
- Vector de estado desde la fila inicial elegida hasta 200 filas posteriores.
- Fila N, siempre mostrada aparte.
- Opción para descargar los resultados en Excel.

## Supuestos actuales

- Se usa el generador pseudoaleatorio nativo de Python.
- Se usa Box-Muller para la distribución normal.
- Si la normal genera tiempos bajos o negativos, se aceptan tal como salen.
- La congestión solo agrega demora adicional, no cuenta como detención.
- No se almacenan las N filas completas: solo se conservan las filas visibles y la fila N.
