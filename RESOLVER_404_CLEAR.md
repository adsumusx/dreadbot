# 🔧 Resolver Erro 404 no Endpoint /clear

## ❌ Problema

O servidor no Render retorna `404 Not Found` para `/clear` porque o código no servidor não foi atualizado ainda.

## ✅ Soluções

### Solução 1: Atualizar o Servidor no Render (Recomendado)

O código `license_server.py` já tem o endpoint `/clear`, mas precisa ser enviado para o Render.

#### Se você tem o código no GitHub:

1. **Verifique se está tudo commitado:**
   ```bash
   git status
   ```

2. **Adicione e faça commit:**
   ```bash
   git add license_server.py
   git commit -m "Adiciona endpoints /clear e /stats"
   git push
   ```

3. **Aguarde 2-5 minutos** - O Render atualiza automaticamente

4. **Teste novamente:**
   ```bash
   curl -X POST https://dreadbot-d4xc.onrender.com/clear
   ```

#### Se NÃO tem no GitHub:

**Opção A: Conectar GitHub (Melhor)**
1. Acesse: https://dashboard.render.com
2. Vá no seu serviço `dreadbot-d4xc`
3. Clique em "Settings"
4. Em "Build & Deploy", conecte seu repositório GitHub
5. Faça push do código
6. O Render fará deploy automático

**Opção B: Deploy Manual**
1. Acesse: https://dashboard.render.com
2. Vá no seu serviço
3. Clique em "Manual Deploy"
4. Faça upload do `license_server.py` atualizado
5. Aguarde o deploy

### Solução 2: Limpar Registro Local (Temporário)

Enquanto o servidor não atualiza, você pode limpar o registro local:

1. **Delete o arquivo `license.registry`:**
   ```bash
   del license.registry
   ```

2. **Ou limpe o conteúdo:**
   - Abra `license.registry`
   - Deixe apenas: `{}`
   - Salve

3. **Gere uma chave NOVA:**
   ```bash
   python keygen.py 30 teste_novo
   ```

4. **Teste a chave nova** - deve funcionar agora!

### Solução 3: Desabilitar Validação Online Temporariamente

Se você precisa testar AGORA e não pode esperar o deploy:

1. **Edite `license.py` temporariamente:**
   ```python
   # Linha 25, mude para:
   LICENSE_SERVER_URL = None  # Desabilita temporariamente
   ```

2. **Ou use variável de ambiente:**
   ```bash
   set LICENSE_SERVER_URL=
   python bot_gui.py
   ```

3. **Teste** - agora usa apenas validação local

4. **Depois reative:**
   ```python
   LICENSE_SERVER_URL = "https://dreadbot-d4xc.onrender.com/validate"
   ```

## 📊 Verificar Status do Servidor

Antes de limpar, veja o que está registrado:

```bash
curl https://dreadbot-d4xc.onrender.com/stats
```

Isso mostra quantas licenças estão registradas.

## ✅ Verificar se Atualizou

Após atualizar o servidor, teste:

```bash
# Health check
curl https://dreadbot-d4xc.onrender.com/health

# Limpar registro
curl -X POST https://dreadbot-d4xc.onrender.com/clear

# Ver estatísticas
curl https://dreadbot-d4xc.onrender.com/stats
```

## 🎯 Recomendação Final

**Melhor abordagem:**
1. Atualize o servidor no Render (Solução 1)
2. Aguarde 2-5 minutos
3. Limpe o registro: `curl -X POST https://dreadbot-d4xc.onrender.com/clear`
4. Gere chave nova: `python keygen.py 30 teste`
5. Teste no cliente

**Solução rápida (se não pode esperar):**
1. Limpe `license.registry` local
2. Gere chave nova
3. Teste
4. Depois atualize o servidor

