from .console import console


# spinners
def spinner(status="loading", *args, **kwargs):
    return console.status(status=status, *args, spinner="line", **kwargs)


def loading(status="loading", *args, **kwargs):
    return console.status(status=status, *args, spinner="aesthetic", **kwargs)


def clock(status="loading", *args, **kwargs):
    return console.status(status=status, *args, spinner="clock", **kwargs)
