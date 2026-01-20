# Bot DreadmystDB - Interface Gráfica

Interface gráfica amigável para o bot de monitoramento do DreadmystDB.

## 🚀 Como Usar

### Executar a Interface Gráfica:

```bash
python bot_gui.py
```

### Ou executar o bot via linha de comando (modo original):

```bash
python bot.py
```

## 📋 Funcionalidades da Interface

### ✅ Configuração Visual

- **Qualidade do Item**: Selecione as qualidades desejadas (Junk, Normal, Radiant, Blessed, Holy, Godly)
- **Nível**: Defina nível mínimo e máximo (1-25)
- **Preço**: Defina preço mínimo e máximo em gold
- **Atributos**: Selecione os atributos desejados (STR, INT, AGI, etc.) ou adicione customizados
- **Slots**: Selecione os slots de equipamento desejados
- **Intervalo**: Defina quantos segundos entre cada verificação
- **Modo de Filtro**: 
  - **AND**: Item deve ter o slot E o atributo
  - **OR**: Item deve ter o slot OU o atributo

### 🔊 Alertas Sonoros

Quando um item correspondente aos filtros for encontrado:
- **Som de alerta** (se ativado)
- **Popup visual** com informações do item
- **Log na interface** com detalhes

### 💾 Salvar/Carregar Configuração

- **Salvar**: Salva a configuração atual no arquivo `config.json`
- **Carregar**: Carrega a última configuração salva

## 🎯 Exemplo de Uso

1. Abra a interface: `python bot_gui.py`
2. Configure seus filtros:
   - Marque "Godly" em Qualidade
   - Defina Nível mínimo: 24
   - Marque "AGI" em Atributos
   - Marque "chest", "hands", "head" em Slots
   - Ative "Alerta Sonoro"
3. Clique em "▶ Iniciar Monitoramento"
4. O bot começará a verificar periodicamente
5. Quando encontrar um item, você receberá:
   - Alerta sonoro
   - Popup com informações
   - Log na interface

## ⚙️ Requisitos

- Python 3.6+
- tkinter (geralmente já vem com Python)
- Dependências do bot: `requests`, `beautifulsoup4`, `lxml`

Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🔧 Solução de Problemas

### Interface não abre
- Verifique se o tkinter está instalado: `python -m tkinter`
- No Linux, pode precisar instalar: `sudo apt-get install python3-tk`

### Som não funciona
- Windows: Deve funcionar automaticamente
- Linux: Pode precisar instalar `beep`: `sudo apt-get install beep`
- macOS: Deve funcionar automaticamente

### Bot não encontra itens
- Verifique se os filtros não estão muito restritivos
- Ative o modo debug no config.json para ver detalhes
- Verifique sua conexão com a internet

