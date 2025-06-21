from utils import coletar_dados 
from utils import listar_curso
from utils import listar_infos
import sys
 

if __name__ == "__main__":
    if len(sys.argv) == 1:
        data = coletar_dados()
    elif len(sys.argv) == 2:
        unidadesLidas = sys.argv[1]
        data = coletar_dados(unidadesLidas)
    else:
        print("Uso: python test.py [qtd_unidades]")


    #TODO Implementar interface 
    print("*-"*50) 
    print("Bem vindo! Selecione uma das operações:")
    print("*-"*50) 

    print("[1]Listar curso por Unidade")
    print("[2]Filtrar dados de um determinado curso")
    print("[3]Exibir dados de todos os cursos")
    print("[4]Dados de uma disciplina, inclusive quais cursos ela faz parte") 
    print("[5]Disciplinas que são usadas em mais de um curso")

    print("") 
    print("*-"*50)
    
    #Input do usuário
    while True:  
        op = int(input(("Digite o número da operação desejada: ")))

        #Selecionar opções 
        match op: 
            case 1: 
                nome_unidade = input("Insria o nome da unidade (Ex: Instituto de Ciências Matemáticas e da Computação - ( ICMC )): ")
                lista_curso = listar_curso(data, nome_unidade)
                listar_infos(lista_curso)
                break
            case _: 
                print("Operação inválida")




    sys.exit()





    #TODO
    #1)Listar curso por unidade (x)
    #2)Filtrar dados de um determinado curso 
    #3)Dados de todos os cursos
    #4)Dados de uma disciplina, inclusive quais cursos ela faz parte
    #5)Disciplinas que são usadas em mais de um curso
    #6)Outras consultas que você ache relevantes.