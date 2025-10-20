#!/usr/bin/env python3
"""
MODIS Global Land Cover Change Analysis System
Analyzes land use and land cover changes across multiple years
"""

import sys
from datetime import datetime
import yaml
from pathlib import Path

from modis_data_retriever import MODISRetriever
from lulc_analyzer import LULCAnalyzer
from change_analyzer import ChangeAnalyzer
from lulc_visualizer import LULCVisualizer


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main execution function"""
    print(f"=== MODIS Land Cover Analysis System ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load configuration
        config = load_config()
        print(f"Configuration loaded")
        
        # Initialize modules
        retriever = MODISRetriever(config['data_sources'])
        analyzer = LULCAnalyzer(config['analysis'])
        change_analyzer = ChangeAnalyzer(config['analysis'])
        visualizer = LULCVisualizer(config['visualization'])
        print(f"Modules initialized")
        
        # Get years to analyze
        years = config['analysis']['years']
        print(f"\nAnalyzing years: {years}")
        
        # Retrieve MODIS land cover data for each year
        print(f"\nRetrieving MODIS land cover data...")
        all_year_data = {}
        for year in years:
            data = retriever.get_land_cover_data(year)
            if data is not None:
                all_year_data[year] = data
                print(f"  {year}: {len(data)} pixels retrieved")
        
        if len(all_year_data) == 0:
            print("No data retrieved. Exiting.")
            return
        
        # Analyze area coverage for each year
        print(f"\nAnalyzing area coverage by land cover class...")
        area_results = {}
        for year, data in all_year_data.items():
            result = analyzer.analyze_area_coverage(data, year)
            area_results[year] = result
            print(f"  {year}: {result['total_classes']} land cover classes")
        
        # Perform multi-year change analysis
        print(f"\nAnalyzing land cover changes over time...")
        change_results = change_analyzer.analyze_changes(all_year_data, years)
        print(f"  Total transitions detected: {change_results['total_transitions']}")
        print(f"  Major changes: {len(change_results['major_changes'])}")
        
        # Generate visualizations
        print(f"\nGenerating visualizations...")
        
        # Global maps for each year
        for year, data in all_year_data.items():
            visualizer.create_global_map(data, area_results[year], year)
            print(f"  Created global map for {year}")
        
        # Time series and change plots
        visualizer.create_temporal_analysis(area_results, change_results)
        print(f"  Created temporal analysis plots")
        
        # Change detection maps
        if len(years) >= 2:
            visualizer.create_change_map(all_year_data, change_results, years[0], years[-1])
            print(f"  Created change detection map")
        
        # Save results
        print(f"\nSaving results...")
        results_dir = Path('results')
        results_dir.mkdir(exist_ok=True)
        
        analyzer.save_area_results(area_results, results_dir / 'area_statistics.json')
        change_analyzer.save_change_results(change_results, results_dir / 'change_analysis.json')
        
        print(f"\n=== Analysis Complete ===")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nResults saved in 'results/' directory")
        print(f"Visualizations saved in 'plots/' directory")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
