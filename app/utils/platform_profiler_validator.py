import re


REQUIRED_FIELDS = [
    "bios",
    "cpu_usage",
    "os",
    "manufacturer"
]


def validate_text(value, field):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field} cannot be empty")

    if not re.fullmatch(r"[A-Za-z0-9 .,_:%@()\-+/]+", str(value)):
        raise ValueError(f"{field} contains invalid characters")


def validate_platform_profile(data: dict):
    try:
        for field in REQUIRED_FIELDS:
            if field not in data:
                raise ValueError(f"{field} is required")

            value = data.get(field)

            # handle nested dict OR string
            if isinstance(value, dict):
                for k, v in value.items():
                    validate_text(v, f"{field}.{k}")
            else:
                validate_text(value, field)

    except Exception as e:
        raise ValueError(str(e))