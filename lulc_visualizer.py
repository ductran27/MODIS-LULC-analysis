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
        """Create land cover statistics visualization (not attempting full raster)"""
        # Note: True MODIS global maps require processing actual raster data (millions of pixels)
        # For this demonstration, we focus on statistical visualization
        
        fig = plt.figure(figsize=(20, 11))
        
        # Main area statistics visualization
        gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], width_ratios=[3, 2])
        
        # Large bar chart of all classes
        ax1 = fig.add_subplot(gs[0, :])
        class_stats = area_results['class_statistics']
        sorted_classes = sorted(class_stats.items(), 
                               key=lambda x: x[1]['area_km2'], reverse=True)
        
        classes = [c[0][:30] for c in sorted_classes]
        areas = [c[1]['area_km2'] for c in sorted_classes]
        colors = [self.LC_COLORS.get(c[0], '#808080') for c in sorted_classes]
        
        bars = ax1.barh(classes, areas, color=colors, alpha=0.85, edgecolor='black', linewidth=0.8)
        ax1.set_xlabel('Area (km²)', fontsize=13, fontweight='bold')
        ax1.set_title(f'MODIS Land Cover Area Distribution - {year}', 
                     fontsize=18, fontweight='bold', pad=15)
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.tick_params(labelsize=10)
        
        # Add percentage labels
        for i, (bar, (class_name, stats)) in enumerate(zip(bars, sorted_classes)):
            width = bar.get_width()
            ax1.text(width * 1.01, bar.get_y() + bar.get_height()/2,
                    f"{stats['percentage']:.1f}%", 
                    va='center', fontsize=9, fontweight='bold')
        
        # Pie chart
        ax2 = fig.add_subplot(gs[1, 0])
        top_5 = sorted_classes[:8]
        labels = [c[0][:20] for c in top_5]
        sizes = [c[1]['percentage'] for c in top_5]
        colors_pie = [self.LC_COLORS.get(c[0], '#808080') for c in top_5]
        
        ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 8})
        ax2.set_title('Top Land Cover Types', fontsize=12, fontweight='bold')
        
        # Summary text
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.axis('off')
        
        summary_text = f"MODIS Land Cover Summary - {year}\n\n"
        summary_text += f"Total Area Sampled: {area_results['total_area_km2']:.0f} km²\n"
        summary_text += f"Total Pixels: {area_results['total_pixels']:,}\n"
        summary_text += f"Land Cover Classes: {area_results['total_classes']}\n\n"
        summary_text += "Top 3 Classes:\n"
        for i, (class_name, stats) in enumerate(sorted_classes[:3], 1):
            summary_text += f"{i}. {class_name[:25]}\n"
            summary_text += f"   {stats['percentage']:.1f}% ({stats['area_km2']:.0f} km²)\n"
        
        ax3.text(0.1, 0.9, summary_text, transform=ax3.transAxes,
                fontsize=11, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        
        filepath = self.plots_dir / f'lc_statistics_{year}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
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
