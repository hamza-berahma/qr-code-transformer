# Deployment Configuration Files

This directory contains deployment configuration files for various platforms.

## Files

- **Procfile** - Heroku deployment
- **railway.json** - Railway.app configuration
- **railway.toml** - Railway.app TOML config
- **render.yaml** - Render.com configuration
- **runtime.txt** - Python version specification
- **Dockerfile** - Docker container configuration
- **docker-compose.yml** - Docker Compose configuration
- **.dockerignore** - Docker build exclusions

## Usage

These files are automatically detected by their respective platforms when placed in the repository root. However, they can be moved here for organization while maintaining functionality through symlinks or platform-specific configuration.

For deployment instructions, see [DEPLOYMENT.md](../DEPLOYMENT.md) in the root directory.
