#!/usr/bin/env python3
"""
Gerador de Chaves de Licença para o Bot DreadmystDB
Uso: python keygen.py <dias> [customer_id]
"""

import sys
from license import LicenseManager
from datetime import datetime


def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("Gerador de Chaves de Licença - Bot DreadmystDB")
        print("=" * 60)
        print("\nUso:")
        print("  python keygen.py <dias> [customer_id]")
        print("\nExemplos:")
        print("  python keygen.py 30              # Licença de 30 dias")
        print("  python keygen.py 90 cliente123    # Licença de 90 dias para cliente123")
        print("  python keygen.py 365              # Licença de 1 ano")
        print("\nA chave será salva em 'license.key'")
        print("=" * 60)
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        customer_id = sys.argv[2] if len(sys.argv) > 2 else "default"
        
        if days <= 0:
            print("❌ Erro: O número de dias deve ser maior que 0")
            sys.exit(1)
        
        print(f"\n🔑 Gerando licença de {days} dia(s) para cliente: {customer_id}")
        
        manager = LicenseManager()
        license_key = manager.generate_license_key(days, customer_id)
        
        # Valida a chave gerada
        is_valid, message = manager.validate_license_key(license_key)
        
        if not is_valid:
            print(f"❌ Erro ao validar chave gerada: {message}")
            sys.exit(1)
        
        # Salva a chave
        if manager.save_license(license_key):
            print(f"✅ Licença gerada e salva em 'license.key'")
            print(f"📋 Status: {message}")
            
            # Mostra informações
            info = manager.get_license_info()
            if info:
                print(f"\n📊 Informações da Licença:")
                print(f"   Cliente: {info.get('customer_id')}")
                print(f"   Criada em: {info.get('created_date')}")
                print(f"   Expira em: {info.get('expiration_date')}")
                print(f"   Válida por: {info.get('days')} dia(s)")
            
            print(f"\n🔑 Chave de Licença:")
            print("-" * 60)
            print(license_key)
            print("-" * 60)
            print("\n💡 Dica: Envie esta chave para o cliente.")
            print("   O cliente deve salvá-la em um arquivo 'license.key'")
            print("   no mesmo diretório do executável.")
        else:
            print("❌ Erro ao salvar licença")
            sys.exit(1)
            
    except ValueError:
        print(f"❌ Erro: '{sys.argv[1]}' não é um número válido")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

