# eBay Label Printer - Engineering Notes

These are notes for the engineer for this project. Keep them up to date as you work.

Refer to INSTRUCTIONS.md for the project overview and key components.

## Project Overview
- Automate eBay order fulfillment: detect orders → buy labels → generate packing slips → print
- Single Docker container with Python 3.11+
- Print to CUPS server at 192.168.8.194
- Test-first development with pytest

## Key Components
1. `orders.py` - eBay API order polling
2. `labels.py` - Shipping label buying/refunding  
3. `packing.py` - Packing slip generation
4. `print.py` - Print to CUPS server
5. `config.py` - Configuration management

## Current Status
- **MAJOR MILESTONE COMPLETED**: Full automation pipeline implemented ✨
- **Core Features**: All modules completed with comprehensive testing (83% coverage, 56 tests)
- **Latest Change**: Refactored order tracking to use eBay API status instead of local state files
- **Current Branch**: `refactor/remove-seen-order-tracking` (ready for merge)

### Completed Features
- eBay API integration with ebay-rest package for order polling and label purchasing
- PDF packing slip generation with ReportLab
- CUPS printing to remote server (192.168.8.194)
- Docker containerization with multi-stage builds and security best practices
- Comprehensive test suite with unit tests, integration tests, and API sandbox testing
- Enhanced eBay client architecture with shared mixin pattern
- Order processing based on natural API status progression (Completed → buy label → Shipped)

### Key Infrastructure
- GitHub Actions CI pipeline with automated testing
- Development tools: Makefile, docker-compose.yml, comprehensive test markers
- API testing infrastructure with sandbox/production environment support
- Documentation: GET_EBAY_TOKEN.md for authentication setup

## Next Steps for Future PRs
1. **Priority**: Add comprehensive error handling and logging improvements throughout all modules
2. Add eBay API authentication token refresh handling  
3. Add web dashboard for monitoring order processing status
4. Add email notifications for successful/failed processing
5. Performance optimization and containerized deployment testing
6. Implement real-time order processing daemon with continuous polling

## Key Technical Decisions

### eBay API Integration
- **Package**: `ebay-rest==1.0.14` (replaced original ebaysdk)
- **Order Flow**: Polls for "Completed" orders without "ShippedTime" → buy label & print → auto-shipped by eBay
- **Status-Based Processing**: Relies entirely on eBay API order status, no local state tracking
- **Label Workflow**: Create fulfillment → get label URL → download PDF to `data/labels/`
- **Architecture**: Shared eBay client mixin with lazy initialization and validation

### Containerization & Infrastructure
- **Docker**: Multi-stage build with Python 3.11 slim, non-root user, health checks
- **Volumes**: `/app/data` for persistent labels and logs
- **Printing**: CUPS client included for remote printing to 192.168.8.194
- **Testing**: Comprehensive test markers for unit/integration/API sandbox/production testing
