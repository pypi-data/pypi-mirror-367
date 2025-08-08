"""
Este es el módulo que incluye la clase
de reproductor de música.
"""


class Player:
    """
    Esta clase crea un reproductor
    de música.
    """

    def play(self, song):
        """
        Reproduce la canción que recibio
        como parametro.

        Parameters:
        song (str): Este es un string con el Path de la canción.

        Returns:
        int: Devuelve 1 si reproduce con éxito, en caso de fracaso devuelve 0.
        """
        print("Reproduciendo música")

    def stop(self):
        print("Stop.")
