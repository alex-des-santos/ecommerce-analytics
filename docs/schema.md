# Schema de Dados — Ecommerce Analytics

## Banco de Dados: Sample Database (H2)

O Sample Database do Metabase simula um ambiente real de ecommerce com 8 tabelas interconectadas.

## Diagrama de Relacionamentos

```
PEOPLE (1) ──────────── (N) ORDERS (N) ──────────── (1) PRODUCTS
                              │                              │
                              │                         (N) REVIEWS
                              │
ACCOUNTS (1) ──────── (N) INVOICES
         │
         └──────────── (N) ANALYTIC_EVENTS
         │
         └──────────── (N) FEEDBACK
```

## Tabelas

### ORDERS — Pedidos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID | BigInteger (PK) | Identificador único do pedido |
| USER_ID | Integer (FK → PEOPLE) | Cliente que realizou o pedido |
| PRODUCT_ID | Integer (FK → PRODUCTS) | Produto comprado |
| SUBTOTAL | Float | Valor antes do desconto |
| TAX | Float | Imposto aplicado |
| TOTAL | Float | Valor final pago |
| DISCOUNT | Float | Desconto concedido |
| QUANTITY | Integer | Quantidade de itens |
| CREATED_AT | DateTime | Data e hora do pedido |

### PEOPLE — Clientes

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID | BigInteger (PK) | Identificador único do cliente |
| NAME | Text | Nome completo |
| EMAIL | Text | E-mail |
| ADDRESS | Text | Endereço |
| CITY | Text | Cidade |
| STATE | Text | Estado (sigla) |
| ZIP | Text | CEP |
| LATITUDE | Float | Latitude geográfica |
| LONGITUDE | Float | Longitude geográfica |
| SOURCE | Text | Canal de aquisição (Facebook, Google, Organic, Twitter, Affiliate) |
| BIRTH_DATE | Date | Data de nascimento |
| CREATED_AT | DateTime | Data de cadastro |

### PRODUCTS — Produtos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID | BigInteger (PK) | Identificador único do produto |
| EAN | Text | Código de barras EAN |
| TITLE | Text | Nome do produto |
| CATEGORY | Text | Categoria (Widget, Gadget, Gizmo, Doohickey) |
| VENDOR | Text | Fornecedor/fabricante |
| PRICE | Float | Preço de venda |
| RATING | Float | Avaliação média (0-5) |
| CREATED_AT | DateTime | Data de cadastro no catálogo |

### REVIEWS — Avaliações

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID | BigInteger (PK) | Identificador único da avaliação |
| PRODUCT_ID | Integer (FK → PRODUCTS) | Produto avaliado |
| REVIEWER | Text | Nome do avaliador |
| RATING | Integer | Nota (1-5) |
| BODY | Text | Texto da avaliação |
| CREATED_AT | DateTime | Data da avaliação |

### ACCOUNTS — Contas de Assinatura

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID | BigInteger (PK) | Identificador único da conta |
| EMAIL | Text | E-mail da conta |
| FIRST_NAME | Text | Primeiro nome |
| LAST_NAME | Text | Sobrenome |
| PLAN | Text | Plano (Basic, Business, Premium) |
| SOURCE | Text | Canal de aquisição |
| SEATS | Integer | Número de assentos contratados |
| ACTIVE_SUBSCRIPTION | Boolean | Se a assinatura está ativa |
| TRIAL_CONVERTED | Boolean | Se converteu de trial para pago |
| TRIAL_ENDS_AT | DateTime | Data de encerramento do trial |
| CANCELED_AT | DateTime | Data de cancelamento (se aplicável) |
| COUNTRY | Text | País |
| LATITUDE | Float | Latitude |
| LONGITUDE | Float | Longitude |
| CREATED_AT | DateTime | Data de criação da conta |

### INVOICES — Faturas

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID | BigInteger (PK) | Identificador único da fatura |
| ACCOUNT_ID | BigInteger (FK → ACCOUNTS) | Conta relacionada |
| PAYMENT | Float | Valor pago |
| EXPECTED_INVOICE | Boolean | Se era uma fatura esperada |
| PLAN | Text | Plano cobrado |
| DATE_RECEIVED | DateTime | Data de recebimento |

### FEEDBACK — Pesquisas de Satisfação

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID | BigInteger (PK) | Identificador único do feedback |
| ACCOUNT_ID | BigInteger (FK → ACCOUNTS) | Conta que respondeu |
| EMAIL | Text | E-mail do respondente |
| RATING | Integer | Nota numérica (1-5) |
| RATING_MAPPED | Text | Classificação textual (Poor, Below Average, Average, Good, Great) |
| BODY | Text | Comentário livre |
| DATE_RECEIVED | DateTime | Data de recebimento |

### ANALYTIC_EVENTS — Eventos Analíticos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| ID | BigInteger (PK) | Identificador único do evento |
| ACCOUNT_ID | BigInteger (FK → ACCOUNTS) | Conta que gerou o evento |
| EVENT | Text | Tipo de evento (Page Viewed, Button Clicked) |
| PAGE_URL | Text | URL da página onde ocorreu |
| BUTTON_LABEL | Text | Label do botão clicado (se aplicável) |
| TIMESTAMP | DateTime | Data e hora do evento |
