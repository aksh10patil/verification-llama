import json
import torch
from datasets import Dataset

# --- 1. DEFINE OUR GOLDEN TRAINING DATASET ---
training_examples = [
    {
        "task": "triage_classification",
        "input": {"account_id": "acct_2291", "trust_score": 28, "device_new": True, "tor_exit": True, "fast_fill_ms": 140, "cross_network_flag": True, "vertical": "ai_data_labeling"},
        "output": {
            "fraud_hypothesis": "Likely ban-evasion attempt: new device, Tor exit node, and automated 140ms form fill matching a cross-network fraud flag.",
            "recommended_action": "Trigger HumanCheck",
            "confidence_score": 0.96
        }
    },
    {
        "task": "triage_classification",
        "input": {"account_id": "acct_4021", "trust_score": 68, "vpn_exit": True, "canvas_spoofed": True, "password_manager_autofill": True, "fast_fill_ms": 210, "cross_network_flag": False, "vertical": "ai_data_labeling"},
        "output": {
            "fraud_hypothesis": "Legitimate user behavior: privacy tooling (VPN, browser canvas spoofing, password manager) detected, but zero cross-network flags and normal keystroke cadence.",
            "recommended_action": "Allow / Monitor",
            "confidence_score": 0.91
        }
    },
    {
        "task": "rule_compiler",
        "input": {"natural_language_rule": "Step up any checkout from a datacenter IP over $300"},
        "output": {
            "workflow_graph": {
                "when": {"event": "checkout_initiated"},
                "where": {"asn_type": "datacenter"},
                "and": {"transaction_amount_usd": {">": 300}},
                "action": "Trigger HumanCheck"
            }
        }
    }
]

def format_prompt(example):
    """Formats examples into Llama-3.2-3B-Instruct chat template format."""
    if example["task"] == "triage_classification":
        instruction = "You are a Trust & Safety triage copilot for VerifyYou. Ingest the following compressed session telemetry delta and output strict JSON with a 1-sentence fraud hypothesis, recommended action, and confidence score."
    else:
        instruction = "You are a VerifyYou workflow compiler. Translate the plain-English safety rule into a structured When/Where/And JSON workflow condition graph."
        
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>
Input: {json.dumps(example["input"])}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
Output: {json.dumps(example["output"])}<|eot_id|>"""
    return {"text": prompt}

# Convert to HuggingFace Dataset
formatted_data = [format_prompt(ex) for ex in training_examples * 50] # Multiply for demo batching
dataset = Dataset.from_list(formatted_data)
print(f"Generated {len(dataset)} training samples ready for Unsloth.")