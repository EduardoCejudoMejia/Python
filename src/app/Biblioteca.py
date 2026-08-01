import json

RUTA = "/Users/cejudo/Documents/Cursos/Python/Axity/Python/src/app/resources/books.json"


# Funcionalidad que abre el json
def open_book():
    try:
        with open(RUTA, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except FileNotFoundError:
        print("No se encontró el archivo.")
        return []

    except json.JSONDecodeError:
        print("El archivo está vacío o tiene un formato JSON inválido.")
        return []

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return []


# Funcionalidad que muestra todos los libros
def show_books():
    for books in open_book():
        print(books)
    return books


# Funcionalidad que busca por coincidencia
def generic_searching():
    key = input(
        "Escribe el filtro de búsqueda: (name/author/editorial/year/category/available): "
    )
    value = input("Escribe lo que buscas acorde al filtro: ")

    books_list = open_book()

    for book in books_list:
        if book.get(key) == value:
            print(book)
            return book

    return print("No existen coincidencias")


# Funcionalidad de agregar libros
def adding_books():
    print("Agregando libros")

    name = input("Escribe el título del libro: ")
    author = input("Agrega el autor: ")
    editorial = input("Agrega la editorial: ")
    year = int(input("Agrega el año: "))
    category = input("Agrega el tópico: ")
    available = input("Disponible (true/false): ").lower() == "true"

    new_object = {
        "name": name,
        "author": author,
        "editorial": editorial,
        "year": year,
        "category": category,
        "available": available,
    }

    libros = open_book()
    libros.append(new_object)

    try:
        with open(RUTA, "w", encoding="utf-8") as archivo:
            json.dump(libros, archivo, indent=4, ensure_ascii=False)

        print("Libro agregado exitosamente.")

    except Exception as e:
        print(f"No fue posible guardar el libro: {e}")


# Funcionalidad que elimina un libro
def delete_book():
    name = input("Escribe el nombre del libro a eliminar: ")

    libros = open_book()

    for book in libros:
        if book.get("name").lower() == name.lower():
            libros.remove(book)

            with open(RUTA, "w", encoding="utf-8") as archivo:
                json.dump(libros, archivo, indent=4, ensure_ascii=False)

            print("Libro eliminado exitosamente.")
            return

    print("No se encontró ningún libro con ese nombre.")


def menu():
    while True:
        print("\n===== MENÚ =====")
        print("1. Agregar un libro")
        print("2. Mostrar todos los libros")
        print("3. Buscar un libro")
        print("4. Eliminar un libro")
        print("5. Salir")

        option = int(input("Selecciona una opción: "))

        match option:
            case 1:
                adding_books()
            case 2:
                show_books()
            case 3:
                generic_searching()
            case 4:
                delete_book()
            case 5:
                print("¡Hasta luego!")
                break
            case _:
                print("Opción inválida")


menu()
