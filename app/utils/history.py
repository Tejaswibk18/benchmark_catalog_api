from datetime import datetime


def create_history(user, change_type, summary, changes=None):

    return {
        "catalog_version": "1",
        "changed_on": datetime.utcnow(),
        "changed_by": user,
        "change_type": change_type,
        "summary": summary,
        "changes": changes or []
    }