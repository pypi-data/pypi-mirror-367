"""
Copyright © 2025 Omnissa, LLC.
"""

"""
Recommendation engine for generating recommendations for advisor reports.
"""


def rule_1_optimize_spare_policy_provisioning_approach(org, resource_id, resource_type, template_info):
    """
    Rule 1: Recommend optimizing spare policy (on demand vs all at once).
    """
    if resource_type.lower() == "pool":
        template = template_info.get("template", {})
        spare_policy = template.get("sparePolicy", {})
        limit = spare_policy.get("limit")
        min_spare = spare_policy.get("min")
        max_spare = spare_policy.get("max")
        estimated_savings = "XXX"  # Placeholder, replace with real calculation if possible
        utilization_rate = "XXX"  # Placeholder, replace with real calculation if possible
        # All at once: limit == min == max and all are not None
        if limit is not None and min_spare is not None and max_spare is not None:
            if limit == min_spare == max_spare:
                return {
                    "action": "Pool - Optimize Spare Policy - Reevaluate the approach of provisioning VMs 'on demand' rather than 'all at once'",
                    "justification": (
                        f"The pool usage indicates the allocated VMs are underutilized with utilization rate of {utilization_rate}. Currently, all VMs ({limit}) are provisioned at once. "
                        "Consider switching to an 'on demand' provisioning model, "
                        "where only the required number of VMs are kept as spare. "
                        f"This can help improve resource usage and reduce costs, potentially saving around {estimated_savings}."
                    ),
                    "current_settings": {"sparePolicy": {"limit": limit, "min": min_spare, "max": max_spare}},
                    "recommended_settings": {
                        "sparePolicy": {
                            "limit": limit,
                            "min": min_spare,
                            "max": max_spare,
                            "note": "Values should be adjusted so that limit > max >= min",
                        }
                    },
                }
    return None


def rule_2_optimize_spare_policy_values(org, resource_id, resource_type, template_info):
    """
    Rule 2: Optimize Spare Policy Values - Reduce the number of spare VMs.
    """
    if resource_type.lower() == "pool":
        template = template_info.get("template", {})
        spare_policy = template.get("sparePolicy", {})
        min_spare = spare_policy.get("min")
        max_spare = spare_policy.get("max")
        max_vms = spare_policy.get("limit")
        utilization_rate = "XXX"  # Placeholder, replace with real calculation if possible
        estimated_savings = "XXX"  # Placeholder, replace with real calculation if possible

        if min_spare is not None and max_spare is not None and max_vms is not None:
            return {
                "action": "Pool - Optimize Spare Policy - Reduce the Spare Policy Values",
                "justification": (
                    f"The pool usage indicates the allocated VMs are underutilized with {utilization_rate}. "
                    "Consider changing pool spare policy settings Minimum spare VMs, Maximum spare VMs, "
                    "and Maximum VMs to smaller values. This can help improve resource usage and reduce costs, "
                    f"potentially saving around {estimated_savings}"
                ),
                "current_settings": {"sparePolicy": {"limit": max_vms, "min": min_spare, "max": max_spare}},
                "recommended_settings": {
                    "sparePolicy": {
                        "limit": "Smaller value based on actual usage",
                        "min": "Smaller value based on actual usage",
                        "max": "Smaller value based on actual usage",
                    }
                },
            }
    return None


def rule_3_reevaluate_power_policy_schedule(org, resource_id, resource_type, template_info):
    """
    Rule 3: Reevaluate Power Policy Schedule for the dedicated desktop pool.
    """
    if resource_type.lower() == "pool":
        template = template_info.get("template", {})
        if template.get("templateType") != "DEDICATED":
            return None
        power_policy = template.get("powerPolicy", {})
        power_schedules = power_policy.get("powerSchedules")
        if power_schedules and isinstance(power_schedules, list) and len(power_schedules) > 0:
            pool_id = resource_id
            estimated_savings = "XXX"  # Placeholder, replace with real calculation if possible
            return {
                "action": "Pool Group(Dedicaed) - Reevaluate Power Policy - Power management schedule setting",
                "justification": (
                    f"If you set any schedule here on a Dedicated Assignment, all assigned or claimed desktops "
                    f"will be powered on during the schedule period. This is to make sure that all Dedicated desktops "
                    f"are ready to use for mapped-to users during the specified period. As a result, if all desktops "
                    f"in a Dedicated Assignment are assigned/claimed, all desktops will be powered on, even if the "
                    f"schedule is set to power on zero (0) desktops, since that value only applies to unassigned/"
                    f"unclaimed virtual desktops. Refer to Power Management for Dedicated Pool Groups for details.\n"
                    f"Is the power schedule for the dedicated pool {pool_id} still necessary? If it is no longer needed, "
                    f"please consider removing the Power management schedule. This action could help reduce costs, "
                    f"potentially saving around {estimated_savings}."
                ),
                "current_settings": {"powerPolicy": {"powerSchedules": power_schedules}},
                "recommended_settings": {"powerPolicy": {"powerSchedules": []}},
            }
    return None


def rule_4_optimize_power_policy_unused_vms(org, resource_id, resource_type, template_info):
    """
    Rule 4: Optimize Power Policy - Reduce Unused VMs values in Dedicated pool group.
    """
    if resource_type.lower() == "pool":
        template = template_info.get("template", {})
        if template.get("templateType") != "DEDICATED":
            return None

        power_policy = template.get("powerPolicy", {})
        unused_vms = power_policy.get("min")  # example value: 100
        example_unused_vms = "5"  # Example value, could be calculated based on usage patterns
        estimated_savings = "XXX"  # Placeholder, replace with real calculation if possible

        unused_vms_threshold = 50
        if unused_vms is not None and unused_vms > unused_vms_threshold:
            return {
                "action": "Pool Group(Dedicated) - Optimize Power Policy - Reduce Unused VMs values",
                "justification": (
                    "Unused VMs in Dedicated pool group's power policy: The number of unused VMs to be kept powered on "
                    "relative to the total number of unassigned VMs. An unused VM is a VM which is provisioned and "
                    "powered on but not assigned to a user. This setting applies to each pool in the pool group.\n"
                    f"The current value of unused VMs stands at {unused_vms}, indicating a significant number of "
                    f"powered-on virtual machines that are not being utilized. It is advisable to lower this number, "
                    f"e.g. {example_unused_vms}, to enhance efficiency. By reducing the unused VMs, you can decrease "
                    f"the VM's idle time, which may lead to estimated savings of approximately {estimated_savings}."
                ),
                "current_settings": {"powerPolicy": {"min": unused_vms}},
                "recommended_settings": {"powerPolicy": {"min": example_unused_vms}},
            }
    return None


def rule_5_enable_auto_scale_disk_type(org, resource_id, resource_type, template_info):
    """
    Rule 5: Enable Auto Scale Disk Type for cost optimization.
    """
    if resource_type.lower() == "pool":
        template = template_info.get("template", {})

        # example payload: template["infrastructure"]["diskSkus"][0]["data"]["diskSkuAutoScaleEnabled"] = false
        auto_scale_disk_type = (
            template.get("infrastructure", {}).get("diskSkus", [{}])[0].get("data", {}).get("diskSkuAutoScaleEnabled", False)
        )
        # if auto_scale_disk_type is false, then return the recommendation.
        if not auto_scale_disk_type:
            return {
                "action": "Pool - Enable Auto Scale Disk Type",
                "justification": (
                    "The auto-scale logic can automatically change the OS disk type of VMs in all Azure pools to a "
                    "cheaper storage tier (from premium SSD to standard HDD), while the host VM is powered off, and "
                    "back to the higher performance tier immediately before it is started.\n"
                    "With the Auto Scale toggle enabled, an administrator can select both the running and stopped disk "
                    "type. When the VMs are powered off, the disk types are set and auto-converted. Once powered back "
                    "on, the disk type returns to its original settings. This configuration can significantly reduce "
                    "the customer's disk expenses.\n\n"
                    "Note: The Auto Scale toggle can be activated in two places. It can be toggled in the Create a Pool "
                    "page and/or on the global Settings > Pool Settings page available from the left pane Horizon "
                    "Universal Console UI. To set a global policy, use the global Settings > Pool Settings page. "
                    "However, if only specific desktop pools need this feature, use the option on the Create a Pool "
                    "page to activate or deactivate the option when creating a pool. The toggle specified on the "
                    "Create a Pool page takes precedence over the Settings > Pool Settings page."
                ),
                "current_settings": {"infrastructure": {"diskSkus": [{"data": {"diskSkuAutoScaleEnabled": False}}]}},
                "recommended_settings": {
                    "infrastructure": {"diskSkus": [{"data": {"diskSkuAutoScaleEnabled": True, "diskSkuOnPowerOff": "Standard_LRS"}}]}
                },
            }
    return None


def generate_recommendations(org, resource_id, resource_type, template_info):
    """
    Generate recommendations by applying all rule functions.
    """
    rules = [
        rule_1_optimize_spare_policy_provisioning_approach,
        rule_2_optimize_spare_policy_values,
        rule_3_reevaluate_power_policy_schedule,
        rule_4_optimize_power_policy_unused_vms,
        rule_5_enable_auto_scale_disk_type,
    ]
    recommendations = []
    for rule_func in rules:
        rec = rule_func(org, resource_id, resource_type, template_info)
        if rec:
            recommendations.append(rec)
    if not recommendations:
        recommendations = [
            {
                "action": "No recommendations available.",
                "justification": "",
                "current_settings": {},
                "recommended_settings": {},
            }
        ]
    return {"recommendations": recommendations}
