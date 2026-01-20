#!/usr/bin/env python3
"""
Script de teste para verificar se uma chave está sendo validada corretamente
"""

import sys
from license import LicenseManager

def test_license(license_key: str):
    """Testa uma chave de licença"""
    print("=" * 60)
    print("Teste de Validação de Licença")
    print("=" * 60)
    print(f"\nChave: {license_key[:50]}...")
    
    manager = LicenseManager()
    
    # Testa validação
    print("\n1. Validando chave...")
    result = manager.validate_license_key(license_key, return_activated_key=True)
    
    if len(result) == 3:
        is_valid, message, activated_key = result
    else:
        is_valid, message = result
        activated_key = None
    
    print(f"   Válida: {is_valid}")
    print(f"   Mensagem: {message}")
    
    if activated_key and activated_key != license_key:
        print(f"   ✓ Chave foi ativada e modificada")
    
    # Testa hash original
    print("\n2. Calculando hash original...")
    original_hash = manager.get_original_license_hash(license_key)
    print(f"   Hash: {original_hash[:32]}...")
    
    # Testa servidor online
    print("\n3. Testando servidor online...")
    machine_id = manager.get_machine_id()
    print(f"   Machine ID: {machine_id[:32]}...")
    
    online_result = manager.check_license_online(license_key, machine_id, 'check')
    if online_result is not None:
        is_valid_online, message_online = online_result
        print(f"   Servidor disponível: Sim")
        print(f"   Válida no servidor: {is_valid_online}")
        print(f"   Mensagem do servidor: {message_online}")
    else:
        print(f"   Servidor disponível: Não (offline ou erro)")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python test_license.py <chave_de_licença>")
        print("\nOu leia de um arquivo:")
        print("  python test_license.py --file license.key")
        sys.exit(1)
    
    if sys.argv[1] == '--file':
        # Lê de arquivo
        try:
            with open('license.key', 'r', encoding='utf-8') as f:
                license_key = f.read().strip()
        except FileNotFoundError:
            print("Erro: Arquivo license.key não encontrado")
            sys.exit(1)
    else:
        license_key = sys.argv[1]
    
    test_license(license_key)

