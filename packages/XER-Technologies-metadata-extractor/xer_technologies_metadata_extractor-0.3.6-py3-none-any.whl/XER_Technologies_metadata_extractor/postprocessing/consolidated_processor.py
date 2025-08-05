#!/usr/bin/env python3
"""
Consolidated CSV Post-Processing Script

This script consolidates the functionality of naming_script.py and calculations_script.py
to provide a unified CSV processing pipeline that handles bulk folder processing with
column renaming and value calculations.

Usage:
    python consolidated_processor.py folder_path [options]
"""

import argparse
import pandas as pd
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import time
from datetime import datetime

# Import our custom modules
try:
    from .naming_functions import (
        COLUMNS_DICT,
        find_csv_files,
        create_backup_file,
        rename_columns_and_add_derived,
        validate_renamed_columns
    )
    from .calculation_functions import XERDataCalculator
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure naming_functions.py and calculation_functions.py are in the same directory.")
    sys.exit(1)


class ConsolidatedProcessor:
    """Main processor class that coordinates naming and calculation operations."""
    
    def __init__(self, reference_data_dir: str = "reference_data"):
        """
        Initialize the consolidated processor.
        
        Args:
            reference_data_dir: Path to directory containing reference RPM/power CSV files
        """
        self.calculator = XERDataCalculator(reference_data_dir)
        self.reference_data_loaded = False
        
        # Processing statistics
        self.stats = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_renamed_columns': 0,
            'files_with_calculations': 0,
            'start_time': None,
            'end_time': None
        }
    
    def initialize_reference_data(self) -> bool:
        """
        Load reference data once for all files.
        
        Returns:
            bool: True if reference data loaded successfully
        """
        if not self.reference_data_loaded:
            print("=" * 60)
            print("INITIALIZING REFERENCE DATA")
            print("=" * 60)
            self.reference_data_loaded = self.calculator.load_reference_data()
            print()
        return self.reference_data_loaded
    
    def process_single_csv(self, csv_file_path: Path, backup: bool = True, 
                          filter_power: float = 0, remove_outliers: bool = False,
                          outlier_threshold: float = 3) -> Tuple[bool, Dict]:
        """
        Process a single CSV file with naming and calculations.
        
        Args:
            csv_file_path: Path to the CSV file
            backup: Whether to create backup files
            filter_power: Minimum power threshold for filtering (0 = no filtering)
            remove_outliers: Whether to remove statistical outliers
            outlier_threshold: Z-score threshold for outlier removal
            
        Returns:
            Tuple of (success: bool, file_stats: dict)
        """
        file_stats = {
            'file_path': csv_file_path,
            'renamed_columns': 0,
            'calculations_applied': False,
            'initial_rows': 0,
            'final_rows': 0,
            'error': None
        }
        
        try:
            print(f"\nProcessing: {csv_file_path.name}")
            
            # Read original CSV
            df = pd.read_csv(csv_file_path)
            file_stats['initial_rows'] = len(df)
            print(f"  Original: {len(df)} rows, {len(df.columns)} columns")
            
            # Create backup if requested
            if backup:
                create_backup_file(csv_file_path)
            
            # Step 1: Apply column renaming and add derived columns
            print("  Applying column renaming...")
            df, renamed_count = rename_columns_and_add_derived(df, COLUMNS_DICT)
            file_stats['renamed_columns'] = renamed_count
            
            # Step 2: Validate columns for calculations
            validation = validate_renamed_columns(df)
            print(f"  Column validation:")
            print(f"    - UC Voltage available: {'✓' if validation['uc_voltage_available'] else '✗'}")
            print(f"    - PDU Current available: {'✓' if validation['pdu_current_available'] else '✗'}")
            print(f"    - RPM available: {'✓' if validation['rpm_available'] else '✗'}")
            print(f"    - Throttle available: {'✓' if validation['throttle_available'] else '✗'}")
            
            # Step 3: Apply calculations if possible
            can_calculate_pmu = validation['uc_voltage_available'] and validation['pdu_current_available']
            can_calculate_engine = validation['rpm_available'] and validation['throttle_available']
            
            if can_calculate_pmu or can_calculate_engine:
                print("  Applying calculations...")
                df = self.calculator.process_calculations(df)
                file_stats['calculations_applied'] = True
                
                # Step 4: Apply optional filtering
                if filter_power > 0 and 'PMU_power' in df.columns:
                    print(f"  Applying power filtering (>{filter_power}W)...")
                    df = self.calculator.filter_data_by_power(df, filter_power)
                
                if remove_outliers:
                    print(f"  Removing outliers (threshold={outlier_threshold})...")
                    df = self.calculator.remove_outliers(df, outlier_threshold)
            else:
                print("  Skipping calculations (missing required columns)")
            
            file_stats['final_rows'] = len(df)
            
            # Step 5: Save processed CSV
            df.to_csv(csv_file_path, index=False)
            print(f"  ✓ Saved: {len(df)} rows, {len(df.columns)} columns")
            
            return True, file_stats
            
        except Exception as e:
            error_msg = f"Error processing {csv_file_path.name}: {str(e)}"
            print(f"  ✗ {error_msg}")
            file_stats['error'] = error_msg
            return False, file_stats
    
    def process_folder(self, folder_path: str, backup: bool = True,
                      filter_power: float = 0, remove_outliers: bool = False,
                      outlier_threshold: float = 3) -> Dict:
        """
        Process all CSV files in a folder.
        
        Args:
            folder_path: Path to folder containing CSV files
            backup: Whether to create backup files
            filter_power: Minimum power threshold for filtering (0 = no filtering)
            remove_outliers: Whether to remove statistical outliers
            outlier_threshold: Z-score threshold for outlier removal
            
        Returns:
            Processing statistics dictionary
        """
        self.stats['start_time'] = datetime.now()
        
        print("=" * 60)
        print("CONSOLIDATED CSV PROCESSOR")
        print("=" * 60)
        print(f"Target directory: {Path(folder_path).resolve()}")
        
        # Find CSV files
        csv_files = find_csv_files(folder_path)
        if not csv_files:
            return self.stats
        
        self.stats['total_files'] = len(csv_files)
        
        # Initialize reference data
        self.initialize_reference_data()
        
        # Process each file
        print("=" * 60)
        print("PROCESSING CSV FILES")
        print("=" * 60)
        
        file_results = []
        
        for csv_file in csv_files:
            success, file_stats = self.process_single_csv(
                csv_file, backup, filter_power, remove_outliers, outlier_threshold
            )
            
            file_results.append(file_stats)
            
            if success:
                self.stats['successful_files'] += 1
                self.stats['total_renamed_columns'] += file_stats['renamed_columns']
                if file_stats['calculations_applied']:
                    self.stats['files_with_calculations'] += 1
            else:
                self.stats['failed_files'] += 1
        
        self.stats['end_time'] = datetime.now()
        
        # Generate summary report
        self._generate_summary_report(file_results, folder_path)
        
        return self.stats
    
    def _generate_summary_report(self, file_results: List[Dict], folder_path: str):
        """Generate and display processing summary report."""
        processing_time = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        
        # Overall statistics
        print(f"Folder processed: {folder_path}")
        print(f"Processing time: {processing_time:.1f} seconds")
        print(f"Files found: {self.stats['total_files']}")
        print(f"Files processed successfully: {self.stats['successful_files']}")
        print(f"Files with errors: {self.stats['failed_files']}")
        print(f"Total columns renamed: {self.stats['total_renamed_columns']}")
        print(f"Files with calculations applied: {self.stats['files_with_calculations']}")
        
        # Success rate
        if self.stats['total_files'] > 0:
            success_rate = (self.stats['successful_files'] / self.stats['total_files']) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        # Detailed file results
        if file_results:
            print(f"\nDetailed Results:")
            print(f"{'File':<30} {'Status':<10} {'Renamed':<8} {'Calcs':<6} {'Rows':<12}")
            print("-" * 68)
            
            for result in file_results:
                file_name = result['file_path'].name[:29]  # Truncate long names
                status = "✓ Success" if not result['error'] else "✗ Failed"
                renamed = str(result['renamed_columns'])
                calcs = "✓" if result['calculations_applied'] else "✗"
                rows = f"{result['initial_rows']} → {result['final_rows']}"
                
                print(f"{file_name:<30} {status:<10} {renamed:<8} {calcs:<6} {rows:<12}")
                
                if result['error']:
                    print(f"    Error: {result['error']}")
        
        # Reference data status
        print(f"\nReference Data: {'✓ Loaded' if self.reference_data_loaded else '✗ Fallback mode'}")
        
        print("=" * 60)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Consolidated CSV Post-Processing (Naming + Calculations)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python consolidated_processor.py data/                    # Basic processing
  python consolidated_processor.py data/ --no-backup       # Skip backups
  python consolidated_processor.py data/ --filter-power 500 --remove-outliers
        """
    )
    
    parser.add_argument('folder_path', help='Path to folder containing CSV files to process')
    parser.add_argument('--reference-data-dir', default='reference_data',
                       help='Directory containing reference RPM/power CSV files (default: reference_data)')
    parser.add_argument('--no-backup', action='store_true',
                       help="Don't create backup files")
    parser.add_argument('--filter-power', type=float, default=0,
                       help='Minimum power threshold for filtering (default: 0, no filtering)')
    parser.add_argument('--remove-outliers', action='store_true',
                       help='Remove statistical outliers')
    parser.add_argument('--outlier-threshold', type=float, default=3,
                       help='Z-score threshold for outlier removal (default: 3)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not Path(args.folder_path).exists():
        print(f"Error: Folder '{args.folder_path}' does not exist.")
        sys.exit(1)
    
    # Create processor and run
    processor = ConsolidatedProcessor(args.reference_data_dir)
    
    try:
        stats = processor.process_folder(
            folder_path=args.folder_path,
            backup=not args.no_backup,
            filter_power=args.filter_power,
            remove_outliers=args.remove_outliers,
            outlier_threshold=args.outlier_threshold
        )
        
        # Exit with appropriate code
        if stats['failed_files'] > 0:
            print(f"\nWarning: {stats['failed_files']} file(s) had errors.")
            sys.exit(1)
        else:
            print(f"\n✓ All {stats['successful_files']} file(s) processed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 