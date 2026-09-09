from application import create_app, banner
from flask.cli import FlaskGroup
app = create_app()
cli = FlaskGroup(app)

if __name__ == "__main__":
    banner()
    cli()