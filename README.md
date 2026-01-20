# Bot de Monitoramento DreadmystDB Trade

Bot Python que monitora a página de trade do DreadmystDB e alerta quando encontrar itens que correspondam aos seus filtros configurados.

## 🚀 Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

Edite o arquivo `config.json` para configurar seus filtros:

```json
{
  "quality": [5, 6],           // Qualidades: 1=Junk, 2=Normal, 3=Radiant, 4=Blessed, 5=Holy, 6=Godly
  "min_level": 24,              // Nível mínimo do item
  "max_level": null,            // Nível máximo (null = sem limite)
  "min_price": null,            // Preço mínimo em gold
  "max_price": null,            // Preço máximo em gold
  "stats": ["STR", "INT"],      // Lista de atributos desejados (ex: ["STR", "INT", "COU", "Fire Res"])
  "slots": ["chest", "hands"],  // Lista de slots desejados (ex: ["head", "chest", "hands", "ring"])
  "check_interval": 30,         // Intervalo entre verificações em segundos
  "alert_method": "console",    // Método de alerta: "console", "file", ou "both"
  "log_file": "alerts.log"      // Arquivo de log (se alert_method incluir "file")
}
```

### Slots Disponíveis:
- `head` - Cabeça
- `necklace` - Colar
- `chest` - Peito
- `waist` - Cintura
- `legs` - Pernas
- `feet` - Pés
- `hands` - Mãos
- `ring` - Anel
- `main hand` - Mão principal
- `off hand` - Mão secundária
- `ranged` - Arco/Arma à distância

### Atributos Disponíveis:
- `STR` - Strength
- `INT` - Intelligence
- `AGI` - Agility
- `WIL` - Willpower
- `COU` - Courage
- `HP` - Health
- `Mana` - Mana
- `Fire Res` - Resist Fire
- `Frost Res` - Resist Frost
- `Holy Res` - Resist Holy
- `Shadow Res` - Resist Shadow
- `Wpn Dmg` - Weapon Value
- `Shields` - Shields
- `Spell Crit` - Spell Critical
- `Melee Crit` - Melee Critical
- `Meditate` - Meditate
- E muitos outros...

## 📖 Uso

### Primeira execução:

1. O arquivo `config.json` será criado automaticamente na primeira execução
2. Edite o `config.json` com seus filtros desejados
3. Execute o bot:

```bash
python bot.py
```

### Com arquivo de configuração customizado:

```bash
python bot.py -c minha_config.json
```

### O que o bot faz:

1. Faz requisições periódicas para a página de trade do DreadmystDB
2. Analisa todos os itens retornados
3. Verifica se novos itens correspondem aos seus filtros (stats e slots)
4. Alerta quando encontrar itens que correspondam
5. Evita alertas duplicados para o mesmo item

### Exemplo de saída:

```
🤖 Bot de Monitoramento DreadmystDB iniciado!
📋 Configuração carregada: {...}
🔗 URL monitorada: https://dreadmystdb.com/trade?...
⏱️  Intervalo de verificação: 30 segundos

============================================================
Aguardando novos itens...
============================================================

[14:30:15] Verificando 20 itens...

============================================================
🎯 ITEM ENCONTRADO! 🎯
============================================================
Nome: Holy Breastplate of the Dispatching Lion
Slot: chest
Item Level: 25
Stats: +9 Wpn Dmg, +58 STR, +58 COU
Preço: 1,800,000g
Vendedor: huge9991
Tempo restante: about 24 hours left
URL: https://dreadmystdb.com/trade/13158
============================================================
```

## 🔔 Alertas

Quando um item correspondente aos filtros for encontrado, você receberá um alerta com:
- Nome do item
- Slot do equipamento
- Item Level
- Estatísticas
- Preço
- Vendedor
- Tempo restante
- URL do item

## 📝 Exemplos de Configuração

### Buscar itens Holy/Godly nível 24+ com STR e INT:
```json
{
  "quality": [5, 6],
  "min_level": 24,
  "stats": ["STR", "INT"],
  "slots": [],
  "check_interval": 30
}
```

### Buscar apenas escudos (off hand) com resistências:
```json
{
  "quality": [5, 6],
  "slots": ["off hand"],
  "stats": ["Fire Res", "Frost Res", "Shadow Res"],
  "check_interval": 20
}
```

### Buscar itens de peito com STR e COU, preço máximo 100k:
```json
{
  "quality": [5, 6],
  "slots": ["chest"],
  "stats": ["STR", "COU"],
  "max_price": 100000,
  "check_interval": 30
}
```

## ⚠️ Notas

- O bot evita alertas duplicados para o mesmo item
- O intervalo de verificação padrão é 30 segundos (ajuste conforme necessário)
- O bot mantém um registro dos itens já vistos para evitar spam
- Use intervalos razoáveis para não sobrecarregar o servidor

## 🐛 Troubleshooting

Se o bot não encontrar itens:
1. Verifique se os filtros não estão muito restritivos
2. Verifique se a conexão com a internet está funcionando
3. Verifique se os nomes dos stats/slots estão corretos no config.json
4. Tente executar sem filtros primeiro para ver se está funcionando

