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
import json
import time
from datetime import datetime, timezone
from browserstack_sdk.sdk_cli.bstack1lllll1l1l1_opy_ import (
    bstack1llllllll1l_opy_,
    bstack1lllll1l11l_opy_,
    bstack1lllllll1ll_opy_,
    bstack111111l111_opy_,
    bstack1llllllll11_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1ll1lll_opy_ import bstack1llll11l111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1llll1111ll_opy_, bstack1lll11ll111_opy_, bstack1ll1lll1l11_opy_
from browserstack_sdk.sdk_cli.bstack1ll11111l11_opy_ import bstack1l1llll1lll_opy_
from typing import Tuple, Dict, Any, List, Union
from bstack_utils.helper import bstack1l1lll1111l_opy_
from browserstack_sdk import sdk_pb2 as structs
from bstack_utils.measure import measure
from bstack_utils.constants import *
from typing import Tuple, List, Any
class bstack1lll1ll1l1l_opy_(bstack1l1llll1lll_opy_):
    bstack1l1l111l111_opy_ = bstack1ll1ll_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡷ࡯ࡶࡦࡴࡶࠦᎵ")
    bstack1l1ll111l11_opy_ = bstack1ll1ll_opy_ (u"ࠨࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡪࡹࡳࡪࡱࡱࡷࠧᎶ")
    bstack1l1l1111ll1_opy_ = bstack1ll1ll_opy_ (u"ࠢ࡯ࡱࡱࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡴࠤᎷ")
    bstack1l1l111ll11_opy_ = bstack1ll1ll_opy_ (u"ࠣࡶࡨࡷࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࡳࠣᎸ")
    bstack1l11lllllll_opy_ = bstack1ll1ll_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡵࡷࡥࡳࡩࡥࡠࡴࡨࡪࡸࠨᎹ")
    bstack1l1l1ll1l1l_opy_ = bstack1ll1ll_opy_ (u"ࠥࡧࡧࡺ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡥࡵࡩࡦࡺࡥࡥࠤᎺ")
    bstack1l1l111l11l_opy_ = bstack1ll1ll_opy_ (u"ࠦࡨࡨࡴࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡱࡥࡲ࡫ࠢᎻ")
    bstack1l1l11111l1_opy_ = bstack1ll1ll_opy_ (u"ࠧࡩࡢࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡷࡹࡧࡴࡶࡵࠥᎼ")
    def __init__(self):
        super().__init__(bstack1l1llllll1l_opy_=self.bstack1l1l111l111_opy_, frameworks=[bstack1llll11l111_opy_.NAME])
        if not self.is_enabled():
            return
        TestFramework.bstack1ll11l1l111_opy_((bstack1llll1111ll_opy_.BEFORE_EACH, bstack1lll11ll111_opy_.POST), self.bstack1l11l1lllll_opy_)
        TestFramework.bstack1ll11l1l111_opy_((bstack1llll1111ll_opy_.TEST, bstack1lll11ll111_opy_.PRE), self.bstack1ll11l11lll_opy_)
        TestFramework.bstack1ll11l1l111_opy_((bstack1llll1111ll_opy_.TEST, bstack1lll11ll111_opy_.POST), self.bstack1ll111l1l1l_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11l1lllll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1lll1l11_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_],
        *args,
        **kwargs,
    ):
        bstack1l1llll1ll1_opy_ = self.bstack1l11l1ll11l_opy_(instance.context)
        if not bstack1l1llll1ll1_opy_:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠨࡳࡦࡶࡢࡥࡨࡺࡩࡷࡧࡢࡨࡷ࡯ࡶࡦࡴࡶ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡨࡲࡶࠥ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯࠾ࠤᎽ") + str(bstack1llllll1111_opy_) + bstack1ll1ll_opy_ (u"ࠢࠣᎾ"))
        f.bstack1lllll1ll1l_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1ll111l11_opy_, bstack1l1llll1ll1_opy_)
        bstack1l11l1l1l1l_opy_ = self.bstack1l11l1ll11l_opy_(instance.context, bstack1l11l1l1ll1_opy_=False)
        f.bstack1lllll1ll1l_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l1111ll1_opy_, bstack1l11l1l1l1l_opy_)
    def bstack1ll11l11lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1lll1l11_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llllll1111_opy_, *args, **kwargs)
        if not f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l111l11l_opy_, False):
            self.__1l11l1l1lll_opy_(f,instance,bstack1llllll1111_opy_)
    def bstack1ll111l1l1l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1lll1l11_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llllll1111_opy_, *args, **kwargs)
        if not f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l111l11l_opy_, False):
            self.__1l11l1l1lll_opy_(f, instance, bstack1llllll1111_opy_)
        if not f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l11111l1_opy_, False):
            self.__1l11l1ll1l1_opy_(f, instance, bstack1llllll1111_opy_)
    def bstack1l11l1lll1l_opy_(
        self,
        f: bstack1llll11l111_opy_,
        driver: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if not f.bstack1l1lllll1ll_opy_(instance):
            return
        if f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l11111l1_opy_, False):
            return
        driver.execute_script(
            bstack1ll1ll_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂࠨᎿ").format(
                json.dumps(
                    {
                        bstack1ll1ll_opy_ (u"ࠤࡤࡧࡹ࡯࡯࡯ࠤᏀ"): bstack1ll1ll_opy_ (u"ࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨᏁ"),
                        bstack1ll1ll_opy_ (u"ࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢᏂ"): {bstack1ll1ll_opy_ (u"ࠧࡹࡴࡢࡶࡸࡷࠧᏃ"): result},
                    }
                )
            )
        )
        f.bstack1lllll1ll1l_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l11111l1_opy_, True)
    def bstack1l11l1ll11l_opy_(self, context: bstack1llllllll11_opy_, bstack1l11l1l1ll1_opy_= True):
        if bstack1l11l1l1ll1_opy_:
            bstack1l1llll1ll1_opy_ = self.bstack1l1llllll11_opy_(context, reverse=True)
        else:
            bstack1l1llll1ll1_opy_ = self.bstack1ll111111ll_opy_(context, reverse=True)
        return [f for f in bstack1l1llll1ll1_opy_ if f[1].state != bstack1llllllll1l_opy_.QUIT]
    @measure(event_name=EVENTS.bstack1ll1l11l11_opy_, stage=STAGE.bstack1l1l111lll_opy_)
    def __1l11l1ll1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1lll1l11_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_],
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1ll1ll_opy_ (u"ࠨࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠦᏄ")).get(bstack1ll1ll_opy_ (u"ࠢࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦᏅ")):
            bstack1l1llll1ll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1ll111l11_opy_, [])
            if not bstack1l1llll1ll1_opy_:
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠣࡵࡨࡸࡤࡧࡣࡵ࡫ࡹࡩࡤࡪࡲࡪࡸࡨࡶࡸࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦᏆ") + str(bstack1llllll1111_opy_) + bstack1ll1ll_opy_ (u"ࠤࠥᏇ"))
                return
            driver = bstack1l1llll1ll1_opy_[0][0]()
            status = f.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1l11111ll_opy_, None)
            if not status:
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡷࡪࡺ࡟ࡢࡥࡷ࡭ࡻ࡫࡟ࡥࡴ࡬ࡺࡪࡸࡳ࠻ࠢࡱࡳࠥࡹࡴࡢࡶࡸࡷࠥ࡬࡯ࡳࠢࡷࡩࡸࡺࠬࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࠧᏈ") + str(bstack1llllll1111_opy_) + bstack1ll1ll_opy_ (u"ࠦࠧᏉ"))
                return
            bstack1l1l1111l11_opy_ = {bstack1ll1ll_opy_ (u"ࠧࡹࡴࡢࡶࡸࡷࠧᏊ"): status.lower()}
            bstack1l11llllll1_opy_ = f.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1l111ll1l_opy_, None)
            if status.lower() == bstack1ll1ll_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭Ꮛ") and bstack1l11llllll1_opy_ is not None:
                bstack1l1l1111l11_opy_[bstack1ll1ll_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧᏌ")] = bstack1l11llllll1_opy_[0][bstack1ll1ll_opy_ (u"ࠨࡤࡤࡧࡰࡺࡲࡢࡥࡨࠫᏍ")][0] if isinstance(bstack1l11llllll1_opy_, list) else str(bstack1l11llllll1_opy_)
            driver.execute_script(
                bstack1ll1ll_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠢᏎ").format(
                    json.dumps(
                        {
                            bstack1ll1ll_opy_ (u"ࠥࡥࡨࡺࡩࡰࡰࠥᏏ"): bstack1ll1ll_opy_ (u"ࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢᏐ"),
                            bstack1ll1ll_opy_ (u"ࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣᏑ"): bstack1l1l1111l11_opy_,
                        }
                    )
                )
            )
            f.bstack1lllll1ll1l_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l11111l1_opy_, True)
    @measure(event_name=EVENTS.bstack11l11ll11l_opy_, stage=STAGE.bstack1l1l111lll_opy_)
    def __1l11l1l1lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1lll1l11_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_]
    ):
        from browserstack_sdk.sdk_cli.cli import cli
        if not cli.config.get(bstack1ll1ll_opy_ (u"ࠨࡴࡦࡵࡷࡇࡴࡴࡴࡦࡺࡷࡓࡵࡺࡩࡰࡰࡶࠦᏒ")).get(bstack1ll1ll_opy_ (u"ࠢࡴ࡭࡬ࡴࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤᏓ")):
            test_name = f.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l11l1ll111_opy_, None)
            if not test_name:
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡹ࡫ࡳࡵ࠼ࠣࡱ࡮ࡹࡳࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡱࡥࡲ࡫ࠢᏔ"))
                return
            bstack1l1llll1ll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1ll111l11_opy_, [])
            if not bstack1l1llll1ll1_opy_:
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠤࡶࡩࡹࡥࡡࡤࡶ࡬ࡺࡪࡥࡤࡳ࡫ࡹࡩࡷࡹ࠺ࠡࡰࡲࠤࡸࡺࡡࡵࡷࡶࠤ࡫ࡵࡲࠡࡶࡨࡷࡹ࠲ࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࠦᏕ") + str(bstack1llllll1111_opy_) + bstack1ll1ll_opy_ (u"ࠥࠦᏖ"))
                return
            for bstack1l1l1l1ll11_opy_, bstack1l11l1lll11_opy_ in bstack1l1llll1ll1_opy_:
                if not bstack1llll11l111_opy_.bstack1l1lllll1ll_opy_(bstack1l11l1lll11_opy_):
                    continue
                driver = bstack1l1l1l1ll11_opy_()
                if not driver:
                    continue
                driver.execute_script(
                    bstack1ll1ll_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࡾࠤᏗ").format(
                        json.dumps(
                            {
                                bstack1ll1ll_opy_ (u"ࠧࡧࡣࡵ࡫ࡲࡲࠧᏘ"): bstack1ll1ll_opy_ (u"ࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢᏙ"),
                                bstack1ll1ll_opy_ (u"ࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥᏚ"): {bstack1ll1ll_opy_ (u"ࠣࡰࡤࡱࡪࠨᏛ"): test_name},
                            }
                        )
                    )
                )
            f.bstack1lllll1ll1l_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l111l11l_opy_, True)
    def bstack1l1lll11lll_opy_(
        self,
        instance: bstack1ll1lll1l11_opy_,
        f: TestFramework,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llllll1111_opy_, *args, **kwargs)
        bstack1l1llll1ll1_opy_ = [d for d, _ in f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1ll111l11_opy_, [])]
        if not bstack1l1llll1ll1_opy_:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠤࡲࡲࡤࡧࡦࡵࡧࡵࡣࡹ࡫ࡳࡵ࠼ࠣࡲࡴࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡶࡲࠤࡱ࡯࡮࡬ࠤᏜ"))
            return
        if not bstack1l1lll1111l_opy_():
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣᏝ"))
            return
        for bstack1l11ll1111l_opy_ in bstack1l1llll1ll1_opy_:
            driver = bstack1l11ll1111l_opy_()
            if not driver:
                continue
            timestamp = int(time.time() * 1000)
            data = bstack1ll1ll_opy_ (u"ࠦࡔࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࡗࡾࡴࡣ࠻ࠤᏞ") + str(timestamp)
            driver.execute_script(
                bstack1ll1ll_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠥᏟ").format(
                    json.dumps(
                        {
                            bstack1ll1ll_opy_ (u"ࠨࡡࡤࡶ࡬ࡳࡳࠨᏠ"): bstack1ll1ll_opy_ (u"ࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤᏡ"),
                            bstack1ll1ll_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦᏢ"): {
                                bstack1ll1ll_opy_ (u"ࠤࡷࡽࡵ࡫ࠢᏣ"): bstack1ll1ll_opy_ (u"ࠥࡅࡳࡴ࡯ࡵࡣࡷ࡭ࡴࡴࠢᏤ"),
                                bstack1ll1ll_opy_ (u"ࠦࡩࡧࡴࡢࠤᏥ"): data,
                                bstack1ll1ll_opy_ (u"ࠧࡲࡥࡷࡧ࡯ࠦᏦ"): bstack1ll1ll_opy_ (u"ࠨࡤࡦࡤࡸ࡫ࠧᏧ")
                            }
                        }
                    )
                )
            )
    def bstack1l1ll1l11l1_opy_(
        self,
        instance: bstack1ll1lll1l11_opy_,
        f: TestFramework,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_],
        *args,
        **kwargs,
    ):
        self.bstack1l11l1lllll_opy_(f, instance, bstack1llllll1111_opy_, *args, **kwargs)
        keys = [
            bstack1lll1ll1l1l_opy_.bstack1l1ll111l11_opy_,
            bstack1lll1ll1l1l_opy_.bstack1l1l1111ll1_opy_,
        ]
        bstack1l1llll1ll1_opy_ = []
        for key in keys:
            bstack1l1llll1ll1_opy_.extend(f.bstack1llllll1lll_opy_(instance, key, []))
        if not bstack1l1llll1ll1_opy_:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠢࡰࡰࡢࡥ࡫ࡺࡥࡳࡡࡷࡩࡸࡺ࠺ࠡࡷࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡫࡯࡮ࡥࠢࡤࡲࡾࠦࡳࡦࡵࡶ࡭ࡴࡴࡳࠡࡶࡲࠤࡱ࡯࡮࡬ࠤᏨ"))
            return
        if f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l1ll1l1l_opy_, False):
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠣࡱࡱࡣࡦ࡬ࡴࡦࡴࡢࡸࡪࡹࡴ࠻ࠢࡆࡆ࡙ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡤࡴࡨࡥࡹ࡫ࡤࠣᏩ"))
            return
        self.bstack1ll111llll1_opy_()
        bstack111l1l111_opy_ = datetime.now()
        req = structs.TestSessionEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll11ll1l11_opy_)
        req.test_framework_name = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll11lllll1_opy_)
        req.test_framework_version = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l1ll11ll11_opy_)
        req.test_framework_state = bstack1llllll1111_opy_[0].name
        req.test_hook_state = bstack1llllll1111_opy_[1].name
        req.test_uuid = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1ll1l1111ll_opy_)
        for bstack1l1l1l1ll11_opy_, driver in bstack1l1llll1ll1_opy_:
            try:
                webdriver = bstack1l1l1l1ll11_opy_()
                if webdriver is None:
                    self.logger.debug(bstack1ll1ll_opy_ (u"ࠤ࡚ࡩࡧࡊࡲࡪࡸࡨࡶࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࠠࡪࡵࠣࡒࡴࡴࡥࠡࠪࡵࡩ࡫࡫ࡲࡦࡰࡦࡩࠥ࡫ࡸࡱ࡫ࡵࡩࡩ࠯ࠢᏪ"))
                    continue
                session = req.automation_sessions.add()
                session.provider = (
                    bstack1ll1ll_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠤᏫ")
                    if bstack1llll11l111_opy_.bstack1llllll1lll_opy_(driver, bstack1llll11l111_opy_.bstack1l11l1ll1ll_opy_, False)
                    else bstack1ll1ll_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࡤ࡭ࡲࡪࡦࠥᏬ")
                )
                session.ref = driver.ref()
                session.hub_url = bstack1llll11l111_opy_.bstack1llllll1lll_opy_(driver, bstack1llll11l111_opy_.bstack1l1l1l111l1_opy_, bstack1ll1ll_opy_ (u"ࠧࠨᏭ"))
                session.framework_name = driver.framework_name
                session.framework_version = driver.framework_version
                session.framework_session_id = bstack1llll11l111_opy_.bstack1llllll1lll_opy_(driver, bstack1llll11l111_opy_.bstack1l1l11ll1ll_opy_, bstack1ll1ll_opy_ (u"ࠨࠢᏮ"))
                caps = None
                if hasattr(webdriver, bstack1ll1ll_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᏯ")):
                    try:
                        caps = webdriver.capabilities
                        self.logger.debug(bstack1ll1ll_opy_ (u"ࠣࡕࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࡦࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠢࡧ࡭ࡷ࡫ࡣࡵ࡮ࡼࠤ࡫ࡸ࡯࡮ࠢࡧࡶ࡮ࡼࡥࡳ࠰ࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᏰ"))
                    except Exception as e:
                        self.logger.debug(bstack1ll1ll_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠡࡨࡵࡳࡲࠦࡤࡳ࡫ࡹࡩࡷ࠴ࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷ࠿ࠦࠢᏱ") + str(e) + bstack1ll1ll_opy_ (u"ࠥࠦᏲ"))
                try:
                    bstack1l11ll11111_opy_ = json.dumps(caps).encode(bstack1ll1ll_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᏳ")) if caps else bstack1l11l1llll1_opy_ (u"ࠧࢁࡽࠣᏴ")
                    req.capabilities = bstack1l11ll11111_opy_
                except Exception as e:
                    self.logger.debug(bstack1ll1ll_opy_ (u"ࠨࡧࡦࡶࡢࡧࡧࡺ࡟ࡦࡸࡨࡲࡹࡀࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡴࡤࠡࡵࡨࡶ࡮ࡧ࡬ࡪࡼࡨࠤࡨࡧࡰࡴࠢࡩࡳࡷࠦࡲࡦࡳࡸࡩࡸࡺ࠺ࠡࠤᏵ") + str(e) + bstack1ll1ll_opy_ (u"ࠢࠣ᏶"))
            except Exception as e:
                self.logger.error(bstack1ll1ll_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡩࡸࡩࡷࡧࡵࠤ࡮ࡺࡥ࡮࠼ࠣࠦ᏷") + str(str(e)) + bstack1ll1ll_opy_ (u"ࠤࠥᏸ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        return req
    def bstack1ll1l11l11l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1lll1l11_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_],
        *args,
        **kwargs
    ):
        bstack1l1llll1ll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1ll111l11_opy_, [])
        if not bstack1l1lll1111l_opy_() and len(bstack1l1llll1ll1_opy_) == 0:
            bstack1l1llll1ll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l1111ll1_opy_, [])
        if not bstack1l1llll1ll1_opy_:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡳࡳࡥࡢࡦࡨࡲࡶࡪࡥࡴࡦࡵࡷ࠾ࠥࡴ࡯ࠡࡦࡵ࡭ࡻ࡫ࡲࡴࠢࡩࡳࡷࠦࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰ࠿ࡾ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᏹ") + str(kwargs) + bstack1ll1ll_opy_ (u"ࠦࠧᏺ"))
            return {}
        if len(bstack1l1llll1ll1_opy_) > 1:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠧࡵ࡮ࡠࡤࡨࡪࡴࡸࡥࡠࡶࡨࡷࡹࡀࠠࡼ࡮ࡨࡲ࠭ࡪࡲࡪࡸࡨࡶࡤ࡯࡮ࡴࡶࡤࡲࡨ࡫ࡳࠪࡿࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᏻ") + str(kwargs) + bstack1ll1ll_opy_ (u"ࠨࠢᏼ"))
            return {}
        bstack1l1l1l1ll11_opy_, bstack1l1l1l1lll1_opy_ = bstack1l1llll1ll1_opy_[0]
        driver = bstack1l1l1l1ll11_opy_()
        if not driver:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡪࡲࡪࡸࡨࡶࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤᏽ") + str(kwargs) + bstack1ll1ll_opy_ (u"ࠣࠤ᏾"))
            return {}
        capabilities = f.bstack1llllll1lll_opy_(bstack1l1l1l1lll1_opy_, bstack1llll11l111_opy_.bstack1l1l11lllll_opy_)
        if not capabilities:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠤࡲࡲࡤࡨࡥࡧࡱࡵࡩࡤࡺࡥࡴࡶ࠽ࠤࡳࡵࠠࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠦࡦࡰࡷࡱࡨࠥ࡬࡯ࡳࠢ࡫ࡳࡴࡱ࡟ࡪࡰࡩࡳࡂࢁࡨࡰࡱ࡮ࡣ࡮ࡴࡦࡰࡿࠣࡥࡷ࡭ࡳ࠾ࡽࡤࡶ࡬ࡹࡽࠡ࡭ࡺࡥࡷ࡭ࡳ࠾ࠤ᏿") + str(kwargs) + bstack1ll1ll_opy_ (u"ࠥࠦ᐀"))
            return {}
        return capabilities.get(bstack1ll1ll_opy_ (u"ࠦࡦࡲࡷࡢࡻࡶࡑࡦࡺࡣࡩࠤᐁ"), {})
    def bstack1ll11l111ll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1lll1l11_opy_,
        bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_],
        *args,
        **kwargs
    ):
        bstack1l1llll1ll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1ll111l11_opy_, [])
        if not bstack1l1lll1111l_opy_() and len(bstack1l1llll1ll1_opy_) == 0:
            bstack1l1llll1ll1_opy_ = f.bstack1llllll1lll_opy_(instance, bstack1lll1ll1l1l_opy_.bstack1l1l1111ll1_opy_, [])
        if not bstack1l1llll1ll1_opy_:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡤࡳ࡫ࡹࡩࡷࡀࠠ࡯ࡱࠣࡨࡷ࡯ࡶࡦࡴࡶࠤ࡫ࡵࡲࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᐂ") + str(kwargs) + bstack1ll1ll_opy_ (u"ࠨࠢᐃ"))
            return
        if len(bstack1l1llll1ll1_opy_) > 1:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠢࡨࡧࡷࡣࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡠࡦࡵ࡭ࡻ࡫ࡲ࠻ࠢࡾࡰࡪࡴࠨࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰࡶࡸࡦࡴࡣࡦࡵࠬࢁࠥࡪࡲࡪࡸࡨࡶࡸࠦࡦࡰࡴࠣ࡬ࡴࡵ࡫ࡠ࡫ࡱࡪࡴࡃࡻࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࢀࠤࡦࡸࡧࡴ࠿ࡾࡥࡷ࡭ࡳࡾࠢ࡮ࡻࡦࡸࡧࡴ࠿ࠥᐄ") + str(kwargs) + bstack1ll1ll_opy_ (u"ࠣࠤᐅ"))
        bstack1l1l1l1ll11_opy_, bstack1l1l1l1lll1_opy_ = bstack1l1llll1ll1_opy_[0]
        driver = bstack1l1l1l1ll11_opy_()
        if not driver:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠤࡪࡩࡹࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡨࡷ࡯ࡶࡦࡴ࠽ࠤࡳࡵࠠࡥࡴ࡬ࡺࡪࡸࠠࡧࡱࡵࠤ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵ࠽ࡼࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࢁࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᐆ") + str(kwargs) + bstack1ll1ll_opy_ (u"ࠥࠦᐇ"))
            return
        return driver