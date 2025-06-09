import json
import os
from datetime import datetime
from typing import Optional
import streamlit as st


AUDIT_LOG_FILE = "audit_log.json"


def load_audit_log() -> list:
    """Load existing audit log from file."""
    if not os.path.exists(AUDIT_LOG_FILE):
        return []
    
    try:
        with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_audit_log(log_entries: list):
    """Save audit log to file."""
    try:
        with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_entries, f, ensure_ascii=False, indent=2)
    except (IOError, OSError) as e:
        st.error(f"Erro ao guardar log de auditoria: {e}")


def log_activity(action: str, details: Optional[str] = None, sensitive_data: bool = False):
    """Log user activity."""
    # Don't log if user is not authenticated
    if not st.session_state.get("authenticated", False):
        return
    
    username = st.session_state.get("username", "Unknown")
    user_role = st.session_state.get("user_role", "Unknown")
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "user_role": user_role,
        "action": action,
        "details": details if not sensitive_data else "[DADOS SENSÍVEIS]",
        "ip_address": "localhost",  # In production, you'd get real IP
        "session_id": id(st.session_state)  # Simple session identifier
    }
    
    # Load existing logs
    audit_log = load_audit_log()
    
    # Add new entry
    audit_log.append(log_entry)
    
    # Keep only last 1000 entries to prevent file from growing too large
    if len(audit_log) > 1000:
        audit_log = audit_log[-1000:]
    
    # Save back to file
    save_audit_log(audit_log)


def get_user_activity(username: Optional[str] = None, limit: int = 50) -> list:
    """Get recent user activity, optionally filtered by username."""
    audit_log = load_audit_log()
    
    if username:
        filtered_log = [entry for entry in audit_log if entry.get("username") == username]
    else:
        filtered_log = audit_log
    
    # Return most recent entries
    return sorted(filtered_log, key=lambda x: x["timestamp"], reverse=True)[:limit]


def display_audit_log():
    """Display audit log for administrators."""
    current_user = st.session_state.get("user_role", "")
    
    if current_user != "Administrador":
        st.error("⚠️ Acesso negado. Apenas administradores podem ver o log de auditoria.")
        return
    
    st.header("📋 Log de Auditoria")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_user = st.selectbox(
            "Filtrar por utilizador",
            options=["Todos"] + list(set([entry.get("username", "") for entry in load_audit_log()])),
            index=0
        )
    
    with col2:
        limit = st.number_input("Número de entradas", min_value=10, max_value=500, value=50)
    
    # Get filtered data
    username_filter = None if filter_user == "Todos" else filter_user
    activities = get_user_activity(username_filter, limit)
    
    if not activities:
        st.info("📭 Nenhuma atividade registada.")
        return
    
    # Display activities
    for activity in activities:
        with st.expander(f"🕐 {activity['timestamp']} - {activity['username']} - {activity['action']}"):
            st.write(f"**Utilizador:** {activity['username']}")
            st.write(f"**Papel:** {activity['user_role']}")
            st.write(f"**Ação:** {activity['action']}")
            if activity.get('details'):
                st.write(f"**Detalhes:** {activity['details']}")
            st.write(f"**Timestamp:** {activity['timestamp']}")
            st.write(f"**IP:** {activity.get('ip_address', 'N/A')}")


def log_login(username: str, role: str):
    """Log successful login."""
    log_activity("LOGIN", f"Utilizador {username} ({role}) fez login com sucesso")


def log_logout(username: str):
    """Log logout."""
    log_activity("LOGOUT", f"Utilizador {username} fez logout")


def log_expense_generation(year: int, month: int, total_value: float, max_daily: float):
    """Log expense map generation."""
    log_activity(
        "GERAÇÃO_MAPA_DESPESAS",
        f"Gerou mapa de despesas para {month:02d}/{year} - Total: {total_value:.2f}€ - Máx. diário: {max_daily:.2f}€",
        sensitive_data=True
    )


def log_excel_download(filename: str):
    """Log Excel file download."""
    log_activity("DOWNLOAD_EXCEL", f"Download do ficheiro: {filename}")


def log_config_change(field: str, old_value: str, new_value: str):
    """Log configuration changes."""
    log_activity(
        "ALTERAÇÃO_CONFIGURAÇÃO",
        f"Campo '{field}' alterado de '{old_value}' para '{new_value}'"
    ) 