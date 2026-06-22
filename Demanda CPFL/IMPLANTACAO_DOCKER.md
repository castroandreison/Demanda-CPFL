# Implantação com Docker no Raspberry Pi

Este guia descreve como hospedar o Web App (GED-119 / GED-13) em um Raspberry Pi usando **Docker**, com cada plataforma em seu próprio container. O servidor pode rodar múltiplas plataformas independentes, cada uma em seu container.

---

## 1. Estrutura do servidor

Cada plataforma (app) roda em um container Docker independente. Um **proxy reverso** roteia as requisições para o container correto.

```
Raspberry Pi
├── Container: proxy (Nginx) → porta 80
├── Container: demanda-cpfl → http://demanda-cpfl:8000
│   └── Rotas: /ged119, /ged13, / (uma única aplicação Flask)
├── Container: outra-plataforma → http://outra:8000
└── ...
```

> Este Web App **já é uma plataforma completa** com múltiplas rotas (`/ged119`, `/ged13`).  
> Cada nova plataforma (outro sistema web) teria seu próprio container separado.

---

## 2. Pré-requisitos

- Raspberry Pi 3 ou superior (recomendado: Pi 4 / Pi 5 com 4GB+ RAM)
- Raspberry Pi OS (64-bit, Lite ou Desktop)
- Docker e Docker Compose instalados

### 2.1 Instalar Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
# Logout e login novamente (ou reboot)
```

### 2.2 Instalar Docker Compose

```bash
sudo apt update
sudo apt install -y docker-compose-plugin
```

Verificar:

```bash
docker --version
docker compose version
```

---

## 3. Estrutura de diretórios no servidor

```
/home/pi/docker/
├── proxy/                  # Proxy reverso (Nginx)
│   ├── nginx.conf
│   └── Dockerfile
├── demanda-cpfl/           # Plataforma Demanda CPFL (GED-119 + GED-13)
│   ├── Dockerfile
│   ├── docker-compose.yml  # opcional (pode usar compose global)
│   ├── requirements.txt
│   └── web_app/            # código completo da aplicação
│       ├── app.py
│       ├── core/
│       ├── templates/
│       ├── GED119/
│       ├── Ged13/
│       ├── NBR5410/
│       └── db5410/
├── outra-plataforma/       # Exemplo de outra plataforma futura
│   └── ...
└── docker-compose.yml      # Compose global (inicia tudo)
```

---

## 4. Copiar o código para o Raspberry

Opção A — Git (já estando no repositório):

```bash
cd /home/pi/docker
git clone <url-do-repositorio> demanda-cpfl
```

Opção B — SCP (do seu computador local):

```bash
# PowerShell (Windows) - copiar a pasta web_app inteira
scp -r "C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL" pi@<ip>:~/docker/demanda-cpfl
```

---

## 5. Criar Dockerfile da plataforma

### 5.1 `demanda-cpfl/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web_app/ ./web_app/

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--chdir", "/app/web_app", "app:app"]
```

### 5.2 `demanda-cpfl/requirements.txt`

```txt
flask>=3.0
flask-cors>=4.0
gunicorn>=21.0
```

### 5.3 Criar `web_app/wsgi.py` (para o Gunicorn)

Crie o arquivo `web_app/wsgi.py` com:

```python
from app import app

if __name__ == "__main__":
    app.run()
```

E ajuste o `CMD` no Dockerfile:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--chdir", "/app/web_app", "wsgi:app"]
```

---

## 6. Proxy reverso — Nginx

### 6.1 `proxy/nginx.conf`

```nginx
events {
    worker_connections 1024;
}

http {
    upstream demanda-cpfl {
        server demanda-cpfl:8000;
    }

    # Futuras plataformas:
    # upstream outra-plataforma {
    #     server outra-plataforma:8000;
    # }

    server {
        listen 80;
        server_name _;

        # --- Plataforma Demanda CPFL ---
        location /ged119 {
            proxy_pass http://demanda-cpfl;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ged13 {
            proxy_pass http://demanda-cpfl;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            proxy_pass http://demanda-cpfl;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Futuras plataformas:
        # location /outra-rota {
        #     proxy_pass http://outra-plataforma;
        #     ...
        # }
    }
}
```

### 6.2 `proxy/Dockerfile`

```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 7. Docker Compose global (inicia tudo)

`/home/pi/docker/docker-compose.yml`:

```yaml
version: "3.8"

services:
  proxy:
    build: ./proxy
    container_name: proxy
    ports:
      - "80:80"
    restart: unless-stopped
    networks:
      - app_network

  demanda-cpfl:
    build: ./demanda-cpfl
    container_name: demanda-cpfl
    expose:
      - "8000"
    volumes:
      # Montar bancos SQLite para persistência
      - ./demanda-cpfl/web_app/GED119/DB119:/app/web_app/GED119/DB119
      - ./demanda-cpfl/web_app/GED119/Projeto TK:/app/web_app/GED119/Projeto TK
      - ./demanda-cpfl/web_app/Ged13/DB13:/app/web_app/Ged13/DB13
      - ./demanda-cpfl/web_app/Ged13/Projeto TK:/app/web_app/Ged13/Projeto TK
      - ./demanda-cpfl/web_app/db5410:/app/web_app/db5410
      - ./demanda-cpfl/web_app/NBR5410/db5410:/app/web_app/NBR5410/db5410
    restart: unless-stopped
    networks:
      - app_network
    depends_on:
      - proxy

  # Futuras plataformas:
  # outra-plataforma:
  #   build: ./outra-plataforma
  #   ...

networks:
  app_network:
    driver: bridge
```

> **Nota:** Os volumes montam os diretórios de banco SQLite para que os dados persistam mesmo se o container for recriado.

---

## 8. Iniciar tudo

### 8.1 Primeira execução

```bash
cd /home/pi/docker
docker compose up -d --build
```

### 8.2 Verificar

```bash
docker ps
```

Deverá ver 2 containers rodando: `proxy` e `demanda-cpfl`.

Testar localmente:

```bash
curl http://localhost/ged119
curl http://localhost/ged13
```

---

## 9. Adicionar uma nova plataforma no futuro

1. Criar diretório: `mkdir -p /home/pi/docker/nova-plataforma`
2. Copiar o código e criar `Dockerfile` + `requirements.txt`
3. Adicionar serviço no `docker-compose.yml` global
4. Adicionar `upstream` e `location` no `proxy/nginx.conf`
5. Reconstruir:

```bash
cd /home/pi/docker
docker compose up -d --build
```

---

## 10. Manter rodando — Docker sempre ativo

```bash
sudo systemctl enable docker
```

Docker reinicia automaticamente os containers configurados com `restart: unless-stopped`.

---

## 11. Acesso externo — túnel gratuito

### Opção A — Cloudflare Tunnel (recomendado)

#### 11.1 Instalar cloudflared

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

#### 11.2 Autenticar e criar túnel

```bash
cloudflared tunnel login
cloudflared tunnel create app-tunnel
```

#### 11.3 Configurar

Criar `~/.cloudflared/config.yml`:

```yaml
tunnel: <id-do-tunnel>
credentials-file: /home/pi/.cloudflared/<id-do-tunnel>.json

ingress:
  - hostname: app.seudominio.com
    service: http://localhost:80
  - service: http_status:404
```

#### 11.4 Rodar como container (adicione ao `docker-compose.yml`)

```yaml
cloudflared:
  image: cloudflare/cloudflared:latest
  container_name: cloudflared
  command: tunnel run
  environment:
    - TUNNEL_TOKEN=<seu-token>
  restart: unless-stopped
  network_mode: host
```

#### 11.5 DNS

No Cloudflare Dashboard, CNAME de `app.seudominio.com` → ID do túnel.

### Opção B — Ngrok

```bash
docker run -d --name ngrok --network host ngrok/ngrok:latest http 80
```

### Opção C — Serveo

```bash
ssh -R 80:localhost:80 serveo.net
```

---

## 12. Gerenciamento diário

### Atualizar a plataforma

```bash
cd /home/pi/docker/demanda-cpfl
git pull
cd ..
docker compose up -d --build --force-recreate demanda-cpfl
```

### Logs

```bash
docker logs -f demanda-cpfl
docker logs -f proxy
docker logs -f cloudflared
```

### Backup dos bancos de dados

```bash
tar -czf ~/backups/$(date +%Y-%m-%d).tar.gz \
  /home/pi/docker/demanda-cpfl/web_app/GED119/DB119/*.db \
  /home/pi/docker/demanda-cpfl/web_app/GED119/Projeto\ TK/*.db \
  /home/pi/docker/demanda-cpfl/web_app/Ged13/DB13/*.db \
  /home/pi/docker/demanda-cpfl/web_app/Ged13/Projeto\ TK/*.db
```

Automatizar com cron:

```bash
crontab -e
```

```cron
0 3 * * * tar -czf /home/pi/backups/$(date +\%Y-\%m-\%d).tar.gz /home/pi/docker/demanda-cpfl/web_app/GED119/DB*/*.db /home/pi/docker/demanda-cpfl/web_app/GED119/Projeto\ TK/*.db /home/pi/docker/demanda-cpfl/web_app/Ged13/DB*/*.db /home/pi/docker/demanda-cpfl/web_app/Ged13/Projeto\ TK/*.db
```

---

## 13. Resumo de comandos

```bash
# Construir e iniciar
docker compose up -d --build

# Parar tudo
docker compose down

# Reiniciar um container específico
docker compose restart demanda-cpfl

# Ver logs em tempo real
docker compose logs -f

# Acessar o container
docker exec -it demanda-cpfl /bin/bash

# Limpar containers parados
docker system prune
```
