# pylint: disable=W0622
"""cubicweb-email packaging information"""

modname = "email"
distname = f"cubicweb-{modname}"

numversion = (2, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "Logilab"
author_email = "contact@logilab.fr"
web = f"http://www.cubicweb.org/project/{distname}"
description = "email component for the CubicWeb framework"
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]
__depends__ = {
    "cubicweb": ">= 4.0.0, < 6.0.0",
    "cubicweb_web": ">= 1.6.0, < 2.0.0",
    "cubicweb-file": ">= 4.2.0, < 5.0.0",
    "cwclientlib": ">= 1.6.0, < 2.0.0",
}
