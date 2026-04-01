# pacus

Document management and work acts processing system with API and database tooling.

## Architecture

The project includes:

- **Database schema** and ERD for work acts storage
- **NocoDB views** plan for visual data management
- **REST API** for work acts processing
- **Migration scripts** for database management
- **Import tools** for inbox work acts

## Components

### Scripts (`scripts/`)

| Script | Description |
|--------|-------------|
| `start_work_acts_demo.sh` | Start demo environment |
| `stop_work_acts_demo.sh` | Stop demo environment |
| `import_inbox_work_acts.py` | Import work acts from inbox |
| `run_inbox_import.sh` | Wrapper for inbox import |
| `start_print_artifacts_server.sh` | Start print artifacts server |

### Documentation (`docs/`)

Interactive HTML documentation covering architecture, database schema, API endpoints, and migration plans.

## Getting Started

```bash
# Start the demo
./scripts/start_work_acts_demo.sh

# Import inbox work acts
./scripts/run_inbox_import.sh

# Stop when done
./scripts/stop_work_acts_demo.sh
```

## License

See [LICENSE](LICENSE) for details.
