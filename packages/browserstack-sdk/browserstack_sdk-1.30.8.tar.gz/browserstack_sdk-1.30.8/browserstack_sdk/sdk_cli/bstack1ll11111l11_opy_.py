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
from browserstack_sdk.sdk_cli.bstack1llll1l1ll1_opy_ import bstack1llll1l1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1l1l1_opy_ import (
    bstack1llllllll1l_opy_,
    bstack1lllll1l11l_opy_,
    bstack1lllllll1ll_opy_,
    bstack111111l111_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1ll1lll_opy_ import bstack1llll11l111_opy_
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1ll1l_opy_
from browserstack_sdk.sdk_cli.bstack1llll1ll1l1_opy_ import bstack1llllllll11_opy_
from typing import Tuple, Dict, Any, List, Callable
from browserstack_sdk.sdk_cli.bstack1llll1l1ll1_opy_ import bstack1llll1l1l1l_opy_
import weakref
class bstack1l1llll1lll_opy_(bstack1llll1l1l1l_opy_):
    bstack1l1llllll1l_opy_: str
    frameworks: List[str]
    drivers: Dict[str, Tuple[Callable, bstack111111l111_opy_]]
    pages: Dict[str, Tuple[Callable, bstack111111l111_opy_]]
    def __init__(self, bstack1l1llllll1l_opy_: str, frameworks: List[str]):
        super().__init__()
        self.drivers = dict()
        self.pages = dict()
        self.bstack1l1lllll1l1_opy_ = dict()
        self.bstack1l1llllll1l_opy_ = bstack1l1llllll1l_opy_
        self.frameworks = frameworks
        bstack1ll1ll1ll1l_opy_.bstack1ll11l1l111_opy_((bstack1llllllll1l_opy_.bstack1lllll11l11_opy_, bstack1lllll1l11l_opy_.POST), self.__1l1lllllll1_opy_)
        if any(bstack1llll11l111_opy_.NAME in f.lower().strip() for f in frameworks):
            bstack1llll11l111_opy_.bstack1ll11l1l111_opy_(
                (bstack1llllllll1l_opy_.bstack1lllll11l1l_opy_, bstack1lllll1l11l_opy_.PRE), self.__1ll11111111_opy_
            )
            bstack1llll11l111_opy_.bstack1ll11l1l111_opy_(
                (bstack1llllllll1l_opy_.QUIT, bstack1lllll1l11l_opy_.POST), self.__1l1lllll111_opy_
            )
    def __1l1lllllll1_opy_(
        self,
        f: bstack1ll1ll1ll1l_opy_,
        bstack1l1lllll11l_opy_: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            instance, method_name = exec
            if method_name != bstack1ll1ll_opy_ (u"ࠢ࡯ࡧࡺࡣࡵࡧࡧࡦࠤቄ"):
                return
            contexts = bstack1l1lllll11l_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack1ll1ll_opy_ (u"ࠣࡣࡥࡳࡺࡺ࠺ࡣ࡮ࡤࡲࡰࠨቅ") in page.url:
                                self.logger.debug(bstack1ll1ll_opy_ (u"ࠤࡖࡸࡴࡸࡩ࡯ࡩࠣࡸ࡭࡫ࠠ࡯ࡧࡺࠤࡵࡧࡧࡦࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠦቆ"))
                                self.pages[instance.ref()] = weakref.ref(page), instance
                                bstack1lllllll1ll_opy_.bstack1lllll1ll1l_opy_(instance, self.bstack1l1llllll1l_opy_, True)
                                self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡣࡤࡵ࡮ࡠࡲࡤ࡫ࡪࡥࡩ࡯࡫ࡷ࠾ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣቇ") + str(instance.ref()) + bstack1ll1ll_opy_ (u"ࠦࠧቈ"))
        except Exception as e:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸࡺ࡯ࡳ࡫ࡱ࡫ࠥࡴࡥࡸࠢࡳࡥ࡬࡫ࠠ࠻ࠤ቉"),e)
    def __1ll11111111_opy_(
        self,
        f: bstack1llll11l111_opy_,
        driver: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if instance.ref() in self.drivers or bstack1lllllll1ll_opy_.bstack1llllll1lll_opy_(instance, self.bstack1l1llllll1l_opy_, False):
            return
        if not f.bstack1ll1111lll1_opy_(f.hub_url(driver)):
            self.bstack1l1lllll1l1_opy_[instance.ref()] = weakref.ref(driver), instance
            bstack1lllllll1ll_opy_.bstack1lllll1ll1l_opy_(instance, self.bstack1l1llllll1l_opy_, True)
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠨ࡟ࡠࡱࡱࡣࡸ࡫࡬ࡦࡰ࡬ࡹࡲࡥࡩ࡯࡫ࡷ࠾ࠥࡴ࡯࡯ࡡࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡦࡵ࡭ࡻ࡫ࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࠦቊ") + str(instance.ref()) + bstack1ll1ll_opy_ (u"ࠢࠣቋ"))
            return
        self.drivers[instance.ref()] = weakref.ref(driver), instance
        bstack1lllllll1ll_opy_.bstack1lllll1ll1l_opy_(instance, self.bstack1l1llllll1l_opy_, True)
        self.logger.debug(bstack1ll1ll_opy_ (u"ࠣࡡࡢࡳࡳࡥࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡠ࡫ࡱ࡭ࡹࡀࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࠥቌ") + str(instance.ref()) + bstack1ll1ll_opy_ (u"ࠤࠥቍ"))
    def __1l1lllll111_opy_(
        self,
        f: bstack1llll11l111_opy_,
        driver: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, _ = exec
        if not instance.ref() in self.drivers:
            return
        self.bstack1ll1111111l_opy_(instance)
        self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡣࡤࡵ࡮ࡠࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡵࡺ࡯ࡴ࠻ࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࠧ቎") + str(instance.ref()) + bstack1ll1ll_opy_ (u"ࠦࠧ቏"))
    def bstack1l1llllll11_opy_(self, context: bstack1llllllll11_opy_, reverse=True) -> List[Tuple[Callable, bstack111111l111_opy_]]:
        matches = []
        if self.pages:
            for data in self.pages.values():
                if data[1].bstack1ll111111l1_opy_(context):
                    matches.append(data)
        if self.drivers:
            for data in self.drivers.values():
                if (
                    bstack1llll11l111_opy_.bstack1l1lllll1ll_opy_(data[1])
                    and data[1].bstack1ll111111l1_opy_(context)
                    and getattr(data[0](), bstack1ll1ll_opy_ (u"ࠧࡹࡥࡴࡵ࡬ࡳࡳࡥࡩࡥࠤቐ"), False)
                ):
                    matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1lllll1lll1_opy_, reverse=reverse)
    def bstack1ll111111ll_opy_(self, context: bstack1llllllll11_opy_, reverse=True) -> List[Tuple[Callable, bstack111111l111_opy_]]:
        matches = []
        for data in self.bstack1l1lllll1l1_opy_.values():
            if (
                data[1].bstack1ll111111l1_opy_(context)
                and getattr(data[0](), bstack1ll1ll_opy_ (u"ࠨࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠥቑ"), False)
            ):
                matches.append(data)
        return sorted(matches, key=lambda d: d[1].bstack1lllll1lll1_opy_, reverse=reverse)
    def bstack1l1llllllll_opy_(self, instance: bstack111111l111_opy_) -> bool:
        return instance and instance.ref() in self.drivers
    def bstack1ll1111111l_opy_(self, instance: bstack111111l111_opy_) -> bool:
        if self.bstack1l1llllllll_opy_(instance):
            self.drivers.pop(instance.ref())
            bstack1lllllll1ll_opy_.bstack1lllll1ll1l_opy_(instance, self.bstack1l1llllll1l_opy_, False)
            return True
        return False