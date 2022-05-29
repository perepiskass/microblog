from appPackage import appFlask, db
from appPackage.models import User, Post
from appPackage import cli

@appFlask.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'Post':Post}