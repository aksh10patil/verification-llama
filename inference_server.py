import json
from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="VerifyYou Triage Copilot API", version="1.0.0")

# --- 1. DEFINE STRICT OUTPUT SCHEMAS (Pydantic / Instructor Pattern) ---
class TriageResponse(BaseModel):
    fraud_hypothesis: str = Field(..., description="1-sentence plain-English explanation of the risk pattern.")
    recommended_action: str = Field(..., description="Must be one of: Trigger HumanCheck, Batch for 30-day Re-verify, Allow / Monitor")
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class RuleCompilerResponse(BaseModel):
    workflow_graph: Dict[str, Any] = Field(..., description="Structured When/Where/And visual workflow condition graph.")

class TriageRequest(BaseModel):
    account_id: str
    feature_deltas: Dict[str, Any]

class RuleRequest(BaseModel):
    natural_language_rule: str


# --- 2. MOCK LLM INFERENCE WITH STRUCTURED OUTPUT GUARANTEE ---
# (In production, this calls vLLM / Outlines with grammar-constrained decoding)
def run_constrained_llm_triage(payload: Dict[str, Any]) -> TriageResponse:
    trust_score = payload.get("trust_score", 100)
    tor_exit = payload.get("tor_exit", False)
    cross_net = payload.get("cross_network_flag", False)
    fast_fill = payload.get("fast_fill_ms", 500)
    
    # Deterministic fallback guardrails + LLM reasoning simulation
    if tor_exit and cross_net and fast_fill < 200:
        hypothesis = f"Likely ban-evasion attempt: new device + Tor exit node + automated {fast_fill}ms form fill matching cross-network fraud flag."
        action = "Trigger HumanCheck"
        confidence = 0.96
    elif trust_score < 40:
        hypothesis = f"High-risk account state: trust score severely degraded ({trust_score}) with anomalous session parameters."
        action = "Trigger HumanCheck"
        confidence = 0.89
    else:
        hypothesis = "Standard user behavior: normal telemetry patterns with no active cross-network abuse indicators."
        action = "Allow / Monitor"
        confidence = 0.92
        
    return TriageResponse(
        fraud_hypothesis=hypothesis,
        recommended_action=action,
        confidence_score=confidence
    )

def run_constrained_rule_compiler(rule_text: str) -> RuleCompilerResponse:
    # Simulating natural language to VerifyYou's When/Where/And graph compilation
    return RuleCompilerResponse(
        workflow_graph={
            "when": {"event": "checkout_initiated" if "checkout" in rule_text.lower() else "session_started"},
            "where": {"asn_type": "datacenter" if "datacenter" in rule_text.lower() else "any"},
            "and": {"transaction_amount_usd": {">": 300} if "300" in rule_text else {">": 0}},
            "action": "Trigger HumanCheck"
        }
    )


# --- 3. API ENDPOINTS ---
@app.post("/api/v1/triage", response_model=TriageResponse)
def triage_session(request: TriageRequest):
    """Ingests compressed feature deltas and returns strict JSON triage decisions."""
    try:
        result = run_constrained_llm_triage(request.feature_deltas)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/compile-rule", response_model=RuleCompilerResponse)
def compile_rule(request: RuleRequest):
    """Compiles plain-English rule into VerifyYou workflow graph structure."""
    try:
        result = run_constrained_rule_compiler(request.natural_language_rule)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)