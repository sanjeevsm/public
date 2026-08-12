# Public — Independent Projects

This repository is a curated portfolio of independent projects showcasing applications, developer tooling, and deployment automation. Each project includes a dedicated README with platform-specific setup, usage notes, and troubleshooting guidance.

Use the links below to open a project README and follow its Quick Start section for a runnable demo.

## Projects

| Project | Description | README |
|---|---|---|
| CI/CD Dashboard | Real-time CI/CD metrics dashboard with multi-provider support. | [workspace/python/cicd/README.md](workspace/python/cicd/README.md)
| iLab+ — AI Interview Simulator | AI-powered interview question generator and quiz platform (desktop + web modes). | [workspace/python/ilab/README.md](workspace/python/ilab/README.md)
| iTrack+ — Personal Finance Tracker | Personal finance tracker with multi-user collaboration and reporting. | [workspace/python/itrack/README.md](workspace/python/itrack/README.md)
| iTransit+ — Public Transport Viewer | Stateless frontend + FastAPI backend integrating TfL and other UK transport APIs with client-side favourites and mock fallback. | [workspace/python/itransit/README.md](workspace/python/itransit/README.md)
| iCare+ — Clinic Management System | Clinic management system with REST API and reporting features. | [workspace/python/icare/README.md](workspace/python/icare/README.md)

**Default Ports**

| Project | Backend | Frontend | Other / System |
|---|---:|---:|---|
| CI/CD Dashboard | 8000 | — | Prometheus 9000, Grafana 9001 |
| iLab+ | 8001 (web) | — | — |
| iTrack+ | 8002 | 3000 | MongoDB 27017 |
| iTransit+ | 8003 | 3001 | — |
| iCare+ | 8004 | 3003 | Postgres 5432 |
| System services | Postgres 5432 | — | MongoDB 27017, Prometheus 9000, Grafana 9001 |

## Quick start — view any project

1. Clone this repository:

```bash
git clone https://github.com/sanjeevsm/public.git
cd public
```

2. Open the project README you want to evaluate. Example:

```bash
# Open the CI/CD Dashboard README in your editor or viewer
code workspace/python/cicd/README.md
```

Each project README contains platform-specific setup steps (Docker, local, Windows PowerShell and macOS/Linux shells) and quick demo commands.

## For recruiters and reviewers

- Each project is self-contained and includes a `scripts/` folder with cross-platform start/stop/setup helpers.
- Prefer the Docker method for a fast, reproducible demo. Individual project READMEs mark the recommended method.
- Use the project README’s Quick Start for one‑minute verification steps.

## Contributing & license

- Contributions are welcome — please open an issue or a pull request against the project you want to improve. See the project README for contribution guidance.
- Unless stated otherwise in a project folder, code in this repository is provided under the MIT license. See individual project READMEs for exact license details.

## Contact

If you have questions about any project, open an issue in this repository and tag the project folder in the title (for example: `itrack: issue with Docker start`).

---

This landing page is intended as a concise entry point for reviewers. For runnable instructions, troubleshooting, architecture diagrams and developer notes, open the linked project README files above.
