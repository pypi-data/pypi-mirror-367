# Vecna CLI
Vault for Encrypted Credentials, Notes, and Aliases.

> Name inspired by [Vecna](https://forgottenrealms.fandom.com/wiki/Vecna) the arch-lich from Dungeons & Dragons, who is known for his obsession with secrets and knowledge.

Vecna is a secure, developer-focused command-line vault for storing credentials, secrets, and frequently used commands. Whether you're managing API keys, long commands with embedded secrets, or sensitive notes, Vecna provides a simple, encrypted solution that keeps your data safe and easily accessible.

[![Test](https://github.com/thrapai/vecna/actions/workflows/test.yaml/badge.svg)](https://github.com/thrapai/vecna/actions/workflows/test.yaml)
[![Coverage](https://codecov.io/gh/thrapai/vecna/branch/master/graph/badge.svg)](https://codecov.io/gh/thrapai/vecna)
[![PyPI version](https://img.shields.io/pypi/v/vecna.svg)](https://pypi.org/project/vecna/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Security](#security)
- [Changelog](#changelog)
- [License](#license)

## Features

- **Encrypted Vault**
  Securely stores credentials, notes, and sensitive data using AES-256-GCM encryption.

- **Master Password Protection**
  Uses a master password to derive a strong encryption key via PBKDF2 with 200,000 iterations.

- **Credential Management**
  Easily add, retrieve, update, list, and delete credentials from the command line.

- **Alias Management**
  Create aliases for frequently used commands, making it easier to manage complex or sensitive operations.

- **Auto-Expiring Sessions**
  Sessions automatically expire after a configurable timeout (default: 15 minutes), and the vault is re-locked.

- **Clipboard Integration**
  Passwords can be copied to the clipboard for quick, secure use.

- **Password Generator**
  Built-in utility to generate secure, customizable passwords on demand.

- **Local-First, No Cloud**
  All data is stored locally; Vecna performs no network operations and sends nothing externally.

- **Linux-Only Support (for now)**
  Uses `/dev/shm` for secure key caching; support for other platforms is planned.

## Installation

Vecna can be easily installed via pipx.

```bash
python3 -m pip install --user pipx
pipx install vecna
```

## Usage

After installation, you can use `vecna` from the command line to manage your secure vault and credentials.

### Initialize Vault

```bash
vecna init
```

### Lock/Unlock Vault

```bash
vecna lock
vecna unlock
```

### Credentials Management

Vecna provides a simple interface for managing credentials. You can add, retrieve, list, update, and delete credentials securely.

```bash
vecna creds <command> [options]
```

> Use `vecna creds --help` to see available more details on commands and options.

#### Example

```bash
vecna creds add myapi -u myuser -p mypass --notes "API credentials for MyAPI" --tags "api,production"
vecna creds get myapi
vecna creds list
vecna creds update myapi --password newpass
vecna creds delete myapi
```

### Aliases Management

Vecna allows you to create aliases for frequently used commands, making it easier to manage complex or sensitive command-line operations.

```bash
vecna alias <command> [options]
```

#### Example

```bash
vecna alias add myalias --command "curl -X POST https://api.example.com/data" --notes "API data submission" --tags "api,production"
vecna alias get myalias
vecna alias list
vecna alias update myalias --command "curl -X POST https://api.example.com/data --header 'Authorization: Bearer token'"
vecna alias delete myalias
```

### Generate Password

Vecna includes a built-in password generator that can create secure passwords of specified lengths.

```bash
vecna generate [options]
```

#### Example

```bash
vecna generate --length 16 --symbols --numbers --show
```

## Dependencies

Vecna is written in Python and uses the following core libraries:

- [`cryptography`](https://pypi.org/project/cryptography/) — encryption and key derivation
- [`pyperclip`](https://pypi.org/project/pyperclip/) — cross-platform clipboard handling
- [`Typer`](https://pypi.org/project/typer/) — building the CLI
- [`rich`](https://pypi.org/project/rich/) — colored CLI output

## Security

See [SECURITY.md](SECURITY.md) for details on how Vecna secures your data, trust assumptions, and key exposure windows.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes and updates.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to Vecna.

## License

MIT License
