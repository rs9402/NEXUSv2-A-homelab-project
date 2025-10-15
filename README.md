 ```plaintext
    _   _________  ____  _______         ___ 
   / | / / ____/ |/ / / / / ___/   _   _|__ \
  /  |/ / __/  |   / / / /\__ \   | | / /_/ /
 / /|  / /___ /   / /_/ /___/ /   | |/ / __/ 
/_/ |_/_____//_/|_\____//____/    |___/____/ 
                                             
Network EXtensible Utility Server - RS9402
```                                                  
*Self-hosted home lab infrastructure built on Windows 10 for monitoring and media services.*
### Date: October 2025 – Present
***(THIS REPOSITORY IS TO BE SEEN AS A PORTFOLIO OF WORK ONLY, AND NOT A PACKAGED SERVER ENVIRONMENT)***


# Overview

This project documents the migration and optimization of my self-hosted home lab environment — transitioning from a Docker-on-WSL2 architecture on Windows 10 to a more stable, native setup running directly on the host. The goal was to improve reliability, simplify maintenance, and optimize resource usage while keeping critical services accessible and secure.

# Previous Stack

The initial setup ran multiple containerized services using Docker with WSL2 on Windows 10.
Services included:

- Prometheus, and Grafana for real-time system monitoring (CPU, memory, disk, and network).
- Pi-hole for DNS-level ad and malware domain blocking (~900k+ domains).
- Tailscale (WireGuard-based VPN) for remote access.
- Jellyfin media server supporting multiple concurrent users.
- NGINX for serving static dashboards.
- CalibreWeb, a web dashboard for reading a Calibre (An E-Book CMS) database and serving it on network

# New Stack

The current server architecture is built directly on **Windows 10 (Native)** and focuses on stability and minimal overhead.

- **Operating System:** Windows 10 Professional
- **Monitoring & Visualization:** Prometheus and Grafana
- **Metrics Collector:** Windows Exporter (for native system data)
- **Automation:** PowerShell Automation Scripts
- **Media Server:** Jellyfin
- **Web Services:** Python's lightweight `http.server`
- **Custom Service:** Python microservice for OpenMeteo API data fetching
- **Calibre's Integrated Content Server:** Calibre, an E-Book CMS, offers a built in content server with a serviceable dashboard and user authentication, more suitable in my use case than CalibreWeb, as I own a smaller library with few users

# Why?

While Docker with WSL2 provides strong containerization tools for development, it proved unreliable for persistent infrastructure hosting. Frequent network issues, file mounting errors, and performance degradation made the system impractical for continuous uptime. To improve stability and control, all essential services were migrated to run directly on the Windows host, removing unnecessary layers and simplifying the network stack.

# What Changed:

- Removed Docker and WSL2 layer due to instability and downtime, opting for natively run services to eliminate virtualization overhead and simplify troubleshooting.
- Removed Pi-hole, planned for re-deployment on a separate dedicated device for continuous DNS availability in future. Endpoint protection put into place instead (See: https://github.com/t895/DNSNet).
- Removed Tailscale since remote access was not frequently required.
- Replaced NGINX with a lightweight Python http.server for serving static dashboard content. This decision reduced the operational footprint while maintaining necessary functionality for local network access.
- Added Windows Exporter (See: https://github.com/prometheus-community/windows_exporter) for  native metrics collection, ensuring granular, reliable performance data acquisition.

# What’s new:

- Added PowerShell automation scripts to start all services in the background at system launch.
- Developed a custom weather microservice that pulls data from the OpenMeteo API and outputs JSON for dashboard use.
- Updated Grafana dashboards for better visualization of Windows-based metrics (CPU, memory, disk, network).
- Simplified architecture to reduce failure points and improve maintainability.

# Known Issues & Troubleshooting

- **Prometheus Startup Automation:** The service currently requires manual launch after system boot. Investigation is focused on identifying a conflict with Windows permission policies or a port binding contention issue preventing seamless automatic startup via the PowerShell script.


# Future Plans

- Reintroduce Pi-hole on a dedicated low-power device (e.g. Raspberry Pi Zero 2 W or similar)
- Reintroduce reverse proxying. This will benefit from Pi-Hole as well, since it (pi-hole) will act as a local DNS resolver as well

## Notes

This migration marks a transition toward full-stack infrastructure management — combining system administration, networking, and automation under one self-hosted ecosystem. The goal is to create infrastructure that is stable, secure, and transparent while running efficiently on consumer-grade hardware.
