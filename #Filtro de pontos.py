#Filtro de pontos

escolha = []
escolha = input("Digite o tipo de lixo que deseja descartar:").strip().split(",")
tipos_do_ponto = []
import csv

def ler_pontos_por_tipo_lixo(escolha):
    pontos = {}
    with open("pontos-de-coleta.csv", newline='', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo, skipinitialspace=True)
        for row in leitor:
            if row['tipo_lixo']:
                tipos_do_ponto = [t.strip() for t in row['tipo_lixo'].split(r"\,")]
                if all(t in tipos_do_ponto for t in escolha):
                    pontos[row['id']] = {}
                    pontos[row['id']]['nome'] = row['nome']
                    pontos[row['id']]['latitude'] = row['latitude']
                    pontos[row['id']]['longitude'] = row['longitude']
                    pontos[row['id']]['endereco'] = row['endereco']
    return pontos


pontos_filtrados = ler_pontos_por_tipo_lixo(escolha)
if len(pontos_filtrados) == 0:
    print("Nenhum ponto de coleta encontrado para os tipos de lixo selecionados.")
else:
    print(pontos_filtrados)

