from .utils import write_csv_log

CHECKPOINT_INTERVAL = 5


def run_checkpoint_rollback(transactions: list, final_results: dict,
                             checkpoint_log_path: str, rollback_log_path: str) -> dict:
    committed = []          
    checkpoints = []        
    checkpoint_log_rows = []
    rollback_log_rows = []

    def total_amount(txns):
        return sum(t["amount"] for t in txns)

    def make_checkpoint(is_final=False):
        name = f"CP{len(checkpoints) + 1}"
        cp = {
            "name": name,
            "successful_count": len(committed),
            "total_amount": total_amount(committed),
            "transaction_ids": [t["id"] for t in committed],
            "is_final": is_final,
        }
        checkpoints.append(cp)
        checkpoint_log_rows.append({
            "checkpoint": name,
            "successful_transactions": cp["successful_count"],
            "total_amount": cp["total_amount"],
            "state_saved": "ids=" + ",".join(cp["transaction_ids"]),
            "final_checkpoint": "Yes" if is_final else "No",
        })
        return cp

    for txn in transactions:
        outcome = final_results[txn["id"]]
        if outcome == "Success":
            committed.append(txn)
            if len(committed) % CHECKPOINT_INTERVAL == 0:
                make_checkpoint()
        else:  
            latest_cp = checkpoints[-1] if checkpoints else None
            before_count = len(committed)
            if latest_cp:
                committed = [t for t in committed if t["id"] in latest_cp["transaction_ids"]]
                restored_to = latest_cp["name"]
            else:
                committed = []
                restored_to = "INITIAL_STATE"
            rollback_log_rows.append({
                "transaction": txn["id"],
                "trigger": "Database fault - max retries exhausted",
                "committed_before_rollback": before_count,
                "restored_to_checkpoint": restored_to,
                "committed_after_rollback": len(committed),
                "restored_amount": total_amount(committed),
            })

    if len(committed) > (len(checkpoints) * CHECKPOINT_INTERVAL):
        make_checkpoint(is_final=True)

    write_csv_log(
        checkpoint_log_path,
        fieldnames=["checkpoint", "successful_transactions", "total_amount", "state_saved", "final_checkpoint"],
        rows=checkpoint_log_rows,
    )
    write_csv_log(
        rollback_log_path,
        fieldnames=["transaction", "trigger", "committed_before_rollback", "restored_to_checkpoint",
                    "committed_after_rollback", "restored_amount"],
        rows=rollback_log_rows,
    )

    return {
        "checkpoints": checkpoints,
        "rollbacks": rollback_log_rows,
        "final_committed": committed,
        "final_committed_count": len(committed),
        "final_committed_amount": total_amount(committed),
    }
