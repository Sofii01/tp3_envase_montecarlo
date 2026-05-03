from dataclasses import dataclass


@dataclass(frozen=True)
class ParametrosSimulacion:
    """Parámetros configurables del sistema simulado."""

    cantidad_jornadas: int = 100_000
    fila_inicial: int = 1
    semilla: int | None = 12345

    # Circuitos logísticos internos
    prob_circuito_2: float = 0.25
    prob_circuito_4: float = 0.50
    prob_circuito_5: float = 0.25

    # Eventos probabilísticos
    prob_parada_escaneo: float = 0.55
    prob_congestion: float = 0.35
    prob_auditoria: float = 40 / 180

    # Distribuciones de tiempos, expresadas en minutos
    media_demora_escaneo: float = 4.0
    media_demora_auditoria: float = 5.0
    media_tiempo_sector: float = 4.0
    desviacion_tiempo_sector: float = 85 / 60

    # Impacto de la congestión
    aumento_congestion: float = 0.60

    # Cantidad de filas del vector de estado a mostrar desde fila_inicial.
    # "200 filas más abajo" implica 201 filas incluyendo la inicial.
    filas_extra_visibles: int = 200

    def validar(self) -> None:
        """Valida que los parámetros ingresados sean coherentes."""
        if self.cantidad_jornadas < 1:
            raise ValueError("La cantidad de jornadas N debe ser mayor o igual a 1.")

        if self.fila_inicial < 1 or self.fila_inicial > self.cantidad_jornadas:
            raise ValueError("La fila inicial debe estar entre 1 y N.")

        suma_circuitos = self.prob_circuito_2 + self.prob_circuito_4 + self.prob_circuito_5
        if abs(suma_circuitos - 1.0) > 1e-9:
            raise ValueError("Las probabilidades de los circuitos deben sumar 1.")

        for nombre, valor in [
            ("prob_parada_escaneo", self.prob_parada_escaneo),
            ("prob_congestion", self.prob_congestion),
            ("prob_auditoria", self.prob_auditoria),
        ]:
            if not 0 <= valor <= 1:
                raise ValueError(f"{nombre} debe estar entre 0 y 1.")

        for nombre, valor in [
            ("media_demora_escaneo", self.media_demora_escaneo),
            ("media_demora_auditoria", self.media_demora_auditoria),
            ("media_tiempo_sector", self.media_tiempo_sector),
            ("desviacion_tiempo_sector", self.desviacion_tiempo_sector),
            ("aumento_congestion", self.aumento_congestion),
        ]:
            if valor < 0:
                raise ValueError(f"{nombre} no puede ser negativo.")
