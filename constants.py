OBJECTIVES = [
    "Viagem a visitar cliente Parfois (HQ)",
    "Reunião com cliente Parfois",
    "Entrega de documentação a Parfois",
    "Visita técnica a Parfois",
    "Formação em cliente Parfois",
]

PARFOIS_ADDRESS = "Parfois S.A., Rua de Sistelo, 755 - Lugar de Santegãos, 4435-429 Rio Tinto, Portugal"

EXCEL_TEMPLATE_PATH = "MG_AjudasCustoNacionais_Original_V2025.xlsx"
EXCEL_OUTPUT_NAME = "MapaDespesasPreenchido.xlsx"
COMPANY_NAME = "Your Company Name"
COMPANY_NIPC = "000000000"
COMPANY_ADDRESS = "Your Company Address"
GESTOR_NAME = "Your Name"
GESTOR_ADDRESS = "Your Address"
GESTOR_NIFPS = "000000000"
GESTOR_CATEGORIA = "Gestor"

EXCEL_START_ROW = 10
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
