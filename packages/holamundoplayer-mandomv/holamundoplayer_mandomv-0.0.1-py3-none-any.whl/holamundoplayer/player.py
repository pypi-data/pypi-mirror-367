'''
Este es el modulo que incluye la clase del reproductor de música
'''


class Player:
    '''    Esta clase crea un reproductor de música    '''

    def play(self, song):
        '''
        Reproduce la canción que recibió como parametro 
        Parameters: 
        song (str): este es un string con el path de la canción
        Returns:
        int: devuelve 1 si reproduce con éxito, en caso de fracaso retorna 0
        '''
        print('Reproduciendo canción')

    def stop(self):
        print('Parando canción')
