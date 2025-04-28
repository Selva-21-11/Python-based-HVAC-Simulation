# AI-Enhanced HVAC System Simulation for Energy Efficiency

## 📖 Overview
This project simulates an energy-efficient Heating, Ventilation, and Air Conditioning (HVAC) system using **SimPy** (Python) with **AI-based optimization**. It compares traditional rule-based control with an AI-optimized controller that adapts cooling based on real-time weather and historical temperature patterns.

## 🎯 Features
- HVAC system simulation using discrete-event modeling (SimPy).
- Real-time weather data integration via OpenWeather API.
- AI-driven adaptive cooling strategy to minimize energy consumption.
- Comparison with traditional threshold-based HVAC control.
- Performance analysis based on temperature stability, runtime, and energy use.

## 🛠️ Tech Stack
- **Python 3.10+**
- **SimPy** (Discrete-event simulation)
- **NumPy**, **Pandas** (Data processing)
- **Matplotlib** (Graph visualization)
- **OpenWeather API** (Live weather data)

## 📊 Results

| Metric | Traditional Model | AI-Optimized Model |
|:------:|:-----------------:|:------------------:|
| HVAC Runtime (60 min) | 30 mins | 22 mins |
| Total Energy Consumed | 3.00 kWh | 2.10 kWh |
| Temperature Stability | Moderate | High |

### 📈 Traditional HVAC Room Temperature
![TR output](https://github.com/user-attachments/assets/d82408b0-2c78-4b2e-b418-9e25f73064d6)

### 📈 AI-Enhanced HVAC Room Temperature
![AI output](https://github.com/user-attachments/assets/519616ab-d9c1-4edd-955e-a156c9bd1baa)

## 🚀 How to Run the Project

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ai-hvac-simulation.git
   cd ai-hvac-simulation
   ```

2. **Install the required libraries**:
   ```bash
   pip install simpy numpy pandas matplotlib requests
   ```

3. **Set your OpenWeather API Key**:
   - Update your API key inside the Python script:
     ```python
     API_KEY = "your_api_key_here"
     ```

4. **Run the simulation**:
   ```bash
   python simulation.py
   ```

5. **View the results**:
   - Output graphs for Room Temperature, Outdoor Temperature, and Humidity Trends will be plotted automatically.
   - Energy consumption and HVAC runtime will be printed in the console.

## 🔮 Future Improvements
- Expand simulation to multi-zone HVAC systems.
- Integrate occupancy detection and predictive control.
- Implement Reinforcement Learning (RL) based dynamic control.

## 🤝 Acknowledgements
- Velammal College of Engineering and Technology
- Department of Mechanical Engineering
- Project Guide: Mr. R. Ezilvannan

---

