from typing import List, Dict, AsyncGenerator, Optional
import aiohttp
import asyncio
from datetime import datetime
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PopulationData:
    country: str
    year: int
    population: int
    growth_rate: Optional[float] = None

class PopulationAPIClient:
    BASE_URL = "https://api.worldbank.org/v2/country"
    
    def __init__(self, rate_limit: int = 10, time_window: int = 1):
        """
        Initialize the API client with rate limiting.
        
        Args:
            rate_limit: Number of requests allowed per time window
            time_window: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.semaphore = asyncio.Semaphore(rate_limit)
        self.last_request_time = datetime.now()
        self.request_count = 0

    async def _rate_limit(self) -> None:
        """Implement rate limiting for API requests."""
        now = datetime.now()
        time_diff = (now - self.last_request_time).total_seconds()
        
        if time_diff >= self.time_window:
            self.request_count = 0
            self.last_request_time = now
        elif self.request_count >= self.rate_limit:
            await asyncio.sleep(self.time_window - time_diff)
            self.request_count = 0
            self.last_request_time = datetime.now()
        
        self.request_count += 1

    async def get_country_population(self, country_code: str, year: int) -> PopulationData:
        """
        Get population data for a specific country and year.
        
        Args:
            country_code: ISO country code
            year: Year to get data for
            
        Returns:
            PopulationData object containing the population information
        """
        async with self.semaphore:
            await self._rate_limit()
            
            url = f"{self.BASE_URL}/{country_code}/indicator/SP.POP.TOTL"
            params = {
                "format": "json",
                "date": str(year)
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data and len(data) > 1 and data[1]:
                                population = data[1][0]['value']
                                return PopulationData(
                                    country=country_code,
                                    year=year,
                                    population=population
                                )
            except Exception as e:
                logger.error(f"Error fetching data for {country_code} in {year}: {str(e)}")
            
            return PopulationData(country=country_code, year=year, population=0)

    async def get_country_population_range(
        self, 
        country_code: str, 
        start_year: int, 
        end_year: int
    ) -> AsyncGenerator[PopulationData, None]:
        """
        Get population data for a country over a range of years.
        
        Args:
            country_code: ISO country code
            start_year: Starting year
            end_year: Ending year
            
        Yields:
            PopulationData objects for each year
        """
        tasks = [
            self.get_country_population(country_code, year)
            for year in range(start_year, end_year + 1)
        ]
        
        for task in asyncio.as_completed(tasks):
            data = await task
            if data.population > 0:  # Only yield valid data
                yield data

    async def calculate_growth_rate(
        self, 
        country_code: str, 
        start_year: int, 
        end_year: int
    ) -> List[PopulationData]:
        """
        Calculate population growth rates for a country over a range of years.
        
        Args:
            country_code: ISO country code
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            List of PopulationData objects with growth rates
        """
        population_data = []
        async for data in self.get_country_population_range(country_code, start_year, end_year):
            population_data.append(data)
        
        # Calculate growth rates
        for i in range(1, len(population_data)):
            prev_pop = population_data[i-1].population
            curr_pop = population_data[i].population
            if prev_pop > 0:
                growth_rate = ((curr_pop - prev_pop) / prev_pop) * 100
                population_data[i].growth_rate = growth_rate
        
        return population_data 