import json
import re
from app.utils.groq_client import ask_ai



def extract_json(response: str):
    """
    Extract JSON object from LLM response safely
    """
    response = response.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", response, re.DOTALL)

    if match:
        return match.group()

    return response


def safe_json_parse(response: str):
    """
    Parse JSON safely with auto-fix attempts
    """

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    #  Fix common issues

    # remove newlines inside strings
    response = response.replace("\n", " ")

    # fix trailing commas
    response = re.sub(r",\s*}", "}", response)
    response = re.sub(r",\s*]", "]", response)

    # fix lowercase visibility
    response = response.replace('"public"', '"Public"')

    # fix unclosed quotes (best effort)
    response = re.sub(r'(?<!\\)"\s*(?=[,}])', '"', response)

    try:
        return json.loads(response)
    except:
        return None


def clean_suggestions(data):

    suggestions = data.get("suggestions", [])
    cleaned = []

    for s in suggestions:
        if isinstance(s, str):
            s = s.replace('\\"', '"').strip()
            cleaned.append(s)

    data["suggestions"] = cleaned
    return data


# ---------------- NORMALIZER ---------------- #

def normalize_payload(payload: dict):

    # -------- REQUIRED FIELDS -------- #
    payload["catalog_name"] = payload.get("catalog_name", "default_catalog")
    payload["benchmark_name"] = payload.get("benchmark_name", "generated_benchmark")
    payload["benchmark_category"] = payload.get("benchmark_category", "performance")
    payload["description"] = payload.get("description", "Auto-generated benchmark")

    # -------- scripts -------- #
    scripts = payload.get("scripts", {})
    payload["scripts"] = {
        "sut_setup": scripts.get("sut_setup") or "sudo apt install nginx -y",
        "sut_teardown": scripts.get("sut_teardown") or "sudo systemctl stop nginx"
    }

    # -------- metrics -------- #
    metrics = payload.get("metrics", [])

    if isinstance(metrics, list):
        payload["metrics"] = [
            str(m.get("name") if isinstance(m, dict) else m).lower()
            for m in metrics if m
        ] or ["latency", "throughput"]
    else:
        payload["metrics"] = ["latency", "throughput"]

    # -------- visibility -------- #
    payload["visibility"] = payload.get("visibility", "Public")

    # -------- run_parameters -------- #
    rp = payload.get("run_parameters", {})

    payload["run_parameters"] = {
        "threads": rp.get("threads", {
            "data_type": "integer",
            "value_type": "range",
            "min": 1,
            "max": 16,
            "default": 8,
            "description": "Number of threads"
        }),
        "connections": rp.get("connections", {
            "data_type": "integer",
            "value_type": "range",
            "min": 1,
            "max": 1000,
            "default": 100,
            "description": "Number of connections"
        })
    }

    return payload


# ---------------- VALIDATION ---------------- #

def validate_benchmark(payload: dict):

    prompt = f"""
You are an expert benchmark configuration validator.

Analyze the benchmark configuration below.

Payload:
{json.dumps(payload, indent=2)}

Return STRICT JSON:

{{
  "suggestions": [
    "text suggestion 1",
    "text suggestion 2"
  ]
}}

Rules:
- ONLY plain strings
- NO nested JSON
- NO markdown
"""

    response = ask_ai(prompt)

    cleaned = extract_json(response)
    parsed = safe_json_parse(cleaned)

    if parsed:
        parsed = clean_suggestions(parsed)

        return {
            "suggestions": parsed.get("suggestions", [])
        }

    return {
        "suggestions": [],
        "error": "AI response invalid",
        "raw_response": cleaned
    }


# ---------------- GENERATE ---------------- #

def generate_benchmark_from_text(user_prompt: str):

    prompt = f"""
Convert user instruction into VALID benchmark_catalog JSON.

Instruction:
{user_prompt}

STRICT schema:
- catalog_name
- benchmark_name
- benchmark_category
- description
- scripts (sut_setup, sut_teardown)
- run_parameters (threads, connections)
- metrics (list of strings)
- visibility

Rules:
- Return ONLY JSON
- NO explanation
- NO markdown
"""

    response = ask_ai(prompt)

    cleaned = extract_json(response)
    parsed = safe_json_parse(cleaned)

    if not parsed:
        return {
            "errors": ["AI response invalid"],
            "warnings": [],
            "suggestions": [],
            "raw_ai_response": cleaned
        }

    corrected = normalize_payload(parsed)

    return {
        "errors": [],
        "warnings": [],
        "suggestions": [],
        "corrected_payload": corrected
    }


# ---------------- AUTO FIX ---------------- #

def auto_fix_benchmark(payload: dict):

    prompt = f"""
Fix the benchmark payload strictly.

Payload:
{json.dumps(payload, indent=2)}

Return STRICT JSON:

{{
  "errors": [],
  "warnings": [],
  "suggestions": [],
  "corrected_payload": {{ VALID_SCHEMA_OBJECT }}
}}

Rules:
- DO NOT change schema
- DO NOT add fields
- RETURN ONLY JSON
"""

    response = ask_ai(prompt)

    cleaned = extract_json(response)
    parsed = safe_json_parse(cleaned)

    if parsed:
        corrected = normalize_payload(parsed.get("corrected_payload", {}))

        return {
            "errors": parsed.get("errors", []),
            "warnings": parsed.get("warnings", []),
            "suggestions": parsed.get("suggestions", []),
            "corrected_payload": corrected
        }

    return {
        "errors": ["AI could not fix payload"],
        "warnings": [],
        "suggestions": [],
        "raw_ai_response": cleaned
    }