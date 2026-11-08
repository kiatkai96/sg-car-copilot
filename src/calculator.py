"""A plain calculator for the true cost of owning a car.

Why not let the AI do the maths? AI models are good with words but can slip on
arithmetic. Normal Python code never makes a sum mistake.

NOTE: This file contains NO Singapore rules on purpose. You type in the numbers
(from your documents or a dealer quote), and it just adds them up correctly.
"""


def total_cost_of_ownership(
    purchase_price,        # what you pay upfront for the car (including COE & taxes)
    years_owned,           # how many years you keep it
    resale_value,          # what you expect to sell it for at the end (0 if scrapped)
    annual_road_tax=0.0,
    annual_insurance=0.0,
    annual_fuel=0.0,
    annual_parking=0.0,
    annual_maintenance=0.0,
    other_annual=0.0,
):
    if years_owned <= 0:
        raise ValueError("years_owned must be more than 0")

    depreciation = purchase_price - resale_value
    yearly_running = (
        annual_road_tax + annual_insurance + annual_fuel
        + annual_parking + annual_maintenance + other_annual
    )
    running_total = yearly_running * years_owned
    total = depreciation + running_total
    months = years_owned * 12

    return {
        "depreciation_total": depreciation,
        "running_costs_total": running_total,
        "total_cost": total,
        "per_year": total / years_owned,
        "per_month": total / months,
    }
