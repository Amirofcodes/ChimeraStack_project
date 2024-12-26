# ChimeraStack

ChimeraStack is a **Docker-centric tool** that simplifies the creation of consistent, production-ready development environments for **PHP** and **Python** projects. By combining an intelligent setup system with Docker's reliability, ChimeraStack ensures your environment is easily reproducible, whether you're coding locally, testing in staging, or deploying to production.

---

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Configuration](#configuration)
7. [Development](#development)
8. [License](#license)
9. [Author](#author)

---

## Features

- **Docker-based Configuration**  
  Ensures consistent, isolated environments across local machines and different deployment targets.

- **Built-in PHP & Python Support**

  - **PHP**: Laravel, Symfony, or vanilla PHP
  - **Python**: Django, Flask, or vanilla Python

- **Flexible Infrastructure Choices**

  - **Web Servers**: Nginx or Apache with optimized configurations
  - **Databases**: MySQL, PostgreSQL, or MariaDB (production-ready settings)
  - **Additional Services**: Redis, logging, and monitoring tools

- **Environment-specific Configurations**

  - **Development**: Optimized for local development with dynamic port allocation
  - **Testing**: Perfect for staging and integration tests
  - **Production**: Secure and performance-tuned

- **Intelligent Project Scaffolding**  
  Respects framework conventions while maintaining a clean, organized structure.

- **Automated Docker Resource Management**
  - Dynamic port allocation to prevent conflicts
  - Efficient container orchestration
  - Automatic cleanup and resource management

---

## Prerequisites

Make sure you have the following installed:

- **Python** 3.8 or higher
- **Docker** 20.10 or higher
- **Docker Compose V2**
- **Git**

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Amirofcodes/chimera-stack.git
   ```
2. **Navigate to the project directory:**
   ```bash
   cd chimera-stack
   ```
3. **Install the package (in editable mode):**
   ```bash
   pip install -e .
   ```

Once installed, you'll have access to the `chimera` command-line interface (CLI).

---

## Usage

ChimeraStack provides a straightforward CLI for creating and managing project environments.

### Create a New Project

```bash
chimera create myproject --language php --framework laravel
```

**Available options**:

- `--language`: `php` | `python`
- `--framework`: `none` | `laravel` | `symfony` | `django` | `flask`
- `--webserver`: `nginx` | `apache`
- `--database`: `mysql` | `postgresql` | `mariadb`
- `--env`: `development` | `testing` | `production`

### Interactive Setup

For guided setup:

```bash
chimera init
```

### Manage Environments

```bash
# Start an environment
chimera start myproject

# Stop an environment
chimera stop myproject
```

---

## Project Structure

When you create a new project (e.g., `myproject`), ChimeraStack generates a structured directory layout:

```
myproject/
├── docker/
│   ├── nginx/ or apache/
│   ├── php/ or python/
│   └── database/
├── config/
│   ├── development.yaml
│   ├── testing.yaml
│   └── production.yaml
├── docker-compose.yml
└── .env
```

- **docker/**: Contains service-specific Docker configurations
- **config/**: Holds environment-specific settings
- **docker-compose.yml**: Orchestrates your development stack
- **.env**: Stores environment variables

---

## Configuration

ChimeraStack includes secure, optimized configurations for each environment that you can customize:

- **Docker Compose**: Service orchestration and resource allocation
- **Web Server Configs**: Optimized Nginx or Apache settings
- **Database Settings**: Performance-tuned database configurations
- **Environment Variables**: Secure secrets management
- **Port Management**: Dynamic port allocation to prevent conflicts

---

## Development

To contribute to ChimeraStack:

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run tests**:
   ```bash
   pytest
   ```

Feel free to submit pull requests with improvements or new features.

---

## License

ChimeraStack is released under the [MIT License](LICENSE).

---

## Author

**Created by:** [Jaouad Bouddehbine](https://github.com/Amirofcodes)

For bug reports and feature requests, please [open an issue](https://github.com/Amirofcodes/chimera-stack/issues).

---

Feel free to reach out or submit a pull request if you have questions or suggestions. Thank you for using ChimeraStack!
