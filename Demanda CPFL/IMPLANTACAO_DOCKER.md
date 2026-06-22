# Implantação com Docker no Raspberry Pi

Este guia descreve como hospedar o Web App GED-119 / GED-13 em um Raspberry Pi usando **Docker**, com cada aplicação em seu próprio container, podendo escalar para múltiplas páginas no mesmo servidor.

---

## 1. Estrutura do servidor

Cada aplicação roda em um container Docker independente. Um **proxy reverso** (Nginx ou Traefik) roteia as requisições para o container correto.

```
Raspberry Pi
├── Container: proxy (Nginx/Traefik) → porta 80/443
├── Container: ged119 → http://ged119:8000
├── Container: ged13  → http://ged13:8000
├── Container: app-x  → http://app-x:8000
└── ... (outros apps)
```

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
│   └── docker-compose.yml
├── ged119/                 # Aplicação GED-119
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── web_app/            # código da aplicação
├── ged13/                  # Aplicação GED-13
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── web_app/            # código da aplicação
└── ... (outras aplicações)
```

---

## 4. Copiar o código para o Raspberry

Opção A — Git:

```bash
cd /home/pi/docker
git clone <url-do-repositorio> ged119
```

Opção B — SCP (do seu computador local):

```bash
# PowerShell (Windows)
scp -r "C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\web_app" pi@<ip>:~/docker/ged119/web_app
```

---

## 5. Criar Dockerfile para cada aplicação

### 5.1 `ged119/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "wsgi:app"]
```

### 5.2 `ged119/requirements.txt`

```txt
flask>=3.0
flask-cors>=4.0
gunicorn>=21.0
```

Crie o `ged119/web_app/wsgi.py` (se não existir):

```python
from app import app

if __name__ == "__main__":
    app.run()
```

### 5.3 `ged119/docker-compose.yml`

```yaml
version: "3.8"

services:
  ged119:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ged119
    expose:
      - "8000"
    volumes:
      - ./web_app/GED119/DB119:/app/web_app/GED119/DB119
      - ./web_app/GED119/Projeto\ TK:/app/web_app/GED119/Projeto\ TK
      - ./web_app/db5410:/app/web_app/db5410
      - ./web_app/NBR5410:/app/web_app/NBR5410
    restart: unless-stopped
    networks:
      - app_network

networks:
  app_network:
    external: true
```

### 5.4 Repetir para `ged13/`

Mesma estrutura, alterando os caminhos dos volumes e o nome do container.

---

## 6. Proxy reverso — Nginx

### 6.1 `proxy/nginx.conf`

```nginx
events {
    worker_connections 1024;
}

http {
    upstream ged119 {
        server ged119:8000;
    }

    upstream ged13 {
        server ged13:8000;
    }

    server {
        listen 80;
        server_name _;

        location /ged119 {
            proxy_pass http://ged119;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ged13 {
            proxy_pass http://ged13;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            return 200 "Servidor de Aplicacoes - Docker\n";
            add_header Content-Type text/plain;
        }
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

### 6.3 `proxy/docker-compose.yml`

```yaml
version: "3.8"

services:
  proxy:
    build: .
    container_name: proxy
    ports:
      - "80:80"
    restart: unless-stopped
    networks:
      - app_network

networks:
  app_network:
    external: true
```

---

## 7. Rede compartilhada entre containers

Criar a rede uma única vez (todos os containers usam a mesma):

```bash
docker network create app_network
```

---

## 8. Iniciar tudo

### 8.1 Construir e iniciar cada aplicação

```bash
cd /home/pi/docker/ged119
docker compose up -d --build

cd /home/pi/docker/ged13
docker compose up -d --build

cd /home/pi/docker/proxy
docker compose up -d --build
```

### 8.2 Verificar

```bash
docker ps
```

Deverá ver 3 containers rodando: `proxy`, `ged119`, `ged13`.

Testar:

```bash
curl http://localhost/ged119
curl http://localhost/ged13
```

---

## 9. Script de inicialização único (docker-compose global)

Para facilitar, crie um compose global em `/home/pi/docker/docker-compose.yml`:

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

  ged119:
    build: ./ged119
    container_name: ged119
    expose:
      - "8000"
    volumes:
      - ./ged119/web_app/GED119/DB119:/app/web_app/GED119/DB119
      - ./ged119/web_app/GED119/Projeto TK:/app/web_app/GED119/Projeto TK
      - ./ged119/web_app/db5410:/app/web_app/db5410
      - ./ged119/web_app/NBR5410:/app/app/web_app/NBR5410
    restart: unless-stopped
    networks:
      - app_network
    depends_on:
      - proxy

  ged13:
    build: ./ged13
    container_name: ged13
    expose:
      - "8000"
    volumes:
      - ./ged13/web_app/Ged13/DB13:/app/web_app/Ged13/DB13
      - ./ged13/web_app/Ged13/Projeto TK:/app/web_app/Ged13/Projeto TK
    restart: unless-stopped
    networks:
      - app_network
    depends_on:
      - proxy

networks:
  app_network:
    external: true
```

Iniciar tudo com um comando:

```bash
cd /home/pi/docker
docker compose up -d --build
```

---

## 10. Manter rodando — systemd + Docker

Docker já reinicia containers com `restart: unless-stopped`. Mas para garantir que o Docker Engine reinicie após reboot:

```bash
sudo systemctl enable docker
```

Testar:

```bash
sudo reboot
# Após reiniciar, verificar:
docker ps
```

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

#### 11.3 Configurar o túnel

Criar `~/.cloudflared/config.yml`:

```yaml
tunnel: <id-do-tunnel>
credentials-file: /home/pi/.cloudflared/<id-do-tunnel>.json

ingress:
  - hostname: app.seudominio.com
    service: http://localhost:80
  - service: http_status:404
```

#### 11.4 Rodar como container Docker (opcional)

```yaml
services:
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

No Cloudflare Dashboard, crie um registro CNAME de `app.seudominio.com` apontando para o ID do túnel.

### Opção B — Ngrok (túnel rápido para testes)

```bash
docker run -d --name ngrok --network host ngrok/ngrok:latest http 80 --domain <seu-subdominio>.ngrok-free.app
```

### Opção C — Serveo (sem instalação)

```bash
ssh -R 80:localhost:80 serveo.net
```

---

## 12. Gerenciamento e manutenção

### Atualizar uma aplicação

```bash
cd /home/pi/docker/ged119
git pull
docker compose up -d --build --force-recreate
```

### Ver logs

```bash
docker logs -f ged119
docker logs -f proxy
docker logs -f cloudflared
```

### Backup dos bancos de dados

Os dados ficam em volumes montados. Fazer backup:

```bash
tar -czf ~/backups/$(date +%Y-%m-%d).tar.gz \
  /home/pi/docker/ged119/web_app/GED119/DB119/*.db \
  /home/pi/docker/ged119/web_app/GED119/Projeto\ TK/*.db \
  /home/pi/docker/ged13/web_app/Ged13/DB13/*.db \
  /home/pi/docker/ged13/web_app/Ged13/Projeto\ TK/*.db
```

Automatizar com cron:

```bash
crontab -e
```

```cron
0 3 * * * tar -czf /home/pi/backups/$(date +\%Y-\%m-\%d).tar.gz /home/pi/docker/ged*/web_app/*/DB*/*.db /home/pi/docker/ged*/web_app/*/Projeto\ TK/*.db
```

---

## 13. Adicionar uma nova aplicação

1. Criar diretório: `mkdir -p /home/pi/docker/nova-app/web_app`
2. Copiar o código para `web_app/`
3. Criar `Dockerfile` e `requirements.txt`
4. Adicionar serviço no `docker-compose.yml` global
5. Adicionar `location /nova-rota` no `proxy/nginx.conf`
6. Reconstruir:

```bash
cd /home/pi/docker
docker compose up -d --build
```

---

## 14. Recomendações finais

| Item                    | Sugestão                                   |
|-------------------------|--------------------------------------------|
| **Container base**      | `python:3.11-slim` (imagem oficial)        |
| **Proxy reverso**       | Nginx ou Traefik (com Docker labels)       |
| **Túnel gratuito**      | Cloudflare Tunnel (HTTPS incluso, estável) |
| **Orquestração**        | Docker Compose (simples, suficente)        |
| **Workers Gunicorn**    | 2 por container (Pi 4)                     |
| **Backup**              | Cron + tar nos volumes montados            |
| **Segurança**           | Cloudflare (DDoS, SSL, tunnel criptografado)|
| **Domínio**             | Cloudflare (DNS grátis, tunnel na borda)   |
