"""
Exemplos de Uso da API REST de Pontos de Coleta

Este arquivo demonstra como usar a API em diferentes cenários.
"""

# ============================================================================
# Exemplo 1: Uso Direto da Função (sem HTTP)
# ============================================================================

def exemplo_1_uso_direto():
    """Chamar a função de filtro diretamente sem HTTP."""
    from coleta_service import ler_pontos_por_tipo_lixo
    
    # Filtrar pontos que aceitam pilhas
    pontos = ler_pontos_por_tipo_lixo(['pilhas'])
    print(f"Encontrados {len(pontos)} pontos com pilhas")
    
    # Filtrar pontos que aceitam AMBOS eletroeletronicos E pilhas
    pontos = ler_pontos_por_tipo_lixo(['eletroeletronicos', 'pilhas'])
    print(f"Encontrados {len(pontos)} pontos com eletroeletronicos e pilhas")
    
    # Iterar sobre resultados
    for ponto_id, ponto in pontos.items():
        print(f"{ponto['nome']}: {ponto['endereco']}")


# ============================================================================
# Exemplo 2: Usar a API via Requests (HTTP)
# ============================================================================

def exemplo_2_requests_basico():
    """Usar a API com a biblioteca requests."""
    try:
        import requests
    except ImportError:
        print("Instale requests: pip install requests")
        return
    
    BASE_URL = 'http://localhost:5000/api'
    
    # Filtrar por tipo
    response = requests.get(
        f'{BASE_URL}/coleta-pontos',
        params={'tipos': 'pilhas'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data['total']} pontos")
        
        for ponto in data['pontos']:
            print(f"  - {ponto['nome']} ({ponto['id']})")
    else:
        print(f"Erro: {response.status_code}")


# ============================================================================
# Exemplo 3: Filtro Avançado com Múltiplos Tipos
# ============================================================================

def exemplo_3_multiplos_tipos():
    """Filtrar por múltiplos tipos (AND logic)."""
    try:
        import requests
    except ImportError:
        return
    
    # Encontrar pontos que aceitam AMBOS eletroeletronicos E pilhas
    response = requests.get(
        'http://localhost:5000/api/coleta-pontos',
        params={'tipos': 'eletroeletronicos,pilhas'}
    )
    
    data = response.json()
    print(f"Pontos com eletroeletronicos E pilhas: {data['total']}")
    
    for ponto in data['pontos']:
        tipos = ponto['tipo_lixo'].replace('\\,', ', ')
        print(f"  - {ponto['nome']}")
        print(f"    Tipos: {tipos}")
        print(f"    Localização: {ponto['latitude']}, {ponto['longitude']}")


# ============================================================================
# Exemplo 4: Paginação
# ============================================================================

def exemplo_4_paginacao():
    """Listar pontos com paginação."""
    try:
        import requests
    except ImportError:
        return
    
    BASE_URL = 'http://localhost:5000/api'
    
    # Listar 10 pontos, pulando os primeiros 20
    response = requests.get(
        f'{BASE_URL}/coleta-pontos',
        params={'limit': 10, 'offset': 20}
    )
    
    data = response.json()
    print(f"Mostrando {len(data['pontos'])} de {data['total']} pontos")
    
    for i, ponto in enumerate(data['pontos'], 1):
        print(f"{i}. {ponto['nome']}")


# ============================================================================
# Exemplo 5: Tratamento de Erros
# ============================================================================

def exemplo_5_tratamento_erros():
    """Demonstrar tratamento de erros."""
    try:
        import requests
    except ImportError:
        return
    
    BASE_URL = 'http://localhost:5000/api'
    
    # Erro 1: Parâmetro faltando
    response = requests.get(f'{BASE_URL}/coleta-pontos')
    if response.status_code == 400:
        error = response.json()
        print(f"Erro 400: {error['error']}")
    
    # Erro 2: Ponto não existe
    response = requests.get(f'{BASE_URL}/coleta-pontos/999')
    if response.status_code == 404:
        error = response.json()
        print(f"Erro 404: {error['error']}")


# ============================================================================
# Exemplo 6: Aplicação com Geolocalização (usando Folium)
# ============================================================================

def exemplo_6_mapa():
    """Criar mapa com os pontos de coleta."""
    try:
        import folium
        import requests
    except ImportError:
        print("Instale folium e requests: pip install folium requests")
        return
    
    # Buscar pontos com pilhas
    response = requests.get(
        'http://localhost:5000/api/coleta-pontos',
        params={'tipos': 'pilhas'}
    )
    
    data = response.json()
    pontos = data['pontos']
    
    # Calcular centro do mapa
    if pontos:
        lat_media = sum(p['latitude'] for p in pontos) / len(pontos)
        lon_media = sum(p['longitude'] for p in pontos) / len(pontos)
        
        # Criar mapa
        mapa = folium.Map(
            location=[lat_media, lon_media],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Adicionar marcadores
        for ponto in pontos:
            folium.Marker(
                location=[ponto['latitude'], ponto['longitude']],
                popup=f"{ponto['nome']}<br>{ponto['endereco']}",
                tooltip=ponto['nome']
            ).add_to(mapa)
        
        # Salvar mapa
        mapa.save('mapa_coleta.html')
        print(f"Mapa criado: mapa_coleta.html ({len(pontos)} pontos)")


# ============================================================================
# Exemplo 7: CLI Interativa
# ============================================================================

def exemplo_7_cli():
    """Interface de linha de comando."""
    from coleta_service import ler_pontos_por_tipo_lixo
    
    print("=" * 60)
    print("Buscar Pontos de Coleta")
    print("=" * 60)
    
    tipos_input = input("Digite os tipos de lixo (separados por vírgula): ")
    tipos = [t.strip() for t in tipos_input.split(',')]
    
    try:
        pontos = ler_pontos_por_tipo_lixo(tipos)
        
        if not pontos:
            print(f"Nenhum ponto encontrado para: {', '.join(tipos)}")
        else:
            print(f"\nEncontrados {len(pontos)} ponto(s):\n")
            
            for ponto_id, ponto in pontos.items():
                print(f"ID: {ponto['id']}")
                print(f"Nome: {ponto['nome']}")
                print(f"Endereço: {ponto['endereco']}")
                print(f"Coordenadas: ({ponto['latitude']}, {ponto['longitude']})")
                print("-" * 60)
    
    except FileNotFoundError:
        print("Arquivo CSV não encontrado!")


# ============================================================================
# Exemplo 9: Batch Processing
# ============================================================================

def exemplo_9_batch():
    """Processar múltiplas requisições."""
    try:
        import requests
    except ImportError:
        return
    
    tipos_lista = [
        ['pilhas'],
        ['eletroeletronicos'],
        ['lampadas'],
        ['eletrodomesticos']
    ]
    
    resultados = {}
    
    for tipos in tipos_lista:
        response = requests.get(
            'http://localhost:5000/api/coleta-pontos',
            params={'tipos': ','.join(tipos)}
        )
        
        if response.status_code == 200:
            data = response.json()
            resultados[tipos[0]] = data['total']
    
    print("Resumo por tipo:")
    for tipo, total in resultados.items():
        print(f"  {tipo}: {total} pontos")


# ============================================================================
# Executar Exemplos
# ============================================================================

if __name__ == '__main__':
    print("Selecione um exemplo:\n")
    print("1. Uso direto da função")
    print("2. Requests básico")
    print("3. Múltiplos tipos")
    print("4. Paginação")
    print("5. Tratamento de erros")
    print("6. Mapa (requer folium)")
    print("7. CLI Interativa")
    print("8. Batch processing")
    
    escolha = input("\nDigite o número: ").strip()
    
    exemplos = {
        '1': exemplo_1_uso_direto,
        '2': exemplo_2_requests_basico,
        '3': exemplo_3_multiplos_tipos,
        '4': exemplo_4_paginacao,
        '5': exemplo_5_tratamento_erros,
        '6': exemplo_6_mapa,
        '7': exemplo_7_cli,
        '8': exemplo_8_batch,
    }
    
    if escolha in exemplos:
        print("\n" + "=" * 60 + "\n")
        exemplos[escolha]()
    else:
        print("Escolha inválida!")
