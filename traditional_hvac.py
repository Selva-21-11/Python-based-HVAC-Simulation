import simpy
import matplotlib.pyplot as plt
import numpy as np
import json
import requests

# OpenWeather API Settings
API_KEY = ""  # 🔁 Replace with your actual API key
CITY_NAME = ""   # 🔁 Replace with your actual city

# Constants
ROOM_TEMP = 24.5  # Initial Room Temperature (°C)
THERMOSTAT_TEMP = 24  # Target Temperature (°C)
THERMOSTAT_LOWER_BUFFER = 23.8  # Lower Bound Hysteresis
THERMOSTAT_UPPER_BUFFER = 25.2  # Upper Bound Hysteresis
SIM_TIME = 60  # Simulation Time (Minutes)
ROOM_VOLUME = 50  # Room Volume (m^3)
AIR_HEAT_CAPACITY = 0.0012  # Heat Capacity of Air (kWh per m³ per °C)
WALL_INSULATION = 0.5  # Heat Transfer Coefficient (kW/°C)
HVAC_BLOWER_SPEED = 3.0  # Airflow Speed (m³/min)
AIRFLOW_EFFICIENCY = 0.7  # Efficiency of Air Mixing
HUMIDITY_REMOVAL_EFFICIENCY = 0.3  # Latent Heat Effect
OCCUPANTS = 5  # Number of People
SUNLIGHT_HEAT_GAIN = 1.5  # Sunlight Heat Gain (kW)
INITIAL_OUTDOOR_TEMP = 30  # Fallback Outdoor Temperature (°C)
INITIAL_HUMIDITY = 60  # Initial Humidity (%)

# Cooling Power Settings
MIN_COOLING_POWER = 2.5  # kW
MAX_COOLING_POWER = 10.0  # kW

# HVAC Efficiency Factors
MAX_EFFICIENCY = 0.9  # Best case efficiency
MIN_EFFICIENCY = 0.6  # Worst case efficiency
OUTDOOR_TEMP_IMPACT = 0.01  # Efficiency drop per °C above 30°C

# Weather Variability Parameters
TEMP_VARIABILITY = 0.5  # Outdoor Temp Fluctuation (°C per min) - More stable
HUMIDITY_VARIABILITY = 2  # Humidity Fluctuation (%)

# Heat gain function
def calculate_heat_gain(room_temp, outdoor_temp, humidity):
    conduction_loss = WALL_INSULATION * (outdoor_temp - room_temp)
    latent_heat_load = HUMIDITY_REMOVAL_EFFICIENCY * (humidity / 100)
    occupant_heat = OCCUPANTS * 0.1
    return conduction_loss + latent_heat_load + occupant_heat + SUNLIGHT_HEAT_GAIN

# Function to fetch real-time outdoor temperature
def fetch_outdoor_temperature():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        return data["main"]["temp"]
    except Exception as e:
        print("Failed to fetch outdoor temperature:", e)
        return INITIAL_OUTDOOR_TEMP  # Fallback

class SmartHVACSystem:
    def __init__(self, env):
        self.env = env
        self.room_temp = ROOM_TEMP
        self.room_temps = []
        self.time_steps = []
        self.hvac_runtime = 0
        self.hvac_status = False
        self.cooling_power = MIN_COOLING_POWER
        self.total_energy = 0  # Energy consumption tracker
        self.outdoor_temp = INITIAL_OUTDOOR_TEMP
        self.humidity = INITIAL_HUMIDITY
        self.outdoor_temps = []
        self.humidity_levels = []

    def adjust_efficiency(self):
        temp_diff = max(self.room_temp - THERMOSTAT_TEMP, 0.1)  # Avoid divide by zero
        efficiency = MAX_EFFICIENCY - (self.outdoor_temp - 30) * OUTDOOR_TEMP_IMPACT
        efficiency = np.clip(efficiency * (temp_diff / 2), MIN_EFFICIENCY, MAX_EFFICIENCY)
        return efficiency

    def update_weather(self):
        real_temp = fetch_outdoor_temperature()
        self.outdoor_temp = np.clip(real_temp + np.random.uniform(-TEMP_VARIABILITY, TEMP_VARIABILITY), 20, 35)
        self.humidity += np.random.uniform(-HUMIDITY_VARIABILITY, HUMIDITY_VARIABILITY)
        self.humidity = np.clip(self.humidity, 30, 90)
        self.outdoor_temps.append(self.outdoor_temp)
        self.humidity_levels.append(self.humidity)

    def smart_cooling(self):
        while self.env.now < SIM_TIME:
            self.room_temps.append(self.room_temp)
            self.time_steps.append(self.env.now)
            self.update_weather()  # Introduce weather variability
            heat_gain = calculate_heat_gain(self.room_temp, self.outdoor_temp, self.humidity)

            if self.hvac_status:
                efficiency = self.adjust_efficiency()
                self.cooling_power = np.clip(MAX_COOLING_POWER * efficiency, MIN_COOLING_POWER, MAX_COOLING_POWER)

                airflow_cooling_effect = (self.cooling_power * HVAC_BLOWER_SPEED * AIRFLOW_EFFICIENCY) / (ROOM_VOLUME * AIR_HEAT_CAPACITY)
                self.room_temp -= airflow_cooling_effect * 0.4  # Adjusting factor for realistic drop
                self.hvac_runtime += 1
                self.total_energy += self.cooling_power / 60  # Energy per minute

                if self.room_temp <= THERMOSTAT_LOWER_BUFFER:
                    self.room_temp = THERMOSTAT_LOWER_BUFFER
                    self.hvac_status = False  # Turn off HVAC

            else:
                self.room_temp += heat_gain * 0.3
                if self.room_temp >= THERMOSTAT_UPPER_BUFFER:
                    self.room_temp = THERMOSTAT_UPPER_BUFFER
                    self.hvac_status = True  # Turn on HVAC

            yield self.env.timeout(1)

# Run simulation
env = simpy.Environment()
hvac = SmartHVACSystem(env)
env.process(hvac.smart_cooling())
env.run(until=SIM_TIME)

# Smooth out the plot
smooth_x = np.linspace(0, SIM_TIME, 500)
smooth_y = np.interp(smooth_x, hvac.time_steps, hvac.room_temps)
smooth_outdoor_y = np.interp(smooth_x, hvac.time_steps, hvac.outdoor_temps)
smooth_humidity_y = np.interp(smooth_x, hvac.time_steps, hvac.humidity_levels)

# Plot results
plt.figure(figsize=(15, 8))
plt.subplot(2, 1, 1)
plt.plot(smooth_x, smooth_y, label="Room Temperature", color="blue", linewidth=2)
plt.axhline(y=THERMOSTAT_TEMP, color="red", linestyle="--", label="Target Temp (24°C)")
plt.axhline(y=THERMOSTAT_LOWER_BUFFER, color="purple", linestyle=":", label="Lower Hysteresis (23.8°C)")
plt.axhline(y=THERMOSTAT_UPPER_BUFFER, color="orange", linestyle=":", label="Upper Hysteresis (25.2°C)")
plt.ylabel("Temperature (°C)")
plt.title("HVAC Room Temperature Control with Dynamic Airflow")
plt.legend()
plt.grid()

plt.subplot(2, 1, 2)
plt.plot(smooth_x, smooth_outdoor_y, label="Outdoor Temperature", color="green", linewidth=2)
plt.plot(smooth_x, smooth_humidity_y, label="Humidity (%)", color="brown", linewidth=2)
plt.xlabel("Time (minutes)")
plt.ylabel("Outdoor Conditions")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

# Print energy consumption
print(f"Total HVAC Runtime: {hvac.hvac_runtime} minutes")
print(f"Total Energy Consumed: {hvac.total_energy:.2f} kWh")

# Create a dictionary for JSON output
hvac_results = {
    "Total HVAC Runtime (minutes)": hvac.hvac_runtime,
    "Total Energy Consumed (kWh)": round(hvac.total_energy, 2)
}

# Print the JSON output
print(json.dumps(hvac_results))
