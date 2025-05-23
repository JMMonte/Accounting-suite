import hashlib
import time
from typing import Optional, Tuple
import streamlit as st


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed_password


def get_user_credentials() -> dict:
    """Get user credentials from secrets."""
    return {
        "admin": st.secrets["auth"]["admin_password"],
        "gestor": st.secrets["auth"]["gestor_password"],
    }


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user with username and password."""
    credentials = get_user_credentials()
    if username in credentials:
        return credentials[username] == password
    return False


def get_user_role(username: str) -> str:
    """Get user role based on username."""
    roles = {"admin": "Administrador", "gestor": "Gestor"}
    return roles.get(username, "Utilizador")


def login_form() -> Tuple[Optional[str], Optional[str]]:
    """Display login form and return username, role if successful."""
    st.markdown("### 🔐 Autenticação")
    st.markdown("Acesso ao sistema de gestão de despesas")

    with st.form("login_form"):
        username = st.text_input("Nome de utilizador")
        password = st.text_input("Palavra-passe", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if authenticate_user(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["user_role"] = get_user_role(username)
                st.session_state["login_time"] = time.time()

                # Log successful login
                try:
                    import audit_log

                    audit_log.log_login(username, get_user_role(username))
                except ImportError:
                    pass  # Audit logging not available

                st.success("✅ Autenticação bem-sucedida!")
                st.rerun()

    return None, None


def is_session_valid() -> bool:
    """Check if the current session is still valid."""
    if not st.session_state.get("authenticated", False):
        return False

    # Check session timeout
    try:
        session_timeout = st.secrets["app"]["session_timeout"]
    except KeyError:
        session_timeout = 3600  # 1 hour default

    login_time = st.session_state.get("login_time", 0)
    current_time = time.time()

    if current_time - login_time > session_timeout:
        logout_user()
        return False

    return True


def logout_user():
    """Logout the current user and clear session state."""
    # Log logout before clearing session
    try:
        import audit_log

        username = st.session_state.get("username", "Unknown")
        audit_log.log_logout(username)
    except ImportError:
        pass

    keys_to_clear = [
        "authenticated",
        "username",
        "user_role",
        "login_time",
        "password_correct",
        "password",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def require_auth():
    """Decorator/function to require authentication for accessing the app."""
    if not is_session_valid():
        st.title("🧾 Mapa de Despesas Automático")
        st.markdown("---")

        # Display login form
        login_form()

        if not st.session_state.get("authenticated", False):
            st.warning("⚠️ Por favor, faça login para aceder ao sistema.")
            st.stop()

    return True


def get_current_user() -> dict:
    """Get current authenticated user information."""
    return {
        "username": st.session_state.get("username", ""),
        "role": st.session_state.get("user_role", ""),
        "login_time": st.session_state.get("login_time", 0),
    }


def display_user_info():
    """Display current user information in the sidebar."""
    if st.session_state.get("authenticated", False):
        user = get_current_user()
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Utilizador")
        st.sidebar.write(f"**Nome:** {user['username']}")
        st.sidebar.write(f"**Papel:** {user['role']}")

        # Show session info
        login_time = user.get("login_time", 0)
        if login_time:
            session_duration = int(time.time() - login_time)
            minutes, seconds = divmod(session_duration, 60)
            hours, minutes = divmod(minutes, 60)
            st.sidebar.write(f"**Sessão:** {hours:02d}:{minutes:02d}:{seconds:02d}")

        # Logout button
        if st.sidebar.button("🚪 Terminar Sessão"):
            logout_user()
            st.rerun()
