# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pysentry` is a Rust-based security vulnerability auditing tool for Python packages. It's a standalone version inspired by `pip-audit` that works with uv lock files and various vulnerability databases (PyPA, PyPI JSON API, OSV.dev).

## Development Commands

### Build and Test
- `cargo build` - Build the project in debug mode
- `cargo build --release` - Build optimized release version
- `cargo test` - Run all unit and integration tests
- `cargo test [TESTNAME]` - Run specific test containing the name
- `cargo test --no-run` - Compile tests without running them
- `cargo check` - Fast compilation check without building binaries

### Running the Tool
- `cargo run -- <path>` - Run audit on a directory (debug build)
- `cargo run --release -- <path>` - Run with release optimizations
- `cargo run -- --help` - Show complete CLI help
- `cargo run -- test-project/` - Audit the test project
- `cargo run -- test-project/ --format json` - JSON output
- `cargo run -- test-project/ --format sarif` - SARIF output

### Testing with Test Project
The `test-project/` directory contains a large benchmark project with 100+ dependencies:
- Contains both `pyproject.toml` and `uv.lock` for comprehensive testing
- Useful for performance testing and validating real-world scenarios

## Architecture Overview

### High-Level Data Flow
The tool follows a 4-phase pipeline:
1. **Dependency Discovery**: Parse project files → extract dependency graph → apply filters
2. **Vulnerability Fetching**: Select source → check cache → fetch/parse vulnerability data
3. **Vulnerability Matching**: Match dependencies → apply version constraints → filter by severity
4. **Report Generation**: Generate statistics → format output → write results

### Core Module Architecture

**Entry Points**:
- `main.rs`: CLI interface using clap with comprehensive argument parsing
- `lib.rs`: High-level API orchestration and `AuditEngine` for programmatic use

**Dependency Scanning** (`dependency/` + `parsers/`):
- Registry pattern for auto-detecting project file formats
- `UvLockParser` (priority 1): Full dependency graph with exact versions
- `PyProjectParser` (priority 5): Fallback for pyproject.toml parsing
- Handles dependency classification (main/dev/optional) and graph analysis

**Vulnerability Sources** (`providers/`):
- Trait-based provider system for extensibility: `VulnerabilityProvider`
- **PyPA**: Downloads ZIP archives, parses YAML advisories
- **PyPI**: Queries JSON API for vulnerability data
- **OSV**: Batch API interface for OSV.dev database
- Factory pattern via `VulnerabilitySource` enum

**Caching System** (`cache/`):
- Two-tier: `storage.rs` (file operations) + `audit.rs` (audit-specific logic)
- TTL-based cache invalidation with separate buckets per vulnerability source
- Atomic operations to prevent cache corruption
- Cache directory: `~/.cache/pysentry/` (or system temp)

**Vulnerability Processing** (`vulnerability/`):
- `database.rs`: In-memory vulnerability database with efficient lookups
- `matcher.rs`: Version constraint matching using PEP 440, severity filtering
- Supports ignore lists and fix analysis with upgrade suggestions

**Output Generation** (`output/`):
- Unified `ReportGenerator` supporting Human/JSON/SARIF formats
- `report.rs`: Console output with color coding and statistical summaries
- `sarif.rs`: Static Analysis Results Interchange Format for IDE integration

### Key Architectural Patterns

**Async-First Design**: All I/O operations use tokio for concurrent processing

**Type Safety**: 
- Custom `PackageName` type with normalization (underscores → hyphens)
- `Version` wrapper around `pep440_rs::Version`
- Strong typing prevents common string-based errors

**Error Handling**:
- Comprehensive `AuditError` enum covering all failure modes
- Uses `thiserror` for structured error messages and context

**Extensibility**:
- Trait-based providers allow adding new vulnerability databases
- Parser registry enables supporting additional project file formats
- Format generators can be extended for new output types

## Testing Strategy

The codebase has **29 unit tests** distributed across modules:
- Each module includes `#[cfg(test)]` blocks with focused unit tests
- Integration testing uses the realistic `test-project/` directory
- Tests cover parsing, caching, matching logic, and all output formats
- Run specific module tests: `cargo test cache::` or `cargo test parsers::`

## Cache Behavior

Cache is critical for performance with large projects:
- **Location**: `~/.cache/pysentry/` or `$TEMP/pysentry/` if cache dir unavailable
- **Structure**: Separate buckets for each vulnerability source (PyPA/PyPI/OSV)
- **Invalidation**: TTL-based, configurable per source
- **Disable**: Use `--no-cache` flag for testing or CI environments
- **Custom location**: Use `--cache-dir` to specify directory

## CLI Design Patterns

The CLI uses structured enums that convert to library types:
- `AuditFormat` → `pysentry::AuditFormat`
- `SeverityLevel` → `pysentry::SeverityLevel`  
- `VulnerabilitySourceType` → `pysentry::VulnerabilitySourceType`

This pattern ensures CLI arguments are validated and type-safe before reaching the library layer.

## Dependency Graph Analysis

The tool builds comprehensive dependency graphs from `uv.lock`:
- **Direct dependencies**: Listed in pyproject.toml
- **Transitive dependencies**: Resolved by uv, tracked with parent relationships
- **Reachability analysis**: Determines which transitive deps are reachable from which direct deps
- **Source tracking**: Identifies package sources (PyPI, Git, Path, URL)

This enables filtering strategies like `--direct-only` while maintaining accurate vulnerability reporting.

## Performance Considerations

- **Concurrent fetching**: Async operations for vulnerability data retrieval
- **Efficient matching**: In-memory indexing of vulnerability databases
- **Smart caching**: Reduces redundant API calls and parsing
- **Streaming**: Large ZIP files (PyPA database) processed incrementally
- **Memory usage**: Vulnerability databases kept in memory for fast matching

## Common Development Tasks

When adding new functionality, consider these architectural touchpoints:
- **New vulnerability source**: Implement `VulnerabilityProvider` trait
- **New project format**: Implement `ProjectParser` trait and register
- **New output format**: Add variant to `AuditFormat` and implement generator
- **Performance optimization**: Focus on cache efficiency and async operations
- **Error handling**: Add new variants to `AuditError` enum as needed