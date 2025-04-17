from typing import List, Dict, Generator, Optional
from dataclasses import dataclass
from .api import PopulationData
import pandas as pd
from datetime import datetime

@dataclass
class PopulationAnalysis:
    country: str
    start_year: int
    end_year: int
    average_growth_rate: float
    max_population: int
    min_population: int
    total_change: int
    percentage_change: float

def process_population_data(
    data: List[PopulationData]
) -> Generator[PopulationData, None, None]:
    """
    Process population data and yield valid entries.
    
    Args:
        data: List of PopulationData objects
        
    Yields:
        Valid PopulationData objects
    """
    for entry in data:
        if entry.population > 0:
            yield entry

def analyze_population_trends(
    data: List[PopulationData]
) -> PopulationAnalysis:
    """
    Analyze population trends from the given data.
    
    Args:
        data: List of PopulationData objects
        
    Returns:
        PopulationAnalysis object with calculated statistics
    """
    valid_data = list(process_population_data(data))
    
    if not valid_data:
        raise ValueError("No valid population data available for analysis")
    
    # Convert to pandas DataFrame for easier analysis
    df = pd.DataFrame([
        {
            'year': d.year,
            'population': d.population,
            'growth_rate': d.growth_rate
        }
        for d in valid_data
    ])
    
    # Calculate statistics
    avg_growth = df['growth_rate'].mean() if 'growth_rate' in df.columns else 0
    max_pop = df['population'].max()
    min_pop = df['population'].min()
    total_change = max_pop - min_pop
    percentage_change = (total_change / min_pop) * 100 if min_pop > 0 else 0
    
    return PopulationAnalysis(
        country=valid_data[0].country,
        start_year=df['year'].min(),
        end_year=df['year'].max(),
        average_growth_rate=avg_growth,
        max_population=max_pop,
        min_population=min_pop,
        total_change=total_change,
        percentage_change=percentage_change
    )

def filter_by_growth_rate(
    data: List[PopulationData],
    min_growth: Optional[float] = None,
    max_growth: Optional[float] = None
) -> List[PopulationData]:
    """
    Filter population data by growth rate range.
    
    Args:
        data: List of PopulationData objects
        min_growth: Minimum growth rate (optional)
        max_growth: Maximum growth rate (optional)
        
    Returns:
        Filtered list of PopulationData objects
    """
    growth_filter = lambda x: (
        (min_growth is None or x.growth_rate >= min_growth) and
        (max_growth is None or x.growth_rate <= max_growth)
    )
    
    return list(filter(growth_filter, data))

def export_to_csv(
    data: List[PopulationData],
    filename: str
) -> None:
    """
    Export population data to a CSV file.
    
    Args:
        data: List of PopulationData objects
        filename: Output filename
    """
    df = pd.DataFrame([
        {
            'country': d.country,
            'year': d.year,
            'population': d.population,
            'growth_rate': d.growth_rate
        }
        for d in data
    ])
    
    df.to_csv(filename, index=False) 