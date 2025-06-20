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
