import os
import requests


def download_file_from_repo(url: str, filename: str):
    """
    Función que permite descargar archivos desde repositorios de bitbucket

    Parámetros
    ----------
    `url : str`
        Dirección de Bitbucket donde se encuentra el archivo

    `destionation_filename: str`
        Nombre y dirección del archivo donde se guardarán los datos descargados

    `user : str`
        Nombre de usuario de Bitbucket

    `password : str`
        Contraseña del usuario

    Notas
    -----
    Ninguna

    Ejemplos
    --------
    Descargar un archivo
    >>> usuario = descarga_datos.util.get_user_from_enviorment_variable()
    >>> contrasenia = descarga_datos.util.get_password_from_enviormet_variable()
    >>> url = 'https://bitbucket.org/usuario_prueba/repo_datos/raw/9fd54/datos.xlsx'
    >>> download_file(url, 'inst/extdata/datos.xlsx', usuario, contrasenia)
    """
    directory = os.path.split(url)[1]
    path = os.path.join(filename, directory)
    response = requests.request("GET", url)
    with open(path, "wb") as f:
        f.write(response.content)
