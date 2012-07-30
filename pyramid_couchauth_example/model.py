# Copyright (c) 2011, Ryan Bourgeois <bluedragonx@gmail.com>
# All rights reserved.
#
# This software is licensed under a modified BSD license as defined in the
# provided license file at the root of this project.  You may modify and/or
# distribute in accordance with those terms.
#
# This software is provided "as is" and any express or implied warranties,
# including, but not limited to, the implied warranties of merchantability and
# fitness for a particular purpose are disclaimed.

from couchdbkit import Server, Document, StringProperty, SchemaListProperty
import bcrypt

def hashpw(password, salt=None):
    """
    Hash a password using the optional salt.  If salt is not specified one
    will be generated.  The hash, which includes the salt, is returned.
    :param password: The password to hash.
    :param salt: The optional salt to use.
    :return: The hashed password.
    """
    if salt is None:
        salt = bcrypt.gensalt()
    return unicode(bcrypt.hashpw(password, salt))

def hashcmp(hash, password):
    """
    Compare a hash to an un-hashed password.  Returns True if they match
    or false otherwise.
    :param hash A password hash generated by hashpw().
    :param password An unhashed password to compare against.
    :return: True if the password matches the hash, False if it does not.
    """
    salt = hash[:29]
    return hash == hashpw(password, salt)

class Permission(Document):
    """
    Permission document.  Permissions belong to groups in a many-to-many relationship.
    """
    name = StringProperty(required=True)

class Group(Document):
    """
    Group document.  Groups are assigned to users in a many-to-many relationship.
    """
    name = StringProperty(required=True)
    permissions = SchemaListProperty(Permission)

class User(Document):
    """
    User document.
    """
    username = StringProperty(required=True)
    password = StringProperty()
    groups = SchemaListProperty(Group)

    @staticmethod
    def create(username, password, groups=[]):
        """
        Convenience method for creating a new user.
        :param username: The username of the new user.
        :param password: The password of the new user.
        :param groups: The groups to assign to the new user.
        :return: The new user document.
        """
        hash = hashpw(password)
        return User(username=username, password=hash, groups=groups)

    def authenticate(self, password):
        """
        Authenticate the user against a plaintext password.
        :param password: The plaintext password to authenticate the user with.
        :return: True if authentication is successful, False otherwise.
        """
        return hashcmp(self.password, password)

    def set_password(self, password):
        """
        Set the password.  Hashes the password before setting.
        :param password: The password to set in plaintext.
        """
        self.password = hashpw(password)

class CouchSession:

    def __init__(self):
        """
        Constructor.  Creates a new CouchSession object.
        """
        self.uri_key = 'couch.uri'

    def configure(self, settings):
        """
        Configure the session.
        :param settings: WSGI settings dict.
        """
        if self.uri_key in settings:
            """
            If a URI was provided in the config file, use it to configure
            the CouchDB connection.
            """
            self.server = Server(settings[self.uri_key])
        else:
            """
            Otherwise it defaults to CouchDB's default, which is localhost.
            """
            self.server = Server()
        """
        Use the new session to initialize the whatcouch model.  We will
        use the 'auth' database by default.
        """

def init_model(settings):
    """
    Initialize the CouchDB models.  Called from main during app startup.
    :param settings: The WSGI settings dict.
    """
    Session.configure(settings)
    db_name = 'auth'
    db_key = 'whatcouch.db'
    if db_key in settings:
        """
        If a db name was provided in the config file we'll use it intead.
        """
        db_name = settings[db_key]
    Session.auth = Session.server.get_or_create_db(db_name)

    """
    Associate the model with the database.
    """
    User.set_db(Session.auth)
    Group.set_db(Session.auth)
    Permission.set_db(Session.auth)

Session = CouchSession()

