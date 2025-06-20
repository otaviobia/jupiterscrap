class Curso:
    """Representa um curso oferecido por uma unidade da USP"""
    def __init__(self, nome, unidade, durIdeal, durMin, durMax, disObr, disOptLiv, disOptEle):
        self.nome = nome
        self.unidade = unidade
        self.durIdeal = durIdeal
        self.durMin = durMin
        self.durMax = durMax
        self.disObr = disObr
        self.disOptLiv = disOptLiv
        self.disOptEle = disOptEle

