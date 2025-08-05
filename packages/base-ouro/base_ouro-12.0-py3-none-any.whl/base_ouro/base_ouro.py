import re
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from datetime import datetime as dt
pd.options.mode.chained_assignment = None  # default='warn'


def separa_turma(turma: str) -> list:
    """Separa o nome da turma por hífen e realiza a limpeza dos dados para padronização.

    Args:
        turma (str): Nome da turma

    Returns:
        list: Lista com as informações da turma
    """
    return [re.sub(r"\d+", "", str_turma.strip()) for 
            str_turma in turma.split('-')]


def encontra_periodo(tipo_turma: str) -> str:
    """Busca no nome da turma o período em que está sendo ofertada.
    Alguns casos tem o valor fixado, sendo eles:
    - LIBRAS: Será de 10º período, exceto para o curso de Serviço Social de Curitiba (CSSC) onde é do 8º
    - LEA: Será de 2º período, exceto para o campus de Londrina onde é 3º
    - CIDE: Programa da Diretoria de Identidade do 1º período
    - Fora de formatação (sem '-'): Não tem retorno

    Args:
        tipo_turma (str): Nome da turma

    Returns:
        str: Período da turma
    """
    if 'LIBRAS' in tipo_turma:
        return '8' if 'CSSC' in tipo_turma else '10'
    if 'LEA' in tipo_turma:
        return '3' if 'LDN' in tipo_turma else '2'
    if 'CIDE' in tipo_turma:
        return '1'
    if '-' not in tipo_turma:
        return ''

    tipo_turma = tipo_turma.split('-')[1].strip()
    periodo = ''
    for ch in tipo_turma:
        if ch in '0123456789':
            periodo += ch
        else:
            break
    return periodo


def encontra_cr(turma: str, dict_sigla_cr: dict) -> str:
    """Busca no dicionário de Siglas, o cr do curso. 
    Utiliza como base o nome da turma, para realizar as tratativas e obter a sigla.

    Args:
        turma (str): Nome da turma
        dict_sigla_cr (dict): Dicionário contendo a reglação da Sigla do curso com o CR de oferta

    Returns:
        str: CR de oferta
    """
    if '-' not in turma:
        return ''
    else:
        turma = separa_turma(turma)
        if 'LEA' in turma or 'LIBRAS' in turma:
            validador = turma[0]
        elif 'INTERCAMBIO' in turma:
            validador = f'{turma[0]} {turma[1]}'
        else:
            validador = f'{turma[0]} {turma[2]}'
        return dict_sigla_cr.get(validador, '')


def encontra_curso(turma: str, dict_sigla_curso: dict) -> str:
    """Busca no dicionário de Siglas, o nome do curso. 
    Utiliza como base o nome da turma, para realizar as tratativas e obter a sigla.

    Args:
        turma (str): Nome da turma
        dict_sigla_curso (dict): Dicionário contendo a reglação da Sigla do curso com o nome do curso de oferta

    Returns:
        str: Nome do curso de oferta
    """
    turma = separa_turma(turma)
    if 'INTERCAMBIO' in turma:
        cod_turma = f'{turma[0]} {turma[1]}'
    else:
        cod_turma = turma[0]
    return dict_sigla_curso.get(cod_turma, '')


def encontra_escola(turma: str, dict_cr_escola: dict) -> str:
    """Busca no dicionário de CR, o nome da Escola. 

    Args:
        cr (str): CR de oferta
        dict_cr_escola (dict): Dicionário contendo a reglação do CR de oferta e do Nome da Escola

    Returns:
        str: Nome da Escola
    """
    turma = separa_turma(turma)[0]
    return dict_cr_escola.get(turma, '')


def trata_turma(df: pd.DataFrame, coluna_validacao: str) -> pd.DataFrame:
    """Trata o nome da turma para obter a Sigla.
    - Caso a coluna de validação seja do CR irá trazer também o turno, se não for uma das turmas com tratamento especial
    - Caso a turma seja LEA, LIBRAS, LETTC, ISOLADAS ou CIDE, irá sempre trazer apenas a Sigla
    - Caso a turma seja de INTERCAMBIO a Sigla será acompanhada de INTERCAMBIO

    Args:
        df (pd.DataFrame): Tabela com o nome das turmas para serem tratadas
        coluna_validacao (str): Nome da coluna, para realizar a validação de tratativa

    Returns:
        pd.DataFrame: Tabela com o nome das turmas tratados
    """
    for i in range(len(df)):
        turma = separa_turma(df[i])
        if coluna_validacao == 'CR Curso' \
                and 'LEA' not in df[i] \
                and 'LIBRAS' not in df[i] \
                and 'LETTC' not in df[i] \
                and 'INTERCAMBIO' not in df[i] \
                and 'ISOLADAS' not in df[i] \
                and 'CIDE' not in df[i]:
            sigla = f'{turma[0].strip()} {turma[2].strip()}'
        else:
            if 'INTERCAMBIO' in turma and coluna_validacao != '':
                sigla = f'{turma[0].strip()} {turma[1].strip()}'
            else:
                sigla = f'{turma[0].strip()}'
        df[i] = sigla
    return df


def trata_df_turma(df: pd.DataFrame, coluna_validacao: str) -> pd.DataFrame:
    """Chama a função para tratamento no nome das turmas. E remove os dados duplicados.

    Args:
        df (pd.DataFrame): Dataframe que será tratado
        coluna_validacao (str): Nome das coluna do Dataframe, que serão usados para validações posteriores

    Returns:
        pd.DataFrame: Dataframe com as turmas renomeadas no formato tratado
    """
    colunas = df.columns.to_list()

    df[colunas[0]] = trata_turma(df[colunas[0]], coluna_validacao).astype(dtype='str', errors='ignore')
    df = df.drop_duplicates().reset_index(drop=True)
    return df


def sigla_cr_curso(df: pd.DataFrame) -> dict:
    """Realiza as tratativas do Dataframe para transformar em um dicionário, 
    que será utilizado para realizar o preenchimento dos dados da disciplina para nº de CR e nome de Curso.
    Há dois possíveis dicionários que podem ser criados:
    - Sigla x CR: Caso o Dataframe não contenha a coluna Curso
    - Sigla x Curso: Caso o Dataframe contenha a coluna Curso

    Args:
        df (pd.DataFrame): Dataframe com as informações que serão transformadas em i

    Returns:
        dict: Dicionário de dados contendo a relação Sigla x CR | Nome do Curso
    """
    dict_turmas = {}
    colunas = df.columns.values.tolist()
    info = df.sort_values(by=[colunas[0], colunas[1]])
    info[colunas[-1]] = info[colunas[-1]].fillna(0).astype(dtype='int', errors='ignore') \
        .astype(dtype='str', errors='ignore')
    info = info.drop_duplicates().reset_index(drop=True)

    # A eletiva é tratada separada das demais, pois algumas turmas, possuem CRs distintos de suas contrapartes Regulares
    eletivas = ['U1', 'U2', 'U3']
    info_eletivas = trata_df_turma(info[info[colunas[0]].str.contains('|'.join(eletivas))]
                                    .reset_index(drop=True), colunas[1])
    
    info = info[~info[colunas[0]].str.contains('|'.join(eletivas))].reset_index(drop=True)
    info = trata_df_turma(info, colunas[1])

    # Para complementar o dicionário, verifica e insere as chaves que foram encontradas apenas nas eletivas
    for index, row in info_eletivas.iterrows():
        if info_eletivas[colunas[0]][index] not in info[colunas[0]].values:
            valor = info_eletivas[colunas[0]][index]
            info_faltante = info_eletivas[info_eletivas[colunas[0]].str.contains(valor)]
            info = pd.concat([info, info_faltante], ignore_index=True)
    info = info.loc[(info[colunas[-1]] != ' ') & (info[colunas[-1]] != '0')].reset_index(drop=True)

    # Cria o dicionário
    for index, row in info.iterrows():
        dict_turmas[info[colunas[0]][index]] = info[colunas[1]][index]
        if colunas[1] == 'Curso':
            if info[colunas[1]][index] == 'Multicom' or \
                    info[colunas[1]][index] == 'Humanidades' or \
                    info[colunas[1]][index] == 'Engenharia':
                cr = info[colunas[-1]][index]
                curso = info.loc[(info[colunas[-1]] == cr) & (info[colunas[1]] != info[colunas[1]][index])]
                dict_turmas[info[colunas[0]][index]] = curso[colunas[1]].to_list()[0]
    return dict_turmas


def sigla_escola(df_curso: pd.DataFrame, df_escola: pd.DataFrame) -> dict:
    """Realiza as tratativas do Dataframe para transformar em um dicionário, 
    que será utilizado para realizar o preenchimento dos dados da disciplina para Nome da Escola.
    Utiliza duas bases, uma que traz o nome dos Cursos e outra que traz o nome das Escolas.
    - O nome do curso é utilizado exclusivamente para tratamentos pontuais e específicos.

    Args:
        df_curso (pd.DataFrame): Dataframe com as informações que serão utilizadas para tratamentos
        df_escola (pd.DataFrame): Dataframe com as informações que serão transformadas em dicionário

    Returns:
        dict: Dicionário de dados contendo a relação Sigla x Nome da Escola
    """
    dict_escola = {}
    escola = df_escola.sort_values(by=['Estabelecimento', 'Escola', 'Turma']) \
        .drop_duplicates().reset_index(drop=True)
    escola['Turma'] = trata_turma(escola['Turma'], '').astype(dtype='str', errors='ignore')
    escola = escola.drop_duplicates().reset_index(drop=True)
    escola['Escola'] = escola['Escola'] \
        .str.replace('Escola de ', '') \
        .str.replace('Escola ', '')
    escola['Estabelecimento'] = escola['Estabelecimento'].str.replace(
        'Pontifícia Universidade Católica do Paraná - ', '')
    curso = df_curso.sort_values(by=['Turma', 'Curso']).drop_duplicates().reset_index(drop=True)
    curso['Turma'] = trata_turma(curso['Turma'], '').astype(dtype='str', errors='ignore')
    curso = curso.drop_duplicates().reset_index(drop=True)
    curso.rename(columns={'Curso': 'Escola'}, inplace=True)
    for index, row in curso.iterrows():
        valida_curso = curso['Escola'][index]
        # Trata a Escola dos Programas
        if valida_curso == 'Identidade':
            dict_escola[curso['Turma'][index]] = 'Administração da Diretoria de Relações Internas'
        elif curso['Turma'][index] == 'COPA':
            dict_escola[curso['Turma'][index]] = 'Open Academy'
        # Trata a Escola dos Eixos 
        elif valida_curso == 'Engenharia':
            dict_escola[curso['Turma'][index]] = 'Politécnica'
        elif valida_curso == 'Multicom':
            dict_escola[curso['Turma'][index]] = 'Belas Artes'
        elif valida_curso == 'Humanidades' or 'LEA' in curso['Turma'][index]:
            dict_escola[curso['Turma'][index]] = 'Educação e Humanidades'
        # Trata a Escola dos Programas e Eixos de Campus Fora de Sede
        elif curso['Turma'][index] == 'LDN':
            dict_escola[curso['Turma'][index]] = 'Londrina'
        elif curso['Turma'][index] == 'TLD':
            dict_escola[curso['Turma'][index]] = 'Toledo'
        else:
            info = escola.loc[(escola['Turma'] == curso['Turma'][index])].reset_index(drop=True)
            if info.empty:
                info.loc[0] = ['', '', '']
            # Trata a Escolas dos Campus Fora de Sede
            if (info['Estabelecimento'][0] == 'Londrina'
                    or info['Estabelecimento'][0] == 'Toledo'):
                dict_escola[curso['Turma'][index]] = info['Estabelecimento'][0]
            # Trata nomenclatura da Escola de Medicina e Ciências da Vida, caso esteja separado
            elif (info['Escola'][0] == 'Ciências da Vida'
                  or info['Escola'][0] == 'Medicina'):
                dict_escola[curso['Turma'][index]] = 'Medicina e Ciências da Vida'
            else:
                dict_escola[curso['Turma'][index]] = info['Escola'][0]
    return dict_escola



def trata_relatorio_ch(df: pd.DataFrame) -> pd.DataFrame:
    """Trata o relatório de CH e cria uma chave para ser criada a relação com os demais dados.

    Args:
        df (pd.DataFrame): Dataframe que será tratado

    Returns:
        pd.DataFrame: Dataframe tratado
    """
    ch_tratado = df[['CR Curso', 'Turma', 'Disciplina', 'C.H. Relógio Oficial']]
    ch_tratado['CR Curso'] = pd.to_numeric(ch_tratado['CR Curso'], errors='coerce')

    ch_tratado['CR Curso'] = ch_tratado['CR Curso'].fillna(0.0).astype(int)

    ch_tratado.insert(0, 'Validador', '', True)
    ch_tratado['Validador'] = ch_tratado.apply(lambda row: f"{str(row['CR Curso']).strip()}    "
                                                           f"{str(row['Turma']).strip()}    "
                                                           f"{str(row['Disciplina']).strip()}", axis=1)

    ch_tratado = ch_tratado[['Validador', 'C.H. Relógio Oficial']]

    return ch_tratado


def filtra_alunos(df: pd.DataFrame) -> pd.DataFrame:
    """Realiza o filtro dos estudantes, para remover estudantes com contratos duplicados para o mesmo curso.

    Args:
        df (pd.DataFrame): Dataframe que será tratado

    Returns:
        pd.DataFrame: Dataframe tratado
    """
    ndf = df.loc[:, ('Estabelecimento', 'Matrícula', 'Nome Completo', 'Turma Aluno', 'DT_CADASTRO_CONTRATO')] \
        .sort_values(by=['Matrícula', 'Turma Aluno', 'DT_CADASTRO_CONTRATO']).drop_duplicates().reset_index(drop=True)
    c = ndf.loc[:, ('Matrícula', 'Turma Aluno', 'Estabelecimento')].groupby('Matrícula').value_counts()
    incorretos = []
    index = c.index.tolist()
    valores = c.tolist()
    for i in range(len(c.index)):
        if valores[i] >= 2:
            tdf = ndf.loc[ndf['Matrícula'] == index[i][0]].sort_values(by='DT_CADASTRO_CONTRATO').reset_index(drop=True)
            for item in range(len(tdf.index)):
                if tdf['DT_CADASTRO_CONTRATO'][item] != tdf['DT_CADASTRO_CONTRATO'].iat[-1]:
                    incorretos.append(f"{str(tdf['Matrícula'][item]).strip()} "
                                      f"{str(tdf['Turma Aluno'][item].strip())} "
                                      f"{str(tdf['DT_CADASTRO_CONTRATO'][item]).strip()}")
    df.insert(0, 'Validador', '', True)
    df['Validador'] = df.apply(lambda row: f"{str(row['Matrícula']).strip()} "
                                           f"{str(row['Turma Aluno']).strip()} "
                                           f"{str(row['DT_CADASTRO_CONTRATO']).strip()}", axis=1)
    if len(incorretos) > 0:
        df = df[~df['Validador'].str.contains('|'.join(incorretos))].reset_index(drop=True)
    del df['Validador']
    return df


def recebe_arquivos(alunos: str, disciplinas: str, ch: str, name: str):
    """Trata os dados recebidos para geração da Base Ouo

    Args:
        alunos (str): Caminho do arquivo de Alunos/Pais Exportação
        disciplinas (str): Caminho do arquivo de Disciplinas/Turma Destino (Relatório SQL)
        ch (str): Caminho do arquivo do Professor - CH/Turma Disciplina
        name (str): Caminho e nome para salvar o arquivo da Base Ouro
    """
    print('Gerando a base ouro...')

    # Relatório Alunos Pais Exportação
    df_alunos = pd.read_excel(alunos)

    df_alunos = df_alunos[[
        'Estabelecimento', 'Escola', 'Centro de Resultado', 'Curso', 'Série', 'Matrícula',
        'Nome Completo', 'CPF', 'Data de Nascimento', 'Usuário Internet', 'E-mail', 'Telefone Celular',
        'Situação Acadêmica', 'Tipo de Entrada', 'Tipo de Ingresso', 'Turma', 'Turno', 'Gênero'
    ]]
    df_alunos = df_alunos.loc[df_alunos["Situação Acadêmica"] == 'Matriculado Curso Normal']
    df_alunos = df_alunos.drop_duplicates()

    # Relatório Disicplinas SQL
    df_disciplinas = pd.read_excel(disciplinas)
    df_disciplinas = df_disciplinas[[
        'CODIGO', 'DT_CADASTRO_CONTRATO', 'TURMA_BASE', 'DISCIPLINA', 'TURMA_DISCIPLINA', 'DIVISAO', 'DIVISAO2'
    ]]
    df_disciplinas = df_disciplinas.drop_duplicates()

    # Relatório CH Turma
    df_ch = pd.read_excel(ch)
    # Dicionário de cr
    dict_sigla_cr = sigla_cr_curso(df_ch.loc[:, ('Turma', 'CR Curso')])
    # Dicionário de curso
    dict_sigla_curso = sigla_cr_curso(df_ch.loc[:, ('Turma', 'Curso', 'CR Curso')])
    # Dicionário de escola
    dict_sigla_escola = sigla_escola(df_ch.loc[:, ('Curso', 'Turma')],
                                     df_alunos.loc[:, ('Turma', 'Escola', 'Estabelecimento')])
        
    df_ch = trata_relatorio_ch(df_ch)

    print('Juntando dados...')

    df_joined = pd.merge(
        left=df_alunos, right=df_disciplinas, left_on=['Matrícula', 'Turma'], right_on=['CODIGO', 'TURMA_BASE']
    )

    # modificando o dataframe
    df_joined = df_joined[['Estabelecimento', 'Escola', 'Centro de Resultado', 'Curso', 'Série', 'Matrícula',
                           'Nome Completo', 'CPF', 'Data de Nascimento', 'Usuário Internet', 'E-mail',
                           'Telefone Celular', 'Situação Acadêmica', 'Tipo de Entrada', 'Tipo de Ingresso',
                           'Turma', 'Turno', 'Gênero',
                           # dados disciplina
                           'DT_CADASTRO_CONTRATO', 'DISCIPLINA', 'TURMA_DISCIPLINA', 'DIVISAO', 'DIVISAO2']]

    df_joined.rename(columns={
        'Série': 'Período Aluno',
        'Turma': 'Turma Aluno',
        'Centro de Resultado': 'CR Aluno',
        'Curso': 'Curso Aluno',
        'Usuário Internet': 'E-mail Institucional',
        'Disciplina': 'DISCIPLINA',
        'Turma Destino': 'TURMA_DISCIPLINA',
    }, inplace=True)

    print('Calculando...')

    df_joined.insert(18, 'Escola Disciplina', '', True)
    df_joined['Escola Disciplina'] = df_joined.apply(
        lambda row: encontra_escola(row['TURMA_DISCIPLINA'], dict_sigla_escola),
        axis=1)

    df_joined.insert(19, 'Curso_Disciplina', '', True)
    df_joined['Curso_Disciplina'] = df_joined.apply(
        lambda row: encontra_curso(row['TURMA_DISCIPLINA'], dict_sigla_curso),
        axis=1)

    df_joined.insert(20, 'Período_Disciplina', '', True)
    df_joined['Período_Disciplina'] = df_joined.apply(
        lambda row: encontra_periodo(row['TURMA_DISCIPLINA']),
        axis=1)

    df_joined.insert(21, 'CR_Disciplina', '', True)
    df_joined['CR_Disciplina'] = df_joined.apply(
        lambda row: encontra_cr(row['TURMA_DISCIPLINA'], dict_sigla_cr),
        axis=1)

    # Remove o início do nome do estabelecimento
    df_joined['Estabelecimento'] = df_joined['Estabelecimento'].str.replace(
        'Pontifícia Universidade Católica do Paraná - ', '')

    # Remove o início do nome da escola
    df_joined['Escola'] = df_joined['Escola'] \
        .str.replace('Escola de ', '') \
        .str.replace('Escola ', '')

    # Corrige 'Belas Artes' E 'Medicina e Ciências da Vida'
    for escola in df_joined.itertuples():
        if (df_joined['Escola'][escola.Index] == 'Comunicação e Artes'
                or df_joined['Escola'][escola.Index] == 'Arquitetura e Design'):
            df_joined['Escola'][escola.Index] = 'Belas Artes'
        elif (df_joined['Escola'][escola.Index] == 'Ciências da Vida'
              or df_joined['Escola'][escola.Index] == 'Medicina'):
            df_joined['Escola'][escola.Index] = 'Medicina e Ciências da Vida'
        else:
            pass

    # Altera a escola para o nome do campus fora de sede
    df_joined.loc[
        (df_joined['Estabelecimento'] == 'Londrina') |
        (df_joined['Estabelecimento'] == 'Maringá') |
        (df_joined['Estabelecimento'] == 'Toledo'),
        'Escola'] = df_joined['Estabelecimento']

    # No período do aluno deixar só os números
    df_joined['Período Aluno'] = df_joined['Período Aluno'] \
        .str.replace('º Periodo', '') \
        .str.replace('º Período', '')

    # Preenche a coluna Gênero com "Não informado" quando estiver vazia
    df_joined["Gênero"] = df_joined["Gênero"].fillna("Não informado")

    # Remove espaços antes e depois dos nomes
    df_joined['Nome Completo'] = df_joined['Nome Completo'].str.strip()

    # Insere validador para a inclusão da coluna de carga horária
    df_joined.insert(0, 'Validador', '', True)
    df_joined['Validador'] = df_joined.apply(lambda row: f"{str(row['CR_Disciplina']).strip()}    "
                                                         f"{str(row['TURMA_DISCIPLINA']).strip()}    "
                                                         f"{str(row['DISCIPLINA']).strip()}", axis=1)

    df_joined = pd.merge(left=df_joined, right=df_ch, left_on='Validador', right_on='Validador', how='left')
    del df_joined['Validador']

    # Remove linhas duplicadas
    df_joined = df_joined.drop_duplicates()
    df_joined = filtra_alunos(df_joined)

    print('Criando arquivos de saída...')

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(name, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    df_joined.to_excel(writer, sheet_name='Sheet1', index=False)

    print(f'Salvando arquivos em\n{name}')

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

    print('Geração de arquivos finalizada!')


if __name__ == '__main__':
    print('Selecione a Relação de Alunos/Pais Exportação')

    Tk().withdraw()
    relacao_alunos = askopenfilename(
        filetypes=[('Arquivo excel', '.xlsx')],
        title='Selecione a Relação de Alunos/Pais Exportação')
    print(f'    {relacao_alunos}')

    print('Selecione o relatório de Alunos Matriculados por Disciplina')

    relatorio_disciplinas = askopenfilename(
        filetypes=[('Arquivo excel', '.xlsx')],
        title='Selecione o relatório de Alunos Matriculados por Disciplina')
    print(f'    {relatorio_disciplinas}')

    print('Selecione o relatório de Professor - Carga Horária por Turma e Disciplina')

    relatorio_ch = askopenfilename(
        filetypes=[('Arquivo excel', '.xlsx')],
        title='Selecione o relatório de Professor - Carga Horária por Turma e Disciplina')
    print(f'    {relatorio_ch}')

    file_name = f'Base_ouro_completa_{dt.now().strftime("%Y%m%d_%Hh%M")}.xlsx'

    recebe_arquivos(relacao_alunos, relatorio_disciplinas, relatorio_ch, file_name)

# Identidade fica sempre no 1º período > Pode ser que mude ao longo dos semestres
