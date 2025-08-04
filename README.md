# AliExpress API Server Python

Servidor Flask que utiliza o SDK Python oficial da Alibaba para integração com APIs do AliExpress.

## 🚀 Características

- **SDK Oficial**: Utiliza o SDK Python oficial da Alibaba (`iop-sdk-python`)
- **Flask Framework**: Servidor web moderno e eficiente
- **Interface Web**: Página HTML interativa para testes
- **OAuth2**: Implementação completa do fluxo de autorização
- **Cache de Tokens**: Armazenamento em memória dos tokens de acesso

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🛠️ Instalação

1. **Clonar o repositório**:
```bash
git clone <repository-url>
cd aliexpress-python-api
```

2. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

3. **Configurar variáveis de ambiente**:
```bash
cp config.env.example .env
# Editar .env com suas credenciais
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` com as seguintes variáveis:

```env
APP_KEY=517616
APP_SECRET=TTqNmTMs5Q0QiPbulDNenhXr2My18nN4
REDIRECT_URI=https://mercadodasophia-api.onrender.com/api/aliexpress/oauth-callback
PORT=10000
```

### Credenciais AliExpress

1. Acesse [AliExpress Open Platform](https://openservice.aliexpress.com/)
2. Registre-se como desenvolvedor
3. Crie uma aplicação
4. Obtenha `APP_KEY` e `APP_SECRET`
5. Configure a URL de callback

## 🚀 Execução

### Desenvolvimento Local

```bash
python server.py
```

O servidor estará disponível em: `http://localhost:10000`

### Produção (Render)

1. Conecte seu repositório ao Render
2. Configure as variáveis de ambiente
3. Deploy automático

## 📡 Endpoints

### 🔐 Autenticação

- `GET /api/aliexpress/auth` - Gera URL de autorização
- `GET /api/aliexpress/oauth-callback` - Callback OAuth
- `GET /api/aliexpress/tokens/status` - Status dos tokens

### 🛍️ Produtos

- `GET /api/aliexpress/products` - Buscar produtos
- `GET /api/aliexpress/categories` - Buscar categorias

### 📊 Informações

- `GET /` - Página inicial com interface web

## 🔧 Diferenças do SDK Python

### Vantagens

1. **Oficial da Alibaba**: SDK mantido pela própria Alibaba
2. **Timestamp Correto**: Usa milissegundos como esperado pela API
3. **Parâmetros Corretos**: Inclui `partner_id` e outros parâmetros necessários
4. **Implementação Testada**: Usado em produção por muitos desenvolvedores

### Características Técnicas

- **URL Base**: `https://api-sg.aliexpress.com/sync`
- **Timestamp**: Milissegundos (`time.time() * 1000`)
- **Assinatura**: HMAC-SHA256 com ordenação alfabética
- **Parâmetros**: Inclui `partner_id` e outros parâmetros do sistema

## 🐛 Solução de Problemas

### Erro "IncompleteSignature"

O SDK Python resolve este problema porque:

1. **Timestamp Correto**: Usa milissegundos em vez de segundos
2. **Parâmetros Completos**: Inclui todos os parâmetros necessários
3. **Ordenação Correta**: Parâmetros ordenados alfabeticamente
4. **Assinatura Oficial**: Implementação oficial da Alibaba

### Logs

O servidor gera logs detalhados para debug:

```
🔍 URL de autorização gerada: https://api-sg.aliexpress.com/oauth/authorize?...
🔍 Callback OAuth recebido com code: 3_517616_...
✅ Resposta do token: {...}
✅ Tokens salvos em cache
```

## 📚 Documentação

- [AliExpress Open Platform](https://openservice.aliexpress.com/)
- [SDK Python Documentation](https://openservice.aliexpress.com/doc/doc.htm)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆚 Comparação com Node.js

| Aspecto | Python (iop) | Node.js (ae_sdk) |
|---------|-------------|------------------|
| **Origem** | Oficial Alibaba | Não oficial |
| **Timestamp** | Milissegundos | Segundos |
| **URL Base** | `/sync` | `/rest` |
| **Parâmetros** | `partner_id` incluído | Sem `partner_id` |
| **Assinatura** | Implementação oficial | Implementação terceira |

## 🎯 Próximos Passos

1. **Testar OAuth**: Verificar se resolve o problema de assinatura
2. **Comparar Resultados**: Testar ambos os SDKs
3. **Escolher Melhor**: Decidir qual SDK usar em produção
4. **Migrar se Necessário**: Implementar o melhor SDK no projeto principal 