# Tools Content File Extractor

Extrator de conteúdo de arquivos com suporte a PDFs e integração com APIs de IA (Google Gemini e Azure OpenAI).

## Pré-requisitos

- Python 3.8+
- Poetry (para gerenciamento de dependências)

## Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd tools-content-file-extractor
```

2. Instale as dependências usando Poetry:
```bash
poetry install
```

3. Configure as variáveis de ambiente:
```bash
cp env.example .env
```

## Configuração das Variáveis de Ambiente

Este projeto requer as seguintes variáveis de ambiente para funcionar corretamente:

### Variáveis Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `GOOGLE_API_KEY` | Chave da API Google Gemini | `your_google_api_key_here` |
| `OPENAI_API_URL` | URL da API Azure OpenAI | `https://your-resource.openai.azure.com` |
| `OPENAI_API_KEY` | Chave da API Azure OpenAI | `your_azure_openai_api_key_here` |
| `ENVIRONMENT` | Ambiente de execução | `development`, `production` |

### Como Configurar

1. Copie o arquivo de exemplo:
```bash
cp env.example .env
```

2. Edite o arquivo `.env` e preencha as variáveis:
```env
# Configurações da API Google Gemini
GOOGLE_API_KEY=your_google_api_key_here

# Configurações da API Azure OpenAI
OPENAI_API_KEY=your_azure_openai_api_key_here
OPENAI_API_URL=https://your-resource.openai.azure.com

# Ambiente de execução
ENVIRONMENT=development
```

### Obtenção das Chaves de API

- **Google API Key**: Acesse o [Google Cloud Console](https://console.cloud.google.com/) e habilite a API Gemini
- **Azure OpenAI**: Configure no [Azure Portal](https://portal.azure.com/) e obtenha as credenciais necessárias

## Uso

### Ativar o Ambiente Virtual

```bash
poetry env activate
source .venv/bin/activate
```

### Executar o Projeto

```bash
poetry run python main.py
```

## Estrutura do Projeto

```
tools-content-file-extractor/
├── business/           # Lógica de negócio
│   ├── azure/         # Serviços Azure OpenAI
│   ├── context/       # Contexto e configurações
│   ├── output/        # Geradores de saída
│   ├── pdf/           # Extratores de PDF
│   └── security/      # Serviços de segurança
├── storage/           # Serviços de armazenamento
├── tools/             # Ferramentas auxiliares
├── docs/              # Documentação
└── docs-exemplos/     # Exemplos de documentos
```

## Funcionalidades

- Extração de conteúdo de PDFs
- Processamento com IA (Google Gemini e Azure OpenAI)
- Geração de saída em JSON
- Armazenamento seguro de dados
- Criptografia de informações sensíveis

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença [MIT](LICENSE).