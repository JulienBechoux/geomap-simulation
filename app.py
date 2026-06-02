"""
GeoMap Simulation App - Interactive mapping and Monte Carlo simulation for Europe, Middle East, and Africa.

This application provides:
- Interactive map with country selection and color tagging
- Country-level data management
- Monte Carlo simulation with configurable parameters
- Results visualization and statistical analysis
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import dash
from dash import dcc, html, Input, Output, State, callback, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import geopandas as gpd
from functools import lru_cache

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================
EMEA_REGIONS = {
    'Europe': [
        'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czechia',
        'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',
        'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Lithuania',
        'Luxembourg', 'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania',
        'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'United Kingdom', 'Switzerland',
        'Norway', 'Serbia', 'Bosnia and Herzegovina', 'Montenegro', 'North Macedonia',
        'Albania', 'Ukraine', 'Belarus', 'Russia', 'Moldova', 'Georgia', 'Armenia'
    ],
    'Middle East': [
        'Bahrain', 'Iran', 'Iraq', 'Israel', 'Jordan', 'Kuwait', 'Lebanon',
        'Oman', 'Qatar', 'Saudi Arabia', 'Syria', 'Turkey', 'United Arab Emirates',
        'West Bank', 'Yemen', 'Palestine'
    ],
    'Africa': [
        'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi',
        'Cameroon', 'Cape Verde', 'Central African Republic', 'Chad', 'Comoros',
        'Congo', 'Democratic Republic of the Congo', 'Djibouti', 'Egypt',
        'Equatorial Guinea', 'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana',
        'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia',
        'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius',
        'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda',
        'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia',
        'South Africa', 'South Sudan', 'Sudan', 'Swaziland', 'Tanzania', 'Togo',
        'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
    ]
}

DEFAULT_COLOR = '#e0e0e0'
COLOR_PALETTE = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#ABEBC6'
]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def validate_input_value(value: any, input_type: str, bounds: Tuple = None) -> bool:
    """
    Validate user input with type checking and bounds validation.
    
    Args:
        value: The value to validate
        input_type: Type of input ('int', 'float', 'string')
        bounds: Optional tuple of (min, max) for numeric values
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if input_type == 'int':
            val = int(value)
            if bounds and (val < bounds[0] or val > bounds[1]):
                return False
            return True
        elif input_type == 'float':
            val = float(value)
            if bounds and (val < bounds[0] or val > bounds[1]):
                return False
            return True
        elif input_type == 'string':
            return isinstance(value, str) and len(value) > 0
        return False
    except (ValueError, TypeError):
        return False


@lru_cache(maxsize=1)
def load_geojson() -> Dict:
    """
    Load GeoJSON data for EMEA regions.
    Uses Natural Earth data via geopandas.
    
    Returns:
        dict: GeoJSON feature collection
    """
    try:
        # Load world data
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        
        # Filter for EMEA countries
        all_countries = []
        for region_countries in EMEA_REGIONS.values():
            all_countries.extend(region_countries)
        
        emea_data = world[world['name'].isin(all_countries)]
        geojson = json.loads(emea_data.to_json())
        
        logger.info(f"Loaded GeoJSON for {len(geojson['features'])} EMEA countries")
        return geojson
    except Exception as e:
        logger.error(f"Error loading GeoJSON: {e}")
        return {}


def get_country_region(country: str) -> Optional[str]:
    """Get the region for a given country."""
    for region, countries in EMEA_REGIONS.items():
        if country in countries:
            return region
    return None


def validate_simulation_params(
    num_simulations: int,
    num_iterations: int,
    mean_value: float,
    std_dev: float,
    distribution: str
) -> Tuple[bool, str]:
    """
    Validate Monte Carlo simulation parameters.
    
    Args:
        num_simulations: Number of simulation runs
        num_iterations: Iterations per simulation
        mean_value: Mean value for distribution
        std_dev: Standard deviation
        distribution: Type of distribution
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    errors = []
    
    if not validate_input_value(num_simulations, 'int', (1, 10000)):
        errors.append("Simulations must be between 1 and 10,000")
    
    if not validate_input_value(num_iterations, 'int', (1, 100000)):
        errors.append("Iterations must be between 1 and 100,000")
    
    if not validate_input_value(mean_value, 'float', (-1000, 1000)):
        errors.append("Mean value must be between -1,000 and 1,000")
    
    if not validate_input_value(std_dev, 'float', (0.01, 100)):
        errors.append("Standard deviation must be between 0.01 and 100")
    
    if distribution not in ['normal', 'lognormal', 'uniform']:
        errors.append("Invalid distribution type")
    
    return (len(errors) == 0, " | ".join(errors))


# ============================================================================
# MONTE CARLO SIMULATION ENGINE
# ============================================================================
class MonteCarloSimulator:
    """Performs Monte Carlo simulations with configurable parameters."""
    
    def __init__(
        self,
        num_simulations: int,
        num_iterations: int,
        mean_value: float,
        std_dev: float,
        distribution: str = 'normal'
    ):
        """
        Initialize the simulator.
        
        Args:
            num_simulations: Number of independent simulations
            num_iterations: Iterations per simulation
            mean_value: Mean of the distribution
            std_dev: Standard deviation
            distribution: Type of distribution (normal, lognormal, uniform)
        """
        self.num_simulations = num_simulations
        self.num_iterations = num_iterations
        self.mean_value = mean_value
        self.std_dev = std_dev
        self.distribution = distribution
        self.results = None
        self.statistics = None
        
    def run(self) -> Dict:
        """
        Execute the Monte Carlo simulation.
        
        Returns:
            dict: Simulation results and statistics
        """
        try:
            logger.info(
                f"Starting Monte Carlo simulation: "
                f"{self.num_simulations} simulations × {self.num_iterations} iterations"
            )
            
            # Generate random samples based on distribution
            if self.distribution == 'normal':
                samples = np.random.normal(
                    self.mean_value,
                    self.std_dev,
                    (self.num_simulations, self.num_iterations)
                )
            elif self.distribution == 'lognormal':
                # For lognormal, use mean/std as parameters
                sigma = np.sqrt(np.log(1 + (self.std_dev / self.mean_value) ** 2))
                mu = np.log(self.mean_value) - sigma ** 2 / 2
                samples = np.random.lognormal(mu, sigma, (self.num_simulations, self.num_iterations))
            else:  # uniform
                lower = self.mean_value - self.std_dev
                upper = self.mean_value + self.std_dev
                samples = np.random.uniform(lower, upper, (self.num_simulations, self.num_iterations))
            
            # Calculate cumulative values for each simulation
            cumulative = np.cumsum(samples, axis=1)
            final_values = cumulative[:, -1]
            
            self.results = {
                'cumulative': cumulative,
                'final_values': final_values,
                'samples': samples
            }
            
            # Calculate statistics
            self._calculate_statistics()
            
            logger.info("Monte Carlo simulation completed successfully")
            return {
                'status': 'success',
                'statistics': self.statistics,
                'results': self.results
            }
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _calculate_statistics(self) -> None:
        """Calculate statistical measures from simulation results."""
        final_values = self.results['final_values']
        
        self.statistics = {
            'mean': float(np.mean(final_values)),
            'median': float(np.median(final_values)),
            'std_dev': float(np.std(final_values)),
            'min': float(np.min(final_values)),
            'max': float(np.max(final_values)),
            'percentile_5': float(np.percentile(final_values, 5)),
            'percentile_25': float(np.percentile(final_values, 25)),
            'percentile_75': float(np.percentile(final_values, 75)),
            'percentile_95': float(np.percentile(final_values, 95)),
            'skewness': float(calculate_skewness(final_values)),
            'kurtosis': float(calculate_kurtosis(final_values))
        }


def calculate_skewness(data: np.ndarray) -> float:
    """Calculate skewness of data distribution."""
    mean = np.mean(data)
    std = np.std(data)
    return np.mean(((data - mean) / std) ** 3)


def calculate_kurtosis(data: np.ndarray) -> float:
    """Calculate kurtosis of data distribution."""
    mean = np.mean(data)
    std = np.std(data)
    return np.mean(((data - mean) / std) ** 4) - 3


# ============================================================================
# DASH APP INITIALIZATION
# ============================================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "GeoMap Monte Carlo Simulation - EMEA"

# Initialize session storage
app.layout = dbc.Container([
    dcc.Store(id='country-colors-store', data={}),
    dcc.Store(id='simulation-results-store', data=None),
    
    # Header
    dbc.Row([
        dbc.Col([
            html.H1(
                "🌍 EMEA GeoMap Monte Carlo Simulator",
                className="my-4 text-center text-primary"
            ),
            html.P(
                "Interactive mapping, country tagging, and probabilistic analysis for Europe, "
                "Middle East, and Africa",
                className="text-center text-muted mb-4"
            )
        ])
    ]),
    
    # Main content tabs
    dbc.Tabs([
        # TAB 1: MAP & TAGGING
        dbc.Tab(
            label="📍 Map & Country Tagging",
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Map Controls", className="card-title"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Select Color:", className="fw-bold"),
                                        dcc.Dropdown(
                                            id='color-selector',
                                            options=[
                                                {'label': '🔴 Red', 'value': '#FF6B6B'},
                                                {'label': '🔵 Blue', 'value': '#4ECDC4'},
                                                {'label': '🟡 Yellow', 'value': '#F7DC6F'},
                                                {'label': '🟣 Purple', 'value': '#BB8FCE'},
                                                {'label': '🟢 Green', 'value': '#ABEBC6'},
                                                {'label': '⚪ Gray', 'value': '#e0e0e0'},
                                            ],
                                            value='#FF6B6B',
                                            clearable=False
                                        )
                                    ], md=6),
                                    
                                    dbc.Col([
                                        html.Label("Selected Country:", className="fw-bold"),
                                        html.Div(
                                            id='selected-country-display',
                                            children="None",
                                            className="p-2 bg-light rounded"
                                        )
                                    ], md=6),
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Button(
                                            "🔄 Reset All Colors",
                                            id='reset-colors-btn',
                                            color="warning",
                                            outline=True,
                                            size="sm",
                                            className="w-100"
                                        )
                                    ], md=6),
                                    
                                    dbc.Col([
                                        dbc.Button(
                                            "💾 Save Configuration",
                                            id='save-config-btn',
                                            color="success",
                                            outline=True,
                                            size="sm",
                                            className="w-100"
                                        )
                                    ], md=6),
                                ]),
                                
                                html.Div(id='save-status', className="text-success mt-2")
                            ])
                        ], className="mb-3")
                    ], md=12, lg=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-map",
                                    type="default",
                                    children=[
                                        dcc.Graph(id='emea-map', style={'height': '600px'})
                                    ]
                                )
                            ])
                        ])
                    ], md=12, lg=9),
                ], className="mb-4"),
                
                # Tagged countries summary
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Tagged Countries Summary")),
                            dbc.CardBody([
                                html.Div(id='tagged-countries-summary')
                            ])
                        ])
                    ])
                ])
            ]
        ),
        
        # TAB 2: MONTE CARLO SIMULATION
        dbc.Tab(
            label="🎲 Monte Carlo Simulation",
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Simulation Parameters")),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Number of Simulations:", className="fw-bold"),
                                        dcc.Input(
                                            id='num-simulations-input',
                                            type='number',
                                            placeholder='e.g., 1000',
                                            value=1000,
                                            min=1,
                                            max=10000,
                                            step=100,
                                            className="form-control"
                                        ),
                                        html.Small(
                                            "Total number of independent Monte Carlo runs (1-10,000)",
                                            className="form-text text-muted"
                                        )
                                    ], md=6, className="mb-3"),
                                    
                                    dbc.Col([
                                        html.Label("Iterations per Simulation:", className="fw-bold"),
                                        dcc.Input(
                                            id='num-iterations-input',
                                            type='number',
                                            placeholder='e.g., 100',
                                            value=100,
                                            min=1,
                                            max=100000,
                                            step=10,
                                            className="form-control"
                                        ),
                                        html.Small(
                                            "Steps per simulation run (1-100,000)",
                                            className="form-text text-muted"
                                        )
                                    ], md=6, className="mb-3"),
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Mean Value:", className="fw-bold"),
                                        dcc.Input(
                                            id='mean-value-input',
                                            type='number',
                                            placeholder='e.g., 0',
                                            value=0,
                                            min=-1000,
                                            max=1000,
                                            step=0.1,
                                            className="form-control"
                                        ),
                                        html.Small(
                                            "Expected value of distribution (-1,000 to 1,000)",
                                            className="form-text text-muted"
                                        )
                                    ], md=6, className="mb-3"),
                                    
                                    dbc.Col([
                                        html.Label("Standard Deviation:", className="fw-bold"),
                                        dcc.Input(
                                            id='std-dev-input',
                                            type='number',
                                            placeholder='e.g., 1',
                                            value=1,
                                            min=0.01,
                                            max=100,
                                            step=0.1,
                                            className="form-control"
                                        ),
                                        html.Small(
                                            "Variability measure (0.01 to 100)",
                                            className="form-text text-muted"
                                        )
                                    ], md=6, className="mb-3"),
                                ]),
                                
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Distribution Type:", className="fw-bold"),
                                        dcc.Dropdown(
                                            id='distribution-selector',
                                            options=[
                                                {'label': 'Normal (Gaussian)', 'value': 'normal'},
                                                {'label': 'Log-Normal', 'value': 'lognormal'},
                                                {'label': 'Uniform', 'value': 'uniform'},
                                            ],
                                            value='normal',
                                            clearable=False
                                        ),
                                        html.Small(
                                            "Select probability distribution for sampling",
                                            className="form-text text-muted"
                                        )
                                    ], md=12, className="mb-3"),
                                ]),
                                
                                html.Div(id='param-validation-error', className="alert alert-warning d-none"),
                                
                                dbc.Button(
                                    "🚀 Run Simulation",
                                    id='run-simulation-btn',
                                    color="primary",
                                    size="lg",
                                    className="w-100 mt-3"
                                ),
                            ])
                        ], className="mb-4")
                    ], md=12, lg=4),
                    
                    dbc.Col([
                        dcc.Loading(
                            id="loading-simulation",
                            type="default",
                            children=[
                                html.Div(id='simulation-status', children="No simulation run yet"),
                                html.Div(id='simulation-results-container')
                            ]
                        )
                    ], md=12, lg=8)
                ])
            ]
        ),
        
        # TAB 3: RESULTS & ANALYSIS
        dbc.Tab(
            label="📊 Results & Analysis",
            children=[
                dbc.Row([
                    dbc.Col([
                        html.Div(id='results-analysis-container')
                    ])
                ])
            ]
        ),
        
        # TAB 4: DOCUMENTATION
        dbc.Tab(
            label="📖 Help & Documentation",
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Getting Started", className="mb-3"),
                                html.H6("1. Map & Country Tagging"),
                                html.P([
                                    "Click on any country in the map to select it. ",
                                    "Choose a color from the dropdown and the country will be tagged. ",
                                    "You can change colors by selecting a different color and clicking another country."
                                ]),
                                
                                html.H6("2. Monte Carlo Simulation", className="mt-3"),
                                html.P([
                                    "Configure simulation parameters and click 'Run Simulation'. ",
                                    "The simulation will generate random samples from your chosen distribution "
                                    "and accumulate them over iterations."
                                ]),
                                
                                html.H6("3. Interpreting Results", className="mt-3"),
                                html.P([
                                    "Review statistical summaries including mean, standard deviation, and percentiles. ",
                                    "Visualizations show distribution shapes and convergence patterns."
                                ]),
                                
                                html.Hr(),
                                
                                html.H5("Parameter Guide", className="mb-3"),
                                dbc.Table([
                                    html.Thead(
                                        html.Tr([
                                            html.Th("Parameter"),
                                            html.Th("Range"),
                                            html.Th("Description")
                                        ])
                                    ),
                                    html.Tbody([
                                        html.Tr([
                                            html.Td("Simulations"),
                                            html.Td("1 - 10,000"),
                                            html.Td("Number of independent Monte Carlo runs")
                                        ]),
                                        html.Tr([
                                            html.Td("Iterations"),
                                            html.Td("1 - 100,000"),
                                            html.Td("Steps per simulation (time horizon)")
                                        ]),
                                        html.Tr([
                                            html.Td("Mean Value"),
                                            html.Td("-1,000 to 1,000"),
                                            html.Td("Expected value of each random draw")
                                        ]),
                                        html.Tr([
                                            html.Td("Std Dev"),
                                            html.Td("0.01 - 100"),
                                            html.Td("Volatility of random draws")
                                        ]),
                                    ])
                                ], bordered=True, hover=True, responsive=True),
                                
                                html.Hr(),
                                
                                html.H5("Distribution Types", className="mb-3"),
                                html.P(html.B("Normal (Gaussian):")),
                                html.P("Symmetric bell curve. Most observations cluster around the mean."),
                                
                                html.P(html.B("Log-Normal:"), className="mt-2"),
                                html.P("Right-skewed. Useful for modeling positive values (prices, returns)."),
                                
                                html.P(html.B("Uniform:"), className="mt-2"),
                                html.P("Equal probability across range [mean - std_dev, mean + std_dev]."),
                            ])
                        ])
                    ])
                ])
            ]
        ),
    ]),
    
    html.Div(id='debug-output', style={'display': 'none'})
], fluid=True, className="mb-5")


# ============================================================================
# CALLBACKS: MAP INTERACTION
# ============================================================================
@callback(
    Output('emea-map', 'figure'),
    Output('selected-country-display', 'children'),
    Input('emea-map', 'clickData'),
    Input('color-selector', 'value'),
    Input('reset-colors-btn', 'n_clicks'),
    State('country-colors-store', 'data'),
    prevent_initial_call=False
)
def update_map(click_data, selected_color, reset_clicks, country_colors):
    """Update map with selected countries and colors."""
    try:
        if not country_colors:
            country_colors = {}
        
        # Handle reset
        ctx = dash.callback_context
        if ctx.triggered and 'reset-colors-btn' in ctx.triggered[0]['prop_id']:
            country_colors = {}
        
        # Handle country selection
        selected_country = "None"
        if click_data and 'points' in click_data and len(click_data['points']) > 0:
            selected_country = click_data['points'][0].get('properties', {}).get('name', 'Unknown')
            if selected_country and selected_country != 'Unknown':
                country_colors[selected_country] = selected_color
        
        # Load GeoJSON
        geojson_data = load_geojson()
        if not geojson_data:
            return go.Figure().add_annotation(text="Error loading map data"), selected_country
        
        # Create color mapping
        country_color_map = {}
        for feature in geojson_data['features']:
            country_name = feature['properties'].get('name', '')
            country_color_map[country_name] = country_colors.get(country_name, DEFAULT_COLOR)
        
        # Create figure
        fig = go.Figure(data=go.Choropleth(
            geojson=geojson_data,
            locations=[f['properties']['name'] for f in geojson_data['features']],
            z=[1] * len(geojson_data['features']),
            marker_line_width=0.5,
            marker_line_color='white',
            colorscale=[[0, '#e0e0e0'], [1, '#e0e0e0']],
            showscale=False,
            hovertemplate='<b>%{locations}</b><extra></extra>',
            customdata=[country_color_map.get(f['properties']['name'], DEFAULT_COLOR) 
                       for f in geojson_data['features']],
            marker=dict(
                line=dict(width=1, color='white'),
                opacity=0.8
            )
        ))
        
        # Apply custom colors
        for i, feature in enumerate(geojson_data['features']):
            country_name = feature['properties']['name']
            color = country_colors.get(country_name, DEFAULT_COLOR)
            
            fig.add_trace(go.Choropleth(
                geojson=geojson_data,
                locations=[country_name],
                z=[1],
                marker_line_width=1.5 if country_name == selected_country else 0.5,
                marker_line_color='darkblue' if country_name == selected_country else 'white',
                colorscale=[[0, color], [1, color]],
                showscale=False,
                hovertemplate=f'<b>{country_name}</b><extra></extra>',
                marker=dict(opacity=0.9)
            ))
        
        fig.update_layout(
            title_text="EMEA Region Interactive Map",
            geo=dict(
                scope='world',
                projection_type='mercator',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastcolor='rgb(204, 204, 204)',
                lonaxis=dict(range=[-15, 60]),
                lataxis=dict(range=[10, 72]),
            ),
            height=600,
            margin=dict(l=0, r=0, t=40, b=0),
            hovermode='closest',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig, selected_country
    
    except Exception as e:
        logger.error(f"Error updating map: {e}")
        return go.Figure().add_annotation(text=f"Error: {str(e)}"), "Error"


@callback(
    Output('country-colors-store', 'data'),
    Output('save-status', 'children'),
    Input('emea-map', 'clickData'),
    Input('color-selector', 'value'),
    Input('reset-colors-btn', 'n_clicks'),
    Input('save-config-btn', 'n_clicks'),
    State('country-colors-store', 'data'),
    prevent_initial_call=False
)
def update_country_store(click_data, selected_color, reset_clicks, save_clicks, country_colors):
    """Update and manage country color storage."""
    try:
        if not country_colors:
            country_colors = {}
        
        ctx = dash.callback_context
        if not ctx.triggered:
            return country_colors, ""
        
        trigger_id = ctx.triggered[0]['prop_id']
        
        if 'reset-colors-btn' in trigger_id:
            return {}, ""
        
        if 'save-config-btn' in trigger_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"config_{timestamp}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(country_colors, f, indent=2)
                message = f"✅ Configuration saved to {filename}"
                logger.info(message)
                return country_colors, message
            except Exception as e:
                logger.error(f"Save error: {e}")
                return country_colors, f"❌ Save failed: {str(e)}"
        
        if click_data and 'points' in click_data and len(click_data['points']) > 0:
            selected_country = click_data['points'][0].get('properties', {}).get('name', '')
            if selected_country:
                country_colors[selected_country] = selected_color
        
        return country_colors, ""
    
    except Exception as e:
        logger.error(f"Error updating store: {e}")
        return country_colors, f"❌ Error: {str(e)}"


@callback(
    Output('tagged-countries-summary', 'children'),
    Input('country-colors-store', 'data')
)
def update_tagged_summary(country_colors):
    """Display summary of tagged countries."""
    try:
        if not country_colors:
            return html.P("No countries tagged yet.", className="text-muted")
        
        # Group by region
        region_colors = {}
        for country, color in country_colors.items():
            region = get_country_region(country)
            if region not in region_colors:
                region_colors[region] = []
            region_colors[region].append((country, color))
        
        # Build summary
        summary_items = []
        for region in sorted(region_colors.keys()):
            countries_list = region_colors[region]
            summary_items.append(
                html.Div([
                    html.H6(f"{region} ({len(countries_list)} countries)", className="mt-2 mb-2"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Badge(
                                country,
                                color="light",
                                text_color="dark",
                                style={'backgroundColor': color, 'color': 'white', 'marginRight': '5px'},
                                className="mb-2"
                            )
                        ], width="auto")
                        for country, color in sorted(countries_list)
                    ], className="g-1")
                ])
            )
        
        return summary_items
    
    except Exception as e:
        logger.error(f"Error updating summary: {e}")
        return html.P(f"Error: {str(e)}", className="text-danger")


# ============================================================================
# CALLBACKS: SIMULATION
# ============================================================================
@callback(
    Output('param-validation-error', 'children'),
    Output('param-validation-error', 'className'),
    Input('run-simulation-btn', 'n_clicks'),
    State('num-simulations-input', 'value'),
    State('num-iterations-input', 'value'),
    State('mean-value-input', 'value'),
    State('std-dev-input', 'value'),
    State('distribution-selector', 'value'),
    prevent_initial_call=True
)
def validate_params(n_clicks, num_sims, num_iters, mean_val, std_dev, dist):
    """Validate simulation parameters."""
    is_valid, error_msg = validate_simulation_params(
        int(num_sims) if num_sims else 0,
        int(num_iters) if num_iters else 0,
        float(mean_val) if mean_val is not None else 0,
        float(std_dev) if std_dev is not None else 0,
        dist or 'normal'
    )
    
    if is_valid:
        return "", "alert alert-warning d-none"
    else:
        return error_msg, "alert alert-warning"


@callback(
    Output('simulation-results-store', 'data'),
    Output('simulation-status', 'children'),
    Input('run-simulation-btn', 'n_clicks'),
    State('num-simulations-input', 'value'),
    State('num-iterations-input', 'value'),
    State('mean-value-input', 'value'),
    State('std-dev-input', 'value'),
    State('distribution-selector', 'value'),
    prevent_initial_call=True
)
def run_simulation(n_clicks, num_sims, num_iters, mean_val, std_dev, dist):
    """Execute Monte Carlo simulation."""
    try:
        is_valid, error_msg = validate_simulation_params(
            int(num_sims) if num_sims else 0,
            int(num_iters) if num_iters else 0,
            float(mean_val) if mean_val is not None else 0,
            float(std_dev) if std_dev is not None else 0,
            dist or 'normal'
        )
        
        if not is_valid:
            return None, html.Div([
                html.Div(f"❌ Validation Error: {error_msg}", className="alert alert-danger")
            ])
        
        # Run simulation
        simulator = MonteCarloSimulator(
            num_simulations=int(num_sims),
            num_iterations=int(num_iters),
            mean_value=float(mean_val),
            std_dev=float(std_dev),
            distribution=dist
        )
        
        result = simulator.run()
        
        if result['status'] == 'success':
            # Convert numpy arrays to lists for JSON serialization
            data = {
                'status': 'success',
                'statistics': result['statistics'],
                'parameters': {
                    'num_simulations': int(num_sims),
                    'num_iterations': int(num_iters),
                    'mean_value': float(mean_val),
                    'std_dev': float(std_dev),
                    'distribution': dist
                },
                'timestamp': datetime.now().isoformat()
            }
            
            status_msg = html.Div([
                html.Div("✅ Simulation completed successfully", className="alert alert-success")
            ])
            
            return data, status_msg
        else:
            return None, html.Div([
                html.Div(f"❌ Simulation error: {result['message']}", className="alert alert-danger")
            ])
    
    except Exception as e:
        logger.error(f"Simulation execution error: {e}")
        return None, html.Div([
            html.Div(f"❌ Error: {str(e)}", className="alert alert-danger")
        ])


@callback(
    Output('simulation-results-container', 'children'),
    Input('simulation-results-store', 'data'),
    prevent_initial_call=True
)
def display_simulation_results(sim_data):
    """Display simulation results."""
    if not sim_data or sim_data.get('status') != 'success':
        return ""
    
    try:
        stats = sim_data['statistics']
        params = sim_data['parameters']
        
        # Create statistics table
        stats_df = pd.DataFrame({
            'Metric': [
                'Mean', 'Median', 'Std Dev', 'Min', 'Max',
                '5th Percentile', '25th Percentile', '75th Percentile', '95th Percentile',
                'Skewness', 'Kurtosis'
            ],
            'Value': [
                f"{stats['mean']:.4f}",
                f"{stats['median']:.4f}",
                f"{stats['std_dev']:.4f}",
                f"{stats['min']:.4f}",
                f"{stats['max']:.4f}",
                f"{stats['percentile_5']:.4f}",
                f"{stats['percentile_25']:.4f}",
                f"{stats['percentile_75']:.4f}",
                f"{stats['percentile_95']:.4f}",
                f"{stats['skewness']:.4f}",
                f"{stats['kurtosis']:.4f}"
            ]
        })
        
        # Create histogram figure
        hist_fig = go.Figure()
        hist_fig.add_trace(go.Histogram(
            x=list(range(int(stats['min']), int(stats['max']) + 1)),
            nbinsx=50,
            name='Distribution',
            marker_color='#4ECDC4'
        ))
        hist_fig.update_layout(
            title="Final Values Distribution (Histogram)",
            xaxis_title="Final Cumulative Value",
            yaxis_title="Frequency",
            height=400,
            hovermode='x unified'
        )
        
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Simulation Parameters")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.P([html.B("Simulations: "), f"{params['num_simulations']:,}"]),
                                html.P([html.B("Iterations: "), f"{params['num_iterations']:,}"]),
                            ], md=6),
                            dbc.Col([
                                html.P([html.B("Distribution: "), params['distribution'].title()]),
                                html.P([html.B("Timestamp: "), sim_data['timestamp']]),
                            ], md=6),
                        ])
                    ])
                ], className="mb-3")
            ], md=12),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Statistical Summary")),
                    dbc.CardBody([
                        dbc.Table.from_dataframe(
                            stats_df,
                            striped=True,
                            bordered=True,
                            hover=True,
                            responsive=True,
                            index=False
                        )
                    ])
                ], className="mb-3")
            ], md=12),
            
            dbc.Col([
                dcc.Graph(figure=hist_fig)
            ], md=12)
        ])
    
    except Exception as e:
        logger.error(f"Error displaying results: {e}")
        return html.Div(f"Error displaying results: {str(e)}", className="alert alert-danger")


@callback(
    Output('results-analysis-container', 'children'),
    Input('simulation-results-store', 'data'),
    prevent_initial_call=True
)
def display_analysis(sim_data):
    """Display comprehensive analysis of simulation results."""
    if not sim_data or sim_data.get('status') != 'success':
        return html.P("No simulation results available. Run a simulation first.", className="text-muted")
    
    try:
        stats = sim_data['statistics']
        params = sim_data['parameters']
        
        # Create comprehensive analysis
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📈 Key Metrics")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("Mean", className="text-muted"),
                                    html.H4(f"{stats['mean']:.4f}", className="text-primary fw-bold")
                                ], className="p-3 text-center bg-light rounded")
                            ], md=4, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H6("Median", className="text-muted"),
                                    html.H4(f"{stats['median']:.4f}", className="text-info fw-bold")
                                ], className="p-3 text-center bg-light rounded")
                            ], md=4, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H6("Std Dev", className="text-muted"),
                                    html.H4(f"{stats['std_dev']:.4f}", className="text-warning fw-bold")
                                ], className="p-3 text-center bg-light rounded")
                            ], md=4, className="mb-3"),
                        ]),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("Min", className="text-muted"),
                                    html.H5(f"{stats['min']:.4f}", className="fw-bold")
                                ], className="p-3 text-center bg-light rounded")
                            ], md=3, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H6("5th Percentile", className="text-muted"),
                                    html.H5(f"{stats['percentile_5']:.4f}", className="fw-bold")
                                ], className="p-3 text-center bg-light rounded")
                            ], md=3, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H6("95th Percentile", className="text-muted"),
                                    html.H5(f"{stats['percentile_95']:.4f}", className="fw-bold")
                                ], className="p-3 text-center bg-light rounded")
                            ], md=3, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H6("Max", className="text-muted"),
                                    html.H5(f"{stats['max']:.4f}", className="fw-bold")
                                ], className="p-3 text-center bg-light rounded")
                            ], md=3, className="mb-3"),
                        ])
                    ])
                ], className="mb-3")
            ], md=12),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📊 Distribution Shape")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("Skewness", className="text-muted"),
                                    html.H5(f"{stats['skewness']:.4f}", className="fw-bold"),
                                    html.Small(
                                        "Positive = right-skewed | Negative = left-skewed | ~0 = symmetric",
                                        className="text-muted"
                                    )
                                ], className="p-3 bg-light rounded")
                            ], md=6, className="mb-3"),
                            
                            dbc.Col([
                                html.Div([
                                    html.H6("Kurtosis", className="text-muted"),
                                    html.H5(f"{stats['kurtosis']:.4f}", className="fw-bold"),
                                    html.Small(
                                        "Positive = heavy tails | Negative = light tails",
                                        className="text-muted"
                                    )
                                ], className="p-3 bg-light rounded")
                            ], md=6, className="mb-3"),
                        ])
                    ])
                ], className="mb-3")
            ], md=12),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("⚙️ Simulation Configuration")),
                    dbc.CardBody([
                        dbc.Table([
                            html.Thead(html.Tr([
                                html.Th("Parameter"),
                                html.Th("Value")
                            ])),
                            html.Tbody([
                                html.Tr([html.Td("Distribution Type"), html.Td(params['distribution'].title())]),
                                html.Tr([html.Td("Mean Value"), html.Td(f"{params['mean_value']:.4f}")]),
                                html.Tr([html.Td("Std Deviation"), html.Td(f"{params['std_dev']:.4f}")]),
                                html.Tr([html.Td("Number of Simulations"), html.Td(f"{params['num_simulations']:,}")]),
                                html.Tr([html.Td("Iterations per Simulation"), html.Td(f"{params['num_iterations']:,}")]),
                                html.Tr([html.Td("Timestamp"), html.Td(sim_data['timestamp'])]),
                            ])
                        ], bordered=True, hover=True, responsive=True)
                    ])
                ])
            ], md=12)
        ])
    
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        return html.Div(f"Error: {str(e)}", className="alert alert-danger")


# Server instance for production deployment
server = app.server

if __name__ == '__main__':
    debug = os.getenv('DASH_DEBUG', 'False').lower() == 'true'
    app.run_server(debug=debug, host='0.0.0.0', port=8050)
