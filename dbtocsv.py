# import sqlite3
#
# # Connect to the SQLite database (replace 'your_database.db' with your actual database file)
# db_file = './instance/tracker.db'
# conn = sqlite3.connect(db_file)
# cursor = conn.cursor()
#
# # Query to get all table names in the database
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#
# # Fetch all the table names
# tables = cursor.fetchall()
# print(tables)
# # Print the table names
# for table in tables:
#     print(table[0])
#
# # Close the database connection
# conn.close()



import sqlite3
import csv

# Connect to the SQLite database (replace 'your_database.db' with your actual database file)
db_file = './instance/tracker.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Query to fetch all the data from a table (replace 'your_table_name' with your actual table name)
cursor.execute("SELECT * FROM expenses")

# Get the column headers (field names)
columns = [description[0] for description in cursor.description]

# Open the CSV file for writing
csv_file = 'output_file.csv'  # The output CSV file name
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write the column headers to the CSV file
    writer.writerow(columns)

    # Write all rows of data to the CSV file
    for row in cursor.fetchall():
        writer.writerow(row)

# Close the database connection
conn.close()

print(f"Data successfully written to {csv_file}")

#[('expenses',), ('user',)] are the table names