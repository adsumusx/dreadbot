#!/usr/bin/env python3
"""
Script de teste para verificar se o bot está funcionando corretamente
"""

from bot import TradeMonitor
import json

# Carrega a configuração
monitor = TradeMonitor("config.json")

print("="*60)
print("TESTE DE DETECÇÃO")
print("="*60)

# Testa a detecção de slots
print("\n1. Testando detecção de slots:")
test_items = [
    "Holy Breastplate of the Lion",
    "Godly Hood of the Eagle",
    "Holy Handwraps of the Squid",
    "Holy Coif of the Bear"
]

for item_name in test_items:
    slot = monitor.detect_slot(item_name)
    print(f"  {item_name} -> Slot: {slot}")

# Testa normalização de slots
print("\n2. Testando normalização de slots:")
test_slots = ["Helmet", "Head", "chest", "Hands", "off hand"]
for slot in test_slots:
    normalized = monitor.normalize_slot_name(slot)
    print(f"  '{slot}' -> '{normalized}'")

# Testa normalização de stats
print("\n3. Testando normalização de stats:")
test_stats = ["AGI", "agi", "Agility", "STR", "str", "Strength"]
for stat in test_stats:
    normalized = monitor.normalize_stat(stat)
    print(f"  '{stat}' -> '{normalized}'")

# Testa matching de stats
print("\n4. Testando matching de stats:")
from bot import Item

test_item = Item(
    listing_id="12345",
    name="Holy Breastplate of the Lion",
    item_level="25",
    stats=["+58 STR", "+44 AGI", "+30 COU"],
    price="100,000g",
    seller="testuser",
    time_left="24 hours",
    url="https://dreadmystdb.com/trade/12345",
    slot="chest"
)

print(f"\nItem de teste: {test_item.name}")
print(f"Stats: {test_item.stats}")
print(f"Slot: {test_item.slot}")

# Testa com diferentes configurações
test_configs = [
    {"stats": ["AGI"], "slots": ["chest"]},
    {"stats": ["STR"], "slots": ["chest"]},
    {"stats": ["INT"], "slots": ["chest"]},
    {"stats": ["AGI"], "slots": ["hands"]},
]

for test_config in test_configs:
    monitor.config.update(test_config)
    matches = monitor.item_matches_filters(test_item, debug=True)
    print(f"\nConfig: {test_config}")
    print(f"Resultado: {'✓ MATCH' if matches else '✗ NO MATCH'}")

print("\n" + "="*60)
print("Teste concluído!")
print("="*60)

