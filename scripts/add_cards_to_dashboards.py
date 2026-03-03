#!/usr/bin/env python3
"""
Configuração de cards nos dashboards de ecommerce existentes no Metabase.

Este script é um complemento ao `create_ecommerce_dashboards.py`. Ele foi
criado para resolver um problema específico: na primeira execução do script
principal, alguns cards KPI foram criados sem o campo `description`, o que
causou falhas silenciosas na API do Metabase. Este script recria esses cards
com a descrição obrigatória e os posiciona corretamente nos dashboards.

Contexto de uso:
    Execute este script apenas se os dashboards (IDs 36–40) já existirem no
    Metabase mas estiverem sem cards ou com cards faltando. Para uma instalação
    limpa, prefira executar `create_ecommerce_dashboards.py` diretamente.

Dashboards configurados:
    - ID 36: Visão Geral de Vendas
    - ID 37: Análise de Produtos
    - ID 38: Análise de Clientes
    - ID 39: Funil de Conversão e Comportamento
    - ID 40: Análise Financeira e Assinaturas

Uso:
    python add_cards_to_dashboards.py

Requisitos:
    - Python 3.8+
    - requests >= 2.28.0
    - Dashboards 36–40 já criados no Metabase
    - Cards de gráficos (IDs 63–92) já criados pelo script principal
"""

import os
import requests


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

METABASE_URL = os.getenv("METABASE_URL", "https://analytics.arconde.cloud")
API_KEY = os.getenv("METABASE_API_KEY", "mb_o8a+35jbsOddbO/l105odmnwGDh3b1KWyBomDTIc1IE=")

# ID do banco de dados no Metabase (1 = Sample Database H2 padrão)
DATABASE_ID = int(os.getenv("METABASE_DATABASE_ID", "1"))

REQUEST_HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
}


# =============================================================================
# FUNÇÕES DE API
# =============================================================================

def create_card(name, sql_query, visualization_type, description, viz_settings=None):
    """Cria um card (questão) no Metabase usando uma query SQL nativa.

    Args:
        name (str): Título do card exibido no dashboard.
        sql_query (str): Query SQL compatível com o dialeto H2 do Sample Database.
        visualization_type (str): Tipo de visualização. Valores aceitos:
            "scalar", "line", "bar", "row", "pie", "area", "combo", "table".
        description (str): Descrição obrigatória do card (exibida como tooltip).
        viz_settings (dict, optional): Configurações de visualização como eixos
            e dimensões. Padrão: None (dicionário vazio).

    Returns:
        int | None: ID do card criado, ou None em caso de falha na API.

    Examples:
        >>> card_id = create_card(
        ...     name="Receita Total",
        ...     sql_query='SELECT SUM(TOTAL) AS "Receita" FROM ORDERS',
        ...     visualization_type="scalar",
        ...     description="Soma de todos os pedidos realizados"
        ... )
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


def add_cards_to_dashboard(dashboard_id, cards_layout):
    """Adiciona múltiplos cards a um dashboard em uma única requisição PUT.

    A API do Metabase exige IDs temporários negativos para cada card no
    payload. Esses IDs são substituídos pelos IDs reais após a criação.

    Args:
        dashboard_id (int): ID do dashboard de destino.
        cards_layout (list[dict]): Lista de posicionamentos. Cada item deve ter:
            - card_id (int): ID do card a ser adicionado.
            - row (int): Linha inicial no grid (base 0).
            - col (int): Coluna inicial no grid (base 0, máx 24 colunas).
            - size_x (int): Largura em colunas (1–24).
            - size_y (int): Altura em linhas (mínimo 2).

    Returns:
        bool: True se os cards foram adicionados com sucesso, False caso contrário.

    Examples:
        >>> success = add_cards_to_dashboard(
        ...     dashboard_id=36,
        ...     cards_layout=[
        ...         {"card_id": 101, "row": 0, "col": 0,  "size_x": 6, "size_y": 3},
        ...         {"card_id": 102, "row": 0, "col": 6,  "size_x": 6, "size_y": 3},
        ...     ]
        ... )
    """
    # Cada card recebe um ID temporário negativo único, exigido pelo Metabase
    cards_payload = [
        {
            "id": -(position + 1),
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

    print(f"  ✗ Falha: {response.status_code} — {response.text[:300]}")
    return False


# =============================================================================
# DASHBOARD 36: VISÃO GERAL DE VENDAS
# Cards de gráficos pré-existentes: IDs 63–69 (criados pelo script principal)
# =============================================================================

def setup_sales_overview_dashboard():
    """Recria os KPIs e configura o layout do dashboard Visão Geral de Vendas.

    Os cards de gráficos (receita mensal, pedidos por mês, etc.) já foram
    criados pelo script principal com IDs 63–69. Esta função recria apenas
    os KPIs escalares que falharam por falta de descrição.
    """
    print("\n=== Configurando: Visão Geral de Vendas (Dashboard ID: 36) ===")

    # Recria os KPIs que falharam na primeira execução
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

    cards_layout = []

    # Linha 0: 5 KPIs de largura 4 cada (total = 20 colunas do grid de 24)
    kpi_cards = [kpi_total_revenue, kpi_total_orders, kpi_average_ticket, kpi_unique_customers, kpi_total_discounts]
    kpi_column_positions = [0, 5, 10, 15, 20]

    for card_id, col_position in zip(kpi_cards, kpi_column_positions):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": col_position, "size_x": 4, "size_y": 3})

    # Linha 3: Receita Mensal (gráfico de linha) + Pedidos por Mês (barras)
    cards_layout.append({"card_id": 63, "row": 3, "col": 0,  "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 64, "row": 3, "col": 12, "size_x": 12, "size_y": 5})

    # Linha 8: Receita por Canal de Aquisição + Top 10 Estados
    cards_layout.append({"card_id": 65, "row": 8, "col": 0,  "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 66, "row": 8, "col": 12, "size_x": 12, "size_y": 5})

    # Linha 13: Receita vs Desconto (combo) + Distribuição por Faixa de Valor (pizza)
    cards_layout.append({"card_id": 68, "row": 13, "col": 0,  "size_x": 14, "size_y": 5})
    cards_layout.append({"card_id": 69, "row": 13, "col": 14, "size_x": 10, "size_y": 5})

    add_cards_to_dashboard(36, cards_layout)


# =============================================================================
# DASHBOARD 37: ANÁLISE DE PRODUTOS
# Cards de gráficos pré-existentes: IDs 70–76
# =============================================================================

def setup_products_dashboard():
    """Recria os KPIs e configura o layout do dashboard Análise de Produtos."""
    print("\n=== Configurando: Análise de Produtos (Dashboard ID: 37) ===")

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

    cards_layout = []

    # Linha 0: 4 KPIs de largura 6 cada (total = 24 colunas)
    kpi_cards = [kpi_total_products, kpi_total_categories, kpi_average_rating, kpi_average_price]
    for index, card_id in enumerate(kpi_cards):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": index * 6, "size_x": 6, "size_y": 3})

    # Linha 3: Receita por Categoria (barras) + Participação por Categoria (pizza)
    cards_layout.append({"card_id": 70, "row": 3,  "col": 0,  "size_x": 14, "size_y": 5})
    cards_layout.append({"card_id": 71, "row": 3,  "col": 14, "size_x": 10, "size_y": 5})

    # Linha 8: Top 10 Produtos Mais Vendidos + Avaliação por Categoria
    cards_layout.append({"card_id": 72, "row": 8,  "col": 0,  "size_x": 12, "size_y": 6})
    cards_layout.append({"card_id": 73, "row": 8,  "col": 12, "size_x": 12, "size_y": 6})

    # Linha 14: Preço Médio por Categoria + Receita por Fornecedor
    cards_layout.append({"card_id": 74, "row": 14, "col": 0,  "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 76, "row": 14, "col": 12, "size_x": 12, "size_y": 5})

    # Linha 19: Produtos Melhor Avaliados (tabela completa)
    cards_layout.append({"card_id": 75, "row": 19, "col": 0,  "size_x": 24, "size_y": 5})

    add_cards_to_dashboard(37, cards_layout)


# =============================================================================
# DASHBOARD 38: ANÁLISE DE CLIENTES
# Cards de gráficos pré-existentes: IDs 77–82
# =============================================================================

def setup_customers_dashboard():
    """Recria os KPIs e configura o layout do dashboard Análise de Clientes."""
    print("\n=== Configurando: Análise de Clientes (Dashboard ID: 38) ===")

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
        description="Média de pedidos por cliente — indicador de recorrência de compra",
    )

    kpi_average_ltv = create_card(
        name="LTV Médio",
        sql_query="""
            SELECT ROUND(SUM(TOTAL) / COUNT(DISTINCT USER_ID), 2) AS "LTV Médio"
            FROM ORDERS
        """,
        visualization_type="scalar",
        description="Lifetime Value médio por cliente — receita total gerada por cliente",
    )

    cards_layout = []

    # Linha 0: 4 KPIs de largura 6 cada
    kpi_cards = [kpi_total_customers, kpi_customers_with_orders, kpi_orders_per_customer, kpi_average_ltv]
    for index, card_id in enumerate(kpi_cards):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": index * 6, "size_x": 6, "size_y": 3})

    # Linha 3: Novos Clientes por Mês (área) + Clientes por Canal (pizza)
    cards_layout.append({"card_id": 77, "row": 3,  "col": 0,  "size_x": 14, "size_y": 5})
    cards_layout.append({"card_id": 78, "row": 3,  "col": 14, "size_x": 10, "size_y": 5})

    # Linha 8: Top 10 Estados + Segmentação por Frequência (RFM)
    cards_layout.append({"card_id": 79, "row": 8,  "col": 0,  "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 80, "row": 8,  "col": 12, "size_x": 12, "size_y": 5})

    # Linha 13: Receita por Faixa Etária (análise demográfica)
    cards_layout.append({"card_id": 82, "row": 13, "col": 0,  "size_x": 24, "size_y": 5})

    # Linha 18: Top 10 Clientes por Receita (tabela)
    cards_layout.append({"card_id": 81, "row": 18, "col": 0,  "size_x": 24, "size_y": 5})

    add_cards_to_dashboard(38, cards_layout)


# =============================================================================
# DASHBOARD 39: FUNIL DE CONVERSÃO E COMPORTAMENTO
# Cards de gráficos pré-existentes: IDs 83–87
# =============================================================================

def setup_conversion_funnel_dashboard():
    """Recria os KPIs e configura o layout do dashboard Funil de Conversão."""
    print("\n=== Configurando: Funil de Conversão (Dashboard ID: 39) ===")

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
        description="Usuários únicos que geraram pelo menos um evento registrado",
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

    cards_layout = []

    # Linha 0: 4 KPIs de largura 6 cada
    kpi_cards = [kpi_total_events, kpi_active_users, kpi_event_types, kpi_average_satisfaction]
    for index, card_id in enumerate(kpi_cards):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": index * 6, "size_x": 6, "size_y": 3})

    # Linha 3: Eventos por Tipo (barras) + Eventos por Mês (linha)
    cards_layout.append({"card_id": 83, "row": 3,  "col": 0,  "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 84, "row": 3,  "col": 12, "size_x": 12, "size_y": 5})

    # Linha 8: Páginas Mais Visitadas (largura total)
    cards_layout.append({"card_id": 85, "row": 8,  "col": 0,  "size_x": 24, "size_y": 5})

    # Linha 13: Distribuição de Avaliações + Satisfação por Mês
    cards_layout.append({"card_id": 86, "row": 13, "col": 0,  "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 87, "row": 13, "col": 12, "size_x": 12, "size_y": 5})

    add_cards_to_dashboard(39, cards_layout)


# =============================================================================
# DASHBOARD 40: ANÁLISE FINANCEIRA E ASSINATURAS
# Cards de gráficos pré-existentes: IDs 88–92
# =============================================================================

def setup_financial_dashboard():
    """Recria os KPIs e configura o layout do dashboard Análise Financeira."""
    print("\n=== Configurando: Análise Financeira (Dashboard ID: 40) ===")

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

    # Taxa de conversão de trial: métrica crítica para avaliar o produto
    # no período de teste gratuito antes da cobrança
    kpi_trial_conversion = create_card(
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

    cards_layout = []

    # Linha 0: 4 KPIs de largura 6 cada
    kpi_cards = [kpi_invoice_revenue, kpi_total_accounts, kpi_active_subscriptions, kpi_trial_conversion]
    for index, card_id in enumerate(kpi_cards):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": index * 6, "size_x": 6, "size_y": 3})

    # Linha 3: Receita por Plano (barras) + Distribuição por Plano (pizza)
    cards_layout.append({"card_id": 88, "row": 3,  "col": 0,  "size_x": 14, "size_y": 5})
    cards_layout.append({"card_id": 89, "row": 3,  "col": 14, "size_x": 10, "size_y": 5})

    # Linha 8: Receita Mensal de Faturas (combo) + Novas Contas por Mês (área)
    cards_layout.append({"card_id": 90, "row": 8,  "col": 0,  "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 91, "row": 8,  "col": 12, "size_x": 12, "size_y": 5})

    # Linha 13: Contas por País — Top 10 (largura total)
    cards_layout.append({"card_id": 92, "row": 13, "col": 0,  "size_x": 24, "size_y": 5})

    add_cards_to_dashboard(40, cards_layout)


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def main():
    """Executa a configuração de todos os cinco dashboards em sequência."""
    print("=" * 60)
    print("ECOMMERCE ANALYTICS — CONFIGURAÇÃO DE DASHBOARDS")
    print("Metabase:", METABASE_URL)
    print("=" * 60)

    setup_sales_overview_dashboard()
    setup_products_dashboard()
    setup_customers_dashboard()
    setup_conversion_funnel_dashboard()
    setup_financial_dashboard()

    print("\n" + "=" * 60)
    print("CONFIGURAÇÃO CONCLUÍDA")
    print("=" * 60)
    print("\nAcesse os dashboards em:")

    dashboard_map = {
        36: "Visão Geral de Vendas",
        37: "Análise de Produtos",
        38: "Análise de Clientes",
        39: "Funil de Conversão e Comportamento",
        40: "Análise Financeira e Assinaturas",
    }

    for dashboard_id, dashboard_name in dashboard_map.items():
        print(f"  {METABASE_URL}/dashboard/{dashboard_id} — {dashboard_name}")


if __name__ == "__main__":
    main()
