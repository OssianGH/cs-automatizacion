import sys
import csv
import pandas as pd
import pyodbc
from os.path import isfile
from tkinter import Tk
from tkinter.filedialog import askopenfilename

YEAR_MIN = 1900
YEAR_MAX = 2100
FIELD_COUNT = 19


def solicitar_archivo():
    """Solicita al usuario la selección de un archivo CSV o Excel.
    Devuelve el path al archivo seleccionado o si no se selecciona
    un archivo, termina la ejecución.
    """
    Tk().withdraw()

    archivo = askopenfilename(
        title="Seleccione el archivo para validar y cargar",
        filetypes=(
            ("Archivos CSV y Excel", "*.csv *.xlsx"),
            ("Todos los archivos", "*.*"),
        ),
    )

    if archivo is None or archivo == "":
        sys.exit(33)

    return archivo


def leer_archivo(archivo: str):
    """Abre el archivo CSV en la ruta `archivo`, lee y lo convierte
    a una lista de listas de strings donde cada fila es un registro
    y cada columna un campo
    """

    # Comprueba que el archivo exista
    if not isfile(archivo):
        print("Error: No existe el archivo: '" + archivo + "'")
        sys.exit(1)

    if archivo.endswith(".csv"):
        # Si es csv abre el archivo y retorna la lista
        with open(archivo, mode="r", newline="") as ar:
            archivoCSV = csv.reader(ar, delimiter=",", quotechar='"')
            return [registro for registro in archivoCSV][1:]

    if archivo.endswith(".xlsx"):
        # Si es xlsx abre el archivo y retorna la lista
        df = pd.read_excel(archivo)
        df = df.fillna("")
        return df.astype(str).values.tolist()

    # Si no es un archivo csv o xlsx
    print("Error: El archivo no es CSV ni XLSX.")
    sys.exit(2)


def validar_numero_campos(registros: list[list[str]], n_campos: int):
    """Comprueba si el numero de campos de cada registro en `registros`
    es de `n_campos`.
    """
    for i, registro in enumerate(registros):
        lon = len(registro)

        if lon > n_campos:
            # Si el registro actual supera el numero de campos
            # especificado, levanta un error indicando en qué
            # registro sucede y los campos excedentes
            print(
                "Error: El registro "
                + str(i + 2)
                + " tiene uno o más campos extras -> "
                + ",".join(registro[n_campos:])
            )
            sys.exit(3)

        if lon < n_campos:
            # Si el registro actual tiene menos campos del
            # especificado, levanta un error indicando en qué
            # registro sucede
            print(
                "Error: El registro " + str(i + 2) + " tiene menos campos del esperado"
            )
            sys.exit(4)


def validar_fecha(registros: list[list[str]], campo: int):
    """Comprueba si el número en el `campo` en cada registro en
    `registros` cumple el formato de fecha 'aaaammdd'.
    """
    for i, registro in enumerate(registros):
        valor = registro[campo - 1]

        # Valida la longitud del campo
        if len(valor) != 8:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", la fecha del campo "
                + str(campo)
                + " no cumple con el formato 'aaaammdd' -> '"
                + valor
                + "'"
            )
            sys.exit(5)

        # Valida el valor del año
        try:
            year = int(valor[0:4])
        except:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el año de la fecha del campo "
                + str(campo)
                + " no es un número entero -> '"
                + valor
                + "'"
            )
            sys.exit(6)

        # Valida el rango del año
        if year < YEAR_MIN or year > YEAR_MAX:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el año de la fecha del campo "
                + str(campo)
                + " no está en el rango permitido ["
                + str(YEAR_MIN)
                + ", "
                + str(YEAR_MAX)
                + "] -> "
                + valor
            )
            sys.exit(7)

        # Valida el valor del mes
        try:
            mes = int(valor[4:6])
        except:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el mes de la fecha del campo "
                + str(campo)
                + " no es un número entero -> '"
                + valor
                + "'"
            )
            sys.exit(8)

        # Valida el rango del mes
        if mes < 1 or mes > 12:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el mes de la fecha del campo "
                + str(campo)
                + " no está en el rango permitido -> "
                + valor
            )
            sys.exit(9)

        # Valida el valor del día
        try:
            dia = int(valor[6:8])
        except:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el día de la fecha del campo "
                + str(campo)
                + " no es un número entero -> '"
                + valor
                + "'"
            )
            sys.exit(10)

        diasMes = [
            31,
            28 if not biciesto(year) else 29,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ]
        # Valida el rango del día
        if dia < 1 or dia > diasMes[mes - 1]:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el día de la fecha del campo "
                + str(campo)
                + " no está en el rango permitido -> "
                + valor
            )
            sys.exit(11)

        # Una vez validado convierte a entero
        registro[campo - 1] = int(registro[campo - 1])


def validar_mes(registros: list[list[str]], campo: int):
    """Comprueba si el valor en el `campo` en cada registro en
    `registros` es un mes válido.
    """
    for i, registro in enumerate(registros):
        # Valida el valor del mes
        try:
            registro[campo - 1] = int(registro[campo - 1])
        except:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el valor del campo "
                + str(campo)
                + " no es un número entero -> '"
                + registro[campo - 1]
                + "'"
            )
            sys.exit(12)

        # Valida el rango del mes
        if registro[campo - 1] < 1 or registro[campo - 1] > 12:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el valor del campo "
                + str(campo)
                + " no es un mes válido -> "
                + registro[campo - 1]
            )
            sys.exit(13)


def validar_entero(registros: list[list[str]], campo: int):
    """Comprueba si el valor en el `campo` en cada registro en
    `registros` es un número entero.
    """
    for i, registro in enumerate(registros):
        # Intenta convertir el valor del campo del registro
        # actual en entero
        try:
            registro[campo - 1] = int(registro[campo - 1])
        except:
            # En caso de no poder convertir, levanta un error
            # indicando en qué registro sucede y el contenido
            # del campo que levantó el error
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el valor del campo "
                + str(campo)
                + " no es un número entero -> '"
                + registro[campo - 1]
                + "'"
            )
            sys.exit(14)

        # Comprueba que sea positivo
        if registro[campo - 1] < 0:
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el valor del campo "
                + str(campo)
                + " no es un número entero positivo -> "
                + registro[campo - 1]
            )
            sys.exit(15)


def validar_flotante(registros: list[list[str]], campo: int):
    """Comprueba si el valor en el `campo` en cada registro en
    `registros` es un número decimal.
    """
    for i, registro in enumerate(registros):
        registro[campo - 1] = registro[campo - 1].replace(",", "")

        # Intenta convertir el valor del campo del registro
        # actual en flotante
        try:
            registro[campo - 1] = float(registro[campo - 1])
        except:
            # En caso de no poder convertir, levanta un error
            # indicando en qué registro sucede y el contenido
            # del campo que levantó el error
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el valor del campo "
                + str(campo)
                + " no es un número flotante -> '"
                + registro[campo - 1]
                + "'"
            )
            sys.exit(16)


def validar_si_no(registros: list[list[str]], campo: int):
    """Comprueba si el valor en el `campo` en cada registro en
    `registros` es un 'SI' o 'NO' sin distinguir mayúsculas y
    minúsculas.
    """
    permitidos = ["SI", "NO"]

    for i, registro in enumerate(registros):
        registro[campo - 1] = registro[campo - 1].upper()

        if not registro[campo - 1] in permitidos:
            # En caso de que el valor del campo del registro
            # actual no sea ni 'SI' ni 'NO', levanta un error
            # indicando el registro actual y el contenido del
            # campo que levantó el error
            print(
                "Error: En el registro "
                + str(i + 2)
                + ", el valor del campo "
                + str(campo)
                + " no pertenece al conjunto {'SI', 'NO'} -> '"
                + registro[campo - 1]
                + "'"
            )
            sys.exit(17)


def biciesto(year):
    """Comprueba si el año es biciesto."""

    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def conectar_pyodbc(driver, server, base_datos, uid, pwd):
    """Realiza una conexión SQL con los parametros
    dados y devuelve el cursor de la conexión.
    """

    conexion = pyodbc.connect(
        f"DRIVER={driver};SYSTEM={server};DATABASE={base_datos};UID={uid};PWD={pwd};"
    )

    return conexion.cursor()


def migrar(cursor, registros):
    """Envía cada registro en `registros` a una tabla
    de base de datos asociada con el `cursor`.
    """

    cursor.executemany(
        "INSERT INTO ESQUEMA.TABLA VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        registros,
    )
    cursor.commit()


archivo = solicitar_archivo()
print(archivo)

print("Leyendo...")
registros = leer_archivo(archivo)

print("Validando...")
validar_numero_campos(registros, FIELD_COUNT)
validar_fecha(registros, 1)
validar_entero(registros, 2)
validar_mes(registros, 3)
validar_entero(registros, 5)
validar_entero(registros, 7)
validar_entero(registros, 9)
validar_entero(registros, 11)
validar_flotante(registros, 14)
validar_flotante(registros, 15)
validar_entero(registros, 16)
validar_si_no(registros, 19)

print("Cargando...")
cursor = conectar_pyodbc(
    "{DRIVER}", "SERVER", "BASE_DATOS", "USUARIO", "CONTRASEÑA"
)
migrar(cursor, registros)

print("Carga finalizada.")
