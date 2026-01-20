#!/usr/bin/env python3
"""
Exemplo de uso do bot de monitoramento
"""

from bot import TradeMonitor

# Exemplo 1: Monitorar itens Holy/Godly nível 24+ com STR e INT
config1 = {
    "quality": [5, 6],
    "min_level": 24,
    "stats": ["STR", "INT"],
    "slots": [],
    "check_interval": 30,
    "alert_method": "console"
}

# Exemplo 2: Monitorar apenas escudos com resistências
config2 = {
    "quality": [5, 6],
    "slots": ["off hand"],
    "stats": ["Fire Res", "Frost Res"],
    "check_interval": 20,
    "alert_method": "both"
}

# Exemplo 3: Monitorar itens de peito com STR e COU, preço máximo 100k
config3 = {
    "quality": [5, 6],
    "slots": ["chest"],
    "stats": ["STR", "COU"],
    "max_price": 100000,
    "check_interval": 30,
    "alert_method": "console"
}

if __name__ == '__main__':
    import json
    
    # Salva uma das configurações como exemplo
    with open('config.exemplo.json', 'w', encoding='utf-8') as f:
        json.dump(config1, f, indent=2, ensure_ascii=False)
    
    print("Configuração de exemplo criada em config.exemplo.json")
    print("\nPara usar:")
    print("1. Copie config.exemplo.json para config.json")
    print("2. Edite config.json com seus filtros desejados")
    print("3. Execute: python bot.py")

