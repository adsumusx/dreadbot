# ⚡ Guia Rápido - Deploy em Render.com (5 minutos)

## 🎯 Passo a Passo Simplificado

### 1. Preparar Arquivos

Certifique-se de ter:
- ✅ `license_server.py`
- ✅ `requirements.txt` (com flask e gunicorn)
- ✅ `Procfile` (já criado)

### 2. Criar Repositório GitHub

```bash
git init
git add .
git commit -m "License server"
git remote add origin https://github.com/SEU_USUARIO/license-server.git
git push -u origin main
```

### 3. Deploy no Render

1. Acesse: https://render.com
2. Faça login com GitHub
3. Clique em "New +" → "Web Service"
4. Conecte seu repositório
5. Configure:
   - **Name:** `license-server`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT license_server:app`
6. Clique em "Create Web Service"
7. Aguarde 2-5 minutos

### 4. Copiar URL

Após o deploy, copie a URL:
```
https://license-server.onrender.com
```

### 5. Configurar no Cliente

Edite `license.py`:
```python
LICENSE_SERVER_URL = "https://license-server.onrender.com/validate"
```

### ✅ Pronto!

O servidor está online e funcionando!

---

## 🔄 Atualizar o Servidor

Sempre que fizer mudanças:

```bash
git add .
git commit -m "Atualização"
git push
```

O Render atualiza automaticamente!

---

## 📝 Nota Importante

- O servidor "dorme" após 15min de inatividade
- A primeira requisição pode demorar alguns segundos (acorda o servidor)
- Para evitar isso, use Railway.app ou Fly.io

