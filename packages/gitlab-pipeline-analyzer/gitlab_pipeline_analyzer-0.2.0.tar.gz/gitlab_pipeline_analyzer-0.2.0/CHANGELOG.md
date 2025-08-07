# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-08-06

### Added
- Comprehensive test coverage for all MCP tools (info, log, pytest, analysis, utils)
- Added 280+ unit tests covering edge cases and error handling
- Added test documentation and summary in `tests/test_mcp_tools_summary.md`

### Updated
- **Major dependency updates:**
  - FastMCP: 2.0.0 → 2.11.1 (major feature updates)
  - python-gitlab: 4.0.0 → 6.2.0 (major API improvements)
  - httpx: 0.25.0 → 0.28.1 (performance and security fixes)
  - pydantic: 2.0.0 → 2.11.7 (validation improvements)
  - typing-extensions: 4.0.0 → 4.14.1 (latest type hints)
- **Development tool updates:**
  - pytest: 7.0.0 → 8.4.1 (latest testing framework)
  - pytest-asyncio: 0.21.0 → 1.1.0 (improved async testing)
  - pytest-cov: 4.0.0 → 6.2.1 (coverage improvements)
  - ruff: 0.1.0 → 0.12.7 (latest linting and formatting)
  - mypy: 1.0.0 → 1.17.1 (improved type checking)
  - pre-commit-hooks: v4.6.0 → v5.0.0 (latest hooks)

### Improved
- Enhanced code quality with updated linting rules
- Better error handling and type safety
- Improved test coverage and reliability
- Updated pre-commit configuration for better development experience

## [0.1.2] - 2025-08-04

### Fixed
- Added missing `main` function to `gitlab_analyzer.mcp.server` module to fix entry point execution
- Fixed ImportError when running `gitlab-analyzer` command via uvx

## [0.1.1] - Previous Release

### Added
- Initial release of GitLab Pipeline Analyzer MCP Server
- FastMCP server for analyzing GitLab CI/CD pipeline failures
- Support for extracting errors and warnings from job traces
- Structured JSON responses for AI analysis
- GitHub Actions workflows for CI/CD and PyPI publishing
- Comprehensive code quality checks (Ruff, MyPy, Bandit)
- Pre-commit hooks for development
- Security scanning with Trivy and Bandit

### Features
- `analyze_failed_pipeline(project_id, pipeline_id)` - Analyze a failed pipeline by ID
- `get_pipeline_jobs(project_id, pipeline_id)` - Get all jobs for a pipeline
- `get_job_trace(project_id, job_id)` - Get job trace/logs
- `extract_errors_from_logs(logs)` - Extract structured errors from logs

## [0.1.0] - 2025-07-31

### Added
- Initial project setup
- Basic MCP server implementation
- GitLab API integration
- Pipeline analysis capabilities
