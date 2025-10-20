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
        """Create global land cover map showing spatial distribution"""
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection=ccrs.Robinson())
        
        ax.set_global()
        
        # Add geographic features
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='#333333')
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='#666666', alpha=0.5)
        ax.add_feature(cfeature.OCEAN, facecolor='#E0F3F8')
        
        # Plot land cover pixels with proper colors
        for lc_class in sorted(df['land_cover_class'].unique()):
            class_data = df[df['land_cover_class'] == lc_class]
            lc_name = class_data['land_cover_name'].iloc[0]
            color = self.LC_COLORS.get(lc_name, '#808080')
            
            ax.scatter(class_data['longitude'], class_data['latitude'],
                      c=color, s=8, alpha=0.8, edgecolors='none',
                      transform=ccrs.PlateCarree(), rasterized=True,
                      label=lc_name if len(class_data) > 100 else None)
        
        # Title
        ax.set_title(f'MODIS Global Land Cover Classification - {year}', 
                    fontsize=18, fontweight='bold', pad=20)
        
        # Create custom legend with all classes
        legend_elements = []
        for lc_name, color in self.LC_COLORS.items():
            if lc_name in df['land_cover_name'].values:
                legend_elements.append(mpatches.Patch(color=color, label=lc_name))
        
        # Place legend outside plot
        ax.legend(handles=legend_elements[:12], loc='lower left', 
                 fontsize=8, ncol=2, frameon=True, framealpha=0.95,
                 title='Land Cover Classes', title_fontsize=9)
        
        plt.tight_layout()
        
        filepath = self.plots_dir / f'global_lc_map_{year}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Also create area statistics chart
        self._create_area_chart(area_results, year)
        
        return filepath
    
    def _create_area_chart(self, area_results, year):
        """Create separate area statistics chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Pie chart
        top_classes = area_results['top_5_classes'][:10]
        labels = [c['name'][:20] for c in top_classes]
        values = [c['percentage'] for c in top_classes]
        colors = [self.LC_COLORS.get(top_classes[i]['name'], '#808080') 
                 for i in range(len(top_classes))]
        
        ax1.pie(values, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 9})
        ax1.set_title(f'Land Cover Distribution - {year}', fontsize=14, fontweight='bold')
        
        # Bar chart
        ax2.barh(labels, values, color=colors, alpha=0.8, edgecolor='black')
        ax2.set_xlabel('Coverage (%)', fontsize=11)
        ax2.set_title('Top Land Cover Classes', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        filepath = self.plots_dir / f'area_stats_{year}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
    
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
        """Create change comparison chart showing land cover transitions"""
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Get major changes
        changes = change_results['area_changes'][:12]  # Top 12 changes
        
        class_names = [c['class_name'][:30] for c in changes]
        pixels_start = [c['pixels_start'] for c in changes]
        pixels_end = [c['pixels_end'] for c in changes]
        
        x = np.arange(len(class_names))
        width = 0.35
        
        # Create grouped bar chart
        bars1 = ax.barh(x - width/2, pixels_start, width, label=f'{year_start}',
                       color='steelblue', alpha=0.8, edgecolor='black')
        bars2 = ax.barh(x + width/2, pixels_end, width, label=f'{year_end}',
                       color='coral', alpha=0.8, edgecolor='black')
        
        ax.set_ylabel('Land Cover Class', fontsize=12)
        ax.set_xlabel('Pixel Count', fontsize=12)
        ax.set_title(f'Land Cover Change Comparison: {year_start} vs {year_end}', 
                    fontsize=16, fontweight='bold')
        ax.set_yticks(x)
        ax.set_yticklabels(class_names, fontsize=10)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add change indicators
        for i, change in enumerate(changes):
            change_pct = change['change_percentage']
            if abs(change_pct) > 2:
                color = 'green' if change_pct > 0 else 'red'
                ax.text(max(pixels_start[i], pixels_end[i]) * 1.02, i,
                       f'{change_pct:+.1f}%', va='center',
                       color=color, fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        
        filepath = self.plots_dir / f'change_comparison_{year_start}_{year_end}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
