# MagaBip 🚀

O **MagaBip** é um sistema de gestão e monitoramento de ativos (coletores, impressoras, rádios e máquinas) focado em eficiência operacional e manutenção proativa em Centros de Distribuição.

## ✨ Funcionalidades Principais

- **📦 Gestão de Ativos**: Controle completo de coletores, impressoras térmicas, rádios e máquinas pesadas.
- **🔄 Check-in/Check-out**: Sistema rigoroso de retirada e devolução baseado em turnos de trabalho.
- **🛠 Suporte e Manutenção**: Abertura de tickets de suporte com integração opcional a sistemas de chamados.
- **📊 Dashboard Inteligente**: Visualização em tempo real de equipamentos em uso, disponíveis ou em manutenção.
- **🔋 Monitoramento de Saúde (IoT)**: Rastreamento de nível de bateria e sinal RSSI (em dispositivos compatíveis).
- **🏢 Multi-filial**: Suporte a múltiplos centros de distribuição com isolamento de dados por unidade.

## 🛠 Tecnologias Utilizadas

- **Backend**: Python 3.x com Flask
- **Banco de Dados**: SQLAlchemy (Suporte a PostgreSQL e SQLite)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Monitoramento**: Prometheus & Grafana
- **Autenticação**: Flask-Login & OAuth2 (Google, Humand, Corporate)

## 🚀 Como Executar o Projeto

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/rafaelacamecran-cell/MagaBip.git
   cd MagaBip
   ```

2. **Crie e ative um ambiente virtual**:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # No Windows
   ```

3. **Instale as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**:
   - Crie um arquivo `.env` baseado no `.env.example` e preencha suas credenciais.

5. **Inicie o servidor**:

   ```bash
   python app.py
   ```

   *O sistema estará disponível em: `http://localhost:5000`*

## 🔒 Segurança e Regras de Negócio

- **Regras de Turno**: Bloqueio automático de retiradas fora do horário estipulado para cada turno.
- **VPN Corporativa**: Opção de restringir o acesso apenas a IPs internos da empresa.
- **Sessão Segura**: Timeout automático baseado no perfil do usuário.

---
Desenvolvido por [Rafaela Camecran](https://github.com/rafaelacamecran-cell)
