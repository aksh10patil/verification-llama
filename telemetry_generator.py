import json
import random
from typing import Any, Dict, List

class VerifyYouTelemetryEngine:
    """Simulates VerifyYou's passive telemetry schema (350+ signals) 
    and extracts high-value feature deltas for Llama-3.2-3B inference.
    """
    
    def __init__(self):
        # Baseline noise template representing standard benign device properties
        self.standard_noise_keys = {
            "screen_color_depth": 24,
            "pixel_ratio": 2.0,
            "hardware_concurrency": 8,
            "device_memory_gb": 16,
            "platform": "MacIntel",
            "language": "en-US",
            "touch_support": False,
            "cookie_enabled": True,
            "do_not_track": "1"
        }

    def generate_raw_session(self, archetype_id: str) -> Dict[str, Any]:
        """Generates a full 350-signal raw payload based on 4 key threat archetypes."""
        
        # Start with standard noise to bloat payload realistically (~350 properties simulated)
        raw_signals = {f"noise_attr_{i}": random.choice([True, False, 100, "normal"]) for i in range(340)}
        raw_signals.update(self.standard_noise_keys)
        
        session_id = f"acct_{random.randint(2000, 9999)}"
        
        if archetype_id == "sybil_ban_evader":
            raw_signals.update({
                "account_id": session_id,
                "trust_score": 28,
                "device_new": True,
                "tor_exit": True,
                "vpn_exit": False,
                "fast_fill_ms": 140,
                "copy_paste_count": 6,
                "cross_network_flag": True,
                "canvas_spoofed": False,
                "mouse_entropy": 0.89,
                "asn_type": "hosting",
                "vertical": "ai_data_labeling"
            })
        elif archetype_id == "bot_farm_agent":
            raw_signals.update({
                "account_id": session_id,
                "trust_score": 19,
                "device_new": True,
                "tor_exit": False,
                "vpn_exit": True,
                "fast_fill_ms": 85,
                "copy_paste_count": 0,
                "cross_network_flag": True,
                "canvas_hash_cluster_size": 42,
                "agent_declared": True,
                "agent_owner_verified": False,
                "mouse_entropy": 0.04,  # Unnaturally linear/robotic
                "asn_type": "datacenter",
                "vertical": "agent_platform"
            })
        elif archetype_id == "sleeper_ato":
            raw_signals.update({
                "account_id": session_id,
                "trust_score": 54,
                "account_age_days": 194,
                "device_new": True,
                "tor_exit": False,
                "vpn_exit": False,
                "geo_velocity_kmh": 920, # Impossible travel speed
                "keystroke_dwell_delta": 0.12,
                "payout_method_changed": True,
                "cross_network_flag": False,
                "asn_type": "residential",
                "vertical": "online_community"
            })
        elif archetype_id == "privacy_power_user": # Crucial False-Positive Test Case
            raw_signals.update({
                "account_id": session_id,
                "trust_score": 68,
                "account_age_days": 420,
                "device_new": False,
                "tor_exit": False,
                "vpn_exit": True, # Mullvad VPN
                "canvas_spoofed": True, # Brave Browser
                "password_manager_autofill": True,
                "fast_fill_ms": 210,
                "copy_paste_count": 0,
                "cross_network_flag": False,
                "keystroke_cadence_human": True,
                "asn_type": "isp",
                "vertical": "ai_data_labeling"
            })
        else:
            raise ValueError(f"Unknown archetype: {archetype_id}")
            
        return raw_signals

    def extract_feature_deltas(self, raw_session: Dict[str, Any]) -> Dict[str, Any]:
        """The Anomaly Filter: Strips 340+ noise fields and isolates risk factors 
        to keep the prompt under ~150 tokens for Llama-3.2-3B.
        """
        # Keys we care about for T&S triage decisioning
        key_risk_indicators = [
            "account_id", "trust_score", "device_new", "tor_exit", "vpn_exit",
            "fast_fill_ms", "copy_paste_count", "cross_network_flag", "canvas_spoofed",
            "canvas_hash_cluster_size", "agent_declared", "agent_owner_verified",
            "mouse_entropy", "geo_velocity_kmh", "payout_method_changed", 
            "password_manager_autofill", "asn_type", "account_age_days", "vertical"
        ]
        
        # Filter raw session to keep only active deviations/signals
        compressed_delta = {k: raw_session[k] for k in key_risk_indicators if k in raw_session}
        
        # Retain only risk factors where values indicate a deviation from baseline
        anomalies_only = {
            k: v for k, v in compressed_delta.items() 
            if v is True or (isinstance(v, (int, float)) and v not in [24, 8, 16]) or k in ["trust_score", "account_id", "vertical", "asn_type"]
        }
        
        return anomalies_only

# --- Quick Test Execution ---
if __name__ == "__main__":
    engine = VerifyYouTelemetryEngine()
    
    print("=== TESTING ARCHETYPE 1: BAN-EVADING SYBIL ===")
    raw_1 = engine.generate_raw_session("sybil_ban_evader")
    delta_1 = engine.extract_feature_deltas(raw_1)
    print(f"Total Raw Keys Generated: {len(raw_1)}")
    print("Compressed LLM Input Payload (Feature Deltas):\n", json.dumps(delta_1, indent=2))
    
    print("\n=== TESTING ARCHETYPE 4: PRIVACY POWER USER (FALSE-POSITIVE CHECK) ===")
    raw_4 = engine.generate_raw_session("privacy_power_user")
    delta_4 = engine.extract_feature_deltas(raw_4)
    print(f"Compressed LLM Input Payload (Feature Deltas):\n", json.dumps(delta_4, indent=2))