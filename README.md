````markdown
# 🌍 EMEA GeoMap Monte Carlo Simulator

A comprehensive interactive web application for mapping Europe, the Middle East, and Africa with real-time country tagging, color coding, and advanced Monte Carlo simulation capabilities.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [API & Simulation Engine](#api--simulation-engine)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**GeoMap Simulation** is a Dash-based interactive web application that combines geospatial visualization with probabilistic analysis. It enables users to:

- **Tag geographic regions** across Europe, Middle East, and Africa with custom colors
- **Run Monte Carlo simulations** with configurable parameters
- **Analyze probability distributions** with comprehensive statistical metrics
- **Export configurations** and results for further analysis

Perfect for financial modeling, risk assessment, scenario planning, and geographic analysis workflows.

---

## ✨ Features

### 1. **Interactive EMEA Map** 📍
- **Click-to-select interface**: Simply click any country to tag it
- **Color customization**: Choose from 6 predefined colors (Red, Blue, Yellow, Purple, Green, Gray)
- **Real-time visualization**: Instant feedback on color assignments
- **Regional grouping**: Automatic organization by Europe, Middle East, Africa
- **Configuration export**: Save tagged country configurations as JSON files

### 2. **Monte Carlo Simulation Engine** 🎲
- **Multiple distributions**: Normal (Gaussian), Log-Normal, and Uniform
- **Configurable parameters**:
  - 1 to 10,000 independent simulations
  - 1 to 100,000 iterations per simulation
  - Custom mean values (-1,000 to 1,000)
  - Variable standard deviations (0.01 to 100)
- **Real-time execution**: Fast computation with NumPy optimization
- **Parameter validation**: Comprehensive input validation with user feedback

### 3. **Statistical Analysis** 📊
- **Descriptive statistics**: Mean, median, standard deviation, min/max
- **Percentile analysis**: 5th, 25th, 75th, 95th percentiles
- **Distribution shape metrics**: Skewness and kurtosis calculations
- **Visual summaries**: Histogram distributions and metric dashboards
- **Timestamped results**: Full audit trail with execution timestamps

### 4. **User Interface** 🎨
- **Bootstrap-powered design**: Professional, responsive layout
- **Tabbed navigation**:
  - Map & Country Tagging
  - Monte Carlo Simulation
  - Results & Analysis
  - Help & Documentation
- **Real-time loading states**: User feedback during computation
- **Error handling**: Graceful error messages with actionable guidance
- **Mobile responsive**: Works on desktop, tablet, and mobile devices

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Web Framework** | Dash | 2.14.2 |
| **UI Components** | dash-bootstrap-components | 1.6.0 |
| **Visualization** | Plotly | 5.18.0 |
| **Data Processing** | Pandas, NumPy | 2.1.4, 1.26.3 |
| **Geospatial** | GeoPandas, Shapely | 0.14.1, 2.0.2 |
| **Production Server** | Gunicorn / Waitress | 21.2.0 / 2.1.2 |
| **Language** | Python | 3.9+ |

---

## 📦 Installation

### Prerequisites
- **Python 3.9 or higher**
- **pip** or **conda** package manager
- **Git** (optional, for cloning)

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/JulienBechoux/geomap-simulation.git
   cd geomap-simulation
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   Open your browser and navigate to: `http://localhost:8050`

### Option 2: Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t geomap-simulator .
   ```

2. **Run the container**
   ```bash
   docker run -p 8050:8050 geomap-simulator
   ```

3. **Access the app**
   Open: `http://localhost:8050`

### Option 3: Using Conda

```bash
conda create -n geomap python=3.11
conda activate geomap
pip install -r requirements.txt
python app.py
```

---

## 📚 Usage Guide

### Getting Started (5 minutes)

#### Step 1: Tag Countries on the Map 🗺️

1. Navigate to the **"📍 Map & Country Tagging"** tab
2. Select a color from the **"Select Color"** dropdown
3. Click on any country in the map to tag it with the selected color
4. The country name appears in the **"Selected Country"** field
5. Repeat steps 2-4 to tag multiple countries with different colors

**Example workflow:**
- Select Red → Click on France, Germany, UK
- Select Blue → Click on Egypt, Nigeria, South Africa
- Select Green → Click on Turkey, Saudi Arabia, UAE

#### Step 2: View Tagged Countries Summary

- Tagged countries are automatically grouped by region (Europe, Middle East, Africa)
- Each country badge shows its assigned color
- Use **"🔄 Reset All Colors"** to clear all tags
- Use **"💾 Save Configuration"** to export tags as JSON

#### Step 3: Run a Monte Carlo Simulation 🎲

1. Navigate to the **"🎲 Monte Carlo Simulation"** tab
2. Configure your simulation parameters:

   | Parameter | Recommended | Range | Purpose |
   |-----------|------------|-------|---------|
   | **Simulations** | 1000 | 1-10,000 | Number of independent runs |
   | **Iterations** | 100 | 1-100,000 | Steps per simulation (time horizon) |
   | **Mean Value** | 0 | -1,000 to 1,000 | Expected value per iteration |
   | **Std Dev** | 1 | 0.01-100 | Variability of draws |
   | **Distribution** | Normal | 3 types | Probability distribution |

3. Click **"🚀 Run Simulation"**
4. Wait for completion (usually 1-10 seconds depending on size)
5. View results in the **"📊 Results & Analysis"** tab

#### Step 4: Analyze Results 📊

Results automatically include:
- **Key Metrics**: Mean, median, standard deviation, min/max
- **Percentiles**: 5th, 25th, 75th, 95th
- **Distribution Shape**: Skewness, kurtosis
- **Configuration Details**: Full parameter audit trail
- **Histogram**: Visual distribution of final values

---

## ⚙️ Configuration

### Parameter Validation Rules

All user inputs are validated server-side:

```python
# Simulations: Integer between 1-10,000
validate_input_value(num_simulations, 'int', (1, 10000))

# Iterations: Integer between 1-100,000
validate_input_value(num_iterations, 'int', (1, 100000))

# Mean: Float between -1,000 and 1,000
validate_input_value(mean_value, 'float', (-1000, 1000))

# Std Dev: Float between 0.01 and 100
validate_input_value(std_dev, 'float', (0.01, 100))

# Distribution: One of ['normal', 'lognormal', 'uniform']
distribution in ['normal', 'lognormal', 'uniform']
```

### Environment Variables

Create a `.env` file for configuration:

```env
# Debug mode (set to True for development)
DASH_DEBUG=False

# Server settings
DASH_HOST=0.0.0.0
DASH_PORT=8050

# Logging level
LOG_LEVEL=INFO
```

### EMEA Countries Supported

The app includes **180+ countries** across three regions:

- **Europe**: 38 countries (Austria, France, Germany, UK, Russia, etc.)
- **Middle East**: 16 countries (Saudi Arabia, UAE, Israel, Turkey, Iran, etc.)
- **Africa**: 54 countries (Egypt, Nigeria, South Africa, Kenya, Morocco, etc.)

See the source code `EMEA_REGIONS` dictionary for the complete list.

---

## 🔬 API & Simulation Engine

### Monte Carlo Simulator Class

```python
from app import MonteCarloSimulator

# Initialize
simulator = MonteCarloSimulator(
    num_simulations=1000,
    num_iterations=100,
    mean_value=0,
    std_dev=1,
    distribution='normal'
)

# Run simulation
result = simulator.run()

# Access results
print(result['statistics'])  # Dict with mean, std_dev, percentiles, etc.
print(result['results']['final_values'])  # Array of final cumulative values
```

### Supported Distributions

#### 1. **Normal (Gaussian)**
- Symmetric bell curve distribution
- Best for: Financial returns, symmetric uncertainties
- Formula: `N(μ, σ²)`

#### 2. **Log-Normal**
- Right-skewed, suitable for positive values
- Best for: Stock prices, asset values, positive growth rates
- Derived from: `exp(Normal(μ', σ'))`

#### 3. **Uniform**
- Equal probability across range
- Best for: Discrete choices, bounded uncertainties
- Range: `[mean - std_dev, mean + std_dev]`

### Statistical Metrics

The simulator calculates:

```python
{
    'mean': float,              # Average of final values
    'median': float,            # 50th percentile
    'std_dev': float,           # Standard deviation
    'min': float,               # Minimum value
    'max': float,               # Maximum value
    'percentile_5': float,      # 5th percentile (VaR 95%)
    'percentile_25': float,     # 25th percentile (Q1)
    'percentile_75': float,     # 75th percentile (Q3)
    'percentile_95': float,     # 95th percentile (VaR 5%)
    'skewness': float,          # Distribution asymmetry
    'kurtosis': float           # Tail heaviness
}
```

**Interpretation:**
- **Skewness**: 
  - Positive: Right-skewed (long right tail)
  - Negative: Left-skewed (long left tail)
  - ~0: Symmetric
- **Kurtosis**:
  - Positive: Heavy tails (more extreme values)
  - Negative: Light tails (fewer extreme values)

### Error Handling

All functions include comprehensive error handling:

```python
def validate_simulation_params(...) -> Tuple[bool, str]:
    """Returns (is_valid, error_message)"""
    # Validates all inputs with specific error messages

def run(...) -> Dict:
    """Returns {'status': 'success'|'error', 'data': {...}, 'message': str}"""
    # Graceful error recovery with logging
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `DASH_DEBUG=False` in environment
- [ ] Use production WSGI server (Gunicorn/Waitress)
- [ ] Enable HTTPS/TLS encryption
- [ ] Configure CORS headers appropriately
- [ ] Set up logging and monitoring
- [ ] Define resource limits (CPU, memory)
- [ ] Configure database backups (if using)
- [ ] Set up health check endpoints

### Deployment Targets

#### **Heroku** (Recommended for small apps)

1. **Create Procfile**
   ```
   web: gunicorn app:server
   ```

2. **Deploy**
   ```bash
   heroku create geomap-simulator
   git push heroku main
   ```

#### **Docker (AWS, GCP, Azure)**

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   RUN apt-get update && apt-get install -y \
       build-essential gdal-bin libgdal-dev
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   
   EXPOSE 8050
   CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:8050"]
   ```

2. **Build and push**
   ```bash
   docker build -t geomap-simulator .
   docker tag geomap-simulator:latest myregistry/geomap-simulator:latest
   docker push myregistry/geomap-simulator:latest
   ```

#### **Render.com** (Simple PaaS)

1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn app:server --bind 0.0.0.0:8050`

#### **AWS EC2**

```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance

# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip gdal-bin libgdal-dev

# Clone repo and install
git clone https://github.com/JulienBechoux/geomap-simulation.git
cd geomap-simulation
pip install -r requirements.txt

# Run with supervisor
sudo systemctl start geomap-simulator
```

### Scaling Considerations

- **NumPy vectorization**: Already optimized for large simulations
- **Caching**: GeoJSON loaded once on startup (`@lru_cache`)
- **Memory**: 10,000 simulations × 100,000 iterations = ~40GB (watch limits)
- **Concurrency**: Use multi-worker Gunicorn: `gunicorn app:server -w 4`
- **CDN**: Serve static assets from CDN for faster loading

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'geopandas'"

**Solution:**
```bash
pip install --upgrade geopandas fiona shapely pyproj
```

System dependencies may be needed:
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev

# macOS
brew install gdal
```

### Issue: "Port 8050 already in use"

**Solution:**
```bash
# Find and kill process using port 8050
lsof -i :8050
kill -9 <PID>

# Or use different port
python app.py --port 8051
```

### Issue: Map doesn't load or shows "Error loading map data"

**Solution:**
1. Verify GeoPandas installation: `python -c "import geopandas; print(geopandas.datasets.get_path('naturalearth_lowres'))"`
2. Check internet connection (first load downloads Natural Earth data)
3. Try clearing browser cache
4. Check console for detailed error messages

### Issue: Simulation very slow or crashes

**Solution:**
- Reduce number of simulations (start with 100)
- Reduce iterations per simulation (start with 10)
- Use server with more RAM for large simulations
- Monitor memory usage: `watch -n 1 free -h`

### Issue: Configuration won't save

**Solution:**
- Check write permissions in current directory
- Use absolute path for configuration files
- Check available disk space
- Review browser console for JavaScript errors

---

## 📊 Example Use Cases

### 1. Financial Risk Assessment
- **Simulations**: 5,000
- **Iterations**: 250 (1-year daily data)
- **Distribution**: Log-Normal
- **Mean**: 0.05 (5% expected return)
- **Std Dev**: 0.15 (15% volatility)
- **Analysis**: Review 95th percentile for Value-at-Risk

### 2. Project Timeline Estimation
- **Simulations**: 1,000
- **Iterations**: 100 (task completion steps)
- **Distribution**: Normal
- **Mean**: 50 (50 days expected)
- **Std Dev**: 10 (±10 day uncertainty)
- **Analysis**: Use 75th percentile for conservative planning

### 3. Geographic Risk Mapping
- **Tag countries** by risk level (Red=High, Yellow=Medium, Green=Low)
- **Run simulation** of economic impact by region
- **Analyze percentiles** for best/worst-case scenarios
- **Export results** for stakeholder reporting

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with clear commit messages
4. **Add tests** for new functionality
5. **Submit a pull request** with description

### Code Style
- Follow PEP 8 conventions
- Add docstrings to all functions
- Include type hints where applicable
- Comment complex logic

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support & Contact

For issues, questions, or suggestions:
- **GitHub Issues**: [geomap-simulation/issues](https://github.com/JulienBechoux/geomap-simulation/issues)
- **Email**: julien_bechoux@goodyear.com

---

## 🙏 Acknowledgments

- **Dash Community**: For the fantastic reactive framework
- **Plotly**: For beautiful geospatial visualizations
- **GeoPandas**: For robust geospatial data handling
- **Natural Earth**: For high-quality geographic data

---

## 🔒 Security & Privacy

- ✅ All computations run server-side (secure)
- ✅ No data stored permanently
- ✅ Input validation on all endpoints
- ✅ Error messages don't expose system details
- ✅ Suitable for enterprise deployment with HTTPS

---

## 📈 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-02 | Initial release with map tagging and Monte Carlo simulation |

---

## 🌟 Future Roadmap

- [ ] Multi-simulation comparison tools
- [ ] Export to Excel/PDF reports
- [ ] Simulation history/versioning
- [ ] Advanced visualizations (3D maps, confidence bands)
- [ ] API for programmatic access
- [ ] Database backend for persistence
- [ ] Real-time collaboration features
- [ ] Machine learning integration

---

**Built with ❤️ for geospatial analysis and probabilistic modeling**
````
