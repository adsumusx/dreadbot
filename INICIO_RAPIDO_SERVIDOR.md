# 🚀 Início Rápido - Servidor no Seu Computador

## Método Mais Fácil: Usando ngrok

### 1. Instale o Flask:
```bash
pip install flask
```

### 2. Execute o servidor:
**Windows:**
```cmd
start_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

Ou manualmente:
```bash
python license_server.py
```

### 3. Em outro terminal, execute o ngrok:
```bash
ngrok http 5000
```

### 4. Copie a URL HTTPS do ngrok:
```
Forwarding: https://abc123.ngrok.io -> http://localhost:5000
```

### 5. Configure no cliente (license.py):
```python
LICENSE_SERVER_URL = "https://abc123.ngrok.io/validate"
```

### 6. Pronto! ✅

O servidor está rodando e acessível pela internet.

---

## Método Alternativo: Port Forwarding

### 1. Descubra seu IP público:
- Acesse: https://whatismyipaddress.com
- Anote o IP

### 2. Configure Port Forwarding:
- Acesse o painel do roteador (geralmente 192.168.1.1)
- Configure port forwarding: porta 5000 → IP do seu PC
- Permita a porta 5000 no firewall

### 3. Execute o servidor:
```bash
python license_server.py
```

### 4. Configure no cliente:
```python
LICENSE_SERVER_URL = "http://SEU_IP_PUBLICO:5000/validate"
```

---

## ⚠️ Importante

- **ngrok:** URL muda a cada reinício (plano grátis)
- **Port Forwarding:** IP pode mudar se for dinâmico
- **Solução:** Use DNS dinâmico (No-IP, DuckDNS) com port forwarding

---

## 📖 Guia Completo

Veja `SETUP_SERVIDOR_LOCAL.md` para instruções detalhadas.

