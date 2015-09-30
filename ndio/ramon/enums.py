
class InvalidEnumerationException(Exception):
    def __init__(self, msg = "Invalid Enumeration."):
        self.msg = msg

    def __str__(self):
        return self.msg

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

eRAMONAnnoStatus = enum("DEFAULT",
                        UNPROCESSED=0,
                        LOCKED=1,
                        PROCESSED=2,
                        IGNORED=3)

DEFAULT_ID                  = -1
DEFAULT_CONFIDENCE          = 00
DEFAULT_DYNAMIC_METADATA    = {}
DEFAULT_STATUS              = eRAMONAnnoStatus.DEFAULT
DEFAULT_AUTHOR              = ''
