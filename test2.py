# Importa o Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Importa o BeautifulSoup
from bs4 import BeautifulSoup

# Importa o time e inicia timer
import time
start = time.time()

class Unidade:
	"""*É uma unidade. Você sente que poderia comentar melhor esse trecho."""
	def __init__(self, nome, cursos):
		self.nome = nome
		self.cursos = cursos

class Curso:
	"""*É um curso. Você sente que poderia comentar melhor esse trecho."""
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
	"""É uma disciplina. Você sente que poderia comentar melhor esse trecho."""
	def __init__(self, codigo, nome, creditosAula, creditosTrabalho, cargaHoraria, cargaHorariaEstagio, cargaHorariaPraticas, atividadesAprofundamento):
		self.codigo = codigo
		self.nome = nome
		self.creditosAula = creditosAula
		self.creditosTrabalho = creditosTrabalho
		self.cargaHoraria = cargaHoraria
		self.cargaHorariaEstagio = cargaHorariaEstagio
		self.cargaHorariaPraticas = cargaHorariaPraticas
		self.atividadesAprofundamento = atividadesAprofundamento

unidades = []
cursos = []
disciplinas = []

# Avisa usuário
print("Abrindo o driver...")

# Abre o driver
driver = webdriver.Firefox()

# Vai até a página do jupiterweb
driver.get("https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275")

# Imprime nome da página
print(f"Começando a busca em {driver.title}:\n")

wait = WebDriverWait(driver, timeout=10)
wait.until(lambda _ : len(driver.find_elements(By.ID, "comboUnidade")) != 0)

# Pega elementos pelo id
seletorUnidades = driver.find_element(By.ID, "comboUnidade")
seletorCursos = driver.find_element(By.ID, "comboCurso")
botaoEnviar = driver.find_element(By.ID, "enviar")
botaoBuscar = driver.find_element(By.ID, "step1-tab")

contador = 1

# Imprime unidades e cursos
unidades = seletorUnidades.find_elements(By.TAG_NAME, "option")
for u in unidades:
	if (u.text == ""):
		continue
	print(u.text + ":")
	unidades.append(Unidade(u.text, []))
	u.click()
	cursos = seletorCursos.find_elements(By.TAG_NAME, 'option')
	for c in cursos:
		if (c.text == ""):
			continue
		print(f"  -> {c.text} - ", end="")
		c.click()
		botaoEnviar.click()

		# Espera carregamento terminar)
		wait = WebDriverWait(driver, timeout=10)
		wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "blockPage")) 
			 and EC.invisibility_of_element_located((By.CLASS_NAME, "blockUI"))
			 and EC.invisibility_of_element_located((By.CLASS_NAME, "blockOverlay")))
		if (len(driver.find_elements(By.CLASS_NAME, "ui-widget-overlay")) != 0):
			print("Falha ao recuperar")
			errorDiv = driver.find_element(By.CLASS_NAME, "ui-dialog-buttonset")
			botaoFechar = errorDiv.find_element(By.CLASS_NAME, "ui-button")
			botaoFechar.click()
		else:
			gredeCurricular = driver.find_element(By.ID, "step4-tab")
			gredeCurricular.click()
			wait = WebDriverWait(driver, timeout=10)
			wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "blockPage")) 
			 and EC.invisibility_of_element_located((By.CLASS_NAME, "blockUI"))
			 and EC.invisibility_of_element_located((By.CLASS_NAME, "blockOverlay")))
			wait = WebDriverWait(driver, timeout=10)
			wait.until(lambda _ : len(driver.find_elements(By.CLASS_NAME, "disciplina")) != 0)
			html_content = driver.page_source
			# Usa BeautifulSoup para indexar a página
			soup = BeautifulSoup(html_content, "html.parser")
			contador+=1
		botaoBuscar.click()

print(f"Busca concluída em {time.time() - start:.2f} segundos.")

# Fecha o driver
driver.quit()