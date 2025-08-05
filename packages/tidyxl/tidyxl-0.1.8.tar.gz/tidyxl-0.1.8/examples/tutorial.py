#!/usr/bin/env python3
"""
Step-by-step tutorial for using the tidyxl package
"""

import pandas as pd

from tidyxl import xlsx_cells, xlsx_formats

print("=" * 60)
print("TIDYXL PACKAGE TUTORIAL - Step by Step Guide")
print("=" * 60)

# STEP 1: Create a sample Excel file for demonstration
print("\nSTEP 1: Creating a sample Excel file")
print("-" * 40)

# Create sample data with different data types
employees_data = {
    'Name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown'],
    'Age': [25, 30, 35],
    'Salary': [50000.50, 60000.75, 70000.00],
    'Active': [True, False, True],
    'Start Date': pd.to_datetime(['2020-01-15', '2019-06-01', '2021-03-10'])
}

products_data = {
    'Product': ['Widget A', 'Widget B', 'Widget C'],
    'Price': [10.99, 15.50, 20.00],
    'Stock': [100, 50, 75],
    'Description': ['Small widget', 'Medium widget', 'Large widget']
}

# Create Excel file with formulas and formatting
with pd.ExcelWriter('tutorial_sample.xlsx', engine='openpyxl') as writer:
    df_emp = pd.DataFrame(employees_data)
    df_prod = pd.DataFrame(products_data)

    df_emp.to_excel(writer, sheet_name='Employees', index=False)
    df_prod.to_excel(writer, sheet_name='Products', index=False)

    # Add a summary sheet with formulas
    summary_data = {
        'Metric': ['Total Employees', 'Average Age', 'Total Salary'],
        'Value': ['=COUNTA(Employees.A:A)-1', '=AVERAGE(Employees.B:B)', '=SUM(Employees.C:C)']
    }
    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

print("✓ Created 'tutorial_sample.xlsx' with 3 sheets:")
print("  - Employees: Employee data with various data types")
print("  - Products: Product catalog")
print("  - Summary: Sheet with formulas")

# STEP 2: Basic usage - Read all cells from all sheets
print("\n\nSTEP 2: Basic Usage - Read all cells from all sheets")
print("-" * 50)

# Import all cells from all sheets
all_cells = xlsx_cells('tutorial_sample.xlsx')

print(f"✓ Loaded {len(all_cells)} total cells from all sheets")
print(f"✓ Sheets found: {all_cells['sheet'].unique().tolist()}")
print(f"✓ Data types found: {all_cells['data_type'].unique().tolist()}")

print("\nFirst 5 cells:")
print(all_cells.head()[['sheet', 'address', 'content', 'data_type']].to_string(index=False))

# STEP 3: Read specific sheet only
print("\n\nSTEP 3: Reading a specific sheet")
print("-" * 35)

employees_only = xlsx_cells('tutorial_sample.xlsx', sheets='Employees')
print(f"✓ Loaded {len(employees_only)} cells from 'Employees' sheet only")

# Show only cells with content (exclude blanks)
content_cells = employees_only[employees_only['data_type'] != 'blank']
print("\nEmployees sheet content:")
print(content_cells[['address', 'content', 'data_type']].to_string(index=False))

# STEP 4: Read multiple specific sheets
print("\n\nSTEP 4: Reading multiple specific sheets")
print("-" * 40)

emp_and_prod = xlsx_cells('tutorial_sample.xlsx', sheets=['Employees', 'Products'])
print(f"✓ Loaded {len(emp_and_prod)} cells from Employees and Products sheets")

print("\nBreakdown by sheet:")
sheet_counts = emp_and_prod.groupby('sheet').size()
for sheet, count in sheet_counts.items():
    print(f"  {sheet}: {count} cells")

# STEP 5: Analyzing different data types
print("\n\nSTEP 5: Analyzing different data types")
print("-" * 38)

print("Data type distribution:")
type_counts = all_cells['data_type'].value_counts()
for dtype, count in type_counts.items():
    print(f"  {dtype}: {count} cells")

# Show examples of each data type
print("\nExamples by data type:")
for dtype in all_cells['data_type'].unique():
    if dtype != 'blank':
        example = all_cells[all_cells['data_type'] == dtype].iloc[0]
        print(f"  {dtype}: {example['content']} (at {example['address']})")

# STEP 6: Working with formulas
print("\n\nSTEP 6: Working with formulas")
print("-" * 30)

formula_cells = all_cells[all_cells['data_type'] == 'formula']
if len(formula_cells) > 0:
    print(f"✓ Found {len(formula_cells)} formula cells:")
    for _, cell in formula_cells.iterrows():
        print(f"  {cell['address']}: {cell['content']}")
else:
    print("ℹ No formula cells found in this example")

# STEP 7: Examining cell positions and structure
print("\n\nSTEP 7: Examining cell positions and structure")
print("-" * 45)

# Find headers (typically row 1)
headers = all_cells[(all_cells['row'] == 1) & (all_cells['data_type'] != 'blank')]
print("Header cells (row 1):")
for _, header in headers.iterrows():
    print(f"  {header['sheet']}.{header['address']}: '{header['content']}'")

# Find numeric data
numeric_data = all_cells[all_cells['data_type'] == 'numeric']
print("\nNumeric data summary:")
print(f"  Count: {len(numeric_data)} cells")
if len(numeric_data) > 0:
    values = pd.to_numeric(numeric_data['content'], errors='coerce')
    print(f"  Range: {values.min()} to {values.max()}")
    print(f"  Average: {values.mean():.2f}")

# STEP 8: Getting formatting information
print("\n\nSTEP 8: Getting formatting information")
print("-" * 38)

try:
    formats = xlsx_formats('tutorial_sample.xlsx')
    print("✓ Formatting information extracted:")
    for format_type, format_list in formats.items():
        print(f"  {format_type}: {len(format_list)} entries")

    # Show some font information if available
    if formats['fonts']:
        print("\nFont examples:")
        for i, font in enumerate(formats['fonts'][:3]):  # Show first 3
            print(f"  Font {i}: {font}")

except Exception as e:
    print(f"⚠ Could not extract detailed formatting: {e}")

# STEP 9: Filtering and analyzing specific data
print("\n\nSTEP 9: Filtering and analyzing specific data")
print("-" * 43)

# Filter for specific sheet and data type
employee_text = all_cells[
    (all_cells['sheet'] == 'Employees') &
    (all_cells['data_type'] == 'text')
]
print(f"Text cells in Employees sheet: {len(employee_text)}")

# Find cells in specific columns
column_a_cells = all_cells[all_cells['col'] == 1]  # Column A
print(f"Cells in column A across all sheets: {len(column_a_cells)}")

# Find cells with specific content
name_cells = all_cells[all_cells['content'].astype(str).str.contains('Alice', na=False)]
if len(name_cells) > 0:
    print("Cells containing 'Alice':")
    for _, cell in name_cells.iterrows():
        print(f"  {cell['sheet']}.{cell['address']}: {cell['content']}")

# STEP 10: Converting back to tabular format (bonus)
print("\n\nSTEP 10: Converting back to tabular format (bonus)")
print("-" * 48)

# Example: Reconstruct the Employees table from tidy data
emp_cells = all_cells[
    (all_cells['sheet'] == 'Employees') &
    (all_cells['data_type'] != 'blank')
]

print("Reconstructed Employees table structure:")
print("Original tidy format (first few rows):")
print(emp_cells[['address', 'row', 'col', 'content']].head(8).to_string(index=False))

# Create a pivot to reconstruct tabular format
if len(emp_cells) > 0:
    pivot_table = emp_cells.pivot_table(
        index='row',
        columns='col',
        values='content',
        aggfunc='first'
    ).fillna('')
    print(f"\nReconstructed as table ({pivot_table.shape[0]} rows x {pivot_table.shape[1]} cols):")
    print(pivot_table.to_string())

print("\n" + "=" * 60)
print("TUTORIAL COMPLETE!")
print("=" * 60)
print("\nKey takeaways:")
print("1. Use xlsx_cells(file) to read all cells from all sheets")
print("2. Use sheets parameter to read specific sheets")
print("3. Each cell becomes one row with position, content, and metadata")
print("4. Filter by data_type, sheet, row, col for specific analysis")
print("5. Use xlsx_formats() to get formatting information")
print("6. The tidy format is perfect for complex Excel file analysis!")
