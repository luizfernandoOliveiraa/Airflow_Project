# Pipeline de Extração de Dados - Airflow

Este projeto implementa um pipeline de extração de dados utilizando Apache Airflow, Docker e PostgreSQL para automatizar a coleta de dados de múltiplas fontes e carregá-los em um Data Warehouse.

## 📋 Visão Geral

O pipeline realiza extração de dados de:
- Banco de dados PostgreSQL (origem)
- Arquivo CSV com transações de clientes

Os dados extraídos são processados e carregados em um Data Warehouse containerizado para análise posterior.

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     CSV File    │    │   Data Lake     │
│   (Origem)      │───▶│   (Transações)  │───▶│   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │  Data Warehouse │
                                              │   (PostgreSQL)  │
                                              └─────────────────┘
```

## 🛠️ Tecnologias Utilizadas

- **Apache Airflow** - Orquestração de workflows
- **Astro CLI** - Desenvolvimento local do Airflow
- **Docker & Docker Compose** - Containerização
- **PostgreSQL** - Banco de dados origem e Data Warehouse
- **Pandas** - Processamento de dados
- **Python 3.12** - Linguagem principal

## 📁 Estrutura do Projeto

```
project/
├── dags/
│   └── pipeline_extraction.py    # DAG principal
├── include/
│   ├── transacoes.csv           # Arquivo CSV de origem
│   └── datalake/               # Diretório de armazenamento temporário
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## ⚙️ Configuração

### Pré-requisitos

- Docker e Docker Compose instalados
- Astro CLI instalado (`pip install astro-cli`)
- Python 3.8+

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/luizfernandoOliveiraa/Airflow_Project.git
cd pipeline-extraction
```

2. **Inicie o ambiente com Astro**
```bash
astro dev start
```

3. **Configure as conexões no Airflow**

Acesse `http://localhost:8080` e configure as seguintes conexões:

#### Conexão: `db_origem`
- **Connection Type**: Postgres
- **Host**: db_origem 
- **Schema**: db_origem
- **Login**: dborigem_teste
- **Password**: dborigem_teste2025
- **Port**: 5432

#### Conexão: `db_datawarehouse`
- **Connection Type**: Postgres
- **Host**: db_datawarehouse
- **Schema**: db_datawarehouse
- **Login**: db_datawarehouse_teste2025
- **Password**: db_datawarehouse_teste2025
- **Port**: 5432

## 🚀 Execução

### Execução Manual
1. Acesse a interface do Airflow em `http://localhost:8080`
2. Localize a DAG `pipeline_extraction`
3. Ative a DAG e execute manualmente ou aguarde o agendamento

### Execução Automática
A DAG está configurada para executar diariamente às 4:35 AM:
```python
schedule='35 4 * * *'
```

## 📊 Tabelas Extraídas

### Do PostgreSQL:
- `agencias`
- `clientes`
- `colaborador_agencia`
- `colaboradores`
- `contas`
- `propostas_credito`

### Do CSV:
- `transacoes` (dados de transações de clientes)

## 🔄 Fluxo de Execução

1. **Extração PostgreSQL** (`postgres_extract`)
   - Conecta no banco de origem
   - Extrai dados das tabelas configuradas
   - Salva no data lake como CSV

2. **Extração CSV** (`extract_csv`)
   - Lê arquivo de transações
   - Processa e salva no data lake

3. **Carregamento Data Warehouse** (`load_dw`)
   - Carrega todos os CSVs do data lake
   - Insere/atualiza tabelas no DW
   - Limpa dados temporários

## 📝 Logs e Monitoramento

- Logs detalhados disponíveis na interface do Airflow
- Tratamento de erros implementado em todas as tasks
- Notificações de falha configuráveis

## 🔧 Personalização

### Adicionar Nova Tabela
1. Adicione o nome da tabela em `SOURCE_TABLES`
2. Reinicie a DAG

### Modificar Agendamento
Altere o parâmetro `schedule` na definição da DAG:
```python
@dag(
    dag_id="pipeline_extraction",
    schedule='0 6 * * *',  # 6:00 AM diário
    ...
)
```

## 🐛 Troubleshooting

### Problemas Comuns

**Erro de Conexão com Banco**
- Verifique se as conexões estão configuradas corretamente
- Confirme se os containers estão rodando

**Arquivo CSV não encontrado**
- Verifique se o arquivo está em `/usr/local/airflow/include/transacoes.csv`
- Confirme as permissões de leitura

**Falha no Carregamento do DW**
- Verifique espaço em disco
- Confirme credenciais do Data Warehouse

### Comandos Úteis

```bash
# Ver logs dos containers
docker-compose logs -f

# Reiniciar ambiente Airflow
astro dev restart

# Acessar container Airflow
astro dev bash

# Parar ambiente
astro dev stop
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

Obs: Esse projeto foi desenvolvido em outro ambiente restrito, e adaptado para esse repositório, por isso temos poucos commits e sem desenvolvimento de testes.
