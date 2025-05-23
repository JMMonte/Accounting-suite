import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Client information loaded from environment variables (default to generic placeholders)
DEFAULT_OBJECTIVES = [
    "Reunião de trabalho",
    "Visita a cliente",
    "Entrega de documentação",
    "Visita técnica",
    "Formação em cliente",
]

# Parse objectives from environment variable (comma-separated) or use defaults
OBJECTIVES_ENV = os.getenv("CLIENT_OBJECTIVES", "")
if OBJECTIVES_ENV.strip():
    OBJECTIVES = [obj.strip() for obj in OBJECTIVES_ENV.split(",") if obj.strip()]
else:
    OBJECTIVES = DEFAULT_OBJECTIVES

CLIENT_ADDRESS = os.getenv("CLIENT_ADDRESS", "Endereço do Cliente, Cidade, Portugal")

EXCEL_TEMPLATE_PATH = os.getenv("EXCEL_TEMPLATE_PATH", "MapaDespesas_2025.xlsx")
EXCEL_OUTPUT_NAME = "MapaDespesasPreenchido.xlsx"

# Private information loaded from environment variables
COMPANY_NAME = os.getenv("COMPANY_NAME", "Your Company Name")
COMPANY_NIPC = os.getenv("COMPANY_NIPC", "000000000")
COMPANY_ADDRESS = os.getenv("COMPANY_ADDRESS", "Your Company Address")
GESTOR_NAME = os.getenv("GESTOR_NAME", "Your Name")
GESTOR_ADDRESS = os.getenv("GESTOR_ADDRESS", "Your Address")
GESTOR_NIFPS = os.getenv("GESTOR_NIFPS", "000000000")
GESTOR_CATEGORIA = os.getenv("GESTOR_CATEGORIA", "Gestor")

# Authentication credentials from environment variables
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "default_admin_password")
GESTOR_USERNAME = os.getenv("GESTOR_USERNAME", "gestor")
GESTOR_PASSWORD = os.getenv("GESTOR_PASSWORD", "default_gestor_password")

# Application settings from environment variables
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour default

EXCEL_START_ROW = 11
EXCEL_MAX_ROW = 35
EXCEL_COLUMN_MAPPING = [
    ("B", "Data"),
    ("C", "Mapa deslocação / Objectivo"),
    ("E", "Local onde foram prestados"),
    ("F", "Início Dia"),
    ("G", "Início Hora"),
    ("H", "Regresso Dia"),
    ("I", "Regresso Hora"),
]

YEAR_MIN = 2020
YEAR_MAX = 2100
MAX_DAILY_MIN = 1
MAX_DAILY_MAX = 100
MAX_DAILY_DEFAULT = 65
MAX_TOTAL_MIN = 1
MAX_TOTAL_MAX = 5000
MAX_TOTAL_DEFAULT = 1000

TRIP_START_TIME = "09:00"
TRIP_END_TIME = "18:00"
