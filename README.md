# Adaptive AI-Powered Dynamic Honeypot with Real-Time Threat Hunting
BS Cyber Security FYP | KFUEIT

## Project Structure
- `configs/` - Configuration files for Cowrie, ELK, and the AI Engine.
- `scripts/` - Core Python and Bash scripts for detection and testing.
- `ISOs/` - Hypervisor installation images (pfSense and Ubuntu 22.04).
- `logs/` - Engine and attack logs.
- `models/` - Trained scikit-learn/XGBoost models.
- `data/` - Training and evaluation datasets.

## Quick Start
1.  **Phase 1**: Install VirtualBox and deploy the VMs using `MASTER_ARCHITECTURE_BLUEPRINT.md`.
2.  **Phase 2**: Run the `start.bat` launcher to initialize the virtual environment and AI dashboards.
3.  **Phase 3**: Verify live telemetry on `http://localhost:5000`.
4.  **Testing**: Execute attack scenarios documented in `HOW_TO_TEST.md`.

## Dependencies
Automated via `start.bat`. Python 3.x is required on the host.

---
*Project Master Repository | FYP CYBER SECURITY*
