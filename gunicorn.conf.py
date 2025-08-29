# Configuração Gunicorn para otimizar memória e evitar SIGKILL
import multiprocessing
import os

# Configurações básicas
bind = "0.0.0.0:5000"
workers = 2  # Reduzir número de workers para economizar memória
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Configurações de memória
worker_tmp_dir = "/dev/shm"  # Usar RAM para arquivos temporários
preload_app = True  # Pré-carregar aplicação

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de reinicialização
graceful_timeout = 30
restart_workers = True

# Configurações de monitoramento
def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)

# Configurações de memória específicas
def on_starting(server):
    server.log.info("Starting server with memory optimization")

def on_reload(server):
    server.log.info("Reloading server")

def on_exit(server):
    server.log.info("Server exiting")
