FROM prom/prometheus:v2.54.1

COPY infra/render/prometheus/prometheus.tmpl.yml /etc/prometheus/prometheus.tmpl.yml
COPY infra/render/prometheus/start.sh /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]