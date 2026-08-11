import logging
import time
from pathlib import Path

import httpx

# Configuración del logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class HttpClient:
    """
    - Realizar peticiones HTTP.
    - Aplicar timeout.
    - Reintentar errores temporales.
    - Descargar archivos mediante streaming.
    """

    def __init__(
        self,
        timeout: float = 10.0,
        max_retries: int = 3,
    ) -> None:

        # Tiempo máximo que esperamos por una petición.
        self.timeout = timeout

        # Número máximo de intentos.
        self.max_retries = max_retries

    # GET

    def get(self, url: str) -> httpx.Response:
        """
        Realiza una petición GET con reintentos.
        """

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "GET %s - intento %d",
                    url,
                    attempt,
                )

                # Creamos un cliente HTTP.
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(url)

                    # Si la respuesta contiene un código HTTP
                    # de error (4xx o 5xx), lanza una excepción.
                    response.raise_for_status()

                    logger.info(
                        "Respuesta recibida: %s",
                        response.status_code,
                    )

                    return response

            except httpx.TimeoutException:
                # El servidor tardó demasiado.
                logger.warning(
                    "Timeout en intento %d",
                    attempt,
                )

            except httpx.HTTPStatusError as error:
                # El servidor respondió pero con un código de error.
                logger.error(
                    "Error HTTP: %s",
                    error.response.status_code,
                )

                # Los errores HTTP normalmente no deberían
                # reintentarse indiscriminadamente.
                raise

            except httpx.RequestError as error:
                # Error de conexión, DNS, etc.
                logger.warning(
                    "Error de conexión: %s",
                    error,
                )

            # Esperamos antes de volver a intentar.
            if attempt < self.max_retries:
                wait_time = 2 ** (attempt - 1)

                logger.info(
                    "Esperando %d segundos antes de reintentar...",
                    wait_time,
                )

                time.sleep(wait_time)

        # Si llegamos aquí, todos los intentos fallaron.
        raise RuntimeError(f"No fue posible realizar GET {url}")

    # DOWNLOAD STREAMING

    def download(
        self,
        url: str,
        destination: str,
    ) -> None:
        """
        Descarga un archivo utilizando streaming.

        Los datos no se cargan completamente en memoria.
        """

        destination_path = Path(destination)

        logger.info(
            "Iniciando descarga: %s",
            url,
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    # stream() permite recibir la respuesta
                    # progresivamente.
                    with client.stream(
                        "GET",
                        url,
                    ) as response:
                        # Verificamos si el servidor respondió
                        # correctamente.
                        response.raise_for_status()

                        # Abrimos el archivo destino.
                        with destination_path.open("wb") as file:
                            # iter_bytes() entrega pequeños
                            # bloques de información.
                            for chunk in response.iter_bytes(chunk_size=8192):
                                # Escribimos inmediatamente el
                                # bloque en disco.
                                file.write(chunk)

                logger.info(
                    "Descarga completada: %s",
                    destination,
                )

                return

            except httpx.TimeoutException:
                logger.warning(
                    "Timeout durante la descarga. Intento %d",
                    attempt,
                )

            except httpx.RequestError as error:
                logger.warning(
                    "Error de conexión: %s",
                    error,
                )

            except httpx.HTTPStatusError as error:
                logger.error(
                    "Error HTTP: %s",
                    error.response.status_code,
                )

                # No reintentamos cualquier error HTTP.
                raise

            if attempt < self.max_retries:
                wait_time = 2 ** (attempt - 1)

                logger.info(
                    "Reintentando en %d segundos...",
                    wait_time,
                )

                time.sleep(wait_time)

        raise RuntimeError("No fue posible descargar el archivo.")
