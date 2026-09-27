


class TransactionProcessingError(Exception):
   

    def __init__(self, transaction_id: str, message: str):
        self.transaction_id = transaction_id
        super().__init__(message)


class NetworkFaultError(TransactionProcessingError):
    ""


class TimeoutFaultError(TransactionProcessingError):
    ''


class DatabaseFaultError(TransactionProcessingError):
    ''


FAILURE_TYPE_TO_EXCEPTION = {
    "Network": NetworkFaultError,
    "Timeout": TimeoutFaultError,
    "Database": DatabaseFaultError,
}
