# 🖥️ Configuração do Servidor de Validação no Seu Computador

Este guia explica como rodar o servidor de validação no seu próprio computador e torná-lo acessível pela internet.

## 📋 Pré-requisitos

1. Python instalado no seu computador
2. Conexão com internet
3. Porta disponível (recomendado: 5000 ou 8080)

## 🚀 Passo 1: Instalar Dependências

```bash
pip install flask
```

## 🔧 Passo 2: Configurar o Servidor

O arquivo `license_server.py` já está pronto. Você só precisa executá-lo.

## 🌐 Passo 3: Expor o Servidor para a Internet

Você tem 3 opções principais:

### Opção 1: Usando ngrok (MAIS FÁCIL - Recomendado)

**ngrok** cria um túnel seguro para o seu servidor local.

1. **Baixe o ngrok:**
   - Acesse: https://ngrok.com/download
   - Baixe e extraia o arquivo

2. **Execute o servidor Flask:**
   ```bash
   python license_server.py
   ```
   O servidor ficará rodando em `http://localhost:5000`

3. **Em outro terminal, execute o ngrok:**
   ```bash
   ngrok http 5000
   ```

4. **Copie a URL HTTPS gerada:**
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:5000
   ```
   Use essa URL (ex: `https://abc123.ngrok.io/validate`) no cliente.

**⚠️ IMPORTANTE:** A URL do ngrok muda a cada vez que você reinicia. Para ter uma URL fixa, você precisa da versão paga do ngrok.

### Opção 2: Port Forwarding no Roteador (Mais Permanente)

1. **Descubra seu IP local:**
   - Windows: `ipconfig` (procure por "IPv4 Address")
   - Linux/Mac: `ifconfig` ou `ip addr`

2. **Descubra seu IP público:**
   - Acesse: https://whatismyipaddress.com
   - Anote o IP público

3. **Configure Port Forwarding no roteador:**
   - Acesse o painel do roteador (geralmente 192.168.1.1 ou 192.168.0.1)
   - Vá em "Port Forwarding" ou "Virtual Server"
   - Adicione regra:
     - Porta Externa: 5000 (ou outra)
     - Porta Interna: 5000
     - IP Local: [IP do seu computador]
     - Protocolo: TCP

4. **Configure firewall:**
   - Windows: Permita a porta 5000 no Firewall do Windows
   - Linux: `sudo ufw allow 5000`

5. **Execute o servidor:**
   ```bash
   python license_server.py
   ```

6. **Use o IP público:**
   - URL: `http://SEU_IP_PUBLICO:5000/validate`
   - Exemplo: `http://123.45.67.89:5000/validate`

**⚠️ IMPORTANTE:** Se seu IP público mudar (IP dinâmico), você precisará atualizar a URL no cliente.

### Opção 3: Serviço de DNS Dinâmico (Recomendado para IP Dinâmico)

1. **Registre-se em um serviço de DNS dinâmico:**
   - No-IP: https://www.noip.com (grátis)
   - DuckDNS: https://www.duckdns.org (grátis)
   - Dynu: https://www.dynu.com (grátis)

2. **Configure o DNS dinâmico:**
   - Crie um hostname (ex: `meuservidor.ddns.net`)
   - Configure o cliente DNS dinâmico no seu computador

3. **Combine com Port Forwarding:**
   - Configure port forwarding no roteador (Passo 2, Opção 2)
   - Use o hostname DNS dinâmico

4. **URL final:**
   - `http://meuservidor.ddns.net:5000/validate`

## 🔐 Passo 4: Configurar HTTPS (Opcional mas Recomentado)

### Usando ngrok:
- ngrok já fornece HTTPS automaticamente ✅

### Usando Port Forwarding:
Você pode usar um proxy reverso com Let's Encrypt, mas é mais complexo. Para começar, HTTP funciona, mas HTTPS é mais seguro.

## ⚙️ Passo 5: Configurar o Cliente

### Opção 1: Variável de Ambiente

**Windows:**
```cmd
set LICENSE_SERVER_URL=http://SEU_IP_OU_URL:5000/validate
```

**Linux/Mac:**
```bash
export LICENSE_SERVER_URL=http://SEU_IP_OU_URL:5000/validate
```

### Opção 2: Editar license.py

Edite `license.py` e altere:

```python
LICENSE_SERVER_URL = "http://SEU_IP_OU_URL:5000/validate"
```

Ou se usar ngrok:
```python
LICENSE_SERVER_URL = "https://abc123.ngrok.io/validate"
```

### Opção 3: No Executável

Antes de gerar o .exe, configure a URL em `license.py`.

## 🚀 Passo 6: Executar o Servidor

### Desenvolvimento (para testes):
```bash
python license_server.py
```

### Produção (recomendado):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 license_server:app
```

## 📝 Passo 7: Manter o Servidor Rodando

### Windows - Usando Task Scheduler:

1. Crie um arquivo `start_server.bat`:
```batch
@echo off
cd C:\caminho\para\seu\projeto
python license_server.py
```

2. Configure no Task Scheduler para executar na inicialização

### Windows - Usando NSSM (Serviço):

1. Baixe NSSM: https://nssm.cc/download
2. Instale como serviço:
```cmd
nssm install LicenseServer "C:\Python\python.exe" "C:\caminho\license_server.py"
nssm start LicenseServer
```

### Linux - Usando systemd:

Crie `/etc/systemd/system/license-server.service`:

```ini
[Unit]
Description=License Server
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/caminho/para/projeto
ExecStart=/usr/bin/python3 /caminho/para/projeto/license_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative o serviço:
```bash
sudo systemctl enable license-server
sudo systemctl start license-server
```

## 🧪 Teste

### 1. Teste o servidor localmente:

```bash
curl http://localhost:5000/health
```

Deve retornar: `{"status":"ok"}`

### 2. Teste de fora (se exposto):

```bash
curl http://SEU_IP_OU_URL:5000/health
```

### 3. Teste de validação:

```bash
curl -X POST http://SEU_IP_OU_URL:5000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "SUA_CHAVE",
    "machine_id": "MACHINE_ID",
    "action": "check"
  }'
```

## ⚠️ Considerações Importantes

### Segurança:

1. **Firewall:** Configure o firewall para permitir apenas conexões necessárias
2. **HTTPS:** Use HTTPS quando possível (ngrok fornece automaticamente)
3. **Rate Limiting:** Considere adicionar limite de requisições
4. **Backup:** Faça backup regular de `license_registry.json`

### IP Dinâmico:

- Se seu IP mudar, você precisará atualizar a URL no cliente
- Use DNS dinâmico para evitar isso
- Ou use ngrok com plano pago para URL fixa

### Performance:

- O servidor Flask é suficiente para uso pessoal
- Para muitos clientes simultâneos, considere usar gunicorn com múltiplos workers

## 🆘 Solução de Problemas

### Servidor não inicia:
- Verifique se a porta 5000 está livre: `netstat -an | findstr 5000`
- Tente outra porta: `app.run(port=8080)`

### Cliente não consegue conectar:
- Verifique se o servidor está rodando
- Verifique firewall
- Verifique se a URL está correta
- Teste com curl primeiro

### ngrok não funciona:
- Verifique se o servidor Flask está rodando
- Verifique se a porta está correta
- Tente reiniciar o ngrok

### Port Forwarding não funciona:
- Verifique se o IP local está correto
- Verifique se o roteador está configurado corretamente
- Verifique se o firewall permite a porta
- Teste se consegue acessar localmente primeiro

## 📊 Monitoramento

### Ver logs do servidor:
O servidor Flask mostra logs no console. Para produção, redirecione para arquivo:

```bash
python license_server.py >> server.log 2>&1
```

### Verificar registros:
O arquivo `license_registry.json` contém todas as ativações.

## ✅ Checklist

- [ ] Servidor Flask instalado e funcionando
- [ ] Servidor exposto para internet (ngrok/port forwarding)
- [ ] URL configurada no cliente
- [ ] Teste de conexão bem-sucedido
- [ ] Servidor configurado para iniciar automaticamente
- [ ] Backup do registro configurado
- [ ] Firewall configurado

