import csv
import requests

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"


def get_distances_from_google(origin_lat, origin_lon, destinations):
    """
    Chama a API Google Distance Matrix para obter distância e tempo de direção.
    
    Args:
        origin_lat: Latitude do usuário
        origin_lon: Longitude do usuário
        destinations: Lista de tuplas (lat, lon)
    
    Retorna:
        Lista de dicionários com distance_km e duration_min
    """
    if not destinations:
        return []
    
    origin = f"{origin_lat},{origin_lon}"
    dest_str = "|".join([f"{lat},{lon}" for lat, lon in destinations])
    
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    params = {
        "origins": origin,
        "destinations": dest_str,
        "mode": "driving",
        "units": "metric",
        "key": GOOGLE_API_KEY
    }
    
    try:
        resposta = requests.get(url, params=params).json()
        
        if resposta.get("status") != "OK":
            raise Exception(f"Erro na API Google: {resposta.get('status')}")
        
        results = []
        elements = resposta["rows"][0]["elements"]
        
        for element in elements:
            if element["status"] == "OK":
                dist_m = element["distance"]["value"]
                dur_s = element["duration"]["value"]
                results.append({
                    "distance_km": dist_m / 1000,
                    "duration_min": dur_s / 60
                })
            else:
                results.append({
                    "distance_km": None,
                    "duration_min": None
                })
        
        return results
    
    except Exception as e:
        print(f"Erro ao chamar API Google: {str(e)}")
        return [{"distance_km": None, "duration_min": None}] * len(destinations)


def enriquecer_pontos_com_distancias(pontos, user_lat, user_lon):
    """
    Adiciona distance_km e duration_min a cada ponto usando API Google.
    Trata o limite de 25 destinos da API com chunking.
    
    Args:
        pontos: Dicionário de pontos {id: {latitude, longitude, ...}}
        user_lat: Latitude do usuário
        user_lon: Longitude do usuário
    
    Retorna:
        Dicionário pontos atualizado com distance_km e duration_min adicionados
    """
    if not pontos or not user_lat or not user_lon:
        return pontos
    
    # Extrair destinos como lista de tuplas (lat, lon)
    destinations = [(ponto['latitude'], ponto['longitude']) for ponto in pontos.values()]
    
    # Obter distâncias da API Google (trata limite de 25 pontos com chunking)
    results = []
    for i in range(0, len(destinations), 25):
        chunk = destinations[i:i+25]
        print(f"Chamando API Google para lote {i//25 + 1}, {len(chunk)} pontos...")
        chunk_results = get_distances_from_google(user_lat, user_lon, chunk)
        results.extend(chunk_results)
    
    # Adicionar distância e duração a cada ponto
    ponto_list = list(pontos.items())
    for (id_ponto, ponto), result in zip(ponto_list, results):
        ponto['distance_km'] = result['distance_km']
        ponto['duration_min'] = result['duration_min']
    
    return pontos


def ler_pontos_por_tipo_lixo(tipos_lixo, user_lat=None, user_lon=None, n=None, csv_file="pontos-de-coleta.csv"):
    """
    Filtra pontos de coleta pelos tipos de lixo especificados.
    Opcionalmente, calcula distância e tempo de direção do usuário e retorna os N mais próximos.
    
    Args:
        tipos_lixo: Lista de tipos de lixo para filtrar
        user_lat: Latitude do usuário (opcional, para calcular proximidade)
        user_lon: Longitude do usuário (opcional, para calcular proximidade)
        n: Número de pontos mais próximos a retornar (opcional)
        csv_file: Caminho do arquivo CSV
        
    Retorna:
        Dicionário com pontos de coleta filtrados, chaveado por ID
        Se user_lat/user_lon fornecidos: inclui distance_km e duration_min
    """
    if not tipos_lixo:
        return {}
    
    # Limpar e normalizar os tipos de lixo da entrada
    tipos_lixo_normalizados = [t.strip().lower() for t in tipos_lixo]
    
    pontos = {}
    try:
        with open(csv_file, newline='', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo, skipinitialspace=True)
            for row in leitor:
                if row['tipo_lixo']:
                    # Dividir os tipos pelo separador \,
                    tipos_do_ponto = [t.strip().lower() for t in row['tipo_lixo'].split(r"\,")]
                    
                    # Verificar se todos os tipos solicitados estão presentes no ponto
                    if all(t in tipos_do_ponto for t in tipos_lixo_normalizados):
                        pontos[row['id']] = {
                            'id': row['id'],
                            'nome': row['nome'],
                            'tipo_lixo': row['tipo_lixo'],
                            'latitude': float(row['latitude']),
                            'longitude': float(row['longitude']),
                            'endereco': row['endereco']
                        }
        # Se user_lat e user_lon forem fornecidos, enriquecer com distâncias do Google API
        if user_lat and user_lon:
            pontos = enriquecer_pontos_com_distancias(pontos, user_lat, user_lon)
        
        # Ordenar pelos N mais próximos se solicitado
        if user_lat and user_lon and n:
            pontos = pontos_mais_proximos(pontos, n)
                        
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_file}")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo CSV: {str(e)}")
    
    return pontos

def pontos_mais_proximos(pontos, n):
    """
    Ordena pontos pelo tempo de direção (quando disponível) e retorna os N mais próximos.
    
    Args:
        pontos: Dicionário de pontos com duração calculada
        n: Número de pontos a retornar
        
    Retorna:
        Dicionário com até N pontos ordenados por proximidade
    """
    if not pontos or n <= 0:
        return {}
    
    def ordem_dist(tupla):
        return tupla[1]
    
    def pontos_ordenados(pontos, n):
        pontos_ordem = []
        for id in pontos:
            dist_ponto = (id, pontos[id].get('duration_min', float('inf')))
            pontos_ordem.append(dist_ponto)
        pontos_ordem.sort(key= ordem_dist)
        if len(pontos_ordem) < n:
            return pontos_ordem
        return pontos_ordem[:n]
                        
    def refinar_pontos(pontos, pontos_ordenados):
        pontos_refinados = {}
        for tupla in pontos_ordenados:
            id_ponto = tupla[0]
            pontos_refinados[id_ponto] = pontos[id_ponto]
        return pontos_refinados
    return refinar_pontos(pontos, pontos_ordenados(pontos, n))