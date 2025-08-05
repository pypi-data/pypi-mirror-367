#!/usr/bin/env python3
"""
CSV Column Renaming Script

This script renames CSV columns according to the COLUMNS_DICT mapping.
Provide a folder path and it will process all CSV files in that directory and subdirectories.

Usage:
    python naming_script.py <folder_path>
""" 

import os
import sys
import argparse
from pathlib import Path

# Try to import pandas, provide helpful error if not available
try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required but not installed.")
    print("Install it with: pip install pandas")
    sys.exit(1)

COLUMNS_DICT = {
                'gen_speed': 'SN',
                'batt_curr': 'MAP',
                'load_curr': 'MAT',
                'power': 'ECU_voltage',
                'voltage': 'UC_voltage',
                'rectifier_tem': 'MOSFET_temperature',
                'current_setpoint': 'HUB_fuel_pressure',
                'gen_temp': 'generator_temperature',
                'run_time': 'FW',
                'maintenance': 'RC_enable',
                'rpm': 'generator_rpm',
                'fuel_consumed': 'battery_current',
                'fuel_flow': 'fuel_level',
                'engine_load': 'PDU_current',
                'throttle_position': 'ECU_throttle',
                'spark_dwell_time': 'UC_throttle',
                'barometric_pressure': 'ECU_fuel_pressure',
                'intake_manifold_pressure': 'frame_temperature',
                'intake_manifold_temperature': 'CHT_1',
                'cylinder_head_temperature': 'engine_fan_current_1',
                'ignition_timing': 'OAT',
                'injection_time': 'PDU_temperature',
                'exhaust_gas_temperature': 'CHT_2',
                'throttle_out': 'engine_fan_current_2',
                'Pt_compensation': 'PMU_fan_current'}


def find_csv_files(folder_path):
    """Find all CSV files in the specified directory and subdirectories."""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return []
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return []
    
    csv_files = list(folder.rglob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in '{folder_path}' or its subdirectories.")
        return []
    
    print(f"Found {len(csv_files)} CSV file(s) in '{folder_path}':")
    for file in csv_files:
        rel_path = file.relative_to(folder)
        print(f"  - {rel_path}")
    
    return csv_files


def rename_csv_columns(csv_file_path, column_mapping, backup=True):
    """
    Rename columns in a CSV file according to the provided mapping.
    
    Args:
        csv_file_path: Path to the CSV file
        column_mapping: Dictionary mapping old column names to new column names
        backup: Whether to create a backup of the original file
    
    Returns:
        tuple: (success: bool, renamed_count: int)
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        original_columns = df.columns.tolist()
        
        # Create backup if requested
        if backup:
            backup_path = csv_file_path.with_suffix('.csv.backup')
            df.to_csv(backup_path, index=False)
            print(f"  Backup created: {backup_path.name}")
        
        # Apply column renaming
        renamed_columns = []
        renamed_count = 0
        
        for col in df.columns:
            if col in column_mapping:
                new_name = column_mapping[col]
                renamed_columns.append(new_name)
                print(f"    '{col}' -> '{new_name}'")
                renamed_count += 1
            else:
                renamed_columns.append(col)
                print(f"    '{col}' (unchanged)")
        
        # Update column names
        df.columns = renamed_columns

        # Add 'isGeneratorRunning' column if not present
        if 'isGeneratorRunning' not in df.columns:
            # Determine which column to use for RPM (after renaming)
            rpm_col = None
            if 'generator_rpm' in df.columns:
                rpm_col = 'generator_rpm'
            elif 'rpm' in df.columns:
                rpm_col = 'rpm'
            if rpm_col:
                df['isGeneratorRunning'] = (df[rpm_col] > 2000).astype(int)
                print(f"    'isGeneratorRunning' column added (1 if {rpm_col} > 2000, else 0)")
            else:
                print("    Skipped adding 'isGeneratorRunning': no RPM column found.")
        else:
            print("    'isGeneratorRunning' column already exists (unchanged)")

        # Save the updated CSV
        df.to_csv(csv_file_path, index=False)
        
        return True, renamed_count
    
    except Exception as e:
        print(f"  Error processing {csv_file_path.name}: {str(e)}")
        return False, 0


def main():
    """Main function to process all CSV files."""
    parser = argparse.ArgumentParser(description="Rename CSV columns according to predefined schema")
    parser.add_argument("folder_path", help="Path to folder containing CSV files to process")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backup files")
    
    args = parser.parse_args()
    
    print("="*60)
    print("CSV Column Renamer")
    print("="*60)
    
    folder_path = Path(args.folder_path).resolve()
    print(f"Target directory: {folder_path}")
    
    # Find CSV files
    csv_files = find_csv_files(folder_path)
    if not csv_files:
        sys.exit(1)
    
    print(f"\nColumn mapping schema ({len(COLUMNS_DICT)} mappings):")
    for old_name, new_name in COLUMNS_DICT.items():
        print(f"  '{old_name}' -> '{new_name}'")
    
    print(f"\nProcessing CSV files...")
    
    total_files = len(csv_files)
    successful_files = 0
    total_renamed_columns = 0
    
    for csv_file in csv_files:
        rel_path = csv_file.relative_to(folder_path)
        print(f"\nProcessing: {rel_path}")
        
        success, renamed_count = rename_csv_columns(
            csv_file, 
            COLUMNS_DICT, 
            backup=not args.no_backup
        )
        
        if success:
            successful_files += 1
            total_renamed_columns += renamed_count
            print(f"  ✓ Successfully processed ({renamed_count} columns renamed)")
        else:
            print(f"  ✗ Failed to process")
    
    print(f"\n" + "="*60)
    print(f"Summary:")
    print(f"  Files processed: {successful_files}/{total_files}")
    print(f"  Total columns renamed: {total_renamed_columns}")
    
    if successful_files == total_files:
        print(f"  ✓ All files processed successfully!")
    else:
        print(f"  ⚠ {total_files - successful_files} file(s) had errors")
    
    print("="*60)


if __name__ == "__main__":
    main()





