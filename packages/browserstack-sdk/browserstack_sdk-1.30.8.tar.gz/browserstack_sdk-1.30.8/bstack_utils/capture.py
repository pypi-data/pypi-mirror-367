# coding: UTF-8
import sys
bstack1l11111_opy_ = sys.version_info [0] == 2
bstack1ll_opy_ = 2048
bstack1l1lll1_opy_ = 7
def bstack1ll1ll_opy_ (bstack11l1l1_opy_):
    global bstack1ll1l1_opy_
    bstack1ll1111_opy_ = ord (bstack11l1l1_opy_ [-1])
    bstack1l1l1l_opy_ = bstack11l1l1_opy_ [:-1]
    bstack11l11_opy_ = bstack1ll1111_opy_ % len (bstack1l1l1l_opy_)
    bstack1l111_opy_ = bstack1l1l1l_opy_ [:bstack11l11_opy_] + bstack1l1l1l_opy_ [bstack11l11_opy_:]
    if bstack1l11111_opy_:
        bstack1l1l11l_opy_ = unicode () .join ([unichr (ord (char) - bstack1ll_opy_ - (bstack11ll1l_opy_ + bstack1ll1111_opy_) % bstack1l1lll1_opy_) for bstack11ll1l_opy_, char in enumerate (bstack1l111_opy_)])
    else:
        bstack1l1l11l_opy_ = str () .join ([chr (ord (char) - bstack1ll_opy_ - (bstack11ll1l_opy_ + bstack1ll1111_opy_) % bstack1l1lll1_opy_) for bstack11ll1l_opy_, char in enumerate (bstack1l111_opy_)])
    return eval (bstack1l1l11l_opy_)
import builtins
import logging
class bstack111lll1111_opy_:
    def __init__(self, handler):
        self._11ll111l1l1_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._11ll111ll11_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack1ll1ll_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧ᝸"), bstack1ll1ll_opy_ (u"ࠪࡨࡪࡨࡵࡨࠩ᝹"), bstack1ll1ll_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬ᝺"), bstack1ll1ll_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ᝻")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._11ll111l1ll_opy_
        self._11ll111lll1_opy_()
    def _11ll111l1ll_opy_(self, *args, **kwargs):
        self._11ll111l1l1_opy_(*args, **kwargs)
        message = bstack1ll1ll_opy_ (u"࠭ࠠࠨ᝼").join(map(str, args)) + bstack1ll1ll_opy_ (u"ࠧ࡝ࡰࠪ᝽")
        self._log_message(bstack1ll1ll_opy_ (u"ࠨࡋࡑࡊࡔ࠭᝾"), message)
    def _log_message(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack1ll1ll_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ᝿"): level, bstack1ll1ll_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫក"): msg})
    def _11ll111lll1_opy_(self):
        for level, bstack11ll111llll_opy_ in self._11ll111ll11_opy_.items():
            setattr(logging, level, self._11ll111ll1l_opy_(level, bstack11ll111llll_opy_))
    def _11ll111ll1l_opy_(self, level, bstack11ll111llll_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack11ll111llll_opy_(msg, *args, **kwargs)
            self._log_message(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._11ll111l1l1_opy_
        for level, bstack11ll111llll_opy_ in self._11ll111ll11_opy_.items():
            setattr(logging, level, bstack11ll111llll_opy_)