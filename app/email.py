class EmailClient:
    def send_email(self, recipient: str, title: str, body: str) -> None:
        raise NotImplementedError()


def get_email_client() -> EmailClient:
    raise NotImplementedError("Unimplemented email client")
