# ⚡ Solução Imediata - Limpar Registro do Servidor

## 🔍 Problema Identificado

O servidor no Render não tem o endpoint `/clear` ainda porque precisa ser atualizado.

## ✅ Solução Rápida

### Opção 1: Atualizar o Servidor no Render

1. **Se você tem o código no GitHub:**
   ```bash
   git add license_server.py
   git commit -m "Adiciona endpoints /clear e /stats"
   git push
   ```
   O Render atualiza automaticamente em 2-5 minutos.

2. **Se não tem no GitHub:**
   - Acesse: https://dashboard.render.com
   - Vá no seu serviço
   - Clique em "Manual Deploy"
   - Faça upload do `license_server.py` atualizado

### Opção 2: Limpar Manualmente (Temporário)

Como solução temporária, você pode **desabilitar temporariamente a validação online**:

1. **Edite `license.py` localmente:**
   ```python
   # Comente ou mude a URL para None temporariamente
   LICENSE_SERVER_URL = None  # Desabilita validação online temporariamente
   ```

2. **Ou use variável de ambiente:**
   ```bash
   set LICENSE_SERVER_URL=
   ```

3. **Teste a chave:**
   - Agora vai usar apenas validação local
   - Funciona, mas menos seguro

4. **Depois reative:**
   ```python
   LICENSE_SERVER_URL = "https://dreadbot-d4xc.onrender.com/validate"
   ```

### Opção 3: Limpar Registro Local

O arquivo `license.registry` local tem várias chaves. Limpe:

1. **Delete o arquivo:**
   ```bash
   del license.registry
   ```

2. **Ou limpe o conteúdo:**
   - Abra `license.registry`
   - Deixe apenas: `{}`
   - Salve

3. **Teste novamente**

## 🎯 Recomendação

**Melhor solução:** Atualize o servidor no Render com o código novo que tem `/clear`, depois limpe o registro e teste com chave nova.

**Solução rápida:** Limpe o `license.registry` local e desabilite temporariamente a validação online para testar.

