# Publishing Guide for pysentry

This guide covers how to publish the `pysentry` Rust tool to both PyPI (with Python bindings) and GitHub releases.

## PyPI Publishing with Python Bindings

### 1. Add Python Dependencies

Add to `Cargo.toml`:
```toml
[lib]
name = "pysentry"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.22", features = ["extension-module"] }
```

### 2. Create Python Interface

Create `src/python.rs`:
```rust
use pyo3::prelude::*;
use crate::{AuditEngine, AuditConfig, AuditFormat};

#[pyfunction]
fn audit_python(path: String, format: Option<String>) -> PyResult<String> {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        let config = AuditConfig::default();
        let engine = AuditEngine::new(config);
        
        let format = match format.as_deref() {
            Some("json") => AuditFormat::Json,
            Some("sarif") => AuditFormat::Sarif,
            _ => AuditFormat::Human,
        };
        
        match engine.audit_path(&path, format).await {
            Ok(result) => Ok(result),
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
        }
    })
}

#[pymodule]
fn pysentry(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(audit_python, m)?)?;
    Ok(())
}
```

### 3. Update lib.rs

Add to `src/lib.rs`:
```rust
#[cfg(feature = "python")]
mod python;
```

### 4. Create pyproject.toml

```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "pysentry"
description = "Security vulnerability auditing tool for Python packages"
readme = "README.md"
requires-python = ">=3.8"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Rust",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Security",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dynamic = ["version"]

[project.urls]
Homepage = "https://github.com/yourusername/pysentry"
Repository = "https://github.com/yourusername/pysentry"
Issues = "https://github.com/yourusername/pysentry/issues"

[project.scripts]
pysentry = "pysentry:main"

[tool.maturin]
features = ["pyo3/extension-module"]
python-source = "python"
module-name = "pysentry._internal"
```

### 5. Create Python Wrapper

Create `python/pysentry/__init__.py`:
```python
"""pysentry: Security vulnerability auditing tool for Python packages."""

from ._internal import audit_python

__version__ = "0.1.0"
__all__ = ["audit_python", "main"]

def main():
    """CLI entry point."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Audit Python packages for vulnerabilities")
    parser.add_argument("path", help="Path to Python project")
    parser.add_argument("--format", choices=["human", "json", "sarif"], 
                        default="human", help="Output format")
    
    args = parser.parse_args()
    
    try:
        result = audit_python(args.path, args.format)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 6. Build and Publish

```bash
# Install maturin
pip install maturin

# Test locally
maturin develop

# Test the Python module
python -c "import pysentry; print(pysentry.audit_python('.'))"

# Build wheels for all platforms
maturin build --release

# Publish to PyPI (requires API token)
maturin publish --username __token__ --password your_pypi_token
```

## GitHub Releases

### 1. Create GitHub Actions Workflow

Create `.github/workflows/release.yml`:
```yaml
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  build:
    strategy:
      matrix:
        include:
          - target: x86_64-unknown-linux-gnu
            os: ubuntu-latest
            name: linux-x64
          - target: x86_64-apple-darwin
            os: macos-latest
            name: macos-x64
          - target: aarch64-apple-darwin
            os: macos-latest
            name: macos-arm64
          - target: x86_64-pc-windows-msvc
            os: windows-latest
            name: windows-x64
            ext: .exe

    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      
      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}
      
      - name: Build
        run: cargo build --release --target ${{ matrix.target }}
      
      - name: Package Unix
        if: matrix.os != 'windows-latest'
        run: |
          name=pysentry-${{ matrix.name }}
          mkdir $name
          cp target/${{ matrix.target }}/release/pysentry $name/
          cp README.md $name/
          cp LICENSE $name/
          tar -czf $name.tar.gz $name
      
      - name: Package Windows
        if: matrix.os == 'windows-latest'
        run: |
          $name = "pysentry-${{ matrix.name }}"
          mkdir $name
          cp target/${{ matrix.target }}/release/pysentry.exe $name/
          cp README.md $name/
          cp LICENSE $name/
          Compress-Archive -Path $name -DestinationPath "$name.zip"
      
      - uses: actions/upload-artifact@v4
        with:
          name: pysentry-${{ matrix.name }}
          path: |
            *.tar.gz
            *.zip

  release:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/download-artifact@v4
        with:
          path: artifacts
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: artifacts/*/*
          generate_release_notes: true
          draft: false
          prerelease: false
```

### 2. Create Installation Script

Create `install.sh`:
```bash
#!/bin/bash
set -e

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case $OS in
  darwin)
    if [ "$ARCH" = "arm64" ]; then
      PLATFORM="macos-arm64"
    else
      PLATFORM="macos-x64"
    fi
    EXT="tar.gz"
    ;;
  linux)
    PLATFORM="linux-x64"
    EXT="tar.gz"
    ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac

# Get latest release
LATEST_RELEASE=$(curl -s https://api.github.com/repos/yourusername/pysentry/releases/latest | grep -o '"tag_name": "[^"]*"' | cut -d'"' -f4)
DOWNLOAD_URL="https://github.com/yourusername/pysentry/releases/download/${LATEST_RELEASE}/pysentry-${PLATFORM}.${EXT}"

echo "Downloading pysentry ${LATEST_RELEASE} for ${PLATFORM}..."

# Download and extract
curl -L "$DOWNLOAD_URL" | tar -xz

# Install to /usr/local/bin (requires sudo)
sudo mv pysentry-${PLATFORM}/pysentry /usr/local/bin/

echo "pysentry installed successfully!"
echo "Run 'pysentry --help' to get started."
```

## Release Process

### 1. Prepare Release

```bash
# Update version in Cargo.toml
sed -i 's/version = ".*"/version = "0.1.0"/' Cargo.toml

# Update version in Python wrapper
sed -i 's/__version__ = ".*"/__version__ = "0.1.0"/' python/pysentry/__init__.py

# Commit changes
git add .
git commit -m "Release v0.1.0"
```

### 2. Create and Push Tag

```bash
# Create tag
git tag v0.1.0

# Push tag (triggers GitHub Actions)
git push origin v0.1.0
```

### 3. Publish to PyPI

```bash
# After GitHub release is created
maturin publish --username __token__ --password your_pypi_token
```

## Setup Requirements

### PyPI Setup
1. Create account on https://pypi.org
2. Generate API token in account settings
3. Store token securely for publishing

### GitHub Setup
1. Repository must have proper LICENSE file
2. README.md should document installation and usage
3. GitHub Actions will automatically create releases when you push tags

## Installation Methods After Publishing

Users will be able to install via:

### From PyPI (Python users)
```bash
pip install pysentry
pysentry --help
```

### From GitHub Releases (Direct binary)
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/pysentry/main/install.sh | bash
```

### From Cargo (Rust users)
```bash
cargo install pysentry
```

## Notes

- Update `yourusername` with your actual GitHub username throughout
- Ensure proper licensing (add LICENSE file)
- Test builds locally before tagging releases
- Consider semantic versioning for releases
- GitHub Actions require permissions to create releases