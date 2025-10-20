"""
LULC Analyzer Module
Analyzes land cover area statistics
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path


class LULCAnalyzer:
    """Analyze land cover area coverage statistics"""
    
    # Pixel area at 500m resolution
    PIXEL_AREA_KM2 = 0.25  # 500m x 500m = 0.25 km²
    
    def __init__(self, config):
        """Initialize LULC analyzer"""
        self.config = config
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
    
    def analyze_area_coverage(self, df, year):
        """
        Analyze area coverage by land cover class
        
        Args:
            df: DataFrame with land cover data
            year: Year being analyzed
        
        Returns:
            dict: Area statistics
        """
        results = {}
        results['year'] = year
        results['total_pixels'] = len(df)
        results['total_area_km2'] = len(df) * self.PIXEL_AREA_KM2
        
        # Count pixels per class
        class_counts = df['land_cover_class'].value_counts().to_dict()
        class_names = df.groupby('land_cover_class')['land_cover_name'].first().to_dict()
        
        # Calculate areas
        class_areas = {}
        class_percentages = {}
        
        for lc_class, count in class_counts.items():
            area_km2 = count * self.PIXEL_AREA_KM2
            percentage = (count / len(df)) * 100
            
            class_name = class_names[lc_class]
            class_areas[class_name] = {
                'class_id': int(lc_class),
                'pixel_count': int(count),
                'area_km2': float(area_km2),
                'percentage': float(percentage)
            }
            class_percentages[class_name] = float(percentage)
        
        results['class_statistics'] = class_areas
        results['class_percentages'] = class_percentages
        results['total_classes'] = len(class_counts)
        
        # Dominant classes
        sorted_classes = sorted(class_percentages.items(), 
                               key=lambda x: x[1], reverse=True)
        results['top_5_classes'] = [{'name': name, 'percentage': pct} 
                                    for name, pct in sorted_classes[:5]]
        
        return results
    
    def save_area_results(self, area_results, filepath):
        """Save area analysis results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(area_results, f, indent=2)
