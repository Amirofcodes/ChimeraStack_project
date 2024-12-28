# ChimeraStack

ChimeraStack is a **Docker-centric tool** that simplifies the creation of consistent, production-ready development environments for **PHP** and **Python** projects. By combining an intelligent setup system with Docker's reliability, ChimeraStack ensures your environment is easily reproducible, whether you're coding locally, testing in staging, or deploying to production.

## Project Status - v0.1.0 (In Development)

ChimeraStack is currently under active development. Here's the current status:

### ✅ Currently Working

Vanilla PHP environment with:

- Language: PHP
- Framework: None (Vanilla PHP)
- Web Server: Nginx
- Database: MySQL
- Environment: Development

Both creation methods are fully functional:

```bash
# Direct creation
chimera create myproject --language php --framework none --webserver nginx --database mysql --env development

# Interactive setup
chimera init
```

### 🚧 In Progress (v0.1.0 Roadmap)

Working on validating the following vanilla setups:

1. PHP Setups (no framework):

   - [x] Nginx + MySQL
   - [ ] Nginx + PostgreSQL
   - [ ] Nginx + MariaDB
   - [ ] Apache + MySQL
   - [ ] Apache + PostgreSQL
   - [ ] Apache + MariaDB

2. Python Setups (no framework):
   - [ ] Nginx + MySQL
   - [ ] Nginx + PostgreSQL
   - [ ] Nginx + MariaDB
   - [ ] Apache + MySQL
   - [ ] Apache + PostgreSQL
   - [ ] Apache + MariaDB

### 📅 Future Plans

After v0.1.0, we plan to add:

1. Framework Support:
   - PHP: Laravel, Symfony
   - Python: Django, Flask
2. Additional Services:
   - Redis
   - Monitoring tools
   - Logging solutions

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
  - **Additional Services**: Redis, logging, and monitoring tools (planned)

- **Environment-specific Configurations**
  - **Development**: Optimized for local development with dynamic port allocation
  - **Testing**: Perfect for staging and integration tests (coming soon)
  - **Production**: Secure and performance-tuned (coming soon)

## Prerequisites

Make sure you have the following installed:

- **Python** 3.8 or higher
- **Docker** 20.10 or higher
- **Docker Compose V2**
- **Git**

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

## Quick Start

### Direct Creation

```bash
# Create a vanilla PHP project with Nginx and MySQL
chimera create myproject --language php --framework none --webserver nginx --database mysql --env development
```

### Interactive Setup

```bash
# Follow the interactive setup wizard
chimera init
```

### Managing Projects

```bash
# Start an environment
chimera start myproject

# Stop an environment
chimera stop myproject
```

## License

ChimeraStack is released under the [MIT License](LICENSE).

## Author

**Created by:** [Jaouad Bouddehbine](https://github.com/Amirofcodes)

For bug reports and feature requests, please [open an issue](https://github.com/Amirofcodes/chimera-stack/issues).

---

Thank you for your interest in ChimeraStack! We're actively working to make this tool more robust and feature-complete.
