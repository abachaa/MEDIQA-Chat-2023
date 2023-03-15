import csv
import os

filepath = ""

# Check that the file path exists
if not os.path.exists(filepath):
    raise ValueError("File path does not exist")

# Extract the file name from the file path
filename = os.path.basename(filepath)

# Check that the file name starts with "taskA", "taskB", or "taskC"
if not (filename.startswith("taskA") or filename.startswith("taskB") or filename.startswith("taskC")):
    raise ValueError("File name must start with 'taskA', 'taskB', or 'taskC'")

# Check that the file is a CSV file
if not filename.endswith(".csv"):
    raise ValueError("File must be a CSV file")

# Open the file and check that it has 2 columns
with open(filepath, "r") as file:
    reader = csv.reader(file)
    header = next(reader)
    if len(header) != 2:
        raise ValueError("CSV file must have 2 columns")
    
    # Check that the first column contains test IDs:
    for row in reader:
        if not (row[0].startswith("D2N") or row[0].isdigit()):
            raise ValueError("First column must contain test IDs.")

print("File is valid.")
