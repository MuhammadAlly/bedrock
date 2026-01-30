import os
import sys
import boto3


def converse_nova_lite(prompt, region=None, model_id=None, temperature=0.7, max_tokens=512, top_p=0.9):
    if os.getenv("BEDROCK_DRY_RUN") == "1":
        return "DRY-RUN: No request sent. Prompt: " + prompt

    region = region or os.getenv("AWS_REGION", "us-east-1")
    model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"temperature": temperature, "maxTokens": max_tokens, "topP": top_p},
    )

    msg = response["output"]["message"]
    parts = [c["text"] for c in msg.get("content", []) if "text" in c]
    return "\n".join(parts) if parts else ""


def main():
    prompt = "Write a short haiku about winter."
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    try:
        text = converse_nova_lite(prompt)
        print(text)
    except Exception as e:
        print("Error: " + str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
