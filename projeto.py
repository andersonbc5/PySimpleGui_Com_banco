import PySimpleGUI as sg

import sqlite3 as conector

def conectar_banco(nome_banco):
    conexao = conector.connect(nome_banco)
    print('Conexão com o Banco aberta com sucesso.')
    return conexao
    
def criar_tabela(conexao):
    cursor = conexao.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS SUPLEMENTO (
                        LOTE CHAR(10),
                        PRODUTO TEXT,
                        FORNECEDOR TEXT
        )''')
        print('TABELA CRIADA COM SUCESSO')
        conexao.commit()
    except Exception as e:
        print(f'erro ao criar tabela{e}')
    finally:
        cursor.close()

def carregar_dados(nome_banco):
    conexao = conectar_banco(nome_banco)
    cursor = conexao.cursor()
    cursor.execute("SELECT LOTE, PRODUTO, FORNECEDOR FROM SUPLEMENTO")
    resultados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultados

dados = carregar_dados('banco_db.sqlite')
titulos = ['Lote', 'Produto', 'Fornecedor']

layout = [
    [sg.Text(titulos[0]), sg.Input(size=10, key=titulos[0])],
    [sg.Text(titulos[1]), sg.Input(size=10, key=titulos[1])],
    [sg.Text(titulos[2]), sg.Combo(['Fornecedor 1', 'Fornecedor 2', 'Fornecedor 3'], key=titulos[2])],
    [sg.Button('Adicionar'), sg.Button('Editar'),sg.Button('Salvar', disabled = True), sg.Button('Excluir'), sg.Exit('Sair')],
    [sg.Table(dados, titulos, key='tabela')]
]

# Criação e execução da janela
janela = sg.Window(
    'Sistema de gerencia de suplementos',
    layout
)

conexao = conectar_banco('banco_db.sqlite')
criar_tabela(conexao)
conexao.close()



while True:
    evento, valores = janela.read()
    
    if evento == 'Adicionar':
        dados.append([valores[titulos[0]], valores[titulos[1]], valores[titulos[2]]])
        janela['tabela'].update(values=dados)
        for i in range(3):
            janela[titulos[i]].update(value='')
        
        conexao = conectar_banco('banco_db.sqlite')
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO SUPLEMENTO (LOTE, PRODUTO, FORNECEDOR) VALUES (?, ?, ?)",
            (valores[titulos[0]], valores[titulos[1]], valores[titulos[2]])
        )
        conexao.commit()
        cursor.close()
        
    
    if evento == 'Editar':
        if valores['tabela'] == []:
            sg.popup('Nenhuma linha selecionada')
        else:
            editarLinha = valores['tabela'][0]
            sg.popup('Editar linha selecionada')
            for i in range(3):
                janela[titulos[i]].update(value=dados[editarLinha][i])
            janela['Salvar'].update(disabled=False)
    
    if evento == 'Salvar':
        # Corrija a atribuição da linha editada
        dados[editarLinha] = [valores[titulos[0]], valores[titulos[1]], valores[titulos[2]]]
        janela['tabela'].update(values=dados)  # <-- aqui estava 'valores=dados'
        for i in range(3):
            janela[titulos[i]].update(value='')
        janela['Salvar'].update(disabled=True)
        
        conexao = conectar_banco('banco_db.sqlite')
        cursor = conexao.cursor()
        # Corrija o comando SQL UPDATE
        cursor.execute(
            'UPDATE SUPLEMENTO SET PRODUTO = ?, FORNECEDOR = ?, LOTE = ? WHERE LOTE = ?',
            (valores[titulos[1]], valores[titulos[2]], valores[titulos[0]], dados[editarLinha][0])
        )
        conexao.commit()
        cursor.close()

    if evento == 'Excluir':
        if valores['tabela'] == []:
            sg.popup('Nenhuma linha selecionada')
        else:
            if sg.popup_ok_cancel('Essa operação não pode ser desfeita. Confirma?') == 'OK':
                conexao = conectar_banco('banco_db.sqlite')
                cursor = conexao.cursor()
                # Use o LOTE da linha selecionada para excluir corretamente
                lote_excluir = dados[valores['tabela'][0]][0]
                cursor.execute('DELETE FROM SUPLEMENTO WHERE LOTE = ?', (lote_excluir,))
                conexao.commit()
                cursor.close()
                
                del dados[valores['tabela'][0]]
                janela['tabela'].update(values=dados)  # <-- aqui também estava 'valores=dados'

    
    
    
    if evento == sg.WINDOW_CLOSED or evento == 'Sair':
        break

janela.close()

