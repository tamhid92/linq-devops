
# Linq DevOps Assessment

This project presents a scalable, secure, and production-ready monitoring solution using Prometheus, Grafana, and custom Python-based telemetry, designed to meet Linq's DevOps take-home assessment criteria.

---

## 📁 Project Structure

```
linq-devops/
├── README.md
├── ansible/
│   ├── files/
│   │   ├── custom-exporter.py         # Python-based Prometheus custom exporter
│   │   └── hvac_lib.py                # Vault integration for secrets handling
│   ├── templates/
│   │   └── custom_exporter.service.j2 # Systemd unit template to run exporter as a service
│   ├── inventory.ini                  # Ansible inventory for target nodes
│   └── deploy-exporter.yml           # Ansible playbook for deployment
├── docker-compose.yml                # Docker Compose setup for Prometheus and Grafana
├── prometheus.yml                    # Prometheus configuration file
└── grafana-dash.yml                  # Pre-configured Grafana dashboard definition
```

---

## 🧩 Solution Overview

This solution deploys a secure and modular monitoring stack using Docker Compose for Prometheus and Grafana, along with a Python-based custom exporter. The exporter collects essential system metrics and monitors service health, pushing data to Prometheus. Real-time alerting is integrated via Slack, with secrets securely managed using HashiCorp Vault.

---

## ✅ Key Features

- **Metric Collection**: CPU, memory, disk usage, and network latency.
- **Custom Exporter**: Lightweight Python script using `psutil` and ICMP ping.
- **Service Monitoring**: Checks for availability of critical internal services.
- **Alerting**: Slack integration via `slack_sdk` with thresholds for all key metrics.
- **Infrastructure as Code**: Fully automated with Ansible for scalable deployments.
- **Secrets Management**: Secure handling of Slack tokens and other secrets via Vault.
- **Visualization**: Grafana dashboard pre-wired to Prometheus for easy insights.

---

## 🚀 Deployment Instructions

To deploy the exporter across your infrastructure using Ansible:

```bash
ansible-playbook ansible/deploy-exporter.yml -i ansible/inventory.ini
```

Prometheus and Grafana can be launched locally using:

```bash
docker-compose up -d
```

---

## 📊 Monitoring Design

**Metrics Tracked**:
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Network latency (ms)

**Tools**:
- `psutil` for system metrics
- `ping` to Google DNS for latency
- Custom Python exporter exposed on `/metrics` for Prometheus

**Backend**: Prometheus

---

## 🚨 Alerting Strategy

**Alert Conditions**:
- CPU usage > 80% for 5 minutes
- Memory usage > 80% for 5 minutes
- Disk usage > 80%
- Network latency > 200ms

**Alert Delivery**:
- Slack notifications via `slack_sdk`
- Tokens and channel info securely fetched from Vault

---

## ⚙️ Scalability and Extensibility

This architecture is designed for scalability:
- Add servers by updating the `inventory.ini` file.
- Run the playbook to install the exporter and auto-register with Prometheus.
- Script updates are propagated to all nodes via Ansible.

**Future Improvements**:
- Split playbooks to support partial deployments (e.g., script-only updates).
- Extend support to Windows systems with platform-aware task definitions.
- Add automated validation and recovery for exporter services.

---
Grafana Dashboard
![grafana-dashboard](/screenshots/grafana.PNG)


Slack alert during stress test, time set to 2 minutes for testing.
![alert](/screenshots/stress-test.PNG)


## 📌 Notes

- The pipeline is tailored to my home lab setup and assumes certain configurations are pre-installed.
    -  The infrastructure architecture is illustrated [here](https://www.github.com/tamhid92/devops)
- The monitoring script is compatible with any Linux machine given dependencies are met and a valid Slack token is provided.
