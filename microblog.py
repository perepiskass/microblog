from appPackage import create_app, db, cli
from appPackage.models import User, Post, Notification, Message

app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'Post':Post, 'Notification': Notification, 'Message': Message}