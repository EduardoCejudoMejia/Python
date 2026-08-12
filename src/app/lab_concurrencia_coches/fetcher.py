"""Ejemplos de E/S y CPU-bound para el laboratorio de concurrencia."""

import asyncio
import cProfile
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from timeit import timeit
from typing import Any

import httpx


class CocheFetcher:
    """Consulta fichas de coches desde URLs que devuelven JSON."""

    def obtener_fichas_sincrono(
        self, urls: list[str], cliente: httpx.Client | None = None
    ) -> dict[str, Any]:
        """Versión base: una petición termina antes de iniciar la siguiente."""
        if cliente is None:
            with httpx.Client() as cliente_local:
                return self.obtener_fichas_sincrono(urls, cliente_local)

        return {url: self._respuesta_json(cliente.get(url)) for url in urls}

    def obtener_fichas_con_hilos(
        self,
        urls: list[str],
        cliente: httpx.Client | None = None,
        max_trabajadores: int = 4,
    ) -> dict[str, Any]:
        """Alternativa para E/S bloqueante; no acelera cálculos de CPU por el GIL."""
        if cliente is None:
            with httpx.Client() as cliente_local:
                return self.obtener_fichas_con_hilos(
                    urls, cliente_local, max_trabajadores
                )

        with ThreadPoolExecutor(max_workers=max_trabajadores) as executor:
            respuestas = executor.map(cliente.get, urls)
        return {
            url: self._respuesta_json(respuesta)
            for url, respuesta in zip(urls, respuestas, strict=True)
        }

    async def obtener_fichas_async(
        self,
        urls: list[str],
        cliente: httpx.AsyncClient | None = None,
        max_concurrentes: int = 4,
    ) -> dict[str, Any]:
        """Hace E/S concurrente y limita peticiones en curso con un semáforo."""
        if max_concurrentes < 1:
            raise ValueError("max_concurrentes debe ser al menos 1.")
        if cliente is None:
            async with httpx.AsyncClient() as cliente_local:
                return await self.obtener_fichas_async(
                    urls, cliente_local, max_concurrentes
                )

        semaforo = asyncio.Semaphore(max_concurrentes)

        async def obtener_una(url: str) -> tuple[str, Any]:
            async with semaforo:
                respuesta = await cliente.get(url)
                return url, self._respuesta_json(respuesta)

        return dict(await asyncio.gather(*(obtener_una(url) for url in urls)))

    @staticmethod
    def _respuesta_json(respuesta: httpx.Response) -> Any:
        respuesta.raise_for_status()
        return respuesta.json()


def calcular_desgaste(kilometros: int) -> int:
    """Cálculo deliberadamente CPU-bound: ideal para usar procesos, no hilos."""
    if kilometros < 0:
        raise ValueError("Los kilómetros no pueden ser negativos.")
    return sum((kilometro * kilometro) % 97 for kilometro in range(kilometros))


def calcular_desgastes_en_procesos(
    kilometrajes: list[int], max_trabajadores: int = 2
) -> list[int]:
    """Distribuye cálculos independientes entre procesos y evita el GIL."""
    with ProcessPoolExecutor(max_workers=max_trabajadores) as executor:
        return list(executor.map(calcular_desgaste, kilometrajes))


def medir_sincrono(urls: list[str], repeticiones: int = 3) -> float:
    """Mide una versión síncrona. Usar sólo contra un servicio de pruebas local."""
    fetcher = CocheFetcher()
    return timeit(lambda: fetcher.obtener_fichas_sincrono(urls), number=repeticiones)


def perfilar_calculo(kilometros: int) -> cProfile.Profile:
    """Devuelve un perfil para inspeccionarlo con ``perfil.print_stats()``."""
    perfil = cProfile.Profile()
    perfil.enable()
    calcular_desgaste(kilometros)
    perfil.disable()
    return perfil
