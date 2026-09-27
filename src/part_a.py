from .fault_rules import ATTEMPT_OUTCOMES
from .utils import write_csv_log


def _validate_process_record(txn: dict) -> None:
    outcome = ATTEMPT_OUTCOMES[txn["failure_type"]][0]
    if outcome == "Fail":
        raise RuntimeError(f"{txn['id']} failed ({txn['failure_type']} fault) - no fault tolerance, aborting batch")


def run_baseline(transactions: list, log_path: str) -> dict:
    attempted = 0
    successful_txns = []
    log_rows = []
    crashed_on = None

    for txn in transactions:
        attempted += 1
        try:
            _validate_process_record(txn)
            successful_txns.append(txn)
            log_rows.append({
                "transaction": txn["id"], "amount": txn["amount"],
                "failure_type": txn["failure_type"], "outcome": "SUCCESS",
                "note": "Validate -> Process -> Record completed",
            })
        except RuntimeError as exc:
            crashed_on = txn
            log_rows.append({
                "transaction": txn["id"], "amount": txn["amount"],
                "failure_type": txn["failure_type"], "outcome": "CRASH",
                "note": str(exc),
            })
            break  

    remaining = transactions[attempted:]
    lost_txns = ([crashed_on] if crashed_on else []) + remaining

    for txn in remaining:
        log_rows.append({
            "transaction": txn["id"], "amount": txn["amount"],
            "failure_type": txn["failure_type"], "outcome": "NEVER_ATTEMPTED",
            "note": "Batch already aborted before reaching this transaction",
        })

    write_csv_log(
        log_path,
        fieldnames=["transaction", "amount", "failure_type", "outcome", "note"],
        rows=log_rows,
    )

    processed_amount = sum(t["amount"] for t in successful_txns)
    lost_amount = sum(t["amount"] for t in lost_txns)

    return {
        "attempted": attempted,
        "successful": len(successful_txns),
        "lost": len(lost_txns),
        "processed_amount": processed_amount,
        "lost_amount": lost_amount,
        "successful_txns": successful_txns,
        "lost_txns": lost_txns,
        "crashed_on": crashed_on["id"] if crashed_on else None,
    }
