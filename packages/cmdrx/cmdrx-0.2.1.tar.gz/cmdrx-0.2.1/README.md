# CmdRx - AI-Powered Command Line Troubleshooting Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)

CmdRx is a command line tool designed to assist IT personnel in analyzing CLI command outputs and providing troubleshooting steps and suggested fixes using artificial intelligence. It supports multiple LLM providers including OpenAI, Anthropic Claude, Grok, and custom on-premises solutions.

## Features

- **Multiple Input Modes**: Analyze command output directly or via piped input
- **AI-Powered Analysis**: Uses advanced language models to provide intelligent troubleshooting
- **Multiple LLM Providers**: Support for OpenAI, Anthropic, Grok, and custom endpoints
- **Secure Configuration**: Safe storage of API keys using system keyring
- **Detailed Logging**: Timestamped analysis logs with comprehensive information
- **Automated Fix Scripts**: Generates executable shell scripts with suggested fixes
- **User-Friendly TUI**: Text-based configuration interface for easy setup
- **Cross-Platform**: Works on Linux and macOS

## Installation

### From PyPI (Recommended)

```bash
pip install cmdrx
```

### From Source

```bash
git clone https://github.com/ryantischer2/cmdrx.git
cd cmdrx
pip install -e .
```

### Package Managers

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install cmdrx
```

**Fedora/RHEL:**
```bash
sudo dnf install cmdrx
```

**macOS (Homebrew):**
```bash
brew install cmdrx
```

## Quick Start

### 1. Configure CmdRx

Run the configuration wizard to set up your LLM provider:

```bash
cmdrx --config
```

This will guide you through:
- Selecting an LLM provider (OpenAI, Anthropic, Grok, or custom)
- Entering your API credentials securely
- Configuring output directories and preferences

### 2. Analyze Command Output

**Standalone Mode** (CmdRx executes the command):
```bash
cmdrx systemctl status httpd
cmdrx journalctl -xe
cmdrx docker ps -a
```

**Piped Mode** (analyze output from another command):
```bash
systemctl status httpd | cmdrx
journalctl -xe | cmdrx
docker logs my-container | cmdrx
```

### 3. Review Results

CmdRx will display:
- Analysis of the command output
- Identified issues
- Troubleshooting steps
- Suggested fixes with risk levels
- Generated log files and fix scripts

## Usage Examples

### Troubleshooting a Failed Service

```bash
$ cmdrx systemctl status apache2
```

Output:
```
╭─ Analysis (ERROR) ────────────────────────────────────────╮
│ Apache2 service is failed due to configuration syntax    │
│ error in /etc/apache2/sites-enabled/000-default.conf     │
╰───────────────────────────────────────────────────────────╯

╭─ Issues Identified ───────────────────────────────────────╮
│ • Configuration syntax error in virtual host             │
│ • Service failed to start                                │
│ • Port conflict possible                                  │
╰───────────────────────────────────────────────────────────╯

╭─ Troubleshooting Steps ───────────────────────────────────╮
│ 1. Check configuration syntax                            │
│    Command: apache2ctl configtest                        │
│    This will show specific syntax errors                 │
│                                                           │
│ 2. Review error logs                                     │
│    Command: journalctl -u apache2 -n 20                  │
│    Check for detailed error messages                     │
╰───────────────────────────────────────────────────────────╯

Generated Files:
📄 Log file: ~/.cmdrx_logs/cmdrx_analysis_20241201_143022.log
🔧 Fix script: ~/.cmdrx_logs/cmdrx_fix_20241201_143022.sh
   Run with: bash ~/.cmdrx_logs/cmdrx_fix_20241201_143022.sh
```

### Analyzing Docker Issues

```bash
$ docker ps | cmdrx
```

### Custom Analysis with Piped Input

```bash
$ cat /var/log/syslog | tail -50 | cmdrx
```

## Configuration

### LLM Providers

CmdRx supports multiple LLM providers:

#### OpenAI
- Models: gpt-4, gpt-3.5-turbo, etc.
- Requires: OpenAI API key
- Configuration: Select "openai" in config menu

#### Anthropic Claude
- Models: claude-3-sonnet, claude-3-haiku, etc.
- Requires: Anthropic API key
- Configuration: Select "anthropic" in config menu

#### Grok (xAI)
- Models: grok-beta, etc.
- Requires: xAI API key
- Configuration: Select "grok" in config menu

#### Custom/On-Premises
- Any OpenAI-compatible API endpoint
- Examples: Ollama, LocalAI, custom deployments
- Configuration: Select "custom" and provide endpoint details

### Configuration File

Configuration is stored in `~/.config/cmdrx/config.json`:

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4",
  "log_directory": "~/cmdrx_logs",
  "verbose": false,
  "auto_fix_scripts": true,
  "command_timeout": 30
}
```

### Secure Credential Storage

CmdRx offers multiple secure methods for storing API keys and tokens:

#### Method 1: System Keyring (Preferred)
- **Linux**: Secret Service (GNOME Keyring, KWallet)
- **macOS**: Keychain
- **Windows**: Windows Credential Store
- **Setup**: Use `cmdrx --config` to store credentials securely

#### Method 2: Environment Variables
Perfect for development and CI/CD environments:
```bash
# OpenAI
export CMDRX_OPENAI_API_KEY="sk-your-openai-key"

# Anthropic Claude
export CMDRX_ANTHROPIC_API_KEY="sk-ant-your-claude-key"

# Grok (xAI)
export CMDRX_GROK_API_KEY="xai-your-grok-key"

# Custom providers
export CMDRX_CUSTOM_API_KEY="your-custom-key"
export CMDRX_CUSTOM_BEARER_TOKEN="your-bearer-token"
```

#### Method 3: Credentials File
For manual credential management:
```bash
# Create secure credentials file
mkdir -p ~/.config/cmdrx
cat > ~/.config/cmdrx/credentials.json << 'EOF'
{
  "openai_api_key": "sk-your-openai-key",
  "anthropic_api_key": "sk-ant-your-claude-key",
  "grok_api_key": "xai-your-grok-key"
}
EOF

# Secure the file (owner-only access)
chmod 600 ~/.config/cmdrx/credentials.json
```

#### Priority Order
CmdRx will search for credentials in this order:
1. System keyring
2. Environment variables (`CMDRX_*`)
3. Credentials file (`~/.config/cmdrx/credentials.json`)

#### Setting Up API Keys

**Option A: Interactive Configuration with Storage Choice (Recommended)**
```bash
cmdrx --config
```

When configuring an API key, CmdRx will present you with storage method options:

| **Option** | **Method** | **Security** | **Best For** |
|------------|------------|--------------|--------------|
| **1** | System Keyring | High | Desktop users, single-user systems |
| **2** | Environment Variable | Medium | Development, CI/CD, automation |
| **3** | Credentials File | Medium | Manual management, shared systems |

The interface will:
- Show available storage methods for your system
- Display security levels for each method
- Provide setup instructions for your chosen method
- Automatically secure file permissions (if using file storage)
- Fall back to alternative methods if the preferred method fails

**Option B: Environment Variables (Quick Setup)**
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export CMDRX_OPENAI_API_KEY="sk-your-actual-key"' >> ~/.zshrc
source ~/.zshrc
```

**Option C: One-time Usage**
```bash
CMDRX_OPENAI_API_KEY="sk-your-key" cmdrx your-command
```

## Command Line Options

```bash
cmdrx [OPTIONS] [COMMAND...]

Options:
  -c, --config          Open configuration interface
  -v, --verbose         Enable verbose output
  --version            Show version and exit
  --log-dir PATH       Override default log directory
  --dry-run            Analyze without creating fix scripts
  --help               Show help message
```

## Generated Files

CmdRx generates several types of output files:

### Log Files
- **Location**: `~/cmdrx_logs/` (configurable)
- **Format**: `cmdrx_analysis_YYYYMMDD_HHMMSS.log`
- **Content**: Complete analysis with system info, command output, and AI response

### Fix Scripts
- **Location**: `~/cmdrx_logs/` (configurable)
- **Format**: `cmdrx_fix_YYYYMMDD_HHMMSS.sh`
- **Content**: Executable bash script with suggested fixes
- **Safety**: Includes confirmations and risk warnings

## Security Considerations

- **Credential Storage**: Multiple secure options (system keyring, environment variables, encrypted file)
- **File Permissions**: Credentials files automatically secured with `chmod 600` (owner-only access)
- **No Plain Text**: API keys never stored in configuration files or logs
- **Input Validation**: Commands are validated to prevent injection attacks
- **Fix Scripts**: Generated with safety confirmations and warnings
- **HTTPS**: All remote API calls use HTTPS encryption
- **No Auto-Execution**: Fixes require explicit user approval
- **Fallback Security**: If keyring fails, secure alternatives are available

## Troubleshooting

### Common Issues

**Configuration Error: No LLM provider configured**
```bash
cmdrx --config  # Run configuration wizard
```

**API Key Issues**
```bash
# Method 1: Interactive configuration
cmdrx --config

# Method 2: Environment variable (quick fix)
export CMDRX_OPENAI_API_KEY="sk-your-key"

# Method 3: Check which credential source is being used
cmdrx --verbose echo "test"  # Shows credential source in output

# Method 4: Verify credential file
ls -la ~/.config/cmdrx/credentials.json
```

**Keyring Problems**
If system keyring is unavailable, CmdRx automatically falls back to:
```bash
# Use environment variables instead
export CMDRX_OPENAI_API_KEY="sk-your-key"

# Or create credentials file
mkdir -p ~/.config/cmdrx
echo '{"openai_api_key": "sk-your-key"}' > ~/.config/cmdrx/credentials.json
chmod 600 ~/.config/cmdrx/credentials.json
```

**Connection Problems**
```bash
# Test your configuration
cmdrx --config  # Use "Test Configuration" option
```

### Verbose Mode

For detailed debugging information:
```bash
cmdrx --verbose your-command
```

### Log Files

Check the generated log files for complete analysis details:
```bash
ls -la ~/cmdrx_logs/
cat ~/cmdrx_logs/cmdrx_analysis_*.log
```

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/ryantischer2/cmdrx.git
cd cmdrx
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=src/cmdrx
```

### Code Quality

```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [cmdrx.readthedocs.io](https://cmdrx.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/ryantischer2/cmdrx/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ryantischer2/cmdrx/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

---

**Disclaimer**: CmdRx provides AI-generated suggestions. Always review and understand commands before executing them. The authors are not responsible for any system damage or data loss.