"""
MODIS Data Retriever Module
Retrieves MODIS Land Cover data for analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path


class MODISRetriever:
    """Retrieve MODIS MCD12Q1 land cover data"""
    
    # IGBP Land Cover Classes
    LAND_COVER_CLASSES = {
        1: 'Evergreen Needleleaf Forest',
        2: 'Evergreen Broadleaf Forest',
        3: 'Deciduous Needleleaf Forest',
        4: 'Deciduous Broadleaf Forest',
        5: 'Mixed Forests',
        6: 'Closed Shrublands',
        7: 'Open Shrublands',
        8: 'Woody Savannas',
        9: 'Savannas',
        10: 'Grasslands',
        11: 'Permanent Wetlands',
        12: 'Croplands',
        13: 'Urban and Built-up',
        14: 'Cropland/Natural Vegetation Mosaic',
        15: 'Snow and Ice',
        16: 'Barren',
        17: 'Water Bodies'
    }
    
    def __init__(self, config):
        """Initialize MODIS data retriever"""
        self.config = config
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
    
    def get_land_cover_data(self, year):
        """
        Retrieve MODIS land cover data for specified year
        
        Args:
            year: int, year to retrieve
        
        Returns:
            pandas.DataFrame: Land cover pixel data
        """
        print(f"  Retrieving MODIS land cover for {year}...")
        
        # Generate sample data representing global land cover
        # In production, this would download actual MODIS MCD12Q1 product
        data = self._generate_sample_land_cover(year)
        
        if data is not None:
            self._save_data(data, year)
        
        return data
    
    def _generate_sample_land_cover(self, year):
        """
        Generate sample land cover data
        Simulates realistic global distribution with temporal changes
        """
        np.random.seed(year)  # Different pattern each year
        
        # Sample many more pixels for better coverage
        n_pixels = 50000  # Increased for better spatial coverage
        
        # Generate global coordinates
        lons = np.random.uniform(-180, 180, n_pixels)
        lats = np.random.uniform(-60, 80, n_pixels)  # Avoid poles
        
        # Assign land cover classes based on latitude (simplified climate zones)
        land_cover = np.zeros(n_pixels, dtype=int)
        
        for i in range(n_pixels):
            lat = lats[i]
            
            # Tropical zone (-23 to 23)
            if -23 <= lat <= 23:
                land_cover[i] = np.random.choice([2, 8, 9, 12, 17], 
                                                 p=[0.3, 0.2, 0.2, 0.2, 0.1])  # Tropical forest, savanna, cropland
            # Temperate zone (23 to 45, -45 to -23)
            elif (23 < lat <= 45) or (-45 <= lat < -23):
                land_cover[i] = np.random.choice([4, 5, 10, 12, 13], 
                                                 p=[0.25, 0.15, 0.25, 0.25, 0.1])  # Deciduous forest, grassland, cropland
            # Boreal zone (45 to 60, -60 to -45)
            elif (45 < lat <= 60) or (-60 <= lat < -45):
                land_cover[i] = np.random.choice([1, 3, 6, 10, 15], 
                                                 p=[0.35, 0.15, 0.2, 0.2, 0.1])  # Needleleaf forest, shrubland
            # Polar/Tundra (60+, -60-)
            else:
                land_cover[i] = np.random.choice([15, 16, 11], 
                                                 p=[0.5, 0.3, 0.2])  # Snow/ice, barren, wetlands
        
        # Add temporal changes based on year (simulate deforestation, urbanization)
        change_factor = (year - 2010) * 0.01  # Small changes over time
        
        # Simulate deforestation: some forest -> cropland/urban
        forest_mask = np.isin(land_cover, [1, 2, 3, 4, 5])
        deforest_chance = 0.02 + change_factor
        to_change = forest_mask & (np.random.random(n_pixels) < deforest_chance)
        land_cover[to_change] = np.random.choice([12, 13], size=to_change.sum(), 
                                                 p=[0.7, 0.3])
        
        # Create DataFrame
        data = {
            'pixel_id': [f'P{year}_{i:05d}' for i in range(n_pixels)],
            'longitude': lons,
            'latitude': lats,
            'land_cover_class': land_cover,
            'land_cover_name': [self.LAND_COVER_CLASSES[lc] for lc in land_cover],
            'year': year
        }
        
        df = pd.DataFrame(data)
        
        return df
    
    def _save_data(self, df, year):
        """Save data to local storage"""
        filename = self.data_dir / f"modis_lc_{year}.csv"
        df.to_csv(filename, index=False)
        print(f"  Saved to {filename}")
