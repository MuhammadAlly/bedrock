# Bedrock Nova Lite (Python)

Baseline Python example to call Amazon Bedrock's Nova Lite using the Converse API.

## Prerequisites
- AWS account with access to Bedrock and Nova Lite enabled (Bedrock Console → Model access).
- IAM permission `bedrock:InvokeModel` for the chosen region.
- AWS credentials configured (`aws configure`) or environment variables set.
- Python 3.9+.

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Quick Start
```powershell
# Optional: set region (default us-east-1)
$env:AWS_REGION = "us-east-1"

# Optional: override the model id
$env:BEDROCK_MODEL_ID = "amazon.nova-lite-v1:0"

# Run (replaces the default prompt)
python .\main.py "Write a two-line poem about stargazing."
```

## Dry-Run (no AWS call)
Useful for verifying the script wiring locally.
```powershell
$env:BEDROCK_DRY_RUN = "1"
python .\main.py "Hello Nova Lite"
```

## Notes
- Regions: ensure Nova Lite is available in your selected region (commonly `us-east-1` / `us-west-2`).
- If you see `AccessDeniedException`, check Bedrock Model Access and your IAM policy includes `bedrock:InvokeModel`.
- The code uses the Bedrock `converse` API and expects text results in `response.output.message.content`.
