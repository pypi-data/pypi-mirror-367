import os


def get_user_from_enviorment_variable() -> str:
    """
    Función que regresa el nombre de usuario de Bitbucket desde la variable de
    entorno BITBUCKET_USERNAME

    Parámetros
    ----------
    Ninguno

    Notas
    -----
    Ninguna

    Ejemplos
    --------
    Obtener nombre de usuario
    >>> usuario = descarga_datos.util.get_user_from_enviorment_variable()
    """
    return os.environ["BITBUCKET_USERNAME"]


def get_password_from_enviormet_variable() -> str:
    """
    Función que regresa la contraseña de Bitbucket desde la variable de entorno
    BITBUCKET_PASSWORD

    Parámetros
    ----------
    Ninguno

    Notas
    -----
    Ninguna

    Ejemplos
    --------
    Obtener contraseña del usuario
    >>> contrasenia = descarga_datos.util.get_password_from_enviormet_variable()
    """
    return os.environ["BITBUCKET_PASSWORD"]
