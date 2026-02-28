# 🗺️ Integração do Mapa Interativo - EcoLocal

## ✅ O Que Foi Feito

### 1. **Rota do Mapa (`/mapa`)**
- Integração completa com Folium (biblioteca de mapas)
- Suporte a todos os filtros: `tipos`, `lat`, `lon`
- Marcadores coloridos por tipo de lixo
- Popup com informações detalhadas (nome, endereço, distância, tempo)
- Controle de localização do usuário
- Integração com Google Maps para direções

### 2. **Página Inicial (`/`)**
- Landing page moderna e responsiva
- Links diretos para Mapa e Sobre
- Informações sobre a API REST
- Design visual atraente

### 3. **Página Sobre (`/sobre`)**
- Documentação do projeto
- Funcionalidades principais
- Stack tecnológico
- Impacto ambiental
- Links de navegação

### 4. **Estrutura de Pastas**
```
ecolocal_backend/
├── app.py                      (atualizado com novas rotas)
├── coleta_service.py           (sem alterações)
├── requirements.txt            (+ folium==0.14.0)
├── pontos-de-coleta.csv        (sem alterações)
│
├── templates/                  (NOVO)
│   ├── index.html              (página inicial)
│   └── sobre.html              (página sobre)
│
└── static/                     (NOVO)
    └── style.css               (estilos adicionais)
```

---

## 🚀 Como Usar

### 1. Instalar Dependência
```bash
pip install -r requirements.txt
```

Ou apenas folium:
```bash
pip install folium==0.14.0
```

### 2. Executar a Aplicação
```bash
python app.py
```

### 3. Acessar no Navegador
- **Home:** http://localhost:5000
- **Mapa:** http://localhost:5000/mapa
- **Sobre:** http://localhost:5000/sobre
- **API REST:** http://localhost:5000/api/coleta-pontos

---

## 📍 Funcionalidades do Mapa

### Filtros por Query Parameters
```
/mapa                                    # Todos os pontos
/mapa?tipos=pilhas                       # Apenas pilhas
/mapa?tipos=eletroeletronicos,pilhas    # Múltiplos tipos
/mapa?lat=-23.5505&lon=-46.6333&n=5    # 5 mais próximos
/mapa?tipos=pilhas&lat=-23.5505&lon=-46.6333&n=3
```

### Cores dos Marcadores
- 🟢 **Verde**: Eletrônicos (padrão)
- 🔴 **Vermelho**: Pilhas
- 🟡 **Amarelo**: Lâmpadas
- 🟣 **Roxo**: Eletrodomésticos

### Controles do Mapa
- **Zoom**: Scroll do mouse ou botões `+` e `-`
- **Localização**: Ícone de localização (superior esquerdo)
- **Filtros**: Menu fixo no canto superior esquerdo
- **Sobre**: Botão "ℹ️ Sobre" (superior direito)

---

## 🔗 Integração com API REST Existente

O mapa utiliza automaticamente sua API:

1. **Sem Filtro**: Lê direto do CSV (todos os pontos)
2. **Com Filtro**: Chama `ler_pontos_por_tipo_lixo()` de `coleta_service.py`
3. **Com Proximidade**: Chama Google Distance Matrix API (se configurada)

### Fluxo de Dados
```
Requisição HTTP
    ↓
/mapa?tipos=pilhas&lat=-23.5505&lon=-46.6333&n=3
    ↓
coleta_service.ler_pontos_por_tipo_lixo(
    tipos=['pilhas'],
    user_lat=-23.5505,
    user_lon=-46.6333,
    n=3
)
    ↓
Pontos filtrados com distance_km e duration_min
    ↓
Folium renderiza no mapa
    ↓
HTML enviado ao navegador
```

---

## 📱 Responsividade

O mapa é totalmente responsivo:
- ✓ Desktop (1920x1080+)
- ✓ Tablet (768px+)
- ✓ Mobile (320px+)

---

## 🎨 Personalizações Possíveis

### Mudar Centro do Mapa
Em `app.py`, função `mapa()`:
```python
centro_lat, centro_lon = -15.793889, -47.882778  # Alterar para suas coordenadas
```

### Mudar Zoom Padrão
```python
mapa = folium.Map(
    location=[centro_lat, centro_lon],
    zoom_start=13  # Alterar para mais/menos zoom
)
```

### Adicionar Layer de Terreno
```python
folium.TileLayer('Stamen Terrain').add_to(mapa)
```

### Customizar Cores dos Marcadores
Em `app.py`, procure por `icon_color = ...` e modifique conforme necessário.

---

## 🐛 Possíveis Problemas e Soluções

### Erro: "ModuleNotFoundError: No module named 'folium'"
**Solução:** Instale folium
```bash
pip install folium
```

### Mapa não carrega
**Solução:** Verifique se `pontos-de-coleta.csv` está no mesmo diretório que `app.py`

### Marcadores não aparecem
**Solução:** Verifique se o arquivo CSV está bem formatado e contém colunas `latitude` e `longitude`

### Proximidade não funciona
**Solução:** Configure o token do Mapbox como variável de ambiente antes de iniciar o servidor:
```powershell
$env:MAPBOX_API_KEY = "seu_token_mapbox_aqui"
```
```bash
export MAPBOX_API_KEY="seu_token_mapbox_aqui"
```

---

## 📊 Estatísticas

- **Linhas de código (app.py):** +150 linhas
- **Arquivos criados:** 3 (index.html, sobre.html, style.css)
- **Dependências adicionadas:** folium==0.14.0
- **Rotas novas:** 3 (`/`, `/mapa`, `/sobre`)

---

## ✨ Próximas Melhorias

- [ ] Adicionar clusters de marcadores (MarkerCluster)
- [ ] Adicionar heatmap de densidade
- [ ] Exportar mapa como imagem PNG
- [ ] Adicionar camadas customizadas (satélite, terreno)
- [ ] Busca por nome de local
- [ ] Botão para compartilhar mapa
- [ ] Análise de dados (estatísticas)

---

## 📞 Suporte

Se encontrar algum problema, verifique:
1. Dependências instaladas: `pip list | grep folium`
2. Arquivo CSV presente no diretório
3. Porta 5000 não em uso
4. Permissões de arquivo

---

**Status:** ✅ Integração Completa e Funcional

Versão: 1.0
Data: 2025-11-30
