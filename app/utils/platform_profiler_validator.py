import re

REQUIRED_FIELDS = [
    "bios",
    "cpu_usage",
    "os",
    "manufacturer"
]


def validate_text(value, field, errors):
    # -------------------------------
    # EMPTY CHECK
    # -------------------------------
    if value is None or str(value).strip() == "":
        errors.append({
            "field": field,
            "error": "cannot be empty"
        })
        return

    # -------------------------------
    # REGEX VALIDATION
    # -------------------------------
    if not re.fullmatch(r"[A-Za-z0-9 .,_:%@()\-+/]+", str(value)):
        errors.append({
            "field": field,
            "error": "contains invalid characters"
        })


def validate_platform_profile(data: dict):
    errors = []

    try:
        for field in REQUIRED_FIELDS:

            # -------------------------------
            # REQUIRED FIELD CHECK
            # -------------------------------
            if field not in data:
                errors.append({
                    "field": field,
                    "error": "is required"
                })
                continue

            value = data.get(field)

            # -------------------------------
            # NESTED DICT HANDLING
            # -------------------------------
            if isinstance(value, dict):
                for k, v in value.items():
                    validate_text(v, f"{field}.{k}", errors)
            else:
                validate_text(value, field, errors)

        # -------------------------------
        # FINAL ERROR THROW
        # -------------------------------
        if errors:
            raise ValueError(errors)

        return True  # optional success

    except Exception as e:
        # if already structured error list
        if isinstance(e.args[0], list):
            raise ValueError(e.args[0])

        # fallback (unexpected errors)
        raise ValueError([{
            "field": "system",
            "error": str(e)
        }])