from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import sys
from bs4 import BeautifulSoup
import time

# Cria classes representando os dados
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

def clamp(value, min_value, max_value):
    """Prende um valor entre um limite inferior e superior"""
    return max(min_value, min(value, max_value))

def iniciar_driver(tipo):
    """Inicializa o driver"""
    return webdriver.Chrome() if tipo == 0 else webdriver.Firefox()

def aguardar_carregamento(driver):
    """Espera bloqueios de carregamento sumirem"""
    WebDriverWait(driver, timeout=10).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "blockPage"))
        and EC.invisibility_of_element_located((By.CLASS_NAME, "blockUI"))
        and EC.invisibility_of_element_located((By.CLASS_NAME, "blockOverlay"))
    )

def acessar_jupiter(driver):
    """Abre a página principal"""
    driver.get("https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275")
    print(f"Driver aberto em {driver.title}, coletando dados...")

def esperar_options_validos(driver, seletor_id, timeout=10):
    def _options_validos(driver):
        seletor = driver.find_element(By.ID, seletor_id)
        options = seletor.find_elements(By.TAG_NAME, "option")
        # Filtra options que não são vazias nem placeholders
        valid_options = [opt for opt in options if opt.text.strip() and "Selecione" not in opt.text]
        return len(valid_options) > 0
    WebDriverWait(driver, timeout).until(_options_validos)

def coletar_dados(quantidade = None):
    start = time.time()
    driver = iniciar_driver(1)
    print("Abrindo o driver... ", end='')

    try:
        acessar_jupiter(driver)

        seletorUnidades = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "comboUnidade"))
        )
        seletorCursos = driver.find_element(By.ID, "comboCurso")
        botaoEnviar = driver.find_element(By.ID, "enviar")
        botaoBuscar = driver.find_element(By.ID, "step1-tab")

        lista_unidades = seletorUnidades.find_elements(By.TAG_NAME, "option")
        resultado_unidades = []

        qnt = len(lista_unidades) if not quantidade else clamp(int(quantidade) + 1, 0, len(lista_unidades))
        
        for i in range(1, qnt):
            nome_unidade = lista_unidades[i].text.strip()

            print(f"{nome_unidade}:")
            unidade = Unidade(nome_unidade)

            lista_unidades[i].click()
            esperar_options_validos(driver, "comboCurso", timeout=10)
            seletorCursos = driver.find_element(By.ID, "comboCurso")
            lista_cursos = seletorCursos.find_elements(By.TAG_NAME, "option")
            for j in range(1, len(lista_cursos)):
                nome_curso = lista_cursos[j].text.strip()

                lista_cursos[j].click()
                botaoEnviar.click()

                try:
                    aguardar_carregamento(driver)

                    if driver.find_elements(By.CLASS_NAME, "ui-widget-overlay"):
                        print(f"  -> [Dados não encontrados] {nome_curso}")
                        fechar = driver.find_element(By.CLASS_NAME, "ui-dialog-buttonset").find_element(By.CLASS_NAME, "ui-button")
                        fechar.click()
                        continue

                    driver.find_element(By.ID, "step4-tab").click()
                    aguardar_carregamento(driver)
                    try:
                        WebDriverWait(driver, 1).until(
                            lambda d: len(d.find_elements(By.CLASS_NAME, "disciplina")) > 0
                        )
                        # Se passou daqui, tem disciplinas
                        html_content = driver.page_source
                        soup = BeautifulSoup(html_content, "html.parser")


                        #Dados das disciplinas
                        disciplina = dados_disciplinas(soup)
                        info_curso = dados_curso(soup) 


                        


                            


                        # Processa as disciplinas normalmente
                        print(f"  -> [OK] {nome_curso}")
                    except:
                        # Curso sem disciplinas
                        print(f"  -> [Ok] {nome_curso} (não tem disciplinas)")
                except Exception as e:
                    print(f"  -> [Erro] {nome_curso}: {e}")
                finally:
                    aguardar_carregamento(driver)
                    botaoBuscar.click()

            resultado_unidades.append(unidade)

    finally:
        driver.quit()
        print(f"Dados coletados em {time.time() - start:.2f} segundos.")

    return resultado_unidades 


#Funções adicionadas 
def converter_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def dados_disciplinas(soup): 

    div_grade = soup.find('div', id = 'gradeCurricular') 
                        
    if div_grade: 
        for linha in div_grade.find_all('tr'): 
            celulas = linha.find_all('td') 
        if len(celulas) == 1 and celulas[0].get('colspan') == '8': 
            continue
        
        if len(celulas) > 1 and celulas[0].get('colspan') == '2': 
            continue 
        
        if len(celulas) == 8: 
            codigo = celulas[0].text.strip() 
            nome = celulas[1].text.strip() 
            cred_aula = converter_int(celulas[2].text.strip())
            cred_trab = converter_int(celulas[3].text.strip())
            carga_horaria = converter_int(celulas[4].text.strip())
            ce = converter_int(celulas[5].text.strip()) 
            cp = converter_int(celulas[6].text.strip())
            atpa = converter_int(celulas[7].text.strip()) 
        
        disciplina = Disciplina(codigo, nome, cred_aula, cred_trab, carga_horaria, ce, cp, atpa) 

    return disciplina

def dados_curso(soup): 
    div_curso = soup.find('div', id="step4") 
    
    if not div_curso:
        return None

    # Extrai cada informação usando a função auxiliar
    unidade = get_span_text(div_curso, 'unidade')
    nome_curso = get_span_text(div_curso, 'curso')
    dur_ideal = get_span_text(div_curso, 'duridlhab')
    dur_min = get_span_text(div_curso, 'durminhab')
    dur_max = get_span_text(div_curso, 'durmaxhab')

    info_curso = Curso(curso, unidade, dur_ideal, dur_min, dur_max)
    
    return info_curso
    

def get_span_text(parent_tag, class_name):
    element = parent_tag.find('span', class_=class_name)
    return element.get_text(strip=True) if element else ""     


def listar_curso(resultado_unidades, sigla):

    for unidade in resultado_unidades: 
        if(sigla == unidade.getNome()): 
            resultados_cursos = (unidade.getCursos()).copy()
            return resultados_cursos
    
    return None 



    #TODO
    #1)Listar curso por unidade (x)
    #2)Filtrar dados de um determinado curso 
    #3)Dados de todos os cursos
    #4)Dados de uma disciplina, inclusive quais cursos ela faz parte
    #5)Disciplinas que são usadas em mais de um curso
    #6)Outras consultas que você ache relevantes.

 

if __name__ == "__main__":
    if len(sys.argv) == 1:
        coletar_dados()
    elif len(sys.argv) == 2:
        unidadesLidas = sys.argv[1]
        coletar_dados(unidadesLidas)
    else:
        print("Uso: python test.py [qtd_unidades]")
    sys.exit()