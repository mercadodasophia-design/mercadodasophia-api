# 🚀 Guia de Inicialização Automática da API

## 📋 **Opções Disponíveis:**

### **1. Inicialização Manual (Atual)**
```bash
cd api-express
npm start
```
- ✅ **Simples**
- ❌ **Precisa iniciar manualmente**

### **2. Inicialização Automática com Windows**
```bash
# Execute como administrador:
setup-auto-start.bat
```
- ✅ **Inicia automaticamente com o PC**
- ✅ **Não precisa lembrar**
- ⚠️ **Precisa executar como administrador**

### **3. Script Melhorado**
```bash
# Use este script para iniciar:
start-api-auto.bat
```
- ✅ **Verifica dependências automaticamente**
- ✅ **Mostra IP da máquina**
- ✅ **Interface mais amigável**

## 🔧 **Como Configurar:**

### **Passo 1: Configurar Inicialização Automática**
1. **Clique com botão direito** em `setup-auto-start.bat`
2. **Selecione "Executar como administrador"**
3. **Confirme a criação da tarefa**

### **Passo 2: Testar**
1. **Reinicie o PC**
2. **Verifique se a API está rodando:**
   ```
   http://192.168.1.24:3000
   ```

## 🛠️ **Comandos Úteis:**

### **Verificar se está rodando:**
```bash
netstat -an | findstr :3000
```

### **Parar inicialização automática:**
```bash
schtasks /delete /tn "MercadoDaSophia-API" /f
```

### **Ver tarefas agendadas:**
```bash
schtasks /query /tn "MercadoDaSophia-API"
```

## 📱 **URLs da API:**

- **Local**: `http://localhost:3000`
- **Rede**: `http://192.168.1.24:3000`
- **Endpoints**:
  - `GET /api/search?q=produto`
  - `GET /api/product?url=url`
  - `POST /api/import`

## ⚠️ **Importante:**

1. **Firewall**: Permita conexões na porta 3000
2. **Rede**: Celular e PC na mesma WiFi
3. **Node.js**: Deve estar instalado
4. **Dependências**: `npm install` na primeira vez

## 🎯 **Próximos Passos:**

1. **Configure a inicialização automática**
2. **Teste no celular**
3. **Use o app para importar produtos**

---
*Configurado para o Mercado da Sophia* 🏪 