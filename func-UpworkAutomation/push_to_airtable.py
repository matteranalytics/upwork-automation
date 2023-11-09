#!/usr/bin/env python3
import feedparser
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from pyairtable import Api
import numpy as np
import html
import time
import os
import re
import smtplib
from email.mime.text import MIMEText


# You can change how many results you want to get back by changing the paging parameter: &paging=0%3B50 (0 to 50 results)
rss_urls = [
    "https://www.upwork.com/ab/feed/jobs/rss?sort=recency&verified_payment_only=1&q=%28%22data+scientist%22+OR+%22data+analyst%22+OR+%22python+developer%22+OR+%22python+engineer%22+OR+%22python+programmer%22+OR+%22python+script%22+OR+%22machine+learning+developer%22+OR+%22machine+learning+engineer%22%29+AND+NOT+%28%22AWS%22+OR+%22Google+Cloud%22+OR+%22React%22+OR+%22Angular%22+OR+%22Django%22%29&paging=0%3B50&api_params=1&securityToken=caf380ffeb8576e212c4c2df55138ce0ac5943876a813c7e64da76095a9969fe2bc170a4196f2bd78f13e0776080c7cd8730d42dd15f99c791f7c2b3d1312b81&userUid=1210893680552497152&orgUid=1210893680560885761",
    "https://www.upwork.com/ab/feed/jobs/rss?sort=recency&verified_payment_only=1&q=%28%22machine+learning+programmer%22+OR+%22machine+learning+script%22+OR+%22AI+developer%22+OR+%22AI+engineer%22+OR+%22AI+programmer%22+OR+%22AI+script%22+OR+%22ML+developer%22+OR+%22ML+engineer%22+OR+%22ML+programmer%22+OR+%22ML+script%22%29+AND+NOT+%28%22AWS%22+OR+%22Google+Cloud%22+OR+%22React%22+OR+%22Angular%22+OR+%22Django%22%29&paging=0%3B50&api_params=1&securityToken=caf380ffeb8576e212c4c2df55138ce0ac5943876a813c7e64da76095a9969fe2bc170a4196f2bd78f13e0776080c7cd8730d42dd15f99c791f7c2b3d1312b81&userUid=1210893680552497152&orgUid=1210893680560885761",
    "https://www.upwork.com/ab/feed/jobs/rss?sort=recency&verified_payment_only=1&q=%28%22deep+learning+developer%22+OR+%22deep+learning+engineer%22+OR+%22deep+learning+programmer%22+OR+%22deep+learning+script%22+OR+%22forecasting+developer%22+OR+%22forecasting+engineer%22+OR+%22forecasting+programmer%22+OR+%22forecasting+script%22%29+AND+NOT+%28%22AWS%22+OR+%22Google+Cloud%22+OR+%22React%22+OR+%22Angular%22+OR+%22Django%22%29&paging=0%3B50&api_params=1&securityToken=caf380ffeb8576e212c4c2df55138ce0ac5943876a813c7e64da76095a9969fe2bc170a4196f2bd78f13e0776080c7cd8730d42dd15f99c791f7c2b3d1312b81&userUid=1210893680552497152&orgUid=1210893680560885761",
]


def html_to_text(html_string):
    # Unescape HTML characters like &amp; to &
    html_string = html.unescape(html_string)

    # Use BeautifulSoup to convert <br> to newlines and get plain text
    soup = BeautifulSoup(html_string, "html.parser")
    text = soup.get_text("\n")

    return text.strip()


def extract_job_info(entry):
    job_info = {}
    job_info["title"] = entry.title
    job_info["url"] = entry.link

    # Extract description from content
    content = entry.content[0].value
    regex_pattern = "|".join(map(re.escape, ["Hourly Range</b>:", "Budget</b>:"]))
    description = re.split(regex_pattern, content, maxsplit=1)[0]
    job_info["description"] = html_to_text(description)

    # Extract skills, category, country, budget, and hourly range from summary
    content = content.replace("\n", "").replace("&nbsp;", " ").strip()
    skills_match = re.search(r"<b>Skills</b>:(.*?)<br />", content)
    category_match = re.search(r"<b>Category</b>:(.*?)<br />", content)
    country_match = re.search(r"<b>Country</b>:(.*?)<br />", content)
    budget_match = re.search(r"<b>Budget</b>:(.*?)<br />", content)
    hourly_range_match = re.search(r"<b>Hourly Range</b>:(.*?)<br />", content)

    job_info["skills"] = skills_match.group(1).split(",") if skills_match else np.nan
    job_info["category"] = (
        html.unescape(category_match.group(1).strip()) if category_match else np.nan
    )
    job_info["country"] = country_match.group(1).strip() if country_match else np.nan
    job_info["budget"] = budget_match.group(1).strip() if budget_match else np.nan
    job_info["hourly_range"] = (
        hourly_range_match.group(1).strip() if hourly_range_match else np.nan
    )

    published_parsed = entry["published_parsed"]
    date_object = datetime.fromtimestamp(time.mktime(published_parsed))
    job_info["published"] = date_object.strftime("%Y-%m-%d %H:%M:%S")

    return job_info


def send_email(subject, body):
    sender = os.environ["MY_EMAIL"]
    recipient = os.environ["TO_EMAIL"]
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(os.environ["MY_EMAIL"], os.environ["MY_EMAIL_PWD"])
        server.sendmail(sender, [recipient], msg.as_string())


def generate_job_dataframe(rss_urls):
    job_df_list = []
    for url in rss_urls:
        # Parse the RSS feed
        feed = feedparser.parse(url)

        # Extract job information and store it in a DataFrame
        jobs = [extract_job_info(entry) for entry in feed.entries]
        df = pd.DataFrame(jobs)

        # # Adjust currencies
        df["budget"] = df["budget"].apply(
            lambda x: float(x.replace("$", "").replace(",", ""))
            if pd.notna(x)
            else np.nan
        )

        # Split the 'hourly_range' column and expand into new DataFrame
        new_cols = df["hourly_range"].str.split("-", expand=True)
        df["hourly_range_min"] = (
            new_cols[0].str.replace("$", "", regex=False).astype(float)
        )
        df["hourly_range_max"] = (
            new_cols[1].str.replace("$", "", regex=False).astype(float)
        )

        # Handle missing values
        df["budget"] = df["budget"].fillna("")
        df["hourly_range_min"] = df["hourly_range_min"].fillna("")
        df["hourly_range_max"] = df["hourly_range_max"].fillna("")

        # Drop original 'hourly_rate' column
        df.drop("hourly_range", axis=1, inplace=True)

        # Add a column to indicate which RSS feed the job came from
        df["rss_url"] = url

        job_df_list.append(df)

    job_dfs = pd.concat(job_df_list).sort_values("published", ascending=False)

    # Drop duplicate jobs from overlapping searches
    job_dfs = job_dfs.drop_duplicates(subset=["url"])

    return job_dfs


def push_to_airtable():
    df = generate_job_dataframe(rss_urls)

    # Initialize the Airtable API
    # https://pyairtable.readthedocs.io/en/latest/getting-started.html
    api = Api(os.environ["AIRTABLE_ACCESS_TOKEN"])
    table = api.table(os.environ["BASE_ID"], os.environ["TABLE_ID"])

    # There's no way to check for duplicates on Airtbale, so we do it here.
    airtable_data = table.all()
    airtable_df = pd.DataFrame([x["fields"] for x in airtable_data])
    airtable_df = airtable_df.assign(url=airtable_df.get('url', None))
    new_records = df[~df["url"].isin(airtable_df["url"])]

    print(f"Pushing {len(new_records)} new records to Airtable")

    # Create a new record in the "Jobs" table for each job
    # TODO: Fix InvalidJSONError: Out of range float values are not JSON compliant
    for index, row in new_records.iterrows():
        try:
            row_dict = row.to_dict()
            print("-", row_dict)

            table.create(row_dict, True)
        except Exception as e:
            print(e)
            pass
    added_records = len(new_records)
    if added_records > 0:
        send_email("UpWork Automation Job Completed", f"The UpWork Automation job has completed running with {added_records} new records added to the database.")
    else:
        pass
    
    send_email("UpWork Automation Job Completed", f"The UpWork Automation job has completed running with {len(new_records)} new records added to the database.\n You can view the database here: {os.environ['DATABASE_LINK']}")
    
def main():
    pass

if __name__ == "__main__":
   main()