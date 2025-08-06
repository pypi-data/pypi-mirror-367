from descarga_datos.utils import (
    get_password_from_enviormet_variable,
    get_user_from_enviorment_variable,
)


class DataFile:
    """
    Clase que representa un archivo de datos especificado como dependencia de
    algún analisis en analyses.json

    Parámetros
    ----------
    `source : str`
        Nombre del repositorio donde se encuentran los datos consignados

    `path : str`
        Ruta donde se encuentran consignados los datos dentro del repositorio

    `filename : str`
        Nombre del archivo de datos

    `version : str`
        Hash de la consignación en la que se encuentran los datos

    `type : str`
        Cadena de texto que representa el tipo de datos, ej. datapackage, gpx,
        csv, excel.

    Atributos
    ----------
    `filename : str`
        Cadena que representa el nombre del archivo

    `path : str`
        Cadena que representa la ruta de consignación del archivo


    Métodos
    -------
    `get_url_to_file(user: str): str`
        Regresa el url de donde se puede descargar el archivo de datos

    Notas
    -----
    None

    Ejemplos
    --------
    Crear un archivo
    >>> archivo = descargar_datos.internals.DataFile("repo_datos_inventado", "carpeta_datos",
                                                     "datos.csv", "9cc34")
    Obtener url a archivo
    >>> archivo.get_url_to_file()
    'https://bitbucket.org/IslasGECI/repo_datos_inventado/raw/9cc34/carpeta_datos/datos.csv'
    """

    def __init__(self, source: str, path: str, filename: str, version: str, type: str):
        self._source = source
        self._path = path
        self._filename = filename
        self._version = version
        self._type = type

    @property
    def filename(self):
        """
        Regresa el nombre del archivo
        """
        return self._filename

    @property
    def path(self):
        """
        Regresa el path
        """
        return self._path

    def get_url_to_file(self) -> str:
        """
        Regresa el url de donde se puede descargar el archivo desde Bitbucket.

        Parámetros
        ----------
        `user str`
            Usuario que es dueño del repositorio de datos, por default será IslasGECI

        Notas
        -----
        Ninguna

        Ejemplos
        --------
        Obtener url a archivo
        >>> archivo = descargar_datos.internals.DataFile("repo_datos_inventado", "carpeta_datos",
                                                         "datos.csv", "9cc34")
        >>> archivo.get_url_to_file()
        'https://bitbucket.org/IslasGECI/repo_datos/raw/9cc34/carpeta_datos/datos.csv'
        >>> archivo.get_url_to_file(user="usuario")
        'https://bitbucket.org/usuario/repo_datos/raw/9cc34/carpeta_datos/datos.csv'
        """
        bitbucket_username = get_user_from_enviorment_variable()
        bitbucket_password = get_password_from_enviormet_variable()
        base_url = f"https://{bitbucket_username}:{bitbucket_password}@api.bitbucket.org/2.0/repositories/IslasGECI/"
        return base_url + f"{self._source}/src/{self._version}/{self._path}/{self._filename}"
