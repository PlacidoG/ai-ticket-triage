from fastapi import HTTPException

# Gives consistent error responses for across entire API


class TicketNotFoundError(HTTPException):
    def __init__(self, ticket_id):
        super().__init__(
            status_code=404,
            detail={
                "error": "ticket_not_found",
                "message": f"No ticket with id {ticket_id} ",
            },
        )



class InvalidStatusError(HTTPException):
    def __init__(self, status, valid_statuses):
        super().__init__(
            status_code=422,
            detail={
                "error": "invalid_status",
                "message": f"'{status}' is not a valid status",
                "valid_values": valid_statuses,
            },
        )


