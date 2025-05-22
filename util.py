# util.py
"""
This file contains the utility functions for the app.

Functions:
- random_fill_days: Fill business days with random values,
respecting the max_daily and max_total constraints.
- split_dia_hora: Split a date and time string into two parts.
- export_to_excel: Export the preview DataFrame to an Excel file.
- group_consecutive_days: Group consecutive days into trips.
- categorize_trips: Categorize trips into 100%, 75%, 50%, and 25% values.
"""
# Standard library imports
import random
from io import BytesIO
from datetime import datetime
import io

# Third party imports
import openpyxl
from openpyxl.cell.cell import MergedCell
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage

# Local imports
from constants import (
    EXCEL_START_ROW,
    EXCEL_MAX_ROW,
    EXCEL_COLUMN_MAPPING,
    TRIP_START_TIME,
    TRIP_END_TIME,
)


def _generate_random_values(n, max_daily, max_total):
    """
    Generate random values for the days, respecting the max_daily and max_total constraints.
    """
    mean = max_daily * 0.8
    stddev = max_daily * 0.15
    values = []
    for _ in range(n):
        while True:
            value = random.gauss(mean, stddev)
            value = max(max_daily * 0.5, min(max_daily, value))
            value = round(value, 2)
            if not any(abs(value - v) < 0.5 for v in values):
                break
        values.append(value)
    scale = max_total / sum(values)
    values = [round(v * scale, 2) for v in values]
    for i, v in enumerate(values):
        values[i] = min(v, max_daily)
    diff = round(max_total - sum(values), 2)
    if abs(diff) > 0.01:
        values[-1] = round(values[-1] + diff, 2)
    return values


def _fill_days_with_values(days, values):
    filled_days_list = []
    for i, d in enumerate(sorted(days)):
        filled_days_list.append(
            {
                "Dia": d.day,
                "Data": d.strftime("%Y-%m-%d"),
                "Dia da Semana": d.strftime("%A"),
                "Valor (€)": values[i],
            }
        )
    return filled_days_list


def random_fill_days(business_days, max_daily, max_total):
    """
    Fill business days with random values, respecting the max_daily and max_total constraints.
    """
    days = business_days.copy()
    random.shuffle(days)
    min_possible = max_daily * 0.5 * len(days)
    if max_total > min_possible:
        n = len(days)
        values = _generate_random_values(n, max_daily, max_total)
        filled_days_list = _fill_days_with_values(days, values)
        total = round(sum(d["Valor (€)"] for d in filled_days_list), 2)
        return filled_days_list, total
    filled_days_list = []
    total = 0.0
    used_values = set()
    for d in days:
        if random.random() < 0.7:
            while True:
                value = random.gauss(max_daily * 0.8, max_daily * 0.15)
                value = max(max_daily * 0.5, min(max_daily, value))
                value = round(value, 2)
                if value not in used_values:
                    used_values.add(value)
                    break
            filled_days_list.append(
                {
                    "Dia": d.day,
                    "Data": d.strftime("%Y-%m-%d"),
                    "Dia da Semana": d.strftime("%A"),
                    "Valor (€)": value,
                }
            )
            total += value
            if total >= max_total:
                break
    if filled_days_list:
        total = sum(d["Valor (€)"] for d in filled_days_list)
        remainder = max_total - total
        i = len(filled_days_list) - 1
        while remainder > 0.01 and i >= 0:
            current = filled_days_list[i]["Valor (€)"]
            addable = min(max_daily - current, remainder)
            if addable > 0.01:
                filled_days_list[i]["Valor (€)"] = round(current + addable, 2)
                remainder -= addable
            i -= 1
        filled_days_list = [d for d in filled_days_list if d["Valor (€)"] > 0]
        total = round(sum(d["Valor (€)"] for d in filled_days_list), 2)
    return filled_days_list, total


def split_dia_hora(val):
    """
    Split a date and time string into two parts.
    """
    if val and isinstance(val, str) and len(val.split()) == 2:
        d, h = val.split()
        try:
            d = datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            pass
        return d, h
    return "", ""


def export_to_excel(
    template_path,
    preview_df,
    company_name,
    nipc,
    company_address,
    gestor_name,
    gestor_address,
    gestor_nifps,
    gestor_categoria,
    signature_file=None,
    max_daily=None,
):
    """
    Export the preview DataFrame to an Excel file.
    """
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active
    ws["C4"] = company_name
    ws["C5"] = nipc
    # Add company address to merged cell C6-I6
    ws["C6"] = company_address
    # Add Gestor info
    ws["C40"] = gestor_name
    ws["C41"] = gestor_address
    ws["C42"] = gestor_nifps
    ws["C43"] = gestor_categoria
    # Set Valor Atribuído (max_daily) in I40
    if max_daily is not None:
        ws["I40"] = max_daily
    # Add signature image (uploaded or default)

    if signature_file is not None:
        image_bytes = signature_file.read()
        pil_img = PILImage.open(io.BytesIO(image_bytes))
    else:
        pil_img = PILImage.open("black.png")
    # Resize to max width 200px, keep aspect ratio, don't upscale
    max_width = 200
    w, h = pil_img.size
    if w > max_width:
        new_w = max_width
        new_h = int(h * (max_width / w))
        pil_img = pil_img.resize((new_w, new_h), PILImage.Resampling.LANCZOS)
    img_buffer = io.BytesIO()
    pil_img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    xl_img = XLImage(img_buffer)
    ws.add_image(xl_img, "C65")
    start_row = EXCEL_START_ROW
    for i, row in enumerate(preview_df.iterrows(), start=start_row):
        if i > EXCEL_MAX_ROW:
            break
        row_dict = row[1].to_dict()
        mapping = EXCEL_COLUMN_MAPPING
        if i == start_row:
            print("DEBUG: Writing row_dict:", row_dict)
        for col, key in mapping:
            value = row_dict.get(key, "")
            cell = ws[f"{col}{i}"]
            if i == start_row:
                print(f"DEBUG: Writing to {col}{i}: {key} = {value}")
            if not isinstance(cell, MergedCell):
                cell.value = value
        for col, col_name in zip(["K", "L", "M", "N"], ["100%", "75%", "50%", "25%"]):
            cell = ws[f"{col}{i}"]
            if not isinstance(cell, MergedCell):
                value = row_dict.get(col_name, 0)
                if i == start_row:
                    print(f"DEBUG: Writing to {col}{i}: {col_name} = {value}")
                cell.value = value
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def group_consecutive_days(filled_days):
    """
    Group consecutive days into trips.
    """
    filled_sorted = sorted([d for d in filled_days], key=lambda x: x["Data"])
    trips = []
    if filled_sorted:
        for d in filled_sorted:
            d["_date_obj"] = datetime.strptime(d["Data"], "%Y-%m-%d").date()
        trip = [filled_sorted[0]]
        for prev, curr in zip(filled_sorted, filled_sorted[1:]):
            if (curr["_date_obj"] - prev["_date_obj"]).days == 1:
                trip.append(curr)
            else:
                trips.append(trip)
                trip = [curr]
        trips.append(trip)
        for d in filled_sorted:
            del d["_date_obj"]
    return trips


def categorize_trips(trips, max_daily, OBJECTIVES, PARFOIS_ADDRESS):
    """
    Categorize trips into 100%, 75%, 50%, and 25% values.
    """
    filled_days_categorized = []
    trip_id = 0
    for trip in trips:
        n = len(trip)
        for i, d in enumerate(trip):
            value = max_daily
            inicio_dia_hora = ""
            regresso_dia_hora = ""
            objetivo = random.choice(OBJECTIVES)
            local = PARFOIS_ADDRESS
            if n == 1:
                val_100 = value
                val_75 = val_50 = val_25 = ""
                inicio_dia_hora = f"{d['Data']} {TRIP_START_TIME}"
                regresso_dia_hora = f"{d['Data']} {TRIP_END_TIME}"
            else:
                if i == 0:
                    val_100 = value
                    val_75 = val_50 = val_25 = ""
                    inicio_dia_hora = f"{d['Data']} {TRIP_START_TIME}"
                elif i == n - 1:
                    val_100 = val_75 = val_50 = ""
                    val_25 = round(value * 0.25, 2)
                    regresso_dia_hora = f"{d['Data']} {TRIP_END_TIME}"
                else:
                    val_100 = value
                    val_75 = val_50 = val_25 = ""
            filled_days_categorized.append(
                {
                    **d,
                    "Valor 100% (€)": val_100,
                    "Valor 75% (€)": val_75,
                    "Valor 50% (€)": val_50,
                    "Valor 25% (€)": val_25,
                    "inicio (Dia Hora)": inicio_dia_hora,
                    "regresso (Dia Hora)": regresso_dia_hora,
                    "Mapa deslocação / Objectivo": objetivo,
                    "Local onde foram prestados": local,
                    "_trip_id": trip_id,
                }
            )
        trip_id += 1
    return filled_days_categorized
