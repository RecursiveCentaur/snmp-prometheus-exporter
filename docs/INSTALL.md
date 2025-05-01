# Installationsanleitung

## Voraussetzungen

- Python 3 (>= 3.6)
- pip: `python3 -m pip install --upgrade pip`
- Netzwerkkonnektivität zum SNMP-Gerät
- Systemd (unter Linux)

## Bibliotheken installieren

```bash
pip3 install prometheus_client pysnmp


## Repository klonen

git clone https://github.com/recursivecentaur/snmp-prometheus-exporter.git
cd snmp-prometheus-exporter


## systemd-Service einrichten

sudo cp snmp_exporter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now snmp_exporter


## Prometheus konfigurieren
In deiner prometheus.yml:

scrape_configs:
  - job_name: 'snmp_exporter'
    static_configs:
      - targets: ['<DEIN_SERVER>:9116']


Anschließend Prometheus neu starten.


## Grafana-Dashboard importieren

    In Grafana → Dashboards → Import

    JSON-Datei grafana-dashboard.json hochladen

    Prometheus-Data-Source auswählen

    Dashboard speichern und ansehen