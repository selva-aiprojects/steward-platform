FROM grafana/grafana:11.2.0

# Disable login form for demo ease - optional, remove if you want auth
ENV GF_AUTH_ANONYMOUS_ENABLED=true
ENV GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
ENV GF_SECURITY_ALLOW_EMBEDDING=true

# Copy provisioning
COPY infra/observability/grafana/provisioning /etc/grafana/provisioning
COPY infra/observability/grafana/dashboards /var/lib/grafana/dashboards

# Use a custom datasource for Render to point to the correct internal service name
COPY infra/render/grafana/datasource.render.yml /etc/grafana/provisioning/datasources/datasource.yml
