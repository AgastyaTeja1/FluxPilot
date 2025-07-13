# serving/gunicorn_conf.py

# Gunicorn configuration for production
# Save as: fluxpilot-llm-pipeline/serving/gunicorn_conf.py

bind = "0.0.0.0:8080"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
accesslog = "-"        # stdout
errorlog = "-"         # stdout
loglevel = "info"
