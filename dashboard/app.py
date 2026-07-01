import os
import time
from datetime import datetime

import httpx
import pandas as pd
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")


def headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY} if API_KEY else {}


@st.cache_data(ttl=2)
def fetch_metrics() -> dict[str, float]:
    response = httpx.get(f"{API_BASE_URL}/metrics", timeout=5.0)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=2)
def fetch_servers() -> list[dict]:
    response = httpx.get(f"{API_BASE_URL}/servers", timeout=5.0)
    response.raise_for_status()
    return response.json()


def register_server(name: str, host: str, port: int, tags: list[str]) -> None:
    response = httpx.post(
        f"{API_BASE_URL}/servers",
        json={"name": name, "host": host, "port": port, "tags": tags},
        headers=headers(),
        timeout=5.0,
    )
    response.raise_for_status()
    fetch_servers.clear()


def check_server(server_id: int) -> None:
    response = httpx.post(f"{API_BASE_URL}/servers/{server_id}/check", timeout=8.0)
    response.raise_for_status()
    fetch_servers.clear()


def status_style(value: str) -> str:
    colors = {
        "UP": "background-color: #d1fae5; color: #065f46",
        "DEGRADED": "background-color: #fef3c7; color: #92400e",
        "DOWN": "background-color: #fee2e2; color: #991b1b",
        "unknown": "background-color: #e5e7eb; color: #374151",
    }
    return colors.get(value, "")


st.set_page_config(page_title="DevOps Monitoring Dashboard", layout="wide")
st.title("DevOps Monitoring Dashboard")

metrics_tab, servers_tab = st.tabs(["Metrics", "Servers"])

with metrics_tab:
    if "history" not in st.session_state:
        st.session_state.history = []

    try:
        metrics = fetch_metrics()
        st.session_state.history.append(
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                **metrics,
            }
        )
        st.session_state.history = st.session_state.history[-60:]

        cpu_col, memory_col, disk_col = st.columns(3)
        cpu_col.metric("CPU", f"{metrics['cpu_percent']:.1f}%")
        memory_col.metric("Memory", f"{metrics['memory_percent']:.1f}%")
        disk_col.metric("Disk", f"{metrics['disk_percent']:.1f}%")

        history = pd.DataFrame(st.session_state.history).set_index("time")
        st.line_chart(history)

        if st.toggle("Auto refresh", value=False):
            time.sleep(1)
            st.rerun()
    except httpx.HTTPError as exc:
        st.error(f"Unable to load metrics: {exc}")

with servers_tab:
    try:
        servers = fetch_servers()
        if servers:
            dataframe = pd.DataFrame(servers)
            styled = dataframe.style.map(status_style, subset=["status"])
            st.dataframe(styled, use_container_width=True, hide_index=True)
        else:
            st.info("No servers registered yet.")

        with st.form("register-server", clear_on_submit=True):
            name = st.text_input("Name")
            host = st.text_input("Host", placeholder="httpbin.org")
            port = st.number_input("Port", min_value=1, max_value=65535, value=443)
            tags = st.text_input("Tags", placeholder="prod,api")
            submitted = st.form_submit_button("Register server")
            if submitted:
                parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
                register_server(name=name, host=host, port=int(port), tags=parsed_tags)
                st.success("Server registered.")
                st.rerun()

        if servers:
            server_ids = {
                f"{server['id']} - {server['name']}": server["id"]
                for server in servers
            }
            selected = st.selectbox("Manual health check", list(server_ids))
            if st.button("Check selected server"):
                check_server(server_ids[selected])
                st.rerun()
    except httpx.HTTPError as exc:
        st.error(f"Unable to load servers: {exc}")
