FROM grafana/grafana:latest

COPY ./compose/local/grafana/provisioning /etc/grafana/provisioning

ENV GF_SECURITY_ADMIN_PASSWORD=admin
ENV GF_SECURITY_ADMIN_USER=admin

EXPOSE 3000
