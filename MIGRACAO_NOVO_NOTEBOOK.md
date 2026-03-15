# Guia: Migrando o MagaBip para um Novo Notebook (Windows)

Este guia explica como preparar e rodar o sistema completo em uma nova máquina.

## 1. Pré-requisitos na Nova Máquina

Certifique-se de ter instalado:

1. **Docker Desktop** (obrigatório para rodar o banco, métricas e logs facilmente).
2. **Git** (opcional, mas recomendado para baixar o código).
3. **Python 3.11+** (opcional, se quiser rodar fora do Docker).

## 2. Preparando os Arquivos

1. Copie a pasta inteira `MagaBip` para o novo notebook.
2. **NÃO COPIE** as pastas de ambiente virtual (`.venv`) ou pastas temporárias (`__pycache__`). O Docker irá gerenciar isso.
3. Localize o arquivo `.env.example` e renomeie-o para `.env`.
4. Preencha as chaves no `.env` (Gemini API, Webhooks, etc.).

## 3. Rodando o Sistema (Com Docker - Recomendado)

Abra o terminal (PowerShell ou CMD) na pasta do projeto e execute:

```powershell
docker-compose up -d --build
```

Isso vai:

- Criar o Banco de Dados PostgreSQl.
- Instalar todas as dependências do Python.
- Subir o Dashboard (Grafana), Métricas (Prometheus) e Logs (Fluent Bit).
- Iniciar o App MagaBip na porta **80**.

## 4. Populando o Banco de Dados

Como o novo banco estará vazio, você precisa criar o usuário admin e os aparelhos iniciais:

### No Windows (Localmente)

```powershell
.\.venv\Scripts\python.exe populate_filiais.py
.\.venv\Scripts\python.exe seed_devices.py
.\.venv\Scripts\python.exe create_admin.py
```

### Dentro do Docker (Se preferir)

```powershell
docker exec -it magabip-app python populate_filiais.py
docker exec -it magabip-app python seed_devices.py
docker exec -it magabip-app python create_admin.py
```

## 5. Acessando o Sistema

- **MagaBip:** `http://localhost`
- **Grafana:** `http://localhost:3000` (Login: `admin` / Senha: `admin`)
- **Prometheus:** `http://localhost:9090`

## 6. Dicas de Migração de Dados (Backup)

Se você quiser levar os dados (usuários, registros de retiradas) do notebook antigo, siga estes passos:

1. **No notebook antigo:**

   ```powershell
   docker exec -t magabip-db pg_dump -U magabip_user magabip_db > backup_banco.sql
   ```

2. **No notebook novo (após o docker-compose up):**

   ```powershell
   cat backup_banco.sql | docker exec -i magabip-db psql -U magabip_user -d magabip_db
   ```

---
Desenvolvido para MagaBip - 2026
