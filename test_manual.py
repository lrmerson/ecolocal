#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste rápido para a API sem precisar de HTTP.
Testa a lógica de negócio diretamente.
"""

from coleta_service import ler_pontos_por_tipo_lixo


def main():
    """Função principal com testes interativos."""
    print("=" * 60)
    print("TESTE INTERATIVO - API de Pontos de Coleta")
    print("=" * 60)
    
    while True:
        print("\nOpções:")
        print("1. Filtrar por tipos de lixo")
        print("2. Sair")
        
        opcao = input("\nEscolha uma opção (1 ou 2): ").strip()
        
        if opcao == '1':
            tipos_input = input("Digite os tipos de lixo (separados por vírgula): ").strip()
            
            if not tipos_input:
                print("Por favor, digite pelo menos um tipo de lixo!")
                continue
            
            tipos = [t.strip() for t in tipos_input.split(',')]
            
            try:
                resultado = ler_pontos_por_tipo_lixo(tipos)
                
                if not resultado:
                    print(f"\n❌ Nenhum ponto encontrado para: {', '.join(tipos)}")
                else:
                    print(f"\n✓ Encontrados {len(resultado)} ponto(s):")
                    print("-" * 60)
                    
                    for ponto_id, ponto in resultado.items():
                        print(f"\nID: {ponto['id']}")
                        print(f"Nome: {ponto['nome']}")
                        print(f"Tipos: {ponto['tipo_lixo']}")
                        print(f"Latitude: {ponto['latitude']}")
                        print(f"Longitude: {ponto['longitude']}")
                        print(f"Endereço: {ponto['endereco']}")
                        print("-" * 60)
                        
            except FileNotFoundError as e:
                print(f"❌ Erro: {e}")
            except Exception as e:
                print(f"❌ Erro ao processar: {e}")
                
        elif opcao == '2':
            print("Até logo!")
            break
        else:
            print("Opção inválida! Digite 1 ou 2.")


if __name__ == '__main__':
    main()
