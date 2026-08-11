from client import HttpClient


def main() -> None:

    # Creamos nuestro cliente HTTP.
    #
    # Timeout:
    # máximo 5 segundos esperando una respuesta.
    #
    # Retries:
    # máximo 3 intentos.
    client = HttpClient(
        timeout=5.0,
        max_retries=3,
    )

    # Ejemplo 1: consumir una API

    response = client.get("https://httpbin.org/get")

    print(response.json())

    # Ejemplo 2: descargar un archivo

    client.download(
        url="https://ash-speed.hetzner.com/100MB.bin",
        destination="/Users/cejudo/Documents/Cursos/Python/Axity/Python/src/app/downloads/",
    )


if __name__ == "__main__":
    main()
