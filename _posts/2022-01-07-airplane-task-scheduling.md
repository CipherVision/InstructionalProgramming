---
layout: post
current: post
cover: "/assets/uploads/new-project.jpg"
navigation: true
title: How To Schedule Recurring Python Scripts in the Cloud With Airplane’s Task-Scheduling
date: 2022-04-06T05:00:00.000+00:00
tags:
- featured
frontpagepost: true
class: post-template
subclass: post
author: jeremiah

---
<p>Python is one of the <a href="https://www.jetbrains.com/lp/devecosystem-2021/">fastest-growing programming languages of 2021</a>, and it's no wonder: it’s ease-of-use and versatility makes it a great choice for any sized project. </p>One of its many use-cases are data extraction and ETL processes. A pain point often encountered is the management of recurring Python scripts outside the local system, i.e. cron tasks; I’ve yet to come across a cloud-based solution that makes the deployment and management of Python scripts an easy process.

That is, until now:

![](/assets/uploads/airplane-cover.png)  
[Airplane](https://www.airplane.dev) is a platform that allows engineers to quickly create internal tools to power recurring workflows within their organization.

Through Airplane, operations where engineers would typically run scripts or SQL queries on behalf of others can be transformed into self-service tools for support, operations, and other teams.

You can read more about Airplane and its use-cases [here]().

In today's guide, we'll be covering the following topics:

* <a href="#setting-up-postgresql">Setting up a PostgreSQL database</a>
* <a href="#setting-up-a-task">Setting up a task in Airplane</a>
* <a href="#pushing-to-postgresql">Pushing PostgreSQL data to Airtable</a>
* <a href="#deploying-to-airplane">Deploying code to Airplane via Airplane’s CLI</a>
* <a href="#scheduling-a-task">Scheduling a recurring task in Airplane</a>

To summarize, we will be creating a Python script that checks a PostgreSQL database for newly-added users and outputs those entries into Airtable; this script will be uploaded to Airplane and then triggered periodically with the help of Airplane’s task-scheduling.

Let’s get started!

<h2 id="setting-up-postgresql">Setting up a PostgreSQL database with Supabase</h2>

For those unfamiliar, Supabase is an open-source Firebase alternative. What this means is you can create an entire backend with ease, including a PostgreSQL database, authentication, APIs, real-time subscriptions and more. They offer a free-tier, which we will be using today.

Provided below is a brief how-to on getting started with a PostgreSQL database in Supabase:

1. Navigate to Supabase and [connect your GitHub account](https://app.supabase.io).
2. Once registered, click **New Project** and fill out the required information.
3. Navigate to the table editor and input dummy data relevant to this guide.
4. Navigate to the project settings and obtain the credentials of the PostgreSQL database for use in our script later.

<h2 id="setting-up-a-task">Setting up a task in Airplane</h2>

To get started, you’ll need to make sure you've [registered for an account](https://app.airplane.dev/signup), if you haven’t already.

Once you're presented with the dashboard, we’ll go ahead and create our first task by clicking **Library** → **New Task**

![](/assets/uploads/new-task.png)

Airplane supports a few different languages out-of-the-box — if these happen to not fit your use-case, you also have the ability to load entire Docker images for maximum usability.

In our case, we'll be using **Python**.

![](/assets/uploads/task-creation.png)

We'll need to give our task a name, so anything will do here! After, click **Continue** → **Create Task**

![](/assets/uploads/init-task.png)

From here, you’re instructed on how to download Airplane’s CLI and the task's project file. For convenience, the following are OS-specific commands needed to download Airplane’s CLI — these can be run from the Terminal (or PowerShell, depending on your OS):

    ** macOS **
    brew install airplanedev/tap/airplane
    airplane login
    
    ** Windows **
    iwr https://github.com/airplanedev/cli/releases/latest/download/install.ps1 -useb | iex
    airplane login
    
    ** Linux **
    curl -L https://github.com/airplanedev/cli/releases/latest/download/install.sh | sh
    airplane login

After the CLI has been downloaded, follow the prompts to authenticate your account.

Once completed, we can then initialize the task’s project files mentioned:

    airplane init --from=postgresql_to_airtable postgresql_to_airtable.task.yaml

Keep in mind, each task will have a slightly different setup of commands (depending on the task's name).

<h2 id="pushing-to-postgresql">Pushing PostgreSQL data to Airtable</h2>

Now that we have the project file downloaded, we can get started. First, we'll need to install a few different Python packages:

    pip install airtable
    pip install requests
    pip install psycopg2-binary

A quick overview:

* **airtable** — this package makes communicating with Airtable's API a breeze.
* **requests** — this package is necessary for the **airtable** package to work properly.
* **psycopg2-binary** — this package is essential to connect to our PostgreSQL database.

Now, we’ll need to obtain an API token from Airtable:

1. Navigate to your [account settings](https://airtable.com/account).
2. Click **Generate API Key**.
3. Save this API key for use in our script.

You'll want to make sure the schema of the table matches that of the database you're retrieving data from — this is considered an essential step so we can seamlessly push data to Airtable.

![](/assets/uploads/airtable.png)

As you can see here, along with the schema, I've added another column into Airtable, **synced_at**, which will be used to track when we have last synced our data — I'll get more into this in a moment.

Provided below is the completed Python script, with a glorious amount of verbosity:

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
            "records"], key=lambda x: datetime.strptime(x["fields"]["synced_at"], "%Y-%m-%dT%H:%M:%S.000Z"), reverse=True)
    
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

Before moving on to deployment, we'll need to create a **requirements.txt** file in the root of the project folder. This text file needs to contain all relevant Python packages Airplane should install before running the script. In our case, the text file will look like this:

    airtable
    requests
    psycopg2-binary

<h2 id="deploying-to-airplane">Deploying code to Airplane via Airplane’s CLI</h2>

Great job! Now that we’ve put together the project files, we can push the task's code to Airplane via Airplane’s CLI:

    airplane deploy postgresql_to_airtable.task.yaml

<h2 id="scheduling-a-task">Scheduling a recurring task in Airplane</h2>

Now that we’ve deployed our task's code to Airplane, we can assign a schedule to run the task at a specific interval. Navigate back to the task in Airplane and click **New schedule**.

![](/assets/uploads/scheduling.png)

For simplicity, we’ll choose _every **hour** at **0 minutes** past the hour_.

The fact that you have the option to specify an interval in cron syntax is also a plus.

Next, click **Create schedule** — and we're done!

For your reference, the completed code repository containing all relevant project files can be found [here](https://github.com/CipherVision/InstructionalProgramming/tree/main/airplane-example).

Airplane does an excellent job at managing and deploying Python scripts to the cloud, and it takes less than 5 minutes to be up and running. For a more in-depth look at Airplane’s capabilities, please take a look at their [official quick-start guide](https://docs.airplane.dev/getting-started/quickstart-guide).

![](/assets/uploads/giphy.gif)

Thanks for reading! We'll see you next time.