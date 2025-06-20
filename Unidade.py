class Unidade:
    """Representa uma unidade da USP (ex: IME, Poli, etc.)"""
    def __init__(self, nome):
        self.nome = nome
        self.cursos = []

    #Função para inserir os cursos 
    def inserir_cursos(self, lista_cursos): 
        for curso in lista_cursos: 
            self.cursos.append(curso)

    def getNome(self): 
        return self.nome
    
    def getCursos(self): 
        return self.cursos