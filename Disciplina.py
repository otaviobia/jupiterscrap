class Disciplina:
    """Representa uma disciplina cadastrada na grade curricular"""
    def __init__(self, codigo, nome, creditosAula, creditosTrabalho, cargaHoraria, cargaHorariaEstagio, cargaHorariaPraticas, atividadesAprofundamento):
        self.codigo = codigo
        self.nome = nome
        self.creditosAula = creditosAula
        self.creditosTrabalho = creditosTrabalho
        self.cargaHoraria = cargaHoraria
        self.cargaHorariaEstagio = cargaHorariaEstagio
        self.cargaHorariaPraticas = cargaHorariaPraticas
        self.atividadesAprofundamento = atividadesAprofundamento

    def getNome(self): 
        return self.nome 
    
    def getCodigo(self): 
        return self.codigo 

    def getCreditosAula(self): 
        return self.creditosAula 
    
    def getCreditosTrabalho(self): 
        return self.creditosTrabalho
    
    def getCargaHoraria(self): 
        return self.cargaHoraria
    
    def getCargaHorariaEstagio(self): 
        return self.cargaHorariaEstagio

    def getCargaHorariaPraticas(self): 
        return  self.cargaHorariaPraticas 
    
    def getAtividadesAprofundamento(self): 
        return self.atividadesAprofundamento