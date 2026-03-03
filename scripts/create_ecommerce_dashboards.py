#!/usr/bin/env python3
"""
Script para criar dashboards de ecommerce no Metabase via API.
Banco de dados: Sample Database (ID: 1) - H2
"""

import requests
import json
import time

METABASE_URL = "https://analytics.arconde.cloud"
API_KEY = "mb_o8a+35jbsOddbO/l105odmnwGDh3b1KWyBomDTIc1IE="
DATABASE_ID = 1  # Sample Database (H2)

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# IDs das tabelas
TABLE_ORDERS = 2
TABLE_PEOPLE = 1
TABLE_PRODUCTS = 3
TABLE_REVIEWS = 4
TABLE_ACCOUNTS = 6
TABLE_INVOICES = 8
TABLE_FEEDBACK = 5
TABLE_ANALYTIC_EVENTS = 7

# IDs dos campos (ORDERS)
FIELD_ORDERS_ID = 9
FIELD_ORDERS_USER_ID = 11
FIELD_ORDERS_PRODUCT_ID = 14
FIELD_ORDERS_SUBTOTAL = 10
FIELD_ORDERS_TAX = 6
FIELD_ORDERS_TOTAL = 5
FIELD_ORDERS_DISCOUNT = 3
FIELD_ORDERS_CREATED_AT = 13
FIELD_ORDERS_QUANTITY = 2

# IDs dos campos (PEOPLE)
FIELD_PEOPLE_ID = 4
FIELD_PEOPLE_STATE = 1
FIELD_PEOPLE_SOURCE = 30
FIELD_PEOPLE_BIRTH_DATE = 12
FIELD_PEOPLE_CREATED_AT = 50
FIELD_PEOPLE_CITY = 53
FIELD_PEOPLE_LATITUDE = 52
FIELD_PEOPLE_LONGITUDE = 58

# IDs dos campos (PRODUCTS)
FIELD_PRODUCTS_ID = 8
FIELD_PRODUCTS_TITLE = 17
FIELD_PRODUCTS_CATEGORY = 18
FIELD_PRODUCTS_VENDOR = 34
FIELD_PRODUCTS_PRICE = 44
FIELD_PRODUCTS_RATING = 16
FIELD_PRODUCTS_CREATED_AT = 63

# IDs dos campos (REVIEWS)
FIELD_REVIEWS_ID = 59
FIELD_REVIEWS_PRODUCT_ID = 65
FIELD_REVIEWS_RATING = 19
FIELD_REVIEWS_CREATED_AT = 55


def create_card(name, query, visualization_type, description=""):
    """Cria um card (questão) no Metabase."""
    payload = {
        "name": name,
        "description": description,
        "display": visualization_type,
        "dataset_query": {
            "type": "native",
            "native": {
                "query": query,
                "template-tags": {}
            },
            "database": DATABASE_ID
        },
        "visualization_settings": {}
    }
    
    response = requests.post(
        f"{METABASE_URL}/api/card",
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code in [200, 201]:
        card = response.json()
        print(f"  ✓ Card criado: {name} (ID: {card['id']})")
        return card['id']
    else:
        print(f"  ✗ Erro ao criar card '{name}': {response.status_code} - {response.text[:200]}")
        return None


def create_card_with_settings(name, query, visualization_type, viz_settings, description=""):
    """Cria um card com configurações de visualização personalizadas."""
    payload = {
        "name": name,
        "description": description,
        "display": visualization_type,
        "dataset_query": {
            "type": "native",
            "native": {
                "query": query,
                "template-tags": {}
            },
            "database": DATABASE_ID
        },
        "visualization_settings": viz_settings
    }
    
    response = requests.post(
        f"{METABASE_URL}/api/card",
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code in [200, 201]:
        card = response.json()
        print(f"  ✓ Card criado: {name} (ID: {card['id']})")
        return card['id']
    else:
        print(f"  ✗ Erro ao criar card '{name}': {response.status_code} - {response.text[:200]}")
        return None


def create_dashboard(name, description=""):
    """Cria um dashboard no Metabase."""
    payload = {
        "name": name,
        "description": description
    }
    
    response = requests.post(
        f"{METABASE_URL}/api/dashboard",
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code in [200, 201]:
        dashboard = response.json()
        print(f"✓ Dashboard criado: {name} (ID: {dashboard['id']})")
        return dashboard['id']
    else:
        print(f"✗ Erro ao criar dashboard '{name}': {response.status_code} - {response.text[:200]}")
        return None


def add_card_to_dashboard(dashboard_id, card_id, row, col, size_x=6, size_y=4):
    """Adiciona um card a um dashboard."""
    payload = {
        "cardId": card_id,
        "row": row,
        "col": col,
        "size_x": size_x,
        "size_y": size_y
    }
    
    response = requests.post(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}/cards",
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code in [200, 201]:
        print(f"  ✓ Card {card_id} adicionado ao dashboard {dashboard_id} (pos: {row},{col})")
        return True
    else:
        print(f"  ✗ Erro ao adicionar card {card_id}: {response.status_code} - {response.text[:200]}")
        return False


def add_text_card_to_dashboard(dashboard_id, text, row, col, size_x=24, size_y=2):
    """Adiciona um card de texto/heading a um dashboard."""
    payload = {
        "cardId": None,
        "row": row,
        "col": col,
        "size_x": size_x,
        "size_y": size_y,
        "visualization_settings": {
            "virtual_card": {
                "name": None,
                "display": "text",
                "visualization_settings": {},
                "dataset_query": {},
                "archived": False
            },
            "text": text,
            "click_behavior": {}
        }
    }
    
    response = requests.post(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}/cards",
        headers=HEADERS,
        json=payload
    )
    
    if response.status_code in [200, 201]:
        print(f"  ✓ Card de texto adicionado ao dashboard {dashboard_id}")
        return True
    else:
        print(f"  ✗ Erro ao adicionar texto: {response.status_code} - {response.text[:200]}")
        return False


# ============================================================
# DASHBOARD 1: VISÃO GERAL DE VENDAS (KPIs Executivos)
# ============================================================

def create_dashboard_vendas():
    print("\n" + "="*60)
    print("CRIANDO: Visão Geral de Vendas")
    print("="*60)
    
    dashboard_id = create_dashboard(
        "Visão Geral de Vendas",
        "KPIs executivos de vendas: receita total, pedidos, ticket médio e crescimento"
    )
    if not dashboard_id:
        return None
    
    cards = {}
    
    # KPI: Receita Total
    cards['receita_total'] = create_card(
        "Receita Total",
        "SELECT SUM(TOTAL) AS \"Receita Total\" FROM ORDERS",
        "scalar",
        "Soma de todos os valores de pedidos"
    )
    
    # KPI: Total de Pedidos
    cards['total_pedidos'] = create_card(
        "Total de Pedidos",
        "SELECT COUNT(*) AS \"Total de Pedidos\" FROM ORDERS",
        "scalar",
        "Número total de pedidos realizados"
    )
    
    # KPI: Ticket Médio
    cards['ticket_medio'] = create_card(
        "Ticket Médio",
        "SELECT ROUND(AVG(TOTAL), 2) AS \"Ticket Médio\" FROM ORDERS",
        "scalar",
        "Valor médio por pedido"
    )
    
    # KPI: Total de Clientes
    cards['total_clientes'] = create_card(
        "Total de Clientes",
        "SELECT COUNT(DISTINCT USER_ID) AS \"Clientes Ativos\" FROM ORDERS",
        "scalar",
        "Número de clientes únicos que realizaram pedidos"
    )
    
    # Receita por Mês (linha do tempo)
    cards['receita_mes'] = create_card_with_settings(
        "Receita Mensal",
        """SELECT 
    FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
    SUM(TOTAL) AS "Receita"
FROM ORDERS
GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
ORDER BY "Mês" """,
        "line",
        {
            "graph.x_axis.title_text": "Mês",
            "graph.y_axis.title_text": "Receita (R$)",
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Receita"]
        },
        "Evolução da receita ao longo dos meses"
    )
    
    # Pedidos por Mês
    cards['pedidos_mes'] = create_card_with_settings(
        "Pedidos por Mês",
        """SELECT 
    FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
    COUNT(*) AS "Pedidos"
FROM ORDERS
GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
ORDER BY "Mês" """,
        "bar",
        {
            "graph.x_axis.title_text": "Mês",
            "graph.y_axis.title_text": "Quantidade de Pedidos",
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Pedidos"]
        },
        "Quantidade de pedidos por mês"
    )
    
    # Receita por Canal de Aquisição
    cards['receita_canal'] = create_card_with_settings(
        "Receita por Canal de Aquisição",
        """SELECT 
    P.SOURCE AS "Canal",
    SUM(O.TOTAL) AS "Receita",
    COUNT(O.ID) AS "Pedidos"
FROM ORDERS O
JOIN PEOPLE P ON O.USER_ID = P.ID
GROUP BY P.SOURCE
ORDER BY "Receita" DESC""",
        "bar",
        {
            "graph.x_axis.title_text": "Canal",
            "graph.y_axis.title_text": "Receita (R$)",
            "graph.dimensions": ["Canal"],
            "graph.metrics": ["Receita"]
        },
        "Receita total por canal de aquisição de clientes"
    )
    
    # Receita por Estado (Top 10)
    cards['receita_estado'] = create_card_with_settings(
        "Top 10 Estados por Receita",
        """SELECT 
    P.STATE AS "Estado",
    SUM(O.TOTAL) AS "Receita",
    COUNT(O.ID) AS "Pedidos"
FROM ORDERS O
JOIN PEOPLE P ON O.USER_ID = P.ID
GROUP BY P.STATE
ORDER BY "Receita" DESC
LIMIT 10""",
        "row",
        {
            "graph.x_axis.title_text": "Receita (R$)",
            "graph.y_axis.title_text": "Estado",
            "graph.dimensions": ["Estado"],
            "graph.metrics": ["Receita"]
        },
        "Top 10 estados com maior receita"
    )
    
    # Desconto Total Concedido
    cards['desconto_total'] = create_card(
        "Desconto Total Concedido",
        "SELECT ROUND(SUM(DISCOUNT), 2) AS \"Desconto Total\" FROM ORDERS WHERE DISCOUNT > 0",
        "scalar",
        "Soma de todos os descontos aplicados"
    )
    
    # Receita vs Desconto por Mês
    cards['receita_vs_desconto'] = create_card_with_settings(
        "Receita vs Desconto por Mês",
        """SELECT 
    FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
    SUM(TOTAL) AS "Receita",
    SUM(DISCOUNT) AS "Desconto"
FROM ORDERS
GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
ORDER BY "Mês" """,
        "combo",
        {
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Receita", "Desconto"]
        },
        "Comparativo entre receita e descontos por mês"
    )
    
    # Distribuição de Pedidos por Faixa de Valor
    cards['faixa_valor'] = create_card_with_settings(
        "Distribuição por Faixa de Valor",
        """SELECT 
    CASE 
        WHEN TOTAL < 20 THEN 'Até R$20'
        WHEN TOTAL < 50 THEN 'R$20 - R$50'
        WHEN TOTAL < 100 THEN 'R$50 - R$100'
        WHEN TOTAL < 200 THEN 'R$100 - R$200'
        ELSE 'Acima de R$200'
    END AS "Faixa de Valor",
    COUNT(*) AS "Pedidos"
FROM ORDERS
GROUP BY 
    CASE 
        WHEN TOTAL < 20 THEN 'Até R$20'
        WHEN TOTAL < 50 THEN 'R$20 - R$50'
        WHEN TOTAL < 100 THEN 'R$50 - R$100'
        WHEN TOTAL < 200 THEN 'R$100 - R$200'
        ELSE 'Acima de R$200'
    END
ORDER BY MIN(TOTAL)""",
        "pie",
        {
            "graph.dimensions": ["Faixa de Valor"],
            "graph.metrics": ["Pedidos"]
        },
        "Distribuição de pedidos por faixa de valor"
    )
    
    # Adicionar cards ao dashboard
    print("\nAdicionando cards ao dashboard...")
    
    # Linha 1: KPIs (4 cards de 6x3)
    if cards.get('receita_total'):
        add_card_to_dashboard(dashboard_id, cards['receita_total'], 0, 0, 6, 3)
    if cards.get('total_pedidos'):
        add_card_to_dashboard(dashboard_id, cards['total_pedidos'], 0, 6, 6, 3)
    if cards.get('ticket_medio'):
        add_card_to_dashboard(dashboard_id, cards['ticket_medio'], 0, 12, 6, 3)
    if cards.get('total_clientes'):
        add_card_to_dashboard(dashboard_id, cards['total_clientes'], 0, 18, 6, 3)
    
    # Linha 2: Receita Mensal (linha) + Pedidos por Mês (barra)
    if cards.get('receita_mes'):
        add_card_to_dashboard(dashboard_id, cards['receita_mes'], 3, 0, 12, 5)
    if cards.get('pedidos_mes'):
        add_card_to_dashboard(dashboard_id, cards['pedidos_mes'], 3, 12, 12, 5)
    
    # Linha 3: Receita por Canal + Top 10 Estados
    if cards.get('receita_canal'):
        add_card_to_dashboard(dashboard_id, cards['receita_canal'], 8, 0, 12, 5)
    if cards.get('receita_estado'):
        add_card_to_dashboard(dashboard_id, cards['receita_estado'], 8, 12, 12, 5)
    
    # Linha 4: Receita vs Desconto + Faixa de Valor + Desconto Total
    if cards.get('receita_vs_desconto'):
        add_card_to_dashboard(dashboard_id, cards['receita_vs_desconto'], 13, 0, 12, 5)
    if cards.get('faixa_valor'):
        add_card_to_dashboard(dashboard_id, cards['faixa_valor'], 13, 12, 6, 5)
    if cards.get('desconto_total'):
        add_card_to_dashboard(dashboard_id, cards['desconto_total'], 13, 18, 6, 5)
    
    return dashboard_id


# ============================================================
# DASHBOARD 2: ANÁLISE DE PRODUTOS
# ============================================================

def create_dashboard_produtos():
    print("\n" + "="*60)
    print("CRIANDO: Análise de Produtos")
    print("="*60)
    
    dashboard_id = create_dashboard(
        "Análise de Produtos",
        "Performance de produtos: vendas por categoria, produtos mais vendidos, avaliações e preços"
    )
    if not dashboard_id:
        return None
    
    cards = {}
    
    # KPI: Total de Produtos
    cards['total_produtos'] = create_card(
        "Total de Produtos no Catálogo",
        "SELECT COUNT(*) AS \"Total de Produtos\" FROM PRODUCTS",
        "scalar"
    )
    
    # KPI: Categorias
    cards['total_categorias'] = create_card(
        "Categorias de Produtos",
        "SELECT COUNT(DISTINCT CATEGORY) AS \"Categorias\" FROM PRODUCTS",
        "scalar"
    )
    
    # KPI: Avaliação Média
    cards['avaliacao_media'] = create_card(
        "Avaliação Média dos Produtos",
        "SELECT ROUND(AVG(RATING), 2) AS \"Avaliação Média\" FROM PRODUCTS",
        "scalar"
    )
    
    # KPI: Preço Médio
    cards['preco_medio'] = create_card(
        "Preço Médio dos Produtos",
        "SELECT ROUND(AVG(PRICE), 2) AS \"Preço Médio\" FROM PRODUCTS",
        "scalar"
    )
    
    # Receita por Categoria
    cards['receita_categoria'] = create_card_with_settings(
        "Receita por Categoria de Produto",
        """SELECT 
    P.CATEGORY AS "Categoria",
    SUM(O.TOTAL) AS "Receita",
    COUNT(O.ID) AS "Pedidos",
    ROUND(AVG(O.TOTAL), 2) AS "Ticket Médio"
FROM ORDERS O
JOIN PRODUCTS P ON O.PRODUCT_ID = P.ID
GROUP BY P.CATEGORY
ORDER BY "Receita" DESC""",
        "bar",
        {
            "graph.dimensions": ["Categoria"],
            "graph.metrics": ["Receita"]
        },
        "Receita total por categoria de produto"
    )
    
    # Participação de Vendas por Categoria (pizza)
    cards['participacao_categoria'] = create_card_with_settings(
        "Participação de Vendas por Categoria",
        """SELECT 
    P.CATEGORY AS "Categoria",
    COUNT(O.ID) AS "Pedidos"
FROM ORDERS O
JOIN PRODUCTS P ON O.PRODUCT_ID = P.ID
GROUP BY P.CATEGORY
ORDER BY "Pedidos" DESC""",
        "pie",
        {
            "graph.dimensions": ["Categoria"],
            "graph.metrics": ["Pedidos"]
        },
        "Participação percentual de cada categoria no total de pedidos"
    )
    
    # Top 10 Produtos Mais Vendidos
    cards['top_produtos'] = create_card_with_settings(
        "Top 10 Produtos Mais Vendidos",
        """SELECT 
    P.TITLE AS "Produto",
    P.CATEGORY AS "Categoria",
    COUNT(O.ID) AS "Pedidos",
    SUM(O.TOTAL) AS "Receita Total"
FROM ORDERS O
JOIN PRODUCTS P ON O.PRODUCT_ID = P.ID
GROUP BY P.ID, P.TITLE, P.CATEGORY
ORDER BY "Pedidos" DESC
LIMIT 10""",
        "row",
        {
            "graph.dimensions": ["Produto"],
            "graph.metrics": ["Pedidos"]
        },
        "Os 10 produtos com maior número de pedidos"
    )
    
    # Avaliação Média por Categoria
    cards['avaliacao_categoria'] = create_card_with_settings(
        "Avaliação Média por Categoria",
        """SELECT 
    P.CATEGORY AS "Categoria",
    ROUND(AVG(R.RATING), 2) AS "Avaliação Média",
    COUNT(R.ID) AS "Total de Avaliações"
FROM PRODUCTS P
LEFT JOIN REVIEWS R ON P.ID = R.PRODUCT_ID
GROUP BY P.CATEGORY
ORDER BY "Avaliação Média" DESC""",
        "bar",
        {
            "graph.dimensions": ["Categoria"],
            "graph.metrics": ["Avaliação Média"]
        },
        "Avaliação média dos produtos por categoria"
    )
    
    # Distribuição de Preços por Categoria
    cards['preco_categoria'] = create_card_with_settings(
        "Preço Médio por Categoria",
        """SELECT 
    CATEGORY AS "Categoria",
    ROUND(MIN(PRICE), 2) AS "Preço Mínimo",
    ROUND(AVG(PRICE), 2) AS "Preço Médio",
    ROUND(MAX(PRICE), 2) AS "Preço Máximo"
FROM PRODUCTS
GROUP BY CATEGORY
ORDER BY "Preço Médio" DESC""",
        "bar",
        {
            "graph.dimensions": ["Categoria"],
            "graph.metrics": ["Preço Médio"]
        },
        "Faixa de preços por categoria de produto"
    )
    
    # Produtos com Melhor Avaliação
    cards['melhores_avaliados'] = create_card_with_settings(
        "Produtos Melhor Avaliados",
        """SELECT 
    P.TITLE AS "Produto",
    P.CATEGORY AS "Categoria",
    P.PRICE AS "Preço",
    P.RATING AS "Avaliação",
    COUNT(R.ID) AS "Qtd Avaliações"
FROM PRODUCTS P
LEFT JOIN REVIEWS R ON P.ID = R.PRODUCT_ID
GROUP BY P.ID, P.TITLE, P.CATEGORY, P.PRICE, P.RATING
HAVING COUNT(R.ID) >= 3
ORDER BY P.RATING DESC, "Qtd Avaliações" DESC
LIMIT 10""",
        "table",
        {},
        "Produtos com as melhores avaliações (mínimo 3 avaliações)"
    )
    
    # Vendas por Fornecedor
    cards['vendas_fornecedor'] = create_card_with_settings(
        "Receita por Fornecedor (Top 10)",
        """SELECT 
    P.VENDOR AS "Fornecedor",
    SUM(O.TOTAL) AS "Receita",
    COUNT(O.ID) AS "Pedidos"
FROM ORDERS O
JOIN PRODUCTS P ON O.PRODUCT_ID = P.ID
GROUP BY P.VENDOR
ORDER BY "Receita" DESC
LIMIT 10""",
        "row",
        {
            "graph.dimensions": ["Fornecedor"],
            "graph.metrics": ["Receita"]
        },
        "Top 10 fornecedores por receita gerada"
    )
    
    # Adicionar cards ao dashboard
    print("\nAdicionando cards ao dashboard...")
    
    # Linha 1: KPIs
    if cards.get('total_produtos'):
        add_card_to_dashboard(dashboard_id, cards['total_produtos'], 0, 0, 6, 3)
    if cards.get('total_categorias'):
        add_card_to_dashboard(dashboard_id, cards['total_categorias'], 0, 6, 6, 3)
    if cards.get('avaliacao_media'):
        add_card_to_dashboard(dashboard_id, cards['avaliacao_media'], 0, 12, 6, 3)
    if cards.get('preco_medio'):
        add_card_to_dashboard(dashboard_id, cards['preco_medio'], 0, 18, 6, 3)
    
    # Linha 2: Receita por Categoria + Participação
    if cards.get('receita_categoria'):
        add_card_to_dashboard(dashboard_id, cards['receita_categoria'], 3, 0, 14, 5)
    if cards.get('participacao_categoria'):
        add_card_to_dashboard(dashboard_id, cards['participacao_categoria'], 3, 14, 10, 5)
    
    # Linha 3: Top Produtos + Avaliação por Categoria
    if cards.get('top_produtos'):
        add_card_to_dashboard(dashboard_id, cards['top_produtos'], 8, 0, 12, 6)
    if cards.get('avaliacao_categoria'):
        add_card_to_dashboard(dashboard_id, cards['avaliacao_categoria'], 8, 12, 12, 6)
    
    # Linha 4: Preço por Categoria + Vendas por Fornecedor
    if cards.get('preco_categoria'):
        add_card_to_dashboard(dashboard_id, cards['preco_categoria'], 14, 0, 12, 5)
    if cards.get('vendas_fornecedor'):
        add_card_to_dashboard(dashboard_id, cards['vendas_fornecedor'], 14, 12, 12, 5)
    
    # Linha 5: Melhores Avaliados
    if cards.get('melhores_avaliados'):
        add_card_to_dashboard(dashboard_id, cards['melhores_avaliados'], 19, 0, 24, 5)
    
    return dashboard_id


# ============================================================
# DASHBOARD 3: ANÁLISE DE CLIENTES
# ============================================================

def create_dashboard_clientes():
    print("\n" + "="*60)
    print("CRIANDO: Análise de Clientes")
    print("="*60)
    
    dashboard_id = create_dashboard(
        "Análise de Clientes",
        "Comportamento e perfil dos clientes: aquisição, retenção, segmentação e LTV"
    )
    if not dashboard_id:
        return None
    
    cards = {}
    
    # KPI: Total de Clientes
    cards['total_clientes'] = create_card(
        "Total de Clientes Cadastrados",
        "SELECT COUNT(*) AS \"Total de Clientes\" FROM PEOPLE",
        "scalar"
    )
    
    # KPI: Clientes com Pedidos
    cards['clientes_ativos'] = create_card(
        "Clientes com Pedidos",
        "SELECT COUNT(DISTINCT USER_ID) AS \"Clientes com Pedidos\" FROM ORDERS",
        "scalar"
    )
    
    # KPI: Pedidos por Cliente (média)
    cards['pedidos_por_cliente'] = create_card(
        "Média de Pedidos por Cliente",
        """SELECT ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT USER_ID), 2) AS "Pedidos por Cliente"
FROM ORDERS""",
        "scalar"
    )
    
    # KPI: Receita por Cliente (LTV médio)
    cards['ltv_medio'] = create_card(
        "LTV Médio por Cliente",
        """SELECT ROUND(SUM(TOTAL) / COUNT(DISTINCT USER_ID), 2) AS "LTV Médio"
FROM ORDERS""",
        "scalar"
    )
    
    # Novos Clientes por Mês
    cards['novos_clientes_mes'] = create_card_with_settings(
        "Novos Clientes por Mês",
        """SELECT 
    FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
    COUNT(*) AS "Novos Clientes"
FROM PEOPLE
GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
ORDER BY "Mês" """,
        "area",
        {
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Novos Clientes"]
        },
        "Crescimento da base de clientes ao longo do tempo"
    )
    
    # Clientes por Canal de Aquisição
    cards['clientes_canal'] = create_card_with_settings(
        "Clientes por Canal de Aquisição",
        """SELECT 
    SOURCE AS "Canal",
    COUNT(*) AS "Clientes",
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS "Percentual"
FROM PEOPLE
GROUP BY SOURCE
ORDER BY "Clientes" DESC""",
        "pie",
        {
            "graph.dimensions": ["Canal"],
            "graph.metrics": ["Clientes"]
        },
        "Distribuição de clientes por canal de aquisição"
    )
    
    # Clientes por Estado (Top 10)
    cards['clientes_estado'] = create_card_with_settings(
        "Top 10 Estados por Número de Clientes",
        """SELECT 
    STATE AS "Estado",
    COUNT(*) AS "Clientes"
FROM PEOPLE
GROUP BY STATE
ORDER BY "Clientes" DESC
LIMIT 10""",
        "row",
        {
            "graph.dimensions": ["Estado"],
            "graph.metrics": ["Clientes"]
        },
        "Estados com maior concentração de clientes"
    )
    
    # Segmentação por Frequência de Compra
    cards['segmentacao_frequencia'] = create_card_with_settings(
        "Segmentação por Frequência de Compra",
        """SELECT 
    CASE 
        WHEN pedidos = 1 THEN '1 pedido (One-time)'
        WHEN pedidos = 2 THEN '2 pedidos'
        WHEN pedidos BETWEEN 3 AND 5 THEN '3-5 pedidos'
        WHEN pedidos BETWEEN 6 AND 10 THEN '6-10 pedidos'
        ELSE 'Mais de 10 pedidos (VIP)'
    END AS "Segmento",
    COUNT(*) AS "Clientes"
FROM (
    SELECT USER_ID, COUNT(*) AS pedidos
    FROM ORDERS
    GROUP BY USER_ID
) t
GROUP BY 
    CASE 
        WHEN pedidos = 1 THEN '1 pedido (One-time)'
        WHEN pedidos = 2 THEN '2 pedidos'
        WHEN pedidos BETWEEN 3 AND 5 THEN '3-5 pedidos'
        WHEN pedidos BETWEEN 6 AND 10 THEN '6-10 pedidos'
        ELSE 'Mais de 10 pedidos (VIP)'
    END
ORDER BY MIN(pedidos)""",
        "pie",
        {
            "graph.dimensions": ["Segmento"],
            "graph.metrics": ["Clientes"]
        },
        "Segmentação de clientes por frequência de compra"
    )
    
    # Top Clientes por Receita
    cards['top_clientes'] = create_card_with_settings(
        "Top 10 Clientes por Receita",
        """SELECT 
    P.NAME AS "Cliente",
    P.EMAIL AS "Email",
    P.STATE AS "Estado",
    COUNT(O.ID) AS "Pedidos",
    ROUND(SUM(O.TOTAL), 2) AS "Receita Total"
FROM ORDERS O
JOIN PEOPLE P ON O.USER_ID = P.ID
GROUP BY P.ID, P.NAME, P.EMAIL, P.STATE
ORDER BY "Receita Total" DESC
LIMIT 10""",
        "table",
        {},
        "Os 10 clientes que mais geraram receita"
    )
    
    # Receita por Faixa Etária
    cards['receita_idade'] = create_card_with_settings(
        "Receita por Faixa Etária",
        """SELECT 
    CASE 
        WHEN DATEDIFF('year', P.BIRTH_DATE, NOW()) < 25 THEN 'Até 24 anos'
        WHEN DATEDIFF('year', P.BIRTH_DATE, NOW()) BETWEEN 25 AND 34 THEN '25-34 anos'
        WHEN DATEDIFF('year', P.BIRTH_DATE, NOW()) BETWEEN 35 AND 44 THEN '35-44 anos'
        WHEN DATEDIFF('year', P.BIRTH_DATE, NOW()) BETWEEN 45 AND 54 THEN '45-54 anos'
        ELSE '55+ anos'
    END AS "Faixa Etária",
    COUNT(O.ID) AS "Pedidos",
    ROUND(SUM(O.TOTAL), 2) AS "Receita"
FROM ORDERS O
JOIN PEOPLE P ON O.USER_ID = P.ID
GROUP BY 
    CASE 
        WHEN DATEDIFF('year', P.BIRTH_DATE, NOW()) < 25 THEN 'Até 24 anos'
        WHEN DATEDIFF('year', P.BIRTH_DATE, NOW()) BETWEEN 25 AND 34 THEN '25-34 anos'
        WHEN DATEDIFF('year', P.BIRTH_DATE, NOW()) BETWEEN 35 AND 44 THEN '35-44 anos'
        WHEN DATEDIFF('year', P.BIRTH_DATE, NOW()) BETWEEN 45 AND 54 THEN '45-54 anos'
        ELSE '55+ anos'
    END
ORDER BY MIN(DATEDIFF('year', P.BIRTH_DATE, NOW()))""",
        "bar",
        {
            "graph.dimensions": ["Faixa Etária"],
            "graph.metrics": ["Receita"]
        },
        "Receita e pedidos por faixa etária dos clientes"
    )
    
    # Adicionar cards ao dashboard
    print("\nAdicionando cards ao dashboard...")
    
    # Linha 1: KPIs
    if cards.get('total_clientes'):
        add_card_to_dashboard(dashboard_id, cards['total_clientes'], 0, 0, 6, 3)
    if cards.get('clientes_ativos'):
        add_card_to_dashboard(dashboard_id, cards['clientes_ativos'], 0, 6, 6, 3)
    if cards.get('pedidos_por_cliente'):
        add_card_to_dashboard(dashboard_id, cards['pedidos_por_cliente'], 0, 12, 6, 3)
    if cards.get('ltv_medio'):
        add_card_to_dashboard(dashboard_id, cards['ltv_medio'], 0, 18, 6, 3)
    
    # Linha 2: Novos Clientes por Mês (área) + Canal de Aquisição (pizza)
    if cards.get('novos_clientes_mes'):
        add_card_to_dashboard(dashboard_id, cards['novos_clientes_mes'], 3, 0, 14, 5)
    if cards.get('clientes_canal'):
        add_card_to_dashboard(dashboard_id, cards['clientes_canal'], 3, 14, 10, 5)
    
    # Linha 3: Top Estados + Segmentação por Frequência
    if cards.get('clientes_estado'):
        add_card_to_dashboard(dashboard_id, cards['clientes_estado'], 8, 0, 12, 5)
    if cards.get('segmentacao_frequencia'):
        add_card_to_dashboard(dashboard_id, cards['segmentacao_frequencia'], 8, 12, 12, 5)
    
    # Linha 4: Receita por Faixa Etária
    if cards.get('receita_idade'):
        add_card_to_dashboard(dashboard_id, cards['receita_idade'], 13, 0, 24, 5)
    
    # Linha 5: Top Clientes
    if cards.get('top_clientes'):
        add_card_to_dashboard(dashboard_id, cards['top_clientes'], 18, 0, 24, 5)
    
    return dashboard_id


# ============================================================
# DASHBOARD 4: FUNIL DE CONVERSÃO E COMPORTAMENTO
# ============================================================

def create_dashboard_conversao():
    print("\n" + "="*60)
    print("CRIANDO: Funil de Conversão e Comportamento")
    print("="*60)
    
    dashboard_id = create_dashboard(
        "Funil de Conversão e Comportamento",
        "Análise do funil de compras, eventos analíticos e comportamento dos usuários"
    )
    if not dashboard_id:
        return None
    
    cards = {}
    
    # KPI: Total de Eventos
    cards['total_eventos'] = create_card(
        "Total de Eventos Registrados",
        "SELECT COUNT(*) AS \"Total de Eventos\" FROM ANALYTIC_EVENTS",
        "scalar"
    )
    
    # KPI: Usuários com Eventos
    cards['usuarios_eventos'] = create_card(
        "Usuários com Eventos",
        "SELECT COUNT(DISTINCT ACCOUNT_ID) AS \"Usuários Ativos\" FROM ANALYTIC_EVENTS",
        "scalar"
    )
    
    # KPI: Tipos de Eventos
    cards['tipos_eventos'] = create_card(
        "Tipos de Eventos",
        "SELECT COUNT(DISTINCT EVENT) AS \"Tipos de Eventos\" FROM ANALYTIC_EVENTS",
        "scalar"
    )
    
    # Eventos por Tipo
    cards['eventos_tipo'] = create_card_with_settings(
        "Eventos por Tipo",
        """SELECT 
    EVENT AS "Evento",
    COUNT(*) AS "Ocorrências"
FROM ANALYTIC_EVENTS
GROUP BY EVENT
ORDER BY "Ocorrências" DESC""",
        "bar",
        {
            "graph.dimensions": ["Evento"],
            "graph.metrics": ["Ocorrências"]
        },
        "Frequência de cada tipo de evento analítico"
    )
    
    # Eventos por Mês
    cards['eventos_mes'] = create_card_with_settings(
        "Eventos por Mês",
        """SELECT 
    FORMATDATETIME(TIMESTAMP, 'yyyy-MM') AS "Mês",
    COUNT(*) AS "Eventos"
FROM ANALYTIC_EVENTS
GROUP BY FORMATDATETIME(TIMESTAMP, 'yyyy-MM')
ORDER BY "Mês" """,
        "line",
        {
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Eventos"]
        },
        "Volume de eventos ao longo do tempo"
    )
    
    # Páginas Mais Visitadas
    cards['paginas_visitadas'] = create_card_with_settings(
        "Páginas Mais Visitadas",
        """SELECT 
    PAGE_URL AS "Página",
    COUNT(*) AS "Visitas"
FROM ANALYTIC_EVENTS
WHERE PAGE_URL IS NOT NULL AND PAGE_URL != ''
GROUP BY PAGE_URL
ORDER BY "Visitas" DESC
LIMIT 10""",
        "row",
        {
            "graph.dimensions": ["Página"],
            "graph.metrics": ["Visitas"]
        },
        "Top 10 páginas mais visitadas"
    )
    
    # Satisfação dos Clientes (Feedback)
    cards['satisfacao_geral'] = create_card(
        "Satisfação Geral dos Clientes",
        "SELECT ROUND(AVG(RATING), 2) AS \"Satisfação Média\" FROM FEEDBACK",
        "scalar"
    )
    
    # Distribuição de Ratings
    cards['distribuicao_ratings'] = create_card_with_settings(
        "Distribuição de Avaliações",
        """SELECT 
    RATING AS "Nota",
    RATING_MAPPED AS "Classificação",
    COUNT(*) AS "Respostas"
FROM FEEDBACK
GROUP BY RATING, RATING_MAPPED
ORDER BY RATING DESC""",
        "bar",
        {
            "graph.dimensions": ["Classificação"],
            "graph.metrics": ["Respostas"]
        },
        "Distribuição das notas de satisfação dos clientes"
    )
    
    # Satisfação por Mês
    cards['satisfacao_mes'] = create_card_with_settings(
        "Satisfação Média por Mês",
        """SELECT 
    FORMATDATETIME(DATE_RECEIVED, 'yyyy-MM') AS "Mês",
    ROUND(AVG(RATING), 2) AS "Satisfação Média"
FROM FEEDBACK
GROUP BY FORMATDATETIME(DATE_RECEIVED, 'yyyy-MM')
ORDER BY "Mês" """,
        "line",
        {
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Satisfação Média"]
        },
        "Evolução da satisfação dos clientes ao longo do tempo"
    )
    
    # Adicionar cards ao dashboard
    print("\nAdicionando cards ao dashboard...")
    
    # Linha 1: KPIs de Eventos
    if cards.get('total_eventos'):
        add_card_to_dashboard(dashboard_id, cards['total_eventos'], 0, 0, 8, 3)
    if cards.get('usuarios_eventos'):
        add_card_to_dashboard(dashboard_id, cards['usuarios_eventos'], 0, 8, 8, 3)
    if cards.get('tipos_eventos'):
        add_card_to_dashboard(dashboard_id, cards['tipos_eventos'], 0, 16, 8, 3)
    
    # Linha 2: Eventos por Tipo + Eventos por Mês
    if cards.get('eventos_tipo'):
        add_card_to_dashboard(dashboard_id, cards['eventos_tipo'], 3, 0, 12, 5)
    if cards.get('eventos_mes'):
        add_card_to_dashboard(dashboard_id, cards['eventos_mes'], 3, 12, 12, 5)
    
    # Linha 3: Páginas Mais Visitadas
    if cards.get('paginas_visitadas'):
        add_card_to_dashboard(dashboard_id, cards['paginas_visitadas'], 8, 0, 24, 5)
    
    # Linha 4: Satisfação
    if cards.get('satisfacao_geral'):
        add_card_to_dashboard(dashboard_id, cards['satisfacao_geral'], 13, 0, 8, 3)
    if cards.get('distribuicao_ratings'):
        add_card_to_dashboard(dashboard_id, cards['distribuicao_ratings'], 13, 8, 16, 5)
    
    # Linha 5: Satisfação por Mês
    if cards.get('satisfacao_mes'):
        add_card_to_dashboard(dashboard_id, cards['satisfacao_mes'], 18, 0, 24, 5)
    
    return dashboard_id


# ============================================================
# DASHBOARD 5: ANÁLISE FINANCEIRA E ASSINATURAS
# ============================================================

def create_dashboard_financeiro():
    print("\n" + "="*60)
    print("CRIANDO: Análise Financeira e Assinaturas")
    print("="*60)
    
    dashboard_id = create_dashboard(
        "Análise Financeira e Assinaturas",
        "Receita de assinaturas, faturas, planos e análise financeira detalhada"
    )
    if not dashboard_id:
        return None
    
    cards = {}
    
    # KPI: Receita Total de Faturas
    cards['receita_faturas'] = create_card(
        "Receita Total de Faturas",
        "SELECT ROUND(SUM(PAYMENT), 2) AS \"Receita Total\" FROM INVOICES",
        "scalar"
    )
    
    # KPI: Total de Contas
    cards['total_contas'] = create_card(
        "Total de Contas",
        "SELECT COUNT(*) AS \"Total de Contas\" FROM ACCOUNTS",
        "scalar"
    )
    
    # KPI: Assinaturas Ativas
    cards['assinaturas_ativas'] = create_card(
        "Assinaturas Ativas",
        "SELECT COUNT(*) AS \"Assinaturas Ativas\" FROM ACCOUNTS WHERE ACTIVE_SUBSCRIPTION = TRUE",
        "scalar"
    )
    
    # KPI: Taxa de Conversão de Trial
    cards['taxa_conversao_trial'] = create_card(
        "Taxa de Conversão de Trial",
        """SELECT 
    ROUND(
        SUM(CASE WHEN TRIAL_CONVERTED = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        1
    ) AS "Taxa de Conversão (%)"
FROM ACCOUNTS
WHERE TRIAL_ENDS_AT IS NOT NULL""",
        "scalar"
    )
    
    # Receita por Plano
    cards['receita_plano'] = create_card_with_settings(
        "Receita por Plano de Assinatura",
        """SELECT 
    PLAN AS "Plano",
    ROUND(SUM(PAYMENT), 2) AS "Receita",
    COUNT(*) AS "Faturas"
FROM INVOICES
GROUP BY PLAN
ORDER BY "Receita" DESC""",
        "bar",
        {
            "graph.dimensions": ["Plano"],
            "graph.metrics": ["Receita"]
        },
        "Receita gerada por cada plano de assinatura"
    )
    
    # Distribuição de Contas por Plano
    cards['contas_plano'] = create_card_with_settings(
        "Distribuição de Contas por Plano",
        """SELECT 
    PLAN AS "Plano",
    COUNT(*) AS "Contas"
FROM ACCOUNTS
GROUP BY PLAN
ORDER BY "Contas" DESC""",
        "pie",
        {
            "graph.dimensions": ["Plano"],
            "graph.metrics": ["Contas"]
        },
        "Distribuição de contas por plano de assinatura"
    )
    
    # Receita Mensal de Faturas
    cards['receita_mensal_faturas'] = create_card_with_settings(
        "Receita Mensal de Faturas",
        """SELECT 
    FORMATDATETIME(DATE_RECEIVED, 'yyyy-MM') AS "Mês",
    ROUND(SUM(PAYMENT), 2) AS "Receita",
    COUNT(*) AS "Faturas"
FROM INVOICES
GROUP BY FORMATDATETIME(DATE_RECEIVED, 'yyyy-MM')
ORDER BY "Mês" """,
        "combo",
        {
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Receita", "Faturas"]
        },
        "Evolução da receita mensal de faturas"
    )
    
    # Novas Contas por Mês
    cards['novas_contas_mes'] = create_card_with_settings(
        "Novas Contas por Mês",
        """SELECT 
    FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
    COUNT(*) AS "Novas Contas"
FROM ACCOUNTS
GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
ORDER BY "Mês" """,
        "area",
        {
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Novas Contas"]
        },
        "Crescimento de novas contas por mês"
    )
    
    # Contas por País
    cards['contas_pais'] = create_card_with_settings(
        "Contas por País (Top 10)",
        """SELECT 
    COUNTRY AS "País",
    COUNT(*) AS "Contas",
    ROUND(SUM(SEATS), 0) AS "Total de Assentos"
FROM ACCOUNTS
GROUP BY COUNTRY
ORDER BY "Contas" DESC
LIMIT 10""",
        "row",
        {
            "graph.dimensions": ["País"],
            "graph.metrics": ["Contas"]
        },
        "Top 10 países por número de contas"
    )
    
    # Adicionar cards ao dashboard
    print("\nAdicionando cards ao dashboard...")
    
    # Linha 1: KPIs
    if cards.get('receita_faturas'):
        add_card_to_dashboard(dashboard_id, cards['receita_faturas'], 0, 0, 6, 3)
    if cards.get('total_contas'):
        add_card_to_dashboard(dashboard_id, cards['total_contas'], 0, 6, 6, 3)
    if cards.get('assinaturas_ativas'):
        add_card_to_dashboard(dashboard_id, cards['assinaturas_ativas'], 0, 12, 6, 3)
    if cards.get('taxa_conversao_trial'):
        add_card_to_dashboard(dashboard_id, cards['taxa_conversao_trial'], 0, 18, 6, 3)
    
    # Linha 2: Receita por Plano + Distribuição por Plano
    if cards.get('receita_plano'):
        add_card_to_dashboard(dashboard_id, cards['receita_plano'], 3, 0, 14, 5)
    if cards.get('contas_plano'):
        add_card_to_dashboard(dashboard_id, cards['contas_plano'], 3, 14, 10, 5)
    
    # Linha 3: Receita Mensal + Novas Contas
    if cards.get('receita_mensal_faturas'):
        add_card_to_dashboard(dashboard_id, cards['receita_mensal_faturas'], 8, 0, 12, 5)
    if cards.get('novas_contas_mes'):
        add_card_to_dashboard(dashboard_id, cards['novas_contas_mes'], 8, 12, 12, 5)
    
    # Linha 4: Contas por País
    if cards.get('contas_pais'):
        add_card_to_dashboard(dashboard_id, cards['contas_pais'], 13, 0, 24, 5)
    
    return dashboard_id


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CRIAÇÃO DE DASHBOARDS DE ECOMMERCE - METABASE")
    print("=" * 60)
    print(f"URL: {METABASE_URL}")
    print(f"Database ID: {DATABASE_ID}")
    print()
    
    results = {}
    
    # Dashboard 1: Visão Geral de Vendas
    results['vendas'] = create_dashboard_vendas()
    time.sleep(1)
    
    # Dashboard 2: Análise de Produtos
    results['produtos'] = create_dashboard_produtos()
    time.sleep(1)
    
    # Dashboard 3: Análise de Clientes
    results['clientes'] = create_dashboard_clientes()
    time.sleep(1)
    
    # Dashboard 4: Funil de Conversão
    results['conversao'] = create_dashboard_conversao()
    time.sleep(1)
    
    # Dashboard 5: Análise Financeira
    results['financeiro'] = create_dashboard_financeiro()
    
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    for name, dashboard_id in results.items():
        status = f"✓ ID: {dashboard_id}" if dashboard_id else "✗ FALHOU"
        print(f"  {name}: {status}")
    
    print("\nAcesse os dashboards em:")
    print(f"  {METABASE_URL}/collection/root")
