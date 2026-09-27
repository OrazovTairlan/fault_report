
ATTEMPT_OUTCOMES = {
    "None": ["Success"],
    "Network": ["Fail", "Success"],
    "Timeout": ["Fail", "Fail", "Success"],
    "Database": ["Fail", "Fail", "Fail"],
}

FINAL_RESULT = {
    "None": "Success",
    "Network": "Success",
    "Timeout": "Success",
    "Database": "Rollback",
}

ATTEMPT_LABELS = ["Initial attempt", "Retry 1", "Retry 2"]
