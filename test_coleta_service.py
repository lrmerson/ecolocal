import unittest
import os
import csv
import tempfile
from coleta_service import ler_pontos_por_tipo_lixo


class TestColetaService(unittest.TestCase):
    """Testes unitários para o serviço de coleta de pontos."""
    
    @classmethod
    def setUpClass(cls):
        """Criar um arquivo CSV de teste."""
        cls.temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                                    suffix='.csv', encoding='utf-8')
        
        # Escrever dados de teste
        writer = csv.writer(cls.temp_csv)
        writer.writerow(['id', 'nome', 'tipo_lixo', 'latitude', 'longitude', 'endereco'])
        writer.writerow(['001', 'Ponto A', 'eletroeletronicos\\,pilhas', '-15.1', '-47.1', 'Endereco A'])
        writer.writerow(['002', 'Ponto B', 'eletrodomesticos', '-15.2', '-47.2', 'Endereco B'])
        writer.writerow(['003', 'Ponto C', 'eletroeletronicos\\,eletrodomesticos\\,pilhas', '-15.3', '-47.3', 'Endereco C'])
        writer.writerow(['004', 'Ponto D', 'lampadas\\,pilhas', '-15.4', '-47.4', 'Endereco D'])
        
        cls.temp_csv.close()
    
    @classmethod
    def tearDownClass(cls):
        """Remover arquivo CSV de teste."""
        if os.path.exists(cls.temp_csv.name):
            os.unlink(cls.temp_csv.name)
    
    def test_filtrar_por_um_tipo(self):
        """Teste: filtrar pontos por um único tipo de lixo."""
        resultado = ler_pontos_por_tipo_lixo(['pilhas'], self.temp_csv.name)
        
        # Deve retornar 3 pontos que têm pilhas
        self.assertEqual(len(resultado), 3)
        self.assertIn('001', resultado)
        self.assertIn('003', resultado)
        self.assertIn('004', resultado)
    
    def test_filtrar_por_multiplos_tipos(self):
        """Teste: filtrar pontos que têm TODOS os tipos especificados."""
        resultado = ler_pontos_por_tipo_lixo(['eletroeletronicos', 'pilhas'], self.temp_csv.name)
        
        # Deve retornar apenas pontos que têm AMBOS eletroeletronicos E pilhas
        self.assertEqual(len(resultado), 2)
        self.assertIn('001', resultado)
        self.assertIn('003', resultado)
    
    def test_filtrar_com_tipo_inexistente(self):
        """Teste: filtrar por tipo que não existe."""
        resultado = ler_pontos_por_tipo_lixo(['tipo_inexistente'], self.temp_csv.name)
        
        # Deve retornar vazio
        self.assertEqual(len(resultado), 0)
    
    def test_filtrar_com_lista_vazia(self):
        """Teste: filtrar com lista vazia de tipos."""
        resultado = ler_pontos_por_tipo_lixo([], self.temp_csv.name)
        
        # Deve retornar vazio
        self.assertEqual(len(resultado), 0)
    
    def test_filtrar_com_None(self):
        """Teste: filtrar com None."""
        resultado = ler_pontos_por_tipo_lixo(None, self.temp_csv.name)
        
        # Deve retornar vazio
        self.assertEqual(len(resultado), 0)
    
    def test_estrutura_dados_retornados(self):
        """Teste: verificar se a estrutura dos dados retornados é correta."""
        resultado = ler_pontos_por_tipo_lixo(['pilhas'], self.temp_csv.name)
        
        # Verificar estrutura de um ponto
        ponto = resultado['001']
        self.assertIn('id', ponto)
        self.assertIn('nome', ponto)
        self.assertIn('tipo_lixo', ponto)
        self.assertIn('latitude', ponto)
        self.assertIn('longitude', ponto)
        self.assertIn('endereco', ponto)
        
        # Verificar tipos de dados
        self.assertEqual(ponto['id'], '001')
        self.assertEqual(ponto['nome'], 'Ponto A')
        self.assertIsInstance(ponto['latitude'], float)
        self.assertIsInstance(ponto['longitude'], float)
    
    def test_case_insensitive(self):
        """Teste: verificar se o filtro é case-insensitive."""
        resultado1 = ler_pontos_por_tipo_lixo(['PILHAS'], self.temp_csv.name)
        resultado2 = ler_pontos_por_tipo_lixo(['pilhas'], self.temp_csv.name)
        resultado3 = ler_pontos_por_tipo_lixo(['Pilhas'], self.temp_csv.name)
        
        # Todos devem retornar o mesmo resultado
        self.assertEqual(len(resultado1), len(resultado2))
        self.assertEqual(len(resultado2), len(resultado3))
    
    def test_arquivo_nao_encontrado(self):
        """Teste: comportamento quando arquivo CSV não existe."""
        with self.assertRaises(FileNotFoundError):
            ler_pontos_por_tipo_lixo(['pilhas'], 'arquivo_inexistente.csv')
    
    def test_tipos_com_espacos(self):
        """Teste: filtro com tipos que têm espaços em branco."""
        resultado = ler_pontos_por_tipo_lixo(['  pilhas  ', ' eletroeletronicos '], self.temp_csv.name)
        
        # Deve remover espaços e encontrar os pontos
        self.assertEqual(len(resultado), 2)
        self.assertIn('001', resultado)
        self.assertIn('003', resultado)


if __name__ == '__main__':
    unittest.main()
