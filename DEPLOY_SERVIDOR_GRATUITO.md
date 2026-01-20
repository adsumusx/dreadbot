# 🌐 Deploy do Servidor em Serviços Gratuitos

Este guia mostra como fazer deploy do servidor de validação em serviços web gratuitos.

## 🎯 Opções de Serviços Gratuitos

### 1. Render.com (⭐ RECOMENDADO - Mais Fácil)
- ✅ Grátis para sempre
- ✅ HTTPS automático
- ✅ Deploy automático via GitHub
- ✅ Fácil de configurar
- ⚠️ Servidor "dorme" após 15min de inatividade (acorda na primeira requisição)

### 2. Railway.app
- ✅ Grátis com créditos mensais ($5 grátis/mês)
- ✅ HTTPS automático
- ✅ Deploy via GitHub
- ✅ Não "dorme"

### 3. Fly.io
- ✅ Plano gratuito generoso
- ✅ HTTPS automático
- ✅ Globalmente distribuído

### 4. PythonAnywhere
- ✅ Grátis para apps web
- ✅ Específico para Python
- ⚠️ Requer verificação por SMS

---

## 🚀 Método 1: Render.com (Recomendado)

### Passo 1: Preparar o Código

Crie um arquivo `requirements.txt` na raiz do projeto:

```txt
flask>=3.0.0
gunicorn>=21.2.0
```

Crie um arquivo `render.yaml` (opcional, facilita o deploy):

```yaml
services:
  - type: web
    name: license-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 4 -b 0.0.0.0:$PORT license_server:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

Ou crie um arquivo `Procfile`:

```
web: gunicorn -w 4 -b 0.0.0.0:$PORT license_server:app
```

### Passo 2: Atualizar license_server.py

Certifique-se de que o servidor usa a variável `PORT` do ambiente:

```python
import os

port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=False)
```

### Passo 3: Criar Conta no Render

1. Acesse: https://render.com
2. Clique em "Get Started for Free"
3. Faça login com GitHub (recomendado)

### Passo 4: Fazer Deploy

**Opção A: Via GitHub (Recomendado)**

1. **Crie um repositório no GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/SEU_USUARIO/license-server.git
   git push -u origin main
   ```

2. **No Render:**
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub
   - Selecione o repositório
   - Configure:
     - **Name:** `license-server`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT license_server:app`
   - Clique em "Create Web Service"

3. **Aguarde o deploy** (pode levar 2-5 minutos)

4. **Copie a URL gerada:**
   ```
   https://license-server.onrender.com
   ```

**Opção B: Deploy Manual**

1. No Render, clique em "New +" → "Web Service"
2. Selecione "Public Git repository"
3. Cole a URL do seu repositório
4. Configure como acima

### Passo 5: Configurar no Cliente

Edite `license.py`:

```python
LICENSE_SERVER_URL = "https://license-server.onrender.com/validate"
```

Ou use variável de ambiente:
```bash
export LICENSE_SERVER_URL=https://license-server.onrender.com/validate
```

### ✅ Pronto!

O servidor está rodando e acessível pela internet!

---

## 🚂 Método 2: Railway.app

### Passo 1: Preparar o Código

Crie `requirements.txt`:
```txt
flask>=3.0.0
gunicorn>=21.2.0
```

Crie `Procfile`:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT license_server:app
```

### Passo 2: Criar Conta

1. Acesse: https://railway.app
2. Clique em "Start a New Project"
3. Faça login com GitHub

### Passo 3: Deploy

1. Clique em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Selecione seu repositório
4. Railway detecta automaticamente e faz o deploy

### Passo 4: Obter URL

1. Após o deploy, clique no serviço
2. Vá em "Settings" → "Generate Domain"
3. Copie a URL (ex: `license-server.up.railway.app`)

### Passo 5: Configurar no Cliente

```python
LICENSE_SERVER_URL = "https://license-server.up.railway.app/validate"
```

---

## ✈️ Método 3: Fly.io

### Passo 1: Instalar Fly CLI

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Linux/Mac:**
```bash
curl -L https://fly.io/install.sh | sh
```

### Passo 2: Criar Conta

```bash
fly auth signup
```

### Passo 3: Preparar App

Crie `fly.toml`:

```toml
app = "license-server"
primary_region = "gru"  # ou outra região próxima

[build]

[env]
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

### Passo 4: Deploy

```bash
fly launch
fly deploy
```

### Passo 5: Obter URL

```bash
fly open
```

A URL será algo como: `https://license-server.fly.dev`

---

## 🔧 Atualizar license_server.py para Produção

Atualize o final do arquivo `license_server.py`:

```python
if __name__ == '__main__':
    import os
    
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("Servidor de Validação de Licenças - Bot DreadmystDB")
    print("=" * 60)
    print(f"\n📡 Servidor iniciado na porta {port}")
    print(f"   URL: http://0.0.0.0:{port}")
    print("\n" + "=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
```

---

## 📋 Checklist de Deploy

- [ ] `requirements.txt` criado com Flask e gunicorn
- [ ] `Procfile` ou comando de start configurado
- [ ] `license_server.py` atualizado para usar variável PORT
- [ ] Código commitado no GitHub
- [ ] Conta criada no serviço escolhido
- [ ] Deploy realizado com sucesso
- [ ] URL obtida e testada
- [ ] URL configurada no cliente (`license.py`)

---

## 🧪 Testar o Deploy

### 1. Teste Health Check:

```bash
curl https://SEU_SERVIDOR.com/health
```

Deve retornar: `{"status":"ok"}`

### 2. Teste Validação:

```bash
curl -X POST https://SEU_SERVIDOR.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "TESTE",
    "machine_id": "TESTE",
    "action": "check"
  }'
```

---

## 🔒 Segurança

### Recomendações:

1. **HTTPS:** Todos os serviços acima fornecem HTTPS automaticamente ✅
2. **Rate Limiting:** Considere adicionar limite de requisições
3. **Backup:** Faça backup regular de `license_registry.json`
4. **Monitoramento:** Configure alertas se disponível

### Adicionar Rate Limiting:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/validate', methods=['POST'])
@limiter.limit("10 per minute")
def validate_license():
    # ...
```

---

## 📊 Monitoramento

### Render.com:
- Dashboard mostra logs em tempo real
- Métricas de uso disponíveis

### Railway.app:
- Logs disponíveis no dashboard
- Métricas de recursos

### Fly.io:
```bash
fly logs
```

---

## 🆘 Solução de Problemas

### Deploy falha:
- Verifique se `requirements.txt` está correto
- Verifique se o comando de start está correto
- Veja os logs no dashboard do serviço

### Servidor não responde:
- Verifique se o deploy foi bem-sucedido
- Verifique os logs
- Teste o endpoint `/health` primeiro

### Erro 500:
- Verifique os logs do servidor
- Verifique se `license_registry.json` tem permissões de escrita
- Em alguns serviços, pode precisar usar banco de dados

---

## 💡 Dica: Usar Banco de Dados (Opcional)

Para produção, considere usar um banco de dados em vez de arquivo JSON:

### SQLite (simples):
```python
import sqlite3

def init_db():
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (hash TEXT PRIMARY KEY, machine_id TEXT, date TEXT)''')
    conn.commit()
    conn.close()
```

### PostgreSQL (Render/Railway fornecem grátis):
```python
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL)
```

---

## ✅ Recomendação Final

**Para começar rápido:** Use **Render.com**
- Mais fácil de configurar
- HTTPS automático
- Deploy via GitHub
- Grátis para sempre

**Para uso intensivo:** Use **Railway.app**
- Não "dorme"
- Mais recursos
- Melhor para produção

