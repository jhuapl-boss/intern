from __future__ import absolute_import
from .enums import *
from .errors import *


class RAMONBase(object):
    """
    RAMONBase Object for storing neuroscience data
    """

    def __init__(self, id=DEFAULT_ID,
                 confidence=DEFAULT_CONFIDENCE,
                 kvpairs=DEFAULT_DYNAMIC_METADATA,
                 status=DEFAULT_STATUS,
                 author=DEFAULT_AUTHOR):
        """
        Initialize a new RAMONBase object with default attributes.

        Arguments:
            id (int): Unique 32-bit ID value assigned by OCP database
            confidence (float): Value 0-1 indicating confidence in annotation
            kvpairs (dict): A collection of key-value pairs
            status (string): Status of annotation in database
            author (string): Username of the person who created the annotation
        """
        self.id = id
        self.confidence = confidence
        self.kvpairs = kvpairs
        self.status = status
        self.author = author

    def __str__(self):
        """
        String representation of a RAMON object for convenience.
        """
        return "<{} object. id={}>".format(type(self), self.id)

    def __repr__(self):
        """
        String representation of a RAMON object for convenience.
        """
        return "{} object. id={}".format(type(self), self.id)
