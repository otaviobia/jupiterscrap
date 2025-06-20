from bs4 import BeautifulSoup 
import requests

url = "https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275" 

response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

#Filtrando disciplinas 
div_principal = soup.find('div', id = 'gradeCurricular') 
if div_principal:
    linhas_tabela = div_principal.find('tbody').find_all('tr')

for linhas in linhas_tabela: 
    celulas = find_all('td') 
    
    if(celulas >= 3): 
        print(celulas)