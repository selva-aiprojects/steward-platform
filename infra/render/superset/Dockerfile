FROM apache/superset:4.1.2

USER root
COPY infra/render/superset/superset_config.py /app/pythonpath/superset_config.py
COPY infra/render/superset/start.sh /app/start.sh
RUN chmod +x /app/start.sh

USER superset
ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py
CMD ["/app/start.sh"]

