from utils import coletar_dados
from utils import exbir_todos_cursos
from utils import exibir_dados_disciplinas
from utils import exibir_lista_unidades
from utils import obter_cursos_por_selecao
import sys

def mostrar_menu():
    print("-" * 100)
    print("[1] Listar cursos por Unidade")
    print("[2] Filtrar dados de um determinado curso (Não implementado)")
    print("[3] Exibir dados de todos os cursos")
    print("[4] Buscar dados de uma disciplina") 
    print("[5] Disciplinas que são usadas em mais de um curso (Não implementado)")
    print("[0] Sair")
    print("-" * 100)

def esperar_usuario():
    print("-" * 100)
    input("> Pressione Enter para continuar...")

def main():
    data = []
    execution_time = 0
    
    if len(sys.argv) == 1:
        data, execution_time = coletar_dados()
    elif len(sys.argv) == 2:
        unidadesLidas = sys.argv[1]
        data, execution_time = coletar_dados(unidadesLidas)
    else:
        print("Uso: python main.py [qtd_unidades]")
        sys.exit(1)

    print("-" * 100)
    print(f"Coleta concluída em {execution_time:.2f} segundos. Selecione uma das operações:")
    
    #Input do usuário
    while True:  
        mostrar_menu()
        op = input(("> Digite o número da operação desejada: "))

        #Selecionar opções 
        match op: 
            case '0': 
                print("-" * 100)
                print("Programa finalizado.")
                break
            
            case '1':
                # 1. Mostra a lista de unidades e guarda os nomes ordenados
                nomes_ordenados = exibir_lista_unidades(data)
                
                # 2. Se houver unidades, pede a entrada do usuário
                if nomes_ordenados:
                    print("-" * 100)
                    selecao = input("> Digite o número, sigla ou nome da unidade desejada: ")
                    
                    # 3. Obtém a lista de cursos com base na seleção
                    cursos = obter_cursos_por_selecao(data, selecao, nomes_ordenados)
                    
                    # 4. Exibe os cursos se a lista não for nula
                    if cursos is not None:
                        for curso in cursos:
                            print(f"  - {curso}")
                
                # 5. Espera o usuário pressionar Enter
                esperar_usuario()

            case '3':
                exbir_todos_cursos(data)
                esperar_usuario()

            case '4': 
                print("-" * 100)
                nome_disciplina = input("> Insira o nome da disciplina: ")
                exibir_dados_disciplinas(data, nome_disciplina)
                esperar_usuario()

            case _: 
                print("Operação inválida")
                esperar_usuario()

    sys.exit()

if __name__ == "__main__":
    main()