import random
from datetime import datetime, date, timedelta
from workalendar.europe import Portugal
import streamlit as st
import pandas as pd
from util import (
    random_fill_days,
    split_dia_hora,
    export_to_excel,
    group_consecutive_days,
    categorize_trips,
)
from constants import (
    OBJECTIVES,
    PARFOIS_ADDRESS,
    EXCEL_TEMPLATE_PATH,
    COMPANY_NAME,
    COMPANY_NIPC,
    COMPANY_ADDRESS,
    GESTOR_NAME,
    GESTOR_ADDRESS,
    GESTOR_NIFPS,
    GESTOR_CATEGORIA,
    YEAR_MIN,
    YEAR_MAX,
    MAX_DAILY_MIN,
    MAX_DAILY_MAX,
    MAX_DAILY_DEFAULT,
    MAX_TOTAL_MIN,
    MAX_TOTAL_MAX,
    MAX_TOTAL_DEFAULT,
)

# --- Streamlit Page Config ---
st.set_page_config(page_title="Mapa de Despesas Automático", layout="centered")
st.title("Mapa de Despesas Automático - Ajudas de Custo Nacionais")

# --- Sidebar: User Inputs ---
st.sidebar.header("Configurações")

# Frequently changed options
today = datetime.today()
default_year = today.year
default_month = today.month

# Max daily value for 2025 legal limit for gestor
LEGAL_MAX_DAILY_2025 = 72.65

# Month and year selection
month = st.sidebar.selectbox(
    "Mês",
    options=list(range(1, 13)),
    index=today.month - 1,
    format_func=lambda x: datetime(2000, x, 1).strftime("%B").capitalize(),
)
year = st.sidebar.number_input(
    "Ano", min_value=YEAR_MIN, max_value=YEAR_MAX, value=today.year
)

# Set max_daily default and max for 2025
max_daily_default = LEGAL_MAX_DAILY_2025 if year == 2025 else MAX_DAILY_DEFAULT
max_daily_max = LEGAL_MAX_DAILY_2025 if year == 2025 else MAX_DAILY_MAX
max_daily = st.sidebar.number_input(
    "Valor máximo diário (€)",
    min_value=float(MAX_DAILY_MIN),
    max_value=float(max_daily_max),
    value=float(max_daily_default),
    help=(
        "Limite legal para gestor em 2025: 72,65 € (Decreto-Lei n.º 1/2025, de 16 de janeiro)"
        if year == 2025 else ""
    ),
)
max_total = st.sidebar.number_input(
    "Valor máximo total do mês (€)",
    min_value=MAX_TOTAL_MIN,
    max_value=MAX_TOTAL_MAX,
    value=MAX_TOTAL_DEFAULT,
)

# Less frequently changed: company and gestor info
with st.sidebar.expander("Dados da Empresa e Gestor", expanded=False):
    company_name = st.text_input("Nome da Empresa", value=COMPANY_NAME)
    company_nipc = st.text_input("NIPC da Empresa", value=COMPANY_NIPC)
    company_address = st.text_input("Morada da Empresa", value=COMPANY_ADDRESS)
    gestor_name = st.text_input("Gestor", value=GESTOR_NAME)
    gestor_address = st.text_input("Morada do Gestor", value=GESTOR_ADDRESS)
    gestor_nifps = st.text_input("NIFPS do Gestor", value=GESTOR_NIFPS)
    gestor_categoria = st.text_input("Categoria do Gestor", value=GESTOR_CATEGORIA)
    signature_file = st.file_uploader(
        "Assinatura (imagem)", type=["png", "jpg", "jpeg"]
    )

# Placeholder for next steps
st.info("Configure as opções à esquerda e avance para gerar o ficheiro Excel.")

# Set a random seed for reproducibility based on year, month, and company NIPC
seed_str = f"{year}-{month}-{company_nipc}"
random.seed(seed_str)

# --- Step 1: Generate all days in the selected month and business days ---
first_day = date(year, month, 1)
if month == 12:
    next_month = date(year + 1, 1, 1)
else:
    next_month = date(year, month + 1, 1)

days_in_month = (next_month - first_day).days
all_days = [first_day + timedelta(days=i) for i in range(days_in_month)]

# Business days
cal = Portugal()
business_days = [d for d in all_days if cal.is_working_day(d)]

# --- Step 2: Fill business days as before ---
filled_days, total_filled = random_fill_days(business_days, max_daily, max_total)
filled_dict = {d["Data"]: d for d in filled_days}

# --- Step: Aggregate consecutive filled business days into trips ---
trips = group_consecutive_days(filled_days)
filled_days_categorized = categorize_trips(
    trips, max_daily, OBJECTIVES, PARFOIS_ADDRESS
)

filled_dict = {d["Data"]: d for d in filled_days_categorized}


def safe_float(val):
    """
    Convert a value to a float, returning 0.0 if conversion fails.
    """
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


total_filled = sum(
    safe_float(d.get(key, 0))
    for d in filled_days_categorized
    for key in ["Valor 100% (€)", "Valor 75% (€)", "Valor 50% (€)", "Valor 25% (€)"]
)

# Calculate Sub Total a Pagar as in Excel
sub_total = total_filled

# --- Step 3: Prepare preview table with all days ---
preview_rows = []
for d in all_days:
    data_str = d.strftime("%Y-%m-%d")
    filled = filled_dict.get(data_str)
    if filled:
        objetivo = random.choice(OBJECTIVES)
        local = PARFOIS_ADDRESS
        inicio = filled.get("inicio (Dia Hora)", "")
        regresso = filled.get("regresso (Dia Hora)", "")
        valor_100 = filled.get("Valor 100% (€)", "")
        valor_75 = filled.get("Valor 75% (€)", "")
        valor_50 = filled.get("Valor 50% (€)", "")
        valor_25 = filled.get("Valor 25% (€)", "")
        inicio_dia, inicio_hora = split_dia_hora(inicio)
        regresso_dia, regresso_hora = split_dia_hora(regresso)
        row = {
            "Data": data_str,
            "Mapa deslocação / Objectivo": objetivo,
            "Local onde foram prestados": local,
            "Início Dia": inicio_dia,
            "Início Hora": inicio_hora,
            "Regresso Dia": regresso_dia,
            "Regresso Hora": regresso_hora,
            "100%": 1 if valor_100 != "" else 0,
            "75%": 1 if valor_75 != "" else 0,
            "50%": 1 if valor_50 != "" else 0,
            "25%": 1 if valor_25 != "" else 0,
            "_gray": False,
        }
        preview_rows.append(row)
# Only filled days are included in preview_rows now

preview_df = pd.DataFrame(preview_rows)
preview_df = preview_df[
    [
        "Data",
        "Mapa deslocação / Objectivo",
        "Local onde foram prestados",
        "Início Dia",
        "Início Hora",
        "Regresso Dia",
        "Regresso Hora",
        "100%",
        "75%",
        "50%",
        "25%",
        "_gray",
    ]
]

# --- Step 4: Calculate maximum possible value for the month ---
max_possible_value = max_daily * len(business_days)


# --- Step 5: Show preview table with color formatting ---
def highlight_gray(row_data):
    """
    Highlight gray rows in the preview table.
    """
    color = (
        "color: gray; background-color: #f0f0f0;"
        if row_data.get("_gray", False)
        else ""
    )
    return [color] * len(row_data)


if not preview_df.empty and "_gray" in preview_df.columns:
    styled_df = preview_df.drop(columns=["_gray"]).style.apply(highlight_gray, axis=1)
    st.dataframe(styled_df, hide_index=True)
else:
    st.dataframe(preview_df, hide_index=True)

st.write(f"**Total atribuído:** {total_filled} € (máximo: {max_total} €)")
st.write(
    f"**Valor máximo possível para o mês:** {max_possible_value} € (usando todos os dias úteis a {max_daily} €)"
)
st.write(f"**Sub Total a Pagar:** {sub_total:.2f} €")

# --- Excel Export Functionality ---
output_file_name = f"MapaDespesas_{year:04d}_{month:02d}_{company_nipc}.xlsx"
excel_bytes = export_to_excel(
    EXCEL_TEMPLATE_PATH,
    preview_df.drop(columns=["_gray"]),
    company_name,
    company_nipc,
    company_address,
    gestor_name,
    gestor_address,
    gestor_nifps,
    gestor_categoria,
    signature_file,
    max_daily,
)

st.download_button(
    label="Download Excel preenchido",
    data=excel_bytes,
    file_name=output_file_name,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
