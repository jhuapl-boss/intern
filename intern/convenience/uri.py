from ..remote.boss import BossRemote

# A mapping of permitted protocol types:
PROTOCOLS = {
    "bossdb": BossRemote,
    "boss": BossRemote,
}


class InvalidURIError(ValueError):
    def __init__(self, *args):
        self.reason = args[0] if len(args) else None

    def __str__(self):
        return (
            "Invalid URI. URIs must be of the form `[protocol]://[remote]/[resource]`. See intern.convenience.PROTOCOLS for a list of valid protocols. "
            + self.reason
            if self.reason
            else ""
        )


def parse_fquri(fully_qualified_uri, **kwargs):
    """
    Given a fully-qualified URI string, return a Remote and Resource.

    These should be directly usable as, e.g., `remote.get_cutout(resource)`.

    Arguments:
        fully_qualified_uri (str): The URI to parse, of the form explained in
            the docstrings above.

    kwargs:
        token: str

    Returns:
        Tuple[Remote, Resource]

    """
    # Split the string on the protocol-delimiter first:
    PROTOCOL_DELIM = "://"
    split_by_protocol = fully_qualified_uri.split(PROTOCOL_DELIM)

    protocol = None
    secondary_protocol = None
    remote_path = None

    if len(split_by_protocol) is 1:
        raise InvalidURIError(fully_qualified_uri + " must have a `[protocol]://`.")

    elif len(split_by_protocol) is 2:
        # This URI is of the form `[protocol]://[remote+resource]`, and doesn't
        # specify, e.g., an HTTP/HTTPS protocol.
        protocol, remote_path = split_by_protocol
        secondary_protocol = None

    elif len(split_by_protocol) is 3:
        # This URI has a secondary (e.g. https) protocol, and is of the form
        # `[protocol]://[secondary_protocol]://[remote+resource]`.
        protocol, secondary_protocol, remote_path = split_by_protocol

    else:
        raise InvalidURIError(fully_qualified_uri + " is not a valid URI.")

    if protocol not in PROTOCOLS:
        raise InvalidURIError(
            "Protocol "
            + protocol
            + " is not valid. Valid protocols are: "
            + ",".join([str(i) for i in PROTOCOLS.keys()])
        )

    remote_constructor = PROTOCOLS[protocol]

    if remote_constructor == BossRemote:
        # `remote_path` should be of the form `host/col/exp/chan`:
        remote_path_components = remote_path.split("/")
        if len(remote_path_components) is 4:
            host, collection, experiment, channel = remote_path_components
            remote = remote_constructor(
                {
                    "protocol": secondary_protocol,
                    "host": host,
                    "token": kwargs.get("token", "public"),
                }
            )
        elif len(remote_path_components) is 3 and secondary_protocol is None:
            # This means the host/protocol/token will be specified in a config
            # file, and we only have col/exp/chan, of the form:
            # `bossdb://col/exp/chan`
            collection, experiment, channel = remote_path_components
            remote = remote_constructor()
        else:
            raise InvalidURIError(
                "BossDB URIs must be of the form bossdb://http[s]://[host]/[collection]/[experiment]/[echannel], got "
                + remote_path
            )

        resource = remote.get_channel(channel, collection, experiment)
        return (remote, resource)
