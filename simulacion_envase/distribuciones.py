from __future__ import annotations

import math
import random
from dataclasses import dataclass


class GeneradorAleatorio:
    """Generador uniforme que usa el generador nativo de Python."""

    def __init__(self, semilla: int | None = None) -> None:
        self._aleatorio = random.Random(semilla)

    def rnd(self) -> float:
        """Devuelve un RND uniforme en el intervalo [0, 1)."""
        return self._aleatorio.random()

    def rnd_abierto_0_1(self) -> float:
        """Devuelve un RND en (0, 1), útil cuando se aplica logaritmo."""
        valor = self.rnd()
        while valor <= 0.0:
            valor = self.rnd()
        return valor


def exponencial_desde_rnd(media: float, rnd: float) -> float:
    """Transformada inversa de una distribución exponencial con media indicada."""
    return -media * math.log(1 - rnd)


@dataclass(frozen=True)
class SorteoNormal:
    """Resultado de un sorteo normal generado con Box-Muller."""

    rnd1: float
    rnd2: float
    normal_usada: str
    valor: float


class GeneradorNormalBoxMuller:
    """
    Generador normal por método Box-Muller.

    Con cada par de RND uniformes genera dos normales:
    - N1 usando coseno.
    - N2 usando seno.

    La primera llamada devuelve N1 y guarda N2.
    La siguiente llamada devuelve N2, reutilizando los mismos RND.
    """

    def __init__(self, generador: GeneradorAleatorio, media: float, desviacion: float) -> None:
        self.generador = generador
        self.media = media
        self.desviacion = desviacion
        self._pendiente: SorteoNormal | None = None

    def sortear(self) -> SorteoNormal:
        """Devuelve un valor normal y los RND que lo originaron."""
        if self._pendiente is not None:
            pendiente = self._pendiente
            self._pendiente = None
            return pendiente

        rnd1 = self.generador.rnd_abierto_0_1()
        rnd2 = self.generador.rnd()

        factor = math.sqrt(-2 * math.log(rnd1))
        angulo = 2 * math.pi * rnd2

        z1 = factor * math.cos(angulo)
        z2 = factor * math.sin(angulo)

        n1 = self.media + z1 * self.desviacion
        n2 = self.media + z2 * self.desviacion

        self._pendiente = SorteoNormal(rnd1=rnd1, rnd2=rnd2, normal_usada="N2", valor=n2)
        return SorteoNormal(rnd1=rnd1, rnd2=rnd2, normal_usada="N1", valor=n1)
