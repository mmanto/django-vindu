from pypushwoosh.client import PushwooshClient
from pypushwoosh.filter import ApplicationFilter
from pypushwoosh.command import CreateTargetedMessageCommand

client = PushwooshClient()


def pw_notify(msg):
    """Notificar a Pushwoosh"""
    command = CreateTargetedMessageCommand()
    command.auth = 'TLaAs1OIqin9Ql8CYrO09mqc24YcGpBORveFzhXPZ5REIyhN1cUd19cZLZB5ad8M4luiytetdXsQYWzWPRH6'
    command.devices_filter = ApplicationFilter('95FA9-DCCDC')
    command.content = msg
    try:
        client.invoke(command)
    except OSError:
        # Connection Error
        pass
