> **Note**
> This repository contains the improved version of the Gmail Organizer script. The original code and the AI-generated code review report are included for reference.

# Gmail Organizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Automated Email Labeling, Sorting & Migration System for Gmail. This script creates over 80 hierarchical labels, automatically sorts every email in your mailbox, and migrates emails from existing labels into the new, organized hierarchy.

## Features

*   **Automated Label Creation**: Generates a comprehensive, multi-level label hierarchy.
*   **Security Focused**: Uses JSON for token storage, avoiding insecure pickle deserialization.
*   **Robust Error Handling**: Implements exponential backoff with jitter for API rate limits.
*   **Performance Optimized**: Caches labels and uses batch API requests to minimize latency.
*   **Configurable**: Settings can be managed via environment variables.
*   **Structured Logging**: Provides detailed logs for monitoring and debugging.

## Getting Started

### Prerequisites

*   Python 3.9+
*   Google Cloud Project with the Gmail API enabled.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/MIDNGHTSAPPHIRE/gmail-organizer.git
    cd gmail-organizer
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up credentials:**

    *   Follow the instructions in `credentials_setup.md` to obtain your `credentials.json` file.
    *   Place the `credentials.json` file in the root of the project directory.

### Usage

Run the script for the first time to authenticate and create the `token.json` file:

```bash
python3 gmail_organizer.py --create-labels
```

This will open a browser window for you to authorize the application. After authorization, the script will create the complete label hierarchy in your Gmail account.

## Code Review

A comprehensive code review was performed using AI. The full report, which guided the improvements in this version, can be found in `final_code_review.md`.

## Included Files

*   `gmail_organizer.py`: The main, improved application script.
*   `test_gmail_organizer.py`: Test suite for the application.
*   `README.md`: This file.
*   `final_code_review.md`: The AI-generated code review report.
*   `gmail_organizer_original.py`: The original, unimproved script.
*   `credentials_setup.md`: Guide for setting up Google Cloud credentials.
*   `gmail_label_creator.gs`: Google Apps Script for label creation (alternative method).
*   `gmail_filters_expanded.xml`: Example XML for Gmail filter import.
*   `email_directory_structure.md`: Markdown outlining the label structure.
*   `slack_channel_mapping.md`: Document for mapping emails to Slack channels.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
