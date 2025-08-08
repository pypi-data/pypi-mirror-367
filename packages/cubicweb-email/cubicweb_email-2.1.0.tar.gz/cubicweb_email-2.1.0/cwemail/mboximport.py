#!/usr/bin/python


import argparse
import mailbox
from email.utils import parsedate
from io import BytesIO
from itertools import combinations

from cwclientlib import cwproxy, cwproxy_for
from logilab.common.umessage import message_from_file


class StreamMailbox(mailbox.mbox):
    """A read-only mbox format mailbox from stream."""

    _mangle_from_ = True

    def __init__(self, stream, factory=None, create=True):
        """Initialize a stream mailbox."""
        self._message_factory = mailbox.mboxMessage
        mailbox.Mailbox.__init__(self, "", factory, create)
        self._file = stream
        self._toc = None
        self._next_key = 0
        self._pending = False  # No changes require rewriting the file.
        self._locked = False
        self._file_length = None  # Used to record mailbox size


class Importer:
    def __init__(self, proxy, skipsign=False):
        self.proxy = proxy
        self._address_cache = {}
        self._reqs = []
        self._skipsign = skipsign

    def import_mbox_stream(self, stream):
        self._import(StreamMailbox(stream, message_from_file, create=False))

    def import_mbox(self, path):
        self._import(mailbox.mbox(path, message_from_file, create=False))

    def import_maildir(self, path):
        self._import(mailbox.Maildir(path, message_from_file, create=False))

    def _import(self, mailbox):
        for message in sorted(mailbox, key=lambda x: parsedate(x["Date"])):
            self.import_message(message)

    def import_message(self, message):
        rql = "INSERT Email E: E headers %(headers)s"
        args = {
            "headers": "\n".join(
                "{}: {}".format(*header) for header in message.message.items()
            )
        }
        self._reqs.append((rql, args))
        emaileid = f"__r{len(self._reqs) - 1}"
        self._part_index = 0
        self._context = None
        self._alternatives = []
        self.import_message_parts(message, emaileid)
        try:
            resp = self.proxy.rqlio(self._reqs)
            resp.raise_for_status()
        except cwproxy.RemoteValidationError as exc:
            print(f"could not import message {message.get('message-id')}: {exc.args}")
        else:
            return resp.json()
        finally:
            self._reqs = []

    def import_message_parts(self, message, emaileid):
        if message.is_multipart():
            self._context = message.get_content_type().split("/")[1]
            if self._context == "alternative":
                self._alternatives.append([])
            for part in message.get_payload():
                self.import_message_parts(part, emaileid)
            if self._context == "alternative":
                alternatives = self._alternatives.pop()
                for eid1, eid2 in combinations(alternatives, 2):
                    self._reqs.append(
                        (
                            "SET X alternative Y WHERE X eid %(x)s, Y eid %(y)s",
                            {"x": eid1, "y": eid2},
                        )
                    )
            self._context = None
        else:
            self._import_message_part(message, emaileid)

    def _import_message_part(self, part, emaileid):
        assert not part.is_multipart()
        contenttype = part.get_content_type()
        main, sub = contenttype.split("/")
        data = part.get_payload(decode=True)
        if main == "text":
            encoding = "UTF-8"
        elif contenttype == "application/pgp-signature":
            if self._skipsign:
                return
            encoding = "ascii"
            if isinstance(data, bytes):
                data = data.decode(encoding)
            # XXXX
        else:
            encoding = None
        name = part.get_filename()
        if name or main != "text" and contenttype != "application/pgp-signature":
            # suppose if we have a name, this is an attachement else this is a
            # part/alternative
            name = name or "no name"
            if isinstance(data, str):
                data = data.encode("utf8")
            self._reqs.append(
                (
                    "INSERT File F: F data %(data)s, F data_name %(name)s, "
                    "F data_format %(ctype)s, F data_encoding %(encoding)s",
                    {
                        "data": BytesIO(data),
                        "name": name,
                        "ctype": contenttype,
                        "encoding": encoding,
                    },
                )
            )
            parteid = f"__r{len(self._reqs) - 1}"
            self._reqs.append(
                (
                    "SET X attachment Y WHERE X eid %(x)s, Y eid %(y)s",
                    {"x": emaileid, "y": parteid},
                )
            )
        else:
            self._part_index += 1
            self._reqs.append(
                (
                    "INSERT EmailPart P: P content %(data)s, P content_format %(ctype)s, P ordernum %(idx)s",
                    {"data": data, "ctype": contenttype, "idx": self._part_index},
                )
            )
            parteid = f"__r{len(self._reqs) - 1}"
            self._reqs.append(
                (
                    "SET X parts Y WHERE X eid %(x)s, Y eid %(y)s",
                    {"x": emaileid, "y": parteid},
                )
            )
            if self._context == "alternative":
                self._alternatives[-1].append(parteid)


def main():
    parser = argparse.ArgumentParser(
        description="import email into a cubicweb instance"
    )
    parser.add_argument(
        "endpoint",
        metavar="endpoint",
        type=str,
        help="cwclientlib endpoint of the cubicweb instance",
    )
    parser.add_argument(
        "mbox",
        metavar="mailbox",
        type=argparse.FileType("rb"),
        nargs="+",
        help="mbox files to import (- for stdin)",
    )
    parser.add_argument(
        "-S",
        "--skipsign",
        action="store_true",
        default=False,
        help="do not create EmailPart for PGP/GPG signatures",
    )
    args = parser.parse_args()

    proxy = cwproxy_for(args.endpoint)

    importer = Importer(proxy, skipsign=args.skipsign)
    for f in args.mbox:
        try:
            f.seek(0)
        except OSError:
            buf = BytesIO()
            buf.writelines(f)
            buf.seek(0)
            f = buf
        importer.import_mbox_stream(f)


if __name__ == "__main__":
    main()
