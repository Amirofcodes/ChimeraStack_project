# DevStack Factory

DevStack Factory is a **Docker-centric tool** that simplifies the creation of consistent, production-ready development environments for **PHP** and **Python** projects. By combining an intelligent setup system with Docker’s reliability, DevStack Factory ensures your environment is easily reproducible, whether you’re coding locally, testing in staging, or deploying to production.

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

  - **Development**: Optimized for local development
  - **Testing**: Perfect for staging and integration tests
  - **Production**: Secure and performance-tuned

- **Intelligent Project Scaffolding**  
  Respects framework conventions, creating a boilerplate that follows best practices.

- **Automated Docker Resource Management**  
  Abstracts away the complexity of handling multiple containers and services.

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
   git clone https://github.com/Amirofcodes/devstack-factory.git
   ```
2. **Navigate to the project directory:**
   ```bash
   cd devstack-factory
   ```
3. **Install the package (in editable mode):**
   ```bash
   pip install -e .
   ```

Once installed, you’ll have access to the `devstack` command-line interface (CLI).

---

## Usage

DevStack Factory provides a straightforward CLI for creating and managing project environments.

### Create a New Project

```bash
devstack create myproject --language php --framework laravel
```

**Available options**:

- `--language`: `php` | `python`
- `--framework`: `none` | `laravel` | `symfony` | `django` | `flask`
- `--webserver`: `nginx` | `apache`
- `--database`: `mysql` | `postgresql` | `mariadb`
- `--env`: `development` | `testing` | `production`

### Start an Existing Environment

```bash
devstack start myproject
```

### Stop an Environment

```bash
devstack stop myproject
```

Use these commands to quickly spin up and tear down your Docker environments.

---

## Project Structure

When you create a new project (e.g., `myproject`), DevStack Factory generates a structured directory layout:

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

- **docker/**: Contains Docker configurations for your web server, language runtime, and database.
- **config/**: Holds environment-specific settings for development, testing, and production.
- **docker-compose.yml**: Orchestrates all containers in your stack.
- **.env**: Stores environment variables used by `docker-compose` and your application.

---

## Configuration

DevStack Factory includes default, secure, and optimized configurations for each environment. You can customize these to fit your needs:

- **Docker Compose**: Update service orchestration, port mappings, and resource allocations.
- **Web Server Configs**: Modify your Nginx or Apache settings to adapt for advanced use cases.
- **Database Settings**: Tweak performance and security settings for MySQL, PostgreSQL, or MariaDB.
- **Environment Variables**: Manage secrets and sensitive information using the `.env` file.

---

## Development

If you’re interested in contributing to DevStack Factory or modifying it locally:

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

DevStack Factory is released under the [MIT License](LICENSE). You are free to use, modify, and distribute this software as permitted by the license.

---

## Author

**Created by:** [Jaouad Bouddehbine](https://github.com/yourusername)

For bug reports and feature requests, please [open an issue](https://github.com/Amirofcodes/devstack-factory/issues).

---

Feel free to reach out or submit a pull request if you have questions or suggestions. Thank you for using DevStack Factory!
