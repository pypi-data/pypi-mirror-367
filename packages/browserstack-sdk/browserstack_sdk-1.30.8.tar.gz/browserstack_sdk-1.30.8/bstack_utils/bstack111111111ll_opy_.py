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
import threading
import logging
logger = logging.getLogger(__name__)
bstack1lllllllllll_opy_ = 1000
bstack111111111l1_opy_ = 2
class bstack1llllllll1l1_opy_:
    def __init__(self, handler, bstack1lllllllll1l_opy_=bstack1lllllllllll_opy_, bstack1llllllllll1_opy_=bstack111111111l1_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1lllllllll1l_opy_ = bstack1lllllllll1l_opy_
        self.bstack1llllllllll1_opy_ = bstack1llllllllll1_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack111111l1ll_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack11111111111_opy_()
    def bstack11111111111_opy_(self):
        self.bstack111111l1ll_opy_ = threading.Event()
        def bstack1111111111l_opy_():
            self.bstack111111l1ll_opy_.wait(self.bstack1llllllllll1_opy_)
            if not self.bstack111111l1ll_opy_.is_set():
                self.bstack1llllllll1ll_opy_()
        self.timer = threading.Thread(target=bstack1111111111l_opy_, daemon=True)
        self.timer.start()
    def bstack1lllllllll11_opy_(self):
        try:
            if self.bstack111111l1ll_opy_ and not self.bstack111111l1ll_opy_.is_set():
                self.bstack111111l1ll_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack1ll1ll_opy_ (u"ࠧ࡜ࡵࡷࡳࡵࡥࡴࡪ࡯ࡨࡶࡢࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯࠼ࠣࠫᾕ") + (str(e) or bstack1ll1ll_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡨࡵࡵ࡭ࡦࠣࡲࡴࡺࠠࡣࡧࠣࡧࡴࡴࡶࡦࡴࡷࡩࡩࠦࡴࡰࠢࡶࡸࡷ࡯࡮ࡨࠤᾖ")))
        finally:
            self.timer = None
    def bstack1llllllll11l_opy_(self):
        if self.timer:
            self.bstack1lllllllll11_opy_()
        self.bstack11111111111_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1lllllllll1l_opy_:
                threading.Thread(target=self.bstack1llllllll1ll_opy_).start()
    def bstack1llllllll1ll_opy_(self, source = bstack1ll1ll_opy_ (u"ࠩࠪᾗ")):
        with self.lock:
            if not self.queue:
                self.bstack1llllllll11l_opy_()
                return
            data = self.queue[:self.bstack1lllllllll1l_opy_]
            del self.queue[:self.bstack1lllllllll1l_opy_]
        self.handler(data)
        if source != bstack1ll1ll_opy_ (u"ࠪࡷ࡭ࡻࡴࡥࡱࡺࡲࠬᾘ"):
            self.bstack1llllllll11l_opy_()
    def shutdown(self):
        self.bstack1lllllllll11_opy_()
        while self.queue:
            self.bstack1llllllll1ll_opy_(source=bstack1ll1ll_opy_ (u"ࠫࡸ࡮ࡵࡵࡦࡲࡻࡳ࠭ᾙ"))