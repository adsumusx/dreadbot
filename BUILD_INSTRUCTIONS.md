# 📦 Instruções de Build - Bot DreadmystDB

Este guia explica como gerar o executável (.exe) do bot e criar licenças para distribuição.

## 🚀 Pré-requisitos

1. **Python 3.7+** instalado
2. **Todas as dependências** instaladas:
   ```bash
   pip install -r requirements.txt
   ```

## 🔨 Gerar o Executável

### Método 1: Usando o script build.py (Recomendado)

```bash
python build.py
```

Isso irá:
- Verificar se PyInstaller está instalado
- Instalar PyInstaller se necessário
- Gerar o executável `DreadmystBot.exe` na pasta `dist/`

### Método 2: Comando manual

```bash
pyinstaller --onefile --windowed --name DreadmystBot --clean bot_gui.py
```

### Limpar arquivos temporários após o build

```bash
python build.py --clean
```

Ou manualmente:
```bash
rmdir /s /q build __pycache__
del DreadmystBot.spec
```

## 🔑 Gerar Licenças

### Gerar uma licença de 30 dias

```bash
python keygen.py 30
```

### Gerar uma licença de 90 dias para um cliente específico

```bash
python keygen.py 90 cliente123
```

### Gerar uma licença de 1 ano

```bash
python keygen.py 365
```

A chave será:
- Salva automaticamente em `license.key`
- Exibida no terminal
- Validada antes de ser salva

## 📋 Estrutura de Distribuição

Quando distribuir o software para clientes, você precisa fornecer:

1. **DreadmystBot.exe** - O executável principal
2. **license.key** - A chave de licença gerada para o cliente

### Estrutura de pastas recomendada:

```
DreadmystBot/
├── DreadmystBot.exe
└── license.key
```

## 🔐 Sistema de Licenciamento

### Como funciona:

1. **Geração de Licença**: Use `keygen.py` para gerar chaves com data de expiração
2. **Validação**: O executável valida a licença na inicialização
3. **Armazenamento**: A licença é salva em `license.key` no mesmo diretório do .exe
4. **Expiração**: Após a data de expiração, o software não funciona mais
5. **Uso Único**: Cada chave só pode ser usada em **uma única máquina**. Quando uma chave é ativada pela primeira vez, ela fica vinculada ao ID único da máquina. Tentar usar a mesma chave em outra máquina resultará em erro.

### Segurança:

- As licenças são assinadas com HMAC-SHA256
- Não podem ser modificadas sem invalidar a assinatura
- A chave secreta está no código (em produção, considere usar um servidor de validação)

### ⚠️ IMPORTANTE:

- **NUNCA compartilhe** a chave secreta (`LICENSE_SECRET_KEY` em `license.py`)
- Mantenha `keygen.py` e `license.py` privados
- Distribua apenas o executável e as licenças geradas

## 🧪 Testar o Executável

1. Gere uma licença de teste:
   ```bash
   python keygen.py 1
   ```

2. Execute o executável:
   ```bash
   dist\DreadmystBot.exe
   ```

3. Verifique se:
   - A interface abre normalmente
   - Não há erros de licença
   - O bot funciona corretamente

## 📝 Notas Adicionais

### Tamanho do Executável

O executável gerado será relativamente grande (30-50 MB) porque inclui:
- Python runtime
- Todas as bibliotecas necessárias
- Código do bot

### Antivírus

Alguns antivírus podem marcar executáveis gerados com PyInstaller como suspeitos. Isso é um falso positivo comum. Considere:
- Assinar o executável com um certificado digital
- Adicionar o executável à whitelist do antivírus
- Informar os clientes sobre isso

### Atualizações

Para atualizar o bot:
1. Modifique o código
2. Regenere o executável com `build.py`
3. Distribua a nova versão

As licenças antigas continuarão funcionando, desde que não estejam expiradas.

## 🆘 Solução de Problemas

### Erro: "PyInstaller não encontrado"
```bash
pip install pyinstaller
```

### Erro: "license.key não encontrado"
- Gere uma licença com `keygen.py`
- Coloque o arquivo `license.key` no mesmo diretório do executável

### Erro: "Licença expirada"
- Gere uma nova licença com `keygen.py`
- Substitua o arquivo `license.key` antigo

### Executável não abre
- Verifique se há mensagens de erro no terminal (se executar via linha de comando)
- Verifique se o arquivo `license.key` existe e é válido
- Teste executando o Python diretamente: `python bot_gui.py`

