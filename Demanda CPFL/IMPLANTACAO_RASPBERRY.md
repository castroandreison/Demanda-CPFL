# Implantação do Web App em Raspberry Pi

Este guia descreve como hospedar o Web App GED-119 / GED-13 em um Raspberry Pi, servindo múltiplas páginas e com acesso externo via túnel gratuito.

---

## 1. Pré-requisitos

- Raspberry Pi 3 ou superior (recomendado: Pi 4 / Pi 5 com 4GB+ RAM)
- Sistema operacional: Raspberry Pi OS (64-bit, Lite ou Desktop)
- Conexão com internet (cabo ou Wi-Fi)
- Fonte de alimentação estável

---

## 2. Configuração inicial do Raspberry Pi

### 2.1 Instalar o sistema

Use o **Raspberry Pi Imager** para gravar o sistema no cartão SD:

```bash
# Habilitar SSH e configurar Wi-Fi antes da primeira inicialização
# No Raspberry Pi Imager, clique em Ctrl+Shift+X para abrir opções avançadas
```

Acessar via SSH (Linux/Mac) ou PowerShell (Windows):

```bash
# Descobrir IP do Raspberry Pi
# Pelo roteador, ou usar:
ping raspberrypi.local

# Conectar via SSH
ssh pi@<ip-do-raspberry>
# Senha padrão: raspberry (altere imediatamente)
```

### 2.2 Atualizar o sistema

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git sqlite3 nginx
```

### 2.3 Criar diretório do projeto

```bash
mkdir -p ~/webapps
cd ~/webapps
```

---

## 3. Copiar o projeto para o Raspberry

Opção A — via Git (recomendado):

```bash
cd ~/webapps
git clone <url-do-repositorio> demanda-cpfl
cd demanda-cpfl
```

Opção B — via SCP (cópia direta):

```bash
# No seu computador local (PowerShell):
scp -r "C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL" pi@<ip>:~/webapps/demanda-cpfl
```

---

## 4. Configurar o ambiente Python

```bash
cd ~/webapps/demanda-cpfl

# Criar ambiente virtual
python3 -m venv venv

# Ativar o ambiente
source venv/bin/activate

# Instalar dependências
pip install flask flask-cors gunicorn
```

Se houver um arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Caso não exista, gere-o no seu computador local:

```bash
pip freeze > requirements.txt
```

---

## 5. Configurar o servidor de produção (Gunicorn)

### 5.1 Verificar se o app Flask funciona

```bash
cd ~/webapps/demanda-cpfl/web_app
source ../venv/bin/activate

# Teste rápido
python -c "from app import app; print('App carregado OK')"
```

### 5.2 Criar um arquivo wsgi.py

Caso não exista, crie `~/webapps/demanda-cpfl/web_app/wsgi.py`:

```python
from app import app

if __name__ == "__main__":
    app.run()
```

### 5.3 Testar com Gunicorn

```bash
cd ~/webapps/demanda-cpfl/web_app
../venv/bin/gunicorn --bind 0.0.0.0:8000 wsgi:app
```

Acesse `http://<ip-do-raspberry>:8000/ged119` para testar.

---

## 6. Servir múltiplas páginas (GED-119, GED-13 e outras)

O `app.py` já contém múltiplas rotas:

| Rota            | Funcionalidade        |
|-----------------|-----------------------|
| `/ged119`       | GED-119 (Demanda)     |
| `/ged13`        | GED-13 (Geral)        |
| `/`             | Página inicial        |

Para adicionar novas páginas no futuro, basta:

1. Criar o template em `templates/`
2. Adicionar a rota em `app.py`
3. Reiniciar o servidor

---

## 7. Configurar Nginx como proxy reverso (recomendado)

Nginx serve arquivos estáticos e faz proxy para o Gunicorn.

### 7.1 Instalar e configurar

```bash
sudo apt install -y nginx
```

Criar arquivo de configuração:

```bash
sudo nano /etc/nginx/sites-available/demanda-cpfl
```

Conteúdo:

```nginx
server {
    listen 80;
    server_name _;

    location /static/ {
        alias /home/pi/webapps/demanda-cpfl/web_app/static/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ativar o site:

```bash
sudo ln -s /etc/nginx/sites-available/demanda-cpfl /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # opcional
sudo nginx -t
sudo systemctl restart nginx
```

### 7.2 Firewall (opcional)

```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

Agora acesse `http://<ip-do-raspberry>` (sem precisar da porta 8000).

---

## 8. Manter o servidor rodando 24/7 (systemd)

Criar um serviço systemd para o Gunicorn:

```bash
sudo nano /etc/systemd/system/demanda-cpfl.service
```

Conteúdo:

```ini
[Unit]
Description=Demanda CPFL Web App (Gunicorn)
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/webapps/demanda-cpfl/web_app
Environment="PATH=/home/pi/webapps/demanda-cpfl/venv/bin"
ExecStart=/home/pi/webapps/demanda-cpfl/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Ativar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable demanda-cpfl
sudo systemctl start demanda-cpfl
sudo systemctl status demanda-cpfl
```

Comandos úteis:

```bash
sudo systemctl restart demanda-cpfl   # reiniciar
sudo systemctl stop demanda-cpfl      # parar
sudo journalctl -u demanda-cpfl -f    # ver logs
```

---

## 9. Acesso externo via túnel gratuito

### Opção A — Cloudflare Tunnel (recomendado, mais estável)

#### 9.1 Requisitos
- Um domínio próprio (ex.: `seudominio.com`) gerenciado pela Cloudflare
- Grátis para uso básico

#### 9.2 Instalar e configurar

```bash
# No Raspberry Pi
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Autenticar (abre URL no navegador)
cloudflared tunnel login
```

Criar o túnel:

```bash
cloudflared tunnel create demanda-cpfl
```

Criar arquivo de configuração:

```bash
nano ~/.cloudflared/config.yml
```

```yaml
tunnel: <id-do-tunnel>
credentials-file: /home/pi/.cloudflared/<id-do-tunnel>.json

ingress:
  - hostname: app.seudominio.com
    service: http://localhost:80
  - service: http_status:404
```

Configurar DNS no Cloudflare Dashboard (aponta `app.seudominio.com` para o tunnel).

Instalar como serviço:

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
```

Acesse: `https://app.seudominio.com`

### Opção B — Ngrok (mais simples, para testes)

#### 9.1 Instalar

```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

#### 9.2 Autenticar

```bash
ngrok config add-authtoken <seu-token>  # obter em https://dashboard.ngrok.com
```

#### 9.3 Iniciar túnel para o Nginx (porta 80)

```bash
ngrok http 80
```

Acesse a URL gerada (ex.: `https://abc123.ngrok-free.app`).

**Limitações do ngrok free:**
- URL aleatória que muda a cada reinicialização
- 40 conexões/minuto
- Apenas 1 túnel simultâneo
- Domínio personalizado apenas na versão paga

### Opção C — Serveo (sem instalação, apenas SSH)

```bash
ssh -R 80:localhost:80 serveo.net
```

Acesse a URL gerada pelo Serveo.

**Limitações:** instabilidade, sessão termina ao fechar SSH, sem criptografia real.

---

## 10. Acessar o sistema

| Local          | URL                                      |
|----------------|------------------------------------------|
| Rede local     | `http://<ip-do-raspberry>`               |
| Externo (CF)   | `https://app.seudominio.com`             |
| Externo (ngrok)| `https://abc123.ngrok-free.app`          |

---

## 11. Manutenção e Atualização

### Atualizar código

```bash
cd ~/webapps/demanda-cpfl
git pull origin main
sudo systemctl restart demanda-cpfl
```

### Verificar logs

```bash
# App
journalctl -u demanda-cpfl -f --no-hostname -o cat

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Cloudflare Tunnel
journalctl -u cloudflared -f
```

### Backup do banco de dados

Os bancos SQLite estão em:

```bash
~/webapps/demanda-cpfl/GED119/DB119/databaseCPFLGed119.db
~/webapps/demanda-cpfl/GED119/Projeto TK/projetos_ged119.db
~/webapps/demanda-cpfl/Ged13/DB13/databaseCPFLGed13.db
~/webapps/demanda-cpfl/Ged13/Projeto TK/projetos_ged13.db
```

Agendar backup automático com cron:

```bash
crontab -e
```

Adicionar linha:

```cron
0 3 * * * tar -czf /home/pi/backups/$(date +\%Y-\%m-\%d).tar.gz /home/pi/webapps/demanda-cpfl/*/DB*/ /home/pi/webapps/demanda-cpfl/*/Projeto\ TK/*.db
```

---

## 12. Recomendações finais

| Item                    | Sugestão                                    |
|-------------------------|---------------------------------------------|
| **Process manager**     | systemd (nativo, confiável)                 |
| **Proxy reverso**       | Nginx (leve, serve estáticos)               |
| **Túnel gratuito**      | Cloudflare Tunnel (estável, com HTTPS)      |
| **Workers Gunicorn**    | 3 (Pi 4) ou 2 (Pi 3)                       |
| **Domínio próprio**     | Cloudflare (DNS grátis, proteção DDoS)      |
| **SSL/TLS**             | Cloudflare faz automaticamente              |
| **Backup**              | Cron diário + script de backup              |
| **Monitoramento**       | `htop`, `journalctl`, `ngrok status`        |
