# Guia de Migração: Windows para Linux (Servidor Dedicado)

O sistema MagaBip foi preparado para ser 100% compatível com Linux e Docker. Siga estes passos quando decidir migrar:

## 1. Copiar os Arquivos

Copie toda a pasta do projeto para o novo servidor Linux.

## 2. Configurar o Ambiente (.env)

Certifique-se de que o arquivo `.env` no servidor Linux tenha as variáveis corretas:

```bash
FLASK_ENV=production
MODO_DEBUG=False
DATABASE_URL=postgresql://usuário:senha@localhost:5432/magabip_db
GEMINI_API_KEY=sua_chave_aqui

# Configurações do Portal Corporativo (Opcional se usar login local)
SSOCORP_CLIENT_ID=seu_client_id
SSOCORP_CLIENT_SECRET=seu_client_secret
SSOCORP_AUTHORIZE_URL=https://ssocorp.magazineluiza.com.br/oauth/authorize
SSOCORP_TOKEN_URL=https://ssocorp.magazineluiza.com.br/oauth/token
SSOCORP_USERINFO_URL=https://ssocorp.magazineluiza.com.br/api/v1/userinfo
```

## 3. Usando Docker (Recomendado)

O Docker é a forma mais fácil de rodar no Linux:

1. Instale o Docker e o Docker Compose.
2. Na pasta do projeto, rode:

   ```bash
   docker-compose up -d --build
   ```

O sistema subirá automaticamente usando o **Gunicorn** no container.

## 4. Rodando sem Docker (Manual)

Se preferir não usar Docker:

1. Instale as dependências de sistema: `sudo apt update && sudo apt install -y python3-venv libpq-dev build-essential`
2. Crie e ative o venv: `python3 -m venv .venv && source .venv/bin/activate`
3. Instale os requisitos: `pip install -r requirements.txt`
4. Use o Gunicorn para rodar:

   ```bash
   gunicorn --bind 0.0.0.0:5000 "app:create_app()"
   ```

## 5. Autostart no Linux (sem Docker)

Para que o sistema ligue sozinho com o Linux, use o **Systemd**:
Crie o arquivo `/etc/systemd/system/magabip.service`:

```ini
[Unit]
Description=Servidor MagaBip
After=network.target

[Service]
User=seu_usuario
WorkingDirectory=/caminho/do/projeto
ExecStart=/caminho/do/projeto/.venv/bin/gunicorn --bind 0.0.0.0:80 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

Depois: `sudo systemctl enable magabip && sudo systemctl start magabip`

## 6. Acesso Multirrede (Wi-Fi e Cabeada)

Para que o pessoal da operação (Wi-Fi) e os líderes/SESMT (Cabo) acessem o sistema simultaneamente no CD:

1. **IP Estático**: Recomenda-se configurar um IP estático para o servidor Linux em ambas as interfaces (ou uma reserva de IP no seu roteador/DHCP).
2. **Firewall**: O Linux costuma vir com firewall ativo. Libere a porta 80:

   ```bash
   sudo ufw allow 80/tcp
   sudo ufw reload
   ```

3. **Identificando os IPs**: No terminal do Linux, rode:

   ```bash
   hostname -I
   ```

   Isso mostrará todos os IPs do servidor (ex: o IP do cabo e o IP do Wi-Fi). Qualquer um desses IPs servirá para acesso, desde que as redes não sejam isoladas.

4. **Binding**: O sistema já está configurado para `--bind 0.0.0.0`, o que significa que ele "escuta" em todas as placas de rede do servidor (Cabo e Wi-Fi) ao mesmo tempo.
