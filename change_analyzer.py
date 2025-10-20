"""
Change Analyzer Module
Analyzes land cover changes between years
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path


class ChangeAnalyzer:
    """Analyze land cover changes over time"""
    
    def __init__(self, config):
        """Initialize change analyzer"""
        self.config = config
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
    
    def analyze_changes(self, all_year_data, years):
        """
        Analyze land cover changes between years
        
        Args:
            all_year_data: dict of {year: DataFrame}
            years: list of years
        
        Returns:
            dict: Change analysis results
        """
        results = {}
        results['years_analyzed'] = years
        results['total_transitions'] = 0
        results['major_changes'] = []
        
        if len(years) < 2:
            return results
        
        # Compare first and last year
        year_start = years[0]
        year_end = years[-1]
        
        df_start = all_year_data[year_start]
        df_end = all_year_data[year_end]
        
        # Area change by class
        area_changes = self._calculate_area_changes(df_start, df_end, year_start, year_end)
        results['area_changes'] = area_changes
        
        # Identify major transitions
        major_changes = []
        for change in area_changes:
            if abs(change['change_percentage']) > 2:  # >2% change
                major_changes.append(change)
        
        results['major_changes'] = major_changes
        results['total_transitions'] = len(area_changes)
        
        # Overall summary
        total_forest_start = self._calculate_total_forest_area(df_start)
        total_forest_end = self._calculate_total_forest_area(df_end)
        total_urban_start = len(df_start[df_start['land_cover_class'] == 13])
        total_urban_end = len(df_end[df_end['land_cover_class'] == 13])
        
        results['forest_change'] = {
            'start': int(total_forest_start),
            'end': int(total_forest_end),
            'change': int(total_forest_end - total_forest_start),
            'change_pct': float((total_forest_end - total_forest_start) / total_forest_start * 100)
        }
        
        results['urban_change'] = {
            'start': int(total_urban_start),
            'end': int(total_urban_end),
            'change': int(total_urban_end - total_urban_start),
            'change_pct': float((total_urban_end - total_urban_start) / total_urban_start * 100)
        }
        
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _calculate_area_changes(self, df_start, df_end, year_start, year_end):
        """Calculate area changes for each land cover class"""
        changes = []
        
        # Get class counts for each year
        counts_start = df_start['land_cover_name'].value_counts()
        counts_end = df_end['land_cover_name'].value_counts()
        
        # Find all classes
        all_classes = set(counts_start.index) | set(counts_end.index)
        
        for lc_class in all_classes:
            count_start = counts_start.get(lc_class, 0)
            count_end = counts_end.get(lc_class, 0)
            change = count_end - count_start
            
            if count_start > 0:
                change_pct = (change / count_start) * 100
            else:
                change_pct = 100 if count_end > 0 else 0
            
            changes.append({
                'class_name': lc_class,
                'pixels_start': int(count_start),
                'pixels_end': int(count_end),
                'change_pixels': int(change),
                'change_percentage': float(change_pct)
            })
        
        # Sort by absolute change
        changes.sort(key=lambda x: abs(x['change_pixels']), reverse=True)
        
        return changes
    
    def _calculate_total_forest_area(self, df):
        """Calculate total forest area (all forest classes)"""
        forest_classes = [1, 2, 3, 4, 5]  # All forest types
        return len(df[df['land_cover_class'].isin(forest_classes)])
    
    def _generate_summary(self, results):
        """Generate summary of changes"""
        if len(results['major_changes']) == 0:
            return "No major land cover changes detected"
        
        forest_change = results['forest_change']['change_pct']
        urban_change = results['urban_change']['change_pct']
        
        summary = f"Forest change: {forest_change:+.1f}%, Urban change: {urban_change:+.1f}%"
        return summary
    
    def save_change_results(self, change_results, filepath):
        """Save change analysis results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(change_results, f, indent=2)
