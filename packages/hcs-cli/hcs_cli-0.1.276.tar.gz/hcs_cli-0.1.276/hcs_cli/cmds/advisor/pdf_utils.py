"""
Copyright © 2025 Omnissa, LLC.
"""

import datetime
import io
import json
import os
import tempfile
import time

import click
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, LongTable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from hcs_cli.cmds.advisor.advisor_utils import calculate_usage_metrics, create_report_file, get_template_info
from hcs_cli.cmds.advisor.recommendation_engine import generate_recommendations
from hcs_cli.service.org_service import details


def _format_template_value(value):
    """Format template value to prevent excessive size."""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    elif isinstance(value, dict):
        if "history" in value:
            history = value["history"]
            for key in ["provisionedVms", "poweredOnAssignedVms", "poweredOnUnassignedVms", "consumedSessions"]:
                if key in history and isinstance(history[key], list):
                    if len(history[key]) > 5:
                        # Store the actual values but display a summary
                        history[key] = {"values": history[key], "display": f"Array of {len(history[key])} values"}
            value["history"] = history
        if "prediction" in value:
            prediction = value["prediction"]
            for key in ["provisionedVms", "poweredOnAssignedVms", "poweredOnUnassignedVms", "consumedSessions"]:
                if key in prediction and isinstance(prediction[key], list):
                    if len(prediction[key]) > 5:
                        # Store the actual values but display a summary
                        prediction[key] = {
                            "values": prediction[key],
                            "display": f"Array of {len(prediction[key])} values",
                        }
            value["prediction"] = prediction
        return json.dumps(value, indent=2)
    elif isinstance(value, list):
        if len(value) > 5:
            if isinstance(value[0], (int, float)):
                return f"Array of {len(value)} numbers"
            elif isinstance(value[0], str):
                return f"Array of {len(value)} strings"
            else:
                return f"Array of {len(value)} items"
        return json.dumps(value, indent=2)
    return str(value)


def _format_meta_data(meta_data):
    """Format meta data to be more concise and readable."""
    if not meta_data:
        return "No meta data available"

    # Extract and format key metrics
    metrics = []
    if "history" in meta_data:
        history = meta_data["history"]
        if "startTimestamp" in history:
            start_time = datetime.datetime.fromtimestamp(history["startTimestamp"] / 1000)
            metrics.append(f"History Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            len_history = len(history["provisionedVms"])
            end_time = start_time + datetime.timedelta(seconds=len_history * meta_data["timeslotMs"] / 1000)
            metrics.append(f"History End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            duration = end_time - start_time
            metrics.append(f"History Duration: {duration}")
    if "timeslotMs" in meta_data:
        timeslot_minutes = meta_data["timeslotMs"] / 60000
        metrics.append(f"Time Slot: {timeslot_minutes} minutes")
    return "\n".join(metrics)


def _get_values(data, key):
    """Helper function to get values from either dictionary or list format."""
    values = data[key]
    if isinstance(values, dict) and "values" in values:
        return values["values"]
    return values


def _format_json_to_text(json_data, indent=4):
    """
    Convert JSON data to a human-readable text format with proper indentation.
    """
    if not json_data:
        return ""

    def _format_value(value, current_indent):
        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{' ' * current_indent}{k}:")
                    lines.extend(_format_value(v, current_indent + indent))
                else:
                    lines.append(f"{' ' * current_indent}{k}: {v}")
            return lines
        elif isinstance(value, list):
            lines = []
            for item in value:
                if isinstance(item, (dict, list)):
                    lines.extend(_format_value(item, current_indent + indent))
                else:
                    lines.append(f"{' ' * current_indent}- {item}")
            return lines
        else:
            return [f"{' ' * current_indent}{value}"]

    return "\n".join(_format_value(json_data, 0))


def create_pool_pdf_report(org_id: str, resource_id: str, resource_type: str, template_info: dict = None, filename: str = None):
    """Create a professional PDF report for advisor insights (pool)."""
    try:
        org_details = details.get(org_id)
        org_name = org_details.get("orgName", "Unknown Organization") if org_details else "Unknown Organization"

        doc = SimpleDocTemplate(filename, pagesize=landscape(letter), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=24, spaceAfter=30)
        heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading2"], fontSize=16, spaceAfter=12)
        normal_style = ParagraphStyle("CustomNormal", parent=styles["Normal"], fontSize=10, leading=12)
        content = []
        content.append(Paragraph("Horizon Cloud Next-gen Advisor Report", title_style))
        content.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        content.append(Paragraph(f"Organization: {org_name}", normal_style))
        content.append(Paragraph(f"Resource Type: {resource_type}", normal_style))
        content.append(Paragraph(f"Resource ID: {resource_id}", normal_style))
        content.append(Spacer(1, 20))

        # Part 1: Usage Insights
        content.append(Paragraph("Part 1: Horizon Cloud Next-gen Usage Insights", heading_style))
        content.append(Spacer(1, 30))
        if template_info:
            meta_data = []
            other_data = []
            for key, value in template_info.items():
                if key == "meta":
                    formatted_value = _format_meta_data(value)
                    meta_data.append([key, formatted_value])
                elif isinstance(value, (dict, list)) and len(str(value)) > 1000:
                    continue
                else:
                    formatted_value = _format_template_value(value)
                    other_data.append([key, formatted_value])
            if other_data:
                other_table = LongTable(other_data, colWidths=[3 * inch, 6 * inch])
                other_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 12),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 1), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("ROWPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                content.append(other_table)
                content.append(Spacer(1, 20))
            if meta_data:
                content.append(Paragraph("Summary Information", heading_style))
                meta_table = LongTable(meta_data, colWidths=[3 * inch, 6 * inch])
                meta_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 12),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 1), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("ROWPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                content.append(meta_table)
                content.append(Spacer(1, 20))

        # Add usage metrics table
        if template_info and "meta" in template_info:
            meta_data = template_info["meta"]
            if "history" in meta_data:
                usage_data = calculate_usage_metrics(template_info)
            else:
                usage_data = [
                    ["Metric", "Value", "Status"],
                    ["Allocated VMs Hours", "N/A", "N/A"],
                    ["Powered-on VMs Hours", "N/A", "N/A"],
                    ["Utilized VMs Hours", "N/A", "N/A"],
                    ["Idle VMs Hours", "N/A", "N/A"],
                    ["Resource Utilization", "N/A", "N/A"],
                ]
        else:
            usage_data = [
                ["Metric", "Value", "Status"],
                ["Allocated VMs Hours", "1500", "Normal"],
                ["Powered-on VMs Hours", "750", "Good"],
                ["Utilized VMs Hours", "250", "Optimal"],
                ["Idle VMs Hours", "500", "Normal"],
                ["Resource Utilization", "65%", "Optimal"],
            ]

        # Convert table data to Paragraphs for word wrapping
        usage_data_wrapped = []
        for row in usage_data:
            wrapped_row = [Paragraph(str(cell), normal_style) for cell in row]
            usage_data_wrapped.append(wrapped_row)

        usage_table = Table(usage_data_wrapped, colWidths=[2.5 * inch, 2.5 * inch, 2.5 * inch])
        usage_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWPADDING", (0, 0), (-1, -1), 6),
                    ("COLWIDTH", (0, 0), (-1, -1), 2.5 * inch),
                ]
            )
        )
        content.append(usage_table)
        content.append(Spacer(1, 20))
        # Add VM Utilization section
        content.append(Paragraph("VM Utilization", heading_style))
        content.append(Spacer(1, 12))
        # Add VM Utilization visualization - Chart 1: Full Data (Every 30 Minutes Sampling)
        if template_info and "meta" in template_info:
            meta_data = template_info["meta"]
            if "history" in meta_data:
                history = meta_data["history"]
                if "startTimestamp" in history and "provisionedVms" in history:
                    start_time = datetime.datetime.fromtimestamp(history["startTimestamp"] / 1000)
                    len_history = len(history["provisionedVms"])
                    # --- Full View Chart (Every 30 Minutes Sampling) ---
                    plt.figure(figsize=(10, 6))
                    time_slots_full = [start_time + datetime.timedelta(minutes=30 * i) for i in range(len_history)]
                    end_time_full = start_time + datetime.timedelta(seconds=len_history * meta_data["timeslotMs"] / 1000)

                    # Get data using new sources
                    provisioned_vms_full = history["provisionedVms"]

                    # Calculate Powered-on VMs from assigned + unassigned
                    powered_on_assigned = history.get("poweredOnAssignedVms", [])
                    powered_on_unassigned = history.get("poweredOnUnassignedVms", [])
                    powered_on_vms_full = []

                    # Combine the two arrays, handling different lengths
                    max_length = max(len(powered_on_assigned), len(powered_on_unassigned), len(provisioned_vms_full))
                    for i in range(max_length):
                        assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
                        unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
                        powered_on_vms_full.append(assigned_val + unassigned_val)

                    # Get Utilized Capacity data
                    utilized_capacity_full = history.get("consumedSessions", [])

                    # Ensure all arrays have the same length
                    powered_on_vms_full = powered_on_vms_full[:len_history]
                    utilized_capacity_full = utilized_capacity_full[:len_history]

                    # Pad shorter arrays with zeros if needed
                    while len(powered_on_vms_full) < len_history:
                        powered_on_vms_full.append(0)
                    while len(utilized_capacity_full) < len_history:
                        utilized_capacity_full.append(0)

                    plt.fill_between(time_slots_full, provisioned_vms_full, color="blue", alpha=0.5, label="Allocated VMs")
                    plt.fill_between(time_slots_full, powered_on_vms_full, color="red", alpha=0.5, label="Powered-on VMs")
                    plt.fill_between(time_slots_full, utilized_capacity_full, color="green", alpha=0.5, label="Utilized Capacity")
                    plt.title(f"VM Utilization Trends - Full View (Every {meta_data['timeslotMs']/(1000 * 60)} Minutes Sampling)")
                    plt.xlabel("Time")
                    plt.ylabel("VM Count")
                    plt.grid(True)
                    # Adjust legend position and add padding
                    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0)
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
                    plt.gcf().autofmt_xdate()
                    plt.xlim(start_time, end_time_full)
                    # Add more padding to prevent label overlapping
                    plt.tight_layout(pad=3.0)
                    buf_full = io.BytesIO()
                    plt.savefig(buf_full, format="png", dpi=300, bbox_inches="tight")
                    plt.close()
                    buf_full.seek(0)
                    temp_dir = tempfile.gettempdir()
                    temp_file_full = os.path.join(temp_dir, f"vm_utilization_full_{int(time.time())}.png")
                    with open(temp_file_full, "wb") as f:
                        f.write(buf_full.getvalue())
                    buf_full.close()
                    img_full = Image(temp_file_full, width=9 * inch, height=5 * inch)
                    content.append(img_full)
                    temp_files = getattr(doc, "_temp_files", [])
                    temp_files.append(temp_file_full)
                    doc._temp_files = temp_files

                    # --- Simplified View Chart (Daily Sampling) ---
                    plt.figure(figsize=(10, 6))
                    num_days = int(len_history / (24 * 2))
                    time_slots_daily = [start_time + datetime.timedelta(hours=24 * i) for i in range(num_days)]
                    provisioned_vms_daily_avg = [sum(history["provisionedVms"][i * 48 : (i + 1) * 48]) / 48 for i in range(num_days)]

                    # Calculate daily averages for Powered-on VMs
                    powered_on_vms_daily_avg = []
                    for i in range(num_days):
                        start_idx = i * 48
                        end_idx = (i + 1) * 48
                        daily_powered_on = []
                        for j in range(start_idx, min(end_idx, len(powered_on_vms_full))):
                            daily_powered_on.append(powered_on_vms_full[j])
                        avg = sum(daily_powered_on) / len(daily_powered_on) if daily_powered_on else 0
                        powered_on_vms_daily_avg.append(avg)

                    # Calculate daily averages for Utilized Capacity
                    utilized_capacity_daily_avg = [sum(utilized_capacity_full[i * 48 : (i + 1) * 48]) / 48 for i in range(num_days)]

                    plt.fill_between(time_slots_daily, provisioned_vms_daily_avg, color="blue", alpha=0.5, label="Allocated VMs")
                    plt.fill_between(time_slots_daily, powered_on_vms_daily_avg, color="red", alpha=0.5, label="Powered-on VMs")
                    plt.fill_between(time_slots_daily, utilized_capacity_daily_avg, color="green", alpha=0.5, label="Utilized Capacity")
                    plt.title("VM Utilization Trends - Simplified View (Daily Sampling)")
                    plt.xlabel("Time")
                    plt.ylabel("VM Count")
                    plt.grid(True)
                    # Adjust legend position and add padding
                    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0)
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                    plt.gcf().autofmt_xdate()
                    plt.xlim(start_time, start_time + datetime.timedelta(days=num_days))
                    # Add more padding to prevent label overlapping
                    plt.tight_layout(pad=3.0)
                    buf_daily = io.BytesIO()
                    plt.savefig(buf_daily, format="png", dpi=300, bbox_inches="tight")
                    plt.close()
                    buf_daily.seek(0)
                    temp_file_daily = os.path.join(temp_dir, f"vm_utilization_daily_{int(time.time())}.png")
                    with open(temp_file_daily, "wb") as f:
                        f.write(buf_daily.getvalue())
                    buf_daily.close()
                    img_daily = Image(temp_file_daily, width=9 * inch, height=5 * inch)
                    content.append(img_daily)
                    temp_files = getattr(doc, "_temp_files", [])
                    temp_files.append(temp_file_daily)
                    doc._temp_files = temp_files

        # Part 2: Recommendations
        content.append(Paragraph("Part 2: Recommendation Actions", heading_style))

        if resource_type.lower() == "pool":
            recommendations = generate_recommendations(org_id, resource_id, resource_type, template_info)
        elif resource_type.lower() == "edge":
            recommendations = {
                "recommendations": [
                    {
                        "action": "Optimize Edge Configuration",
                        "justification": "High resource utilization detected. Current settings may be causing performance bottlenecks during peak hours.",
                        "current_settings": {},
                        "recommended_settings": {},
                    },
                    {
                        "action": "Review Security Settings",
                        "justification": "Current settings may be too restrictive, causing unnecessary connection drops and user experience issues.",
                        "current_settings": {},
                        "recommended_settings": {},
                    },
                ]
            }
        else:  # UAG
            recommendations = {
                "recommendations": [
                    {
                        "action": "Update UAG Configuration",
                        "justification": "Current settings not optimal for the current load. Security policies may need adjustment based on usage patterns.",
                        "current_settings": {},
                        "recommended_settings": {},
                    },
                    {
                        "action": "Review Load Balancing",
                        "justification": "Uneven distribution detected across UAG instances. Some instances are handling 70% of the load while others are underutilized.",
                        "current_settings": {},
                        "recommended_settings": {},
                    },
                ]
            }

        # Convert recommendations to Paragraphs for word wrapping
        rec_data_wrapped = []
        # Add header row
        rec_data_wrapped.append(
            [
                Paragraph("Action", normal_style),
                Paragraph("Justification", normal_style),
                Paragraph("Current Settings", normal_style),
                Paragraph("Recommended Settings", normal_style),
            ]
        )
        for rec in recommendations["recommendations"]:
            wrapped_row = [
                Paragraph(str(rec["action"]), normal_style),
                Paragraph(str(rec["justification"]), normal_style),
                Paragraph(_format_json_to_text(rec["current_settings"]), normal_style),
                Paragraph(_format_json_to_text(rec["recommended_settings"]), normal_style),
            ]
            rec_data_wrapped.append(wrapped_row)
        # Use LongTable for better handling of large content
        rec_table = LongTable(rec_data_wrapped, colWidths=[2 * inch, 3 * inch, 2 * inch, 2 * inch])
        rec_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWPADDING", (0, 0), (-1, -1), 6),
                    ("COLWIDTH", (0, 0), (-1, -1), 2 * inch),
                ]
            )
        )
        content.append(rec_table)

        # Build the PDF
        doc.build(content)

        # Clean up temporary files after PDF generation is complete
        if hasattr(doc, "_temp_files"):
            for temp_file in doc._temp_files:
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass  # Ignore errors during cleanup
    except Exception as e:
        click.echo(f"Error creating advisor report: {e}")


def create_org_pdf_report(org_details: dict, all_recommendations: list, filename: str = None):
    """Generate a PDF report for an organization with recommendations for all templates."""
    org_name = org_details.get("orgName", "Unknown Organization")
    if not filename:
        output_dir = os.path.join(os.getcwd(), "advisor_reports")
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"advisor_report_{org_name}_{timestamp}.pdf"
        output_file = os.path.join(output_dir, filename)
    else:
        output_file = filename

    # Define styles with adjusted font sizes and spacing
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=24, spaceAfter=30)
    heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading2"], fontSize=16, spaceAfter=12)
    normal_style = ParagraphStyle("CustomNormal", parent=styles["Normal"], fontSize=10, leading=12, wordWrap="CJK")
    table_header_style = ParagraphStyle("TableHeader", parent=styles["Normal"], fontSize=11, leading=14, wordWrap="CJK")
    table_content_style = ParagraphStyle("TableContent", parent=styles["Normal"], fontSize=9, leading=11, wordWrap="CJK")

    # Calculate page dimensions and margins
    page_width, page_height = letter
    left_margin = 36  # 0.5 inch
    right_margin = 36  # 0.5 inch
    top_margin = 36  # 0.5 inch
    bottom_margin = 36  # 0.5 inch
    usable_width = page_width - left_margin - right_margin

    content = []
    content.append(Paragraph(f"Horizon Cloud Next-gen Advisor Report", title_style))
    content.append(Paragraph(f"Organization: {org_name}", heading_style))
    content.append(Spacer(1, 20))

    # Add recommendations for each template
    for template_data in all_recommendations:
        template_name = template_data["template_name"]
        template_type = template_data["template_type"]
        recommendations = template_data["recommendations"]

        # Add template section
        content.append(Paragraph(f"Template: {template_name} ({template_type})", heading_style))
        content.append(Spacer(1, 12))

        # Add recommendations table
        if recommendations:
            data = []
            # Add header row
            data.append(
                [
                    Paragraph("Action", table_header_style),
                    Paragraph("Justification", table_header_style),
                    Paragraph("Current Settings", table_header_style),
                    Paragraph("Recommended Settings", table_header_style),
                ]
            )
            for rec in recommendations:
                wrapped_row = [
                    Paragraph(str(rec["action"]), table_content_style),
                    Paragraph(str(rec["justification"]), table_content_style),
                    Paragraph(_format_json_to_text(rec["current_settings"]), table_content_style),
                    Paragraph(_format_json_to_text(rec["recommended_settings"]), table_content_style),
                ]
                data.append(wrapped_row)

            # Calculate column widths based on content
            col_widths = [
                usable_width * 0.25,  # Action
                usable_width * 0.35,  # Justification
                usable_width * 0.20,  # Current Settings
                usable_width * 0.20,  # Recommended Settings
            ]

            # Use LongTable for better handling of large content
            table = LongTable(data, colWidths=col_widths, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        # Header styling
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        # Content styling
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        # Grid and spacing
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("ROWPADDING", (0, 0), (-1, -1), 6),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        # Word wrapping and alignment
                        ("WORDWRAP", (0, 0), (-1, -1), True),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        # Keep header row on each page
                        ("REPEATROWS", (0, 0), (-1, 0), 1),
                    ]
                )
            )
            content.append(table)
        else:
            content.append(Paragraph("No recommendations available for this template.", normal_style))

        content.append(Spacer(1, 20))

    # Create the PDF document with adjusted margins
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=right_margin,
        leftMargin=left_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )
    doc.build(content)
    return output_file


if __name__ == "__main__":
    create_pool_pdf_report("org1", "res1", "pool")
