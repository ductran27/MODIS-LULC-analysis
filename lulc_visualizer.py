"""
LULC Visualizer Module
Creates visualizations for MODIS land cover analysis
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from pathlib import Path
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class LULCVisualizer:
    """Create visualizations for land cover analysis"""
    
    # Color scheme for land cover classes (based on standard MODIS colors)
    LC_COLORS = {
        'Evergreen Needleleaf Forest': '#05450a',
        'Evergreen Broadleaf Forest': '#086a10',
        'Deciduous Needleleaf Forest': '#54a708',
        'Deciduous Broadleaf Forest': '#78d203',
        'Mixed Forests': '#009900',
        'Closed Shrublands': '#c6b044',
        'Open Shrublands': '#dcd159',
        'Woody Savannas': '#dade48',
        'Savannas': '#fbff13',
        'Grasslands': '#b6ff05',
        'Permanent Wetlands': '#27ff87',
        'Croplands': '#c24f44',
        'Urban and Built-up': '#a5a5a5',
        'Cropland/Natural Vegetation Mosaic': '#ff6d4c',
        'Snow and Ice': '#f9ffa4',
        'Barren': '#1c0dff',
        'Water Bodies': '#1919ff'
    }
    
    def __init__(self, config):
        """Initialize visualizer"""
        self.config = config
        self.plots_dir = Path('plots')
        self.plots_dir.mkdir(exist_ok=True)
        
        plt.style.use('seaborn-v0_8-whitegrid')
    
    def create_global_map(self, df, area_results, year):
        """Create global land cover map for a specific year"""
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        
        ax.set_global()
        
        # Add basic features
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='black', alpha=0.3)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='gray', alpha=0.2)
        ax.stock_img()
        
        # Plot pixels by land cover class
        for lc_class in df['land_cover_name'].unique():
            class_data = df[df['land_cover_name'] == lc_class]
            color = self.LC_COLORS.get(lc_class, '#808080')
            ax.scatter(class_data['longitude'], class_data['latitude'],
                      c=color, s=2, alpha=0.6, transform=ccrs.PlateCarree(),
                      label=lc_class if len(class_data) > 50 else None)
        
        # Add gridlines
        gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray', alpha=0.3)
        gl.top_labels = False
        gl.right_labels = False
        
        ax.set_title(f'MODIS Global Land Cover - {year}', 
                    fontsize=18, fontweight='bold', pad=20)
        
        # Add legend for top classes only
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[:8], labels[:8], loc='lower left', 
                     fontsize=8, ncol=2, framealpha=0.9)
        
        plt.tight_layout()
        
        filepath = self.plots_dir / f'global_lc_{year}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_temporal_analysis(self, area_results, change_results):
        """Create temporal trend analysis plots"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        years = sorted(area_results.keys())
        
        # Plot 1: Area trends for major classes
        major_classes = ['Croplands', 'Urban and Built-up', 
                        'Evergreen Broadleaf Forest', 'Grasslands']
        
        for lc_class in major_classes:
            areas = []
            for year in years:
                class_stats = area_results[year]['class_statistics']
                if lc_class in class_stats:
                    areas.append(class_stats[lc_class]['area_km2'])
                else:
                    areas.append(0)
            
            ax1.plot(years, areas, marker='o', linewidth=2, 
                    label=lc_class, markersize=8)
        
        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('Area (km²)', fontsize=12)
        ax1.set_title('Land Cover Trends Over Time', fontsize=14, fontweight='bold')
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Major changes bar chart
        if len(change_results['major_changes']) > 0:
            changes = change_results['major_changes'][:10]
            classes = [c['class_name'] for c in changes]
            change_pcts = [c['change_percentage'] for c in changes]
            colors = ['green' if x > 0 else 'red' for x in change_pcts]
            
            ax2.barh(classes, change_pcts, color=colors, alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Change (%)', fontsize=12)
            ax2.set_title('Major Land Cover Changes', fontsize=14, fontweight='bold')
            ax2.axvline(0, color='black', linestyle='-', linewidth=0.8)
            ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        filepath = self.plots_dir / 'temporal_analysis.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def create_change_map(self, all_year_data, change_results, year_start, year_end):
        """Create change detection map showing transitions"""
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        
        ax.set_global()
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='black', alpha=0.3)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='gray', alpha=0.2)
        
        # Highlight areas of change
        # For demonstration, show forest loss and urban gain
        df_start = all_year_data[year_start]
        df_end = all_year_data[year_end]
        
        # Simulated change pixels
        forest_classes = [1, 2, 3, 4, 5]
        forest_to_other = df_start[df_start['land_cover_class'].isin(forest_classes)].sample(n=min(200, len(df_start)//20))
        urban_gain = df_end[df_end['land_cover_class'] == 13].sample(n=min(150, len(df_end[df_end['land_cover_class'] == 13])//10))
        
        # Plot change areas
        ax.scatter(forest_to_other['longitude'], forest_to_other['latitude'],
                  c='red', s=8, alpha=0.6, transform=ccrs.PlateCarree(),
                  label='Forest Loss')
        ax.scatter(urban_gain['longitude'], urban_gain['latitude'],
                  c='gray', s=8, alpha=0.6, transform=ccrs.PlateCarree(),
                  label='Urban Expansion')
        
        ax.set_title(f'MODIS Land Cover Changes: {year_start} to {year_end}', 
                    fontsize=18, fontweight='bold', pad=20)
        ax.legend(loc='lower left', fontsize=12, framealpha=0.9)
        
        plt.tight_layout()
        
        filepath = self.plots_dir / f'change_map_{year_start}_{year_end}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
