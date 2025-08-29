#!/usr/bin/env python3
"""
Script de monitoramento para API AliExpress
Monitora memória, CPU e saúde do servidor
"""

import psutil
import requests
import time
import json
import os
from datetime import datetime

# Configurações
API_URL = "https://service-api-aliexpress.mercadodasophia.com.br"
CHECK_INTERVAL = 60  # segundos
ALERT_THRESHOLD = 0.8  # 80%

def check_system_health():
    """Verificar saúde do sistema"""
    try:
        # Memória
        memory = psutil.virtual_memory()
        memory_percent = memory.percent / 100
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent / 100
        
        # Processos Python
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {
            'timestamp': datetime.now().isoformat(),
            'memory': {
                'percent': memory_percent,
                'available': memory.available,
                'total': memory.total
            },
            'cpu': cpu_percent,
            'disk': {
                'percent': disk_percent,
                'free': disk.free,
                'total': disk.total
            },
            'python_processes': python_processes,
            'alerts': []
        }
    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'alerts': ['Erro ao verificar saúde do sistema']
        }

def check_api_health():
    """Verificar saúde da API"""
    try:
        response = requests.get(f"{API_URL}/test", timeout=10)
        if response.status_code == 200:
            return {
                'status': 'healthy',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
        else:
            return {
                'status': 'unhealthy',
                'status_code': response.status_code,
                'error': f'HTTP {response.status_code}'
            }
    except requests.exceptions.Timeout:
        return {
            'status': 'timeout',
            'error': 'API timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def generate_alerts(health_data):
    """Gerar alertas baseados nos dados de saúde"""
    alerts = []
    
    # Alerta de memória
    if health_data['memory']['percent'] > ALERT_THRESHOLD:
        alerts.append(f"⚠️ ALERTA: Memória alta ({health_data['memory']['percent']:.1%})")
    
    # Alerta de CPU
    if health_data['cpu'] > 80:
        alerts.append(f"⚠️ ALERTA: CPU alta ({health_data['cpu']:.1f}%)")
    
    # Alerta de disco
    if health_data['disk']['percent'] > ALERT_THRESHOLD:
        alerts.append(f"⚠️ ALERTA: Disco cheio ({health_data['disk']['percent']:.1%})")
    
    # Alerta de API
    if health_data.get('api_status') != 'healthy':
        alerts.append(f"🚨 ALERTA: API não saudável - {health_data.get('api_error', 'Unknown error')}")
    
    return alerts

def main():
    """Função principal de monitoramento"""
    print("🔍 Iniciando monitoramento da API AliExpress...")
    
    while True:
        try:
            # Verificar saúde do sistema
            system_health = check_system_health()
            
            # Verificar saúde da API
            api_health = check_api_health()
            system_health['api_status'] = api_health
            
            # Gerar alertas
            alerts = generate_alerts(system_health)
            system_health['alerts'] = alerts
            
            # Log dos dados
            print(f"\n📊 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"💾 Memória: {system_health['memory']['percent']:.1%}")
            print(f"🖥️ CPU: {system_health['cpu']:.1f}%")
            print(f"💿 Disco: {system_health['disk']['percent']:.1%}")
            print(f"🌐 API: {api_health['status']}")
            
            if alerts:
                print("🚨 ALERTAS:")
                for alert in alerts:
                    print(f"  {alert}")
            
            # Salvar dados em arquivo (opcional)
            if os.getenv('SAVE_MONITORING_DATA') == 'true':
                with open('monitoring_data.json', 'a') as f:
                    f.write(json.dumps(system_health) + '\n')
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoramento interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
