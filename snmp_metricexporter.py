#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SNMP-Metrikexporter für Prometheus
# Version: 1.1.0
# Datum: 2025-05-01
# Autor: Matthias Machinek
#
# Beschreibung:
# Dieses Python-Skript liest ausgewählte SNMP-Daten (OID-basiert) mithilfe der pysnmp-Bibliothek 
# direkt von einem Netzwerkgerät aus, konvertiert diese in Prometheus-kompatible Metriken und 
# stellt sie über einen eingebauten HTTP-Server (Port 9116) bereit.
#
# Es werden keine externen MIB-Dateien benötigt – alle OIDs werden rein numerisch angesprochen.
# Dies ist nützlich, wenn z. B. der Prometheus SNMP-Exporter mit generator.yml nicht einsatzfähig ist,
# oder eine kleinere, leichtgewichtige Lösung gewünscht ist.
#
# Changelog:
# - 1.0.0: Erste Version mit Flask-Exporter und snmpwalk-Abfrage
# - 1.0.1: Parserstabilität und Fehlerbehandlung verbessert
# - 1.0.2: Umstieg auf prometheus_client, HTTP-Server direkt integriert
# - 1.1.0: snmpwalk durch direkte pysnmp-Abfragen ersetzt, volle Kontrolle über SNMP-Parsing,
#          mehr Kommentare und bessere Struktur für Wartbarkeit
#
"""
SNMP-Metrikexporter – Erfasst Schnittstellenstatistiken via SNMP und 
exportiert sie für Prometheus.
"""
import time
from prometheus_client import start_http_server, Info, Gauge
from pysnmp.hlapi import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, nextCmd
)

# Gerätekonfiguration (Platzhalter-Name und SNMP-Zugangsdaten)
geraete_bezeichnung = "Switch-Schul_IT-Aruba-6100" #Platzhalter für 
community_string = 'schulit'
snmp_host = '10.10.240.79'   # IP-Adresse des SNMP-Geräts
snmp_port = 161

# Prometheus-Metriken definieren
snmp_in = Gauge(
    'snmp_if_in_octets',
    'Eingehender Netzwerkverkehr (Octets) je Schnittstelle',
    ['geraet', 'interface', 'alias', 'beschreibung']
)
snmp_out = Gauge(
    'snmp_if_out_octets',
    'Ausgehender Netzwerkverkehr (Octets) je Schnittstelle',
    ['geraet', 'interface', 'alias', 'beschreibung']
)
geraete_info = Info(
    'snmp_device_info',
    'Information über das SNMP-Gerät (Hostname und Standort)'
)

def snmp_walk(mib, column):
    """
    Führt einen SNMP-Walk für die gegebene MIB und Spalte aus und liefert
    ein Dict {Index: Wert}. z.B. (mib='IF-MIB', column='ifDescr').
    """
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community_string, mpModel=1),
        UdpTransportTarget((snmp_host, snmp_port)),
        ContextData(),
        ObjectType(ObjectIdentity(mib, column)),
        lexicographicMode=False
    )
    result = {}
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication or errorStatus:
            # Fehler behandeln (hier Abbruch)
            break
        for varBind in varBinds:
            oid_str = varBind[0].prettyPrint()
            value = varBind[1].prettyPrint()
            # Index ist das letzte Segment der OID
            index = int(oid_str.split('.')[-1])
            result[index] = value
    return result

def sammle_snmp_daten():
    """Holt SNMP-Daten und aktualisiert die Prometheus-Metriken."""
    # Basis-Info: Hostname und Standort ermitteln
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community_string, mpModel=1),
        UdpTransportTarget((snmp_host, snmp_port)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0))
    )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    if not errorIndication and not errorStatus:
        hostname = varBinds[0][1].prettyPrint()
        location = varBinds[1][1].prettyPrint()
        # Info-Metrik setzen (Wert 1 mit Labels für Hostname/Standort/Gerät)
        geraete_info.info({
            'hostname': hostname,
            'standort': location,
            'geraet': geraete_bezeichnung
        })

    # Schnittstellen-Labels abrufen
    beschreibungen = snmp_walk('IF-MIB', 'ifDescr')
    namens = snmp_walk('IF-MIB', 'ifName')
    alias = snmp_walk('IF-MIB', 'ifAlias')

    # Verkehrszähler abrufen (High Capacity Octets)
    eingehend = snmp_walk('IF-MIB', 'ifHCInOctets')
    ausgehend = snmp_walk('IF-MIB', 'ifHCOutOctets')

    # Metriken pro Schnittstelle aktualisieren
    for idx, in_octets in eingehend.items():
        iface = namens.get(idx, beschreibungen.get(idx, str(idx)))
        iface_alias = alias.get(idx, '')
        iface_descr = beschreibungen.get(idx, '')
        snmp_in.labels(
            geraet=geraete_bezeichnung,
            interface=iface, alias=iface_alias, beschreibung=iface_descr
        ).set(int(in_octets))
    for idx, out_octets in ausgehend.items():
        iface = namens.get(idx, beschreibungen.get(idx, str(idx)))
        iface_alias = alias.get(idx, '')
        iface_descr = beschreibungen.get(idx, '')
        snmp_out.labels(
            geraet=geraete_bezeichnung,
            interface=iface, alias=iface_alias, beschreibung=iface_descr
        ).set(int(out_octets))

if __name__ == '__main__':
    # Startet den HTTP-Server auf Port 9116 (Prometheus-Endpoint)&#8203;:contentReference[oaicite:1]{index=1}
    start_http_server(9116)
    while True:
        sammle_snmp_daten()
        time.sleep(30)
