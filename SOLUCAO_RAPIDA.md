# ⚡ Solução Rápida - Chave Nova Dizendo que Já Foi Usada

## 🔧 Passos para Resolver

### 1. Teste a Chave

```bash
python test_license.py --file license.key
```

Isso mostrará exatamente o que está acontecendo.

### 2. Verifique o Servidor

```bash
curl https://dreadbot-d4xc.onrender.com/health
```

### 3. Limpe o Registro do Servidor (se necessário)

Se o servidor tem dados antigos, limpe:

```bash
curl -X POST https://dreadbot-d4xc.onrender.com/clear
```

**⚠️ Isso apaga TODAS as ativações! Use apenas para testes.**

### 4. Gere uma Chave NOVA

```bash
python keygen.py 30 teste_fresco
```

### 5. Teste a Chave Nova

```bash
python test_license.py --file license.key
```

## 🐛 Se Ainda Não Funcionar

1. **Verifique se o servidor está rodando:**
   - Acesse: https://dreadbot-d4xc.onrender.com/health
   - Deve retornar `{"status":"ok"}`

2. **Verifique os logs do servidor:**
   - No dashboard do Render, veja os logs
   - Procure por erros

3. **Teste manualmente:**
   ```bash
   curl -X POST https://dreadbot-d4xc.onrender.com/validate \
     -H "Content-Type: application/json" \
     -d '{"license_key":"SUA_CHAVE","machine_id":"TESTE","action":"check"}'
   ```

4. **Verifique se LICENSE_SECRET_KEY é a mesma:**
   - No `license.py` (cliente)
   - No `license_server.py` (servidor)
   - Devem ser IDÊNTICAS!

## 💡 Dica

Se você testou a chave antes, ela pode estar registrada no servidor. Gere uma chave completamente nova.

