# -*- coding: utf-8 -*-

import random
import crypt
import string


def salt():
    """Returns a string of 2 randome letters"""

    return random.choice(string.ascii_letters) + random.choice(string.digits)


class GenHtpasswd:
    """A class for manipulating htpasswd files."""

    def __init__(self, filename, create=False):
        self.entries = []
        self.filename = filename

    def load(self):
        """Read the htpasswd file into memory."""
        lines = open(self.filename, 'r').readlines()
        self.entries = []
        for line in lines:
            username, pwhash = line.split(':')
            entry = [username, pwhash.rstrip()]
            self.entries.append(entry)

    def save(self):
        """Write the htpasswd file to disk"""
        open(self.filename, 'w').writelines(["%s:%s\n" % (entry[0], entry[1])
                                             for entry in self.entries])

    def update(self, username, password):
        """Replace the entry for the given user, or add it if new."""
        pwhash = crypt.crypt(password, salt())
        matching_entries = [entry for entry in self.entries
                            if entry[0] == username]
        if matching_entries:
            matching_entries[0][1] = pwhash
        else:
            self.entries.append([username, pwhash])

    def delete(self, username):
        """Remove the entry for the given user."""
        self.entries = [entry for entry in self.entries
                        if entry[0] != username]

