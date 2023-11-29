"""
    Módulo dedicado a fazer a análise quanto ao recurso solar obtido
"""

import os
from math import ceil
import numpy as np
import pandas as pd
import json

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =========================== Configurações =================================
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Obtém o caminho absoluto para o diretório do script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Potência e preço por unidade dos painéis (kW e R$)
# Df = DataFrame
df = pd.read_csv(os.path.join(script_dir, '..', 'data', 'paineis.csv'))

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# ================== Variáveis Globais e Constantes =========================
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Lista que será preenchida posteriormente com o preço final para cada caso de painel usado
precos = []

# ============== Enums pra evitar numeros mágicos  =====================

POTENCIA, PRECO_UNITARIO = range(2)
DIAS_MES = 30
NUM_MESES_ANO = 12

# Criar matriz com a potência e preço por unidade de cada painel
PAINEIS_SOLARES = df[['potencia[kW]', 'preco']].to_numpy()

# Criar a array NOMES_PAINEIS com o nome dos paineis
NOMES_PAINEIS = df['nome'].to_list()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =============================== Funções ===================================
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def get_dados_consumo():
    """ Pega os dados obtidos de analise_consumo
        através de param.json

    Returns:
        float: retorna os valores calculados anteriormente
    """
    caminho_arquivo_json = os.path.join(script_dir, '..', 'config', 'param.json')
    with open(caminho_arquivo_json, 'r') as file:
        config = json.load(file)

    # Acessar os dados de consumo
    dados_consumo = config.get('Dados_Consumo_Bruto', {})

    media_mensal = dados_consumo.get('media_mensal')
    # Ajuste com o custo de disponibilidade
    nova_media_mensal = novos_dados(media_mensal, config)

    return nova_media_mensal


def novos_dados(media_m, config):
    """
        Valores deverão ser ajustados de acordo
        com o desconto do custo de disponibilidade
    
        Monofásico: o consumidor paga uma taxa mínima equivalente a 30 kWh;
        Bifásico: o custo de disponibilidade pago corresponde a 50 kWh;
        Trifásico: a taxa mínima é igual a 100 kWh.
    """

    # Qualquer erro de digitação na configuração resultará
    # em uma análise trifásica
    # Obter o valor de "padrao_alimentacao" do JSON
    padrao = config.get('padrao_alimentacao')

    if padrao.lower() == 'monofasico':
        tarifa = 30
    elif padrao.lower() == 'bifasico':
        tarifa = 50
    else:
        tarifa = 100        

    nova_media = media_m - tarifa
    novo_cdm = nova_media / DIAS_MES

    aprx_cdm = round(novo_cdm, 2)

    return aprx_cdm 

def calculo_potencia(media):
    """Cálculo da potência mínima do microgerador
    (ou do Inversor)

    Pm = E / (Td x Hsp)

        Pm(Wp): Potência de pico;
        E(kWh): Consumo médio diário (cdm);
        HSP:    Média de HSP anual;
        Td:     Taxa de desempenho (0.75)
    
    Args:
        media (float): média mensal obtida
        cdm (float): consumo diário médio obtido
    """

    taxa_desempenho = 0.75
    HSP = 4.88

    # media = novo consumo médio diário
    Pm = media / (taxa_desempenho * HSP)

    return Pm


def get_numero_de_paineis(Ps):
    """Cálculo do número de paneis necessários
       para atingir a demanda

    Args:
        Ps (__float__): Potência do sistema
    """

    # Número de painéis necessários por modelo
    numero_de_paineis_tipo1 = 0
    numero_de_paineis_tipo2 = 0
    numero_de_paineis_tipo3 = 0
    numero_de_paineis_tipo4 = 0

    # Cálculo iterando pela lista de painéis
    for indice_painel in range(len(PAINEIS_SOLARES)):
        if   indice_painel == 0:
            numero_de_paineis_tipo1 = Ps / PAINEIS_SOLARES[indice_painel][POTENCIA]
        elif indice_painel == 1:    
            numero_de_paineis_tipo2 = Ps / PAINEIS_SOLARES[indice_painel][POTENCIA]
        elif indice_painel == 2:    
            numero_de_paineis_tipo3 = Ps / PAINEIS_SOLARES[indice_painel][POTENCIA]
        elif indice_painel == 3:    
            numero_de_paineis_tipo4 = Ps / PAINEIS_SOLARES[indice_painel][POTENCIA]


    # Arredondando nº de painéis para cima
    numero_paineis_final_1 = ceil(numero_de_paineis_tipo1)
    numero_paineis_final_2 = ceil(numero_de_paineis_tipo2)
    numero_paineis_final_3 = ceil(numero_de_paineis_tipo3)
    numero_paineis_final_4 = ceil(numero_de_paineis_tipo4)

    return numero_paineis_final_1, numero_paineis_final_2, numero_paineis_final_3, numero_paineis_final_4


def decidir_painel(p1, p2, p3, p4):
    """Função para calcular o painel mais barato,
    consequentemente o que será usado

    Args:
        px (_int_): _quantidade para o tipo de painel_

    """
    preco_painel_1 = 0
    preco_painel_2 = 0
    preco_painel_3 = 0
    preco_painel_4 = 0

    # Multiplica o preço unitário x qntd de painéis para calcular
    # custo total para cada caso
    for indice_paniel in range(len(PAINEIS_SOLARES)):
        if   indice_paniel == 0:
            preco_painel_1 = p1 * PAINEIS_SOLARES[indice_paniel][PRECO_UNITARIO]
            precos.append(preco_painel_1)
        elif indice_paniel == 1:    
            preco_painel_2 = p2 * PAINEIS_SOLARES[indice_paniel][PRECO_UNITARIO]
            precos.append(preco_painel_2)
        elif indice_paniel == 2:    
            preco_painel_3 = p3 * PAINEIS_SOLARES[indice_paniel][PRECO_UNITARIO]
            precos.append(preco_painel_3)
        elif indice_paniel == 3:    
            preco_painel_4 = p4 * PAINEIS_SOLARES[indice_paniel][PRECO_UNITARIO]
            precos.append(preco_painel_4)

    # Seleciona o mais barato
    preco_selecionado = min(precos)
    painel_selecionado = precos.index(preco_selecionado)
    
    # Retorna o índice correspondente ao painel solar escolhido
    return painel_selecionado

def salvar_em_json(dados, caminho_arquivo):
    """ Salvando dados obtivos

    Args:
        dados (dictionary): dicionário contendo o conteúdo a ser salvo
        caminho_arquivo (None): caminho para o arquivo
    """
    # Leitura do arquivo JSON atual
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            conteudo_atual = json.load(arquivo)
    except FileNotFoundError:
        # Se o arquivo não existir, crie um dicionário vazio
        conteudo_atual = {}

    # Atualização do dicionário com os novos dados
    conteudo_atual.update(dados)

    # Escrita do dicionário atualizado de volta no arquivo JSON
    with open(caminho_arquivo, 'w') as arquivo:
        json.dump(conteudo_atual, arquivo, indent=2)


def main():
    media_mensal = get_dados_consumo()
    
    Potencia = calculo_potencia(media_mensal)

    qtd_painel1, qtd_painel2, qtd_painel3, qtd_painel4 = get_numero_de_paineis(Potencia)

    # Salvar em uma lista para facilitar visualização
    quantidade_paineis = np.array([qtd_painel1, qtd_painel2, qtd_painel3, qtd_painel4])

    painel_final = decidir_painel(qtd_painel1, qtd_painel2, qtd_painel3, qtd_painel4)

    potencia_final = quantidade_paineis[painel_final] * PAINEIS_SOLARES[painel_final, POTENCIA]

    # Dicionário para organizar os dados
    dados_solar = {
        "painel_selecionado": NOMES_PAINEIS[painel_final], 
        "qtd_paineis_necessarios": int(quantidade_paineis[painel_final]),
        "capacidade_total": round(potencia_final, 2),
        "preco_instalacao": precos[painel_final],
        "demanda": round(Potencia, 4)
    }

    caminho_arquivo_json = os.path.join(script_dir, '..', 'config', 'param.json')
    # Salvar os dados em um arquivo JSON
    salvar_em_json({"Dados_Solar": dados_solar}, caminho_arquivo_json)

    print(f'Painel Selecionado: {NOMES_PAINEIS[painel_final]}')
    print(f'Quantidade de painéis necessários: {quantidade_paineis[painel_final]}')
    print(f'Capacidade ao instalar: {potencia_final:.3f}kW')
    print(f'Preço final: R${precos[painel_final]}')

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# =========================== Início da Execução ============================
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


if __name__ == "__main__":
    main()    