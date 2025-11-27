import csv


def ler_pontos_por_tipo_lixo(tipos_lixo, csv_file="pontos-de-coleta.csv"):
    """
    Filtra pontos de coleta pelos tipos de lixo especificados.
    
    Args:
        tipos_lixo: Lista de tipos de lixo para filtrar
        csv_file: Caminho do arquivo CSV
        
    Returns:
        Dicionário com pontos de coleta filtrados, chaveado por ID
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
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_file}")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo CSV: {str(e)}")
    
    return pontos
