from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Cria classes representando os dados
class Unidade:
    """Representa uma unidade da USP (ex: IME, Poli, etc.)"""
    def __init__(self, nome):
        self.nome = nome
        self.cursos = []

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
    WebDriverWait(driver, timeout=10).until(
        lambda d: len(d.find_elements(By.ID, "comboUnidade")) > 0
    )
    print(f"Acessando: {driver.title}")

def coletar_dados():
    start = time.time()
    driver = iniciar_driver(1)
    print("Abrindo o driver...\n")

    try:
        acessar_jupiter(driver)

        seletorUnidades = driver.find_element(By.ID, "comboUnidade")
        seletorCursos = driver.find_element(By.ID, "comboCurso")
        botaoEnviar = driver.find_element(By.ID, "enviar")
        botaoBuscar = driver.find_element(By.ID, "step1-tab")

        lista_unidades = seletorUnidades.find_elements(By.TAG_NAME, "option")
        resultado_unidades = []

        for unidade_elem in lista_unidades:
            nome_unidade = unidade_elem.text.strip()
            if not nome_unidade:
                continue

            print(f"{nome_unidade}:")

            unidade = Unidade(nome_unidade)
            unidade_elem.click()

            cursos_elem = seletorCursos.find_elements(By.TAG_NAME, "option")
            for curso_elem in cursos_elem:
                nome_curso = curso_elem.text.strip()
                if not nome_curso:
                    continue

                curso_elem.click()
                botaoEnviar.click()

                try:
                    aguardar_carregamento(driver)

                    if driver.find_elements(By.CLASS_NAME, "ui-widget-overlay"):
                        print(f"  -> [Erro] Falha ao recuperar {nome_curso}")
                        fechar = driver.find_element(By.CLASS_NAME, "ui-dialog-buttonset").find_element(By.CLASS_NAME, "ui-button")
                        fechar.click()
                        continue

                    driver.find_element(By.ID, "step4-tab").click()
                    aguardar_carregamento(driver)

                    WebDriverWait(driver, timeout=10).until(
                        lambda d: len(d.find_elements(By.CLASS_NAME, "disciplina")) > 0
                    )

                    html_content = driver.page_source
                    soup = BeautifulSoup(html_content, "html.parser")
                    # Processar as disciplinas com o BeautifulSoup

                    # curso = Curso(nome_curso, ...)
                    # unidade.cursos.append(curso)

                    print(f"  -> [OK] {nome_curso}")

                except Exception as e:
                    print(f"  -> [Erro] {nome_curso}: {e}")
                finally:
                    botaoBuscar.click()

            resultado_unidades.append(unidade)

    finally:
        driver.quit()
        print(f"\nBusca concluída em {time.time() - start:.2f} segundos.")

if __name__ == "__main__":
    coletar_dados()
