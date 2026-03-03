#!/usr/bin/env python3
"""
Criação automatizada de dashboards de ecommerce no Metabase via API REST.

Este script conecta-se a uma instância do Metabase e cria automaticamente
cinco dashboards temáticos para análise de ecommerce, utilizando o Sample
Database (H2) como fonte de dados. Cada dashboard é composto por múltiplos
cards (questões) com visualizações adequadas para cada tipo de análise.

Dashboards criados:
    1. Visão Geral de Vendas    — KPIs executivos, receita e tendências
    2. Análise de Produtos      — Categorias, avaliações e fornecedores
    3. Análise de Clientes      — Aquisição, LTV e segmentação RFM
    4. Funil de Conversão       — Eventos analíticos e satisfação
    5. Análise Financeira       — Assinaturas, faturas e planos

Uso:
    Configure as variáveis de ambiente METABASE_URL e METABASE_API_KEY,
    ou ajuste as constantes na seção de configuração abaixo, e execute:

        python create_ecommerce_dashboards.py

Requisitos:
    - Python 3.8+
    - requests >= 2.28.0
    - Instância do Metabase com API Key habilitada
    - Sample Database (H2) configurado como fonte de dados (ID: 1)
"""

import os
import requests


# =============================================================================
# CONFIGURAÇÃO — ajuste estas variáveis para o seu ambiente
# =============================================================================

METABASE_URL = os.getenv("METABASE_URL", "https://analytics.arconde.cloud")
API_KEY = os.getenv("METABASE_API_KEY", "mb_o8a+35jbsOddbO/l105odmnwGDh3b1KWyBomDTIc1IE=")

# ID do banco de dados no Metabase (1 = Sample Database H2 padrão)
DATABASE_ID = int(os.getenv("METABASE_DATABASE_ID", "1"))

# Cabeçalhos padrão para todas as requisições à API
REQUEST_HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
}


# =============================================================================
# MAPEAMENTO DE TABELAS — IDs das tabelas no Sample Database
# =============================================================================
# Estes IDs são fixos para o Sample Database padrão do Metabase.
# Se você usar um banco de dados diferente, consulte /api/database/{id}/metadata
# para obter os IDs corretos.

TABLE_ID = {
    "people":           1,   # Clientes cadastrados
    "orders":           2,   # Pedidos realizados
    "products":         3,   # Catálogo de produtos
    "reviews":          4,   # Avaliações de produtos
    "feedback":         5,   # Pesquisas de satisfação
    "accounts":         6,   # Contas de assinatura
    "analytic_events":  7,   # Eventos de comportamento
    "invoices":         8,   # Faturas de assinatura
}


# =============================================================================
# FUNÇÕES AUXILIARES DE API
# =============================================================================

def create_card(name, sql_query, visualization_type, description, viz_settings=None):
    """Cria um card (questão) no Metabase usando uma query SQL nativa.

    Um card no Metabase é uma visualização individual — pode ser um número
    escalar, gráfico de barras, linha, pizza, tabela, etc. Cada card é
    independente e pode ser adicionado a um ou mais dashboards.

    Args:
        name (str): Título do card exibido no dashboard.
        sql_query (str): Query SQL que alimenta o card. Deve ser compatível
            com o dialeto H2 (Sample Database) ou o banco configurado.
        visualization_type (str): Tipo de visualização do Metabase.
            Valores aceitos: "scalar", "line", "bar", "row", "pie",
            "area", "combo", "table".
        description (str): Descrição do card exibida como tooltip no dashboard.
        viz_settings (dict, optional): Configurações adicionais de visualização,
            como rótulos de eixos, dimensões e métricas. Padrão: None (vazio).

    Returns:
        int | None: ID do card criado, ou None em caso de falha.

    Examples:
        Criar um KPI de receita total:
        >>> card_id = create_card(
        ...     name="Receita Total",
        ...     sql_query='SELECT SUM(TOTAL) AS "Receita" FROM ORDERS',
        ...     visualization_type="scalar",
        ...     description="Soma de todos os pedidos"
        ... )
        >>> print(card_id)  # Ex: 42
    """
    payload = {
        "name": name,
        "description": description,
        "display": visualization_type,
        "dataset_query": {
            "type": "native",
            "native": {
                "query": sql_query,
                "template-tags": {},
            },
            "database": DATABASE_ID,
        },
        "visualization_settings": viz_settings or {},
    }

    response = requests.post(
        f"{METABASE_URL}/api/card",
        headers=REQUEST_HEADERS,
        json=payload,
    )

    if response.status_code in (200, 201):
        card = response.json()
        print(f"  ✓ Card criado: {name} (ID: {card['id']})")
        return card["id"]

    print(f"  ✗ Falha ao criar card '{name}': {response.status_code} — {response.text[:200]}")
    return None


def create_dashboard(name, description):
    """Cria um dashboard vazio no Metabase.

    O dashboard é criado sem cards. Use add_cards_to_dashboard() em seguida
    para popular o dashboard com as visualizações desejadas.

    Args:
        name (str): Nome do dashboard exibido na interface do Metabase.
        description (str): Descrição do propósito do dashboard.

    Returns:
        int | None: ID do dashboard criado, ou None em caso de falha.

    Examples:
        >>> dashboard_id = create_dashboard(
        ...     name="Visão Geral de Vendas",
        ...     description="KPIs executivos de receita e pedidos"
        ... )
        >>> print(dashboard_id)  # Ex: 10
    """
    payload = {
        "name": name,
        "description": description,
    }

    response = requests.post(
        f"{METABASE_URL}/api/dashboard",
        headers=REQUEST_HEADERS,
        json=payload,
    )

    if response.status_code in (200, 201):
        dashboard = response.json()
        print(f"✓ Dashboard criado: {name} (ID: {dashboard['id']})")
        return dashboard["id"]

    print(f"✗ Falha ao criar dashboard '{name}': {response.status_code} — {response.text[:200]}")
    return None


def add_cards_to_dashboard(dashboard_id, cards_layout):
    """Adiciona múltiplos cards a um dashboard em uma única requisição.

    O Metabase aceita um array de cards no endpoint PUT /api/dashboard/{id}/cards,
    o que é mais eficiente do que adicionar um card por vez. Cada card recebe
    um ID temporário negativo (exigido pela API) que é substituído pelo ID
    real após a criação.

    Args:
        dashboard_id (int): ID do dashboard de destino.
        cards_layout (list[dict]): Lista de posicionamentos de cards. Cada
            item deve conter:
            - card_id (int): ID do card a ser adicionado.
            - row (int): Linha inicial no grid do dashboard (base 0).
            - col (int): Coluna inicial no grid (base 0, máx 24 colunas).
            - size_x (int): Largura em colunas do grid (1–24).
            - size_y (int): Altura em linhas do grid (mínimo 2).

    Returns:
        bool: True se os cards foram adicionados com sucesso, False caso contrário.

    Examples:
        Adicionar dois KPIs lado a lado na primeira linha:
        >>> success = add_cards_to_dashboard(
        ...     dashboard_id=10,
        ...     cards_layout=[
        ...         {"card_id": 42, "row": 0, "col": 0,  "size_x": 6, "size_y": 3},
        ...         {"card_id": 43, "row": 0, "col": 6,  "size_x": 6, "size_y": 3},
        ...     ]
        ... )
    """
    # Constrói o payload com IDs temporários negativos (requisito da API do Metabase)
    cards_payload = [
        {
            "id": -(position + 1),          # ID temporário negativo único por card
            "card_id": card["card_id"],
            "row": card["row"],
            "col": card["col"],
            "size_x": card["size_x"],
            "size_y": card["size_y"],
            "series": [],
            "parameter_mappings": [],
            "visualization_settings": {},
        }
        for position, card in enumerate(cards_layout)
    ]

    response = requests.put(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}/cards",
        headers=REQUEST_HEADERS,
        json={"cards": cards_payload},
    )

    if response.status_code in (200, 201):
        added_count = len(response.json().get("cards", []))
        print(f"  ✓ {added_count} cards adicionados ao dashboard {dashboard_id}")
        return True

    print(f"  ✗ Falha ao adicionar cards: {response.status_code} — {response.text[:300]}")
    return False


def move_dashboard_to_collection(dashboard_id, collection_id):
    """Move um dashboard para uma coleção específica no Metabase.

    Args:
        dashboard_id (int): ID do dashboard a ser movido.
        collection_id (int): ID da coleção de destino.

    Returns:
        bool: True se o dashboard foi movido com sucesso, False caso contrário.
    """
    response = requests.put(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}",
        headers=REQUEST_HEADERS,
        json={"collection_id": collection_id},
    )

    if response.status_code in (200, 201):
        dashboard_name = response.json().get("name", f"ID {dashboard_id}")
        print(f"  ✓ Dashboard '{dashboard_name}' movido para coleção {collection_id}")
        return True

    print(f"  ✗ Falha ao mover dashboard {dashboard_id}: {response.status_code}")
    return False


def create_collection(name, description, color="#509EE3"):
    """Cria uma coleção no Metabase para organizar dashboards e cards.

    Args:
        name (str): Nome da coleção.
        description (str): Descrição do propósito da coleção.
        color (str, optional): Cor hexadecimal da coleção. Padrão: azul Metabase.

    Returns:
        int | None: ID da coleção criada, ou None em caso de falha.
    """
    payload = {
        "name": name,
        "description": description,
        "color": color,
    }

    response = requests.post(
        f"{METABASE_URL}/api/collection",
        headers=REQUEST_HEADERS,
        json=payload,
    )

    if response.status_code in (200, 201):
        collection = response.json()
        print(f"✓ Coleção criada: {name} (ID: {collection['id']})")
        return collection["id"]

    print(f"✗ Falha ao criar coleção '{name}': {response.status_code} — {response.text[:200]}")
    return None


# =============================================================================
# DASHBOARD 1: VISÃO GERAL DE VENDAS
# Foco: KPIs executivos — receita, volume de pedidos e tendências temporais
# =============================================================================

def create_sales_overview_dashboard():
    """Cria o dashboard de Visão Geral de Vendas com KPIs e tendências.

    Este dashboard é voltado para gestores e executivos que precisam de uma
    visão rápida da saúde do negócio. Inclui métricas de receita, volume de
    pedidos, análise por canal de aquisição e distribuição geográfica.

    Returns:
        int | None: ID do dashboard criado, ou None em caso de falha.
    """
    print("\n" + "=" * 60)
    print("CRIANDO: Visão Geral de Vendas")
    print("=" * 60)

    dashboard_id = create_dashboard(
        name="Visão Geral de Vendas",
        description="KPIs executivos de vendas: receita total, pedidos, ticket médio e crescimento",
    )
    if not dashboard_id:
        return None

    # --- KPIs da primeira linha ---
    kpi_total_revenue = create_card(
        name="Receita Total",
        sql_query='SELECT SUM(TOTAL) AS "Receita Total" FROM ORDERS',
        visualization_type="scalar",
        description="Soma de todos os valores de pedidos realizados",
    )

    kpi_total_orders = create_card(
        name="Total de Pedidos",
        sql_query='SELECT COUNT(*) AS "Total de Pedidos" FROM ORDERS',
        visualization_type="scalar",
        description="Número total de pedidos realizados no período",
    )

    kpi_average_ticket = create_card(
        name="Ticket Médio",
        sql_query='SELECT ROUND(AVG(TOTAL), 2) AS "Ticket Médio" FROM ORDERS',
        visualization_type="scalar",
        description="Valor médio por pedido",
    )

    kpi_unique_customers = create_card(
        name="Clientes Únicos",
        sql_query='SELECT COUNT(DISTINCT USER_ID) AS "Clientes Únicos" FROM ORDERS',
        visualization_type="scalar",
        description="Número de clientes únicos que realizaram pelo menos um pedido",
    )

    kpi_total_discounts = create_card(
        name="Desconto Total",
        sql_query='SELECT ROUND(SUM(DISCOUNT), 2) AS "Desconto Total" FROM ORDERS WHERE DISCOUNT > 0',
        visualization_type="scalar",
        description="Soma total de descontos aplicados nos pedidos",
    )

    # --- Gráficos de tendência temporal ---
    chart_monthly_revenue = create_card(
        name="Receita Mensal",
        sql_query="""
            SELECT
                FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
                SUM(TOTAL)                             AS "Receita (R$)"
            FROM ORDERS
            GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
            ORDER BY "Mês"
        """,
        visualization_type="line",
        description="Evolução da receita total ao longo dos meses",
        viz_settings={
            "graph.x_axis.title_text": "Mês",
            "graph.y_axis.title_text": "Receita (R$)",
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Receita (R$)"],
        },
    )

    chart_monthly_orders = create_card(
        name="Pedidos por Mês",
        sql_query="""
            SELECT
                FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
                COUNT(*)                               AS "Quantidade de Pedidos"
            FROM ORDERS
            GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
            ORDER BY "Mês"
        """,
        visualization_type="bar",
        description="Volume de pedidos por mês",
        viz_settings={
            "graph.x_axis.title_text": "Mês",
            "graph.y_axis.title_text": "Quantidade de Pedidos",
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Quantidade de Pedidos"],
        },
    )

    # --- Análise por canal e geografia ---
    chart_revenue_by_channel = create_card(
        name="Receita por Canal de Aquisição",
        sql_query="""
            SELECT
                p.SOURCE   AS "Canal",
                SUM(o.TOTAL) AS "Receita (R$)",
                COUNT(o.ID)  AS "Pedidos"
            FROM ORDERS o
            JOIN PEOPLE p ON o.USER_ID = p.ID
            GROUP BY p.SOURCE
            ORDER BY "Receita (R$)" DESC
        """,
        visualization_type="bar",
        description="Receita total gerada por cada canal de aquisição de clientes",
        viz_settings={
            "graph.x_axis.title_text": "Canal",
            "graph.y_axis.title_text": "Receita (R$)",
            "graph.dimensions": ["Canal"],
            "graph.metrics": ["Receita (R$)"],
        },
    )

    chart_top_states_by_revenue = create_card(
        name="Top 10 Estados por Receita",
        sql_query="""
            SELECT
                p.STATE      AS "Estado",
                SUM(o.TOTAL) AS "Receita (R$)",
                COUNT(o.ID)  AS "Pedidos"
            FROM ORDERS o
            JOIN PEOPLE p ON o.USER_ID = p.ID
            GROUP BY p.STATE
            ORDER BY "Receita (R$)" DESC
            LIMIT 10
        """,
        visualization_type="row",
        description="Os 10 estados que mais geram receita",
        viz_settings={
            "graph.x_axis.title_text": "Receita (R$)",
            "graph.y_axis.title_text": "Estado",
            "graph.dimensions": ["Estado"],
            "graph.metrics": ["Receita (R$)"],
        },
    )

    # Gráfico combo: receita (linha) vs descontos (barras) por mês
    # Útil para identificar se campanhas de desconto estão impactando a margem
    chart_revenue_vs_discounts = create_card(
        name="Receita vs Desconto por Mês",
        sql_query="""
            SELECT
                FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
                SUM(TOTAL)                             AS "Receita",
                SUM(DISCOUNT)                          AS "Desconto"
            FROM ORDERS
            GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
            ORDER BY "Mês"
        """,
        visualization_type="combo",
        description="Comparação mensal entre receita total e descontos concedidos",
        viz_settings={
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Receita", "Desconto"],
        },
    )

    # Distribuição dos pedidos por faixa de valor
    # Ajuda a entender o perfil de compra e definir estratégias de precificação
    chart_order_value_distribution = create_card(
        name="Distribuição por Faixa de Valor",
        sql_query="""
            SELECT
                CASE
                    WHEN TOTAL < 20              THEN 'Até R$20'
                    WHEN TOTAL BETWEEN 20 AND 50 THEN 'R$20 - R$50'
                    WHEN TOTAL BETWEEN 50 AND 100 THEN 'R$50 - R$100'
                    ELSE 'R$100 - R$200'
                END AS "Faixa de Valor",
                COUNT(*) AS "Pedidos"
            FROM ORDERS
            GROUP BY
                CASE
                    WHEN TOTAL < 20              THEN 'Até R$20'
                    WHEN TOTAL BETWEEN 20 AND 50 THEN 'R$20 - R$50'
                    WHEN TOTAL BETWEEN 50 AND 100 THEN 'R$50 - R$100'
                    ELSE 'R$100 - R$200'
                END
            ORDER BY MIN(TOTAL)
        """,
        visualization_type="pie",
        description="Proporção de pedidos em cada faixa de valor",
        viz_settings={
            "graph.dimensions": ["Faixa de Valor"],
            "graph.metrics": ["Pedidos"],
        },
    )

    # --- Layout do dashboard (grid de 24 colunas) ---
    # Linha 0 (row=0): 5 KPIs de largura 4 cada (total = 20 colunas)
    # Linha 3 (row=3): Receita Mensal (12 col) + Pedidos por Mês (12 col)
    # Linha 8 (row=8): Receita por Canal (12 col) + Top Estados (12 col)
    # Linha 13 (row=13): Receita vs Desconto (14 col) + Distribuição (10 col)
    cards_layout = []

    kpi_cards = [
        kpi_total_revenue, kpi_total_orders, kpi_average_ticket,
        kpi_unique_customers, kpi_total_discounts,
    ]
    kpi_column_positions = [0, 5, 10, 15, 20]

    for card_id, col_position in zip(kpi_cards, kpi_column_positions):
        if card_id:
            cards_layout.append({
                "card_id": card_id, "row": 0, "col": col_position,
                "size_x": 4, "size_y": 3,
            })

    if chart_monthly_revenue:
        cards_layout.append({"card_id": chart_monthly_revenue,    "row": 3, "col": 0,  "size_x": 12, "size_y": 5})
    if chart_monthly_orders:
        cards_layout.append({"card_id": chart_monthly_orders,     "row": 3, "col": 12, "size_x": 12, "size_y": 5})
    if chart_revenue_by_channel:
        cards_layout.append({"card_id": chart_revenue_by_channel, "row": 8, "col": 0,  "size_x": 12, "size_y": 5})
    if chart_top_states_by_revenue:
        cards_layout.append({"card_id": chart_top_states_by_revenue, "row": 8, "col": 12, "size_x": 12, "size_y": 5})
    if chart_revenue_vs_discounts:
        cards_layout.append({"card_id": chart_revenue_vs_discounts, "row": 13, "col": 0, "size_x": 14, "size_y": 5})
    if chart_order_value_distribution:
        cards_layout.append({"card_id": chart_order_value_distribution, "row": 13, "col": 14, "size_x": 10, "size_y": 5})

    add_cards_to_dashboard(dashboard_id, cards_layout)
    return dashboard_id


# =============================================================================
# DASHBOARD 2: ANÁLISE DE PRODUTOS
# Foco: Performance do catálogo — categorias, avaliações e fornecedores
# =============================================================================

def create_products_dashboard():
    """Cria o dashboard de Análise de Produtos.

    Voltado para gerentes de produto e compradores, este dashboard permite
    identificar quais categorias e produtos geram mais receita, quais têm
    as melhores avaliações e como os fornecedores se comparam.

    Returns:
        int | None: ID do dashboard criado, ou None em caso de falha.
    """
    print("\n" + "=" * 60)
    print("CRIANDO: Análise de Produtos")
    print("=" * 60)

    dashboard_id = create_dashboard(
        name="Análise de Produtos",
        description="Performance do catálogo: categorias, avaliações, preços e fornecedores",
    )
    if not dashboard_id:
        return None

    # --- KPIs do catálogo ---
    kpi_total_products = create_card(
        name="Total de Produtos",
        sql_query='SELECT COUNT(*) AS "Total de Produtos" FROM PRODUCTS',
        visualization_type="scalar",
        description="Total de produtos ativos no catálogo",
    )

    kpi_total_categories = create_card(
        name="Categorias",
        sql_query='SELECT COUNT(DISTINCT CATEGORY) AS "Categorias" FROM PRODUCTS',
        visualization_type="scalar",
        description="Número de categorias de produtos disponíveis",
    )

    kpi_average_rating = create_card(
        name="Avaliação Média",
        sql_query='SELECT ROUND(AVG(RATING), 2) AS "Avaliação Média" FROM PRODUCTS',
        visualization_type="scalar",
        description="Avaliação média de todos os produtos no catálogo",
    )

    kpi_average_price = create_card(
        name="Preço Médio",
        sql_query='SELECT ROUND(AVG(PRICE), 2) AS "Preço Médio" FROM PRODUCTS',
        visualization_type="scalar",
        description="Preço médio dos produtos no catálogo",
    )

    # --- Análise por categoria ---
    chart_revenue_by_category = create_card(
        name="Receita por Categoria de Produto",
        sql_query="""
            SELECT
                p.CATEGORY   AS "Categoria",
                SUM(o.TOTAL) AS "Receita",
                COUNT(o.ID)  AS "Pedidos"
            FROM ORDERS o
            JOIN PRODUCTS p ON o.PRODUCT_ID = p.ID
            GROUP BY p.CATEGORY
            ORDER BY "Receita" DESC
        """,
        visualization_type="bar",
        description="Receita total gerada por cada categoria de produto",
        viz_settings={
            "graph.dimensions": ["Categoria"],
            "graph.metrics": ["Receita"],
        },
    )

    # Pizza de participação: mostra o peso relativo de cada categoria
    chart_category_share = create_card(
        name="Participação de Vendas por Categoria",
        sql_query="""
            SELECT
                p.CATEGORY  AS "Categoria",
                COUNT(o.ID) AS "Pedidos"
            FROM ORDERS o
            JOIN PRODUCTS p ON o.PRODUCT_ID = p.ID
            GROUP BY p.CATEGORY
            ORDER BY "Pedidos" DESC
        """,
        visualization_type="pie",
        description="Participação percentual de cada categoria no total de pedidos",
        viz_settings={
            "graph.dimensions": ["Categoria"],
            "graph.metrics": ["Pedidos"],
        },
    )

    # Top 10 produtos por volume de pedidos — identifica os best-sellers
    chart_top_products = create_card(
        name="Top 10 Produtos Mais Vendidos",
        sql_query="""
            SELECT
                p.TITLE      AS "Produto",
                p.CATEGORY   AS "Categoria",
                COUNT(o.ID)  AS "Pedidos",
                SUM(o.TOTAL) AS "Receita Total"
            FROM ORDERS o
            JOIN PRODUCTS p ON o.PRODUCT_ID = p.ID
            GROUP BY p.ID, p.TITLE, p.CATEGORY
            ORDER BY "Pedidos" DESC
            LIMIT 10
        """,
        visualization_type="row",
        description="Os 10 produtos com maior número de pedidos",
        viz_settings={
            "graph.dimensions": ["Produto"],
            "graph.metrics": ["Pedidos"],
        },
    )

    chart_rating_by_category = create_card(
        name="Avaliação Média por Categoria",
        sql_query="""
            SELECT
                p.CATEGORY              AS "Categoria",
                ROUND(AVG(r.RATING), 2) AS "Avaliação Média",
                COUNT(r.ID)             AS "Total de Avaliações"
            FROM PRODUCTS p
            LEFT JOIN REVIEWS r ON p.ID = r.PRODUCT_ID
            GROUP BY p.CATEGORY
            ORDER BY "Avaliação Média" DESC
        """,
        visualization_type="bar",
        description="Avaliação média dos produtos agrupada por categoria",
        viz_settings={
            "graph.dimensions": ["Categoria"],
            "graph.metrics": ["Avaliação Média"],
        },
    )

    chart_price_by_category = create_card(
        name="Preço Médio por Categoria",
        sql_query="""
            SELECT
                CATEGORY                 AS "Categoria",
                ROUND(MIN(PRICE), 2)     AS "Preço Mínimo",
                ROUND(AVG(PRICE), 2)     AS "Preço Médio",
                ROUND(MAX(PRICE), 2)     AS "Preço Máximo"
            FROM PRODUCTS
            GROUP BY CATEGORY
            ORDER BY "Preço Médio" DESC
        """,
        visualization_type="bar",
        description="Faixa de preços (mínimo, médio, máximo) por categoria",
        viz_settings={
            "graph.dimensions": ["Categoria"],
            "graph.metrics": ["Preço Médio"],
        },
    )

    # Produtos com melhor avaliação: filtra por mínimo de 3 avaliações
    # para evitar distorções de produtos com pouquíssimas avaliações
    chart_top_rated_products = create_card(
        name="Produtos Melhor Avaliados",
        sql_query="""
            SELECT
                p.TITLE      AS "Produto",
                p.CATEGORY   AS "Categoria",
                p.PRICE      AS "Preço",
                p.RATING     AS "Avaliação",
                COUNT(r.ID)  AS "Qtd Avaliações"
            FROM PRODUCTS p
            LEFT JOIN REVIEWS r ON p.ID = r.PRODUCT_ID
            GROUP BY p.ID, p.TITLE, p.CATEGORY, p.PRICE, p.RATING
            HAVING COUNT(r.ID) >= 3
            ORDER BY p.RATING DESC, "Qtd Avaliações" DESC
            LIMIT 10
        """,
        visualization_type="table",
        description="Top 10 produtos com melhor avaliação (mínimo 3 avaliações para relevância estatística)",
    )

    chart_revenue_by_vendor = create_card(
        name="Receita por Fornecedor (Top 10)",
        sql_query="""
            SELECT
                p.VENDOR     AS "Fornecedor",
                SUM(o.TOTAL) AS "Receita",
                COUNT(o.ID)  AS "Pedidos"
            FROM ORDERS o
            JOIN PRODUCTS p ON o.PRODUCT_ID = p.ID
            GROUP BY p.VENDOR
            ORDER BY "Receita" DESC
            LIMIT 10
        """,
        visualization_type="row",
        description="Top 10 fornecedores por receita gerada",
        viz_settings={
            "graph.dimensions": ["Fornecedor"],
            "graph.metrics": ["Receita"],
        },
    )

    # --- Layout do dashboard ---
    cards_layout = []

    kpi_cards = [kpi_total_products, kpi_total_categories, kpi_average_rating, kpi_average_price]
    for index, card_id in enumerate(kpi_cards):
        if card_id:
            cards_layout.append({
                "card_id": card_id, "row": 0, "col": index * 6,
                "size_x": 6, "size_y": 3,
            })

    if chart_revenue_by_category:
        cards_layout.append({"card_id": chart_revenue_by_category, "row": 3, "col": 0,  "size_x": 14, "size_y": 5})
    if chart_category_share:
        cards_layout.append({"card_id": chart_category_share,      "row": 3, "col": 14, "size_x": 10, "size_y": 5})
    if chart_top_products:
        cards_layout.append({"card_id": chart_top_products,        "row": 8, "col": 0,  "size_x": 12, "size_y": 6})
    if chart_rating_by_category:
        cards_layout.append({"card_id": chart_rating_by_category,  "row": 8, "col": 12, "size_x": 12, "size_y": 6})
    if chart_price_by_category:
        cards_layout.append({"card_id": chart_price_by_category,   "row": 14, "col": 0,  "size_x": 12, "size_y": 5})
    if chart_revenue_by_vendor:
        cards_layout.append({"card_id": chart_revenue_by_vendor,   "row": 14, "col": 12, "size_x": 12, "size_y": 5})
    if chart_top_rated_products:
        cards_layout.append({"card_id": chart_top_rated_products,  "row": 19, "col": 0,  "size_x": 24, "size_y": 5})

    add_cards_to_dashboard(dashboard_id, cards_layout)
    return dashboard_id


# =============================================================================
# DASHBOARD 3: ANÁLISE DE CLIENTES
# Foco: Comportamento e perfil — aquisição, LTV e segmentação RFM
# =============================================================================

def create_customers_dashboard():
    """Cria o dashboard de Análise de Clientes.

    Este dashboard apoia equipes de marketing e CRM com métricas de aquisição
    de clientes, Lifetime Value (LTV), segmentação por frequência de compra
    (análise RFM simplificada) e distribuição geográfica e demográfica.

    Returns:
        int | None: ID do dashboard criado, ou None em caso de falha.
    """
    print("\n" + "=" * 60)
    print("CRIANDO: Análise de Clientes")
    print("=" * 60)

    dashboard_id = create_dashboard(
        name="Análise de Clientes",
        description="Comportamento e perfil dos clientes: aquisição, retenção, segmentação e LTV",
    )
    if not dashboard_id:
        return None

    # --- KPIs de clientes ---
    kpi_total_customers = create_card(
        name="Total de Clientes",
        sql_query='SELECT COUNT(*) AS "Total de Clientes" FROM PEOPLE',
        visualization_type="scalar",
        description="Total de clientes cadastrados na plataforma",
    )

    kpi_customers_with_orders = create_card(
        name="Clientes com Pedidos",
        sql_query='SELECT COUNT(DISTINCT USER_ID) AS "Clientes com Pedidos" FROM ORDERS',
        visualization_type="scalar",
        description="Clientes que realizaram pelo menos um pedido",
    )

    kpi_orders_per_customer = create_card(
        name="Pedidos por Cliente",
        sql_query="""
            SELECT ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT USER_ID), 2)
                AS "Pedidos por Cliente"
            FROM ORDERS
        """,
        visualization_type="scalar",
        description="Média de pedidos por cliente — indicador de recorrência",
    )

    # LTV (Lifetime Value): receita total dividida pelo número de clientes únicos
    kpi_average_ltv = create_card(
        name="LTV Médio",
        sql_query="""
            SELECT ROUND(SUM(TOTAL) / COUNT(DISTINCT USER_ID), 2) AS "LTV Médio"
            FROM ORDERS
        """,
        visualization_type="scalar",
        description="Lifetime Value médio por cliente — receita total gerada por cliente",
    )

    # --- Análise de aquisição e crescimento ---
    chart_new_customers_per_month = create_card(
        name="Novos Clientes por Mês",
        sql_query="""
            SELECT
                FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
                COUNT(*)                               AS "Novos Clientes"
            FROM PEOPLE
            GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
            ORDER BY "Mês"
        """,
        visualization_type="area",
        description="Crescimento da base de clientes ao longo do tempo",
        viz_settings={
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Novos Clientes"],
        },
    )

    chart_customers_by_channel = create_card(
        name="Clientes por Canal de Aquisição",
        sql_query="""
            SELECT
                SOURCE                                                        AS "Canal",
                COUNT(*)                                                      AS "Clientes",
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)           AS "Percentual"
            FROM PEOPLE
            GROUP BY SOURCE
            ORDER BY "Clientes" DESC
        """,
        visualization_type="pie",
        description="Distribuição de clientes por canal de aquisição (Facebook, Google, etc.)",
        viz_settings={
            "pie.dimension": "Canal",
            "pie.metric": "Clientes",
            "graph.dimensions": ["Canal"],
            "graph.metrics": ["Clientes"],
        },
    )

    chart_top_states_by_customers = create_card(
        name="Top 10 Estados por Número de Clientes",
        sql_query="""
            SELECT
                STATE       AS "Estado",
                COUNT(*)    AS "Clientes"
            FROM PEOPLE
            GROUP BY STATE
            ORDER BY "Clientes" DESC
            LIMIT 10
        """,
        visualization_type="row",
        description="Estados com maior concentração de clientes",
        viz_settings={
            "graph.dimensions": ["Estado"],
            "graph.metrics": ["Clientes"],
        },
    )

    # Segmentação RFM simplificada por frequência de compra:
    # Classifica clientes em grupos para identificar VIPs e clientes em risco
    chart_purchase_frequency_segments = create_card(
        name="Segmentação por Frequência de Compra",
        sql_query="""
            SELECT
                CASE
                    WHEN order_count = 1                THEN '1 pedido (One-time)'
                    WHEN order_count = 2                THEN '2 pedidos'
                    WHEN order_count BETWEEN 3 AND 5    THEN '3-5 pedidos'
                    WHEN order_count BETWEEN 6 AND 10   THEN '6-10 pedidos'
                    ELSE 'Mais de 10 pedidos (VIP)'
                END AS "Segmento",
                COUNT(*) AS "Clientes"
            FROM (
                SELECT USER_ID, COUNT(*) AS order_count
                FROM ORDERS
                GROUP BY USER_ID
            ) customer_orders
            GROUP BY
                CASE
                    WHEN order_count = 1                THEN '1 pedido (One-time)'
                    WHEN order_count = 2                THEN '2 pedidos'
                    WHEN order_count BETWEEN 3 AND 5    THEN '3-5 pedidos'
                    WHEN order_count BETWEEN 6 AND 10   THEN '6-10 pedidos'
                    ELSE 'Mais de 10 pedidos (VIP)'
                END
            ORDER BY MIN(order_count)
        """,
        visualization_type="pie",
        description="Segmentação de clientes por frequência de compra (análise RFM simplificada)",
        viz_settings={
            "graph.dimensions": ["Segmento"],
            "graph.metrics": ["Clientes"],
        },
    )

    chart_top_customers_by_revenue = create_card(
        name="Top 10 Clientes por Receita",
        sql_query="""
            SELECT
                p.NAME       AS "Cliente",
                p.EMAIL      AS "Email",
                p.STATE      AS "Estado",
                COUNT(o.ID)  AS "Pedidos",
                SUM(o.TOTAL) AS "Receita Total"
            FROM ORDERS o
            JOIN PEOPLE p ON o.USER_ID = p.ID
            GROUP BY p.ID, p.NAME, p.EMAIL, p.STATE
            ORDER BY "Receita Total" DESC
            LIMIT 10
        """,
        visualization_type="table",
        description="Os 10 clientes que mais geraram receita — base para programas de fidelidade",
    )

    # Análise demográfica: receita por faixa etária
    # Ajuda a identificar o público mais valioso para direcionar campanhas
    chart_revenue_by_age_group = create_card(
        name="Receita por Faixa Etária",
        sql_query="""
            SELECT
                CASE
                    WHEN DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE) < 25  THEN 'Até 24 anos'
                    WHEN DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE) < 35  THEN '25-34 anos'
                    WHEN DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE) < 45  THEN '35-44 anos'
                    WHEN DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE) < 55  THEN '45-54 anos'
                    ELSE '55+ anos'
                END AS "Faixa Etária",
                SUM(o.TOTAL) AS "Receita",
                COUNT(o.ID)  AS "Pedidos"
            FROM ORDERS o
            JOIN PEOPLE p ON o.USER_ID = p.ID
            WHERE p.BIRTH_DATE IS NOT NULL
            GROUP BY
                CASE
                    WHEN DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE) < 25  THEN 'Até 24 anos'
                    WHEN DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE) < 35  THEN '25-34 anos'
                    WHEN DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE) < 45  THEN '35-44 anos'
                    WHEN DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE) < 55  THEN '45-54 anos'
                    ELSE '55+ anos'
                END
            ORDER BY MIN(DATEDIFF('YEAR', p.BIRTH_DATE, CURRENT_DATE))
        """,
        visualization_type="bar",
        description="Receita total gerada por faixa etária dos clientes",
        viz_settings={
            "graph.dimensions": ["Faixa Etária"],
            "graph.metrics": ["Receita"],
        },
    )

    # --- Layout do dashboard ---
    cards_layout = []

    kpi_cards = [kpi_total_customers, kpi_customers_with_orders, kpi_orders_per_customer, kpi_average_ltv]
    for index, card_id in enumerate(kpi_cards):
        if card_id:
            cards_layout.append({
                "card_id": card_id, "row": 0, "col": index * 6,
                "size_x": 6, "size_y": 3,
            })

    if chart_new_customers_per_month:
        cards_layout.append({"card_id": chart_new_customers_per_month,      "row": 3,  "col": 0,  "size_x": 14, "size_y": 5})
    if chart_customers_by_channel:
        cards_layout.append({"card_id": chart_customers_by_channel,         "row": 3,  "col": 14, "size_x": 10, "size_y": 5})
    if chart_top_states_by_customers:
        cards_layout.append({"card_id": chart_top_states_by_customers,      "row": 8,  "col": 0,  "size_x": 12, "size_y": 5})
    if chart_purchase_frequency_segments:
        cards_layout.append({"card_id": chart_purchase_frequency_segments,  "row": 8,  "col": 12, "size_x": 12, "size_y": 5})
    if chart_revenue_by_age_group:
        cards_layout.append({"card_id": chart_revenue_by_age_group,         "row": 13, "col": 0,  "size_x": 24, "size_y": 5})
    if chart_top_customers_by_revenue:
        cards_layout.append({"card_id": chart_top_customers_by_revenue,     "row": 18, "col": 0,  "size_x": 24, "size_y": 5})

    add_cards_to_dashboard(dashboard_id, cards_layout)
    return dashboard_id


# =============================================================================
# DASHBOARD 4: FUNIL DE CONVERSÃO E COMPORTAMENTO
# Foco: Eventos analíticos, páginas visitadas e satisfação dos usuários
# =============================================================================

def create_conversion_funnel_dashboard():
    """Cria o dashboard de Funil de Conversão e Comportamento.

    Voltado para equipes de produto e growth, este dashboard analisa os
    eventos registrados na tabela ANALYTIC_EVENTS e as pesquisas de
    satisfação da tabela FEEDBACK para entender o comportamento do usuário.

    Returns:
        int | None: ID do dashboard criado, ou None em caso de falha.
    """
    print("\n" + "=" * 60)
    print("CRIANDO: Funil de Conversão e Comportamento")
    print("=" * 60)

    dashboard_id = create_dashboard(
        name="Funil de Conversão e Comportamento",
        description="Análise de eventos analíticos, comportamento do usuário e satisfação",
    )
    if not dashboard_id:
        return None

    # --- KPIs de engajamento ---
    kpi_total_events = create_card(
        name="Total de Eventos",
        sql_query='SELECT COUNT(*) AS "Total de Eventos" FROM ANALYTIC_EVENTS',
        visualization_type="scalar",
        description="Total de eventos analíticos registrados na plataforma",
    )

    kpi_active_users = create_card(
        name="Usuários com Eventos",
        sql_query='SELECT COUNT(DISTINCT ACCOUNT_ID) AS "Usuários Ativos" FROM ANALYTIC_EVENTS',
        visualization_type="scalar",
        description="Usuários únicos que geraram pelo menos um evento",
    )

    kpi_event_types = create_card(
        name="Tipos de Eventos",
        sql_query='SELECT COUNT(DISTINCT EVENT) AS "Tipos de Eventos" FROM ANALYTIC_EVENTS',
        visualization_type="scalar",
        description="Número de tipos diferentes de eventos registrados",
    )

    kpi_average_satisfaction = create_card(
        name="Satisfação Geral",
        sql_query='SELECT ROUND(AVG(RATING), 2) AS "Satisfação Média" FROM FEEDBACK',
        visualization_type="scalar",
        description="Nota média de satisfação dos clientes nas pesquisas de feedback",
    )

    # --- Análise de eventos ---
    chart_events_by_type = create_card(
        name="Eventos por Tipo",
        sql_query="""
            SELECT
                EVENT        AS "Evento",
                COUNT(*)     AS "Ocorrências"
            FROM ANALYTIC_EVENTS
            GROUP BY EVENT
            ORDER BY "Ocorrências" DESC
        """,
        visualization_type="bar",
        description="Volume de ocorrências por tipo de evento (Page Viewed, Button Clicked, etc.)",
        viz_settings={
            "graph.dimensions": ["Evento"],
            "graph.metrics": ["Ocorrências"],
        },
    )

    chart_events_over_time = create_card(
        name="Eventos por Mês",
        sql_query="""
            SELECT
                FORMATDATETIME(TIMESTAMP, 'yyyy-MM') AS "Mês",
                COUNT(*)                              AS "Eventos"
            FROM ANALYTIC_EVENTS
            GROUP BY FORMATDATETIME(TIMESTAMP, 'yyyy-MM')
            ORDER BY "Mês"
        """,
        visualization_type="line",
        description="Evolução do volume de eventos ao longo do tempo",
        viz_settings={
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Eventos"],
        },
    )

    # Páginas mais visitadas: identifica os pontos de maior tráfego
    chart_top_pages = create_card(
        name="Páginas Mais Visitadas",
        sql_query="""
            SELECT
                PAGE_URL     AS "Página",
                COUNT(*)     AS "Visitas"
            FROM ANALYTIC_EVENTS
            WHERE EVENT = 'Page Viewed'
            GROUP BY PAGE_URL
            ORDER BY "Visitas" DESC
            LIMIT 10
        """,
        visualization_type="row",
        description="Top 10 páginas com maior número de visualizações",
        viz_settings={
            "graph.dimensions": ["Página"],
            "graph.metrics": ["Visitas"],
        },
    )

    # --- Análise de satisfação ---
    chart_rating_distribution = create_card(
        name="Distribuição de Avaliações",
        sql_query="""
            SELECT
                RATING_MAPPED   AS "Classificação",
                COUNT(*)        AS "Respostas"
            FROM FEEDBACK
            GROUP BY RATING_MAPPED
            ORDER BY MIN(RATING) DESC
        """,
        visualization_type="bar",
        description="Distribuição das respostas de satisfação por classificação",
        viz_settings={
            "graph.dimensions": ["Classificação"],
            "graph.metrics": ["Respostas"],
        },
    )

    chart_satisfaction_over_time = create_card(
        name="Satisfação Média por Mês",
        sql_query="""
            SELECT
                FORMATDATETIME(DATE_RECEIVED, 'yyyy-MM') AS "Mês",
                ROUND(AVG(RATING), 2)                     AS "Satisfação Média"
            FROM FEEDBACK
            GROUP BY FORMATDATETIME(DATE_RECEIVED, 'yyyy-MM')
            ORDER BY "Mês"
        """,
        visualization_type="line",
        description="Evolução da satisfação média dos clientes ao longo do tempo",
        viz_settings={
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Satisfação Média"],
        },
    )

    # --- Layout do dashboard ---
    cards_layout = []

    kpi_cards = [kpi_total_events, kpi_active_users, kpi_event_types, kpi_average_satisfaction]
    for index, card_id in enumerate(kpi_cards):
        if card_id:
            cards_layout.append({
                "card_id": card_id, "row": 0, "col": index * 6,
                "size_x": 6, "size_y": 3,
            })

    if chart_events_by_type:
        cards_layout.append({"card_id": chart_events_by_type,       "row": 3,  "col": 0,  "size_x": 12, "size_y": 5})
    if chart_events_over_time:
        cards_layout.append({"card_id": chart_events_over_time,     "row": 3,  "col": 12, "size_x": 12, "size_y": 5})
    if chart_top_pages:
        cards_layout.append({"card_id": chart_top_pages,            "row": 8,  "col": 0,  "size_x": 24, "size_y": 5})
    if chart_rating_distribution:
        cards_layout.append({"card_id": chart_rating_distribution,  "row": 13, "col": 0,  "size_x": 12, "size_y": 5})
    if chart_satisfaction_over_time:
        cards_layout.append({"card_id": chart_satisfaction_over_time, "row": 13, "col": 12, "size_x": 12, "size_y": 5})

    add_cards_to_dashboard(dashboard_id, cards_layout)
    return dashboard_id


# =============================================================================
# DASHBOARD 5: ANÁLISE FINANCEIRA E ASSINATURAS
# Foco: Receita de faturas, planos de assinatura e conversão de trial
# =============================================================================

def create_financial_dashboard():
    """Cria o dashboard de Análise Financeira e Assinaturas.

    Este dashboard é voltado para equipes financeiras e de growth, focando
    nas métricas de receita recorrente (MRR), distribuição de planos,
    conversão de trials e distribuição geográfica de contas.

    Returns:
        int | None: ID do dashboard criado, ou None em caso de falha.
    """
    print("\n" + "=" * 60)
    print("CRIANDO: Análise Financeira e Assinaturas")
    print("=" * 60)

    dashboard_id = create_dashboard(
        name="Análise Financeira e Assinaturas",
        description="Receita de assinaturas, planos, conversão de trial e distribuição geográfica",
    )
    if not dashboard_id:
        return None

    # --- KPIs financeiros ---
    kpi_invoice_revenue = create_card(
        name="Receita de Faturas",
        sql_query='SELECT ROUND(SUM(PAYMENT), 2) AS "Receita Total" FROM INVOICES',
        visualization_type="scalar",
        description="Receita total gerada por faturas de assinatura",
    )

    kpi_total_accounts = create_card(
        name="Total de Contas",
        sql_query='SELECT COUNT(*) AS "Total de Contas" FROM ACCOUNTS',
        visualization_type="scalar",
        description="Número total de contas cadastradas na plataforma",
    )

    kpi_active_subscriptions = create_card(
        name="Assinaturas Ativas",
        sql_query='SELECT COUNT(*) AS "Assinaturas Ativas" FROM ACCOUNTS WHERE ACTIVE_SUBSCRIPTION = TRUE',
        visualization_type="scalar",
        description="Número de assinaturas ativas no momento",
    )

    # Taxa de conversão de trial: percentual de trials que se tornaram pagantes
    # Métrica crítica para avaliar a eficácia do produto no período de teste
    kpi_trial_conversion_rate = create_card(
        name="Conversão de Trial (%)",
        sql_query="""
            SELECT
                ROUND(
                    SUM(CASE WHEN TRIAL_CONVERTED = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
                    1
                ) AS "Taxa de Conversão (%)"
            FROM ACCOUNTS
            WHERE TRIAL_ENDS_AT IS NOT NULL
        """,
        visualization_type="scalar",
        description="Percentual de trials que converteram para assinatura paga",
    )

    # --- Análise de planos ---
    chart_revenue_by_plan = create_card(
        name="Receita por Plano de Assinatura",
        sql_query="""
            SELECT
                PLAN         AS "Plano",
                SUM(PAYMENT) AS "Receita",
                COUNT(*)     AS "Faturas"
            FROM INVOICES
            GROUP BY PLAN
            ORDER BY "Receita" DESC
        """,
        visualization_type="bar",
        description="Receita total gerada por cada plano de assinatura",
        viz_settings={
            "graph.dimensions": ["Plano"],
            "graph.metrics": ["Receita"],
        },
    )

    chart_accounts_by_plan = create_card(
        name="Distribuição de Contas por Plano",
        sql_query="""
            SELECT
                PLAN        AS "Plano",
                COUNT(*)    AS "Contas"
            FROM ACCOUNTS
            GROUP BY PLAN
            ORDER BY "Contas" DESC
        """,
        visualization_type="pie",
        description="Distribuição percentual de contas por plano de assinatura",
        viz_settings={
            "graph.dimensions": ["Plano"],
            "graph.metrics": ["Contas"],
        },
    )

    # Gráfico combo: receita (barras) e número de faturas (linha) por mês
    # Permite identificar sazonalidade e crescimento da receita recorrente
    chart_monthly_invoice_revenue = create_card(
        name="Receita Mensal de Faturas",
        sql_query="""
            SELECT
                FORMATDATETIME(DATE_RECEIVED, 'yyyy-MM') AS "Mês",
                SUM(PAYMENT)                              AS "Receita",
                COUNT(*)                                  AS "Faturas"
            FROM INVOICES
            GROUP BY FORMATDATETIME(DATE_RECEIVED, 'yyyy-MM')
            ORDER BY "Mês"
        """,
        visualization_type="combo",
        description="Receita mensal de faturas com volume de cobranças",
        viz_settings={
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Receita", "Faturas"],
        },
    )

    chart_new_accounts_per_month = create_card(
        name="Novas Contas por Mês",
        sql_query="""
            SELECT
                FORMATDATETIME(CREATED_AT, 'yyyy-MM') AS "Mês",
                COUNT(*)                               AS "Novas Contas"
            FROM ACCOUNTS
            GROUP BY FORMATDATETIME(CREATED_AT, 'yyyy-MM')
            ORDER BY "Mês"
        """,
        visualization_type="area",
        description="Crescimento do número de contas cadastradas ao longo do tempo",
        viz_settings={
            "graph.dimensions": ["Mês"],
            "graph.metrics": ["Novas Contas"],
        },
    )

    chart_accounts_by_country = create_card(
        name="Contas por País (Top 10)",
        sql_query="""
            SELECT
                COUNTRY     AS "País",
                COUNT(*)    AS "Contas"
            FROM ACCOUNTS
            GROUP BY COUNTRY
            ORDER BY "Contas" DESC
            LIMIT 10
        """,
        visualization_type="row",
        description="Top 10 países por número de contas cadastradas",
        viz_settings={
            "graph.dimensions": ["País"],
            "graph.metrics": ["Contas"],
        },
    )

    # --- Layout do dashboard ---
    cards_layout = []

    kpi_cards = [kpi_invoice_revenue, kpi_total_accounts, kpi_active_subscriptions, kpi_trial_conversion_rate]
    for index, card_id in enumerate(kpi_cards):
        if card_id:
            cards_layout.append({
                "card_id": card_id, "row": 0, "col": index * 6,
                "size_x": 6, "size_y": 3,
            })

    if chart_revenue_by_plan:
        cards_layout.append({"card_id": chart_revenue_by_plan,          "row": 3,  "col": 0,  "size_x": 14, "size_y": 5})
    if chart_accounts_by_plan:
        cards_layout.append({"card_id": chart_accounts_by_plan,         "row": 3,  "col": 14, "size_x": 10, "size_y": 5})
    if chart_monthly_invoice_revenue:
        cards_layout.append({"card_id": chart_monthly_invoice_revenue,  "row": 8,  "col": 0,  "size_x": 12, "size_y": 5})
    if chart_new_accounts_per_month:
        cards_layout.append({"card_id": chart_new_accounts_per_month,   "row": 8,  "col": 12, "size_x": 12, "size_y": 5})
    if chart_accounts_by_country:
        cards_layout.append({"card_id": chart_accounts_by_country,      "row": 13, "col": 0,  "size_x": 24, "size_y": 5})

    add_cards_to_dashboard(dashboard_id, cards_layout)
    return dashboard_id


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def main():
    """Orquestra a criação de todos os dashboards de ecommerce.

    Executa as cinco funções de criação de dashboard em sequência e organiza
    os resultados em uma coleção dedicada no Metabase. Ao final, imprime um
    resumo com os IDs e URLs de acesso de cada dashboard.
    """
    print("=" * 60)
    print("ECOMMERCE ANALYTICS — CRIAÇÃO DE DASHBOARDS")
    print("Metabase:", METABASE_URL)
    print("=" * 60)

    # Cria os cinco dashboards temáticos
    dashboard_ids = {
        "vendas":     create_sales_overview_dashboard(),
        "produtos":   create_products_dashboard(),
        "clientes":   create_customers_dashboard(),
        "conversao":  create_conversion_funnel_dashboard(),
        "financeiro": create_financial_dashboard(),
    }

    # Organiza todos os dashboards em uma coleção dedicada
    collection_id = create_collection(
        name="Ecommerce Analytics",
        description="Dashboards de análise de ecommerce: vendas, produtos, clientes, conversão e financeiro",
    )

    if collection_id:
        print("\nOrganizando dashboards na coleção...")
        for dashboard_id in dashboard_ids.values():
            if dashboard_id:
                move_dashboard_to_collection(dashboard_id, collection_id)

    # Resumo final com links de acesso
    print("\n" + "=" * 60)
    print("CRIAÇÃO CONCLUÍDA — RESUMO")
    print("=" * 60)

    dashboard_labels = {
        "vendas":     "Visão Geral de Vendas",
        "produtos":   "Análise de Produtos",
        "clientes":   "Análise de Clientes",
        "conversao":  "Funil de Conversão e Comportamento",
        "financeiro": "Análise Financeira e Assinaturas",
    }

    for key, dashboard_id in dashboard_ids.items():
        status = f"✓ ID: {dashboard_id}" if dashboard_id else "✗ Falhou"
        label = dashboard_labels[key]
        print(f"  {label}: {status}")
        if dashboard_id:
            print(f"    → {METABASE_URL}/dashboard/{dashboard_id}")

    if collection_id:
        print(f"\nColeção: {METABASE_URL}/collection/{collection_id}")


if __name__ == "__main__":
    main()
