from flask import Flask, request, jsonify
from coleta_service import ler_pontos_por_tipo_lixo

app = Flask(__name__)


@app.route('/api/coleta-pontos', methods=['GET'])
def get_coleta_pontos():
    """
    Endpoint REST GET para filtrar pontos de coleta por tipo de lixo.
    
    Query Parameters:
        tipos: Lista de tipos de lixo separados por vírgula (obrigatório)
               Exemplo: ?tipos=eletroeletronicos,pilhas
    
    Returns:
        JSON com pontos de coleta filtrados
        
    Status Codes:
        200: Sucesso
        400: Parâmetro 'tipos' não fornecido
        500: Erro interno do servidor
    """
    try:
        # Obter parâmetro de query 'tipos'
        tipos_param = request.args.get('tipos')
        
        if not tipos_param:
            return jsonify({
                'error': 'Parâmetro "tipos" é obrigatório',
                'exemplo': '/api/coleta-pontos?tipos=eletroeletronicos,pilhas'
            }), 400
        
        # Dividir e limpar os tipos
        tipos_lixo = [t.strip() for t in tipos_param.split(',')]
        
        # Chamar o serviço
        pontos = ler_pontos_por_tipo_lixo(tipos_lixo)
        
        # Formatar resposta
        response = {
            'total': len(pontos),
            'tipos_filtrados': tipos_lixo,
            'pontos': list(pontos.values()) if pontos else []
        }
        
        return jsonify(response), 200
        
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500


@app.route('/api/coleta-pontos', methods=['GET'])
def list_coleta_pontos():
    """
    Endpoint REST GET para listar todos os pontos de coleta.
    
    Query Parameters (opcional):
        limit: Número máximo de resultados (padrão: todos)
        offset: Número de resultados a pular (padrão: 0)
    
    Returns:
        JSON com lista de pontos de coleta
    """
    try:
        import csv
        pontos = []
        
        with open('pontos-de-coleta.csv', newline='', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo, skipinitialspace=True)
            for row in leitor:
                if row['tipo_lixo']:
                    pontos.append({
                        'id': row['id'],
                        'nome': row['nome'],
                        'tipo_lixo': row['tipo_lixo'],
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'endereco': row['endereco']
                    })
        
        # Aplicar paginação se solicitado
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        if limit:
            pontos = pontos[offset:offset + limit]
        elif offset:
            pontos = pontos[offset:]
        
        response = {
            'total': len(pontos),
            'pontos': pontos
        }
        
        return jsonify(response), 200
        
    except FileNotFoundError:
        return jsonify({'error': 'Arquivo CSV não encontrado'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
