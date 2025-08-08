"""unit tests for email mbox import functionnality"""

import unittest
from io import BytesIO
from os import mkdir
from os.path import exists, join

from cubicweb.pyramid.test import PyramidCWTest
from cwclientlib.cwproxy import CWProxy, SignedRequestAuth

from cwemail.mboximport import Importer


class MBOXImporterTC(PyramidCWTest):
    token_id = "mboximport"
    test_db_id = "mboximport"

    @classmethod
    def pre_setup_database(cls, cnx, config):
        cnx.create_entity(
            "AuthToken", id=cls.token_id, enabled=True, token_for_user=cnx.user.eid
        )
        cnx.commit()

    def setUp(self):
        super().setUp()
        with self.admin_access.client_cnx() as cnx:
            token = cnx.find("AuthToken", id=self.token_id).one()
            self.admineid = cnx.user.eid
            self.token = token.token
        auth = SignedRequestAuth(token_id=self.token_id, secret=self.token)
        self.client = CWProxy(base_url=self.config["base-url"], auth=auth)

    @unittest.skip("should be migrated to proper PyramidCWTest")
    def test_mbox_format(self):
        mi = Importer(self.client)
        mi.import_mbox(self.datapath("mbox"))
        with self.admin_access.client_cnx() as cnx:
            self._test_base(cnx)

    @unittest.skip("should be migrated to proper PyramidCWTest")
    def test_maildir_format(self):
        mi = Importer(self.client)
        maildirpath = self.datapath("maildir")
        newpath = join(maildirpath, "new")
        if not exists(newpath):
            mkdir(newpath)
        mi.import_maildir(maildirpath)
        with self.admin_access.client_cnx() as cnx:
            self._test_base(cnx)

    def _test_base(self, cnx):
        rset = cnx.execute("Any X, S ORDERBY S WHERE X is Email, X subject S")
        self.assertEqual(len(rset), 2, rset.rows)
        email = rset.get_entity(0, 0)
        self.assertEqual(
            email.subject,
            "Re: [Python-projects] Pylint: Disable-msg for a block or statement?",
        )
        self.assertEqual(email.sender[0].address, "pink@odahoda.de")
        self.assertEqual(email.sender[0].alias, "Benjamin Niemann")
        self.assertEqual(
            [r.address for r in email.recipients], ["python-projects@logilab.org"]
        )
        self.assertEqual([r.address for r in email.cc], [])
        self.assertEqual(
            email.in_thread[0].title,
            "[Python-projects] Pylint: Disable-msg for a block or statement?",
        )
        self.assertEqual(
            sorted([(f.data_name, f.data_format) for f in email.attachment]),
            [("astng.patch", "text/x-diff"), ("pylint.patch", "text/x-diff")],
        )
        assert not self.vreg.schema["parts"].inlined
        self.assertEqual(
            len(cnx.execute(f"Any P WHERE E parts P, E eid {email.eid}")), 2
        )
        self.assertEqual(len(email.parts), 2)
        part1, part2 = email.parts_in_order()
        self.assertEqual(part1.content_format, "text/plain")
        self.assertEqual(part2.content_format, "text/plain")
        self.assertEqual(
            part2.content,
            """_______________________________________________
Python-Projects mailing list
Python-Projects@lists.logilab.org
http://lists.logilab.org/mailman/listinfo/python-projects""",
        )

        email = rset.get_entity(1, 0)
        self.assertEqual(
            email.subject,
            "[Python-projects] pylint: False positive about field initialisation",
        )
        self.assertEqual(email.sender[0].address, "maarten.ter.huurne@philips.com")
        self.assertEqual(email.sender[0].alias, "Maarten ter Huurne")
        self.assertEqual(
            [r.address for r in email.recipients], ["python-projects@lists.logilab.org"]
        )
        self.assertEqual([r.address for r in email.cc], [])
        self.assertEqual(
            email.in_thread[0].title,
            "[Python-projects] pylint: False positive about field initialisation",
        )
        self.assertEqual([(f.data_name, f.data_format) for f in email.attachment], [])
        self.assertEqual(len(email.parts), 3)
        self.assertEqual(
            sorted([r.content_format for r in email.parts]),
            ["text/html", "text/plain", "text/plain"],
        )
        part1, part2 = email.parts_in_order()
        self.assertEqual(part1.content_format, "text/html")
        self.assertEqual(part2.content_format, "text/plain")
        self.assertEqual(
            part2.content,
            """_______________________________________________
Python-Projects mailing list
Python-Projects@lists.logilab.org
http://lists.logilab.org/mailman/listinfo/python-projects""",
        )
        part1, part2 = email.parts_in_order("text/plain")
        self.assertEqual(part1.content_format, "text/plain")
        self.assertEqual(part2.content_format, "text/plain")

    NOSUBJECT = b"""
From python-projects-bounces@lists.logilab.org  Tue Mar 28 17:06:41 2006
Return-Path: <python-projects-bounces@lists.logilab.org>
X-Original-To: sylvain.thenault@logilab.fr
Delivered-To: syt@logilab.fr
To: python-projects@lists.logilab.org
MIME-Version: 1.0
X-Mailer: Lotus Notes Release 6.0.3 September 26, 2003
Message-ID: <OFE9ED18DA.E3F2A23A-ONC125713F.00521FE5-C125713F.0052FE93@philips.com>
References: <xxx@blabla>
From: Maarten ter Huurne <MAARTEN.TER.HUURNE@PHILIPS.COM>
Date: Tue, 28 Mar 2006 17:05:23 +0200
X-MIMETrack: Serialize by Router on ehvrmh02/H/SERVER/PHILIPS(Release
\t6.5.3FP1HF291 | September 19, 2005) at 28/03/2006 17:05:23,
\tSerialize complete at 28/03/2006 17:05:23
X-BeenThere: python-projects@lists.logilab.org
X-Mailman-Version: 2.1.5
Precedence: list
Content-Type: multipart/mixed; boundary="===============1708445001=="
Mime-version: 1.0
Sender: python-projects-bounces@lists.logilab.org
Errors-To: python-projects-bounces@lists.logilab.org
X-Spambayes-Classification: ham; 0.00
Status: RO
Content-Length: 2915
Lines: 82

This is a multipart message in MIME format.
--===============1708445001==
Content-Type: multipart/alternative;
\tboundary="=_alternative 0052FE92C125713F_="

This is a multipart message in MIME format.
--=_alternative 0052FE92C125713F_=
Content-Type: text/plain; charset="US-ASCII"

Hi,

On the following program:
===
class C:
    def __init__(self):
        self.set(self, 'abc')
    def set(self, value):
        self.__value = value
        self.__length = len(value)
===
pylint reports:
===
W0201:  5:C.set: Attribute '__value' defined outside __init__
W0201:  6:C.set: Attribute '__length' defined outside __init__
===

Although strictly speaking they are indeed defined outside __init__, these
fields are guaranteed to be initialised when an object of type C is
constructed. It would be useful if pylint could recognise situations like
this one and not issue this warning.

Bye,
                Maarten

--=_alternative 0052FE92C125713F_=
Content-Type: text/html; charset="US-ASCII"


<br><font size=2 face="sans-serif">Hi,</font>
<br>
<br><font size=2 face="sans-serif">On the following program:</font>
<br><font size=2 face="sans-serif">===</font>
<br><font size=2 face="sans-serif">class C:</font>
<br><font size=2 face="sans-serif">&nbsp; &nbsp; def __init__(self):</font>
<br><font size=2 face="sans-serif">&nbsp; &nbsp; &nbsp; &nbsp; self.set(self,
'abc')</font>
<br><font size=2 face="sans-serif">&nbsp; &nbsp; def set(self, value):</font>
<br><font size=2 face="sans-serif">&nbsp; &nbsp; &nbsp; &nbsp; self.__value
= value</font>
<br><font size=2 face="sans-serif">&nbsp; &nbsp; &nbsp; &nbsp; self.__length
= len(value)</font>
<br><font size=2 face="sans-serif">===</font>
<br><font size=2 face="sans-serif">pylint reports:</font>
<br><font size=2 face="sans-serif">===</font>
<br><font size=2 face="sans-serif">W0201: &nbsp;5:C.set: Attribute '__value'
defined outside __init__</font>
<br><font size=2 face="sans-serif">W0201: &nbsp;6:C.set: Attribute '__length'
defined outside __init__</font>
<br><font size=2 face="sans-serif">===</font>
<br>
<br><font size=2 face="sans-serif">Although strictly speaking they are
indeed defined outside __init__, these fields are guaranteed to be initialised
when an object of type C is constructed. It would be useful if pylint could
recognise situations like this one and not issue this warning.</font>
<br>
<br><font size=2 face="sans-serif">Bye,</font>
<br><font size=2 face="sans-serif">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
&nbsp; &nbsp; &nbsp; Maarten</font>
<br>
--=_alternative 0052FE92C125713F_=--

--===============1708445001==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: inline

_______________________________________________
Python-Projects mailing list
Python-Projects@lists.logilab.org
http://lists.logilab.org/mailman/listinfo/python-projects
--===============1708445001==--
"""

    @unittest.skip("should be migrated to proper PyramidCWTest")
    def test_no_subject(self):
        mi = Importer(self.client)
        mi.import_mbox_stream(BytesIO(self.NOSUBJECT))
        with self.admin_access.client_cnx() as cnx:
            rset = cnx.execute("Any X ORDERBY S WHERE X is Email, X subject S")
            self.assertEqual(len(rset), 1)
            email = rset.get_entity(0, 0)
            self.assertEqual(email.subject, "(no subject)")
            self.assertEqual(email.references(), {"<xxx@blabla>"})

    @unittest.skip("should be migrated to proper PyramidCWTest")
    def test_double_import(self):
        mi = Importer(self.client)
        mi.import_mbox_stream(BytesIO(self.NOSUBJECT))
        mi.import_mbox_stream(BytesIO(self.NOSUBJECT))
        with self.admin_access.client_cnx() as cnx:
            rset = cnx.execute("Any X, S ORDERBY S WHERE X is Email, X subject S")
            self.assertEqual(len(rset), 1, rset.rows)

    @unittest.skip("should be migrated to proper PyramidCWTest")
    def test_address_detection(self):
        with self.admin_access.client_cnx() as cnx:
            # test both case normalization and canonicalization of email address
            eid1 = cnx.execute(
                'INSERT EmailAddress X: X address "maarten.ter.huurne@philips.com"'
            )[0][0]
            eid2 = cnx.execute(
                'INSERT EmailAddress X: X address "maarten@philips.com"'
            )[0][0]
            cnx.execute(f"SET X prefered_form Y WHERE X eid {eid1}, Y eid {eid2}")
            cnx.commit()
        mi = Importer(self.client)
        mi.import_mbox_stream(BytesIO(self.NOSUBJECT))
        with self.admin_access.client_cnx() as cnx:
            rset = cnx.execute("Any X ORDERBY S WHERE X is Email, X subject S")
            self.assertEqual(len(rset), 1)
            email = rset.get_entity(0, 0)
            self.assertEqual(email.sender[0].address, "maarten@philips.com")


if __name__ == "__main__":
    unittest.main()
