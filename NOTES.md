# eBay Label Printer - Engineering Notes

These are notes for the engineer for this project. Keep them up to date as you work.

Refer to INSTRUCTIONS.md for the project overview and key components.

## Project Overview
- Automate eBay order fulfillment: detect orders → buy labels → generate packing slips → print
- Single Docker container with Python 3.11+
- Print to CUPS server at 192.168.8.194
- Test-first development with pytest

## Key Components to Build
1. `orders.py` - eBay API order polling
2. `labels.py` - Shipping label buying/refunding  
3. `packing.py` - QR-based packing slip generation
4. `print.py` - Print to CUPS server
5. `config.py` - Configuration management

## Progress Log

### Initial Setup
- [x] Create basic project structure (app/, tests/, etc.)
- [x] Set up requirements.txt with core dependencies
- [ ] Create Dockerfile for containerization
- [x] Set up Makefile for common tasks
- [x] Configure GitHub Actions CI pipeline
- [x] Create basic configuration system

### Core Functionality
- [ ] Implement order polling from eBay API
- [ ] Implement shipping label purchase
- [ ] Implement packing slip PDF generation with QR codes
- [ ] Implement CUPS printing functionality
- [ ] Add comprehensive error handling and logging

### Testing & Quality
- [x] Unit tests for all modules (basic structure)
- [ ] Integration tests
- [x] Linting setup
- [x] Mock external dependencies for tests

## Current Engineer Notes
- Started: Initial project setup
- Focus: Setting up project foundation with small, reviewable PRs
- COMPLETED: Basic project structure with placeholder implementations
- COMPLETED: Fixed linter syntax error in print.py
- COMPLETED: Cleaned up Makefile (removed unnecessary targets)
- COMPLETED: Updated README with concise project overview
- Branch: `feature/initial-project-structure` (pushed to origin)
- Status: Ready for review - linter passing, formatter working, README updated.

## Files Created in First PR
- `app/` directory with all core modules (config.py, orders.py, labels.py, packing.py, print.py)
- `tests/` directory with initial test files
- `requirements.txt` with all necessary dependencies
- `Makefile` with development and build tasks
- `run.py` main entry point
- `setup.py` for package installation
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`)

## Next Steps for Future PRs
1. Implement actual eBay API integration in orders.py
2. Add PDF generation functionality to packing.py
3. Create Dockerfile for containerization
4. Add integration tests
5. Implement error handling and logging improvements

## Technical Decisions Made
(To be updated as development progresses)

## Known Issues / Blockers
(To be updated as needed)