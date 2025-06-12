import json
import os


class PathHelper:
    def __init__(self):
        self.BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        self.DATA = os.path.join(self.BASE_DIR, "data")
        self.APPLICATIONS = os.path.join(self.DATA, "applications")
        self.ENV = os.path.join(self.DATA, "env")
        self.WORKING = os.path.join(self.DATA, "working")
        self.TRACKING_JSON = os.path.join(self.DATA, "tracking.csv")
        self.OPENAI_API_JSON = os.path.join(self.ENV, "OPENAI_API.json")
        self.CREDENTIALS_JSON = os.path.join(self.ENV, "credentials.json")
        self.TOKEN_JSON = os.path.join(self.ENV, "token.json")
        self.EMAIL_TEMPLATE = os.path.join(self.ENV, "EMAIL_TEMPLATE.txt")
        self.JOB_DESCRIPTION = os.path.join(self.WORKING, "JOB_DESCRIPTION.txt")
        self.JOB_URL = os.path.join(self.WORKING, "JOB_URL.txt")
        self.JOB_DESCRIPTION = os.path.join(self.WORKING, "JOB_DESCRIPTION.txt")
        self.RESUME_EXTRACT = os.path.join(self.WORKING, "RESUME_EXTRACT.txt")
        self.RESUME_PDF = os.path.join(self.WORKING, "SoumithReddyPodduturi.pdf")
        self.EMAIL_GENERATED = os.path.join(self.WORKING, "EMAIL_GENERATED.txt")
        self.RECIPIENT_EMAILS = os.path.join(self.WORKING, "RECIPIENT_EMAILS.csv")

    def initialize_resources(self):
        # Create necessary directories
        os.makedirs(self.DATA, exist_ok=True)
        os.makedirs(self.APPLICATIONS, exist_ok=True)
        os.makedirs(self.ENV, exist_ok=True)
        os.makedirs(self.WORKING, exist_ok=True)

        # Move OPENAI_API_KEY from .env to data/env/OPENAI_API_KEY.txt if present
        env_file = os.path.join(self.BASE_DIR, ".env")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                lines = f.readlines()

            new_lines = []
            openai_api_key = None

            for line in lines:
                if line.strip().startswith("OPENAI_API_KEY="):
                    openai_api_key = line.strip().split("=", 1)[1]
                else:
                    new_lines.append(line)

            # ✅ Save to JSON
            os.makedirs(os.path.dirname(self.OPENAI_API_JSON), exist_ok=True)
            with open(self.OPENAI_API_JSON, "w") as f:
                json.dump(
                    {
                        "OPENAI_API_KEY": openai_api_key,
                        "OPENAI_MODEL": "gpt-4o-mini",
                    },
                    f,
                    indent=2,
                )

            # ✅ Rewrite .env without the key
            with open(env_file, "w") as f:
                f.writelines(new_lines)

        # Move credentials.json and token.json to data/env/ if present
        for src, dst in [
            (os.path.join(self.BASE_DIR, "credentials.json"), self.CREDENTIALS_JSON),
            (os.path.join(self.BASE_DIR, "token.json"), self.TOKEN_JSON),
        ]:
            if os.path.exists(src):
                os.replace(src, dst)

        # Move email_template.txt to data/env/EMAIL_TEMPLATE.txt if present
        email_template_src = os.path.join(self.BASE_DIR, "email_template.txt")
        if os.path.exists(email_template_src):
            os.replace(email_template_src, self.EMAIL_TEMPLATE)

        # Create tracking.json if it doesn't exist
        if not os.path.exists(self.TRACKING_JSON):
            with open(self.TRACKING_JSON, "w") as f:
                f.write("{}")
