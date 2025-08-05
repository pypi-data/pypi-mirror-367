import json
import time
import os
import hashlib
import base64
from urllib.parse import quote
import requests
import jwt
from fake_useragent import UserAgent
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
import mcp.types as types


class FileAuthStore:
    def __init__(self, directory):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def _get_path(self, key):
        return os.path.join(self.directory, f"{key}.json")

    def get(self, key):
        try:
            with open(self._get_path(key), "r") as f:
                return json.load(f)
        except:
            return None

    def set(self, key, value):
        with open(self._get_path(key), "w") as f:
            json.dump(value, f)


def get_expire_time(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get("exp")
    except:
        return None


class KSEIClient:
    def __init__(self, auth_store=None, username="", password="", plain_password=True):
        self.base_url = "https://akses.ksei.co.id/service"
        self.base_referer = "https://akses.ksei.co.id"
        self.auth_store = auth_store
        self.username = username
        self.password = password
        self.plain_password = plain_password
        self.ua = UserAgent()

    def _hash_password(self):
        if not self.plain_password:
            return self.password

        password_sha1 = hashlib.sha1(self.password.encode()).hexdigest()
        timestamp = int(time.time())
        param = f"{password_sha1}@@!!@@{timestamp}"
        encoded_param = base64.b64encode(param.encode()).decode()

        url = f"{self.base_url}/activation/generated?param={quote(encoded_param)}"

        response = requests.get(
            url, headers={"Referer": self.base_referer, "User-Agent": self.ua.random}
        )
        response.raise_for_status()

        data = response.json()
        return data["data"][0]["pass"]

    def _login(self):
        hashed_password = self._hash_password()

        login_data = {
            "username": self.username,
            "password": hashed_password,
            "id": "1",
            "appType": "web",
        }

        response = requests.post(
            f"{self.base_url}/login?lang=id",
            json=login_data,
            headers={
                "Referer": self.base_referer,
                "User-Agent": self.ua.random,
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()

        token = response.json()["validation"]

        if self.auth_store:
            self.auth_store.set(self.username, token)

        return token

    def _get_token(self):
        if not self.auth_store:
            return self._login()

        token = self.auth_store.get(self.username)
        if not token:
            return self._login()

        expire_time = get_expire_time(token)
        if not expire_time or expire_time < time.time():
            return self._login()

        return token

    def get(self, path):
        token = self._get_token()

        response = requests.get(
            f"{self.base_url}{path}",
            headers={
                "Referer": self.base_referer,
                "User-Agent": self.ua.random,
                "Authorization": f"Bearer {token}",
            },
        )
        response.raise_for_status()
        return response.json()

    def get_portfolio_summary(self):
        return self.get("/myportofolio/summary")

    def get_cash_balances(self):
        return self.get("/myportofolio/summary-detail/kas")

    def get_equity_balances(self):
        return self.get("/myportofolio/summary-detail/ekuitas")

    def get_mutual_fund_balances(self):
        return self.get("/myportofolio/summary-detail/reksadana")

    def get_bond_balances(self):
        return self.get("/myportofolio/summary-detail/obligasi")

    def get_other_balances(self):
        return self.get("/myportofolio/summary-detail/lainnya")

    def get_global_identity(self):
        return self.get("/myaccount/global-identity/")

    async def get_async(self, session, path):
        token = self._get_token()

        async with session.get(
            f"{self.base_url}{path}",
            headers={
                "Referer": self.base_referer,
                "User-Agent": self.ua.random,
                "Authorization": f"Bearer {token}",
            },
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_all_portfolios_async(self):
        portfolio_types = {
            "cash": "/myportofolio/summary-detail/kas",
            "equity": "/myportofolio/summary-detail/ekuitas",
            "mutual_fund": "/myportofolio/summary-detail/reksadana",
            "bond": "/myportofolio/summary-detail/obligasi",
            "other": "/myportofolio/summary-detail/lainnya",
        }

        async with aiohttp.ClientSession() as session:
            tasks = []
            for portfolio_type, path in portfolio_types.items():
                task = asyncio.create_task(
                    self.get_async(session, path), name=portfolio_type
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            portfolio_data = {}
            for task, result in zip(tasks, results):
                portfolio_type = task.get_name()
                if isinstance(result, Exception):
                    print(f"Error fetching {portfolio_type}: {result}")
                    portfolio_data[portfolio_type] = None
                else:
                    portfolio_data[portfolio_type] = result

            return portfolio_data


# Initialize the MCP server
server = Server("ksei-server")

# Initialize KSEI client
username = os.getenv("KSEI_USERNAME")
password = os.getenv("KSEI_PASSWORD")
auth_path = os.getenv("KSEI_AUTH_PATH", "./auth")

if not username or not password:
    raise ValueError(
        "KSEI_USERNAME and KSEI_PASSWORD environment variables must be set"
    )

auth_store = FileAuthStore(directory=auth_path)
ksei_client = KSEIClient(auth_store=auth_store, username=username, password=password)


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available KSEI resources."""
    return [
        Resource(
            uri="ksei://portfolio/summary",
            name="Portfolio Summary",
            description="Overview of all portfolio holdings and balances",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/cash",
            name="Cash Balances",
            description="Detailed cash balances across securities companies",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/equity",
            name="Equity Holdings",
            description="Stock and equity holdings details",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/mutual-fund",
            name="Mutual Fund Holdings",
            description="Mutual fund investment details",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/bond",
            name="Bond Holdings",
            description="Bond and fixed income securities",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://portfolio/other",
            name="Other Holdings",
            description="Other financial instruments and investments",
            mimeType="application/json",
        ),
        Resource(
            uri="ksei://account/identity",
            name="Account Identity",
            description="Account holder identity and profile information",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific KSEI resource."""
    try:
        if uri == "ksei://portfolio/summary":
            data = ksei_client.get_portfolio_summary()
        elif uri == "ksei://portfolio/cash":
            data = ksei_client.get_cash_balances()
        elif uri == "ksei://portfolio/equity":
            data = ksei_client.get_equity_balances()
        elif uri == "ksei://portfolio/mutual-fund":
            data = ksei_client.get_mutual_fund_balances()
        elif uri == "ksei://portfolio/bond":
            data = ksei_client.get_bond_balances()
        elif uri == "ksei://portfolio/other":
            data = ksei_client.get_other_balances()
        elif uri == "ksei://account/identity":
            data = ksei_client.get_global_identity()
        else:
            raise ValueError(f"Unknown resource URI: {uri}")

        return json.dumps(data, indent=2, ensure_ascii=False)

    except Exception as e:
        raise RuntimeError(f"Failed to fetch resource {uri}: {str(e)}")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available KSEI tools."""
    return [
        Tool(
            name="get_portfolio_summary",
            description="Get a summary of all portfolio holdings and balances",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_cash_balances",
            description="Get detailed cash balances across all securities companies",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_equity_balances",
            description="Get detailed equity/stock holdings",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_mutual_fund_balances",
            description="Get mutual fund investment details",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_bond_balances",
            description="Get bond and fixed income securities details",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_other_balances",
            description="Get other financial instruments and investments",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_global_identity",
            description="Get account holder identity and profile information",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_all_portfolios",
            description="Get all portfolio data concurrently (cash, equity, mutual funds, bonds, other)",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls for KSEI operations."""
    try:
        if name == "get_portfolio_summary":
            result = ksei_client.get_portfolio_summary()
        elif name == "get_cash_balances":
            result = ksei_client.get_cash_balances()
        elif name == "get_equity_balances":
            result = ksei_client.get_equity_balances()
        elif name == "get_mutual_fund_balances":
            result = ksei_client.get_mutual_fund_balances()
        elif name == "get_bond_balances":
            result = ksei_client.get_bond_balances()
        elif name == "get_other_balances":
            result = ksei_client.get_other_balances()
        elif name == "get_global_identity":
            result = ksei_client.get_global_identity()
        elif name == "get_all_portfolios":
            result = await ksei_client.get_all_portfolios_async()
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [
            TextContent(
                type="text", text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]

    except Exception as e:
        return [TextContent(type="text", text=f"Error calling tool {name}: {str(e)}")]


async def main():
    # Import here to avoid issues if mcp package is not available
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ksei-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run():
    asyncio.run(main())
