import os
import pandas as pd
import json
from typing import Dict, List, Tuple
from abc import ABC, abstractmethod

class DataLoader:
    """Loads and manages emission factor data from CSV files"""

    def __init__(self):
        self.data = {}
        self.load_all_data()
    
    def load_all_data(self):
        """Load all CSV files into memory"""
        try:
            # find the directory of this file (backend/calculator)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")

            # use os.path.join for OS-safe paths
            self.data['transportation'] = pd.read_csv(os.path.join(data_dir, "Transportation.csv"))
            self.data['energy'] = pd.read_csv(os.path.join(data_dir, "Energy_Usage.csv"))
            self.data['food'] = pd.read_csv(os.path.join(data_dir, "Food_Diet.csv"))
            self.data['waste'] = pd.read_csv(os.path.join(data_dir, "Waste_Consumption.csv"))
            self.data['appliances'] = pd.read_csv(os.path.join(data_dir, "Household_Appliances.csv"))
            self.data['conversions'] = pd.read_csv(os.path.join(data_dir, "MVP_Conversion_Factors.csv"))

            print("✅ All emission factor datasets loaded successfully!")
        except FileNotFoundError as e:
            print(f"❌ Error loading data files: {e}")
            print("➡️ Make sure all CSV files are in backend/calculator/data directory")
            return False
        return True


    def get_transport_factors(self) -> Dict:
        """Get transportation emission factors"""
        df = self.data['transportation']
        return dict(zip(df['Transport_Mode'], df['CO2_Factor_kg_per_km']))

    def get_energy_factors(self) -> Dict:
        """Get energy emission factors"""
        df = self.data['energy']
        return dict(zip(df['Energy_Source'], df['CO2_Factor']))

    def get_food_factors(self) -> Dict:
        """Get food emission factors"""
        df = self.data['food']
        return dict(zip(df['Food_Category'], df['CO2_Factor_kg_per_kg']))

    def get_waste_factors(self) -> Dict:
        """Get waste emission factors by type and method"""
        df = self.data['waste']
        factors = {}
        for _, row in df.iterrows():
            key = f"{row['Waste_Type']}_{row['Disposal_Method']}"
            factors[key] = row['CO2_Factor_kg_per_kg']
        return factors

    def get_appliance_factors(self) -> Dict:
        """Get appliance annual CO2 factors"""
        df = self.data['appliances']
        return dict(zip(df['Appliance'], df['CO2_kg_per_Year_US_Grid']))

class CategoryCalculator(ABC):
    """Abstract base class for category-specific calculators"""

    @abstractmethod
    def collect_user_input(self) -> Dict:
        pass

    @abstractmethod
    def calculate_emissions(self, inputs: Dict) -> float:
        pass

    @abstractmethod
    def get_recommendations(self, emissions: float, inputs: Dict) -> List[str]:
        pass

class TransportationCalculator(CategoryCalculator):
    """Handles transportation-related carbon footprint calculations"""

    def __init__(self, data_loader: DataLoader):
        self.factors = data_loader.get_transport_factors()

    def collect_user_input(self) -> Dict:
        print("\n🚗 TRANSPORTATION")
        print("Let's calculate your weekly travel emissions...")

        inputs = {}

        # Car usage
        car_usage = input("\nDo you own/use a car? (yes/no): ").lower()
        if car_usage == 'yes':
            car_type = self.get_car_type()
            weekly_km = float(input(f"How many km do you drive per week? "))
            inputs['car'] = {'type': car_type, 'km_per_week': weekly_km}

        # Public transport
        bus_usage = input("\nDo you use buses? (yes/no): ").lower()
        if bus_usage == 'yes':
            bus_km = float(input("How many km by bus per week? "))
            inputs['bus'] = {'km_per_week': bus_km}

        # Train usage
        train_usage = input("\nDo you use trains? (yes/no): ").lower()
        if train_usage == 'yes':
            train_km = float(input("How many km by train per week? "))
            inputs['train'] = {'km_per_week': train_km}

        # Flight usage (annual)
        flight_usage = input("\nDo you take flights? (yes/no): ").lower()
        if flight_usage == 'yes':
            domestic_flights = int(input("How many domestic flights per year? "))
            international_flights = int(input("How many international flights per year? "))
            inputs['flights'] = {
                'domestic_per_year': domestic_flights,
                'international_per_year': international_flights
            }

        return inputs

    def get_car_type(self) -> str:
        print("\nSelect your car type:")
        print("1. Petrol/Gasoline car")
        print("2. Diesel car") 
        print("3. Electric vehicle (EV)")
        print("4. Hybrid car")

        choice = input("Enter choice (1-4): ")
        mapping = {
            '1': 'Car (Petrol)',
            '2': 'Car (Diesel)', 
            '3': 'Electric Car (EV)',
            '4': 'Hybrid Car'
        }
        return mapping.get(choice, 'Car (Petrol)')

    def calculate_emissions(self, inputs: Dict) -> float:
        weekly_emissions = 0

        # Car emissions
        if 'car' in inputs:
            car_factor = self.factors.get(inputs['car']['type'], 0.23)
            weekly_emissions += inputs['car']['km_per_week'] * car_factor

        # Bus emissions
        if 'bus' in inputs:
            bus_factor = self.factors.get('Public Bus', 0.09)
            weekly_emissions += inputs['bus']['km_per_week'] * bus_factor

        # Train emissions
        if 'train' in inputs:
            train_factor = self.factors.get('Train (Regular)', 0.03)
            weekly_emissions += inputs['train']['km_per_week'] * train_factor

        # Flight emissions (convert annual to weekly)
        if 'flights' in inputs:
            # Assume domestic = 500 km avg, international = 8000 km avg
            domestic_km_per_year = inputs['flights']['domestic_per_year'] * 1000
            international_km_per_year = inputs['flights']['international_per_year'] * 8000

            domestic_factor = self.factors.get('Flight (Domestic)', 0.13)
            international_factor = self.factors.get('Flight (International)', 0.10)

            annual_flight_emissions = (domestic_km_per_year * domestic_factor + 
                                     international_km_per_year * international_factor)
            weekly_emissions += annual_flight_emissions / 52  # Convert to weekly

        return weekly_emissions

    def get_recommendations(self, emissions: float, inputs: Dict) -> List[str]:
        recommendations = []

        if emissions > 50:  # High transport emissions
            recommendations.append(" Consider cycling or walking for short trips (<5 km)")
            recommendations.append(" Use public transport more frequently")

        if 'car' in inputs and inputs['car']['type'] in ['Car (Petrol)', 'Car (Diesel)']:
            recommendations.append(" Consider switching to an electric or hybrid vehicle")

        if 'flights' in inputs and inputs['flights']['domestic_per_year'] > 4:
            recommendations.append(" Reduce domestic flights - try trains for shorter distances")

        if emissions < 10:
            recommendations.append(" Great job! Your transport footprint is very low")

        return recommendations

class EnergyCalculator(CategoryCalculator):
    """Handles home energy consumption calculations"""

    def __init__(self, data_loader: DataLoader):
        self.factors = data_loader.get_energy_factors()

    def collect_user_input(self) -> Dict:
        print("\n⚡ HOME ENERGY")
        print("Let's calculate your monthly energy consumption...")

        inputs = {}

        # Electricity
        monthly_kwh = float(input("\nWhat's your monthly electricity consumption (kWh)? "))

        print("\nSelect your electricity grid type:")
        print("1. Average grid mix")
        print("2. Coal-heavy region") 
        print("3. Natural gas region")
        print("4. Renewable/clean energy")

        grid_choice = input("Enter choice (1-4): ")
        grid_mapping = {
            '1': 'Electricity (US Grid Average)',
            '2': 'Electricity (Coal-heavy)',
            '3': 'Electricity (Natural Gas)',
            '4': 'Electricity (Renewable)'
        }

        inputs['electricity'] = {
            'kwh_per_month': monthly_kwh,
            'grid_type': grid_mapping.get(grid_choice, 'Electricity (US Grid Average)')
        }

        # Natural Gas
        gas_usage = input("\nDo you use natural gas for heating/cooking? (yes/no): ").lower()
        if gas_usage == 'yes':
            gas_amount = float(input("Monthly natural gas usage (scf): "))
            inputs['natural_gas'] = {'scf_per_month': gas_amount}

        # LPG/Propane
        lpg_usage = input("\nDo you use LPG/Propane? (yes/no): ").lower()
        if lpg_usage == 'yes':
            lpg_gallons = float(input("Monthly LPG usage (gallons): "))
            inputs['lpg'] = {'gallons_per_month': lpg_gallons}

        return inputs

    def calculate_emissions(self, inputs: Dict) -> float:
        monthly_emissions = 0

        # Electricity
        if 'electricity' in inputs:
            grid_factor = self.factors.get(inputs['electricity']['grid_type'], 0.45)
            monthly_emissions += inputs['electricity']['kwh_per_month'] * grid_factor

        # Natural Gas
        if 'natural_gas' in inputs:
            gas_factor = self.factors.get('Natural Gas', 0.0544)
            monthly_emissions += inputs['natural_gas']['scf_per_month'] * gas_factor

        # LPG
        if 'lpg' in inputs:
            lpg_factor = self.factors.get('Propane (LPG)', 5.72)
            monthly_emissions += inputs['lpg']['gallons_per_month'] * lpg_factor

        weekly_emissions = monthly_emissions * (12 / 52)
        return weekly_emissions

    def get_recommendations(self, emissions: float, inputs: Dict) -> List[str]:
        recommendations = []

        if emissions > 200:  # High energy emissions
            recommendations.append(" Switch to LED lighting and energy-efficient appliances")
            recommendations.append(" Optimize heating/cooling - use programmable thermostats")

        if 'electricity' in inputs:
            if inputs['electricity']['grid_type'] == 'Electricity (Coal-heavy)':
                recommendations.append(" Consider installing solar panels or switching to green energy")
            if inputs['electricity']['kwh_per_month'] > 400:
                recommendations.append(" Your electricity usage is high - audit your appliances")

        if emissions < 50:
            recommendations.append(" Excellent! Your home energy footprint is very efficient")

        return recommendations

class FoodCalculator(CategoryCalculator):
    """Handles food and diet-related calculations"""

    def __init__(self, data_loader: DataLoader):
        self.factors = data_loader.get_food_factors()

    def collect_user_input(self) -> Dict:
        print("\n🍽️ FOOD & DIET")
        print("Let's calculate your weekly food consumption...")

        inputs = {}

        # Meat consumption
        print("\nMeat consumption per week:")
        beef_kg = float(input("Beef/Red meat (kg): ") or "0")
        chicken_kg = float(input("Chicken (kg): ") or "0")
        pork_kg = float(input("Pork (kg): ") or "0")
        fish_kg = float(input("Fish (kg): ") or "0")

        inputs['meat'] = {
            'beef': beef_kg,
            'chicken': chicken_kg, 
            'pork': pork_kg,
            'fish': fish_kg
        }

        # Dairy
        print("\nDairy consumption per week:")
        milk_kg = float(input("Milk (kg/liters): ") or "0")
        cheese_kg = float(input("Cheese (kg): ") or "0")

        inputs['dairy'] = {
            'milk': milk_kg,
            'cheese': cheese_kg
        }

        # Plant foods
        print("\nPlant foods per week:")
        vegetables_kg = float(input("Vegetables (kg): ") or "5")
        fruits_kg = float(input("Fruits (kg): ") or "3")
        grains_kg = float(input("Rice/Grains (kg): ") or "2")

        inputs['plants'] = {
            'vegetables': vegetables_kg,
            'fruits': fruits_kg,
            'grains': grains_kg
        }

        return inputs

    def calculate_emissions(self, inputs: Dict) -> float:
        weekly_emissions = 0

        # Meat emissions
        if 'meat' in inputs:
            weekly_emissions += inputs['meat']['beef'] * self.factors.get('Beef (Red Meat)', 27.0)
            weekly_emissions += inputs['meat']['chicken'] * self.factors.get('Chicken', 6.9)
            weekly_emissions += inputs['meat']['pork'] * self.factors.get('Pork', 7.2)
            weekly_emissions += inputs['meat']['fish'] * self.factors.get('Fish (Wild-caught)', 2.9)

        # Dairy emissions
        if 'dairy' in inputs:
            weekly_emissions += inputs['dairy']['milk'] * self.factors.get('Milk (Dairy)', 3.3)
            weekly_emissions += inputs['dairy']['cheese'] * self.factors.get('Cheese (Hard)', 13.5)

        # Plant emissions
        if 'plants' in inputs:
            weekly_emissions += inputs['plants']['vegetables'] * self.factors.get('Vegetables (Root)', 0.4)
            weekly_emissions += inputs['plants']['fruits'] * self.factors.get('Bananas', 0.7)
            weekly_emissions += inputs['plants']['grains'] * self.factors.get('Rice', 2.7)

        return weekly_emissions

    def get_recommendations(self, emissions: float, inputs: Dict) -> List[str]:
        recommendations = []

        total_meat = sum(inputs.get('meat', {}).values())

        if total_meat > 2:  # High meat consumption
            recommendations.append(" Consider reducing red meat consumption - try chicken or plant proteins")
            recommendations.append(" Add more plant-based meals to your weekly diet")

        if inputs.get('meat', {}).get('beef', 0) > 0.5:
            recommendations.append(" Beef has the highest carbon footprint - try substituting with chicken")

        if emissions > 50:
            recommendations.append(" Your diet has high emissions - focus on more vegetables and less meat")

        if emissions < 20:
            recommendations.append(" Great! You have a low-carbon diet")

        return recommendations

class CarbonFootprintCalculator:
    """Main calculator class that orchestrates all category calculations"""

    def __init__(self):
        self.data_loader = DataLoader()
        if not hasattr(self.data_loader, 'data') or not self.data_loader.data:
            print("❌ Failed to load emission factor data. Exiting...")
            return

        self.transport_calc = TransportationCalculator(self.data_loader)
        self.energy_calc = EnergyCalculator(self.data_loader)
        self.food_calc = FoodCalculator(self.data_loader)
        self.waste_calc = WasteCalculator(self.data_loader)

        self.results = {}

    def run_full_assessment(self):
        """Run complete carbon footprint assessment"""
        print("🌍 PERSONAL CARBON FOOTPRINT CALCULATOR")
        print("=" * 50)
        print("This calculator will assess your carbon footprint across key categories.")
        print("Please answer the questions as accurately as possible.\n")

        # Transportation
        transport_inputs = self.transport_calc.collect_user_input()
        transport_emissions = self.transport_calc.calculate_emissions(transport_inputs)
        self.results['transportation'] = {
            'weekly_kg_co2': transport_emissions,
            'annual_kg_co2': transport_emissions * 52,
            'inputs': transport_inputs
        }

        # Energy
        energy_inputs = self.energy_calc.collect_user_input()
        energy_emissions = self.energy_calc.calculate_emissions(energy_inputs)
        self.results['energy'] = {
            'weekly_kg_co2': energy_emissions,
            'annual_kg_co2': energy_emissions * 52,
            'inputs': energy_inputs
        }

        # Food
        food_inputs = self.food_calc.collect_user_input()
        food_emissions = self.food_calc.calculate_emissions(food_inputs)
        self.results['food'] = {
            'weekly_kg_co2': food_emissions,
            'annual_kg_co2': food_emissions * 52,
            'inputs': food_inputs
        }

        # Waste
        waste_inputs = self.waste_calc.collect_user_input()
        waste_emissions_weekly = self.waste_calc.calculate_emissions(waste_inputs)
        self.results['waste'] = {
            'weekly_kg_co2': waste_emissions_weekly,
            'annual_kg_co2': waste_emissions_weekly * 52,
            'inputs': waste_inputs
        }

        total_annual = (
                self.results['transportation']['annual_kg_co2'] +
                self.results['energy']['annual_kg_co2'] +
                self.results['food']['annual_kg_co2'] +
                self.results['waste']['annual_kg_co2']
            )

        self.results['total_annual_kg_co2'] = total_annual

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive footprint report with recommendations"""
        print("\n" + "=" * 60)
        print("📊 YOUR CARBON FOOTPRINT REPORT")
        print("=" * 60)

        # Summary
        total_annual = self.results['total_annual_kg_co2']
        print(f"\n🎯 TOTAL ANNUAL FOOTPRINT: {total_annual:.1f} kg CO₂")
        print(f"📅 Average per month: {total_annual/12:.1f} kg CO₂")
        print(f"📆 Average per day: {total_annual/365:.1f} kg CO₂")

        # Category breakdown
        print(f"\n📋 BREAKDOWN BY CATEGORY:")
        print(f"🚗 Transportation: {self.results['transportation']['annual_kg_co2']:.1f} kg CO₂ ({self.results['transportation']['annual_kg_co2']/total_annual*100:.1f}%)")
        print(f"⚡ Energy:         {self.results['energy']['annual_kg_co2']:.1f} kg CO₂ ({self.results['energy']['annual_kg_co2']/total_annual*100:.1f}%)")
        print(f"🍽️  Food:          {self.results['food']['annual_kg_co2']:.1f} kg CO₂ ({self.results['food']['annual_kg_co2']/total_annual*100:.1f}%)")
        print(f"🧺 Waste:          {self.results['waste']['annual_kg_co2']:.1f} kg CO₂ "
        f"({self.results['waste']['annual_kg_co2']/total_annual*100:.1f}%)")

        # Comparison to averages
        self.compare_to_benchmarks(total_annual)

        # Recommendations
        self.generate_recommendations()

        # Save results
        self.save_results()
    

    def compare_to_benchmarks(self, total_annual: float):
        """Compare user's footprint to global averages"""
        print(f"\n🌍 COMPARISON TO GLOBAL AVERAGES:")

        # Global averages (approximate)
        us_average = 16000  # kg CO2 per year
        eu_average = 8000
        world_average = 4000
        paris_target = 2300  # To limit warming to 1.5°C

        if total_annual > us_average:
            print(f"📈 Your footprint is above US average ({us_average:,} kg)")
        elif total_annual > eu_average:
            print(f"📊 Your footprint is below US but above EU average ({eu_average:,} kg)")
        elif total_annual > world_average:
            print(f"📊 Your footprint is above world average ({world_average:,} kg)")
        elif total_annual > paris_target:
            print(f"📊 Your footprint is below world average but above Paris Agreement target ({paris_target:,} kg)")
        else:
            print(f"🌟 Excellent! Your footprint aligns with Paris Agreement targets!")

    def generate_recommendations(self):
        """Generate personalized recommendations"""
        print(f"\n💡 PERSONALIZED RECOMMENDATIONS:")

        # Get recommendations from each calculator
        transport_recs = self.transport_calc.get_recommendations(
            self.results['transportation']['weekly_kg_co2'],
            self.results['transportation']['inputs']
        )

        energy_recs = self.energy_calc.get_recommendations(
            self.results['energy']['weekly_kg_co2'],
            self.results['energy']['inputs']
        )

        food_recs = self.food_calc.get_recommendations(
            self.results['food']['weekly_kg_co2'],
            self.results['food']['inputs']
        )

        waste_recs = self.waste_calc.get_recommendations(
        self.results['waste']['weekly_kg_co2'],
        self.results['waste']['inputs']
    )

        # Print all recommendations
        all_recs = transport_recs + energy_recs + food_recs + waste_recs
        for i, rec in enumerate(all_recs, 1):
            print(f"{i}. {rec}")

    def save_results(self):
        """Save results to JSON file with summary statistics"""
        try:
            # --- Compute new summary metrics ---
            weekly_totals = {
                "transportation": self.results['transportation'].get('weekly_kg_co2', 0),
                "food": self.results['food'].get('weekly_kg_co2', 0),
                "waste": self.results['waste'].get('weekly_kg_co2', 0),
                "energy": self.results['energy'].get('weekly_kg_co2', 0) 
            }

            total_weekly_kg_co2 = sum(weekly_totals.values())
            category_with_highest = max(weekly_totals, key=weekly_totals.get)

            # --- Compare to last saved result (if any) ---
            previous_week_total = None
            change_from_last_week_percent = None

            if os.path.exists('carbon_footprint_results.json'):
                with open('carbon_footprint_results.json', 'r') as f:
                    prev_data = json.load(f)
                    prev_summary = prev_data.get("summary", {})
                    previous_week_total = prev_summary.get("total_weekly_kg_co2")

            if previous_week_total:
                change_from_last_week_percent = (
                    ((total_weekly_kg_co2 - previous_week_total) / previous_week_total) * 100
                )

            # --- Add new fields ---
            self.results["summary"] = {
                "total_weekly_kg_co2": round(total_weekly_kg_co2, 2),
                "change_from_last_week_percent": round(change_from_last_week_percent, 2) if change_from_last_week_percent else None,
                "category_with_highest_emission": category_with_highest
            }

            # --- Save updated JSON ---
            with open('carbon_footprint_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)

            print(f"\n💾 Results saved to 'carbon_footprint_results.json'")
            print(f"📊 Weekly total: {total_weekly_kg_co2:.2f} kg CO₂")
            print(f"🏆 Highest category: {category_with_highest}")
            if change_from_last_week_percent is not None:
                print(f"📈 Change from last week: {change_from_last_week_percent:.2f}%")

        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def generate_recommendations_from_results(self, results: dict) -> dict:
        """
        Use existing per-category calculators to create combined recommendations
        Returns a dictionary with ordered recommendations and per-category lists.
        """
        try:
            transport_recs = self.transport_calc.get_recommendations(
                results.get('transportation', {}).get('weekly_kg_co2', 0),
                results.get('transportation', {}).get('inputs', {})
            )
            energy_recs = self.energy_calc.get_recommendations(
                results.get('energy', {}).get('weekly_kg_co2', 0),
                results.get('energy', {}).get('inputs', {})
            )
            food_recs = self.food_calc.get_recommendations(
                results.get('food', {}).get('weekly_kg_co2', 0),
                results.get('food', {}).get('inputs', {})
            )
            waste_recs = self.waste_calc.get_recommendations(
                results.get('waste', {}).get('weekly_kg_co2', 0),
                results.get('waste', {}).get('inputs', {})
            )

            # keep order: energy -> transport -> food -> waste (you can change)
            all_recs = []
            for cat, recs in (('energy', energy_recs), ('transport', transport_recs),
                              ('food', food_recs), ('waste', waste_recs)):
                for r in recs:
                    all_recs.append({"category": cat, "text": r})

            # dedupe preserving order
            seen = set()
            deduped = []
            for r in all_recs:
                key = (r['category'], r['text'])
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(r)

            return {
                "count": len(deduped),
                "recommendations": deduped
            }
        except Exception as e:
            # safe fallback
            print(f"❌ Error generating recommendations: {e}")
            return {"count": 0, "recommendations": []}


    def calculate_from_payload(self, payload: dict):
        """
        Calculate carbon footprint directly from JSON payload (for API use)
        """
        try:
            # Extract category inputs from payload
            transport_inputs = payload.get("transportation", {})
            energy_inputs = payload.get("energy", {})
            food_inputs = payload.get("food", {})
            waste_inputs = payload.get("waste", {})

            # Calculate emissions for each category
            transport_emissions = self.transport_calc.calculate_emissions(transport_inputs)
            energy_emissions = self.energy_calc.calculate_emissions(energy_inputs)
            food_emissions = self.food_calc.calculate_emissions(food_inputs)
            waste_emissions = self.waste_calc.calculate_emissions(waste_inputs)

            # Combine all results
            results = {
                "transportation": {
                    "weekly_kg_co2": transport_emissions,
                    "annual_kg_co2": transport_emissions * 52,
                    "inputs": transport_inputs,
                },
                "energy": {
                    "weekly_kg_co2": energy_emissions,
                    "annual_kg_co2": energy_emissions * 52,
                    "inputs": energy_inputs,
                },
                "food": {
                    "weekly_kg_co2": food_emissions,
                    "annual_kg_co2": food_emissions * 52,
                    "inputs": food_inputs,        
                },
                "waste": {
                    "weekly_kg_co2": waste_emissions,
                    "annual_kg_co2": waste_emissions * 52,
                    "inputs": waste_inputs,
                },
            }

            total_weekly = (
                transport_emissions + energy_emissions + food_emissions + waste_emissions
            )
            total_annual = total_weekly * 52

            results["summary"] = {
                "total_weekly_kg_co2": total_weekly,
                "total_annual_kg_co2": total_annual,
                "highest_category": max(
                    results,
                    key=lambda x: results[x].get("weekly_kg_co2", 0),
                ),
            }

            return results

        except Exception as e:
            print(f"❌ Error in calculate_from_payload: {e}")
            raise e


def main():
    """Main function to run the carbon footprint calculator"""
    calculator = CarbonFootprintCalculator()

    if hasattr(calculator, 'data_loader') and calculator.data_loader.data:
        calculator.run_full_assessment()
    else:
        print("❌ Calculator initialization failed. Please check your CSV files.")


class WasteCalculator(CategoryCalculator):
    """Handles weekly household waste estimations with categorical inputs"""

    def __init__(self, data_loader: DataLoader):
        # Expect keys like: 'Plastic_mixed', 'Plastic_recycled', 'Organic_landfill', 'Organic_compost'
        self.factors = data_loader.get_waste_factors()

        # Fallback factors if CSV missing
        self.defaults = {
            "Plastic_mixed": 3.0, "Plastic_recycled": 2.1,
            "Paper_mixed": 1.0,   "Paper_recycled": 0.5,
            "Glass_mixed": 0.85,  "Glass_recycled": 0.64,
            "Metal_mixed": 2.0,   "Metal_recycled": 1.5,
            "Organic_landfill": 0.5, "Organic_compost": 0.1
        }

        self.bins_kg = {
            "plastic": {"none": 0.0, "low": 0.12, "medium": 0.40, "high": 0.80},
            "paper":   {"none": 0.0, "low": 0.5,  "medium": 1.5,  "high": 3.0},
            "glass":   {"none": 0.0, "low": 0.3,  "medium": 0.8,  "high": 1.5},
            "metal":   {"none": 0.0, "low": 0.2,  "medium": 0.6,  "high": 1.2},
            "organic": {"none": 0.0, "low": 2.0,  "medium": 4.0,  "high": 7.0}
        }

    def collect_user_input(self) -> Dict:
        print("\n♻️ WASTE (weekly)")
        print("Select your approximate waste levels this week (none/low/medium/high).")

        def ask_level(label, default="low"):
            val = input(f"{label} (none/low/medium/high) [{default}]: ").strip().lower() or default
            return val if val in ("none","low","medium","high") else default

        inputs = {}
        inputs['levels'] = {
            'plastic': ask_level("Plastic"),
            'paper':   ask_level("Paper/Cardboard"),
            'glass':   ask_level("Glass"),
            'metal':   ask_level("Metal (cans/tins)"),
            'organic': ask_level("Food/Organic scraps", default="medium")
        }

        def ask_yesno(label, default="yes"):
            val = input(f"{label} (yes/no) [{default}]: ").strip().lower() or default
            return 'yes' if val in ('y','yes') else 'no'

        inputs['recycling'] = {
            'plastic': ask_yesno("Do you recycle plastic?", default="no"),
            'paper':   ask_yesno("Do you recycle paper?", default="yes"),
            'glass':   ask_yesno("Do you recycle glass/metal?", default="yes"),
            'metal':   'yes'  # tie to glass prompt; many ULBs co-collect glass/metal
        }
        inputs['compost'] = ask_yesno("Do you compost organics?", default="no")

        return inputs

    def _factor(self, waste_type: str, recycled: bool=False, compost: bool=False) -> float:
        """
        Returns an appropriate factor key with graceful fallback
        """
        key = None
        if waste_type == "organic":
            key = "Organic_compost" if compost else "Organic_landfill"
        else:
            method = "recycled" if recycled else "mixed"
            key = f"{waste_type.capitalize()}_{method}"

        return self.factors.get(key, self.defaults.get(key, 0.0))

    def calculate_emissions(self, inputs: Dict) -> float:
        levels = inputs['levels']
        recycling = inputs['recycling']
        compost = (inputs['compost'] == 'yes')

        weekly_kg_co2 = 0.0

        # Plastic
        kg_plastic = self.bins_kg['plastic'][levels['plastic']]
        f_plastic = self._factor("plastic", recycled=(recycling['plastic'] == 'yes'))
        weekly_kg_co2 += kg_plastic * f_plastic

        # Paper
        kg_paper = self.bins_kg['paper'][levels['paper']]
        f_paper = self._factor("paper", recycled=(recycling['paper'] == 'yes'))
        weekly_kg_co2 += kg_paper * f_paper

        # Glass
        kg_glass = self.bins_kg['glass'][levels['glass']]
        f_glass = self._factor("glass", recycled=(recycling['glass'] == 'yes'))
        weekly_kg_co2 += kg_glass * f_glass

        # Metal
        kg_metal = self.bins_kg['metal'][levels['metal']]
        f_metal = self._factor("metal", recycled=(recycling.get('metal','yes') == 'yes'))
        weekly_kg_co2 += kg_metal * f_metal

        # Organic
        kg_org = self.bins_kg['organic'][levels['organic']]
        f_org = self._factor("organic", compost=compost)
        weekly_kg_co2 += kg_org * f_org

        return weekly_kg_co2

    def get_recommendations(self, emissions: float, inputs: Dict) -> List[str]:
        recs = []
        levels = inputs['levels']
        recycling = inputs['recycling']
        compost = (inputs['compost'] == 'yes')

        if levels['plastic'] in ('medium','high') and recycling['plastic']=='no':
            recs.append(" Reduce single-use plastic; start with a reusable bottle and bags.")
            recs.append(" Begin segregating plastic and find a local recycler.")

        if levels['paper'] in ('medium','high') and recycling['paper']=='no':
            recs.append(" Flatten & recycle cardboard; switch to e-bills where possible.")

        if levels['glass'] in ('medium','high') and recycling['glass']=='no':
            recs.append(" Rinse bottles/cans and recycle; look for return/deposit programs.")

        if levels['organic'] in ('medium','high') and not compost:
            recs.append(" Start basic composting or use a community compost drop-off.")

        if emissions < 5:
            recs.append(" Great job! Your waste footprint is quite low this week.")

        return recs

if __name__ == "__main__":
    main()
