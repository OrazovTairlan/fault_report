from .exceptions import FAILURE_TYPE_TO_EXCEPTION, TransactionProcessingError
from .fault_rules import ATTEMPT_OUTCOMES
from .utils import write_csv_log

RECOVERY_ACTION = "Logged, classified, transaction marked FAILED, processing continued with next transaction"


def _validate_process_record(txn: dict) -> None:
    outcome = ATTEMPT_OUTCOMES[txn["failure_type"]][0]
    if outcome == "Fail":
        exc_class = FAILURE_TYPE_TO_EXCEPTION[txn["failure_type"]]
        raise exc_class(txn["id"], f"{txn['failure_type']} fault while processing {txn['id']}")


def run_exception_handling(transactions: list, log_path: str) -> dict:
    results = []
    log_rows = []
    successful = 0
    failed = 0

    for txn in transactions:
        try:
            _validate_process_record(txn)
            successful += 1
            results.append({
                "transaction": txn["id"], "failure": "None", "exception": "-",
                "recovery_action": "-", "final_status": "SUCCESS",
            })
            log_rows.append({
                "transaction": txn["id"], "amount": txn["amount"],
                "exception_class": "-", "recovery_action": "-", "final_status": "SUCCESS",
            })
        except TransactionProcessingError as exc:
            failed += 1
            results.append({
                "transaction": txn["id"], "failure": txn["failure_type"],
                "exception": type(exc).__name__, "recovery_action": RECOVERY_ACTION,
                "final_status": "FAILED",
            })
            log_rows.append({
                "transaction": txn["id"], "amount": txn["amount"],
                "exception_class": type(exc).__name__, "recovery_action": RECOVERY_ACTION,
                "final_status": "FAILED",
            })
            continue

    write_csv_log(
        log_path,
        fieldnames=["transaction", "amount", "exception_class", "recovery_action", "final_status"],
        rows=log_rows,
    )

    return {"results": results, "successful": successful, "failed": failed}
