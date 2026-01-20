# 🔍 Diagnóstico de Problemas com Licenças

## Problema: "Chave inválida e já foi usada" para chave nova

### Passo 1: Teste a Chave Localmente

```bash
python test_license.py --file license.key
```

Ou:
```bash
python test_license.py "SUA_CHAVE_AQUI"
```

Isso mostrará:
- Se a chave é válida localmente
- O hash da chave original
- Se o servidor está respondendo
- O que o servidor retorna

### Passo 2: Verifique o Servidor

Teste o servidor diretamente:

```bash
curl https://dreadbot-d4xc.onrender.com/health
```

Deve retornar: `{"status":"ok"}`

### Passo 3: Teste Validação no Servidor

```bash
curl -X POST https://dreadbot-d4xc.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "SUA_CHAVE_AQUI",
    "machine_id": "TESTE",
    "action": "check"
  }'
```

### Passo 4: Verifique o Registro do Servidor

Se você tem acesso ao servidor, verifique o arquivo `license_registry.json` no Render.

### Possíveis Causas:

1. **Hash calculado diferente:**
   - Cliente e servidor podem estar calculando o hash de forma diferente
   - Verifique se `LICENSE_SECRET_KEY` é a mesma em ambos

2. **Servidor com dados antigos:**
   - O registro do servidor pode ter dados de testes anteriores
   - Limpe o arquivo `license_registry.json` no servidor

3. **Chave já foi testada:**
   - Se você testou a chave antes, ela pode estar registrada
   - Gere uma nova chave para teste

4. **Erro na validação:**
   - O servidor pode estar retornando erro por outro motivo
   - Verifique os logs do servidor no Render

### Solução Rápida:

1. **Gere uma chave NOVA:**
   ```bash
   python keygen.py 30 teste_novo
   ```

2. **Teste a chave nova:**
   ```bash
   python test_license.py --file license.key
   ```

3. **Se ainda falhar, limpe o registro do servidor:**
   - Acesse o dashboard do Render
   - Vá em "Shell" ou "Logs"
   - Delete ou limpe o arquivo `license_registry.json`

4. **Ou adicione um endpoint para limpar (temporário):**

Adicione no `license_server.py`:

```python
@app.route('/clear', methods=['POST'])
def clear_registry():
    """Limpa o registro (APENAS PARA DESENVOLVIMENTO!)"""
    try:
        if os.path.exists(REGISTRY_FILE):
            os.remove(REGISTRY_FILE)
        return jsonify({'status': 'ok', 'message': 'Registro limpo'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

**⚠️ REMOVA este endpoint em produção!**

