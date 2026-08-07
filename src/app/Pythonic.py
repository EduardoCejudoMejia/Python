import time
from contextlib import contextmanager

# Decorador de reintentos con backoff
callerList = {5: False, 10: False, 15: False, 20: True}


def backOff(function):
    # for key, value in callerList.items():
    def calling(a):
        for segundos, conexion in callerList.items():
            c = function(conexion)

            if conexion:
                print("Reintentos finalizados.")
                break

            print(f"Reintentando en {segundos} segundos...\n")
            time.sleep(segundos)

        return c

    return calling


@backOff
def reintentos(connected):
    if connected:
        c = print("Conexión reestablecida")
    else:
        c = print("Conexión fallida")
    return c


# reintentos(callerList) descoementar para ejecutar


# Generador por lotes y context manager de temporización
@contextmanager
def timer(name):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{name}: {time.perf_counter() - start:.2f}s")


def batch_generator(iterable, size):
    batch = []

    for item in iterable:
        batch.append(item)

        if len(batch) == size:
            yield batch
            batch = []

    if batch:
        yield batch


users = range(1, 10001)

with timer("Procesamiento total"):
    for batch in batch_generator(users, 1000):
        reintentos(callerList)
        sum(batch)
