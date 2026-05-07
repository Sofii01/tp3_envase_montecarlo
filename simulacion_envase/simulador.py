from __future__ import annotations

from .distribuciones import GeneradorAleatorio, GeneradorNormalBoxMuller, exponencial_desde_rnd
from .modelos import Acumuladores, FilaEstado, ResultadoSimulacion
from .parametros import ParametrosSimulacion


class SimuladorEnvase:
    """Ejecuta la simulación de Montecarlo del sistema de traslado de lotes."""

    def __init__(self, parametros: ParametrosSimulacion) -> None:
        parametros.validar()
        self.parametros = parametros
        self.generador = GeneradorAleatorio(parametros.semilla)
        self.generador_normal = GeneradorNormalBoxMuller(
            self.generador,
            media=parametros.media_tiempo_sector,
            desviacion=parametros.desviacion_tiempo_sector,
        )

    def simular(self) -> ResultadoSimulacion:
        """
        Ejecuta la simulación completa.

        No se guardan las N filas completas. El motor mantiene solo la fila
        anterior y la actual; aparte conserva únicamente las filas que deben
        mostrarse en pantalla y la fila N.
        """
        parametros = self.parametros
        acumuladores = Acumuladores()

        filas_seleccionadas: list[FilaEstado] = []
        inicio_visible = parametros.fila_inicial
        fin_visible = min(parametros.cantidad_jornadas, parametros.fila_inicial + parametros.filas_extra_visibles)

        fila_anterior: FilaEstado | None = None
        fila_actual: FilaEstado | None = None

        for jornada in range(1, parametros.cantidad_jornadas + 1):
            fila_actual = self._generar_fila(jornada)
            acumuladores.actualizar(fila_actual)
            fila_actual.aplicar_acumuladores(acumuladores)

            # Se conserva solo la fila anterior y la actual como estado de simulación.
            fila_anterior = fila_actual

            # Salida visible: solo las filas solicitadas, no todas las N filas.
            if inicio_visible <= jornada <= fin_visible:
                filas_seleccionadas.append(fila_actual)

        if fila_actual is None:
            raise RuntimeError("La simulación no generó filas.")

        # Variable mantenida para dejar explícito que el motor podría usar la fila anterior.
        _ = fila_anterior

        return ResultadoSimulacion(
            filas_seleccionadas=filas_seleccionadas,
            fila_final=fila_actual,
            cantidad_jornadas=parametros.cantidad_jornadas,
            fila_inicial=parametros.fila_inicial,
        )

    def _generar_fila(self, jornada: int) -> FilaEstado:
        parametros = self.parametros

        rnd_circuito = self.generador.rnd()
        cantidad_sectores = self._determinar_cantidad_sectores(rnd_circuito)
        recorrido_2_o_5 = cantidad_sectores in (2, 5)

        rnd_parada = self.generador.rnd()
        hay_parada = rnd_parada < parametros.prob_parada_escaneo
        rnd_demora_parada = self.generador.rnd() if hay_parada else None
        demora_escaneo = (
            exponencial_desde_rnd(parametros.media_demora_escaneo, rnd_demora_parada)
            if rnd_demora_parada is not None
            else 0.0
        )

        if recorrido_2_o_5:
            rnd_congestion = self.generador.rnd()
            hay_congestion = rnd_congestion < parametros.prob_congestion
        else:
            rnd_congestion = None
            hay_congestion = False

        rnd_auditoria = self.generador.rnd()
        hay_auditoria = rnd_auditoria < parametros.prob_auditoria
        rnd_demora_auditoria = self.generador.rnd() if hay_auditoria else None
        demora_auditoria = (
            exponencial_desde_rnd(parametros.media_demora_auditoria, rnd_demora_auditoria)
            if rnd_demora_auditoria is not None
            else 0.0
        )

        sorteos_normales = [self.generador_normal.sortear() for _ in range(cantidad_sectores)]
        tiempo_por_sector = sum(sorteo.valor for sorteo in sorteos_normales) / cantidad_sectores
        tiempo_base_traslado = sum(sorteo.valor for sorteo in sorteos_normales)

        demora_congestion = tiempo_base_traslado * parametros.aumento_congestion if hay_congestion else 0.0
        tiempo_parcial_paradas_auditorias = demora_escaneo + demora_auditoria
        tiempo_total = tiempo_base_traslado + demora_congestion + tiempo_parcial_paradas_auditorias

        return FilaEstado(
            jornada=jornada,
            rnd_circuito=rnd_circuito,
            cantidad_sectores=cantidad_sectores,
            rnd_parada=rnd_parada,
            hay_parada=hay_parada,
            rnd_demora_parada=rnd_demora_parada,
            demora_escaneo=demora_escaneo,
            recorrido_2_o_5_sectores=recorrido_2_o_5,
            rnd_congestion=rnd_congestion,
            hay_congestion=hay_congestion,
            rnd_auditoria=rnd_auditoria,
            hay_auditoria=hay_auditoria,
            rnd_demora_auditoria=rnd_demora_auditoria,
            demora_auditoria=demora_auditoria,
            rnd1_tiempo_base=sorteos_normales[0].rnd1,
            rnd2_tiempo_base=sorteos_normales[0].rnd2,
            normal_usada=f"N1..N{cantidad_sectores}",
            tiempo_por_sector=tiempo_por_sector,
            tiempo_base_traslado=tiempo_base_traslado,
            demora_congestion=demora_congestion,
            tiempo_parcial_paradas_auditorias=tiempo_parcial_paradas_auditorias,
            tiempo_total=tiempo_total,
        )

    def _determinar_cantidad_sectores(self, rnd: float) -> int:
        """Determina el circuito logístico según el RND acumulado."""
        parametros = self.parametros
        limite_2 = parametros.prob_circuito_2
        limite_4 = parametros.prob_circuito_2 + parametros.prob_circuito_4

        if rnd <= limite_2:
            return 2
        if rnd <= limite_4:
            return 4
        return 5
