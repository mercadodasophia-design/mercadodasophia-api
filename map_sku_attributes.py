#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time
from collections import defaultdict

# Configurações
API_BASE_URL = "https://mercadodasophia-api.onrender.com/api"

# Categorias mais comuns do AliExpress (IDs reais)
COMMON_CATEGORIES = {
    "200000801": "Women's Clothing",
    "200000802": "Men's Clothing", 
    "200000803": "Kids & Baby Clothing",
    "200000804": "Shoes",
    "200000805": "Bags & Accessories",
    "200000806": "Jewelry & Watches",
    "200000807": "Beauty & Health",
    "200000808": "Home & Garden",
    "200000809": "Sports & Entertainment",
    "200000810": "Automotive",
    "200000811": "Toys & Hobbies",
    "200000812": "Electronics",
    "200000813": "Computer & Office",
    "200000814": "Phones & Telecommunications",
    "200000815": "Lights & Lighting",
    "200000816": "Tools & Hardware",
    "200000817": "Security & Protection",
    "200000818": "Mother & Kids",
    "200000819": "Pet Supplies",
    "200000820": "Wedding & Events"
}

def get_sku_attributes(category_id):
    """Consultar atributos SKU de uma categoria"""
    try:
        url = f"{API_BASE_URL}/aliexpress/sku-attributes/{category_id}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data['data']
            else:
                print(f"❌ Erro na API para categoria {category_id}: {data.get('message', 'Erro desconhecido')}")
                return None
        else:
            print(f"❌ HTTP {response.status_code} para categoria {category_id}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao consultar categoria {category_id}: {e}")
        return None

def analyze_sku_attributes():
    """Analisar e mapear atributos SKU de todas as categorias"""
    print("🔍 Iniciando mapeamento de atributos SKU...")
    print(f"📊 Total de categorias para analisar: {len(COMMON_CATEGORIES)}")
    print("=" * 80)
    
    # Dicionários para armazenar os mapeamentos
    sku_name_mapping = defaultdict(set)  # Nome do atributo -> valores possíveis
    sku_value_mapping = defaultdict(set)  # Valor do atributo -> categorias onde aparece
    common_attribute_mapping = defaultdict(set)  # Atributos comuns
    
    successful_categories = 0
    failed_categories = 0
    
    for category_id, category_name in COMMON_CATEGORIES.items():
        print(f"\n🔍 Analisando categoria: {category_name} (ID: {category_id})")
        
        # Consultar atributos SKU
        data = get_sku_attributes(category_id)
        
        if data:
            successful_categories += 1
            
            # Processar atributos SKU
            sku_attributes = data.get('sku_attributes', [])
            print(f"  📦 Atributos SKU encontrados: {len(sku_attributes)}")
            
            for attr in sku_attributes:
                attr_name = attr.get('aliexpress_sku_name', 'Unknown')
                attr_values = attr.get('aliexpress_sku_value_list', [])
                
                # Mapear nome do atributo
                sku_name_mapping[attr_name].add(category_id)
                
                # Mapear valores do atributo
                for value_obj in attr_values:
                    value_name = value_obj.get('aliexpress_sku_value_name', 'Unknown')
                    sku_value_mapping[value_name].add(category_id)
                
                print(f"    - {attr_name}: {len(attr_values)} valores")
            
            # Processar atributos comuns
            common_attributes = data.get('common_attributes', [])
            print(f"  📋 Atributos comuns encontrados: {len(common_attributes)}")
            
            for attr in common_attributes:
                attr_name = attr.get('aliexpress_common_attribute_name', 'Unknown')
                attr_values = attr.get('aliexpress_common_attribute_value_list', [])
                
                # Mapear atributos comuns
                common_attribute_mapping[attr_name].add(category_id)
                
                # Mapear valores dos atributos comuns
                for value_obj in attr_values:
                    value_name = value_obj.get('aliexpress_common_attribute_value', 'Unknown')
                    sku_value_mapping[value_name].add(category_id)
                
                print(f"    - {attr_name}: {len(attr_values)} valores")
            
        else:
            failed_categories += 1
            print(f"  ❌ Falha ao obter dados da categoria {category_id}")
        
        # Rate limiting
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print("📊 RESUMO DO MAPEAMENTO")
    print("=" * 80)
    print(f"✅ Categorias processadas com sucesso: {successful_categories}")
    print(f"❌ Categorias com falha: {failed_categories}")
    print(f"📦 Tipos de atributos SKU únicos: {len(sku_name_mapping)}")
    print(f"🎨 Valores de atributos únicos: {len(sku_value_mapping)}")
    print(f"📋 Tipos de atributos comuns únicos: {len(common_attribute_mapping)}")
    
    # Salvar mapeamentos em arquivos
    save_mappings(sku_name_mapping, sku_value_mapping, common_attribute_mapping)
    
    return {
        'sku_names': dict(sku_name_mapping),
        'sku_values': dict(sku_value_mapping),
        'common_attributes': dict(common_attribute_mapping)
    }

def save_mappings(sku_name_mapping, sku_value_mapping, common_attribute_mapping):
    """Salvar mapeamentos em arquivos JSON"""
    
    # Salvar mapeamento de nomes de atributos SKU
    sku_names_data = {
        'description': 'Mapeamento de nomes de atributos SKU por categoria',
        'total_sku_names': len(sku_name_mapping),
        'mapping': {name: list(categories) for name, categories in sku_name_mapping.items()}
    }
    
    with open('sku_names_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(sku_names_data, f, indent=2, ensure_ascii=False)
    
    # Salvar mapeamento de valores de atributos
    sku_values_data = {
        'description': 'Mapeamento de valores de atributos por categoria',
        'total_unique_values': len(sku_value_mapping),
        'mapping': {value: list(categories) for value, categories in sku_value_mapping.items()}
    }
    
    with open('sku_values_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(sku_values_data, f, indent=2, ensure_ascii=False)
    
    # Salvar mapeamento de atributos comuns
    common_attrs_data = {
        'description': 'Mapeamento de atributos comuns por categoria',
        'total_common_attributes': len(common_attribute_mapping),
        'mapping': {name: list(categories) for name, categories in common_attribute_mapping.items()}
    }
    
    with open('common_attributes_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(common_attrs_data, f, indent=2, ensure_ascii=False)
    
    print("\n💾 Mapeamentos salvos em:")
    print("  - sku_names_mapping.json")
    print("  - sku_values_mapping.json") 
    print("  - common_attributes_mapping.json")

def generate_translation_dictionary():
    """Gerar dicionário de tradução baseado nos mapeamentos"""
    print("\n🔤 Gerando dicionário de tradução...")
    
    # Carregar mapeamentos
    try:
        with open('sku_names_mapping.json', 'r', encoding='utf-8') as f:
            sku_names = json.load(f)
        
        with open('sku_values_mapping.json', 'r', encoding='utf-8') as f:
            sku_values = json.load(f)
            
    except FileNotFoundError:
        print("❌ Arquivos de mapeamento não encontrados. Execute analyze_sku_attributes() primeiro.")
        return
    
    # Criar dicionário de tradução
    translation_dict = {
        'sku_names': {},
        'sku_values': {},
        'common_attributes': {}
    }
    
    # Traduzir nomes de atributos SKU
    for attr_name in sku_names['mapping'].keys():
        # Mapear nomes comuns
        if 'color' in attr_name.lower():
            translation_dict['sku_names'][attr_name] = 'Cor'
        elif 'size' in attr_name.lower():
            translation_dict['sku_names'][attr_name] = 'Tamanho'
        elif 'style' in attr_name.lower():
            translation_dict['sku_names'][attr_name] = 'Estilo'
        elif 'material' in attr_name.lower():
            translation_dict['sku_names'][attr_name] = 'Material'
        elif 'pattern' in attr_name.lower():
            translation_dict['sku_names'][attr_name] = 'Padrão'
        elif 'brand' in attr_name.lower():
            translation_dict['sku_names'][attr_name] = 'Marca'
        else:
            translation_dict['sku_names'][attr_name] = attr_name  # Manter original
    
    # Traduzir valores de atributos
    for value_name in sku_values['mapping'].keys():
        # Mapear valores comuns de cores
        if value_name.lower() in ['red', 'vermelho']:
            translation_dict['sku_values'][value_name] = 'Vermelho'
        elif value_name.lower() in ['blue', 'azul']:
            translation_dict['sku_values'][value_name] = 'Azul'
        elif value_name.lower() in ['green', 'verde']:
            translation_dict['sku_values'][value_name] = 'Verde'
        elif value_name.lower() in ['yellow', 'amarelo']:
            translation_dict['sku_values'][value_name] = 'Amarelo'
        elif value_name.lower() in ['black', 'preto']:
            translation_dict['sku_values'][value_name] = 'Preto'
        elif value_name.lower() in ['white', 'branco']:
            translation_dict['sku_values'][value_name] = 'Branco'
        elif value_name.lower() in ['pink', 'rosa']:
            translation_dict['sku_values'][value_name] = 'Rosa'
        elif value_name.lower() in ['purple', 'roxo']:
            translation_dict['sku_values'][value_name] = 'Roxo'
        elif value_name.lower() in ['orange', 'laranja']:
            translation_dict['sku_values'][value_name] = 'Laranja'
        elif value_name.lower() in ['brown', 'marrom']:
            translation_dict['sku_values'][value_name] = 'Marrom'
        elif value_name.lower() in ['gray', 'grey', 'cinza']:
            translation_dict['sku_values'][value_name] = 'Cinza'
        else:
            translation_dict['sku_values'][value_name] = value_name  # Manter original
    
    # Salvar dicionário de tradução
    with open('translation_dictionary.json', 'w', encoding='utf-8') as f:
        json.dump(translation_dict, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dicionário de tradução gerado com:")
    print(f"  - {len(translation_dict['sku_names'])} nomes de atributos")
    print(f"  - {len(translation_dict['sku_values'])} valores de atributos")
    print("  - Salvo em: translation_dictionary.json")

if __name__ == "__main__":
    print("🚀 Iniciando mapeamento de atributos SKU do AliExpress")
    print("=" * 80)
    
    # Executar análise
    mappings = analyze_sku_attributes()
    
    # Gerar dicionário de tradução
    generate_translation_dictionary()
    
    print("\n🎉 Processo concluído!")
    print("📁 Arquivos gerados:")
    print("  - sku_names_mapping.json")
    print("  - sku_values_mapping.json")
    print("  - common_attributes_mapping.json")
    print("  - translation_dictionary.json") 