# Ecommerce Analytics — Metabase Dashboards

> **5 dashboards profissionais de ecommerce criados automaticamente via API do Metabase**, cobrindo vendas, produtos, clientes, conversão e análise financeira.

![Metabase](https://img.shields.io/badge/Metabase-v0.58-509EE3?style=flat-square&logo=metabase&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Self--hosted-336791?style=flat-square&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Visão Geral

Este projeto automatiza a criação de dashboards analíticos para ecommerce no Metabase utilizando a API REST. Em vez de criar cada gráfico manualmente pela interface, todos os **50+ cards** distribuídos em **5 dashboards temáticos** são gerados programaticamente via Python.

### Dashboards Criados

| Dashboard | Descrição | Cards |
|-----------|-----------|-------|
| **Visão Geral de Vendas** | KPIs executivos: receita, pedidos, ticket médio, canais de aquisição | 11 |
| **Análise de Produtos** | Categorias, top produtos, avaliações, preços e fornecedores | 11 |
| **Análise de Clientes** | Aquisição, LTV, segmentação RFM, faixa etária e top clientes | 10 |
| **Funil de Conversão e Comportamento** | Eventos analíticos, páginas visitadas, satisfação | 9 |
| **Análise Financeira e Assinaturas** | Receita de faturas, planos, conversão de trial, distribuição geográfica | 9 |

---

## Métricas em Destaque

Os dashboards revelam insights como:

- **Receita Total**: R$ 1,5M em 18.760 pedidos
- **Ticket Médio**: R$ 80,52 por pedido
- **LTV Médio**: R$ 865 por cliente
- **44,5% dos clientes são VIPs** (mais de 10 pedidos)
- **Taxa de Conversão de Trial**: 42,5%
- **Receita de Assinaturas**: R$ 6,7M

---

## Estrutura do Projeto

```
ecommerce-analytics/
├── scripts/
│   ├── create_ecommerce_dashboards.py   # Cria dashboards e cards via API
│   └── add_cards_to_dashboards.py       # Adiciona cards aos dashboards (PUT)
├── docs/
│   └── schema.md                        # Documentação do schema de dados
├── assets/
│   └── (screenshots dos dashboards)
└── README.md
```

---

## Como Usar

### Pré-requisitos

- Python 3.8+
- Instância do Metabase (self-hosted ou cloud)
- API Key do Metabase (Admin → Settings → API Keys)

### Configuração

```bash
# Clone o repositório
git clone https://github.com/alex-des-santos/ecommerce-analytics.git
cd ecommerce-analytics

# Configure as variáveis de ambiente
export METABASE_URL="https://sua-instancia.metabase.com"
export METABASE_API_KEY="mb_sua_chave_aqui"
export DATABASE_ID=1  # ID do banco de dados no Metabase
```

### Execução

```bash
# Passo 1: Criar os dashboards e cards
python scripts/create_ecommerce_dashboards.py

# Passo 2: Adicionar cards aos dashboards
python scripts/add_cards_to_dashboards.py
```

---

## Schema de Dados

O projeto utiliza o **Sample Database** do Metabase (H2), que simula dados reais de ecommerce:

| Tabela | Descrição | Campos Principais |
|--------|-----------|-------------------|
| `ORDERS` | Pedidos realizados | id, user_id, product_id, total, discount, created_at |
| `PEOPLE` | Clientes cadastrados | id, name, email, state, source, birth_date |
| `PRODUCTS` | Catálogo de produtos | id, title, category, vendor, price, rating |
| `REVIEWS` | Avaliações de produtos | id, product_id, rating, body, created_at |
| `ACCOUNTS` | Contas de assinatura | id, plan, seats, active_subscription, trial_converted |
| `INVOICES` | Faturas de assinatura | id, account_id, payment, plan, date_received |
| `FEEDBACK` | Pesquisas de satisfação | id, rating, rating_mapped, date_received |
| `ANALYTIC_EVENTS` | Eventos de comportamento | id, account_id, event, page_url, timestamp |

---

## Detalhes Técnicos

### Endpoints da API Utilizados

| Método | Endpoint | Uso |
|--------|----------|-----|
| `GET` | `/api/database/{id}/metadata` | Explorar schema do banco |
| `POST` | `/api/card` | Criar cards/questões |
| `POST` | `/api/dashboard` | Criar dashboards |
| `PUT` | `/api/dashboard/{id}/cards` | Adicionar cards ao dashboard |
| `PUT` | `/api/card/{id}` | Atualizar configurações de card |
| `POST` | `/api/collection` | Criar coleções |
| `PUT` | `/api/dashboard/{id}` | Mover dashboard para coleção |

### Tipos de Visualização Usados

`scalar` · `line` · `bar` · `row` · `pie` · `area` · `combo` · `table`

---

## Referências

- [Metabase API Documentation](https://www.metabase.com/docs/latest/api-documentation)
- [Metabase Self-Hosting Guide](https://www.metabase.com/docs/latest/installation-and-operation/installing-metabase)
- [SQL Reference for H2 Database](http://www.h2database.com/html/grammar.html)

---

## Licença

MIT License — sinta-se livre para usar, modificar e distribuir.

---

*Criado com 🤖 automação via API + 📊 Metabase*
