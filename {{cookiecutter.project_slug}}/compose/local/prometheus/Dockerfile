FROM prom/prometheus:latest

COPY ./compose/local/prometheus/prometheus.yml /etc/prometheus/prometheus.yml
COPY ./compose/local/prometheus/alert-rules.yml /etc/prometheus/alert-rules.yml

EXPOSE 9090
