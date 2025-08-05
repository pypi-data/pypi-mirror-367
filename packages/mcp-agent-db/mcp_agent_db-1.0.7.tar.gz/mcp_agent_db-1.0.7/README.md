# MCP Agent DB

Uma ferramenta poderosa para consulta de bases de dados usando linguagem natural com agente inteligente.

## 🚀 Características

- 🤖 **Agente Inteligente**: Converte perguntas em linguagem natural para SQL
- 🔍 **Consultas Avançadas**: Suporte para consultas complexas com joins e agregações
- 📊 **Geração de Gráficos**: Integração com ferramentas MCP para visualização
- 🏢 **Multi-empresa**: Suporte para múltiplas empresas e filiais
- 💾 **Cache Inteligente**: Sistema de cache para otimizar performance
- 🔄 **Memória de Conversação**: Mantém contexto entre consultas
- 🌐 **API REST**: Endpoints prontos para integração web e mobile

## 📦 Instalação

```bash
pip install mcp-agent-db
```

## 🔧 Configuração

1. Configure as variáveis de ambiente:

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/database
GOOGLE_API_KEY=sua_chave_google_ai
MCP_SERVER_URL=http://localhost:3000
```

2. Configure o banco de dados no `settings.py`:

```python
DATABASES = {
    'casaa': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'seu_banco',
        'USER': 'usuario',
        'PASSWORD': 'senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 💻 Uso Básico

### Como Biblioteca Python

```python
from mcp_agent_db import consultar_banco_dados

# Consulta simples
resultado = consultar_banco_dados("TOP 10 clientes que mais compraram", "casaa")
print(resultado)

# Consulta com gráfico
resultado = consultar_banco_dados("Gráfico de vendas por mês", "casaa")
print(resultado)
```

### Como API REST

```python
from mcp_agent_db.main import app
import uvicorn

# Iniciar servidor
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🌐 API Endpoints

### POST /api/consulta

Realizar consultas em linguagem natural

```json
{
  "pergunta": "TOP 10 clientes que mais compraram",
  "slug": "casaa"
}
```

### GET /api/schemas

Listar schemas disponíveis

### POST /api/grafico

Gerar gráficos a partir dos dados

```json
{
  "pergunta": "Gráfico de vendas por vendedor",
  "tipo_grafico": "bar",
  "slug": "casaa"
}
```

## 📱 Integração React Native

### Instalação no React Native

```bash
npm install axios
```

### Exemplo de uso

```javascript
import axios from 'axios'

const API_BASE_URL = 'http://seu-servidor:8000'

// Serviço para consultas
export const consultarDados = async (pergunta, slug = 'casaa') => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/consulta`, {
      pergunta,
      slug,
    })
    return response.data
  } catch (error) {
    throw new Error(`Erro na consulta: ${error.message}`)
  }
}

// Serviço para gráficos
export const gerarGrafico = async (
  pergunta,
  tipoGrafico = 'bar',
  slug = 'casaa'
) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/grafico`, {
      pergunta,
      tipo_grafico: tipoGrafico,
      slug,
    })
    return response.data
  } catch (error) {
    throw new Error(`Erro ao gerar gráfico: ${error.message}`)
  }
}

// Componente React Native
import React, { useState } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
} from 'react-native'

const ConsultaScreen = () => {
  const [pergunta, setPergunta] = useState('')
  const [resultado, setResultado] = useState('')
  const [loading, setLoading] = useState(false)

  const handleConsulta = async () => {
    if (!pergunta.trim()) return

    setLoading(true)
    try {
      const response = await consultarDados(pergunta)
      setResultado(response.resultado || response)
    } catch (error) {
      setResultado(`Erro: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>
        Consulta Inteligente
      </Text>

      <TextInput
        style={{
          borderWidth: 1,
          borderColor: '#ccc',
          padding: 10,
          marginBottom: 10,
          borderRadius: 5,
        }}
        placeholder="Digite sua pergunta..."
        value={pergunta}
        onChangeText={setPergunta}
        multiline
      />

      <TouchableOpacity
        style={{
          backgroundColor: '#007bff',
          padding: 15,
          borderRadius: 5,
          marginBottom: 20,
        }}
        onPress={handleConsulta}
        disabled={loading}>
        <Text
          style={{ color: 'white', textAlign: 'center', fontWeight: 'bold' }}>
          {loading ? 'Consultando...' : 'Consultar'}
        </Text>
      </TouchableOpacity>

      <ScrollView style={{ flex: 1 }}>
        <Text style={{ fontSize: 16 }}>{resultado}</Text>
      </ScrollView>
    </View>
  )
}

export default ConsultaScreen
```

## 🔧 Desenvolvimento

### Estrutura do Projeto

### Executar em desenvolvimento

```bash
cd mcp_agent_db
python main.py
```

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📞 Suporte

- Email: leokaique7@gmail.com
- GitHub: https://github.com/leokaique/mcp-agent-db
