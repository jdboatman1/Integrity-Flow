# Boatman Systems™ - AAA Irrigation Service Command Center

## Directory Overview
This directory serves as the master documentation and strategy hub for **AAA Irrigation Service Powered by Boatman Systems™**. It centralizes the architectural blueprints, CRM workflows, and implementation logs required to transform a Integrity Flow Powered by Boatman Systems™ instance into a specialized Field Service Management (FSM) platform.

The project is a hybrid infrastructure integration involving:
- **Integrity Flow Powered by Boatman Systems™ (Linode B):** Core business logic, portal, and website.
- **AI Stack (Linode A & Local):** Ollama-powered LLMs for customer support and coding assistance.
- **Edge Cluster (RPi4):** Local testing and staging environments.
- **The Vault (Synology NAS):** Secure physical data redundancy.

## Key Files
- **`Boatman_Systems_CRM/CRM=Powered-By-Boatman-systems.md`**: The **Master Blueprint**. This is the foundational mandate for all branding, infrastructure, and sales pipeline logic. It contains the "Boatman Standard" for UI/UX, commercial market segmentation, and AI integration.

## Project Structure & Architecture
- **Infrastructure:** Distributed across Linode, local Ubuntu workstations, and Raspberry Pi edge nodes.
- **Branding Standard:** Deep Sky Blue (`#1b7abf`), Emerald Green (`#059669`), and High-Vis Orange (`#ea580c`). Typography focused on heavy italics and bold sans-serif.
- **CRM Workflow:** Linear progression from 3CX-integrated Lead Generation to E-Signed Estimate and Automated Invoicing.
- **Commercial Logic:** High-end sub-contractor workflows (e.g., The Wilkins Group) featuring "Parent/Child" billing and price masking for homeowners.

## Development & Operations
- **System Maintenance:** Managed via SSH (via Tailscale) to Linode instances.
- **AI Tooling:** Local `deepseek-coder` models for real-time development and `qwen2.5-coder` for edge node tasks.
- **Data Safety:** Multi-point backup strategy linking cloud instances to local Synology storage.

## Usage
Use this directory to reference the master implementation plan, track progress logs, and ensure all code modifications or system configurations adhere to the **Boatman Systems™** elite enterprise standard.

## Access Protocol & Credentials
**ERP Server (Linode B)**
- **IP:** `100.106.12.60` (Tailscale)
- **User:** `deploy` (Passwordless Sudo Enabled)
- **SSH Port:** 22
- **Auth Method:** Public Key Authentication

**Authorized Public Key (Gemini CLI)**
If access is lost, add this key to `~/.ssh/authorized_keys` on the server:
```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGckmcb5XG9+HDdZj4i97D8Wf9yQS9XCnhzGNzH9UOXd john@ubuntu-local
```

**AI Server (Local/Tailscale)**
- **IP:** `100.68.151.50`
- **Ollama Port:** `11434` (Internal), `11435` (Docker Container on ERP)
- **Model:** `qwen2.5-coder:1.5b`

