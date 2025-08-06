from .DataFile import DataFile


class Analysis:
    """
    Clase que representa al archivo analyses.json

    Parámetros
    ----------
    `name : str`
        Nombre del análisis

    `description : str`
        Descripción del análisis

    `image_tag : str`
        Etiqueta de la imágen de Docker en la que se genera el resultado

    `report : str`
        Nombre del archivo del reporte donde se presentan los resultados

    `results : list`
        Lista con el nombre de los resultados esperados

    `scripts : list`
        Lista de los programas involucrados en la creación de los resultados

    `data: list`
        Nombre de los archivos de datos de los que depende

    `requirements: list`
        Dependencias de paquetes necesarios para generar los resultados

    Atributos
    ----------
    `name : str`
        Nombre del análisis

    Métodos
    -------
    `is_dependent_on_datafile(filename: str): str`
        Verifica si este análisis depende de algún archivo especificado

    `get_url_to_datafile(filename: str, user: str): str`
        Regresa el url de donde se puede descargar el archivo de datos

    Notas
    -----
    None

    Ejemplos
    --------
    Ejemplo de como cargar un archivo analyses.json
    >>> with open('analyses.json', 'r') as archivo_analysis:
    ...     diccionario_analysis = json.loads(TEXTO_ANALYSIS)
    >>> analisis = Analysis(**diccionario_analysis[0])
    >>> analisis.get_url_to_datafile('archivo_ejemplo.csv')
    """

    def __init__(self, **kwargs):
        self.dictionary = {key: value for (key, value) in kwargs.items()}
        self._name = self.dictionary["name"]
        self._description = self.dictionary["description"]
        self._image_tag = self.dictionary["image_tag"]
        self._report = self.dictionary["report"]
        self._results = self.dictionary["results"]
        self._scripts = self.dictionary["scripts"]
        self._data = self._construct_datafile_array(self.dictionary["data"])
        self._setup_data = self._check_key("setup_data")
        self._docker_parent_image = self._check_key("docker_parent_image")

    def _check_key(self, key):
        if key in self.dictionary.keys():
            return self.dictionary[key]

    def _construct_datafile_array(self, data):
        archivos_datos = []
        for datos in data:
            archivos_datos.append(DataFile(**datos))
        return archivos_datos

    @property
    def name(self):
        return self._name

    def is_dependent_on_datafile(self, path: str, filename: str) -> bool:
        """
        Este método verifica si el análisis depende de algún archivo en específico

        Parámetros
        ----------
        `filename str`
            Nombre del archivo con el que se quiere verificar dependencia

        Notas
        -----
        Ninguna

        Ejemplos
        --------
        Verifica si el Analisis depende de un archivo de datos
        >>> with open('analyses.json', 'r') as archivo_analysis:
        ...     diccionario_analysis = json.loads(TEXTO_ANALYSIS)
        >>> analisis = Analysis(**diccionario_analysis[0])
        >>> analisis.is_dependent_on_datafile('archivo_ejemplo.csv')
        True
        """
        for archivo_datos in self._data:
            if archivo_datos.path == path and archivo_datos.filename == filename:
                return True
        return False

    def get_url_to_datafile(self, path: str, filename: str):
        """
        Regresa el url de donde se puede descargar el archivo desde Bitbucket

        Parámetros
        ----------
        `filename str`
            Usuario que es dueño del repositorio de datos, por default será IslasGECI

        `user str`
            Usuario que es dueño del repositorio de datos, por default será IslasGECI

        Notas
        -----
        Ninguna

        Ejemplos
        --------
        Obtener el url a un archivo de datos
        >>> with open('analyses.json', 'r') as archivo_analysis:
        ...     diccionario_analysis = json.loads(TEXTO_ANALYSIS)
        >>> analisis = Analysis(**diccionario_analysis[0])
        >>> analisis.get_url_to_datafile('archivo_ejemplo.csv')
        """
        for archivo_datos in self._data:
            if archivo_datos.path == path and archivo_datos.filename == filename:
                return archivo_datos.get_url_to_file()
        return None
