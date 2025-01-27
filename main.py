import asyncio

from prueba import get_access_token
from src import utils as utils
from src.activities import ActivitiesManager


def run_async_streams():
    access_token = get_access_token()
    print(
        asyncio.run(
            ActivitiesManager.get_all_streams(
                access_token,
                utils.id_activities,
                utils.streams_keys,
            )
        )
    )


def show_one_activity():
    access_token = get_access_token()
    print(ActivitiesManager(access_token).get_one_activity(13200148363))


def show_last_200_activities():
    access_token = get_access_token()
    print(ActivitiesManager(access_token).get_last_200_activities())


def print_options():
    print("\nElije una opción")

    print("\nStrava - Opciones:")
    print("1. Mostrar la información de una actividad concreta")
    print("2. Mostrar la información de las últimas 10 actividades")
    print("3. Mostrar las actividades de la semana en curso")
    print("4. Mostrar los streams de una actividad")
    print("5. Mostrar los streams de las actividades de la semana en curso")
    print("6. Mostrar un gráfico del tiempo en zona de una actividad en concreto")
    print("7. Mostrar el historial de commits")
    print("8. Salir")


def main():
    while True:
        print_options()
        choice = input("Selecciona una opción (1 al 8): ")

        match choice:
            case "1":
                show_one_activity()

            case "2":
                print("NO HAS CORRIDO")
            case "3":
                show_last_200_activities()

            case "4":
                print("NO HAS CORRIDO")
            case "5":
                print(run_async_streams())

            case "6":
                print("NO HAS CORRIDO")
            case "7":
                print("NO HAS CORRIDO")
            case "8":
                print("Saliendo")
                break
            case _:
                print("Opción no válida.")


if __name__ == "__main__":
    main()
