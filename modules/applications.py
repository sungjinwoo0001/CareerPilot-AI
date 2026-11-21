
from datetime import date


def create_application(company, role, job_url="", status="Applied", notes=""):
    return {
        "company": company,
        "role": role,
        "job_url": job_url,
        "status": status,
        "applied_date": str(date.today()),
        "response": "Pending",
        "notes": notes
    }


def update_application(application, status=None, response=None, notes=None):
    if status is not None:
        application["status"] = status

    if response is not None:
        application["response"] = response

    if notes is not None:
        application["notes"] = notes

    return application


def analyze_application_patterns(applications):
    total = len(applications)

    if total == 0:
        return {
            "total_applications": 0,
            "response_rate": 0,
            "message": "No applications recorded yet."
        }

    responded = sum(
        1 for app in applications
        if app.get("response", "Pending") != "Pending"
    )

    response_rate = round((responded / total) * 100, 2)

    return {
        "total_applications": total,
        "responses_received": responded,
        "response_rate": response_rate,
        "message": (
            "Keep tracking applications to identify which roles "
            "and companies respond most often."
        )
    }
