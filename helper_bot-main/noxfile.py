import nox


@nox.session
def format_and_lint(session: nox.Session) -> None:
    session.install("black", "isort", "ruff")
    session.run("python", "-m", "black", ".")
    session.run("python", "-m", "isort", ".")
    session.run("python", "-m", "ruff", ".")
