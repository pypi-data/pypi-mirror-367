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
import os
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1llll1ll1l1_opy_ import bstack1lllll11ll1_opy_
from browserstack_sdk.sdk_cli.utils.bstack1l11l1lll1_opy_ import bstack1l111111111_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1llll1111ll_opy_,
    bstack1ll1lll1l11_opy_,
    bstack1lll11ll111_opy_,
    bstack1l111l11l1l_opy_,
    bstack1lll1ll1111_opy_,
)
import traceback
from bstack_utils.helper import bstack1l1l1ll11ll_opy_
from bstack_utils.bstack11ll11ll1l_opy_ import bstack1lll1l1ll1l_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1ll1l1ll1ll_opy_ import bstack1llll1l1lll_opy_
from browserstack_sdk.sdk_cli.bstack111111ll11_opy_ import bstack111111l1l1_opy_
bstack1l1lll1ll1l_opy_ = bstack1l1l1ll11ll_opy_()
bstack1l1ll11lll1_opy_ = bstack1ll1ll_opy_ (u"ࠤࡘࡴࡱࡵࡡࡥࡧࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳ࠮ࠤᐢ")
bstack1l111ll11l1_opy_ = bstack1ll1ll_opy_ (u"ࠥࡌࡴࡵ࡫ࡍࡧࡹࡩࡱࠨᐣ")
bstack1l111ll111l_opy_ = bstack1ll1ll_opy_ (u"ࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠥᐤ")
bstack1l111lll1l1_opy_ = 1.0
_1l1ll1ll1l1_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack1l1111llll1_opy_ = bstack1ll1ll_opy_ (u"ࠧࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࡷࠧᐥ")
    bstack1l1111l1lll_opy_ = bstack1ll1ll_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࡢࡷࡹࡧࡲࡵࡧࡧࠦᐦ")
    bstack1l111ll1lll_opy_ = bstack1ll1ll_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᐧ")
    bstack1l111lll11l_opy_ = bstack1ll1ll_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡱࡧࡳࡵࡡࡶࡸࡦࡸࡴࡦࡦࠥᐨ")
    bstack1l11l11l11l_opy_ = bstack1ll1ll_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡲࡡࡴࡶࡢࡪ࡮ࡴࡩࡴࡪࡨࡨࠧᐩ")
    bstack1l111111ll1_opy_: bool
    bstack111111ll11_opy_: bstack111111l1l1_opy_  = None
    bstack1l111lllll1_opy_ = [
        bstack1llll1111ll_opy_.BEFORE_ALL,
        bstack1llll1111ll_opy_.AFTER_ALL,
        bstack1llll1111ll_opy_.BEFORE_EACH,
        bstack1llll1111ll_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack1l111lll1ll_opy_: Dict[str, str],
        bstack1ll111l1lll_opy_: List[str]=[bstack1ll1ll_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠢᐪ")],
        bstack111111ll11_opy_: bstack111111l1l1_opy_ = None,
        bstack1llll1ll111_opy_=None
    ):
        super().__init__(bstack1ll111l1lll_opy_, bstack1l111lll1ll_opy_, bstack111111ll11_opy_)
        self.bstack1l111111ll1_opy_ = any(bstack1ll1ll_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠣᐫ") in item.lower() for item in bstack1ll111l1lll_opy_)
        self.bstack1llll1ll111_opy_ = bstack1llll1ll111_opy_
    def track_event(
        self,
        context: bstack1l111l11l1l_opy_,
        test_framework_state: bstack1llll1111ll_opy_,
        test_hook_state: bstack1lll11ll111_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1llll1111ll_opy_.TEST or test_framework_state in PytestBDDFramework.bstack1l111lllll1_opy_:
            bstack1l111111111_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1llll1111ll_opy_.NONE:
            self.logger.warning(bstack1ll1ll_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵࡩࡩࠦࡣࡢ࡮࡯ࡦࡦࡩ࡫ࠡࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࡂࠨᐬ") + str(test_hook_state) + bstack1ll1ll_opy_ (u"ࠨࠢᐭ"))
            return
        if not self.bstack1l111111ll1_opy_:
            self.logger.warning(bstack1ll1ll_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡵ࡯ࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࠽ࠣᐮ") + str(str(self.bstack1ll111l1lll_opy_)) + bstack1ll1ll_opy_ (u"ࠣࠤᐯ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack1ll1ll_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥࡧࡲࡨࡵࡀࡿࡦࡸࡧࡴࡿࠣ࡯ࡼࡧࡲࡨࡵࡀࠦᐰ") + str(kwargs) + bstack1ll1ll_opy_ (u"ࠥࠦᐱ"))
            return
        instance = self.__1l1111l1l11_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡦࡸࡧࡴ࠿ࠥᐲ") + str(args) + bstack1ll1ll_opy_ (u"ࠧࠨᐳ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l111lllll1_opy_ and test_hook_state == bstack1lll11ll111_opy_.PRE:
                bstack1ll11l11l1l_opy_ = bstack1lll1l1ll1l_opy_.bstack1ll11ll11ll_opy_(EVENTS.bstack11l1ll1ll1_opy_.value)
                name = str(EVENTS.bstack11l1ll1ll1_opy_.name)+bstack1ll1ll_opy_ (u"ࠨ࠺ࠣᐴ")+str(test_framework_state.name)
                TestFramework.bstack1l111l1ll1l_opy_(instance, name, bstack1ll11l11l1l_opy_)
        except Exception as e:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࠤࡪࡸࡲࡰࡴࠣࡴࡷ࡫࠺ࠡࡽࢀࠦᐵ").format(e))
        try:
            if test_framework_state == bstack1llll1111ll_opy_.TEST:
                if not TestFramework.bstack1lllll111ll_opy_(instance, TestFramework.bstack1l1111lll1l_opy_) and test_hook_state == bstack1lll11ll111_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__1l1111l1ll1_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack1ll1ll_opy_ (u"ࠣ࡮ࡲࡥࡩ࡫ࡤࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᐶ") + str(test_hook_state) + bstack1ll1ll_opy_ (u"ࠤࠥᐷ"))
                if test_hook_state == bstack1lll11ll111_opy_.PRE and not TestFramework.bstack1lllll111ll_opy_(instance, TestFramework.bstack1l1l1ll1l11_opy_):
                    TestFramework.bstack1lllll1ll1l_opy_(instance, TestFramework.bstack1l1l1ll1l11_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__1l111l1l11l_opy_(instance, args)
                    self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡷࡪࡺࠠࡵࡧࡶࡸ࠲ࡹࡴࡢࡴࡷࠤ࡫ࡵࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᐸ") + str(test_hook_state) + bstack1ll1ll_opy_ (u"ࠦࠧᐹ"))
                elif test_hook_state == bstack1lll11ll111_opy_.POST and not TestFramework.bstack1lllll111ll_opy_(instance, TestFramework.bstack1l1llll1l11_opy_):
                    TestFramework.bstack1lllll1ll1l_opy_(instance, TestFramework.bstack1l1llll1l11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1ll1ll_opy_ (u"ࠧࡹࡥࡵࠢࡷࡩࡸࡺ࠭ࡦࡰࡧࠤ࡫ࡵࡲࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࡀࡿ࡮ࡴࡳࡵࡣࡱࡧࡪ࠴ࡲࡦࡨࠫ࠭ࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᐺ") + str(test_hook_state) + bstack1ll1ll_opy_ (u"ࠨࠢᐻ"))
            elif test_framework_state == bstack1llll1111ll_opy_.STEP:
                if test_hook_state == bstack1lll11ll111_opy_.PRE:
                    PytestBDDFramework.__1l11l11l111_opy_(instance, args)
                elif test_hook_state == bstack1lll11ll111_opy_.POST:
                    PytestBDDFramework.__1l111l1l1ll_opy_(instance, args)
            elif test_framework_state == bstack1llll1111ll_opy_.LOG and test_hook_state == bstack1lll11ll111_opy_.POST:
                PytestBDDFramework.__1l111ll1111_opy_(instance, *args)
            elif test_framework_state == bstack1llll1111ll_opy_.LOG_REPORT and test_hook_state == bstack1lll11ll111_opy_.POST:
                self.__1l111l1llll_opy_(instance, *args)
                self.__1l111l111l1_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack1l111lllll1_opy_:
                self.__11lllllll11_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡥࡷࡧࡱࡸ࠿ࠦࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᐼ") + str(instance.ref()) + bstack1ll1ll_opy_ (u"ࠣࠤᐽ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack1l1111l11ll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l111lllll1_opy_ and test_hook_state == bstack1lll11ll111_opy_.POST:
                name = str(EVENTS.bstack11l1ll1ll1_opy_.name)+bstack1ll1ll_opy_ (u"ࠤ࠽ࠦᐾ")+str(test_framework_state.name)
                bstack1ll11l11l1l_opy_ = TestFramework.bstack11llllll1l1_opy_(instance, name)
                bstack1lll1l1ll1l_opy_.end(EVENTS.bstack11l1ll1ll1_opy_.value, bstack1ll11l11l1l_opy_+bstack1ll1ll_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥᐿ"), bstack1ll11l11l1l_opy_+bstack1ll1ll_opy_ (u"ࠦ࠿࡫࡮ࡥࠤᑀ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࢁࠧᑁ").format(e))
    def bstack1l1ll1lllll_opy_(self):
        return self.bstack1l111111ll1_opy_
    def __1l111llll11_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack1ll1ll_opy_ (u"ࠨࡧࡦࡶࡢࡶࡪࡹࡵ࡭ࡶࠥᑂ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1ll1ll111_opy_(rep, [bstack1ll1ll_opy_ (u"ࠢࡸࡪࡨࡲࠧᑃ"), bstack1ll1ll_opy_ (u"ࠣࡱࡸࡸࡨࡵ࡭ࡦࠤᑄ"), bstack1ll1ll_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤᑅ"), bstack1ll1ll_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥᑆ"), bstack1ll1ll_opy_ (u"ࠦࡸࡱࡩࡱࡲࡨࡨࠧᑇ"), bstack1ll1ll_opy_ (u"ࠧࡲ࡯࡯ࡩࡵࡩࡵࡸࡴࡦࡺࡷࠦᑈ")])
        return None
    def __1l111l1llll_opy_(self, instance: bstack1ll1lll1l11_opy_, *args):
        result = self.__1l111llll11_opy_(*args)
        if not result:
            return
        failure = None
        bstack11111l111l_opy_ = None
        if result.get(bstack1ll1ll_opy_ (u"ࠨ࡯ࡶࡶࡦࡳࡲ࡫ࠢᑉ"), None) == bstack1ll1ll_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠢᑊ") and len(args) > 1 and getattr(args[1], bstack1ll1ll_opy_ (u"ࠣࡧࡻࡧ࡮ࡴࡦࡰࠤᑋ"), None) is not None:
            failure = [{bstack1ll1ll_opy_ (u"ࠩࡥࡥࡨࡱࡴࡳࡣࡦࡩࠬᑌ"): [args[1].excinfo.exconly(), result.get(bstack1ll1ll_opy_ (u"ࠥࡰࡴࡴࡧࡳࡧࡳࡶࡹ࡫ࡸࡵࠤᑍ"), None)]}]
            bstack11111l111l_opy_ = bstack1ll1ll_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࡅࡳࡴࡲࡶࠧᑎ") if bstack1ll1ll_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࠣᑏ") in getattr(args[1].excinfo, bstack1ll1ll_opy_ (u"ࠨࡴࡺࡲࡨࡲࡦࡳࡥࠣᑐ"), bstack1ll1ll_opy_ (u"ࠢࠣᑑ")) else bstack1ll1ll_opy_ (u"ࠣࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠤᑒ")
        bstack1l11l111111_opy_ = result.get(bstack1ll1ll_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᑓ"), TestFramework.bstack1l1111ll11l_opy_)
        if bstack1l11l111111_opy_ != TestFramework.bstack1l1111ll11l_opy_:
            TestFramework.bstack1lllll1ll1l_opy_(instance, TestFramework.bstack1l1ll11ll1l_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack1l111l1111l_opy_(instance, {
            TestFramework.bstack1l1l111ll1l_opy_: failure,
            TestFramework.bstack1l111ll1l1l_opy_: bstack11111l111l_opy_,
            TestFramework.bstack1l1l11111ll_opy_: bstack1l11l111111_opy_,
        })
    def __1l1111l1l11_opy_(
        self,
        context: bstack1l111l11l1l_opy_,
        test_framework_state: bstack1llll1111ll_opy_,
        test_hook_state: bstack1lll11ll111_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1llll1111ll_opy_.SETUP_FIXTURE:
            instance = self.__1l11l11111l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack1l1111lll11_opy_ bstack1l111llll1l_opy_ this to be bstack1ll1ll_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᑔ")
            if test_framework_state == bstack1llll1111ll_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l111111l1l_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1llll1111ll_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack1ll1ll_opy_ (u"ࠦࡳࡵࡤࡦࠤᑕ"), None), bstack1ll1ll_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᑖ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack1ll1ll_opy_ (u"ࠨ࡮ࡰࡦࡨࠦᑗ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack1ll1ll_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᑘ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1111111111_opy_(target) if target else None
        return instance
    def __11lllllll11_opy_(
        self,
        instance: bstack1ll1lll1l11_opy_,
        test_framework_state: bstack1llll1111ll_opy_,
        test_hook_state: bstack1lll11ll111_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack1l1111ll1ll_opy_ = TestFramework.bstack1llllll1lll_opy_(instance, PytestBDDFramework.bstack1l1111l1lll_opy_, {})
        if not key in bstack1l1111ll1ll_opy_:
            bstack1l1111ll1ll_opy_[key] = []
        bstack11lllllllll_opy_ = TestFramework.bstack1llllll1lll_opy_(instance, PytestBDDFramework.bstack1l111ll1lll_opy_, {})
        if not key in bstack11lllllllll_opy_:
            bstack11lllllllll_opy_[key] = []
        bstack1l11111llll_opy_ = {
            PytestBDDFramework.bstack1l1111l1lll_opy_: bstack1l1111ll1ll_opy_,
            PytestBDDFramework.bstack1l111ll1lll_opy_: bstack11lllllllll_opy_,
        }
        if test_hook_state == bstack1lll11ll111_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack1ll1ll_opy_ (u"ࠣ࡭ࡨࡽࠧᑙ"): key,
                TestFramework.bstack1l111l11lll_opy_: uuid4().__str__(),
                TestFramework.bstack1l11111l111_opy_: TestFramework.bstack1l11111lll1_opy_,
                TestFramework.bstack1l11l111lll_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1l11111l1ll_opy_: [],
                TestFramework.bstack1l1111l111l_opy_: hook_name,
                TestFramework.bstack1l1111l11l1_opy_: bstack1llll1l1lll_opy_.bstack1l111l1ll11_opy_()
            }
            bstack1l1111ll1ll_opy_[key].append(hook)
            bstack1l11111llll_opy_[PytestBDDFramework.bstack1l111lll11l_opy_] = key
        elif test_hook_state == bstack1lll11ll111_opy_.POST:
            bstack1l11l11l1l1_opy_ = bstack1l1111ll1ll_opy_.get(key, [])
            hook = bstack1l11l11l1l1_opy_.pop() if bstack1l11l11l1l1_opy_ else None
            if hook:
                result = self.__1l111llll11_opy_(*args)
                if result:
                    bstack1l111l11l11_opy_ = result.get(bstack1ll1ll_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᑚ"), TestFramework.bstack1l11111lll1_opy_)
                    if bstack1l111l11l11_opy_ != TestFramework.bstack1l11111lll1_opy_:
                        hook[TestFramework.bstack1l11111l111_opy_] = bstack1l111l11l11_opy_
                hook[TestFramework.bstack1l11111l1l1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1l1111l11l1_opy_] = bstack1llll1l1lll_opy_.bstack1l111l1ll11_opy_()
                self.bstack1l11l1111ll_opy_(hook)
                logs = hook.get(TestFramework.bstack1l111lll111_opy_, [])
                self.bstack1l1ll11l11l_opy_(instance, logs)
                bstack11lllllllll_opy_[key].append(hook)
                bstack1l11111llll_opy_[PytestBDDFramework.bstack1l11l11l11l_opy_] = key
        TestFramework.bstack1l111l1111l_opy_(instance, bstack1l11111llll_opy_)
        self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡ࡫ࡳࡴࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾ࡯ࡪࡿࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡮࡯ࡰ࡭ࡶࡣࡸࡺࡡࡳࡶࡨࡨࡂࢁࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࢃࠠࡩࡱࡲ࡯ࡸࡥࡦࡪࡰ࡬ࡷ࡭࡫ࡤ࠾ࠤᑛ") + str(bstack11lllllllll_opy_) + bstack1ll1ll_opy_ (u"ࠦࠧᑜ"))
    def __1l11l11111l_opy_(
        self,
        context: bstack1l111l11l1l_opy_,
        test_framework_state: bstack1llll1111ll_opy_,
        test_hook_state: bstack1lll11ll111_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1ll1ll111_opy_(args[0], [bstack1ll1ll_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᑝ"), bstack1ll1ll_opy_ (u"ࠨࡡࡳࡩࡱࡥࡲ࡫ࠢᑞ"), bstack1ll1ll_opy_ (u"ࠢࡱࡣࡵࡥࡲࡹࠢᑟ"), bstack1ll1ll_opy_ (u"ࠣ࡫ࡧࡷࠧᑠ"), bstack1ll1ll_opy_ (u"ࠤࡸࡲ࡮ࡺࡴࡦࡵࡷࠦᑡ"), bstack1ll1ll_opy_ (u"ࠥࡦࡦࡹࡥࡪࡦࠥᑢ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack1ll1ll_opy_ (u"ࠦࡸࡩ࡯ࡱࡧࠥᑣ")) else fixturedef.get(bstack1ll1ll_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᑤ"), None)
        fixturename = request.fixturename if hasattr(request, bstack1ll1ll_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࠦᑥ")) else None
        node = request.node if hasattr(request, bstack1ll1ll_opy_ (u"ࠢ࡯ࡱࡧࡩࠧᑦ")) else None
        target = request.node.nodeid if hasattr(node, bstack1ll1ll_opy_ (u"ࠣࡰࡲࡨࡪ࡯ࡤࠣᑧ")) else None
        baseid = fixturedef.get(bstack1ll1ll_opy_ (u"ࠤࡥࡥࡸ࡫ࡩࡥࠤᑨ"), None) or bstack1ll1ll_opy_ (u"ࠥࠦᑩ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack1ll1ll_opy_ (u"ࠦࡤࡶࡹࡧࡷࡱࡧ࡮ࡺࡥ࡮ࠤᑪ")):
            target = PytestBDDFramework.__1l111ll1ll1_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack1ll1ll_opy_ (u"ࠧࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠢᑫ")) else None
            if target and not TestFramework.bstack1111111111_opy_(target):
                self.__1l111111l1l_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡬ࡩࡹࡶࡸࡶࡪࡥࡥࡷࡧࡱࡸ࠿ࠦࡦࡢ࡮࡯ࡦࡦࡩ࡫ࠡࡶࡤࡶ࡬࡫ࡴ࠾ࡽࡷࡥࡷ࡭ࡥࡵࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥ࠾ࡽࡩ࡭ࡽࡺࡵࡳࡧࡱࡥࡲ࡫ࡽࠡࡰࡲࡨࡪࡃࡻ࡯ࡱࡧࡩࢂࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࠣᑬ") + str(test_hook_state) + bstack1ll1ll_opy_ (u"ࠢࠣᑭ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack1ll1ll_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱ࡬ࡦࡴࡤ࡭ࡧࡧࠤࡪࡼࡥ࡯ࡶࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁ࠳ࢁࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡧࡩ࡫ࡃࡻࡧ࡫ࡻࡸࡺࡸࡥࡥࡧࡩࢁࠥࡹࡣࡰࡲࡨࡁࢀࡹࡣࡰࡲࡨࢁࠥࡺࡡࡳࡩࡨࡸࡂࠨᑮ") + str(target) + bstack1ll1ll_opy_ (u"ࠤࠥᑯ"))
            return None
        instance = TestFramework.bstack1111111111_opy_(target)
        if not instance:
            self.logger.warning(bstack1ll1ll_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡥࡥࡸ࡫ࡩࡥ࠿ࡾࡦࡦࡹࡥࡪࡦࢀࠤࡹࡧࡲࡨࡧࡷࡁࠧᑰ") + str(target) + bstack1ll1ll_opy_ (u"ࠦࠧᑱ"))
            return None
        bstack1l1111111ll_opy_ = TestFramework.bstack1llllll1lll_opy_(instance, PytestBDDFramework.bstack1l1111llll1_opy_, {})
        if os.getenv(bstack1ll1ll_opy_ (u"࡙ࠧࡄࡌࡡࡆࡐࡎࡥࡆࡍࡃࡊࡣࡋࡏࡘࡕࡗࡕࡉࡘࠨᑲ"), bstack1ll1ll_opy_ (u"ࠨ࠱ࠣᑳ")) == bstack1ll1ll_opy_ (u"ࠢ࠲ࠤᑴ"):
            bstack1l111ll11ll_opy_ = bstack1ll1ll_opy_ (u"ࠣ࠼ࠥᑵ").join((scope, fixturename))
            bstack1l111l1l111_opy_ = datetime.now(tz=timezone.utc)
            bstack11llllll11l_opy_ = {
                bstack1ll1ll_opy_ (u"ࠤ࡮ࡩࡾࠨᑶ"): bstack1l111ll11ll_opy_,
                bstack1ll1ll_opy_ (u"ࠥࡸࡦ࡭ࡳࠣᑷ"): PytestBDDFramework.__1l111111l11_opy_(request.node, scenario),
                bstack1ll1ll_opy_ (u"ࠦ࡫࡯ࡸࡵࡷࡵࡩࠧᑸ"): fixturedef,
                bstack1ll1ll_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᑹ"): scope,
                bstack1ll1ll_opy_ (u"ࠨࡴࡺࡲࡨࠦᑺ"): None,
            }
            try:
                if test_hook_state == bstack1lll11ll111_opy_.POST and callable(getattr(args[-1], bstack1ll1ll_opy_ (u"ࠢࡨࡧࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᑻ"), None)):
                    bstack11llllll11l_opy_[bstack1ll1ll_opy_ (u"ࠣࡶࡼࡴࡪࠨᑼ")] = TestFramework.bstack1l1lll11l11_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll11ll111_opy_.PRE:
                bstack11llllll11l_opy_[bstack1ll1ll_opy_ (u"ࠤࡸࡹ࡮ࡪࠢᑽ")] = uuid4().__str__()
                bstack11llllll11l_opy_[PytestBDDFramework.bstack1l11l111lll_opy_] = bstack1l111l1l111_opy_
            elif test_hook_state == bstack1lll11ll111_opy_.POST:
                bstack11llllll11l_opy_[PytestBDDFramework.bstack1l11111l1l1_opy_] = bstack1l111l1l111_opy_
            if bstack1l111ll11ll_opy_ in bstack1l1111111ll_opy_:
                bstack1l1111111ll_opy_[bstack1l111ll11ll_opy_].update(bstack11llllll11l_opy_)
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡹࡵࡪࡡࡵࡧࡧࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡀࠦᑾ") + str(bstack1l1111111ll_opy_[bstack1l111ll11ll_opy_]) + bstack1ll1ll_opy_ (u"ࠦࠧᑿ"))
            else:
                bstack1l1111111ll_opy_[bstack1l111ll11ll_opy_] = bstack11llllll11l_opy_
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠧࡹࡡࡷࡧࡧࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡶࡧࡴࡶࡥ࠾ࡽࡶࡧࡴࡶࡥࡾࠢࡩ࡭ࡽࡺࡵࡳࡧࡀࡿࡹ࡫ࡳࡵࡡࡩ࡭ࡽࡺࡵࡳࡧࢀࠤࡹࡸࡡࡤ࡭ࡨࡨࡤ࡬ࡩࡹࡶࡸࡶࡪࡹ࠽ࠣᒀ") + str(len(bstack1l1111111ll_opy_)) + bstack1ll1ll_opy_ (u"ࠨࠢᒁ"))
        TestFramework.bstack1lllll1ll1l_opy_(instance, PytestBDDFramework.bstack1l1111llll1_opy_, bstack1l1111111ll_opy_)
        self.logger.debug(bstack1ll1ll_opy_ (u"ࠢࡴࡣࡹࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫ࡳ࠾ࡽ࡯ࡩࡳ࠮ࡴࡳࡣࡦ࡯ࡪࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴࠫࢀࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࠢᒂ") + str(instance.ref()) + bstack1ll1ll_opy_ (u"ࠣࠤᒃ"))
        return instance
    def __1l111111l1l_opy_(
        self,
        context: bstack1l111l11l1l_opy_,
        test_framework_state: bstack1llll1111ll_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1lllll11ll1_opy_.create_context(target)
        ob = bstack1ll1lll1l11_opy_(ctx, self.bstack1ll111l1lll_opy_, self.bstack1l111lll1ll_opy_, test_framework_state)
        TestFramework.bstack1l111l1111l_opy_(ob, {
            TestFramework.bstack1ll11lllll1_opy_: context.test_framework_name,
            TestFramework.bstack1l1ll11ll11_opy_: context.test_framework_version,
            TestFramework.bstack1l11111l11l_opy_: [],
            PytestBDDFramework.bstack1l1111llll1_opy_: {},
            PytestBDDFramework.bstack1l111ll1lll_opy_: {},
            PytestBDDFramework.bstack1l1111l1lll_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1lllll1ll1l_opy_(ob, TestFramework.bstack1l111l111ll_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1lllll1ll1l_opy_(ob, TestFramework.bstack1ll11ll1l11_opy_, context.platform_index)
        TestFramework.bstack1111111l11_opy_[ctx.id] = ob
        self.logger.debug(bstack1ll1ll_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠣࡧࡹࡾ࠮ࡪࡦࡀࡿࡨࡺࡸ࠯࡫ࡧࢁࠥࡺࡡࡳࡩࡨࡸࡂࢁࡴࡢࡴࡪࡩࡹࢃࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫ࡳ࠾ࠤᒄ") + str(TestFramework.bstack1111111l11_opy_.keys()) + bstack1ll1ll_opy_ (u"ࠥࠦᒅ"))
        return ob
    @staticmethod
    def __1l111l1l11l_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1ll1ll_opy_ (u"ࠫ࡮ࡪࠧᒆ"): id(step),
                bstack1ll1ll_opy_ (u"ࠬࡺࡥࡹࡶࠪᒇ"): step.name,
                bstack1ll1ll_opy_ (u"࠭࡫ࡦࡻࡺࡳࡷࡪࠧᒈ"): step.keyword,
            })
        meta = {
            bstack1ll1ll_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࠨᒉ"): {
                bstack1ll1ll_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᒊ"): feature.name,
                bstack1ll1ll_opy_ (u"ࠩࡳࡥࡹ࡮ࠧᒋ"): feature.filename,
                bstack1ll1ll_opy_ (u"ࠪࡨࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨᒌ"): feature.description
            },
            bstack1ll1ll_opy_ (u"ࠫࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭ᒍ"): {
                bstack1ll1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪᒎ"): scenario.name
            },
            bstack1ll1ll_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬᒏ"): steps,
            bstack1ll1ll_opy_ (u"ࠧࡦࡺࡤࡱࡵࡲࡥࡴࠩᒐ"): PytestBDDFramework.__1l1111lllll_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1l11l111l11_opy_: meta
            }
        )
    def bstack1l11l1111ll_opy_(self, hook: Dict[str, Any]) -> None:
        bstack1ll1ll_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡖࡲࡰࡥࡨࡷࡸ࡫ࡳࠡࡶ࡫ࡩࠥࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡳࡪ࡯࡬ࡰࡦࡸࠠࡵࡱࠣࡸ࡭࡫ࠠࡋࡣࡹࡥࠥ࡯࡭ࡱ࡮ࡨࡱࡪࡴࡴࡢࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡖ࡫࡭ࡸࠦ࡭ࡦࡶ࡫ࡳࡩࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡉࡨࡦࡥ࡮ࡷࠥࡺࡨࡦࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡ࡫ࡱࡷ࡮ࡪࡥࠡࢀ࠲࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠲࡙ࡵࡲ࡯ࡢࡦࡨࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡈࡲࡶࠥ࡫ࡡࡤࡪࠣࡪ࡮ࡲࡥࠡ࡫ࡱࠤ࡭ࡵ࡯࡬ࡡ࡯ࡩࡻ࡫࡬ࡠࡨ࡬ࡰࡪࡹࠬࠡࡴࡨࡴࡱࡧࡣࡦࡵ࡙ࠣࠦ࡫ࡳࡵࡎࡨࡺࡪࡲࠢࠡࡹ࡬ࡸ࡭ࠦࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠥࠤ࡮ࡴࠠࡪࡶࡶࠤࡵࡧࡴࡩ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡋࡩࠤࡦࠦࡦࡪ࡮ࡨࠤ࡮ࡴࠠࡵࡪࡨࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠ࡮ࡣࡷࡧ࡭࡫ࡳࠡࡣࠣࡱࡴࡪࡩࡧ࡫ࡨࡨࠥ࡮࡯ࡰ࡭࠰ࡰࡪࡼࡥ࡭ࠢࡩ࡭ࡱ࡫ࠬࠡ࡫ࡷࠤࡨࡸࡥࡢࡶࡨࡷࠥࡧࠠࡍࡱࡪࡉࡳࡺࡲࡺࠢࡲࡦ࡯࡫ࡣࡵࠢࡺ࡭ࡹ࡮ࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤࡩ࡫ࡴࡢ࡫࡯ࡷ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤࡘ࡯࡭ࡪ࡮ࡤࡶࡱࡿࠬࠡ࡫ࡷࠤࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢ࡯ࡳࡨࡧࡴࡦࡦࠣ࡭ࡳࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭࠱ࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡤࡼࠤࡷ࡫ࡰ࡭ࡣࡦ࡭ࡳ࡭ࠠࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧࠦࡷࡪࡶ࡫ࠤࠧࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬࠰ࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࡍࡵ࡯࡬ࡇࡹࡩࡳࡺࠢ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡕࡪࡨࠤࡨࡸࡥࡢࡶࡨࡨࠥࡒ࡯ࡨࡇࡱࡸࡷࡿࠠࡰࡤ࡭ࡩࡨࡺࡳࠡࡣࡵࡩࠥࡧࡤࡥࡧࡧࠤࡹࡵࠠࡵࡪࡨࠤ࡭ࡵ࡯࡬ࠩࡶࠤࠧࡲ࡯ࡨࡵࠥࠤࡱ࡯ࡳࡵ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡆࡸࡧࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡪࡲࡳࡰࡀࠠࡕࡪࡨࠤࡪࡼࡥ࡯ࡶࠣࡨ࡮ࡩࡴࡪࡱࡱࡥࡷࡿࠠࡤࡱࡱࡸࡦ࡯࡮ࡪࡰࡪࠤࡪࡾࡩࡴࡶ࡬ࡲ࡬ࠦ࡬ࡰࡩࡶࠤࡦࡴࡤࠡࡪࡲࡳࡰࠦࡩ࡯ࡨࡲࡶࡲࡧࡴࡪࡱࡱ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡬ࡴࡵ࡫ࡠ࡮ࡨࡺࡪࡲ࡟ࡧ࡫࡯ࡩࡸࡀࠠࡍ࡫ࡶࡸࠥࡵࡦࠡࡒࡤࡸ࡭ࠦ࡯ࡣ࡬ࡨࡧࡹࡹࠠࡧࡴࡲࡱࠥࡺࡨࡦࠢࡗࡩࡸࡺࡌࡦࡸࡨࡰࠥࡳ࡯࡯࡫ࡷࡳࡷ࡯࡮ࡨ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡤࡸ࡭ࡱࡪ࡟࡭ࡧࡹࡩࡱࡥࡦࡪ࡮ࡨࡷ࠿ࠦࡌࡪࡵࡷࠤࡴ࡬ࠠࡑࡣࡷ࡬ࠥࡵࡢ࡫ࡧࡦࡸࡸࠦࡦࡳࡱࡰࠤࡹ࡮ࡥࠡࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠥࡳ࡯࡯࡫ࡷࡳࡷ࡯࡮ࡨ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢᒑ")
        global _1l1ll1ll1l1_opy_
        platform_index = os.environ[bstack1ll1ll_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠩᒒ")]
        bstack1l1ll111l1l_opy_ = os.path.join(bstack1l1lll1ll1l_opy_, (bstack1l1ll11lll1_opy_ + str(platform_index)), bstack1l111ll11l1_opy_)
        if not os.path.exists(bstack1l1ll111l1l_opy_) or not os.path.isdir(bstack1l1ll111l1l_opy_):
            return
        logs = hook.get(bstack1ll1ll_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᒓ"), [])
        with os.scandir(bstack1l1ll111l1l_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1ll1ll1l1_opy_:
                    self.logger.info(bstack1ll1ll_opy_ (u"ࠦࡕࡧࡴࡩࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡻࡾࠤᒔ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack1ll1ll_opy_ (u"ࠧࠨᒕ")
                    log_entry = bstack1lll1ll1111_opy_(
                        kind=bstack1ll1ll_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᒖ"),
                        message=bstack1ll1ll_opy_ (u"ࠢࠣᒗ"),
                        level=bstack1ll1ll_opy_ (u"ࠣࠤᒘ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1ll11llll_opy_=entry.stat().st_size,
                        bstack1l1ll1l1ll1_opy_=bstack1ll1ll_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤᒙ"),
                        bstack11ll_opy_=os.path.abspath(entry.path),
                        bstack1l1111l1111_opy_=hook.get(TestFramework.bstack1l111l11lll_opy_)
                    )
                    logs.append(log_entry)
                    _1l1ll1ll1l1_opy_.add(abs_path)
        platform_index = os.environ[bstack1ll1ll_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪᒚ")]
        bstack1l1111ll1l1_opy_ = os.path.join(bstack1l1lll1ll1l_opy_, (bstack1l1ll11lll1_opy_ + str(platform_index)), bstack1l111ll11l1_opy_, bstack1l111ll111l_opy_)
        if not os.path.exists(bstack1l1111ll1l1_opy_) or not os.path.isdir(bstack1l1111ll1l1_opy_):
            self.logger.info(bstack1ll1ll_opy_ (u"ࠦࡓࡵࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࡌࡴࡵ࡫ࡆࡸࡨࡲࡹࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿࠠࡧࡱࡸࡲࡩࠦࡡࡵ࠼ࠣࡿࢂࠨᒛ").format(bstack1l1111ll1l1_opy_))
        else:
            self.logger.info(bstack1ll1ll_opy_ (u"ࠧࡖࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡦࡳࡱࡰࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠺ࠡࡽࢀࠦᒜ").format(bstack1l1111ll1l1_opy_))
            with os.scandir(bstack1l1111ll1l1_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1ll1ll1l1_opy_:
                        self.logger.info(bstack1ll1ll_opy_ (u"ࠨࡐࡢࡶ࡫ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡽࢀࠦᒝ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack1ll1ll_opy_ (u"ࠢࠣᒞ")
                        log_entry = bstack1lll1ll1111_opy_(
                            kind=bstack1ll1ll_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥᒟ"),
                            message=bstack1ll1ll_opy_ (u"ࠤࠥᒠ"),
                            level=bstack1ll1ll_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᒡ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1ll11llll_opy_=entry.stat().st_size,
                            bstack1l1ll1l1ll1_opy_=bstack1ll1ll_opy_ (u"ࠦࡒࡇࡎࡖࡃࡏࡣ࡚ࡖࡌࡐࡃࡇࠦᒢ"),
                            bstack11ll_opy_=os.path.abspath(entry.path),
                            bstack1l1ll1l1l11_opy_=hook.get(TestFramework.bstack1l111l11lll_opy_)
                        )
                        logs.append(log_entry)
                        _1l1ll1ll1l1_opy_.add(abs_path)
        hook[bstack1ll1ll_opy_ (u"ࠧࡲ࡯ࡨࡵࠥᒣ")] = logs
    def bstack1l1ll11l11l_opy_(
        self,
        bstack1l1ll11l1ll_opy_: bstack1ll1lll1l11_opy_,
        entries: List[bstack1lll1ll1111_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack1ll1ll_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡉࡌࡊࡡࡅࡍࡓࡥࡓࡆࡕࡖࡍࡔࡔ࡟ࡊࡆࠥᒤ"))
        req.platform_index = TestFramework.bstack1llllll1lll_opy_(bstack1l1ll11l1ll_opy_, TestFramework.bstack1ll11ll1l11_opy_)
        req.execution_context.hash = str(bstack1l1ll11l1ll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1ll11l1ll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1ll11l1ll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1llllll1lll_opy_(bstack1l1ll11l1ll_opy_, TestFramework.bstack1ll11lllll1_opy_)
            log_entry.test_framework_version = TestFramework.bstack1llllll1lll_opy_(bstack1l1ll11l1ll_opy_, TestFramework.bstack1l1ll11ll11_opy_)
            log_entry.uuid = entry.bstack1l1111l1111_opy_ if entry.bstack1l1111l1111_opy_ else TestFramework.bstack1llllll1lll_opy_(bstack1l1ll11l1ll_opy_, TestFramework.bstack1ll1l1111ll_opy_)
            log_entry.test_framework_state = bstack1l1ll11l1ll_opy_.state.name
            log_entry.message = entry.message.encode(bstack1ll1ll_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨᒥ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack1ll1ll_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥᒦ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1ll11llll_opy_
                log_entry.file_path = entry.bstack11ll_opy_
        def bstack1l1l1llllll_opy_():
            bstack111l1l111_opy_ = datetime.now()
            try:
                self.bstack1llll1ll111_opy_.LogCreatedEvent(req)
                bstack1l1ll11l1ll_opy_.bstack1lll1ll11_opy_(bstack1ll1ll_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨᒧ"), datetime.now() - bstack111l1l111_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1ll1ll_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡻࡾࠤᒨ").format(str(e)))
                traceback.print_exc()
        self.bstack111111ll11_opy_.enqueue(bstack1l1l1llllll_opy_)
    def __1l111l111l1_opy_(self, instance) -> None:
        bstack1ll1ll_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡎࡲࡥࡩࡹࠠࡤࡷࡶࡸࡴࡳࠠࡵࡣࡪࡷࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦࡧࡪࡸࡨࡲࠥࡺࡥࡴࡶࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡇࡷ࡫ࡡࡵࡧࡶࠤࡦࠦࡤࡪࡥࡷࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡶࡨࡷࡹࠦ࡬ࡦࡸࡨࡰࠥࡩࡵࡴࡶࡲࡱࠥࡳࡥࡵࡣࡧࡥࡹࡧࠠࡳࡧࡷࡶ࡮࡫ࡶࡦࡦࠣࡪࡷࡵ࡭ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆࡹࡸࡺ࡯࡮ࡖࡤ࡫ࡒࡧ࡮ࡢࡩࡨࡶࠥࡧ࡮ࡥࠢࡸࡴࡩࡧࡴࡦࡵࠣࡸ࡭࡫ࠠࡪࡰࡶࡸࡦࡴࡣࡦࠢࡶࡸࡦࡺࡥࠡࡷࡶ࡭ࡳ࡭ࠠࡴࡧࡷࡣࡸࡺࡡࡵࡧࡢࡩࡳࡺࡲࡪࡧࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᒩ")
        bstack1l11111llll_opy_ = {bstack1ll1ll_opy_ (u"ࠧࡩࡵࡴࡶࡲࡱࡤࡳࡥࡵࡣࡧࡥࡹࡧࠢᒪ"): bstack1llll1l1lll_opy_.bstack1l111l1ll11_opy_()}
        TestFramework.bstack1l111l1111l_opy_(instance, bstack1l11111llll_opy_)
    @staticmethod
    def __1l11l11l111_opy_(instance, args):
        request, bstack1l1111111l1_opy_ = args
        bstack1l11l111ll1_opy_ = id(bstack1l1111111l1_opy_)
        bstack1l11111ll1l_opy_ = instance.data[TestFramework.bstack1l11l111l11_opy_]
        step = next(filter(lambda st: st[bstack1ll1ll_opy_ (u"࠭ࡩࡥࠩᒫ")] == bstack1l11l111ll1_opy_, bstack1l11111ll1l_opy_[bstack1ll1ll_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᒬ")]), None)
        step.update({
            bstack1ll1ll_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬᒭ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack1l11111ll1l_opy_[bstack1ll1ll_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᒮ")]) if st[bstack1ll1ll_opy_ (u"ࠪ࡭ࡩ࠭ᒯ")] == step[bstack1ll1ll_opy_ (u"ࠫ࡮ࡪࠧᒰ")]), None)
        if index is not None:
            bstack1l11111ll1l_opy_[bstack1ll1ll_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫᒱ")][index] = step
        instance.data[TestFramework.bstack1l11l111l11_opy_] = bstack1l11111ll1l_opy_
    @staticmethod
    def __1l111l1l1ll_opy_(instance, args):
        bstack1ll1ll_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡻ࡭࡫࡮ࠡ࡮ࡨࡲࠥࡧࡲࡨࡵࠣ࡭ࡸࠦ࠲࠭ࠢ࡬ࡸࠥࡹࡩࡨࡰ࡬ࡪ࡮࡫ࡳࠡࡶ࡫ࡩࡷ࡫ࠠࡪࡵࠣࡲࡴࠦࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡢࡴࡪࡷࠥࡧࡲࡦࠢ࠰ࠤࡠࡸࡥࡲࡷࡨࡷࡹ࠲ࠠࡴࡶࡨࡴࡢࠐࠠࠡࠢࠣࠤࠥࠦࠠࡪࡨࠣࡥࡷ࡭ࡳࠡࡣࡵࡩࠥ࠹ࠠࡵࡪࡨࡲࠥࡺࡨࡦࠢ࡯ࡥࡸࡺࠠࡷࡣ࡯ࡹࡪࠦࡩࡴࠢࡨࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᒲ")
        bstack1l111llllll_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1l1111111l1_opy_ = args[1]
        bstack1l11l111ll1_opy_ = id(bstack1l1111111l1_opy_)
        bstack1l11111ll1l_opy_ = instance.data[TestFramework.bstack1l11l111l11_opy_]
        step = None
        if bstack1l11l111ll1_opy_ is not None and bstack1l11111ll1l_opy_.get(bstack1ll1ll_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᒳ")):
            step = next(filter(lambda st: st[bstack1ll1ll_opy_ (u"ࠨ࡫ࡧࠫᒴ")] == bstack1l11l111ll1_opy_, bstack1l11111ll1l_opy_[bstack1ll1ll_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᒵ")]), None)
            step.update({
                bstack1ll1ll_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨᒶ"): bstack1l111llllll_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack1ll1ll_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫᒷ"): bstack1ll1ll_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᒸ"),
                bstack1ll1ll_opy_ (u"࠭ࡦࡢ࡫࡯ࡹࡷ࡫ࠧᒹ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack1ll1ll_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧᒺ"): bstack1ll1ll_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨᒻ"),
                })
        index = next((i for i, st in enumerate(bstack1l11111ll1l_opy_[bstack1ll1ll_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᒼ")]) if st[bstack1ll1ll_opy_ (u"ࠪ࡭ࡩ࠭ᒽ")] == step[bstack1ll1ll_opy_ (u"ࠫ࡮ࡪࠧᒾ")]), None)
        if index is not None:
            bstack1l11111ll1l_opy_[bstack1ll1ll_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫᒿ")][index] = step
        instance.data[TestFramework.bstack1l11l111l11_opy_] = bstack1l11111ll1l_opy_
    @staticmethod
    def __1l1111lllll_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack1ll1ll_opy_ (u"࠭ࡣࡢ࡮࡯ࡷࡵ࡫ࡣࠨᓀ")):
                examples = list(node.callspec.params[bstack1ll1ll_opy_ (u"ࠧࡠࡲࡼࡸࡪࡹࡴࡠࡤࡧࡨࡤ࡫ࡸࡢ࡯ࡳࡰࡪ࠭ᓁ")].values())
            return examples
        except:
            return []
    def bstack1l1ll1ll1ll_opy_(self, instance: bstack1ll1lll1l11_opy_, bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_]):
        bstack1l11l1111l1_opy_ = (
            PytestBDDFramework.bstack1l111lll11l_opy_
            if bstack1llllll1111_opy_[1] == bstack1lll11ll111_opy_.PRE
            else PytestBDDFramework.bstack1l11l11l11l_opy_
        )
        hook = PytestBDDFramework.bstack1l111111lll_opy_(instance, bstack1l11l1111l1_opy_)
        entries = hook.get(TestFramework.bstack1l11111l1ll_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l11111l11l_opy_, []))
        return entries
    def bstack1l1llll1111_opy_(self, instance: bstack1ll1lll1l11_opy_, bstack1llllll1111_opy_: Tuple[bstack1llll1111ll_opy_, bstack1lll11ll111_opy_]):
        bstack1l11l1111l1_opy_ = (
            PytestBDDFramework.bstack1l111lll11l_opy_
            if bstack1llllll1111_opy_[1] == bstack1lll11ll111_opy_.PRE
            else PytestBDDFramework.bstack1l11l11l11l_opy_
        )
        PytestBDDFramework.bstack1l1111ll111_opy_(instance, bstack1l11l1111l1_opy_)
        TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l11111l11l_opy_, []).clear()
    @staticmethod
    def bstack1l111111lll_opy_(instance: bstack1ll1lll1l11_opy_, bstack1l11l1111l1_opy_: str):
        bstack1l1111l1l1l_opy_ = (
            PytestBDDFramework.bstack1l111ll1lll_opy_
            if bstack1l11l1111l1_opy_ == PytestBDDFramework.bstack1l11l11l11l_opy_
            else PytestBDDFramework.bstack1l1111l1lll_opy_
        )
        bstack1l111l11ll1_opy_ = TestFramework.bstack1llllll1lll_opy_(instance, bstack1l11l1111l1_opy_, None)
        bstack11lllllll1l_opy_ = TestFramework.bstack1llllll1lll_opy_(instance, bstack1l1111l1l1l_opy_, None) if bstack1l111l11ll1_opy_ else None
        return (
            bstack11lllllll1l_opy_[bstack1l111l11ll1_opy_][-1]
            if isinstance(bstack11lllllll1l_opy_, dict) and len(bstack11lllllll1l_opy_.get(bstack1l111l11ll1_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1l1111ll111_opy_(instance: bstack1ll1lll1l11_opy_, bstack1l11l1111l1_opy_: str):
        hook = PytestBDDFramework.bstack1l111111lll_opy_(instance, bstack1l11l1111l1_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1l11111l1ll_opy_, []).clear()
    @staticmethod
    def __1l111ll1111_opy_(instance: bstack1ll1lll1l11_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack1ll1ll_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡤࡱࡵࡨࡸࠨᓂ"), None)):
            return
        if os.getenv(bstack1ll1ll_opy_ (u"ࠤࡖࡈࡐࡥࡃࡍࡋࡢࡊࡑࡇࡇࡠࡎࡒࡋࡘࠨᓃ"), bstack1ll1ll_opy_ (u"ࠥ࠵ࠧᓄ")) != bstack1ll1ll_opy_ (u"ࠦ࠶ࠨᓅ"):
            PytestBDDFramework.logger.warning(bstack1ll1ll_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵ࡭ࡳ࡭ࠠࡤࡣࡳࡰࡴ࡭ࠢᓆ"))
            return
        bstack11llllll1ll_opy_ = {
            bstack1ll1ll_opy_ (u"ࠨࡳࡦࡶࡸࡴࠧᓇ"): (PytestBDDFramework.bstack1l111lll11l_opy_, PytestBDDFramework.bstack1l1111l1lll_opy_),
            bstack1ll1ll_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᓈ"): (PytestBDDFramework.bstack1l11l11l11l_opy_, PytestBDDFramework.bstack1l111ll1lll_opy_),
        }
        for when in (bstack1ll1ll_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢᓉ"), bstack1ll1ll_opy_ (u"ࠤࡦࡥࡱࡲࠢᓊ"), bstack1ll1ll_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧᓋ")):
            bstack1l111ll1l11_opy_ = args[1].get_records(when)
            if not bstack1l111ll1l11_opy_:
                continue
            records = [
                bstack1lll1ll1111_opy_(
                    kind=TestFramework.bstack1l1ll1lll1l_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack1ll1ll_opy_ (u"ࠦࡱ࡫ࡶࡦ࡮ࡱࡥࡲ࡫ࠢᓌ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack1ll1ll_opy_ (u"ࠧࡩࡲࡦࡣࡷࡩࡩࠨᓍ")) and r.created
                        else None
                    ),
                )
                for r in bstack1l111ll1l11_opy_
                if isinstance(getattr(r, bstack1ll1ll_opy_ (u"ࠨ࡭ࡦࡵࡶࡥ࡬࡫ࠢᓎ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack1l11111111l_opy_, bstack1l1111l1l1l_opy_ = bstack11llllll1ll_opy_.get(when, (None, None))
            bstack1l111l11111_opy_ = TestFramework.bstack1llllll1lll_opy_(instance, bstack1l11111111l_opy_, None) if bstack1l11111111l_opy_ else None
            bstack11lllllll1l_opy_ = TestFramework.bstack1llllll1lll_opy_(instance, bstack1l1111l1l1l_opy_, None) if bstack1l111l11111_opy_ else None
            if isinstance(bstack11lllllll1l_opy_, dict) and len(bstack11lllllll1l_opy_.get(bstack1l111l11111_opy_, [])) > 0:
                hook = bstack11lllllll1l_opy_[bstack1l111l11111_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack1l11111l1ll_opy_ in hook:
                    hook[TestFramework.bstack1l11111l1ll_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1llllll1lll_opy_(instance, TestFramework.bstack1l11111l11l_opy_, [])
            logs.extend(records)
    @staticmethod
    def __1l1111l1ll1_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1l11lll1_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__1l111l1lll1_opy_(request.node, scenario)
        bstack1l11111ll11_opy_ = feature.filename
        if not bstack1l11lll1_opy_ or not test_name or not bstack1l11111ll11_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1ll1l1111ll_opy_: uuid4().__str__(),
            TestFramework.bstack1l1111lll1l_opy_: bstack1l11lll1_opy_,
            TestFramework.bstack1ll1l111l11_opy_: test_name,
            TestFramework.bstack1l1l1l1l111_opy_: bstack1l11lll1_opy_,
            TestFramework.bstack1l111l1l1l1_opy_: bstack1l11111ll11_opy_,
            TestFramework.bstack11llllllll1_opy_: PytestBDDFramework.__1l111111l11_opy_(feature, scenario),
            TestFramework.bstack1l11l111l1l_opy_: code,
            TestFramework.bstack1l1l11111ll_opy_: TestFramework.bstack1l1111ll11l_opy_,
            TestFramework.bstack1l11l1ll111_opy_: test_name
        }
    @staticmethod
    def __1l111l1lll1_opy_(node, scenario):
        if hasattr(node, bstack1ll1ll_opy_ (u"ࠧࡤࡣ࡯ࡰࡸࡶࡥࡤࠩᓏ")):
            parts = node.nodeid.rsplit(bstack1ll1ll_opy_ (u"ࠣ࡝ࠥᓐ"))
            params = parts[-1]
            return bstack1ll1ll_opy_ (u"ࠤࡾࢁࠥࡡࡻࡾࠤᓑ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __1l111111l11_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack1ll1ll_opy_ (u"ࠪࡸࡦ࡭ࡳࠨᓒ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack1ll1ll_opy_ (u"ࠫࡹࡧࡧࡴࠩᓓ")) else [])
    @staticmethod
    def __1l111ll1ll1_opy_(location):
        return bstack1ll1ll_opy_ (u"ࠧࡀ࠺ࠣᓔ").join(filter(lambda x: isinstance(x, str), location))