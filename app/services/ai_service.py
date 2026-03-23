import json
import re
from app.utils.groq_client import ask_ai


# ---------------- JSON HELPERS ---------------- #

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
    Parse JSON safely with fallback fixes
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 🔥 Try fixing escaped JSON
    try:
        cleaned = response.replace('\\"', '"')
        return json.loads(cleaned)
    except:
        pass

    return None


def clean_suggestions(data):

    suggestions = data.get("suggestions", [])
    cleaned = []

    for s in suggestions:
        if isinstance(s, str):

            # remove escape characters
            s = s.replace('\\"', '"').replace('%', '').strip()

            # try parsing if it's nested JSON
            try:
                parsed = json.loads(s)
                if isinstance(parsed, dict):
                    cleaned.append(parsed.get("suggestion", str(parsed)))
                else:
                    cleaned.append(str(parsed))
            except:
                cleaned.append(s)

    data["suggestions"] = cleaned
    return data



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
- ONLY plain strings in suggestions
- NO nested JSON
- NO escape characters
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
You are a system that converts user instructions into a benchmark_catalog configuration.

User instruction:
{user_prompt}

Generate a COMPLETE and VALID JSON object using this schema:

{{
  "catalog_name": "string",
  "benchmark_name": "string",
  "benchmark_category": "string",
  "description": "string",
  "scripts": {{
    "sut_setup": "string",
    "sut_teardown": "string"
  }},
  "run_parameters": {{
    "threads": {{
      "data_type": "integer",
      "value_type": "range",
      "min": 1,
      "max": 999,
      "default": 1,
      "description": "Number of threads"
    }},
    "connections": {{
      "data_type": "integer",
      "value_type": "range",
      "min": 1,
      "max": 9999,
      "default": 1,
      "description": "Number of connections"
    }}
  }},
  "metrics": [
    "latency",
    "throughput"
  ],
  "visibility": "Public"
}}

Rules:
- DO NOT skip any fields
- Scripts must NOT be empty
- Infer realistic values
- Return STRICT JSON
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
You are an expert benchmark configuration fixer.

Fix the given payload STRICTLY according to the schema.

Payload:
{json.dumps(payload, indent=2)}

Schema:
- catalog_name (string)
- benchmark_name (string)
- benchmark_category (string)
- description (string)
- scripts (sut_setup, sut_teardown)
- run_parameters (threads, connections)
- metrics (list of strings)
- visibility (Public/Private)

Return STRICT JSON:

{{
  "errors": [],
  "warnings": [],
  "suggestions": [],
  "corrected_payload": {{ VALID_SCHEMA_OBJECT }}
}}

Rules:
- DO NOT add extra fields
- DO NOT change structure
- Return ONLY JSON
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
        "sut_setup": scripts.get("sut_setup") or "sudo apt install nginx",
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