import csv
import requests
import os
import socket

# Forçar uso de IPv4 apenas para resolver problemas de lentidão no Windows
original_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4_only

# Tentar obter a chave de variável de ambiente, senão usar placeholder
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY", "YOUR_MAPBOX_API_KEY")

# Avisar se a chave não foi configurada
if MAPBOX_API_KEY == "YOUR_MAPBOX_API_KEY":
    print("\n⚠️  AVISO: Chave de API do Mapbox não configurada!")
    print("   Configure a variável de ambiente MAPBOX_API_KEY com seu token Mapbox.")
    print("   Sem a chave, a função de proximidade não funcionará.\n")


# Mapbox Matrix API: max 25 coordinates total per request (1 origin + 24 destinations)
_MAPBOX_BATCH_SIZE = 24


def get_distances_from_mapbox(origin_lat, origin_lon, destinations):
    """
    Chama a Mapbox Matrix API para obter distância e tempo de direção de uma origem
    para múltiplos destinos em uma única requisição (ou em lotes de 24 destinos).

    Args:
        origin_lat: Latitude do usuário
        origin_lon: Longitude do usuário
        destinations: Lista de tuplas (lat, lon)

    Retorna:
        Lista de dicionários com distance_km e duration_min (mesma ordem de destinations)
    """
    if not destinations:
        return []

    # Verificar se a chave de API foi configurada
    if MAPBOX_API_KEY == "YOUR_MAPBOX_API_KEY":
        print("❌ Erro: Chave de API do Mapbox não configurada!")
        return [{"distance_km": None, "duration_min": None}] * len(destinations)

    results = []

    # Processar em lotes de _MAPBOX_BATCH_SIZE destinos por requisição
    for batch_start in range(0, len(destinations), _MAPBOX_BATCH_SIZE):
        batch = destinations[batch_start: batch_start + _MAPBOX_BATCH_SIZE]

        # Montar string de coordenadas: origem primeiro (lon,lat), depois destinos
        # A API Mapbox usa a ordem longitude,latitude
        coords_parts = [f"{origin_lon},{origin_lat}"]
        coords_parts += [f"{dest_lon},{dest_lat}" for dest_lat, dest_lon in batch]
        coordinates_str = ";".join(coords_parts)

        # Índices dos destinos (1 até len(batch))
        destination_indices = ";".join(str(i) for i in range(1, len(batch) + 1))

        url = (
            f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/{coordinates_str}"
            f"?sources=0"
            f"&destinations={destination_indices}"
            f"&annotations=duration,distance"
            f"&access_token={MAPBOX_API_KEY}"
        )

        print(f"Debug - Chamando Mapbox Matrix API para lote de {len(batch)} destinos "
              f"(índices {batch_start}–{batch_start + len(batch) - 1})")

        try:
            resposta = requests.get(
                url,
                timeout=10,
                proxies={"http": None, "https": None}  # Desabilita detecção automática de proxy
            ).json()

            if resposta.get("code") != "Ok":
                print(f"⚠️  Aviso: Mapbox retornou código inesperado: {resposta.get('code')}")
                results += [{"distance_km": None, "duration_min": None}] * len(batch)
                continue

            # durations e distances são matrizes [sources][destinations]
            # Como temos 1 source, pegamos a primeira (e única) linha
            durations_row = resposta.get("durations", [[]])[0]   # segundos
            distances_row = resposta.get("distances", [[]])[0]   # metros

            for i in range(len(batch)):
                dur_s = durations_row[i] if i < len(durations_row) else None
                dist_m = distances_row[i] if i < len(distances_row) else None

                if dur_s is not None and dist_m is not None:
                    results.append({
                        "distance_km": dist_m / 1000,
                        "duration_min": round(dur_s / 60)
                    })
                    print(f"  ✅ Destino {batch_start + i}: {dist_m/1000:.2f} km, {dur_s/60:.1f} min")
                else:
                    print(f"  ⚠️  Destino {batch_start + i}: sem dados de rota")
                    results.append({"distance_km": None, "duration_min": None})

        except Exception as e:
            print(f"❌ Erro ao chamar Mapbox Matrix API: {str(e)}")
            results += [{"distance_km": None, "duration_min": None}] * len(batch)

    return results




def enriquecer_pontos_com_distancias(pontos, user_lat, user_lon):
    """
    Adiciona distance_km e duration_min a cada ponto usando a Mapbox Matrix API.

    Todos os destinos filtrados são enviados de uma vez (em lotes de 24 se necessário),
    eliminando a necessidade de uma requisição por destino.

    Args:
        pontos: Dicionário de pontos {id: {latitude, longitude, ...}}
        user_lat: Latitude do usuário
        user_lon: Longitude do usuário

    Retorna:
        Dicionário pontos atualizado com distance_km e duration_min adicionados
    """
    if not pontos or not user_lat or not user_lon:
        return pontos

    # Extrair destinos como lista de tuplas (lat, lon), preservando a ordem
    destinations = [(ponto['latitude'], ponto['longitude']) for ponto in pontos.values()]

    # Obter distâncias via Mapbox Matrix API (em lotes de até 24 destinos)
    print(f"Chamando Mapbox Matrix API para {len(destinations)} pontos...")
    results = get_distances_from_mapbox(user_lat, user_lon, destinations)

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
        # Se duration_min for None, colocar no final (infinito)
        duration = tupla[1]
        return duration if duration is not None else float('inf')
    
    def pontos_ordenados(pontos, n):
        pontos_ordem = []
        for id in pontos:
            dist_ponto = (id, pontos[id].get('duration_min', float('inf')))
            pontos_ordem.append(dist_ponto)
        pontos_ordem.sort(key=ordem_dist)
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


def ler_todos_pontos(csv_file="pontos-de-coleta.csv"):
    """
    Lê todos os pontos do CSV sem filtros.
    
    Args:
        csv_file: Caminho do arquivo CSV
        
    Retorna:
        Dicionário com todos os pontos, chaveado por ID
    """
    pontos = {}
    try:
        with open(csv_file, newline='', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo, skipinitialspace=True)
            for row in leitor:
                if row['tipo_lixo']:
                    pontos[row['id']] = {
                        'id': row['id'],
                        'nome': row['nome'],
                        'tipo_lixo': row['tipo_lixo'],
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'endereco': row['endereco']
                    }
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_file}")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo CSV: {str(e)}")
    
    return pontos