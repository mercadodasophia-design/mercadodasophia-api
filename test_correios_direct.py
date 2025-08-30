import requests
import xml.etree.ElementTree as ET

def test_correios_direct():
    """Teste direto da API dos Correios"""
    
    # Parâmetros para API dos Correios
    correios_params = {
        'nCdEmpresa': '',
        'sDsSenha': '',
        'nCdServico': '04510',  # PAC
        'sCepOrigem': '01001000',  # CEP de origem
        'sCepDestino': '61771800',
        'nVlPeso': '0.5',
        'nCdFormato': '1',  # Caixa/Pacote
        'nVlComprimento': '20',
        'nVlAltura': '10',
        'nVlLargura': '15',
        'nVlDiametro': '0',
        'sCdMaoPropria': 'N',
        'nVlValorDeclarado': '0',
        'sCdAvisoRecebimento': 'N'
    }
    
    print("=== TESTE DIRETO: API dos Correios ===")
    print(f"CEP Destino: {correios_params['sCepDestino']}")
    print(f"Peso: {correios_params['nVlPeso']}kg")
    
    try:
        response = requests.get('https://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx/CalcPrecoPrazo', 
                               params=correios_params, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            # Parsear resposta XML dos Correios
            root = ET.fromstring(response.text)
            
            print(f"\n✅ Resposta XML parseada:")
            for servico in root.findall('.//cServico'):
                codigo = servico.find('Codigo').text if servico.find('Codigo') is not None else 'N/A'
                valor = servico.find('Valor').text if servico.find('Valor') is not None else 'N/A'
                prazo = servico.find('PrazoEntrega').text if servico.find('PrazoEntrega') is not None else 'N/A'
                erro = servico.find('Erro').text if servico.find('Erro') is not None else '0'
                
                print(f"  Código: {codigo}")
                print(f"  Valor: {valor}")
                print(f"  Prazo: {prazo} dias")
                print(f"  Erro: {erro}")
                print("  ---")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_correios_direct()
