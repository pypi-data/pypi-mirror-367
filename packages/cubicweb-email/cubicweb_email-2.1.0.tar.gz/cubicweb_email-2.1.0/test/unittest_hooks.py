import unittest
from io import BytesIO
from os.path import join
from socket import gethostname

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.mail import construct_message_id
from cubicweb.pyramid.test import PyramidCWTest
from cwclientlib import cwproxy
from logilab.common.testlib import unittest_main

from cwemail.mboximport import Importer

MSG = """From sthenault@free.fr  Tue Jan 23 15:21:10 2007
Return-Path: <sthenault@free.fr>
X-Original-To: Sylvain.Thenault@logilab.fr
Delivered-To: syt@logilab.fr
Received: from tucana.logilab.fr (tucana.logilab.fr [172.17.0.4])
        by orion.logilab.fr (Postfix) with ESMTP id E4D79EAA37
        for <Sylvain.Thenault@logilab.fr>; Tue, 23 Jan 2007 15:21:09 +0100 (CET)
Received: from smtp2-g19.free.fr (smtp2-g19.free.fr [212.27.42.28])
        by tucana.logilab.fr (Postfix) with ESMTP id 23B3D7140CE
        for <Sylvain.Thenault@logilab.fr>; Tue, 23 Jan 2007 15:21:08 +0100 (CET)
Received: from nor75-16-82-239-114-67.fbx.proxad.net
        (cap31-2-82-224-153-77.fbx.proxad.net [82.224.153.77])
        by smtp2-g19.free.fr (Postfix) with ESMTP id B057D7D54
        for <Sylvain.Thenault@logilab.fr>; Tue, 23 Jan 2007 15:21:07 +0100 (CET)
MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: base64
Subject: =?utf-8?q?new_comment_for_bug_avoir_un_champ_=22python_compat=22_sur_les_?=
        =?utf-8?q?projets_=3F?=
From: =?utf-8?q?Sylvain_Th=C3=A9nault?= <Sylvain.Thenault@logilab.fr>
Reply-To: =?utf-8?q?Sylvain_Th=C3=A9nault?= <Sylvain.Thenault@logilab.fr>
X-ERUDI: jpl
To: Sylvain.Thenault@logilab.fr
Message-id: <iblaoliejr>
References: <rooteid=15058&eid=17244&timestamp=1169562059@%s.%s>
Date: Tue, 23 Jan 2007 15:21:07 +0100 (CET)
X-Spambayes-Classification: ham; 0.00
Status: RO
Content-Length: 122
Lines: 2
"""


class ChangeStateHooksTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.create_entity(
                "BlogEntry", title="une news !", content="cubicweb c'est beau"
            )
            cnx.create_entity("EmailAddress", address="devel@logilab.fr", alias="devel")
            cnx.commit()
        self.msg = MSG % (self.vreg.config.appid, gethostname())

    def test_email_change_state(self):
        with self.admin_access.client_cnx() as cnx:
            u = cnx.execute(
                'INSERT CWUser X: X login "toto", X upassword "sosafe", X in_group G '
                'WHERE G name "users"'
            ).get_entity(0, 0)
            subject = f":deactivate: {u.eid}"
            cnx.execute(
                "INSERT Email X: "
                "X headers %(headers)s, X subject %(subject)s,"
                'X messageid "hop", X sender EA',
                {"subject": subject, "headers": self.msg},
            )[0][0]
            cnx.commit()
            userstate = cnx.execute(
                "Any SN WHERE X in_state S, S name SN, X eid %(x)s", {"x": u.eid}
            )[0][0]
            self.assertEqual(userstate, "deactivated")
            self.assertEqual(
                u.cw_adapt_to("IWorkflowable").latest_trinfo().creator.login, "admin"
            )

    def test_email_change_state_trinfo_owner(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.execute('SET U use_email E WHERE U login "anon"')
            u = cnx.execute(
                'INSERT CWUser X: X login "toto", X upassword "sosafe", X in_group G '
                'WHERE G name "users"'
            ).get_entity(0, 0)
            subject = f":deactivate: {u.eid}"
            cnx.execute(
                "INSERT Email X: "
                "X headers %(headers)s, X subject %(subject)s,"
                'X messageid "hop", X sender EA',
                {"subject": subject, "headers": self.msg},
            )[0][0]
            cnx.commit()
            userstate = cnx.execute(
                "Any SN WHERE X in_state S, S name SN, X eid %(x)s", {"x": u.eid}
            )[0][0]
            self.assertEqual(userstate, "deactivated")
            self.assertEqual(
                u.cw_adapt_to("IWorkflowable").latest_trinfo().creator.login, "anon"
            )

    def test_email_change_state_wrong_eid(self):
        with self.admin_access.client_cnx() as cnx:
            ueid = cnx.execute(
                'INSERT CWUser X: X login "toto", X upassword "sosafe", X in_group G '
                'WHERE G name "users"'
            )[0][0]
            subject = ":deactivate: 10"
            cnx.execute(
                "INSERT Email X: "
                "X headers %(headers)s, X subject %(subject)s,"
                'X messageid "hop", X sender EA',
                {"subject": subject, "headers": self.msg},
            )[0][0]
            cnx.commit()
            userstate = cnx.execute(
                "Any SN WHERE X in_state S, S name SN, X eid %(x)s", {"x": ueid}
            )[0][0]
            self.assertEqual(userstate, "activated")

    def test_email_change_state_unexistant_eid(self):
        with self.admin_access.client_cnx() as cnx:
            ueid = cnx.execute(
                'INSERT CWUser X: X login "toto", X upassword "sosafe", X in_group G '
                'WHERE G name "users"'
            )[0][0]
            subject = ":deactivate: 999999"
            cnx.execute(
                "INSERT Email X: "
                "X headers %(headers)s, X subject %(subject)s,"
                'X messageid "hop", X sender EA',
                {"subject": subject, "headers": self.msg},
            )[0][0]
            cnx.commit()
            userstate = cnx.execute(
                "Any SN WHERE X in_state S, S name SN, X eid %(x)s", {"x": ueid}
            )[0][0]
            self.assertEqual(userstate, "activated")

    def test_email_change_state_unexistant_transition(self):
        with self.admin_access.client_cnx() as cnx:
            ueid = cnx.execute(
                'INSERT CWUser X: X login "toto", X upassword "sosafe", X in_group G '
                'WHERE G name "users"'
            )[0][0]
            subject = f":blabla: {ueid}"
            cnx.execute(
                "INSERT Email X: "
                "X headers %(headers)s, X subject %(subject)s,"
                'X messageid "hop", X sender EA',
                {"subject": subject, "headers": self.msg},
            )[0][0]
            cnx.commit()
            userstate = cnx.execute(
                "Any SN WHERE X in_state S, S name SN, X eid %(x)s", {"x": ueid}
            )[0][0]
            self.assertEqual(userstate, "activated")


MSG2 = """MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: base64
Subject: =?utf-8?q?new_comment_for_bug_avoir_un_champ_=22python_compat=22_sur_les_?=
        =?utf-8?q?projets_=3F?=
From: =?utf-8?q?Sylvain_Th=C3=A9nault?= <Sylvain.Thenault@logilab.fr>
Reply-To: =?utf-8?q?Sylvain_Th=C3=A9nault?= <Sylvain.Thenault@logilab.fr>
X-ERUDI: jpl
To: Sylvain.Thenault@logilab.fr
Message-id: <iblaoliejr>
References: %s
Date: Tue, 23 Jan 2007 15:21:07 +0100 (CET)
X-Spambayes-Classification: ham; 0.00
Status: RO
Content-Length: 122
Lines: 2

hop
hop
"""


class ReplyCommentHooksTC(PyramidCWTest):
    token_id = "mboximport"

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            self.b = cnx.create_entity(
                "BlogEntry", title="une news !", content="cubicweb c'est beau"
            ).eid
            e = cnx.create_entity(
                "EmailAddress", address="sylvain.thenault@logilab.fr", alias="syt"
            )
            cnx.execute(
                'SET X use_email E WHERE X login "anon", E eid %(e)s', {"e": e.eid}
            )
            cnx.create_entity(
                "AuthToken", enabled=True, id=self.token_id, token_for_user=cnx.user
            )
            cnx.commit()
            self.secret = cnx.execute(
                "String X WHERE T token X, T id %(id)s", {"id": self.token_id}
            )[0][0]

    @unittest.skip("XXX this should be migrated to proper PyramidCWTest")
    def test_comment_created(self):
        msg = open(
            join(self.datadir, "reply.mbox"), "rb"
        ).read() % construct_message_id(self.vreg.config.appid, self.b, False)
        mi = Importer(
            cwproxy.CWProxy(
                self.config["base-url"],
                auth=cwproxy.SignedRequestAuth(self.token_id, self.secret),
            )
        )
        mi.import_mbox_stream(BytesIO(msg.encode("utf-8")))
        with self.admin_access.client_cnx() as cnx:
            self.assertTrue(cnx.execute("Email X"))
            b = cnx.entity_from_eid(self.b)
            self.assertTrue(b.reverse_comments)
            c = b.reverse_comments[0]
            self.assertEqual(c.content_format, "text/plain")
            self.assertEqual(
                c.content,
                """New ticket for project erudi-email :

#22742 - erudi-email #22742: commentaires de mailbot
====================

description
-----------
Sur http://intranet.logilab.fr/jpl/ticket/22309 on voit un commentaire sign\xe9
mailbot. Ce serait mieux d'utiliser l'auteur du mail.

submitter
---------
alf

URL
---
http://intranet.logilab.fr/jpl/ticket/22742
(project URL: http://intranet.logilab.fr/jpl/project/erudi-email)""",
            )
            self.assertEqual(c.creator.login, "anon")
            self.assertEqual(sorted(u.login for u in c.owned_by), ["admin", "anon"])


if __name__ == "__main__":
    unittest_main()
