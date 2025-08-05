"""
Copyright © 2025 Omnissa, LLC.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import click

import hcs_cli.service as hcs


def get_template_info(template_id: str, org_id: str) -> dict:
    """Get template information using hcs scm template command."""
    try:
        usage = hcs.scm.template_usage(org_id, template_id)
        if not usage:
            click.echo(f"Warning: No usage data available for template (ID: {template_id})")
            usage = {}
        template = hcs.template.get(org_id=org_id, id=template_id)
        if not template:
            click.echo("Warning: Could not fetch template details")
            template = {}
        return {"meta": usage, "template": template}
    except Exception as e:
        click.echo(f"Warning: Could not fetch template information: {str(e)}")
        return {}


def create_report_file(prefix: str, id: str, extension: str = "pdf") -> str:
    """Create a report file path in the hcs-reports directory.

    Args:
        prefix: Prefix for the report file (e.g., 'pool_advisor', 'org_advisor')
        id: Identifier for the report (e.g., pool_id, org_id)
        extension: File extension (e.g., 'pdf', 'html')

    Returns:
        str: Full path to the report file
    """
    reports_dir = os.path.expanduser("~/hcs-reports")
    os.makedirs(reports_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(reports_dir, f"{prefix}_{id}_{timestamp}.{extension}")


def calculate_duration_from_history(history_values: List[int], timeslot_ms: int) -> float:
    """
    Calculate total history duration hours from a list of history values and timeslot in milliseconds.

    Args:
        history_values: List of values from history
        timeslot_ms: Time interval between values in milliseconds

    Returns:
        float: Total hours calculated from the values
    """
    if not history_values or not timeslot_ms:
        return 0.0

    # Convert timeslot from milliseconds to hours
    timeslot_hours = timeslot_ms / (1000 * 60 * 60)

    # Calculate total hours
    total_hours = sum(history_values) * timeslot_hours
    return round(total_hours, 2)


def calculate_usage_metrics(template_info: dict) -> List[List[str]]:
    """
    Calculate usage metrics from template_info data.

    Args:
        template_info: Dictionary containing template information and usage data

    Returns:
        List[List[str]]: List of [metric, value, status] for usage data table
    """
    if not template_info or "meta" not in template_info:
        return [
            ["Metric", "Value", "Status"],
            ["Allocated VMs Hours", "N/A", "Unknown"],
            ["Powered-on VMs Hours", "N/A", "Unknown"],
            ["Utilized Capacity Hours", "N/A", "Unknown"],
            ["Idle Capacity Hours", "N/A", "Unknown"],
            ["Resource Utilization", "N/A", "Unknown"],
        ]

    meta_data = template_info["meta"]
    history = meta_data.get("history", {})
    timeslot_ms = meta_data.get("timeslotMs", 0)

    # Calculate metrics using new data sources
    allocated_hours = calculate_duration_from_history(history.get("provisionedVms", []), timeslot_ms)

    # Calculate Powered-on VMs from assigned + unassigned
    powered_on_assigned = history.get("poweredOnAssignedVms", [])
    powered_on_unassigned = history.get("poweredOnUnassignedVms", [])
    powered_on_vms = []

    # Combine the two arrays, handling different lengths
    max_length = max(len(powered_on_assigned), len(powered_on_unassigned))
    for i in range(max_length):
        assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
        unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
        powered_on_vms.append(assigned_val + unassigned_val)

    powered_on_hours = calculate_duration_from_history(powered_on_vms, timeslot_ms)

    # Calculate Utilized Capacity
    utilized_hours = calculate_duration_from_history(history.get("consumedSessions", []), timeslot_ms)

    # Calculate Idle Capacity as Powered-on VMs - Utilized Capacity
    idle_hours = powered_on_hours - utilized_hours
    if idle_hours < 0:
        idle_hours = 0  # Ensure non-negative values

    # Calculate resource utilization
    utilization = 0.0
    if allocated_hours > 0:
        utilization = (utilized_hours / allocated_hours) * 100

    # Determine status based on metrics
    def determine_status(metric: str, value: float, allocated: float) -> str:
        if metric == "Resource Utilization":
            if value >= 80:
                return "Optimal"
            elif value >= 60:
                return "Good"
            else:
                return "Normal"
        elif metric in ["Idle Capacity Hours"]:
            if allocated > 0 and (value / allocated) < 0.1:  # Less than 10%
                return "Good"
            elif allocated > 0 and (value / allocated) < 0.3:  # Less than 30%
                return "Normal"
            else:
                return "Warning"
        else:
            return "Normal"

    # Format the metrics for display
    metrics = [
        ["Metric", "Value", "Status"],
        [
            "Allocated VMs Hours",
            f"{allocated_hours:,.0f}",
            determine_status("Allocated VMs Hours", allocated_hours, allocated_hours),
        ],
        [
            "Powered-on VMs Hours",
            f"{powered_on_hours:,.0f}",
            determine_status("Powered-on VMs Hours", powered_on_hours, allocated_hours),
        ],
        [
            "Utilized Capacity Hours",
            f"{utilized_hours:,.0f}",
            determine_status("Utilized Capacity Hours", utilized_hours, allocated_hours),
        ],
        ["Idle Capacity Hours", f"{idle_hours:,.0f}", determine_status("Idle Capacity Hours", idle_hours, allocated_hours)],
        [
            "Resource Utilization",
            f"{utilization:.1f}%",
            determine_status("Resource Utilization", utilization, allocated_hours),
        ],
    ]

    return metrics


def prompt_for_report_options() -> tuple[bool, bool]:
    """Prompt user to select report generation options when none are specified.

    Returns:
        tuple[bool, bool]: (generate_pdf, generate_html)
    """
    click.echo("No report type specified. Please choose:")
    click.echo("1. Generate PDF report")
    click.echo("2. Generate HTML report")
    click.echo("3. Generate both PDF and HTML reports")
    click.echo("4. No reports (exit)")

    while True:
        choice = click.prompt("Enter your choice (1-4)", type=int)
        if choice == 1:
            return True, False
        elif choice == 2:
            return False, True
        elif choice == 3:
            return True, True
        elif choice == 4:
            return False, False
        else:
            click.echo("Invalid choice. Please enter 1, 2, 3, or 4.")
