from .fault_rules import ATTEMPT_LABELS, ATTEMPT_OUTCOMES, FINAL_RESULT
from .utils import StepClock, write_csv_log


def run_retry(transactions: list, log_path: str) -> dict:
    clock = StepClock()
    log_rows = []
    final_results = {}
    committed_ids = set()
    retry_counts = {}  

    for txn in transactions:
        outcomes = ATTEMPT_OUTCOMES[txn["failure_type"]]
        retries_used = 0
        succeeded = False

        for idx, attempt_outcome in enumerate(outcomes):
            if txn["id"] in committed_ids:
                break  

            label = ATTEMPT_LABELS[idx]
            if idx > 0:
                retries_used += 1
            action = "Process transaction" if idx == 0 else f"Retry attempt #{idx}"

            log_rows.append({
                "timestamp_step": clock.next(),
                "transaction": txn["id"],
                "attempt": label,
                "failure_type": txn["failure_type"] if attempt_outcome == "Fail" else "-",
                "action": action,
                "result": attempt_outcome,
            })

            if attempt_outcome == "Success":
                committed_ids.add(txn["id"])
                succeeded = True
                break

        if succeeded:
            final_results[txn["id"]] = "Success"
        else:
            final_result = FINAL_RESULT[txn["failure_type"]]
            log_rows.append({
                "timestamp_step": clock.next(),
                "transaction": txn["id"],
                "attempt": "Final",
                "failure_type": txn["failure_type"],
                "action": "Max retries exhausted -> trigger rollback",
                "result": final_result,
            })
            final_results[txn["id"]] = final_result

        retry_counts[txn["id"]] = retries_used

    write_csv_log(
        log_path,
        fieldnames=["timestamp_step", "transaction", "attempt", "failure_type", "action", "result"],
        rows=log_rows,
    )

    total_retries = sum(retry_counts.values())
    return {
        "final_results": final_results,     
        "retry_counts": retry_counts,        
        "total_retries": total_retries,
        "log_rows": log_rows,
    }
