import nox


@nox.session(python=["3.9", "3.13", "3.13t", "pypy3.11"], venv_backend="uv")
def test(session: nox.Session) -> None:
    if isinstance(session.python, str) and "t" not in session.python:
        session.install(".[test,test-extra]")
    else:
        session.install(".[test]")
    session.run("pytest", "-v", *session.posargs)
