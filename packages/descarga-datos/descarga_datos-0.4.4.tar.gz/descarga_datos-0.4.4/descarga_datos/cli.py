from .internals import Analysis, read_json
from .network import download_file_from_repo
from descarga_datos.internals.setup_data import _adapt_columns
import sys


def descarga_archivo(file_name, destination_folder, path):
    lista_analisis = read_json("analyses.json")
    for diccionario_analisis in lista_analisis:
        analisis = Analysis(**diccionario_analisis)
        if analisis.is_dependent_on_datafile(path, file_name):
            download_file_from_repo(
                analisis.get_url_to_datafile(path, file_name), destination_folder
            )
            _adapt_columns(file_name, destination_folder)


def cli():
    descarga_archivo(*sys.argv[1:])
