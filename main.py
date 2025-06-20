from utils import coletar_dados 
from utils import sys
 

if __name__ == "__main__":
    if len(sys.argv) == 1:
        coletar_dados()
    elif len(sys.argv) == 2:
        unidadesLidas = sys.argv[1]
        coletar_dados(unidadesLidas)
    else:
        print("Uso: python test.py [qtd_unidades]")
    sys.exit()



    #TODO
    #1)Listar curso por unidade (x)
    #2)Filtrar dados de um determinado curso 
    #3)Dados de todos os cursos
    #4)Dados de uma disciplina, inclusive quais cursos ela faz parte
    #5)Disciplinas que são usadas em mais de um curso
    #6)Outras consultas que você ache relevantes.