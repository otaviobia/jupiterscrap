class Curso:
    """Representa um curso oferecido por uma unidade da USP"""
    def __init__(self, nome, unidade, durIdeal, durMin, durMax, disObr, disOptElet=None, disOptLiv=None):
        self.nome = nome
        self.unidade = unidade
        self.durIdeal = durIdeal
        self.durMin = durMin
        self.durMax = durMax
        self.disObr = disObr
        self.disOptElet = disOptElet if disOptElet is not None else []
        self.disOptLiv = disOptLiv if disOptLiv is not None else []
    
    def getNome(self): 
        return self.nome 
    
    def getDurIdeal(self):
        return self.durIdeal
    
    def getDurMin(self): 
        return self.durMin

    def getDurMax(self): 
        return self.durMax
    
    def getDisObr(self): 
        return self.disObr

    def getDisOptElet(self):
        return self.disOptElet

    def getDisOptLiv(self):
        return self.disOptLiv