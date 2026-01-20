#!/usr/bin/env python3
"""
Servidor de Validação de Licenças para o Bot DreadmystDB
Execute este servidor em um servidor web acessível pela internet
"""

from flask import Flask, request, jsonify
import json
import hashlib
import hmac
from datetime import datetime
import os

app = Flask(__name__)

# Chave secreta (DEVE SER A MESMA do license.py!)
LICENSE_SECRET_KEY = b"dreadmyst_bot_secret_key_2024_secure_v1"

# Arquivo para armazenar registros de ativação
REGISTRY_FILE = "license_registry.json"

def load_registry():
    """Carrega o registro de licenças ativadas"""
    if not os.path.exists(REGISTRY_FILE):
        return {}
    try:
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_registry(registry):
    """Salva o registro de licenças ativadas"""
    try:
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar registro: {e}")
        return False

def get_original_license_hash(license_key: str) -> str:
    """Gera hash da chave original (antes da ativação)"""
    try:
        import base64
        full_json = base64.b64decode(license_key.encode('utf-8')).decode('utf-8')
        full_data = json.loads(full_json)
        license_data = full_data.get("data", {})
        
        # Remove campos de ativação
        original_data = {k: v for k, v in license_data.items() 
                       if k not in ['activated_machine_id', 'activation_date']}
        
        # Recria assinatura original
        original_json = json.dumps(original_data, sort_keys=True)
        original_signature = hmac.new(
            LICENSE_SECRET_KEY,
            original_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        original_full_data = {
            "data": original_data,
            "signature": original_signature
        }
        
        original_json_str = json.dumps(original_full_data, sort_keys=True)
        original_key = base64.b64encode(original_json_str.encode('utf-8')).decode('utf-8')
        
        return hashlib.sha256(original_key.encode('utf-8')).hexdigest()
    except:
        return hashlib.sha256(license_key.encode('utf-8')).hexdigest()

@app.route('/validate', methods=['POST'])
def validate_license():
    """
    Valida uma licença e registra ativação
    
    Body JSON:
    {
        "license_key": "...",
        "machine_id": "...",
        "action": "check" ou "activate"
    }
    """
    try:
        data = request.get_json()
        license_key = data.get('license_key')
        machine_id = data.get('machine_id')
        action = data.get('action', 'check')  # 'check' ou 'activate'
        
        if not license_key or not machine_id:
            return jsonify({
                'valid': False,
                'message': 'Dados incompletos'
            }), 400
        
        # Obtém hash da chave original
        original_hash = get_original_license_hash(license_key)
        
        # Carrega registro
        registry = load_registry()
        
        if action == 'check':
            # Apenas verifica se já foi ativada
            if original_hash in registry:
                registered_machine_id = registry[original_hash]
                if registered_machine_id != machine_id:
                    return jsonify({
                        'valid': False,
                        'message': 'Esta licença já foi ativada em outra máquina. Cada licença só pode ser usada uma vez.',
                        'already_activated': True
                    }), 200
                else:
                    return jsonify({
                        'valid': True,
                        'message': 'Licença válida para esta máquina',
                        'already_activated': True
                    }), 200
            else:
                return jsonify({
                    'valid': True,
                    'message': 'Licença disponível para ativação',
                    'already_activated': False
                }), 200
        
        elif action == 'activate':
            # Tenta ativar a licença
            if original_hash in registry:
                registered_machine_id = registry[original_hash]
                if registered_machine_id != machine_id:
                    return jsonify({
                        'valid': False,
                        'message': 'Esta licença já foi ativada em outra máquina. Cada licença só pode ser usada uma vez.',
                        'already_activated': True
                    }), 200
            
            # Registra a ativação
            registry[original_hash] = machine_id
            registry[f"{original_hash}_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if save_registry(registry):
                return jsonify({
                    'valid': True,
                    'message': 'Licença ativada com sucesso',
                    'activated': True
                }), 200
            else:
                return jsonify({
                    'valid': False,
                    'message': 'Erro ao registrar ativação'
                }), 500
        
        else:
            return jsonify({
                'valid': False,
                'message': 'Ação inválida'
            }), 400
            
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': f'Erro no servidor: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # Configurações do servidor
    # Em produção, use um servidor WSGI como gunicorn ou uwsgi
    # e configure HTTPS!
    import os
    
    # Porta do ambiente (usado por serviços como Render, Railway, Heroku)
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("Servidor de Validação de Licenças - Bot DreadmystDB")
    print("=" * 60)
    print(f"\n📡 Servidor iniciado na porta {port}")
    print(f"   URL Local: http://localhost:{port}")
    
    # Detecta se está rodando em serviço cloud
    if os.environ.get('RENDER') or os.environ.get('RAILWAY_ENVIRONMENT'):
        print(f"   🌐 Servidor em nuvem - acesse via URL do serviço")
    else:
        print(f"   URL Externa: http://SEU_IP_PUBLICO:{port}")
        print("\n💡 Para expor na internet:")
        print("   1. Use ngrok: ngrok http 5000")
        print("   2. Configure port forwarding no roteador")
        print("   3. Use DNS dinâmico (No-IP, DuckDNS)")
        print("   4. Deploy em serviço gratuito (Render, Railway)")
    
    print("\n⚠ ATENÇÃO:")
    print("   - Configure o firewall para permitir a porta")
    print("   - Use HTTPS em produção")
    print("   - Para produção, use: gunicorn -w 4 -b 0.0.0.0:$PORT license_server:app")
    print("\n" + "=" * 60)
    print("Pressione Ctrl+C para parar o servidor")
    print("=" * 60)
    print("")
    
    # Para desenvolvimento/produção
    # host='0.0.0.0' permite acesso de outros computadores na rede
    app.run(host='0.0.0.0', port=port, debug=False)

