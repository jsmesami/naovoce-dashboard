from .email import send_email


def wrap_command(app):
    def wrapper(func):
        def closure(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as inst:
                send_email(
                    app,
                    recipient="jsmesami@gmail.com",
                    subject="Command failed",
                    body=str(inst),
                )

        return closure

    return wrapper
