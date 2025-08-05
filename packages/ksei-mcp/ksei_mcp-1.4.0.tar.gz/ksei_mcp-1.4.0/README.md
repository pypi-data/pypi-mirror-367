# KSEI MCP

An **unofficial Model Context Protocol (MCP)** server for accessing your [AKSes KSEI](https://akses.ksei.co.id) (Acuan Kepemilikan Sekuritas Kustodian Sentral Efek Indonesia) portfolio data.

This server enables AI assistants to retrieve Indonesian securities portfolio information, including:

* Cash balances
* Equity holdings
* Mutual funds
* Bonds
* Other investments

---

## 🔧 Prerequisites

* Python 3.11 or higher
* Valid KSEI account credentials
* [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed (recommended for quick execution)

---

## ⚙️ Installation & Setup

### 1. Set Environment Variables

Set the following environment variables:

```bash
export KSEI_USERNAME="your_ksei_username"
export KSEI_PASSWORD="your_ksei_password"
export KSEI_AUTH_PATH="./data"  # Optional, defaults to "./data" for saving auth tokens
```

### 2. Run with `uvx` (Recommended)

The easiest way to start the server is with [`uvx`](https://docs.astral.sh/uv/reference/cli/#uvx):

```bash
# Run directly from PyPI
uvx ksei-mcp

# Or run from the local directory
uvx --from . ksei-mcp
```

### 3. Alternative: Traditional Installation

If you prefer manual installation:

```bash
# Install dependencies
pip install -e .
```

---

## 🤖 Usage with MCP Clients

Add this configuration to your MCP-compatible client:

```json
{
  "mcpServers": {
    "ksei": {
      "type": "stdio",
      "command": "uvx",
      "args": ["ksei-mcp@latest"]
    }
  }
}
```

---

## 🧪 Development: Using MCP Inspector

For local testing and development:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run with inspector
mcp-inspector uvx --from . ksei-mcp
```

---

## 💬 Example Queries

Once integrated into your AI assistant, you can ask:

```
"Show me my KSEI portfolio summary"
"What are my current cash balances?"
"List all my equity holdings"
"Get my mutual fund investments"
"Fetch all portfolio data"
```

### Example (Using Gemini CLI)

![Gemini CLI Example](assets/gemini.png)

Other supported clients include GitHub Copilot, Claude, and any MCP-compatible assistant.

---

## 🔐 Security Considerations

* **Credentials**: Never commit credentials to version control. Use environment variables or secure vaults.
* **Token Storage**: Auth tokens are stored locally as JSON files.
* **Secure Transport**: All communication with KSEI uses HTTPS.
* **Access Control**: Restrict file system access to the authentication and data directories.

---

## 🛠️ Contributing

1. Fork this repository
2. Create a feature branch
3. Implement your changes
4. Add tests (if applicable)
5. Open a pull request

---

## 📄 License

Licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## ⚠️ Disclaimer

This software is intended for **educational and personal use only**. Users are responsible for complying with KSEI's terms of service and all relevant regulations.

> **Note**: This is an **unofficial client** for KSEI services. It is not affiliated with or endorsed by KSEI.

### Acknowledgement

This project is an adaptation from [chickenzord/goksei](https://github.com/chickenzord/goksei). Many thanks to the original author for their work and inspiration.
