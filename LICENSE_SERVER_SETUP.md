# 🔐 Configuração do Servidor de Validação de Licenças

Este guia explica como configurar o servidor de validação online para o sistema de licenciamento.

## 📋 Por que um Servidor Online?

O servidor online garante que:
- ✅ Cada licença só pode ser usada em **uma única máquina**
- ✅ Validação centralizada e confiável
- ✅ Impossível burlar copiando arquivos locais
- ✅ Controle total sobre ativações

## 🚀 Instalação do Servidor

### 1. Instalar Dependências

```bash
pip install flask
```

### 2. Configurar o Servidor

Edite `license_server.py` e configure:
- **LICENSE_SECRET_KEY**: Deve ser a MESMA chave do `license.py`
- **REGISTRY_FILE**: Arquivo onde serão salvos os registros (opcional)

### 3. Executar o Servidor

#### Desenvolvimento (apenas para testes):
```bash
python license_server.py
```

#### Produção (recomendado):

Use um servidor WSGI como **gunicorn**:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 license_server:app
```

Ou com **uwsgi**:
```bash
pip install uwsgi
uwsgi --http :5000 --wsgi-file license_server.py --callable app
```

### 4. Configurar HTTPS (OBRIGATÓRIO em produção!)

Use um proxy reverso como **nginx** com certificado SSL:

```nginx
server {
    listen 443 ssl;
    server_name seuservidor.com;
    
    ssl_certificate /caminho/para/certificado.crt;
    ssl_certificate_key /caminho/para/chave.key;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Configuração no Cliente

### Opção 1: Variável de Ambiente

Configure a URL do servidor:

**Windows:**
```cmd
set LICENSE_SERVER_URL=https://seuservidor.com/validate
```

**Linux/Mac:**
```bash
export LICENSE_SERVER_URL=https://seuservidor.com/validate
```

### Opção 2: Modificar license.py

Edite `license.py` e altere:

```python
LICENSE_SERVER_URL = "https://seuservidor.com/validate"
```

### Opção 3: No Executável

Antes de gerar o .exe, configure a URL em `license.py`.

## 📦 Deploy em Serviços Cloud

### Heroku

1. Crie um arquivo `Procfile`:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT license_server:app
```

2. Deploy:
```bash
heroku create seu-app
git push heroku main
```

### DigitalOcean / VPS

1. Instale dependências no servidor
2. Configure nginx como proxy reverso
3. Use systemd para manter o servidor rodando:

```ini
[Unit]
Description=License Server
After=network.target

[Service]
User=seu-usuario
WorkingDirectory=/caminho/para/app
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 license_server:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### AWS / Google Cloud

Use serviços como:
- **AWS Lambda** (serverless)
- **Google Cloud Functions**
- **Azure Functions**

Adapte o código para o ambiente serverless.

## 🔒 Segurança

### ⚠️ IMPORTANTE:

1. **Use HTTPS sempre!** Nunca use HTTP em produção
2. **Proteja LICENSE_SECRET_KEY** - nunca compartilhe
3. **Backup do registro** - faça backup regular de `license_registry.json`
4. **Rate limiting** - adicione limite de requisições por IP
5. **Autenticação** - considere adicionar autenticação ao servidor

### Exemplo de Rate Limiting:

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

## 📊 Monitoramento

### Logs

O servidor registra todas as validações. Monitore:
- Tentativas de ativação duplicada
- Erros de validação
- Acessos suspeitos

### Estatísticas

Adicione um endpoint para estatísticas:

```python
@app.route('/stats', methods=['GET'])
def stats():
    registry = load_registry()
    return jsonify({
        'total_licenses': len([k for k in registry.keys() if not k.endswith('_date')]),
        'last_activation': max([v for k, v in registry.items() if k.endswith('_date')], default='N/A')
    })
```

## 🧪 Teste

### Testar o Servidor:

```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "SUA_CHAVE_AQUI",
    "machine_id": "MACHINE_ID_AQUI",
    "action": "check"
  }'
```

### Testar Health Check:

```bash
curl http://localhost:5000/health
```

## ✅ Checklist de Produção

- [ ] Servidor configurado com HTTPS
- [ ] LICENSE_SECRET_KEY protegida
- [ ] Backup automático do registro
- [ ] Rate limiting configurado
- [ ] Monitoramento de logs
- [ ] URL do servidor configurada no cliente
- [ ] Testes realizados
- [ ] Documentação atualizada

## 🆘 Solução de Problemas

### Servidor não responde

- Verifique se o servidor está rodando
- Verifique firewall/portas
- Verifique logs do servidor

### Cliente não consegue conectar

- Verifique URL do servidor
- Verifique conectividade de rede
- Verifique certificado SSL (se HTTPS)

### Licença válida mas rejeitada

- Verifique se LICENSE_SECRET_KEY é a mesma
- Verifique logs do servidor
- Verifique se a chave não foi ativada antes

