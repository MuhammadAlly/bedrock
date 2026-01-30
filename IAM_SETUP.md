# IAM Setup for Bedrock-only CLI

This guide creates an IAM managed policy (Bedrock-only), an IAM role that uses that policy, an IAM user allowed to assume that role, and a CLI profile that assumes the role.

> Note: IAM users cannot be "assigned" roles. Instead, users assume roles via STS. The user gets permission to call `sts:AssumeRole` on the role.

## Prerequisites
- Admin-level credentials to run IAM commands (temporarily).
- AWS CLI v2 installed.
- Replace placeholders: `<ACCOUNT_ID>`, `<USERNAME>`, `<REGION>` (use `us-east-1` for Nova Lite).

## 1) Create Bedrock policy from iam.json
Using the existing `iam.json` policy in this repo.

```powershell
# From repo root
aws iam create-policy `
  --policy-name BedrockInvokeMinimal `
  --policy-document file://iam.json
```

Record the returned `Policy.Arn`, e.g. `arn:aws:iam::<ACCOUNT_ID>:policy/BedrockInvokeMinimal`.

## 2) Create IAM user and access key (before role)
Create the IAM user first so the trust policy Principal is valid.

```powershell
aws iam create-user --user-name <USERNAME>

# Create programmatic credentials for CLI
aws iam create-access-key --user-name <USERNAME>

# Optional: verify ARN
aws iam get-user --user-name <USERNAME>
```
Capture `AccessKeyId` and `SecretAccessKey` from the output.

## 3) Create role with trust policy
Create a trust policy allowing your IAM user to assume the role.

Create `trust-policy.json` locally with:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::<ACCOUNT_ID>:user/<USERNAME>" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
Then create the role and attach the Bedrock policy:
```powershell
aws iam create-role `
  --role-name BedrockInvokeRole `
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy `
  --role-name BedrockInvokeRole `
  --policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/BedrockInvokeMinimal
```

## 4) Allow the user to assume the role
Create a small inline policy for the user.

Create `user-assume-role.json` locally with:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::<ACCOUNT_ID>:role/BedrockInvokeRole"
    }
  ]
}
```
Attach it:
```powershell
aws iam put-user-policy `
  --user-name <USERNAME> `
  --policy-name AllowAssumeBedrockRole `
  --policy-document file://user-assume-role.json
```

## 5) Configure AWS CLI profiles (Windows)
Set a source profile with the user's access key, then a role profile that automatically assumes the role.

```powershell
# Base creds profile (holds access keys)
aws configure --profile base-<USERNAME>
# Enter Access Key, Secret, region (e.g., us-east-1), output json

# Role profile (auto-assume BedrockInvokeRole)
aws configure set profile.bedrock-dev.role_arn arn:aws:iam::<ACCOUNT_ID>:role/BedrockInvokeRole
aws configure set profile.bedrock-dev.source_profile base-<USERNAME>
aws configure set profile.bedrock-dev.region us-east-1
```

Verify:
```powershell
aws sts get-caller-identity --profile bedrock-dev
```
The returned `Arn` should reflect the assumed role session.

## 6) Run the script with the role profile
```powershell
$env:AWS_PROFILE = "bedrock-dev"
$env:AWS_REGION = "us-east-1"
python .\main.py "Write a two-line poem about stargazing."
```

## Notes & Variations
- You can restrict the trust policy further (e.g., MFA requirement) via `Condition`.
- If you prefer not to use roles yet, you can attach the Bedrock policy directly to the user and skip steps 2 and 4.
- For production, consider IAM Identity Center (SSO) instead of long-lived access keys.
