# AIRA - AI Reachout Assistant

A Python-based system for automating the process of sending personalized emails to job opportunities.

## Features

- **Job Description Scraper**: Extracts job details from various job posting websites
- **Email Generator**: Uses OpenAI's GPT models to generate personalized emails based on job descriptions and your resume
- **Email Sender**: Sends emails to multiple recipients with customizable subjects

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/Prashanthkorip/auto-outreach-agent.git
   cd auto-outreach-agent
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Create necessary files:
   - `resume_parsed.txt`: Your resume in text format
   - `email_dataset.csv`: CSV file with recipient email addresses
   - `email_template.txt`: Template for your cold emails
   - `.env`: Environment variables file with your API keys

4. Configure your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

Run the main script:
```
uv run python main.py
```

Follow the prompts to:
1. Enter a job description URL
2. Review the scraped content
3. Confirm sending the generated email
4. Enter a subject line (changing this soon...)

## Project Structure

- `main.py`: Main script that orchestrates the entire process
- `job_scraper.py`: Handles scraping job descriptions from websites
- `email_generator.py`: Generates personalized emails using OpenAI's API
- `email_sender.py`: Sends emails to recipients
- `config.py`: Configuration settings and constants

## License

All rights reserved.
