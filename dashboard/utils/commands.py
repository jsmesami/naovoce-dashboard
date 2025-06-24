from .email import send_email


def report_exception(app):
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
                raise

        return closure

    return wrapper
