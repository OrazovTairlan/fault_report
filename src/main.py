import os

from .part_a import run_baseline
from .part_b import run_exception_handling
from .part_c import run_retry
from .part_d import run_checkpoint_rollback
from .transaction_data import TRANSACTIONS


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def pct(n, d):
    return 0.0 if d == 0 else round(100.0 * n / d, 2)


def main():
    total_amount = sum(t["amount"] for t in TRANSACTIONS)
    total_count = len(TRANSACTIONS)

    a = run_baseline(
        TRANSACTIONS,
        os.path.join(LOGS_DIR, "part_a_baseline_log.csv")
    )

    b = run_exception_handling(
        TRANSACTIONS,
        os.path.join(LOGS_DIR, "part_b_exception_log.csv")
    )

    c = run_retry(
        TRANSACTIONS,
        os.path.join(LOGS_DIR, "part_c_retry_attempt_log.csv")
    )

    d = run_checkpoint_rollback(
        TRANSACTIONS,
        c["final_results"],
        os.path.join(LOGS_DIR, "part_d_checkpoint_log.csv"),
        os.path.join(LOGS_DIR, "part_d_rollback_log.csv"),
    )

    baseline_successful = a["successful"]
    baseline_failed = a["lost"]
    baseline_lost_amount = a["lost_amount"]
    baseline_completion = pct(baseline_successful, total_count)

    ft_successful = d["final_committed_count"]
    ft_failed = total_count - ft_successful
    ft_lost_amount = total_amount - d["final_committed_amount"]
    ft_retries = c["total_retries"]
    ft_rollbacks = len(d["rollbacks"])
    ft_completion = pct(ft_successful, total_count)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    lines = []

    lines.append("Generated Results")
    lines.append("")

    lines.append("Part A - Baseline")
    lines.append(f"Transactions attempted: {a['attempted']}")
    lines.append(f"Successful transactions: {a['successful']}")
    lines.append(f"Transactions lost: {a['lost']}")
    lines.append(f"Processed amount (KZT): {a['processed_amount']}")
    lines.append(f"Lost amount (KZT): {a['lost_amount']}")
    lines.append(f"Batch crashed on: {a['crashed_on']}")
    lines.append("")

    lines.append("Part B - Exception Handling")

    for r in b["results"]:
        if r["final_status"] == "FAILED":
            lines.append(f"Transaction: {r['transaction']}")
            lines.append(f"Failure: {r['failure']}")
            lines.append(f"Exception: {r['exception']}")
            lines.append(f"Recovery Action: {r['recovery_action']}")
            lines.append(f"Final Status: {r['final_status']}")
            lines.append("")

    lines.append("Part C - Retry Attempt Log")

    for row in c["log_rows"]:
        lines.append(f"Timestamp/Step: {row['timestamp_step']}")
        lines.append(f"Transaction: {row['transaction']}")
        lines.append(f"Attempt: {row['attempt']}")
        lines.append(f"Failure: {row['failure_type']}")
        lines.append(f"Action: {row['action']}")
        lines.append(f"Result: {row['result']}")
        lines.append("")

    lines.append(f"Total retry attempts: {c['total_retries']}")
    lines.append("")

    lines.append("Part D - Checkpoints")

    for cp in d["checkpoints"]:
        lines.append(f"Checkpoint: {cp['name']}")
        lines.append(f"Successful transactions: {cp['successful_count']}")
        lines.append(f"Total amount (KZT): {cp['total_amount']}")
        lines.append(f"State saved: ids={','.join(cp['transaction_ids'])}")
        lines.append("")

    lines.append("Part D - Rollbacks")

    for rb in d["rollbacks"]:
        lines.append(f"Transaction: {rb['transaction']}")
        lines.append(f"Trigger: {rb['trigger']}")
        lines.append(f"Committed before: {rb['committed_before_rollback']}")
        lines.append(f"Restored to: {rb['restored_to_checkpoint']}")
        lines.append(f"Committed after: {rb['committed_after_rollback']}")
        lines.append(f"Restored amount: {rb['restored_amount']}")
        lines.append("")

    lines.append("Part E - Before / After")
    lines.append(f"Successful transactions: Baseline {baseline_successful}, Fault-tolerant {ft_successful}, Improvement +{ft_successful - baseline_successful}")
    lines.append(f"Failed transactions: Baseline {baseline_failed}, Fault-tolerant {ft_failed}, Improvement {ft_failed - baseline_failed}")
    lines.append(f"Lost amount (KZT): Baseline {baseline_lost_amount}, Fault-tolerant {ft_lost_amount}, Improvement -{baseline_lost_amount - ft_lost_amount}")
    lines.append(f"Retries: Baseline 0, Fault-tolerant {ft_retries}, Improvement +{ft_retries}")
    lines.append(f"Rollbacks: Baseline 0, Fault-tolerant {ft_rollbacks}, Improvement +{ft_rollbacks}")
    lines.append(f"Completion rate: Baseline {baseline_completion}%, Fault-tolerant {ft_completion}%, Improvement +{round(ft_completion - baseline_completion, 2)} percentage points")
    lines.append("")

    recovery_improvement = (
        pct(ft_successful - baseline_successful, baseline_successful)
        if baseline_successful
        else None
    )

    loss_reduction_amount_pct = pct(
        baseline_lost_amount - ft_lost_amount,
        baseline_lost_amount
    )

    loss_reduction_count_pct = pct(
        baseline_failed - ft_failed,
        baseline_failed
    )

    lines.append("Part E - Calculations")
    lines.append(
        f"Recovery improvement: "
        f"({ft_successful} - {baseline_successful}) / "
        f"{baseline_successful} * 100 = {recovery_improvement}%"
    )

    lines.append(
        f"Completion-rate improvement: "
        f"{ft_completion}% - {baseline_completion}% = "
        f"{round(ft_completion - baseline_completion, 2)} percentage points"
    )

    lines.append(
        f"Transaction-loss reduction by count: "
        f"({baseline_failed} - {ft_failed}) / "
        f"{baseline_failed} * 100 = {loss_reduction_count_pct}%"
    )

    lines.append(
        f"Transaction-loss reduction by amount: "
        f"({baseline_lost_amount} - {ft_lost_amount}) / "
        f"{baseline_lost_amount} * 100 = {loss_reduction_amount_pct}%"
    )

    report_path = os.path.join(OUTPUT_DIR, "generated_results.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("\n".join(lines))
    print(f"\n[OK] Logs written to: {LOGS_DIR}")
    print(f"[OK] Generated summary written to: {report_path}")


if __name__ == "__main__":
    main()
