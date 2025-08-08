import unittest

from cubicweb_email.emailcites import parse_body


class ParseBodyTC(unittest.TestCase):
    def test_remove_sig(self):
        parsedmsg = parse_body(
            """
Des gens qui se sont mis sur le secteur erp avec du zope, du php, de postgresql et du debian : pimentech.

jpl/crm/compta/paie intégré : http://www.pimentech.fr/solutions/pimenstud
gestion/compta :              http://www.pimentech.fr/solutions/pimengest
travail collaboratif :        http://www.pimentech.fr/solutions/notesgroup
CRM :                         http://www.pimentech.fr/solutions/crm

--
Alexandre Fayolle
"""
        )
        self.assertMultiLineEqual(
            parsedmsg.actual_content,
            """Des gens qui se sont mis sur le secteur erp avec du zope, du php, de postgresql et du debian : pimentech.

jpl/crm/compta/paie intégré : http://www.pimentech.fr/solutions/pimenstud
gestion/compta :              http://www.pimentech.fr/solutions/pimengest
travail collaboratif :        http://www.pimentech.fr/solutions/notesgroup
CRM :                         http://www.pimentech.fr/solutions/crm""",
        )
        self.assertMultiLineEqual(parsedmsg.cited_content, "")

    def test_remove_cites(self):
        parsedmsg = parse_body(
            """
On Tue, Jan 08, 2008 at 10:08:46AM +0100, Alexandre Fayolle wrote:
> Des gens qui se sont mis sur le secteur erp avec du zope, du php, de postgresql et du debian : pimentech.
>
> jpl/crm/compta/paie intégré : http://www.pimentech.fr/solutions/pimenstud
> gestion/compta :              http://www.pimentech.fr/solutions/pimengest
> travail collaboratif :        http://www.pimentech.fr/solutions/notesgroup
> CRM :                         http://www.pimentech.fr/solutions/crmi

leur solution CRM est même basé sur Zope...

--
Sylvain Thénault                               LOGILAB, Paris (France)
Formations Python, Zope, Plone, Debian:  http://www.logilab.fr/formations
Développement logiciel sur mesure:       http://www.logilab.fr/services
Python et calcul scientifique:           http://www.logilab.fr/science
"""
        )
        self.assertMultiLineEqual(
            parsedmsg.actual_content, """leur solution CRM est même basé sur Zope..."""
        )
        self.assertMultiLineEqual(
            parsedmsg.cited_content,
            """On Tue, Jan 08, 2008 at 10:08:46AM +0100, Alexandre Fayolle wrote:
Des gens qui se sont mis sur le secteur erp avec du zope, du php, de postgresql et du debian : pimentech.
jpl/crm/compta/paie intégré : http://www.pimentech.fr/solutions/pimenstud
gestion/compta :              http://www.pimentech.fr/solutions/pimengest
travail collaboratif :        http://www.pimentech.fr/solutions/notesgroup
CRM :                         http://www.pimentech.fr/solutions/crmi""",
        )

    def test_ml(self):
        parsedmsg = parse_body(
            """
On Wed, Jan 23, 2008 at 06:48:22PM +0100, Maarten ter Huurne wrote:
> I wrote on 2008-01-23 06:27:07 PM:
>
> [Lotus Notes ate my whitespace, here is the proper code layout, I hope]
>
> > ===
> > class SomeClass:
> >
> >     def __m(self):
> >         pass
> >
> >     SomeClass().__m()
> > ===
>

Hi Marteen,

did you actually execute that code ?

> Bye,
> Maarten

> _______________________________________________
> Python-Projects mailing list
> Python-Projects@lists.logilab.org
> http://lists.logilab.org/mailman/listinfo/python-projects
_______________________________________________
Python-Projects mailing list
Python-Projects@lists.logilab.org
http://lists.logilab.org/mailman/listinfo/python-projects
"""
        )
        self.assertMultiLineEqual(
            parsedmsg.actual_content,
            """Hi Marteen,

did you actually execute that code ?
_______________________________________________
Python-Projects mailing list
Python-Projects@lists.logilab.org
http://lists.logilab.org/mailman/listinfo/python-projects""",
        )
        self.assertMultiLineEqual(
            parsedmsg.cited_content,
            """On Wed, Jan 23, 2008 at 06:48:22PM +0100, Maarten ter Huurne wrote:
I wrote on 2008-01-23 06:27:07 PM:
[Lotus Notes ate my whitespace, here is the proper code layout, I hope]
===
class SomeClass:
def __m(self):
pass
SomeClass().__m()
===
Bye,
Maarten
_______________________________________________
Python-Projects mailing list
Python-Projects@lists.logilab.org
http://lists.logilab.org/mailman/listinfo/python-projects""",
        )


if __name__ == "__main__":
    unittest.main()
