# greaseweazle/image/img.py
#
# Written & released by Keir Fraser <keir.xen@gmail.com>
#
# This is free and unencumbered software released into the public domain.
# See the file COPYING for more details, or visit <http://unlicense.org>.

from typing import Dict, Tuple, Optional, Any

from greaseweazle import error
from greaseweazle.codec import codec
from greaseweazle.flux import HasFlux
from greaseweazle.image.img import IMG

class IBMXDF(IMG):
    default_format = "ibm.xdf"

    def from_bytes(self, dat: bytes) -> None:
        raise NotImplementedError

    def get_image(self) -> bytes:

        tdat = bytearray()

        # If min_cyls is specified, only emit extra cylinders if there is
        # valid data.
        max_cyl = None
        if self.min_cyls is not None:
            max_cyl = self.min_cyls - 1
            for (cyl, head) in self.track_list():
                if cyl > max_cyl and (cyl,head) in self.to_track:
                    track = self.to_track[cyl,head]
                    if track.nr_missing() < track.nsec:
                        max_cyl = cyl

        def get_track(cyl, head):
            if (cyl,head) in self.to_track:
                t = self.to_track[cyl,head]
            else:
                _t = self.fmt.mk_track(cyl, head)
                assert _t is not None # mypy
                t = _t
            return t

        for (cyl, head) in self.track_list():
            if max_cyl is not None and cyl > max_cyl:
                break
            t = get_track(cyl, head)
            if cyl == 0:
                if head == 0:
                    tdat += t.get_img_track()[512*8:]
                    next_track = get_track(0, 1)
                    tdat += next_track.get_img_track()[0:512]
                else:
                    tdat += tdat[-(512*11):]
                    tdat += t.get_img_track()[512:]
                    tdat += bytearray(512*5)
            else:
                tdat += t.get_img_track()

        return tdat

# Local variables:
# python-indent: 4
# End:
