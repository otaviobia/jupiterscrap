from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from Curso import Curso
from Unidade import Unidade
from Disciplina import Disciplina
from bs4 import BeautifulSoup
import time
import difflib

def clamp(value, min_value, max_value):
    """Prende um valor entre um limite inferior e superior"""
    return max(min_value, min(value, max_value))

def iniciar_driver(tipo):
    """Inicializa o driver com opções para reduzir logs no console."""
    if tipo == 0:  # Chrome
        options = Options()
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return webdriver.Chrome(options=options)
    else:  # Firefox
        return webdriver.Firefox()

def aguardar_carregamento(driver):
    """Espera bloqueios de carregamento (que não sejam dialogs) sumirem."""
    timeout = 10
    overlay_classes = ["blockPage", "blockUI", "blockOverlay"]
    for class_name in overlay_classes:
        try:
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, class_name))
            )
        except TimeoutException:
            pass

def acessar_jupiter(driver):
    """Abre a página principal"""
    driver.get("https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275")
    print(f"Driver aberto em {driver.title}, coletando dados...")

def esperar_options_validos(driver, seletor_id, timeout=10):
    """Espera até que as opções de um seletor sejam carregadas."""
    def _options_validos(driver):
        seletor = driver.find_element(By.ID, seletor_id)
        options = seletor.find_elements(By.TAG_NAME, "option")
        valid_options = [opt for opt in options if opt.text.strip() and "Selecione" not in opt.text]
        return len(valid_options) > 0
    WebDriverWait(driver, timeout).until(_options_validos)

def extrair_todas_disciplinas(soup):
    """
    Extrai todas as disciplinas (obrigatórias, eletivas, livres) de uma vez,
    percorrendo a grade curricular e mudando de 'seção' ao encontrar um cabeçalho.
    """
    obrigatorias = []
    eletivas = []
    livres = []
    
    div_grade = soup.find('div', id='gradeCurricular')
    if not div_grade:
        return obrigatorias, eletivas, livres

    current_section = None
    all_rows = div_grade.find_all('tr')

    for linha in all_rows:
        linha_text = linha.get_text().strip().lower()

        # Verifica se a linha é um cabeçalho de seção
        is_header = False
        if 'disciplinas obrigatórias' in linha_text:
            current_section = 'obrigatorias'
            is_header = True
        elif 'disciplinas optativas eletivas' in linha_text:
            current_section = 'eletivas'
            is_header = True
        elif 'disciplinas optativas livres' in linha_text:
            current_section = 'livres'
            is_header = True
        
        # Se for um cabeçalho, pula para a próxima iteração
        if is_header:
            continue

        # Se não for um cabeçalho, tenta processar como uma disciplina
        celulas = linha.find_all('td')
        if len(celulas) == 8:
            codigo = celulas[0].text.strip()
            nome = celulas[1].text.strip()
            
            # Garante que não é uma linha vazia ou de formatação
            if codigo and nome:
                disciplina = Disciplina(codigo, nome, converter_int(celulas[2].text.strip()), 
                                      converter_int(celulas[3].text.strip()), converter_int(celulas[4].text.strip()), 
                                      converter_int(celulas[5].text.strip()), converter_int(celulas[6].text.strip()), 
                                      converter_int(celulas[7].text.strip()))
                
                # Adiciona à lista da seção atual
                if current_section == 'obrigatorias':
                    obrigatorias.append(disciplina)
                elif current_section == 'eletivas':
                    eletivas.append(disciplina)
                elif current_section == 'livres':
                    livres.append(disciplina)

    return obrigatorias, eletivas, livres

def coletar_dados(quantidade = None):
    """
    Coleta os dados do JupiterWeb, exibindo uma linha de progresso detalhada
    e retornando os dados e o tempo de execução.
    """
    start = time.time()
    driver = iniciar_driver(0)
    print("Abrindo o driver... ", end='', flush=True)
    execution_time = 0

    try:
        acessar_jupiter(driver)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "comboUnidade")))
        
        print("Aguardando carregamento da lista de unidades... ", end='', flush=True)
        esperar_options_validos(driver, "comboUnidade", timeout=20)
        print("Lista de unidades carregada. Iniciando coleta...")

        botaoEnviar = driver.find_element(By.ID, "enviar")
        botaoBuscar = driver.find_element(By.ID, "step1-tab")
        lista_unidades_options = driver.find_element(By.ID, "comboUnidade").find_elements(By.TAG_NAME, "option")
        resultado_unidades = []
        padding_final = 180
        
        qnt = len(lista_unidades_options) if not quantidade else clamp(int(quantidade) + 1, 0, len(lista_unidades_options))
        
        total_unidades = qnt - 1
        if total_unidades <= 0:
            print("Nenhuma unidade encontrada para processar.")
            return [], 0

        for i in range(1, qnt):
            seletorUnidades = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "comboUnidade")))
            lista_unidades = seletorUnidades.find_elements(By.TAG_NAME, "option")
            nome_unidade = lista_unidades[i].text.strip()
            unidade = Unidade(nome_unidade)

            lista_unidades[i].click()
            esperar_options_validos(driver, "comboCurso", timeout=10)
            
            seletorCursos_options = driver.find_element(By.ID, "comboCurso").find_elements(By.TAG_NAME, "option")
            total_cursos_na_unidade = len(seletorCursos_options) - 1

            if total_cursos_na_unidade <= 0:
                progress_str = f"Unidade {i}/{total_unidades}: {nome_unidade} (Nenhum curso listado)"
                print(progress_str.ljust(padding_final), end='\r')
                time.sleep(0.2)

            for j in range(1, len(seletorCursos_options)):
                seletorCursos_loop = driver.find_element(By.ID, "comboCurso")
                lista_cursos_loop = seletorCursos_loop.find_elements(By.TAG_NAME, "option")
                nome_curso = lista_cursos_loop[j].text.strip()
                
                unit_info = f"Unidade {i}/{total_unidades}: {nome_unidade}"
                course_info = f"Curso {j}/{total_cursos_na_unidade}: {nome_curso}"
                full_progress_str = f"{unit_info} | {course_info}"
                print(full_progress_str.ljust(padding_final), end='\r')

                lista_cursos_loop[j].click()
                botaoEnviar.click()

                try:
                    try:
                        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-dialog-buttonset")))
                        fechar = driver.find_element(By.CLASS_NAME, "ui-dialog-buttonset").find_element(By.CLASS_NAME, "ui-button")
                        fechar.click()
                        WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.CLASS_NAME, "ui-widget-overlay")))
                        continue
                    except TimeoutException:
                        aguardar_carregamento(driver)

                    driver.find_element(By.ID, "step4-tab").click()
                    aguardar_carregamento(driver)
                    
                    try:
                        WebDriverWait(driver, 5).until(lambda d: len(d.find_elements(By.CLASS_NAME, "disciplina")) > 0)
                        html_content = driver.page_source
                        soup = BeautifulSoup(html_content, "html.parser")
                        
                        # Extração de todos os tipos de disciplinas com a nova função
                        obrigatorias, eletivas, livres = extrair_todas_disciplinas(soup)

                        info_curso = dados_curso(soup)
                        novo_curso = Curso(
                            nome=info_curso.get("nome"), unidade=info_curso.get("unidade"),
                            durIdeal=converter_int(info_curso.get("durIdeal")),
                            durMin=converter_int(info_curso.get("durMin")),
                            durMax=converter_int(info_curso.get("durMax")), 
                            disObr=obrigatorias,
                            disOptElet=eletivas,
                            disOptLiv=livres
                        )
                        unidade.cursos.append(novo_curso)
                    except TimeoutException:
                        pass
                except Exception as e:
                    print(f"\nOcorreu um erro inesperado ao processar o curso {nome_curso}: {e}")
                    pass
                finally:
                    aguardar_carregamento(driver)
                    botaoBuscar.click()
                    aguardar_carregamento(driver)
            
            resultado_unidades.append(unidade)

        print("".ljust(padding_final + 10), end='\r')

    finally:
        execution_time = time.time() - start
        if 'driver' in locals() and driver.service.is_connectable():
            driver.quit()

    return resultado_unidades, execution_time

def converter_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def dados_curso(soup):
    div_curso = soup.find('div', id="step4")
    if not div_curso: return {}
    return {
        "unidade": get_span_text(div_curso, 'unidade'), "nome": get_span_text(div_curso, 'curso'),
        "durIdeal": get_span_text(div_curso, 'duridlhab'), "durMin": get_span_text(div_curso, 'durminhab'),
        "durMax": get_span_text(div_curso, 'durmaxhab')
    }

def get_span_text(parent_tag, class_name):
    element = parent_tag.find('span', class_=class_name)
    return element.get_text(strip=True) if element else ""

def exibir_lista_unidades(resultado_unidades):
    """
    Exibe uma lista numerada de todas as unidades disponíveis e retorna a lista de nomes.
    """
    nomes_unidades = sorted([unidade.getNome() for unidade in resultado_unidades if unidade.getNome()])
    
    if not nomes_unidades:
        print("\n[AVISO] Nenhuma unidade foi encontrada nos dados coletados.")
        return None

    print("-" * 100)
    for i, nome in enumerate(nomes_unidades, 1):
        print(f"[{i}] {nome}")
    
    return nomes_unidades

def obter_cursos_por_selecao(resultado_unidades, selecao, nomes_unidades_ordenados):
    """
    Retorna a lista de cursos de uma unidade selecionada por número, sigla ou nome (fuzzy).
    """
    nome_unidade_selecionada = None
    selecao_upper = selecao.strip().upper()

    # 1. Tenta fazer a correspondência por sigla
    for nome_completo in nomes_unidades_ordenados:
        if nome_completo.endswith(')'):
            try:
                acronimo = nome_completo[nome_completo.rfind('(') + 1:-1].strip()
                if selecao_upper == acronimo:
                    nome_unidade_selecionada = nome_completo
                    break
            except IndexError:
                continue

    # 2. Se não encontrou, tenta por número
    if not nome_unidade_selecionada:
        try:
            num_selecao = int(selecao)
            if 1 <= num_selecao <= len(nomes_unidades_ordenados):
                nome_unidade_selecionada = nomes_unidades_ordenados[num_selecao - 1]
            else:
                print("-" * 100)
                print(f"Número '{num_selecao}' é inválido.")
                return None
        except ValueError:
            pass

    # 3. Se ainda não encontrou, tenta por nome (fuzzy search)
    if not nome_unidade_selecionada:
        matches = difflib.get_close_matches(selecao, nomes_unidades_ordenados, n=1, cutoff=0.6)
        if matches:
            nome_unidade_selecionada = matches[0]
        else:
            print("-" * 100)
            print(f"Nenhuma unidade encontrada para a seleção: '{selecao}'")
            return None

    # 4. Com o nome da unidade em mãos, busca os cursos
    for unidade in resultado_unidades:
        if unidade.getNome() == nome_unidade_selecionada:
            cursos_da_unidade = unidade.getCursos()
            if not cursos_da_unidade:
                print("  - Esta unidade não possui cursos listados.")
                return []
            
            print("-" * 100)
            print(f"Cursos oferecidos por: {nome_unidade_selecionada}")
            return [curso.getNome() for curso in cursos_da_unidade]
            
    return None

def exbir_todos_cursos(resultado_unidades):
    """Exibe os dados de todos os cursos de forma organizada."""
    if not resultado_unidades:
        print("\n[AVISO] A lista de dados está vazia. Execute a coleta de dados primeiro.")
        return
    for unidade in resultado_unidades:
        if not unidade.getCursos(): continue
        print(f"\n\n{'='*20}\nUNIDADE: {unidade.getNome()}\n{'='*20}")
        listar_infos(unidade.getCursos(), show_unit=False)

def exibir_dados_disciplinas(resultado_unidades, nome_dis):
    """Busca dados de uma disciplina por nome usando fuzzy search."""
    nomes_disciplinas = set()
    for unidade in resultado_unidades:
        for curso in unidade.getCursos():
            # Adiciona todos os tipos de disciplinas ao conjunto para busca
            todas_as_disciplinas = curso.getDisObr() + curso.getDisOptElet() + curso.getDisOptLiv()
            for disciplina in todas_as_disciplinas:
                nomes_disciplinas.add(disciplina.getNome())
    
    matches = difflib.get_close_matches(nome_dis, list(nomes_disciplinas), n=1, cutoff=0.6)
    if not matches:
        print("-" * 100)
        print(f"Nenhuma disciplina encontrada com nome similar a '{nome_dis}'.")
        return
        
    best_match_nome = matches[0]
    disciplina_encontrada = None
    lista_cursos_com_disciplina = []
    
    for unidade in resultado_unidades:
        for curso in unidade.getCursos():
            todas_as_disciplinas = curso.getDisObr() + curso.getDisOptElet() + curso.getDisOptLiv()
            for disciplina in todas_as_disciplinas:
                if disciplina.getNome() == best_match_nome:
                    lista_cursos_com_disciplina.append(curso.getNome())
                    if not disciplina_encontrada:
                        disciplina_encontrada = disciplina
    
    if disciplina_encontrada:
        print("-" * 100)
        print(f"Exibindo dados para a disciplina correspondente: '{best_match_nome}'")
        print(f"  Código: {disciplina_encontrada.getCodigo()}")
        print(f"  Créditos Aula: {disciplina_encontrada.getCreditosAula()}")
        print(f"  Créditos Trabalho: {disciplina_encontrada.getCreditosTrabalho()}")
        print(f"  Carga Horária: {disciplina_encontrada.getCargaHoraria()}")
    
    print("\nCursos que contêm esta disciplina:")
    if lista_cursos_com_disciplina:
        for curso in sorted(list(set(lista_cursos_com_disciplina))): 
            print(f"  - {curso}")
    else:
        print("  Nenhum curso encontrado.")


def listar_infos(cursos, show_unit=True):
    """Lista as informações de cursos e suas disciplinas obrigatórias, eletivas e livres."""
    for curso in cursos:
        print(f"\nCURSO: {curso.getNome()}")
        if show_unit:
            print(f"  UNIDADE: {curso.unidade}")
        print("-" * 40)
        print(f"  Duração (Mín./Ideal/Máx.): {curso.getDurMin()} / {curso.getDurIdeal()} / {curso.getDurMax()} semestres")

        # Exibe Disciplinas Obrigatórias
        disciplinas_obrigatorias = curso.getDisObr()
        print("\n  DISCIPLINAS OBRIGATÓRIAS:")
        if disciplinas_obrigatorias:
            for disciplina in disciplinas_obrigatorias:
                print(f"    - {disciplina.getNome()} (Cód: {disciplina.getCodigo()})")
        else:
            print("    - Nenhuma disciplina obrigatória encontrada.")

        # Exibe Disciplinas Optativas Eletivas
        disciplinas_eletivas = curso.getDisOptElet()
        print("\n  DISCIPLINAS OPTATIVAS ELETIVAS:")
        if disciplinas_eletivas:
            for disciplina in disciplinas_eletivas:
                print(f"    - {disciplina.getNome()} (Cód: {disciplina.getCodigo()})")
        else:
            print("    - Nenhuma disciplina optativa eletiva encontrada.")

        # Exibe Disciplinas Optativas Livres
        disciplinas_livres = curso.getDisOptLiv()
        print("\n  DISCIPLINAS OPTATIVAS LIVRES:")
        if disciplinas_livres:
            for disciplina in disciplinas_livres:
                print(f"    - {disciplina.getNome()} (Cód: {disciplina.getCodigo()})")
        else:
            print("    - Nenhuma disciplina optativa livre encontrada.")


def exibir_dados_curso(resultado_unidades, nome_curso_input):
    """Busca dados de um curso por nome usando fuzzy search."""
    todos_cursos = []
    for unidade in resultado_unidades:
        todos_cursos.extend(unidade.getCursos())

    nomes_cursos = [curso.getNome() for curso in todos_cursos]
    if not nomes_cursos:
        print("\n[AVISO] Nenhum curso encontrado nos dados coletados.")
        return

    matches = difflib.get_close_matches(nome_curso_input, nomes_cursos, n=1, cutoff=0.6)

    if not matches:
        print("-" * 100)
        print(f"Nenhum curso encontrado com nome similar a '{nome_curso_input}'.")
        return

    best_match_nome = matches[0]
    curso_encontrado = None
    for curso in todos_cursos:
        if curso.getNome() == best_match_nome:
            curso_encontrado = curso
            break

    if curso_encontrado:
        print("-" * 100)
        print(f"Exibindo dados para o curso correspondente: '{best_match_nome}'")
        listar_infos([curso_encontrado])
    else:
        print(f"\nErro ao tentar recuperar os dados do curso '{best_match_nome}'.")

def exibir_disciplinas_compartilhadas(resultado_unidades):
    """Exibe disciplinas que são utilizadas em mais de um curso."""
    disciplina_cursos = {}

    for unidade in resultado_unidades:
        for curso in unidade.getCursos():
            # Considera todos os tipos de disciplinas
            todas_as_disciplinas = curso.getDisObr() + curso.getDisOptElet() + curso.getDisOptLiv()
            for disciplina in todas_as_disciplinas:
                codigo_disciplina = disciplina.getCodigo()
                if codigo_disciplina not in disciplina_cursos:
                    disciplina_cursos[codigo_disciplina] = {
                        "nome": disciplina.getNome(),
                        "cursos": set()
                    }
                disciplina_cursos[codigo_disciplina]["cursos"].add(curso.getNome())

    disciplinas_filtradas = []
    for codigo, dados in disciplina_cursos.items():
        if len(dados["cursos"]) > 1:
            disciplinas_filtradas.append({
                "codigo": codigo,
                "nome": dados["nome"],
                "cursos": sorted(list(dados["cursos"]))
            })

    print("-" * 100)
    if not disciplinas_filtradas:
        print("Nenhuma disciplina encontrada em mais de um curso.")
        return

    disciplinas_filtradas.sort(key=lambda x: x["nome"])

    print("Disciplinas presentes em mais de um curso:")
    for item in disciplinas_filtradas:
        print(f"\n- DISCIPLINA: {item['nome']} (Cód: {item['codigo']})")
        print(f"  Presente em {len(item['cursos'])} cursos:")
        for nome_curso in item['cursos']:
            print(f"    - {nome_curso}")