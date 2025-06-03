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

# Imprime unidades e cursos
unidades = seletorUnidades.find_elements(By.TAG_NAME, "option")
for u in unidades:
	if (u.text == ""):
		continue
	print(u.text + ":")
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
			semestreIdeal = driver.find_element(By.CLASS_NAME, "duridlhab")
			print(f"{semestreIdeal.text} semestres")
		botaoBuscar.click()

print(f"Busca concluída em {time.time() - start:.2f} segundos.")

# Fecha o driver
driver.quit()