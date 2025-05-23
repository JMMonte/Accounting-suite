# util.py
"""
This file contains the utility functions for the app.

Functions:
- random_fill_days: Fill business days based on max_total constraint,
working with the Excel template's percentage-based calculation system.
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


def _simulate_excel_calculation(filled_days, max_daily):
    """
    Simulate the Excel calculation to estimate the total.
    """
    if not filled_days:
        return 0

    # Group into trips to simulate categorize_trips behavior
    filled_sorted = sorted(filled_days, key=lambda x: x["Data"])

    # Add date objects for grouping
    for d in filled_sorted:
        d["_date_obj"] = datetime.strptime(d["Data"], "%Y-%m-%d").date()

    # Group consecutive days
    trips = []
    if filled_sorted:
        trip = [filled_sorted[0]]
        for prev, curr in zip(filled_sorted, filled_sorted[1:]):
            if (curr["_date_obj"] - prev["_date_obj"]).days == 1:
                trip.append(curr)
            else:
                trips.append(trip)
                trip = [curr]
        trips.append(trip)

    # Count percentages as Excel would
    count_100 = count_75 = count_50 = count_25 = 0

    for trip in trips:
        n = len(trip)
        for i, d in enumerate(trip):
            if n == 1:
                count_100 += 1
            else:
                if i == 0:
                    count_100 += 1
                elif i == n - 1:
                    count_25 += 1
                else:
                    count_100 += 1

    # Clean up temporary date objects
    for d in filled_sorted:
        if "_date_obj" in d:
            del d["_date_obj"]

    # Calculate total as Excel does
    total = (
        (count_100 * max_daily * 1.0)
        + (count_75 * max_daily * 0.75)
        + (count_50 * max_daily * 0.50)
        + (count_25 * max_daily * 0.25)
    )
    return round(total, 2)


def random_fill_days(business_days, max_daily, max_total):
    """
    Fill business days based on max_total constraint.
    Returns days to be filled (without specific values) since Excel template will calculate based on percentages.
    """
    days = business_days.copy()
    random.shuffle(days)

    # Start with estimated number of days
    estimated_avg_percentage = 0.80
    max_days_possible = int(max_total / (max_daily * estimated_avg_percentage))
    max_days_possible = min(max_days_possible, len(days))

    # Try different numbers of days to find the best fit
    best_num_days = max_days_possible
    best_total = 0

    # Test a range around our estimate
    min_test = max(1, max_days_possible - 3)
    max_test = min(len(days), max_days_possible + 5)

    for test_days in range(min_test, max_test + 1):
        test_days_to_fill = days[:test_days]
        test_filled_list = []
        for d in sorted(test_days_to_fill):
            test_filled_list.append(
                {
                    "Dia": d.day,
                    "Data": d.strftime("%Y-%m-%d"),
                    "Dia da Semana": d.strftime("%A"),
                    "Valor (€)": max_daily,
                }
            )

        simulated_total = _simulate_excel_calculation(test_filled_list, max_daily)

        # Find the configuration that gets closest to max_total without exceeding it
        if simulated_total <= max_total and simulated_total > best_total:
            best_num_days = test_days
            best_total = simulated_total

    # Use the best configuration found
    days_to_fill = days[:best_num_days]

    filled_days_list = []
    for d in sorted(days_to_fill):
        filled_days_list.append(
            {
                "Dia": d.day,
                "Data": d.strftime("%Y-%m-%d"),
                "Dia da Semana": d.strftime("%A"),
                "Valor (€)": max_daily,  # Placeholder value, actual calculation done by Excel template
            }
        )

    # Return the days and the simulated total
    return filled_days_list, best_total


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
        for col, key in mapping:
            value = row_dict.get(key, "")
            cell = ws[f"{col}{i}"]
            if not isinstance(cell, MergedCell):
                cell.value = value
        for col, col_name in zip(["K", "L", "M", "N"], ["100%", "75%", "50%", "25%"]):
            cell = ws[f"{col}{i}"]
            if not isinstance(cell, MergedCell):
                value = row_dict.get(col_name, 0)
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


def categorize_trips(trips, OBJECTIVES, CLIENT_ADDRESS):
    """
    Categorizes trips and assigns percentage values based on trip duration.
    Consecutive business days are treated as a single trip.

    Args:
        trips: List of trips, where each trip is a list of consecutive filled days
        OBJECTIVES: List of possible objectives for the trips
        CLIENT_ADDRESS: The client's address to use for trip locations

    Returns:
        List of all individual days with categorization applied
    """
    all_categorized_days = []
    trip_id = 0

    for trip in trips:
        trip_length = len(trip)

        # Apply the same objective to all days in the trip
        objetivo = random.choice(OBJECTIVES)
        local = CLIENT_ADDRESS

        for i, day in enumerate(trip):
            # Reset all percentage columns
            day["Valor 100% (€)"] = ""
            day["Valor 75% (€)"] = ""
            day["Valor 50% (€)"] = ""
            day["Valor 25% (€)"] = ""

            # Determine the percentage based on trip length and position
            if trip_length == 1:
                # Single day trip gets 100%
                day["Valor 100% (€)"] = 1
                inicio_dia_hora = f"{day['Data']} {TRIP_START_TIME}"
                regresso_dia_hora = f"{day['Data']} {TRIP_END_TIME}"
            else:
                if i == 0:
                    # First day of multi-day trip gets 100%
                    day["Valor 100% (€)"] = 1
                    inicio_dia_hora = f"{day['Data']} {TRIP_START_TIME}"
                    regresso_dia_hora = f"{day['Data']} {TRIP_END_TIME}"
                elif i == trip_length - 1:
                    # Last day of multi-day trip gets 25%
                    day["Valor 25% (€)"] = 1
                    inicio_dia_hora = f"{day['Data']} {TRIP_START_TIME}"
                    regresso_dia_hora = f"{day['Data']} {TRIP_END_TIME}"
                else:
                    # Middle days of multi-day trip get 100%
                    day["Valor 100% (€)"] = 1
                    inicio_dia_hora = f"{day['Data']} {TRIP_START_TIME}"
                    regresso_dia_hora = f"{day['Data']} {TRIP_END_TIME}"

            # Add the additional required fields
            day.update(
                {
                    "inicio (Dia Hora)": inicio_dia_hora,
                    "regresso (Dia Hora)": regresso_dia_hora,
                    "Mapa deslocação / Objectivo": objetivo,
                    "Local onde foram prestados": local,
                    "_trip_id": trip_id,
                }
            )

        all_categorized_days.extend(trip)
        trip_id += 1

    return all_categorized_days
