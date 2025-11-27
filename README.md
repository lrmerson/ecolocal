# API REST de Pontos de Coleta

API REST para gerenciar e filtrar pontos de coleta de lixo eletrônico no Distrito Federal.

## Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar a aplicação

```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## Endpoints

### 1. Filtrar pontos por tipo de lixo

**Método:** `GET`  
**URI:** `/api/coleta-pontos?tipos=<tipo1>,<tipo2>,...`

**Descrição:**  
Retorna pontos de coleta que aceitam TODOS os tipos de lixo especificados.

**Parâmetros de Query:**
- `tipos` (obrigatório): Lista de tipos de lixo separados por vírgula
  - Exemplo: `eletroeletronicos,pilhas`

**Exemplo de Requisição:**
```bash
curl "http://localhost:5000/api/coleta-pontos?tipos=eletroeletronicos,pilhas"
```

**Resposta (200 OK):**
```json
{
  "total": 2,
  "tipos_filtrados": ["eletroeletronicos", "pilhas"],
  "pontos": [
    {
      "id": "001",
      "nome": "Zero Impacto Logística Reversa",
      "tipo_lixo": "eletroeletronicos\\,eletrodomesticos\\,pilhas",
      "latitude": -15.762421707078582,
      "longitude": -47.935475219000324,
      "endereco": "Saa Q 2 SETOR DE ABASTECIMENTO..."
    },
    {
      "id": "003",
      "nome": "Carrefour Hipermercado",
      "tipo_lixo": "eletroeletronicos\\,eletrodomesticos\\,pilhas",
      "latitude": -15.733847664170918,
      "longitude": -47.899207515917645,
      "endereco": "Boulevard Shopping ST Setor..."
    }
  ]
}
```

**Erros:**
- `400 Bad Request`: Parâmetro `tipos` não fornecido

### 2. Obter ponto específico por ID

**Método:** `GET`  
**URI:** `/api/coleta-pontos/<ponto_id>`

**Descrição:**  
Retorna os dados de um ponto de coleta específico.

**Parâmetros de Caminho:**
- `ponto_id`: ID do ponto (ex: 001, 015, 119)

**Exemplo de Requisição:**
```bash
curl "http://localhost:5000/api/coleta-pontos/001"
```

**Resposta (200 OK):**
```json
{
  "id": "001",
  "nome": "Zero Impacto Logística Reversa",
  "tipo_lixo": "eletroeletronicos\\,eletrodomesticos\\,pilhas",
  "latitude": -15.762421707078582,
  "longitude": -47.935475219000324,
  "endereco": "Saa Q 2 SETOR DE ABASTECIMENTO..."
}
```

**Erros:**
- `404 Not Found`: Ponto com esse ID não encontrado
- `500 Internal Server Error`: Erro ao processar requisição

### 3. Listar todos os pontos de coleta

**Método:** `GET`  
**URI:** `/api/coleta-pontos`

**Descrição:**  
Retorna lista de todos os pontos de coleta com suporte a paginação.

**Parâmetros de Query (Opcional):**
- `limit`: Número máximo de resultados a retornar
- `offset`: Número de resultados a pular (para paginação)

**Exemplo de Requisição:**
```bash
# Listar todos
curl "http://localhost:5000/api/coleta-pontos"

# Com paginação (10 resultados, pulando os primeiros 20)
curl "http://localhost:5000/api/coleta-pontos?limit=10&offset=20"
```

**Resposta (200 OK):**
```json
{
  "total": 119,
  "pontos": [
    {
      "id": "001",
      "nome": "Zero Impacto Logística Reversa",
      "tipo_lixo": "eletroeletronicos\\,eletrodomesticos\\,pilhas",
      "latitude": -15.762421707078582,
      "longitude": -47.935475219000324,
      "endereco": "Saa Q 2 SETOR DE ABASTECIMENTO..."
    },
    ...
  ]
}
```

## Testes Unitários

Executar os testes unitários da lógica de negócio:

```bash
python -m unittest test_coleta_service.py -v
```

### Cobertura de Testes

Os testes unitários cobrem:
- ✓ Filtrar por um único tipo de lixo
- ✓ Filtrar por múltiplos tipos (AND logic)
- ✓ Filtrar por tipo inexistente
- ✓ Filtrar com lista vazia
- ✓ Estrutura de dados retornados
- ✓ Case-insensitive filtering
- ✓ Tratamento de espaços em branco
- ✓ Tratamento de arquivo não encontrado

## Arquitetura

### Estrutura de Arquivos

```
projeto-apc/
├── app.py                      # Aplicação Flask com endpoints REST
├── coleta_service.py           # Lógica de negócio (camada de serviço)
├── test_coleta_service.py      # Testes unitários
├── pontos-de-coleta.csv        # Dados dos pontos de coleta
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
└── #Filtro de pontos.py        # Script original (legado)
```

### Padrões Utilizados

1. **REST API Design**
   - Recurso: `coleta-pontos` (plural)
   - Operações: GET (leitura de dados)
   - URIs descritivas e previsíveis
   - Códigos HTTP apropriados

2. **Camadas de Arquitetura**
   - **Camada de Apresentação** (`app.py`): Endpoints HTTP
   - **Camada de Negócio** (`coleta_service.py`): Lógica de filtro
   - **Camada de Dados** (`pontos-de-coleta.csv`): Fonte de dados

3. **Boas Práticas**
   - Separação de responsabilidades
   - Testes unitários sem dependência HTTP
   - Tratamento de erros e exceções
   - Documentação clara

## Tipos de Lixo Suportados

- `eletroeletronicos`: Eletrônicos em geral
- `eletrodomesticos`: Eletrodomésticos
- `pilhas`: Pilhas e baterias
- `lampadas`: Lâmpadas fluorescentes e LED

## Exemplos de Uso

### Python Requests

```python
import requests

# Filtrar por um tipo
response = requests.get(
    'http://localhost:5000/api/coleta-pontos',
    params={'tipos': 'pilhas'}
)
pontos = response.json()

# Filtrar por múltiplos tipos
response = requests.get(
    'http://localhost:5000/api/coleta-pontos',
    params={'tipos': 'eletroeletronicos,pilhas'}
)
pontos = response.json()
print(f"Encontrados {pontos['total']} pontos")
```

### JavaScript (Fetch)

```javascript
// Filtrar por tipo
const tipos = 'eletroeletronicos,pilhas';
fetch(`http://localhost:5000/api/coleta-pontos?tipos=${tipos}`)
  .then(res => res.json())
  .then(data => console.log(`${data.total} pontos encontrados`));

// Obter ponto específico
fetch('http://localhost:5000/api/coleta-pontos/001')
  .then(res => res.json())
  .then(ponto => console.log(ponto.nome));
```

## Notas

- Os valores de latitude/longitude são retornados como números (float)
- Os tipos de lixo no CSV usam `\,` como separador (vírgula escapada)
- O filtro é case-insensitive
- O filtro usa lógica AND: retorna apenas pontos que têm TODOS os tipos especificados
