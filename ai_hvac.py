import simpy
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import json
import requests

# 🔐 OpenWeather API Configuration
API_KEY = "77be2c6588d8ba76996beb50beac69a5"      # Replace this with your API key
CITY_NAME = "Madurai"       # Replace this with your city name

# Constants
ROOM_TEMP = 24.5  
THERMOSTAT_TEMP = 24  
THERMOSTAT_LOWER_BUFFER = 23.8  
THERMOSTAT_UPPER_BUFFER = 25.2  
SIM_TIME = 60  
ROOM_VOLUME = 50  
AIR_HEAT_CAPACITY = 0.0012  
WALL_INSULATION = 0.5  
HVAC_BLOWER_SPEED = 3.0  
HUMIDITY_REMOVAL_EFFICIENCY = 0.3  
OCCUPANTS = 5  
SUNLIGHT_HEAT_GAIN = 1.5  
INITIAL_OUTDOOR_TEMP = 30  
INITIAL_HUMIDITY = 60  

# Cooling power settings
MIN_COOLING_POWER = 0.5  
MAX_COOLING_POWER = 3.5  

# HVAC Efficiency Factors
MAX_EFFICIENCY = 0.995  
MIN_EFFICIENCY = 0.85  
OUTDOOR_TEMP_IMPACT = 0.0015  

# Weather variability parameters
TEMP_VARIABILITY = 0.2  
HUMIDITY_VARIABILITY = 1.0  

# Function to fetch real-time outdoor temperature
def fetch_outdoor_temperature():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        return data["main"]["temp"]
    except Exception as e:
        print("Weather API error:", e)
        return INITIAL_OUTDOOR_TEMP  # fallback

# Heat gain function
def calculate_heat_gain(room_temp, outdoor_temp, humidity):
    conduction_loss = WALL_INSULATION * (outdoor_temp - room_temp)
    latent_heat_load = HUMIDITY_REMOVAL_EFFICIENCY * (humidity / 100)
    occupant_heat = OCCUPANTS * 0.06
    return conduction_loss + latent_heat_load + occupant_heat + SUNLIGHT_HEAT_GAIN

class AIHVACSystem:
    def __init__(self, env):
        self.env = env
        self.room_temp = ROOM_TEMP
        self.room_temps = []
        self.time_steps = []
        self.hvac_runtime = 0
        self.hvac_status = False
        self.cooling_power = MIN_COOLING_POWER
        self.total_energy = 0
        self.outdoor_temp = INITIAL_OUTDOOR_TEMP
        self.humidity = INITIAL_HUMIDITY
        self.outdoor_temps = []
        self.humidity_levels = []
    
    def update_weather(self):
        real_temp = fetch_outdoor_temperature()
        self.outdoor_temp = np.clip(real_temp + np.random.uniform(-TEMP_VARIABILITY, TEMP_VARIABILITY), 22, 34)
        self.humidity += np.random.uniform(-HUMIDITY_VARIABILITY, HUMIDITY_VARIABILITY)
        self.humidity = np.clip(self.humidity, 35, 85)
    
    def smart_cooling(self):
        while self.env.now < SIM_TIME:
            self.room_temps.append(self.room_temp)
            self.time_steps.append(self.env.now)
            self.humidity_levels.append(self.humidity)
            self.outdoor_temps.append(self.outdoor_temp)
            
            self.update_weather()
            heat_gain = calculate_heat_gain(self.room_temp, self.outdoor_temp, self.humidity)
            
            if self.hvac_status:
                efficiency = np.clip(MAX_EFFICIENCY - (self.outdoor_temp - 30) * OUTDOOR_TEMP_IMPACT, MIN_EFFICIENCY, MAX_EFFICIENCY)
                cooling_effect = (MAX_COOLING_POWER * efficiency * HVAC_BLOWER_SPEED) / (ROOM_VOLUME * AIR_HEAT_CAPACITY)
                self.room_temp = max(self.room_temp - cooling_effect * 0.18, THERMOSTAT_LOWER_BUFFER)
                self.hvac_runtime += 1
                self.total_energy += MAX_COOLING_POWER / 100  
                if self.room_temp <= THERMOSTAT_LOWER_BUFFER:
                    self.hvac_status = False
            else:
                self.room_temp += heat_gain * 0.10
                if self.room_temp >= THERMOSTAT_UPPER_BUFFER:
                    self.hvac_status = True
            
            self.room_temp = np.clip(self.room_temp, THERMOSTAT_LOWER_BUFFER, THERMOSTAT_UPPER_BUFFER)
            yield self.env.timeout(1)

# Run simulation
env = simpy.Environment()
hvac = AIHVACSystem(env)
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
plt.title("HVAC Room Temperature Control with AI + Live Weather")
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

# Create JSON output
hvac_results = {
    "Total HVAC Runtime (minutes)": hvac.hvac_runtime,
    "Total Energy Consumed (kWh)": round(hvac.total_energy, 2)
}

# Print JSON
print(json.dumps(hvac_results))
