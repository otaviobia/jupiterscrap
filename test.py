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
    print(f"Acessando: {driver.title}")

def esperar_options_validos(driver, seletor_id, timeout=10):
    def _options_validos(driver):
        seletor = driver.find_element(By.ID, seletor_id)
        options = seletor.find_elements(By.TAG_NAME, "option")
        # Filtra options que não são vazias nem placeholders
        valid_options = [opt for opt in options if opt.text.strip() and "Selecione" not in opt.text]
        return len(valid_options) > 0
    WebDriverWait(driver, timeout).until(_options_validos)

def coletar_dados():
    start = time.time()
    driver = iniciar_driver(1)
    print("Abrindo o driver...\n")

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

        for unidade_elem in lista_unidades:
            nome_unidade = unidade_elem.text.strip()
            if not nome_unidade:
                continue

            print(f"{nome_unidade}:")
            unidade = Unidade(nome_unidade)

            unidade_elem.click()
            esperar_options_validos(driver, "comboCurso", timeout=10)
            seletorCursos = driver.find_element(By.ID, "comboCurso")
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
                    try:
                        WebDriverWait(driver, 1).until(
                            lambda d: len(d.find_elements(By.CLASS_NAME, "disciplina")) > 0
                        )
                        # Se passou daqui, tem disciplinas
                        html_content = driver.page_source
                        soup = BeautifulSoup(html_content, "html.parser")
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
        print(f"\nPrograma finalizado em {time.time() - start:.2f} segundos.")

if __name__ == "__main__":
    coletar_dados()
