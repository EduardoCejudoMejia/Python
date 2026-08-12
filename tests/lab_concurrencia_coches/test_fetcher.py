import asyncio

import httpx
import pytest

from app.lab_concurrencia_coches import (
    CocheFetcher,
    calcular_desgaste,
    calcular_desgastes_en_procesos,
)


def test_fetcher_sincrono_obtiene_una_ficha_por_url() -> None:
    def responder(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"modelo": request.url.path.rsplit("/", 1)[-1]})

    with httpx.Client(transport=httpx.MockTransport(responder)) as cliente:
        fichas = CocheFetcher().obtener_fichas_sincrono(
            ["https://coches.test/yaris", "https://coches.test/ibiza"], cliente
        )

    assert fichas == {
        "https://coches.test/yaris": {"modelo": "yaris"},
        "https://coches.test/ibiza": {"modelo": "ibiza"},
    }


def test_fetcher_async_respeta_el_limite_del_semaforo() -> None:
    activas = 0
    maximo_de_activas = 0

    async def responder(request: httpx.Request) -> httpx.Response:
        nonlocal activas, maximo_de_activas
        activas += 1
        maximo_de_activas = max(maximo_de_activas, activas)
        await asyncio.sleep(0.01)
        activas -= 1
        return httpx.Response(200, json={"modelo": request.url.path[1:]})

    async def ejecutar() -> dict[str, object]:
        transporte = httpx.MockTransport(responder)
        async with httpx.AsyncClient(transport=transporte) as cliente:
            return await CocheFetcher().obtener_fichas_async(
                [f"https://coches.test/{indice}" for indice in range(5)],
                cliente,
                max_concurrentes=2,
            )

    fichas = asyncio.run(ejecutar())

    assert len(fichas) == 5
    assert maximo_de_activas == 2


def test_fetcher_async_rechaza_un_limite_invalido() -> None:
    with pytest.raises(ValueError, match="max_concurrentes"):
        asyncio.run(CocheFetcher().obtener_fichas_async([], max_concurrentes=0))


def test_fetcher_propagates_errores_http() -> None:
    transporte = httpx.MockTransport(lambda _: httpx.Response(404))
    with httpx.Client(transport=transporte) as cliente:
        with pytest.raises(httpx.HTTPStatusError):
            CocheFetcher().obtener_fichas_sincrono(
                ["https://coches.test/inexistente"], cliente
            )


def test_calculo_cpu_bound_y_process_pool_producen_el_mismo_resultado() -> None:
    kilometrajes = [10, 100, 250]

    assert calcular_desgastes_en_procesos(kilometrajes) == [
        calcular_desgaste(kilometros) for kilometros in kilometrajes
    ]


def test_calculo_cpu_bound_no_acepta_kilometraje_negativo() -> None:
    with pytest.raises(ValueError, match="no pueden ser negativos"):
        calcular_desgaste(-1)
