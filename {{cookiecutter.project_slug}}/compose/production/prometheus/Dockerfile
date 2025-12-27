FROM prom/prometheus:latest

COPY ./compose/production/prometheus/prometheus.yml /etc/prometheus/prometheus.yml
COPY ./compose/production/prometheus/alert-rules.yml /etc/prometheus/alert-rules.yml

EXPOSE 9090
