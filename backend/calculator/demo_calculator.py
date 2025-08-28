# Demo script to test the carbon footprint calculator
from footprint_cal import CarbonFootprintCalculator

# Create calculator instance
calculator = CarbonFootprintCalculator()

# Example: Calculate emissions for sample data
sample_transport = {
    'car': {'type': 'Car (Petrol)', 'km_per_week': 150},
    'flights': {'domestic_per_year': 2, 'international_per_year': 1}
}

sample_energy = {
    'electricity': {'kwh_per_month': 300, 'grid_type': 'Electricity (US Grid Average)'},
    'natural_gas': {'scf_per_month': 1000}
}

sample_food = {
    'meat': {'beef': 1.0, 'chicken': 2.0, 'pork': 0.5, 'fish': 1.0},
    'dairy': {'milk': 4.0, 'cheese': 0.5},
    'plants': {'vegetables': 8.0, 'fruits': 5.0, 'grains': 3.0}
}

# Calculate emissions
transport_emissions = calculator.transport_calc.calculate_emissions(sample_transport)
energy_emissions = calculator.energy_calc.calculate_emissions(sample_energy)
food_emissions = calculator.food_calc.calculate_emissions(sample_food)

print("Sample Carbon Footprint Calculation:")
print(f"Transportation: {transport_emissions * 52:.1f} kg CO₂/year")
print(f"Energy: {energy_emissions * 12:.1f} kg CO₂/year") 
print(f"Food: {food_emissions * 52:.1f} kg CO₂/year")
print(f"Total: {(transport_emissions * 52) + (energy_emissions * 12) + (food_emissions * 52):.1f} kg CO₂/year")
