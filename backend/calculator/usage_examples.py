"""
Quick Usage Examples for Carbon Footprint Calculator
"""

# Example 1: Interactive Mode (asks questions)
from footprint_cal import CarbonFootprintCalculator

calculator = CarbonFootprintCalculator()
results, total = calculator.run_interactive_calculation()

# Example 2: Batch Mode (with predefined inputs)
sample_data = {
    "car_petrol_km_per_month": 400,
    "electricity_kwh_per_month": 300,
    "vegetarian_meals_per_week": 14,
    "non_vegetarian_meals_per_week": 7,
    "lpg_kg_per_month": 14.2
}

calculator = CarbonFootprintCalculator()
results, total = calculator.run_batch_calculation(sample_data)
print(f"Total carbon footprint: {total:.2f} kg CO₂/month")

# Example 3: Export results
calculator.export_results(results, total, "my_footprint.json")
