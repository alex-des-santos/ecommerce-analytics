#!/usr/bin/env python3
"""
Script para adicionar cards aos dashboards de ecommerce no Metabase.
Usa o endpoint PUT /api/dashboard/{id}/cards com o formato correto.
"""

import requests
import json

METABASE_URL = "https://analytics.arconde.cloud"
API_KEY = "mb_o8a+35jbsOddbO/l105odmnwGDh3b1KWyBomDTIc1IE="

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}


def add_cards_to_dashboard(dashboard_id, cards_layout):
    """
    Adiciona múltiplos cards a um dashboard de uma vez.
    cards_layout: lista de dicts com {card_id, row, col, size_x, size_y}
    """
    cards_payload = []
    for i, card in enumerate(cards_layout):
        cards_payload.append({
            "id": -(i + 1),  # ID temporário negativo
            "card_id": card['card_id'],
            "row": card['row'],
            "col": card['col'],
            "size_x": card['size_x'],
            "size_y": card['size_y'],
            "series": [],
            "parameter_mappings": [],
            "visualization_settings": {}
        })
    
    response = requests.put(
        f"{METABASE_URL}/api/dashboard/{dashboard_id}/cards",
        headers=HEADERS,
        json={"cards": cards_payload}
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        added = len(result.get('cards', []))
        print(f"  ✓ {added} cards adicionados ao dashboard {dashboard_id}")
        return True
    else:
        print(f"  ✗ Erro: {response.status_code} - {response.text[:300]}")
        return False


def create_card_with_description(name, query, visualization_type, description, viz_settings=None):
    """Cria um card com descrição obrigatória."""
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
            "database": 1
        },
        "visualization_settings": viz_settings or {}
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


# ============================================================
# DASHBOARD 36: VISÃO GERAL DE VENDAS
# IDs dos cards: 59-69 (da primeira execução)
# ============================================================

def setup_dashboard_vendas():
    print("\n=== Configurando Dashboard: Visão Geral de Vendas (ID: 36) ===")
    
    # Criar KPI cards que falharam (sem descrição)
    kpi_receita = create_card_with_description(
        "💰 Receita Total",
        'SELECT SUM(TOTAL) AS "Receita Total" FROM ORDERS',
        "scalar",
        "Soma de todos os valores de pedidos realizados"
    )
    
    kpi_pedidos = create_card_with_description(
        "📦 Total de Pedidos",
        'SELECT COUNT(*) AS "Total de Pedidos" FROM ORDERS',
        "scalar",
        "Número total de pedidos realizados no período"
    )
    
    kpi_ticket = create_card_with_description(
        "🎯 Ticket Médio",
        'SELECT ROUND(AVG(TOTAL), 2) AS "Ticket Médio" FROM ORDERS',
        "scalar",
        "Valor médio por pedido"
    )
    
    kpi_clientes = create_card_with_description(
        "👥 Clientes Únicos",
        'SELECT COUNT(DISTINCT USER_ID) AS "Clientes Únicos" FROM ORDERS',
        "scalar",
        "Número de clientes únicos que realizaram pedidos"
    )
    
    kpi_desconto = create_card_with_description(
        "🏷️ Desconto Total",
        'SELECT ROUND(SUM(DISCOUNT), 2) AS "Desconto Total" FROM ORDERS WHERE DISCOUNT > 0',
        "scalar",
        "Soma total de descontos aplicados"
    )
    
    cards_layout = []
    
    # Linha 1: KPIs (5 cards de 4-5 colunas cada)
    kpi_ids = [kpi_receita, kpi_pedidos, kpi_ticket, kpi_clientes, kpi_desconto]
    col_positions = [0, 5, 10, 15, 20]
    for i, card_id in enumerate(kpi_ids):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": col_positions[i], "size_x": 4, "size_y": 3})
    
    # Linha 2: Receita Mensal (linha) + Pedidos por Mês (barra)
    cards_layout.append({"card_id": 63, "row": 3, "col": 0, "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 64, "row": 3, "col": 12, "size_x": 12, "size_y": 5})
    
    # Linha 3: Receita por Canal + Top 10 Estados
    cards_layout.append({"card_id": 65, "row": 8, "col": 0, "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 66, "row": 8, "col": 12, "size_x": 12, "size_y": 5})
    
    # Linha 4: Receita vs Desconto + Distribuição por Faixa
    cards_layout.append({"card_id": 68, "row": 13, "col": 0, "size_x": 14, "size_y": 5})
    cards_layout.append({"card_id": 69, "row": 13, "col": 14, "size_x": 10, "size_y": 5})
    
    add_cards_to_dashboard(36, cards_layout)


# ============================================================
# DASHBOARD 37: ANÁLISE DE PRODUTOS
# IDs dos cards: 70-76
# ============================================================

def setup_dashboard_produtos():
    print("\n=== Configurando Dashboard: Análise de Produtos (ID: 37) ===")
    
    # Criar KPI cards
    kpi_total_prod = create_card_with_description(
        "📦 Total de Produtos",
        'SELECT COUNT(*) AS "Total de Produtos" FROM PRODUCTS',
        "scalar",
        "Total de produtos no catálogo"
    )
    
    kpi_categorias = create_card_with_description(
        "🏷️ Categorias",
        'SELECT COUNT(DISTINCT CATEGORY) AS "Categorias" FROM PRODUCTS',
        "scalar",
        "Número de categorias de produtos disponíveis"
    )
    
    kpi_avaliacao = create_card_with_description(
        "⭐ Avaliação Média",
        'SELECT ROUND(AVG(RATING), 2) AS "Avaliação Média" FROM PRODUCTS',
        "scalar",
        "Avaliação média de todos os produtos"
    )
    
    kpi_preco = create_card_with_description(
        "💵 Preço Médio",
        'SELECT ROUND(AVG(PRICE), 2) AS "Preço Médio" FROM PRODUCTS',
        "scalar",
        "Preço médio dos produtos no catálogo"
    )
    
    cards_layout = []
    
    # Linha 1: KPIs
    for i, card_id in enumerate([kpi_total_prod, kpi_categorias, kpi_avaliacao, kpi_preco]):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": i*6, "size_x": 6, "size_y": 3})
    
    # Linha 2: Receita por Categoria + Participação
    cards_layout.append({"card_id": 70, "row": 3, "col": 0, "size_x": 14, "size_y": 5})
    cards_layout.append({"card_id": 71, "row": 3, "col": 14, "size_x": 10, "size_y": 5})
    
    # Linha 3: Top Produtos + Avaliação por Categoria
    cards_layout.append({"card_id": 72, "row": 8, "col": 0, "size_x": 12, "size_y": 6})
    cards_layout.append({"card_id": 73, "row": 8, "col": 12, "size_x": 12, "size_y": 6})
    
    # Linha 4: Preço por Categoria + Vendas por Fornecedor
    cards_layout.append({"card_id": 74, "row": 14, "col": 0, "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 76, "row": 14, "col": 12, "size_x": 12, "size_y": 5})
    
    # Linha 5: Melhores Avaliados
    cards_layout.append({"card_id": 75, "row": 19, "col": 0, "size_x": 24, "size_y": 5})
    
    add_cards_to_dashboard(37, cards_layout)


# ============================================================
# DASHBOARD 38: ANÁLISE DE CLIENTES
# IDs dos cards: 77-82
# ============================================================

def setup_dashboard_clientes():
    print("\n=== Configurando Dashboard: Análise de Clientes (ID: 38) ===")
    
    # Criar KPI cards
    kpi_total = create_card_with_description(
        "👥 Total de Clientes",
        'SELECT COUNT(*) AS "Total de Clientes" FROM PEOPLE',
        "scalar",
        "Total de clientes cadastrados na plataforma"
    )
    
    kpi_ativos = create_card_with_description(
        "🛒 Clientes com Pedidos",
        'SELECT COUNT(DISTINCT USER_ID) AS "Clientes com Pedidos" FROM ORDERS',
        "scalar",
        "Clientes que realizaram pelo menos um pedido"
    )
    
    kpi_freq = create_card_with_description(
        "📊 Pedidos por Cliente",
        """SELECT ROUND(CAST(COUNT(*) AS FLOAT) / COUNT(DISTINCT USER_ID), 2) AS "Pedidos por Cliente" FROM ORDERS""",
        "scalar",
        "Média de pedidos por cliente"
    )
    
    kpi_ltv = create_card_with_description(
        "💰 LTV Médio",
        """SELECT ROUND(SUM(TOTAL) / COUNT(DISTINCT USER_ID), 2) AS "LTV Médio" FROM ORDERS""",
        "scalar",
        "Lifetime Value médio por cliente"
    )
    
    cards_layout = []
    
    # Linha 1: KPIs
    for i, card_id in enumerate([kpi_total, kpi_ativos, kpi_freq, kpi_ltv]):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": i*6, "size_x": 6, "size_y": 3})
    
    # Linha 2: Novos Clientes por Mês + Canal de Aquisição
    cards_layout.append({"card_id": 77, "row": 3, "col": 0, "size_x": 14, "size_y": 5})
    cards_layout.append({"card_id": 78, "row": 3, "col": 14, "size_x": 10, "size_y": 5})
    
    # Linha 3: Top Estados + Segmentação por Frequência
    cards_layout.append({"card_id": 79, "row": 8, "col": 0, "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 80, "row": 8, "col": 12, "size_x": 12, "size_y": 5})
    
    # Linha 4: Receita por Faixa Etária
    cards_layout.append({"card_id": 82, "row": 13, "col": 0, "size_x": 24, "size_y": 5})
    
    # Linha 5: Top Clientes
    cards_layout.append({"card_id": 81, "row": 18, "col": 0, "size_x": 24, "size_y": 5})
    
    add_cards_to_dashboard(38, cards_layout)


# ============================================================
# DASHBOARD 39: FUNIL DE CONVERSÃO E COMPORTAMENTO
# IDs dos cards: 83-87
# ============================================================

def setup_dashboard_conversao():
    print("\n=== Configurando Dashboard: Funil de Conversão (ID: 39) ===")
    
    # Criar KPI cards
    kpi_eventos = create_card_with_description(
        "📊 Total de Eventos",
        'SELECT COUNT(*) AS "Total de Eventos" FROM ANALYTIC_EVENTS',
        "scalar",
        "Total de eventos analíticos registrados"
    )
    
    kpi_usuarios = create_card_with_description(
        "👤 Usuários com Eventos",
        'SELECT COUNT(DISTINCT ACCOUNT_ID) AS "Usuários Ativos" FROM ANALYTIC_EVENTS',
        "scalar",
        "Usuários únicos com eventos registrados"
    )
    
    kpi_tipos = create_card_with_description(
        "🔢 Tipos de Eventos",
        'SELECT COUNT(DISTINCT EVENT) AS "Tipos de Eventos" FROM ANALYTIC_EVENTS',
        "scalar",
        "Número de tipos diferentes de eventos"
    )
    
    kpi_satisfacao = create_card_with_description(
        "😊 Satisfação Geral",
        'SELECT ROUND(AVG(RATING), 2) AS "Satisfação Média" FROM FEEDBACK',
        "scalar",
        "Nota média de satisfação dos clientes"
    )
    
    cards_layout = []
    
    # Linha 1: KPIs
    for i, card_id in enumerate([kpi_eventos, kpi_usuarios, kpi_tipos, kpi_satisfacao]):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": i*6, "size_x": 6, "size_y": 3})
    
    # Linha 2: Eventos por Tipo + Eventos por Mês
    cards_layout.append({"card_id": 83, "row": 3, "col": 0, "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 84, "row": 3, "col": 12, "size_x": 12, "size_y": 5})
    
    # Linha 3: Páginas Mais Visitadas
    cards_layout.append({"card_id": 85, "row": 8, "col": 0, "size_x": 24, "size_y": 5})
    
    # Linha 4: Distribuição de Avaliações + Satisfação por Mês
    cards_layout.append({"card_id": 86, "row": 13, "col": 0, "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 87, "row": 13, "col": 12, "size_x": 12, "size_y": 5})
    
    add_cards_to_dashboard(39, cards_layout)


# ============================================================
# DASHBOARD 40: ANÁLISE FINANCEIRA E ASSINATURAS
# IDs dos cards: 88-92
# ============================================================

def setup_dashboard_financeiro():
    print("\n=== Configurando Dashboard: Análise Financeira (ID: 40) ===")
    
    # Criar KPI cards
    kpi_receita_fat = create_card_with_description(
        "💰 Receita de Faturas",
        'SELECT ROUND(SUM(PAYMENT), 2) AS "Receita Total" FROM INVOICES',
        "scalar",
        "Receita total gerada por faturas de assinatura"
    )
    
    kpi_contas = create_card_with_description(
        "🏢 Total de Contas",
        'SELECT COUNT(*) AS "Total de Contas" FROM ACCOUNTS',
        "scalar",
        "Número total de contas cadastradas"
    )
    
    kpi_ativas = create_card_with_description(
        "✅ Assinaturas Ativas",
        'SELECT COUNT(*) AS "Assinaturas Ativas" FROM ACCOUNTS WHERE ACTIVE_SUBSCRIPTION = TRUE',
        "scalar",
        "Número de assinaturas ativas no momento"
    )
    
    kpi_trial = create_card_with_description(
        "🔄 Conversão de Trial",
        """SELECT 
    ROUND(
        SUM(CASE WHEN TRIAL_CONVERTED = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        1
    ) AS "Taxa de Conversão (%)"
FROM ACCOUNTS
WHERE TRIAL_ENDS_AT IS NOT NULL""",
        "scalar",
        "Percentual de trials que converteram para assinatura paga"
    )
    
    cards_layout = []
    
    # Linha 1: KPIs
    for i, card_id in enumerate([kpi_receita_fat, kpi_contas, kpi_ativas, kpi_trial]):
        if card_id:
            cards_layout.append({"card_id": card_id, "row": 0, "col": i*6, "size_x": 6, "size_y": 3})
    
    # Linha 2: Receita por Plano + Distribuição por Plano
    cards_layout.append({"card_id": 88, "row": 3, "col": 0, "size_x": 14, "size_y": 5})
    cards_layout.append({"card_id": 89, "row": 3, "col": 14, "size_x": 10, "size_y": 5})
    
    # Linha 3: Receita Mensal + Novas Contas
    cards_layout.append({"card_id": 90, "row": 8, "col": 0, "size_x": 12, "size_y": 5})
    cards_layout.append({"card_id": 91, "row": 8, "col": 12, "size_x": 12, "size_y": 5})
    
    # Linha 4: Contas por País
    cards_layout.append({"card_id": 92, "row": 13, "col": 0, "size_x": 24, "size_y": 5})
    
    add_cards_to_dashboard(40, cards_layout)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CONFIGURANDO DASHBOARDS DE ECOMMERCE - METABASE")
    print("=" * 60)
    
    setup_dashboard_vendas()
    setup_dashboard_produtos()
    setup_dashboard_clientes()
    setup_dashboard_conversao()
    setup_dashboard_financeiro()
    
    print("\n" + "=" * 60)
    print("CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print("\nAcesse os dashboards em:")
    print(f"  {METABASE_URL}/dashboard/36 - Visão Geral de Vendas")
    print(f"  {METABASE_URL}/dashboard/37 - Análise de Produtos")
    print(f"  {METABASE_URL}/dashboard/38 - Análise de Clientes")
    print(f"  {METABASE_URL}/dashboard/39 - Funil de Conversão")
    print(f"  {METABASE_URL}/dashboard/40 - Análise Financeira")
