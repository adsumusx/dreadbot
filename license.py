#!/usr/bin/env python3
"""
Sistema de Licenciamento para o Bot DreadmystDB
"""

import os
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from pathlib import Path
import base64
import platform
import uuid
import urllib.request
import urllib.parse
import urllib.error

# Chave secreta para assinar as licenças (NUNCA compartilhe esta chave!)
# Em produção, esta chave deve ser diferente e mais segura
LICENSE_SECRET_KEY = b"dreadmyst_bot_secret_key_2024_secure_v1"

# URL do servidor de validação
# Servidor em produção: https://dreadbot-d4xc.onrender.com
# Para desabilitar temporariamente, use: None ou ""
LICENSE_SERVER_URL = os.environ.get("LICENSE_SERVER_URL", "https://dreadbot-d4xc.onrender.com/validate")

# Timeout para requisições ao servidor (segundos)
LICENSE_SERVER_TIMEOUT = 10

# Nome do arquivo de licença
LICENSE_FILE = "license.key"
# Arquivo que armazena o vínculo chave-máquina
LICENSE_LOCK_FILE = "license.lock"
# Arquivo que armazena registro global de chaves ativadas (hash da chave original -> machine_id)
LICENSE_REGISTRY_FILE = "license.registry"


class LicenseManager:
    """Gerenciador de licenças"""
    
    def __init__(self, license_file: str = LICENSE_FILE, server_url: str = None):
        self.license_file = license_file
        self.license_data = None
        self.lock_file = LICENSE_LOCK_FILE
        self.registry_file = LICENSE_REGISTRY_FILE
        self.server_url = server_url or LICENSE_SERVER_URL
    
    def get_machine_id(self) -> str:
        """
        Gera um ID único para a máquina atual
        
        Returns:
            String com ID único da máquina
        """
        # Combina várias informações do sistema para criar um ID único
        machine_info = {
            'node': platform.node(),  # Nome do computador
            'processor': platform.processor(),
            'system': platform.system(),
            'machine': platform.machine(),
            'mac': str(uuid.getnode()),  # MAC address
        }
        
        # Cria hash das informações
        machine_str = json.dumps(machine_info, sort_keys=True)
        machine_id = hashlib.sha256(machine_str.encode('utf-8')).hexdigest()
        
        return machine_id
    
    def get_license_hash(self, license_key: str) -> str:
        """
        Gera hash da chave de licença para identificação única
        
        Returns:
            Hash SHA256 da chave
        """
        return hashlib.sha256(license_key.encode('utf-8')).hexdigest()
    
    def get_original_license_hash(self, license_key: str) -> str:
        """
        Gera hash da chave ORIGINAL (antes da ativação) para rastreamento
        
        Isso permite rastrear se uma chave já foi ativada, mesmo que
        a chave tenha sido modificada com machine_id.
        
        Returns:
            Hash SHA256 da chave original
        """
        try:
            # Decodifica a chave
            full_json = base64.b64decode(license_key.encode('utf-8')).decode('utf-8')
            full_data = json.loads(full_json)
            license_data = full_data.get("data", {})
            
            # Remove campos de ativação para obter a chave original
            original_data = {k: v for k, v in license_data.items() 
                           if k not in ['activated_machine_id', 'activation_date']}
            
            # Recria a estrutura original (com assinatura original)
            # Mas precisamos recriar a assinatura também para ter a chave original completa
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
            
            # Recodifica para obter a chave original
            original_json_str = json.dumps(original_full_data, sort_keys=True)
            original_key = base64.b64encode(original_json_str.encode('utf-8')).decode('utf-8')
            
            # Retorna hash da chave original
            return hashlib.sha256(original_key.encode('utf-8')).hexdigest()
        except:
            # Se falhar, retorna hash da chave atual
            return hashlib.sha256(license_key.encode('utf-8')).hexdigest()
    
    def load_license_registry(self) -> dict:
        """
        Carrega o registro global de chaves ativadas
        
        Returns:
            Dicionário com {original_hash: machine_id}
        """
        registry_path = Path(self.registry_file)
        if not registry_path.exists():
            return {}
        
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def save_license_registry(self, original_hash: str, machine_id: str) -> bool:
        """
        Salva uma chave ativada no registro global (local e servidor)
        
        Returns:
            True se salvou com sucesso
        """
        try:
            # Salva localmente
            registry = self.load_license_registry()
            registry[original_hash] = machine_id
            
            registry_path = Path(self.registry_file)
            with open(registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2)
            
            # Tenta registrar no servidor online (já foi feito em validate_license_key)
            # Mas mantemos aqui como fallback
            
            return True
        except Exception as e:
            print(f"Erro ao salvar registro: {e}")
            return False
    
    def check_license_online(self, license_key: str, machine_id: str, action: str = 'check'):
        """
        Verifica/ativa licença no servidor online
        
        Args:
            license_key: Chave de licença
            machine_id: ID da máquina
            action: 'check' para verificar, 'activate' para ativar
        
        Returns:
            (is_valid, message) ou None se servidor não disponível
        """
        # Se a URL do servidor não estiver configurada, retorna None (fallback local)
        if not self.server_url or self.server_url == "None" or self.server_url == "":
            return None
        
        try:
            data = {
                'license_key': license_key,
                'machine_id': machine_id,
                'action': action
            }
            
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                self.server_url,
                data=json_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=LICENSE_SERVER_TIMEOUT) as response:
                result = json.loads(response.read().decode('utf-8'))
                is_valid = result.get('valid', False)
                message = result.get('message', 'Erro desconhecido')
                
                # Log para debug (pode remover depois)
                if not is_valid:
                    print(f"[DEBUG] Servidor retornou inválido: {message}")
                
                return is_valid, message
        
        except urllib.error.URLError as e:
            # Servidor não disponível - retorna None para usar fallback local
            print(f"[DEBUG] Servidor não disponível: {e}")
            return None
        except Exception as e:
            print(f"[DEBUG] Erro ao verificar licença online: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_license_lock(self) -> dict:
        """
        Carrega o arquivo de lock que vincula chave à máquina
        
        Returns:
            Dicionário com {license_hash: machine_id} ou {} se não existir
        """
        lock_path = Path(self.lock_file)
        if not lock_path.exists():
            return {}
        
        try:
            with open(lock_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def save_license_lock(self, license_hash: str, machine_id: str) -> bool:
        """
        Salva o vínculo chave-máquina no arquivo de lock
        
        Returns:
            True se salvou com sucesso
        """
        try:
            # Carrega locks existentes e adiciona/atualiza o novo
            lock_data = self.load_license_lock()
            lock_data[license_hash] = machine_id
            lock_path = Path(self.lock_file)
            with open(lock_path, 'w', encoding='utf-8') as f:
                json.dump(lock_data, f)
            return True
        except Exception as e:
            print(f"Erro ao salvar lock: {e}")
            return False
    
    def generate_license_key(self, days: int, customer_id: str = "default") -> str:
        """
        Gera uma chave de licença válida por N dias
        
        Args:
            days: Número de dias de validade
            customer_id: ID do cliente (opcional)
        
        Returns:
            Chave de licença codificada em base64
        """
        # Data de expiração
        expiration_date = datetime.now() + timedelta(days=days)
        expiration_str = expiration_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Dados da licença
        license_data = {
            "customer_id": customer_id,
            "expiration_date": expiration_str,
            "days": days,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Converte para JSON
        license_json = json.dumps(license_data, sort_keys=True)
        
        # Cria assinatura HMAC
        signature = hmac.new(
            LICENSE_SECRET_KEY,
            license_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Combina dados + assinatura
        full_data = {
            "data": license_data,
            "signature": signature
        }
        
        # Codifica em base64
        full_json = json.dumps(full_data, sort_keys=True)
        license_key = base64.b64encode(full_json.encode('utf-8')).decode('utf-8')
        
        return license_key
    
    def validate_license_key(self, license_key: str, return_activated_key: bool = False):
        """
        Valida uma chave de licença e verifica se já foi usada
        
        Args:
            license_key: Chave de licença a validar
            return_activated_key: Se True, retorna também a chave ativada (se foi ativada)
        
        Returns:
            (is_valid, message) ou (is_valid, message, activated_key) se return_activated_key=True
        """
        try:
            # Decodifica base64
            full_json = base64.b64decode(license_key.encode('utf-8')).decode('utf-8')
            full_data = json.loads(full_json)
            
            # Extrai dados e assinatura
            license_data = full_data.get("data")
            signature = full_data.get("signature")
            
            if not license_data or not signature:
                return (False, "Formato de licença inválido") if not return_activated_key else (False, "Formato de licença inválido", None)
            
            # Verifica se a chave já foi ativada (tem machine_id incorporado)
            activated_machine_id = license_data.get('activated_machine_id')
            activated_license_key = None
            
            # Se já foi ativada, verifica assinatura com dados completos
            # Se não foi ativada, verifica assinatura original (sem machine_id)
            if activated_machine_id:
                # Chave já ativada - verifica assinatura com dados completos
                license_json = json.dumps(license_data, sort_keys=True)
                expected_signature = hmac.new(
                    LICENSE_SECRET_KEY,
                    license_json.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
            else:
                # Chave não ativada - verifica assinatura original (sem campos de ativação)
                original_data = {k: v for k, v in license_data.items() 
                                if k not in ['activated_machine_id', 'activation_date']}
                license_json = json.dumps(original_data, sort_keys=True)
                expected_signature = hmac.new(
                    LICENSE_SECRET_KEY,
                    license_json.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
            
            # Verifica assinatura
            if not hmac.compare_digest(signature, expected_signature):
                return (False, "Licença inválida ou corrompida") if not return_activated_key else (False, "Licença inválida ou corrompida", None)
            
            # Verifica data de expiração
            expiration_str = license_data.get("expiration_date")
            if not expiration_str:
                return (False, "Data de expiração não encontrada") if not return_activated_key else (False, "Data de expiração não encontrada", None)
            
            expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            
            if now > expiration_date:
                days_expired = (now - expiration_date).days
                return (False, f"Licença expirada há {days_expired} dia(s)") if not return_activated_key else (False, f"Licença expirada há {days_expired} dia(s)", None)
            
            # Verifica se a chave já foi ativada em outra máquina
            current_machine_id = self.get_machine_id()
            
            # Obtém hash da chave ORIGINAL (antes da ativação) para verificar no registro
            original_hash = self.get_original_license_hash(license_key)
            
            # Verifica no servidor online PRIMEIRO (mais seguro)
            online_result = self.check_license_online(license_key, current_machine_id, 'check')
            
            if online_result is not None:
                # Servidor online disponível - usa validação online
                is_valid_online, message_online = online_result
                # Se o servidor diz que já foi ativada, verifica se é na mesma máquina
                if not is_valid_online:
                    # Verifica se a mensagem indica que já foi ativada em OUTRA máquina
                    if "outra máquina" in message_online.lower() or "another machine" in message_online.lower():
                        # Já foi ativada em outra máquina - rejeita imediatamente
                        return (False, message_online) if not return_activated_key else (False, message_online, None)
                    elif "já foi ativada" in message_online.lower() or "already_activated" in message_online.lower():
                        # Pode ser a mesma máquina tentando reativar - permite continuar
                        # O servidor vai verificar novamente na ativação
                        pass
                    else:
                        # Outro tipo de erro - retorna
                        return (False, message_online) if not return_activated_key else (False, message_online, None)
            
            # Verifica no registro local também (fallback)
            registry = self.load_license_registry()
            
            if activated_machine_id:
                # Chave já foi ativada - verifica se é na mesma máquina
                if activated_machine_id != current_machine_id:
                    error_msg = "Esta licença já foi ativada em outra máquina. Cada licença só pode ser usada uma vez."
                    return (False, error_msg) if not return_activated_key else (False, error_msg, None)
                
                # Verifica também no registro local (segurança extra)
                if original_hash in registry:
                    registered_machine_id = registry[original_hash]
                    if registered_machine_id != current_machine_id:
                        error_msg = "Esta licença já foi registrada para outra máquina. Cada licença só pode ser usada uma vez."
                        return (False, error_msg) if not return_activated_key else (False, error_msg, None)
                
                # Mesma máquina, mesma chave - OK
                activated_license_key = license_key  # Já está ativada
            else:
                # Primeira vez usando esta chave - VERIFICA NO REGISTRO E SERVIDOR
                # Verifica servidor online primeiro
                if online_result is None:
                    # Servidor offline - verifica registro local
                    if original_hash in registry:
                        registered_machine_id = registry[original_hash]
                        if registered_machine_id != current_machine_id:
                            error_msg = "Esta licença já foi ativada em outra máquina. Cada licença só pode ser usada uma vez."
                            return (False, error_msg) if not return_activated_key else (False, error_msg, None)
                else:
                    # Servidor online já validou - continua
                    pass
                
                # Chave não foi ativada ainda - ativa vinculando ao machine_id
                license_data['activated_machine_id'] = current_machine_id
                license_data['activation_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Recria a assinatura com os novos dados
                license_json = json.dumps(license_data, sort_keys=True)
                new_signature = hmac.new(
                    LICENSE_SECRET_KEY,
                    license_json.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                
                # Atualiza os dados completos
                full_data = {
                    "data": license_data,
                    "signature": new_signature
                }
                
                # Recodifica a chave com o machine_id incorporado
                full_json = json.dumps(full_data, sort_keys=True)
                activated_license_key = base64.b64encode(full_json.encode('utf-8')).decode('utf-8')
                
                # REGISTRA a chave no servidor online PRIMEIRO
                online_activate = self.check_license_online(license_key, current_machine_id, 'activate')
                if online_activate is not None:
                    is_valid_online, message_online = online_activate
                    if not is_valid_online:
                        # Se o servidor rejeitar, retorna o erro
                        # Mas verifica se é realmente outra máquina ou erro de servidor
                        error_msg = message_online
                        # Se a mensagem indica que já foi ativada em outra máquina, rejeita
                        if "outra máquina" in message_online.lower() or "another machine" in message_online.lower():
                            return (False, error_msg) if not return_activated_key else (False, error_msg, None)
                        # Outros erros também rejeitam
                        return (False, error_msg) if not return_activated_key else (False, error_msg, None)
                
                # REGISTRA a chave no registro local também (fallback)
                if not self.save_license_registry(original_hash, current_machine_id):
                    error_msg = "Erro ao registrar licença no sistema"
                    return (False, error_msg) if not return_activated_key else (False, error_msg, None)
                
                # Salva a chave ativada de volta no arquivo IMEDIATAMENTE
                try:
                    license_path = Path(self.license_file)
                    with open(license_path, 'w', encoding='utf-8') as f:
                        f.write(activated_license_key)
                except Exception as e:
                    error_msg = f"Erro ao ativar licença: {str(e)}"
                    return (False, error_msg) if not return_activated_key else (False, error_msg, None)
            
            # Licença válida
            days_left = (expiration_date - now).days
            self.license_data = license_data
            
            if return_activated_key:
                return True, f"Licença válida. {days_left} dia(s) restante(s)", activated_license_key
            else:
                return True, f"Licença válida. {days_left} dia(s) restante(s)"
            
        except Exception as e:
            error_msg = f"Erro ao validar licença: {str(e)}"
            return (False, error_msg) if not return_activated_key else (False, error_msg, None)
    
    def load_license(self):
        """
        Carrega e valida a licença do arquivo
        
        Returns:
            (is_valid, message)
        """
        license_path = Path(self.license_file)
        
        if not license_path.exists():
            return False, "Arquivo de licença não encontrado"
        
        try:
            with open(license_path, 'r', encoding='utf-8') as f:
                license_key = f.read().strip()
            
            # Valida e se foi ativada, salva a versão ativada de volta
            result = self.validate_license_key(license_key, return_activated_key=True)
            
            if len(result) == 3:
                is_valid, message, activated_key = result
                # Se foi ativada e é válida, salva a versão ativada
                if is_valid and activated_key and activated_key != license_key:
                    try:
                        with open(license_path, 'w', encoding='utf-8') as f:
                            f.write(activated_key)
                    except:
                        pass  # Se não conseguir salvar, continua com a validação
                return is_valid, message
            else:
                return result
            
        except Exception as e:
            return False, f"Erro ao ler licença: {str(e)}"
    
    def save_license(self, license_key: str, skip_validation: bool = False) -> bool:
        """
        Salva a chave de licença no arquivo
        
        Args:
            license_key: Chave de licença a ser salva
            skip_validation: Se True, não valida antes de salvar (NÃO recomendado - sempre valida para garantir lock)
        
        Returns:
            True se salvou com sucesso
        """
        try:
            # SEMPRE valida antes de salvar para garantir que o lock seja criado
            # Retorna a chave ativada se foi ativada
            result = self.validate_license_key(license_key, return_activated_key=True)
            
            if len(result) == 3:
                is_valid, message, activated_key = result
            else:
                is_valid, message = result
                activated_key = None
            
            # Se válida e foi ativada, salva a versão ativada
            # Se inválida, salva a original para mostrar erro na GUI
            key_to_save = activated_key if (is_valid and activated_key) else license_key
            
            license_path = Path(self.license_file)
            with open(license_path, 'w', encoding='utf-8') as f:
                f.write(key_to_save)
            
            # Se válida, o lock já foi criado em validate_license_key
            return True
        except Exception as e:
            print(f"Erro ao salvar licença: {e}")
            return False
    
    def get_license_info(self) -> dict:
        """
        Retorna informações da licença atual
        
        Returns:
            Dicionário com informações da licença ou None
        """
        if self.license_data:
            return self.license_data.copy()
        return None
    
    def is_license_valid(self) -> bool:
        """
        Verifica rapidamente se a licença é válida
        
        Returns:
            True se válida, False caso contrário
        """
        is_valid, _ = self.load_license()
        return is_valid

