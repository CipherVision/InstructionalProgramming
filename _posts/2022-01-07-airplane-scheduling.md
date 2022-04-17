---
layout: post
current: post
cover: "/assets/uploads/new-project.jpg"
navigation: true
title: How To Schedule Recurring Python Scripts in the Cloud With Airplane’s Task-Scheduling
date: 2022-04-06 05:00:00 +0000
tags:
- featured
frontpagepost: true
class: post-template
subclass: post
author: jeremiah

---
Python is one of the [fastest-growing programming languages of 2021](https://www.jetbrains.com/lp/devecosystem-2021/), and it’s no wonder: it’s ease-of-use and versatility makes it a great choice for any sized project. One of its many use-cases are data extraction and ETL processes. A pain point often encountered is the management of recurring Python scripts outside the local system, i.e. cron tasks; I’ve yet to come across a cloud-based solution that makes the deployment and management of Python scripts an easy process.

That is, until now:  
![](/assets/uploads/airplane-cover.png)  
[Airplane](https://www.airplane.dev) is a platform that allows engineers to quickly create internal tools to power recurring workflows within their organization.

Through Airplane, operations where engineers would typically run scripts or SQL queries on behalf of others can be transformed into self-service tools for support, operations, and other teams.

You can read more about Airplane and its use-cases [here]().

In today's guide, we'll be covering the following topics:

* Setting up a PostgreSQL database
* Setting up a task in Airplane
* Pushing PostgreSQL data to Airtable
* Deploying code to Airplane via Airplane’s CLI
* Scheduling a recurring task in Airplane

To summarize, we will be creating a Python script that checks a PostgreSQL database for newly-added users and outputs those entries into Airtable; this script will be uploaded to Airplane and then triggered periodically with the help of Airplane’s task-scheduling.

Let’s get started!

## Setting up a PostgreSQL database with Supabase

For those unfamiliar, Supabase is an open-source Firebase alternative. What this means is you can create an entire backend with ease, including a PostgreSQL database, authentication, APIs, real-time subscriptions and more. They offer a free-tier, which we will be using today.

Let’s navigate to Supabase and register for an account:

Once registered, click **New Project** and fill out the required information.

From here, we’ll navigate to the table editor so we can add in data to work with.

Next, we’ll navigate over to the project settings and obtain the credentials of the PostgreSQL database:

## Setting up a task in Airplane

To get started, you’ll need to register for an account, if you haven’t already: this can be a Google account, GitHub account or just regular email.

Now that we have access to the dashboard, we’ll go ahead and click **Create Task** → **Task**

Airplane supports a few different languages out-of-the-box — if these happen to not fit your use-case, you have the ability to load entire Docker images for maximum usability.

In our case, we will be using **Python**.

From here, you’re instructed on how to download Airplane’s CLI and the task's project file. For convenience, the following are OS-specific commands needed to download Airplane’s CLI:

After the CLI has been downloaded, we’ll need to authenticate our account:

Now, let’s download the task’s project file mentioned:

## Pushing PostgreSQL data to Airtable

Now that we have the project file downloaded, we can get started. First, we’ll need to obtain an API token from Airtable:

Going back to our script, let’s install the **airtable** package — this makes communicating with Airtable’s API a breeze:

Now, we’ll add the main logic to our script (comments included):

\# more details here

Our last step before moving on to deployment is to specify the requirements.txt file in the root of the project folder. This text file needs to contain all relevant Python packages Airplane should install before running the script. In our case, the text file will only contain one line:

## Deploying code to Airplane via Airplane’s CLI

Great job! Now that we’ve put together the project files, we can push the script to Airplane via Airplane’s CLI:

## Scheduling a recurring task in Airplane

Now that we’ve deployed our script to Airplane’s task, we can now assign a schedule to run the task at a specific interval. For simplicity, we’ll assign a daily schedule:

The fact that you have the option to specify the interval in UNIX cron format is also a plus.

For your reference, the following is the completed code repository containing the relevant project files:

Airplane does an excellent job at managing and deploying Python scripts to the cloud, and it takes less than 5 minutes to be up and running. For a more in-depth look at Airplane’s capabilities, please take a look at their [official quick-start guide](https://docs.airplane.dev/getting-started/quickstart-guide).

Thanks for reading! We'll see you next time.