# SNMP Prometheus Exporter

Dieser kleine Python-Exporter fragt per SNMP deinen Switch ab und liefert  
die Daten unter `http://<SERVER>:9116/metrics` im Prometheus-Format aus.

## Inhalt

- **snmp_exporter.py** – Das Hauptskript (pysnmp + prometheus_client)  
- **grafana-dashboard.json** – Fertiges Dashboard für Grafana  
- **prometheus.yml** – Beispiel-Scrape-Konfiguration  
- **snmp_exporter.service** – systemd-Unit  
- **docs/INSTALL.md** – Detaillierte Installations- und Betriebshinweise  

## Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/<dein-user>/snmp-prometheus-exporter.git
cd snmp-prometheus-exporter

# 2. Abhängigkeiten installieren
pip3 install prometheus_client pysnmp

# 3. systemd-Service installieren
sudo cp snmp_exporter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now snmp_exporter

# 4. Prometheus konfigurieren
#    In prometheus.yml unter scrape_configs hinzufügen:
#
#    - job_name: 'snmp_exporter'
#      static_configs:
#        - targets: ['<SERVER>:9116']
#
#    Anschließend Prometheus neu starten.

# 5. Grafana-Dashboard importieren
#    Grafana → Dashboards → Import → grafana-dashboard.json

# Fertig! → http://<SERVER>:9116/metrics liefert jetzt deine SNMP-Metriken.
