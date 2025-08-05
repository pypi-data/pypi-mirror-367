# minitonupot

**minitonupot** es un mini módulo diseñado para mejorar el rendimiento de motores creados con `minitonu`, aplicando mejoras automáticas a los puntajes de rendimiento del motor neuronal.

## Características

- Mejora automática del rendimiento (`+15%`)
- Utilidades para normalización de puntuaciones
- Compatible con `minitonu>=0.0.1.1b1`
- Integración simple con `pip install -e .`

## Estructura del módulo

minitonupot/ ├── booster.py        # Lógica principal de mejora └── utils.py          # Funciones auxiliares

## Instalación

```bash
pip install minitonupot

Uso

from minitonupot.booster import boost_engine
from minitonu.core import MiniNeuralEngine

engine = MiniNeuralEngine()
boosted = boost_engine(engine)
