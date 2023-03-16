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

# Open the file and check the number of columns and test IDs
if (filename.startswith("taskA")): 
    with open(filepath, "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        if len(header) != 3:
            raise ValueError("Task A run file must have 3 columns TestID, SystemOutput1, and SystemOutput2.")
        
        # Check that the first column contains test IDs:
        for row in reader:
            if not (row[0].isdigit()):
                raise ValueError("First column of Task A run file must contain test IDs.")
else:
    if (filename.startswith("taskB") or filename.startswith("taskC")): 
        with open(filepath, "r") as file:
            reader = csv.reader(file)
            header = next(reader)
            if len(header) != 2:
                raise ValueError("Task B/C run file must have 2 columns TestID and SystemOutput.")
            
            # Check that the first column contains test IDs:
            for row in reader:
                if not (row[0].startswith("D2N")):
                    raise ValueError("First column of Task B/C run file must contain test IDs.")

print("Run file is valid.")
