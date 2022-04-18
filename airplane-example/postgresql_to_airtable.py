# Import the necessary packages.
from datetime import datetime
from airtable import airtable
import psycopg2

# Initialization variables — replace these values with what corresponds to your Airtable account and project.
at_token = "..."
at_base_id = "..."
at_table_id = "..."

# Airtable's static date format.
at_date_format = '%Y-%m-%dT%H:%M:%S.000Z'

# Initialize the Airtable client.
at = airtable.Airtable(at_base_id, at_token)

# Prepare query data to be parsed by Airtable
def transform_data(e):
    e["created_at"] = e["created_at"].strftime(at_date_format)
    
    # Append a "synced_at" column to the data (this column only exists in Airtable).
    e["synced_at"] = datetime.utcnow().strftime(at_date_format)
    return e

# The "main" function — an argument should always be present since Airplane calls the function.
def main(params):

    # Capture columns and rows when querying the database.
    columns = []
    rows = []

    # Obtain the last time data was synced by fetching the most recent row's data from Airtable.
    print("Fetching last sync time ...")
    last_sync = sorted(at.get(at_table_id)[
        "records"], key=lambda x: datetime.strptime(x["fields"]["synced_at"], at_date_format), reverse=True)

    # Further transform the variable depending on if data exists in the table or not.
    if len(last_sync) > 0:

        # If so, construct the WHERE clause to obtain results newer than the last sync time.
        last_sync = f""" WHERE created_at > '{last_sync[0]["fields"]["synced_at"]}'"""
        
    else:

        # If not, leave the string empty and select all results from the database.
        last_sync = ""

    # Initialize psycopg2 and connect to the PostgreSQL database. You'll want to replace these values with what corresponds to your database credentials.
    print("Connecting to the database ...")
    with psycopg2.connect(user="...",
                          password="...",
                          host="...",
                          port="...",
                          database="...") as connection:

        # Instantiate the cursor.
        with connection.cursor() as cursor: 

            print("Querying for new entries ...")

            # Execute the query. You'll notice the dynamic bit (corresponding to the WHERE clause) appended at the end.
            cursor.execute(f"SELECT * FROM users{last_sync}")

            # Pass column data to the "columns" variable.
            columns = [desc[0] for desc in cursor.description]
            for row in cursor:

                # Pass row data to the "rows" variable.
                rows.append(row)

    # Handle empty query results.
    if not(len(rows) == 0):
        query_output = []
        for el in rows:

            # Transform the column and row data into one unified list of objects.
            query_output.append({columns[i]: el[i]
                                for i in range(len(columns))})
        
        # Prepare the query output for Airtable.
        parsed_output = list(map(transform_data, query_output))

        # Push each row of data to Airtable, in the specified table ID.
        for row in parsed_output:
            at.create(at_table_id, row)
        print("New entries were successfully pushed to Airtable!")
    else:
        print("No new entries found.")
