# 🔄 Como Atualizar o Servidor no Render

O servidor no Render precisa ser atualizado com o novo código que inclui o endpoint `/clear`.

## Método 1: Deploy Automático via GitHub (Recomendado)

### Se você já conectou o GitHub:

1. **Faça commit das mudanças:**
   ```bash
   git add license_server.py
   git commit -m "Adiciona endpoint /clear e /stats"
   git push
   ```

2. **O Render atualiza automaticamente!**
   - Vá no dashboard do Render
   - Veja os logs do deploy
   - Aguarde 2-5 minutos

### Se ainda não conectou:

1. **Crie repositório no GitHub:**
   ```bash
   git init
   git add .
   git commit -m "License server"
   git remote add origin https://github.com/SEU_USUARIO/license-server.git
   git push -u origin main
   ```

2. **No Render:**
   - Vá em "Settings" do seu serviço
   - Conecte o repositório GitHub
   - O Render fará deploy automático

## Método 2: Deploy Manual

1. **No dashboard do Render:**
   - Vá no seu serviço
   - Clique em "Manual Deploy"
   - Selecione a branch/commit
   - Clique em "Deploy"

## Método 3: Via Render CLI (Avançado)

```bash
# Instale o CLI
npm install -g render-cli

# Faça login
render login

# Deploy
render deploy
```

## ✅ Verificar se Atualizou

Após o deploy, teste:

```bash
curl https://dreadbot-d4xc.onrender.com/health
```

E:

```bash
curl -X POST https://dreadbot-d4xc.onrender.com/clear
```

Deve retornar: `{"status":"ok","message":"Registro limpo com sucesso"}`

## 📊 Ver Estatísticas

```bash
curl https://dreadbot-d4xc.onrender.com/stats
```

Isso mostra quantas licenças estão registradas.

