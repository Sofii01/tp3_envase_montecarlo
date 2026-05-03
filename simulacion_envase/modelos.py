from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Acumuladores:
    """Acumuladores y contadores que se actualizan jornada a jornada."""

    acumulador_demora_auditoria: float = 0.0
    acumulador_demora_escaneo: float = 0.0
    acumulador_demora_congestion: float = 0.0
    acumulador_tiempo_total: float = 0.0

    contador_congestion: int = 0
    contador_parada_y_auditoria: int = 0
    contador_sin_parada_ni_auditoria: int = 0

    # Contadores agregados para las variables adicionales.
    contador_paradas_escaneo: int = 0
    contador_auditorias: int = 0

    tiempo_maximo_total: float | None = None
    tiempo_minimo_total: float | None = None

    def actualizar(self, fila: "FilaEstado") -> None:
        """Actualiza los acumuladores usando los datos de la fila actual."""
        self.acumulador_demora_auditoria += fila.demora_auditoria
        self.acumulador_demora_escaneo += fila.demora_escaneo
        self.acumulador_demora_congestion += fila.demora_congestion
        self.acumulador_tiempo_total += fila.tiempo_total

        if fila.hay_congestion:
            self.contador_congestion += 1
        if fila.hay_parada:
            self.contador_paradas_escaneo += 1
        if fila.hay_auditoria:
            self.contador_auditorias += 1
        if fila.hay_parada and fila.hay_auditoria:
            self.contador_parada_y_auditoria += 1

        # Supuesto actual: la congestión solo agrega demora; no cuenta como detención.
        if not fila.hay_parada and not fila.hay_auditoria:
            self.contador_sin_parada_ni_auditoria += 1

        self.tiempo_maximo_total = (
            fila.tiempo_total
            if self.tiempo_maximo_total is None
            else max(self.tiempo_maximo_total, fila.tiempo_total)
        )
        self.tiempo_minimo_total = (
            fila.tiempo_total
            if self.tiempo_minimo_total is None
            else min(self.tiempo_minimo_total, fila.tiempo_total)
        )


@dataclass
class FilaEstado:
    """Representa una fila del vector de estado de la simulación."""

    jornada: int

    rnd_circuito: float
    cantidad_sectores: int

    rnd_parada: float
    hay_parada: bool
    rnd_demora_parada: float | None
    demora_escaneo: float

    recorrido_2_o_5_sectores: bool
    rnd_congestion: float | None
    hay_congestion: bool

    rnd_auditoria: float
    hay_auditoria: bool
    rnd_demora_auditoria: float | None
    demora_auditoria: float

    rnd1_tiempo_base: float
    rnd2_tiempo_base: float
    normal_usada: str
    tiempo_por_sector: float
    tiempo_base_traslado: float
    demora_congestion: float
    tiempo_parcial_paradas_auditorias: float
    tiempo_total: float

    acumulador_demora_auditoria: float = 0.0
    acumulador_demora_escaneo: float = 0.0
    acumulador_demora_congestion: float = 0.0
    acumulador_tiempo_total: float = 0.0

    contador_congestion: int = 0
    contador_parada_y_auditoria: int = 0
    contador_sin_parada_ni_auditoria: int = 0
    contador_paradas_escaneo: int = 0
    contador_auditorias: int = 0

    tiempo_maximo_total: float = 0.0
    tiempo_minimo_total: float = 0.0

    def aplicar_acumuladores(self, acumuladores: Acumuladores) -> None:
        """Copia el estado actual de los acumuladores dentro de la fila."""
        self.acumulador_demora_auditoria = acumuladores.acumulador_demora_auditoria
        self.acumulador_demora_escaneo = acumuladores.acumulador_demora_escaneo
        self.acumulador_demora_congestion = acumuladores.acumulador_demora_congestion
        self.acumulador_tiempo_total = acumuladores.acumulador_tiempo_total
        self.contador_congestion = acumuladores.contador_congestion
        self.contador_parada_y_auditoria = acumuladores.contador_parada_y_auditoria
        self.contador_sin_parada_ni_auditoria = acumuladores.contador_sin_parada_ni_auditoria
        self.contador_paradas_escaneo = acumuladores.contador_paradas_escaneo
        self.contador_auditorias = acumuladores.contador_auditorias
        self.tiempo_maximo_total = acumuladores.tiempo_maximo_total or 0.0
        self.tiempo_minimo_total = acumuladores.tiempo_minimo_total or 0.0

    @staticmethod
    def _si_no(valor: bool) -> str:
        return "SI" if valor else "NO"

    @staticmethod
    def _opcional(valor: float | None) -> float | str:
        return "" if valor is None else valor

    def a_diccionario_visible(self) -> dict[str, Any]:
        """Devuelve la fila con nombres de columnas pensados para pantalla y Excel."""
        return {
            "JORNADA DE OPERACIÓN": self.jornada,
            "RND CIRCUITO": self.rnd_circuito,
            "CANTIDAD DE SECTORES": self.cantidad_sectores,
            "RND PARADA": self.rnd_parada,
            "HAY PARADA": self._si_no(self.hay_parada),
            "RND DEMORA PARADA": self._opcional(self.rnd_demora_parada),
            "DEMORA ADICIONAL POR ESCANEO O REGISTRO": self.demora_escaneo,
            "RECORRIDO DE 2 O 5 SECTORES": self._si_no(self.recorrido_2_o_5_sectores),
            "RND CONGESTIÓN": self._opcional(self.rnd_congestion),
            "HAY CONGESTIÓN": self._si_no(self.hay_congestion),
            "RND AUDITORÍA": self.rnd_auditoria,
            "HAY AUDITORÍA": self._si_no(self.hay_auditoria),
            "RND DEMORA AUDITORÍA": self._opcional(self.rnd_demora_auditoria),
            "DEMORA ADICIONAL POR AUDITORÍA": self.demora_auditoria,
            "RND1 TIEMPO BASE": self.rnd1_tiempo_base,
            "RND2 TIEMPO BASE": self.rnd2_tiempo_base,
            "NORMAL USADA": self.normal_usada,
            "TIEMPO POR SECTOR": self.tiempo_por_sector,
            "TIEMPO BASE DE TRASLADO": self.tiempo_base_traslado,
            "TIEMPO ADICIONAL DE DEMORA POR CONGESTIÓN": self.demora_congestion,
            "TIEMPO PARCIAL CON PARADAS Y AUDITORÍAS": self.tiempo_parcial_paradas_auditorias,
            "TIEMPO TOTAL": self.tiempo_total,
            "ACUMULADOR DEMORA POR AUDITORÍA": self.acumulador_demora_auditoria,
            "ACUMULADOR DEMORA POR ESCANEO Y REGISTRO": self.acumulador_demora_escaneo,
            "ACUMULADOR DEMORA POR CONGESTIÓN": self.acumulador_demora_congestion,
            "ACUMULADOR DE TIEMPOS DE TRASLADO": self.acumulador_tiempo_total,
            "CONTADOR DE RECORRIDO CON CONGESTIÓN": self.contador_congestion,
            "CONTADOR RECORRIDO CON PARADAS Y AUDITORÍAS": self.contador_parada_y_auditoria,
            "CONTADOR RECORRIDO SIN PARADAS Y AUDITORÍAS": self.contador_sin_parada_ni_auditoria,
            "CONTADOR PARADAS POR ESCANEO": self.contador_paradas_escaneo,
            "CONTADOR AUDITORÍAS": self.contador_auditorias,
            "TIEMPO MÁXIMO DE TRASLADO": self.tiempo_maximo_total,
            "TIEMPO MÍNIMO DE TRASLADO": self.tiempo_minimo_total,
        }


@dataclass
class ResultadoSimulacion:
    """Resultado final de una corrida de simulación."""

    filas_seleccionadas: list[FilaEstado]
    fila_final: FilaEstado
    cantidad_jornadas: int
    fila_inicial: int

    def resultados_solicitados(self) -> dict[str, float | int]:
        """Calcula los resultados finales pedidos por el enunciado."""
        final = self.fila_final
        n = self.cantidad_jornadas
        return {
            "Tiempo promedio de traslado": final.acumulador_tiempo_total / n,
            "Porcentaje con parada y auditoría": (final.contador_parada_y_auditoria / n) * 100,
            "Cantidad sin parada ni auditoría": final.contador_sin_parada_ni_auditoria,
            "Tiempo máximo de traslado": final.tiempo_maximo_total,
            "Tiempo mínimo de traslado": final.tiempo_minimo_total,
            # Tres variables adicionales propuestas.
            "Variable adicional 1 - Porcentaje con congestión": (final.contador_congestion / n) * 100,
            "Variable adicional 2 - Promedio demora escaneo cuando hubo parada": (
                final.acumulador_demora_escaneo / final.contador_paradas_escaneo
                if final.contador_paradas_escaneo
                else 0.0
            ),
            "Variable adicional 3 - Promedio demora auditoría cuando hubo auditoría": (
                final.acumulador_demora_auditoria / final.contador_auditorias
                if final.contador_auditorias
                else 0.0
            ),
        }
