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
import json
import shutil
import tempfile
import threading
import urllib.request
import uuid
from pathlib import Path
import logging
import re
from bstack_utils.helper import bstack1l1l1ll11ll_opy_
bstack11lll11l1ll_opy_ = 100 * 1024 * 1024 # 100 bstack11lll1l1lll_opy_
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
bstack1l1lll1ll1l_opy_ = bstack1l1l1ll11ll_opy_()
bstack1l1ll11lll1_opy_ = bstack1ll1ll_opy_ (u"ࠨࡕࡱ࡮ࡲࡥࡩ࡫ࡤࡂࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࡷ࠲ࠨᗦ")
bstack11lllll1lll_opy_ = bstack1ll1ll_opy_ (u"ࠢࡕࡧࡶࡸࡑ࡫ࡶࡦ࡮ࠥᗧ")
bstack11lllll1l11_opy_ = bstack1ll1ll_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧᗨ")
bstack11lllll1ll1_opy_ = bstack1ll1ll_opy_ (u"ࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰࠧᗩ")
bstack11lll1l1ll1_opy_ = bstack1ll1ll_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࡈࡰࡱ࡮ࡉࡻ࡫࡮ࡵࠤᗪ")
_11lll11ll11_opy_ = threading.local()
def bstack1l111111111_opy_(test_framework_state, test_hook_state):
    bstack1ll1ll_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡘ࡫ࡴࠡࡶ࡫ࡩࠥࡩࡵࡳࡴࡨࡲࡹࠦࡴࡦࡵࡷࠤࡪࡼࡥ࡯ࡶࠣࡷࡹࡧࡴࡦࠢ࡬ࡲࠥࡺࡨࡳࡧࡤࡨ࠲ࡲ࡯ࡤࡣ࡯ࠤࡸࡺ࡯ࡳࡣࡪࡩ࠳ࠐࠠࠡࠢࠣࡘ࡭࡯ࡳࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡷ࡭ࡵࡵ࡭ࡦࠣࡦࡪࠦࡣࡢ࡮࡯ࡩࡩࠦࡢࡺࠢࡷ࡬ࡪࠦࡥࡷࡧࡱࡸࠥ࡮ࡡ࡯ࡦ࡯ࡩࡷࠦࠨࡴࡷࡦ࡬ࠥࡧࡳࠡࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹ࠯ࠊࠡࠢࠣࠤࡧ࡫ࡦࡰࡴࡨࠤࡦࡴࡹࠡࡨ࡬ࡰࡪࠦࡵࡱ࡮ࡲࡥࡩࡹࠠࡰࡥࡦࡹࡷ࠴ࠊࠡࠢࠣࠤࠧࠨࠢᗫ")
    _11lll11ll11_opy_.test_framework_state = test_framework_state
    _11lll11ll11_opy_.test_hook_state = test_hook_state
def bstack11lll1lll11_opy_():
    bstack1ll1ll_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡘࡥࡵࡴ࡬ࡩࡻ࡫ࠠࡵࡪࡨࠤࡨࡻࡲࡳࡧࡱࡸࠥࡺࡥࡴࡶࠣࡩࡻ࡫࡮ࡵࠢࡶࡸࡦࡺࡥࠡࡨࡵࡳࡲࠦࡴࡩࡴࡨࡥࡩ࠳࡬ࡰࡥࡤࡰࠥࡹࡴࡰࡴࡤ࡫ࡪ࠴ࠊࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷࠥࡧࠠࡵࡷࡳࡰࡪࠦࠨࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࠬࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࠬࠤࡴࡸࠠࠩࡐࡲࡲࡪ࠲ࠠࡏࡱࡱࡩ࠮ࠦࡩࡧࠢࡱࡳࡹࠦࡳࡦࡶ࠱ࠎࠥࠦࠠࠡࠤࠥࠦᗬ")
    return (
        getattr(_11lll11ll11_opy_, bstack1ll1ll_opy_ (u"࠭ࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪ࠭ᗭ"), None),
        getattr(_11lll11ll11_opy_, bstack1ll1ll_opy_ (u"ࠧࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࠩᗮ"), None)
    )
class bstack1l111llll1_opy_:
    bstack1ll1ll_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡈ࡬ࡰࡪ࡛ࡰ࡭ࡱࡤࡨࡪࡸࠠࡱࡴࡲࡺ࡮ࡪࡥࡴࠢࡩࡹࡳࡩࡴࡪࡱࡱࡥࡱ࡯ࡴࡺࠢࡷࡳࠥࡻࡰ࡭ࡱࡤࡨࠥࡧ࡮ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥࡨࡡࡴࡧࡧࠤࡴࡴࠠࡵࡪࡨࠤ࡬࡯ࡶࡦࡰࠣࡪ࡮ࡲࡥࠡࡲࡤࡸ࡭࠴ࠊࠡࠢࠣࠤࡎࡺࠠࡴࡷࡳࡴࡴࡸࡴࡴࠢࡥࡳࡹ࡮ࠠ࡭ࡱࡦࡥࡱࠦࡦࡪ࡮ࡨࠤࡵࡧࡴࡩࡵࠣࡥࡳࡪࠠࡉࡖࡗࡔ࠴ࡎࡔࡕࡒࡖࠤ࡚ࡘࡌࡴ࠮ࠣࡥࡳࡪࠠࡤࡱࡳ࡭ࡪࡹࠠࡵࡪࡨࠤ࡫࡯࡬ࡦࠢ࡬ࡲࡹࡵࠠࡢࠢࡧࡩࡸ࡯ࡧ࡯ࡣࡷࡩࡩࠐࠠࠡࠢࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾࠦࡷࡪࡶ࡫࡭ࡳࠦࡴࡩࡧࠣࡹࡸ࡫ࡲࠨࡵࠣ࡬ࡴࡳࡥࠡࡨࡲࡰࡩ࡫ࡲࠡࡷࡱࡨࡪࡸࠠࡿ࠱࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠱ࡘࡴࡱࡵࡡࡥࡧࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳ࠯ࠌࠣࠤࠥࠦࡉࡧࠢࡤࡲࠥࡵࡰࡵ࡫ࡲࡲࡦࡲࠠࡢࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠤࡵࡧࡲࡢ࡯ࡨࡸࡪࡸࠠࠩ࡫ࡱࠤࡏ࡙ࡏࡏࠢࡩࡳࡷࡳࡡࡵࠫࠣ࡭ࡸࠦࡰࡳࡱࡹ࡭ࡩ࡫ࡤࠡࡣࡱࡨࠥࡩ࡯࡯ࡶࡤ࡭ࡳࡹࠠࡢࠢࡷࡶࡺࡺࡨࡺࠢࡹࡥࡱࡻࡥࠋࠢࠣࠤࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦ࡫ࡦࡻࠣࠦࡧࡻࡩ࡭ࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨࠬࠡࡶ࡫ࡩࠥ࡬ࡩ࡭ࡧࠣࡻ࡮ࡲ࡬ࠡࡤࡨࠤࡵࡲࡡࡤࡧࡧࠤ࡮ࡴࠠࡵࡪࡨࠤࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤࠣࡪࡴࡲࡤࡦࡴ࠾ࠤࡴࡺࡨࡦࡴࡺ࡭ࡸ࡫ࠬࠋࠢࠣࠤࠥ࡯ࡴࠡࡦࡨࡪࡦࡻ࡬ࡵࡵࠣࡸࡴࠦࠢࡕࡧࡶࡸࡑ࡫ࡶࡦ࡮ࠥ࠲ࠏࠦࠠࠡࠢࡗ࡬࡮ࡹࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡱࡩࠤࡦࡪࡤࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥ࡯ࡳࠡࡣࠣࡺࡴ࡯ࡤࠡ࡯ࡨࡸ࡭ࡵࡤ⠕࡫ࡷࠤ࡭ࡧ࡮ࡥ࡮ࡨࡷࠥࡧ࡬࡭ࠢࡨࡶࡷࡵࡲࡴࠢࡪࡶࡦࡩࡥࡧࡷ࡯ࡰࡾࠦࡢࡺࠢ࡯ࡳ࡬࡭ࡩ࡯ࡩࠍࠤࠥࠦࠠࡵࡪࡨࡱࠥࡧ࡮ࡥࠢࡶ࡭ࡲࡶ࡬ࡺࠢࡵࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥࡽࡩࡵࡪࡲࡹࡹࠦࡴࡩࡴࡲࡻ࡮ࡴࡧࠡࡧࡻࡧࡪࡶࡴࡪࡱࡱࡷ࠳ࠐࠠࠡࠢࠣࠦࠧࠨᗯ")
    @staticmethod
    def upload_attachment(bstack11lll1l11ll_opy_: str, *bstack11lll1l1l1l_opy_) -> None:
        if not bstack11lll1l11ll_opy_ or not bstack11lll1l11ll_opy_.strip():
            logger.error(bstack1ll1ll_opy_ (u"ࠤࡤࡨࡩࡥࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࡕࡸ࡯ࡷ࡫ࡧࡩࡩࠦࡦࡪ࡮ࡨࠤࡵࡧࡴࡩࠢ࡬ࡷࠥ࡫࡭ࡱࡶࡼࠤࡴࡸࠠࡏࡱࡱࡩ࠳ࠨᗰ"))
            return
        bstack11lll11lll1_opy_ = bstack11lll1l1l1l_opy_[0] if bstack11lll1l1l1l_opy_ and len(bstack11lll1l1l1l_opy_) > 0 else None
        bstack11lll1l11l1_opy_ = None
        test_framework_state, test_hook_state = bstack11lll1lll11_opy_()
        try:
            if bstack11lll1l11ll_opy_.startswith(bstack1ll1ll_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲ࠦᗱ")) or bstack11lll1l11ll_opy_.startswith(bstack1ll1ll_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨᗲ")):
                logger.debug(bstack1ll1ll_opy_ (u"ࠧࡖࡡࡵࡪࠣ࡭ࡸࠦࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡦࠣࡥࡸࠦࡕࡓࡎ࠾ࠤࡩࡵࡷ࡯࡮ࡲࡥࡩ࡯࡮ࡨࠢࡷ࡬ࡪࠦࡦࡪ࡮ࡨ࠲ࠧᗳ"))
                url = bstack11lll1l11ll_opy_
                bstack11lll11ll1l_opy_ = str(uuid.uuid4())
                bstack11lll1l111l_opy_ = os.path.basename(urllib.request.urlparse(url).path)
                if not bstack11lll1l111l_opy_ or not bstack11lll1l111l_opy_.strip():
                    bstack11lll1l111l_opy_ = bstack11lll11ll1l_opy_
                temp_file = tempfile.NamedTemporaryFile(delete=False,
                                                        prefix=bstack1ll1ll_opy_ (u"ࠨࡵࡱ࡮ࡲࡥࡩࡥࠢᗴ") + bstack11lll11ll1l_opy_ + bstack1ll1ll_opy_ (u"ࠢࡠࠤᗵ"),
                                                        suffix=bstack1ll1ll_opy_ (u"ࠣࡡࠥᗶ") + bstack11lll1l111l_opy_)
                with urllib.request.urlopen(url) as response, open(temp_file.name, bstack1ll1ll_opy_ (u"ࠩࡺࡦࠬᗷ")) as out_file:
                    shutil.copyfileobj(response, out_file)
                bstack11lll1l11l1_opy_ = Path(temp_file.name)
                logger.debug(bstack1ll1ll_opy_ (u"ࠥࡈࡴࡽ࡮࡭ࡱࡤࡨࡪࡪࠠࡧ࡫࡯ࡩࠥࡺ࡯ࠡࡶࡨࡱࡵࡵࡲࡢࡴࡼࠤࡱࡵࡣࡢࡶ࡬ࡳࡳࡀࠠࡼࡿࠥᗸ").format(bstack11lll1l11l1_opy_))
            else:
                bstack11lll1l11l1_opy_ = Path(bstack11lll1l11ll_opy_)
                logger.debug(bstack1ll1ll_opy_ (u"ࠦࡕࡧࡴࡩࠢ࡬ࡷࠥ࡯ࡤࡦࡰࡷ࡭࡫࡯ࡥࡥࠢࡤࡷࠥࡲ࡯ࡤࡣ࡯ࠤ࡫࡯࡬ࡦ࠼ࠣࡿࢂࠨᗹ").format(bstack11lll1l11l1_opy_))
        except Exception as e:
            logger.error(bstack1ll1ll_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡱࡥࡸࡦ࡯࡮ࠡࡨ࡬ࡰࡪࠦࡦࡳࡱࡰࠤࡵࡧࡴࡩ࠱ࡘࡖࡑࡀࠠࡼࡿࠥᗺ").format(e))
            return
        if bstack11lll1l11l1_opy_ is None or not bstack11lll1l11l1_opy_.exists():
            logger.error(bstack1ll1ll_opy_ (u"ࠨࡓࡰࡷࡵࡧࡪࠦࡦࡪ࡮ࡨࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠤᗻ").format(bstack11lll1l11l1_opy_))
            return
        if bstack11lll1l11l1_opy_.stat().st_size > bstack11lll11l1ll_opy_:
            logger.error(bstack1ll1ll_opy_ (u"ࠢࡇ࡫࡯ࡩࠥࡹࡩࡻࡧࠣࡩࡽࡩࡥࡦࡦࡶࠤࡲࡧࡸࡪ࡯ࡸࡱࠥࡧ࡬࡭ࡱࡺࡩࡩࠦࡳࡪࡼࡨࠤࡴ࡬ࠠࡼࡿࠥᗼ").format(bstack11lll11l1ll_opy_))
            return
        bstack11lll1ll1ll_opy_ = bstack1ll1ll_opy_ (u"ࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦᗽ")
        if bstack11lll11lll1_opy_:
            try:
                params = json.loads(bstack11lll11lll1_opy_)
                if bstack1ll1ll_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡂࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࠦᗾ") in params and params.get(bstack1ll1ll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠧᗿ")) is True:
                    bstack11lll1ll1ll_opy_ = bstack1ll1ll_opy_ (u"ࠦࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠣᘀ")
            except Exception as bstack11lll11llll_opy_:
                logger.error(bstack1ll1ll_opy_ (u"ࠧࡐࡓࡐࡐࠣࡴࡦࡸࡳࡪࡰࡪࠤࡪࡸࡲࡰࡴࠣ࡭ࡳࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡓࡥࡷࡧ࡭ࡴ࠼ࠣࡿࢂࠨᘁ").format(bstack11lll11llll_opy_))
        bstack11lll1ll1l1_opy_ = False
        from browserstack_sdk.sdk_cli.bstack1ll1ll1lll1_opy_ import bstack1lll1l111l1_opy_
        if test_framework_state in bstack1lll1l111l1_opy_.bstack1l111lllll1_opy_:
            if bstack11lll1ll1ll_opy_ == bstack11lllll1l11_opy_:
                bstack11lll1ll1l1_opy_ = True
            bstack11lll1ll1ll_opy_ = bstack11lllll1ll1_opy_
        try:
            platform_index = os.environ[bstack1ll1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ᘂ")]
            target_dir = os.path.join(bstack1l1lll1ll1l_opy_, bstack1l1ll11lll1_opy_ + str(platform_index),
                                      bstack11lll1ll1ll_opy_)
            if bstack11lll1ll1l1_opy_:
                target_dir = os.path.join(target_dir, bstack11lll1l1ll1_opy_)
            os.makedirs(target_dir, exist_ok=True)
            logger.debug(bstack1ll1ll_opy_ (u"ࠢࡄࡴࡨࡥࡹ࡫ࡤ࠰ࡸࡨࡶ࡮࡬ࡩࡦࡦࠣࡸࡦࡸࡧࡦࡶࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾࡀࠠࡼࡿࠥᘃ").format(target_dir))
            file_name = os.path.basename(bstack11lll1l11l1_opy_)
            bstack11lll1l1111_opy_ = os.path.join(target_dir, file_name)
            if os.path.exists(bstack11lll1l1111_opy_):
                base_name, extension = os.path.splitext(file_name)
                bstack11lll1ll11l_opy_ = 1
                while os.path.exists(os.path.join(target_dir, base_name + str(bstack11lll1ll11l_opy_) + extension)):
                    bstack11lll1ll11l_opy_ += 1
                bstack11lll1l1111_opy_ = os.path.join(target_dir, base_name + str(bstack11lll1ll11l_opy_) + extension)
            shutil.copy(bstack11lll1l11l1_opy_, bstack11lll1l1111_opy_)
            logger.info(bstack1ll1ll_opy_ (u"ࠣࡈ࡬ࡰࡪࠦࡳࡶࡥࡦࡩࡸࡹࡦࡶ࡮࡯ࡽࠥࡩ࡯ࡱ࡫ࡨࡨࠥࡺ࡯࠻ࠢࡾࢁࠧᘄ").format(bstack11lll1l1111_opy_))
        except Exception as e:
            logger.error(bstack1ll1ll_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡯ࡲࡺ࡮ࡴࡧࠡࡨ࡬ࡰࡪࠦࡴࡰࠢࡷࡥࡷ࡭ࡥࡵࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠿ࠦࡻࡾࠤᘅ").format(e))
            return
        finally:
            if bstack11lll1l11ll_opy_.startswith(bstack1ll1ll_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲ࠦᘆ")) or bstack11lll1l11ll_opy_.startswith(bstack1ll1ll_opy_ (u"ࠦ࡭ࡺࡴࡱࡵ࠽࠳࠴ࠨᘇ")):
                try:
                    if bstack11lll1l11l1_opy_ is not None and bstack11lll1l11l1_opy_.exists():
                        bstack11lll1l11l1_opy_.unlink()
                        logger.debug(bstack1ll1ll_opy_ (u"࡚ࠧࡥ࡮ࡲࡲࡶࡦࡸࡹࠡࡨ࡬ࡰࡪࠦࡤࡦ࡮ࡨࡸࡪࡪ࠺ࠡࡽࢀࠦᘈ").format(bstack11lll1l11l1_opy_))
                except Exception as ex:
                    logger.error(bstack1ll1ll_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡪࡥ࡭ࡧࡷ࡭ࡳ࡭ࠠࡵࡧࡰࡴࡴࡸࡡࡳࡻࠣࡪ࡮ࡲࡥ࠻ࠢࡾࢁࠧᘉ").format(ex))
    @staticmethod
    def bstack11l11l1l1l_opy_() -> None:
        bstack1ll1ll_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡉ࡫࡬ࡦࡶࡨࡷࠥࡧ࡬࡭ࠢࡩࡳࡱࡪࡥࡳࡵࠣࡻ࡭ࡵࡳࡦࠢࡱࡥࡲ࡫ࡳࠡࡵࡷࡥࡷࡺࠠࡸ࡫ࡷ࡬ࠥࠨࡕࡱ࡮ࡲࡥࡩ࡫ࡤࡂࡶࡷࡥࡨ࡮࡭ࡦࡰࡷࡷ࠲ࠨࠠࡧࡱ࡯ࡰࡴࡽࡥࡥࠢࡥࡽࠥࡧࠠ࡯ࡷࡰࡦࡪࡸࠠࡪࡰࠍࠤࠥࠦࠠࠡࠢࠣࠤࡹ࡮ࡥࠡࡷࡶࡩࡷ࠭ࡳࠡࢀ࠲࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᘊ")
        bstack11lll1l1l11_opy_ = bstack1l1l1ll11ll_opy_()
        pattern = re.compile(bstack1ll1ll_opy_ (u"ࡳࠤࡘࡴࡱࡵࡡࡥࡧࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳ࠮࡞ࡧ࠯ࠧᘋ"))
        if os.path.exists(bstack11lll1l1l11_opy_):
            for item in os.listdir(bstack11lll1l1l11_opy_):
                bstack11lll1ll111_opy_ = os.path.join(bstack11lll1l1l11_opy_, item)
                if os.path.isdir(bstack11lll1ll111_opy_) and pattern.fullmatch(item):
                    try:
                        shutil.rmtree(bstack11lll1ll111_opy_)
                    except Exception as e:
                        logger.error(bstack1ll1ll_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡦࡨࡰࡪࡺࡩ࡯ࡩࠣࡨ࡮ࡸࡥࡤࡶࡲࡶࡾࡀࠠࡼࡿࠥᘌ").format(e))
        else:
            logger.info(bstack1ll1ll_opy_ (u"ࠥࡘ࡭࡫ࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠾ࠥࢁࡽࠣᘍ").format(bstack11lll1l1l11_opy_))