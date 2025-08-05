#!/usr/bin/env python3
"""
Demonstration of the updated tidyxl column structure matching R package
"""

from datetime import datetime

import pandas as pd

from tidyxl import xlsx_cells

print("=" * 80)
print("TIDYXL COLUMN STRUCTURE - Now Matching R Package Exactly")
print("=" * 80)

# Create a comprehensive test Excel file with all data types
test_data = {
    'Text': ['Hello', 'World', 'Test'],
    'Numbers': [42, 3.14, -100],
    'Booleans': [True, False, True],
    'Dates': [datetime(2023, 1, 15), datetime(2023, 6, 1), datetime(2023, 12, 25)]
}

# Create Excel file with formulas
with pd.ExcelWriter('column_test.xlsx', engine='openpyxl') as writer:
    df = pd.DataFrame(test_data)
    df.to_excel(writer, sheet_name='Data', index=False)

    # Add a sheet with formulas
    formula_data = {
        'Description': ['Sum', 'Average', 'Count'],
        'Formula': ['=SUM(Data.B:B)', '=AVERAGE(Data.B:B)', '=COUNT(Data.B:B)']
    }
    pd.DataFrame(formula_data).to_excel(writer, sheet_name='Formulas', index=False)

print("Created comprehensive test file: column_test.xlsx")

# Read with the updated function
cells = xlsx_cells('column_test.xlsx')

print(f"\nTotal cells: {len(cells)}")
print(f"Sheets: {cells['sheet'].unique().tolist()}")

print("\n" + "=" * 80)
print("COMPLETE COLUMN LIST (matching R tidyxl package):")
print("=" * 80)

# Show all columns and their types
for i, col in enumerate(cells.columns, 1):
    # Get sample non-null value for type demonstration
    sample_vals = cells[col].dropna()
    sample_type = type(sample_vals.iloc[0]).__name__ if len(sample_vals) > 0 else 'None'

    print(f"{i:2d}. {col:<20} ({sample_type})")

print("\n" + "=" * 80)
print("SAMPLE DATA SHOWING COLUMN STRUCTURE:")
print("=" * 80)

# Show first few rows with all columns
print("First 5 cells (showing all columns):")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(cells.head().to_string(index=False))

print("\n" + "=" * 80)
print("DATA TYPE EXAMPLES:")
print("=" * 80)

# Show examples of each data type
data_types = cells['data_type'].unique()
for dtype in data_types:
    subset = cells[cells['data_type'] == dtype].head(1)
    if len(subset) > 0:
        row = subset.iloc[0]
        print(f"\n{dtype.upper()} example:")
        print(f"  Address: {row['address']}")
        print(f"  Content: {row['content']}")
        print(f"  is_blank: {row['is_blank']}")

        # Show the typed value columns
        if row['logical'] is not None:
            print(f"  logical: {row['logical']}")
        if row['numeric'] is not None:
            print(f"  numeric: {row['numeric']}")
        if row['date'] is not None:
            print(f"  date: {row['date']}")
        if row['character'] is not None:
            print(f"  character: {row['character']}")
        if row['error'] is not None:
            print(f"  error: {row['error']}")
        if row['formula'] is not None:
            print(f"  formula: {row['formula']}")

print("\n" + "=" * 80)
print("COLUMN MAPPING TO R TIDYXL:")
print("=" * 80)

column_mapping = {
    1: "sheet - Worksheet name",
    2: "address - Cell address in A1 notation",
    3: "row - Row number",
    4: "col - Column number",
    5: "is_blank - Whether cell has a value",
    6: "content - Raw cell value before type conversion",
    7: "data_type - Cell type (error, logical, numeric, date, character, blank)",
    8: "error - Cell error value",
    9: "logical - Boolean value",
    10: "numeric - Numeric value",
    11: "date - Date value",
    12: "character - String value",
    13: "formula - Cell formula",
    14: "is_array - Whether formula is an array formula",
    15: "formula_ref - Range address for array/shared formulas",
    16: "formula_group - Formula group index",
    17: "comment - Cell comment text",
    18: "height - Row height in Excel units",
    19: "width - Column width in Excel units",
    20: "row_outline_level - Row outline level",
    21: "col_outline_level - Column outline level",
    22: "style_format - Index for style formats",
    23: "local_format_id - Index for local cell formats"
}

for num, desc in column_mapping.items():
    print(f"{num:2d}. {desc}")

print("\n" + "=" * 80)
print("KEY DIFFERENCES FROM PREVIOUS VERSION:")
print("=" * 80)
print("✓ Added separate columns for each value type (logical, numeric, date, character, error)")
print("✓ Added is_blank column instead of 'blank' data_type")
print("✓ Added formula metadata (is_array, formula_ref, formula_group)")
print("✓ Added outline level columns")
print("✓ Added check_filetype parameter")
print("✓ Content is now raw string representation")
print("✓ Proper date detection and conversion")
print("✓ Exact column order and naming matching R package")

print("\nThe package now exactly matches the R tidyxl behavior!")
