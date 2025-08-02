# 🧪 Guia de Teste da API

## ✅ **Status Atual:**
- **Servidor**: Rodando na porta 3000
- **Credenciais**: Configuradas ✅
- **API AliExpress**: Configurada ✅
- **Web Scraping**: Fallback disponível ✅
- **Dados Simulados**: Último recurso ✅

## 🚀 **Como Testar:**

### **1. Teste Local (PC)**
```powershell
# Teste básico
Invoke-WebRequest -Uri "http://localhost:3000/api/search?q=smartphone" -Method GET

# Teste com limite
Invoke-WebRequest -Uri "http://localhost:3000/api/search?q=smartphone&limit=5" -Method GET
```

### **2. Teste no Celular**
```
# Abra o navegador no celular e acesse:
http://192.168.1.24:3000/api/search?q=smartphone
```

### **3. Teste no App Flutter**
1. **Abra o app admin**
2. **Vá para a tela de importação**
3. **Digite "smartphone" na busca**
4. **Veja os produtos aparecerem**

## 📊 **Endpoints Disponíveis:**

### **Buscar Produtos**
```
GET http://192.168.1.24:3000/api/search?q=smartphone&limit=10
```

### **Detalhes do Produto**
```
GET http://192.168.1.24:3000/api/product?url=product_url
```

### **Importar Produto**
```
POST http://192.168.1.24:3000/api/import
{
  "url": "product_url",
  "categoryId": "electronics"
}
```

## 🎯 **Credenciais Configuradas:**
- **App Key**: 517616 ✅
- **App Secret**: fbB2SaFHMU20NBpECt1NFHWNXOV3rNuq ✅
- **Status**: Online ✅

## ⚠️ **Sistema Híbrido:**
1. **API Oficial** (Prioridade) - Usa suas credenciais
2. **Web Scraping** (Fallback) - Se API falhar
3. **Dados Simulados** (Último recurso) - Garante funcionamento

## 🎉 **Próximos Passos:**
1. **Teste no celular** (mesma rede WiFi)
2. **Teste no app Flutter**
3. **Importe produtos** para a loja

---
*API configurada e funcionando!* 🚀 