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
import os
import grpc
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1llll1l1ll1_opy_ import bstack1llll1l1l1l_opy_
from browserstack_sdk.sdk_cli.bstack1lllll1l1l1_opy_ import (
    bstack1llllllll1l_opy_,
    bstack1lllll1l11l_opy_,
    bstack111111l111_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1lll111ll1l_opy_ import bstack1ll1ll1ll1l_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack1111lllll_opy_
from bstack_utils.helper import bstack1l1lll1111l_opy_
import threading
import os
import urllib.parse
class bstack1lll1l1ll11_opy_(bstack1llll1l1l1l_opy_):
    def __init__(self, bstack1ll1l1ll11l_opy_):
        super().__init__()
        bstack1ll1ll1ll1l_opy_.bstack1ll11l1l111_opy_((bstack1llllllll1l_opy_.bstack1lllll11l11_opy_, bstack1lllll1l11l_opy_.PRE), self.bstack1l1l11l1lll_opy_)
        bstack1ll1ll1ll1l_opy_.bstack1ll11l1l111_opy_((bstack1llllllll1l_opy_.bstack1lllll11l11_opy_, bstack1lllll1l11l_opy_.PRE), self.bstack1l1l11ll111_opy_)
        bstack1ll1ll1ll1l_opy_.bstack1ll11l1l111_opy_((bstack1llllllll1l_opy_.bstack1lllllll111_opy_, bstack1lllll1l11l_opy_.PRE), self.bstack1l1l11lll1l_opy_)
        bstack1ll1ll1ll1l_opy_.bstack1ll11l1l111_opy_((bstack1llllllll1l_opy_.bstack1lllll11l1l_opy_, bstack1lllll1l11l_opy_.PRE), self.bstack1l1l11ll11l_opy_)
        bstack1ll1ll1ll1l_opy_.bstack1ll11l1l111_opy_((bstack1llllllll1l_opy_.bstack1lllll11l11_opy_, bstack1lllll1l11l_opy_.PRE), self.bstack1l1l11llll1_opy_)
        bstack1ll1ll1ll1l_opy_.bstack1ll11l1l111_opy_((bstack1llllllll1l_opy_.QUIT, bstack1lllll1l11l_opy_.PRE), self.on_close)
        self.bstack1ll1l1ll11l_opy_ = bstack1ll1l1ll11l_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l11l1lll_opy_(
        self,
        f: bstack1ll1ll1ll1l_opy_,
        bstack1l1l11l111l_opy_: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll1ll_opy_ (u"ࠧࡲࡡࡶࡰࡦ࡬ࠧዪ"):
            return
        if not bstack1l1lll1111l_opy_():
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠨࡒࡦࡶࡸࡶࡳ࡯࡮ࡨࠢ࡬ࡲࠥࡲࡡࡶࡰࡦ࡬ࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥያ"))
            return
        def wrapped(bstack1l1l11l111l_opy_, launch, *args, **kwargs):
            response = self.bstack1l1l11l1111_opy_(f.platform_index, instance.ref(), json.dumps({bstack1ll1ll_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ዬ"): True}).encode(bstack1ll1ll_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢይ")))
            if response is not None and response.capabilities:
                if not bstack1l1lll1111l_opy_():
                    browser = launch(bstack1l1l11l111l_opy_)
                    return browser
                bstack1l1l11l1l11_opy_ = json.loads(response.capabilities.decode(bstack1ll1ll_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣዮ")))
                if not bstack1l1l11l1l11_opy_: # empty caps bstack1l1l11l1l1l_opy_ bstack1l1l1l1111l_opy_ bstack1l1l11l11ll_opy_ bstack1llll11lll1_opy_ or error in processing
                    return
                bstack1l1l11ll1l1_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l11l1l11_opy_))
                f.bstack1lllll1ll1l_opy_(instance, bstack1ll1ll1ll1l_opy_.bstack1l1l1l111l1_opy_, bstack1l1l11ll1l1_opy_)
                f.bstack1lllll1ll1l_opy_(instance, bstack1ll1ll1ll1l_opy_.bstack1l1l11lllll_opy_, bstack1l1l11l1l11_opy_)
                browser = bstack1l1l11l111l_opy_.connect(bstack1l1l11ll1l1_opy_)
                return browser
        return wrapped
    def bstack1l1l11lll1l_opy_(
        self,
        f: bstack1ll1ll1ll1l_opy_,
        Connection: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll1ll_opy_ (u"ࠥࡨ࡮ࡹࡰࡢࡶࡦ࡬ࠧዯ"):
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡨ࡮ࡹࡰࡢࡶࡦ࡬ࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥደ"))
            return
        if not bstack1l1lll1111l_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack1ll1ll_opy_ (u"ࠬࡶࡡࡳࡣࡰࡷࠬዱ"), {}).get(bstack1ll1ll_opy_ (u"࠭ࡢࡴࡒࡤࡶࡦࡳࡳࠨዲ")):
                    bstack1l1l1l11111_opy_ = args[0][bstack1ll1ll_opy_ (u"ࠢࡱࡣࡵࡥࡲࡹࠢዳ")][bstack1ll1ll_opy_ (u"ࠣࡤࡶࡔࡦࡸࡡ࡮ࡵࠥዴ")]
                    session_id = bstack1l1l1l11111_opy_.get(bstack1ll1ll_opy_ (u"ࠤࡶࡩࡸࡹࡩࡰࡰࡌࡨࠧድ"))
                    f.bstack1lllll1ll1l_opy_(instance, bstack1ll1ll1ll1l_opy_.bstack1l1l11ll1ll_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡧ࡭ࡸࡶࡡࡵࡥ࡫ࠤࡲ࡫ࡴࡩࡱࡧ࠾ࠥࠨዶ"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack1l1l11llll1_opy_(
        self,
        f: bstack1ll1ll1ll1l_opy_,
        bstack1l1l11l111l_opy_: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll1ll_opy_ (u"ࠦࡨࡵ࡮࡯ࡧࡦࡸࠧዷ"):
            return
        if not bstack1l1lll1111l_opy_():
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠧࡘࡥࡵࡷࡵࡲ࡮ࡴࡧࠡ࡫ࡱࠤࡨࡵ࡮࡯ࡧࡦࡸࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥዸ"))
            return
        def wrapped(bstack1l1l11l111l_opy_, connect, *args, **kwargs):
            response = self.bstack1l1l11l1111_opy_(f.platform_index, instance.ref(), json.dumps({bstack1ll1ll_opy_ (u"࠭ࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠬዹ"): True}).encode(bstack1ll1ll_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨዺ")))
            if response is not None and response.capabilities:
                bstack1l1l11l1l11_opy_ = json.loads(response.capabilities.decode(bstack1ll1ll_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢዻ")))
                if not bstack1l1l11l1l11_opy_:
                    return
                bstack1l1l11ll1l1_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l11l1l11_opy_))
                if bstack1l1l11l1l11_opy_.get(bstack1ll1ll_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨዼ")):
                    browser = bstack1l1l11l111l_opy_.bstack1l1l11l1ll1_opy_(bstack1l1l11ll1l1_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack1l1l11ll1l1_opy_
                    return connect(bstack1l1l11l111l_opy_, *args, **kwargs)
        return wrapped
    def bstack1l1l11ll111_opy_(
        self,
        f: bstack1ll1ll1ll1l_opy_,
        bstack1l1lllll11l_opy_: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll1ll_opy_ (u"ࠥࡲࡪࡽ࡟ࡱࡣࡪࡩࠧዽ"):
            return
        if not bstack1l1lll1111l_opy_():
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡲࡪࡽ࡟ࡱࡣࡪࡩࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥዾ"))
            return
        def wrapped(bstack1l1lllll11l_opy_, bstack1l1l11lll11_opy_, *args, **kwargs):
            contexts = bstack1l1lllll11l_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                                if bstack1ll1ll_opy_ (u"ࠧࡧࡢࡰࡷࡷ࠾ࡧࡲࡡ࡯࡭ࠥዿ") in page.url:
                                    return page
                    else:
                        return bstack1l1l11lll11_opy_(bstack1l1lllll11l_opy_)
        return wrapped
    def bstack1l1l11l1111_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack1ll1ll_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡹࡨࡦࡩࡸࡩࡷࡧࡵࡣ࡮ࡴࡩࡵ࠼ࠣࠦጀ") + str(req) + bstack1ll1ll_opy_ (u"ࠢࠣጁ"))
        try:
            r = self.bstack1llll1ll111_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1ll1ll_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࡶࡹࡨࡩࡥࡴࡵࡀࠦጂ") + str(r.success) + bstack1ll1ll_opy_ (u"ࠤࠥጃ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1ll1ll_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣጄ") + str(e) + bstack1ll1ll_opy_ (u"ࠦࠧጅ"))
            traceback.print_exc()
            raise e
    def bstack1l1l11ll11l_opy_(
        self,
        f: bstack1ll1ll1ll1l_opy_,
        Connection: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll1ll_opy_ (u"ࠧࡥࡳࡦࡰࡧࡣࡲ࡫ࡳࡴࡣࡪࡩࡤࡺ࡯ࡠࡵࡨࡶࡻ࡫ࡲࠣጆ"):
            return
        if not bstack1l1lll1111l_opy_():
            return
        def wrapped(Connection, bstack1l1l11l11l1_opy_, *args, **kwargs):
            return bstack1l1l11l11l1_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll1ll1ll1l_opy_,
        bstack1l1l11l111l_opy_: object,
        exec: Tuple[bstack111111l111_opy_, str],
        bstack1llllll1111_opy_: Tuple[bstack1llllllll1l_opy_, bstack1lllll1l11l_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1ll1ll_opy_ (u"ࠨࡣ࡭ࡱࡶࡩࠧጇ"):
            return
        if not bstack1l1lll1111l_opy_():
            self.logger.debug(bstack1ll1ll_opy_ (u"ࠢࡓࡧࡷࡹࡷࡴࡩ࡯ࡩࠣ࡭ࡳࠦࡣ࡭ࡱࡶࡩࠥࡳࡥࡵࡪࡲࡨ࠱ࠦ࡮ࡰࡶࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠥገ"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped