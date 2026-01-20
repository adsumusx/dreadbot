# 🧹 Como Limpar o Registro Manualmente

Se você não conseguir usar o endpoint `/clear`, pode limpar manualmente:

## Opção 1: Via Render Dashboard

1. Acesse: https://dashboard.render.com
2. Vá no seu serviço `dreadbot-d4xc`
3. Clique em "Shell" ou "Logs"
4. Execute:
   ```bash
   rm license_registry.json
   ```
   Ou:
   ```bash
   echo "{}" > license_registry.json
   ```

## Opção 2: Adicionar Endpoint Temporário

Se o servidor não tem o endpoint `/clear`, você pode adicionar temporariamente:

1. **Edite `license_server.py` localmente**
2. **Adicione o endpoint `/clear`** (já está no código)
3. **Faça commit e push:**
   ```bash
   git add license_server.py
   git commit -m "Adiciona endpoint clear"
   git push
   ```
4. **Aguarde o deploy no Render** (2-5 minutos)
5. **Use o endpoint:**
   ```bash
   curl -X POST https://dreadbot-d4xc.onrender.com/clear
   ```

## Opção 3: Usar o Endpoint /stats para Ver

Primeiro, veja o que está registrado:

```bash
curl https://dreadbot-d4xc.onrender.com/stats
```

Isso mostra quantas licenças estão registradas.

## ⚠️ Importante

Após limpar o registro:
1. **Gere uma chave NOVA:**
   ```bash
   python keygen.py 30 teste_fresco
   ```

2. **Teste a chave nova:**
   ```bash
   python test_license.py --file license.key
   ```

3. **Use no cliente** - deve funcionar agora!

