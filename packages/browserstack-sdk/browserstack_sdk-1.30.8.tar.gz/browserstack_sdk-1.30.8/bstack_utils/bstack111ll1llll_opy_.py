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
from uuid import uuid4
from bstack_utils.helper import bstack1l111ll1_opy_, bstack11l1111llll_opy_
from bstack_utils.bstack1l1lll1l1l_opy_ import bstack1111111l111_opy_
class bstack1111llllll_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1llllll11lll_opy_=None, bstack1lllll1llll1_opy_=True, bstack1l111llllll_opy_=None, bstack1l1ll1llll_opy_=None, result=None, duration=None, bstack111l1111l1_opy_=None, meta={}):
        self.bstack111l1111l1_opy_ = bstack111l1111l1_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1lllll1llll1_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1llllll11lll_opy_ = bstack1llllll11lll_opy_
        self.bstack1l111llllll_opy_ = bstack1l111llllll_opy_
        self.bstack1l1ll1llll_opy_ = bstack1l1ll1llll_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack111l111111_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111ll11l11_opy_(self, meta):
        self.meta = meta
    def bstack111ll1ll11_opy_(self, hooks):
        self.hooks = hooks
    def bstack1lllll1l1lll_opy_(self):
        bstack1llllll1111l_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack1ll1ll_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ‛"): bstack1llllll1111l_opy_,
            bstack1ll1ll_opy_ (u"ࠩ࡯ࡳࡨࡧࡴࡪࡱࡱࠫ“"): bstack1llllll1111l_opy_,
            bstack1ll1ll_opy_ (u"ࠪࡺࡨࡥࡦࡪ࡮ࡨࡴࡦࡺࡨࠨ”"): bstack1llllll1111l_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack1ll1ll_opy_ (u"࡚ࠦࡴࡥࡹࡲࡨࡧࡹ࡫ࡤࠡࡣࡵ࡫ࡺࡳࡥ࡯ࡶ࠽ࠤࠧ„") + key)
            setattr(self, key, val)
    def bstack1lllll1lllll_opy_(self):
        return {
            bstack1ll1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ‟"): self.name,
            bstack1ll1ll_opy_ (u"࠭ࡢࡰࡦࡼࠫ†"): {
                bstack1ll1ll_opy_ (u"ࠧ࡭ࡣࡱ࡫ࠬ‡"): bstack1ll1ll_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ•"),
                bstack1ll1ll_opy_ (u"ࠩࡦࡳࡩ࡫ࠧ‣"): self.code
            },
            bstack1ll1ll_opy_ (u"ࠪࡷࡨࡵࡰࡦࡵࠪ․"): self.scope,
            bstack1ll1ll_opy_ (u"ࠫࡹࡧࡧࡴࠩ‥"): self.tags,
            bstack1ll1ll_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ…"): self.framework,
            bstack1ll1ll_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ‧"): self.started_at
        }
    def bstack1lllll1ll1ll_opy_(self):
        return {
         bstack1ll1ll_opy_ (u"ࠧ࡮ࡧࡷࡥࠬ "): self.meta
        }
    def bstack1lllll1ll111_opy_(self):
        return {
            bstack1ll1ll_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡓࡧࡵࡹࡳࡖࡡࡳࡣࡰࠫ "): {
                bstack1ll1ll_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡠࡰࡤࡱࡪ࠭‪"): self.bstack1llllll11lll_opy_
            }
        }
    def bstack1lllll1ll1l1_opy_(self, bstack1llllll11111_opy_, details):
        step = next(filter(lambda st: st[bstack1ll1ll_opy_ (u"ࠪ࡭ࡩ࠭‫")] == bstack1llllll11111_opy_, self.meta[bstack1ll1ll_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ‬")]), None)
        step.update(details)
    def bstack1ll111l11l_opy_(self, bstack1llllll11111_opy_):
        step = next(filter(lambda st: st[bstack1ll1ll_opy_ (u"ࠬ࡯ࡤࠨ‭")] == bstack1llllll11111_opy_, self.meta[bstack1ll1ll_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ‮")]), None)
        step.update({
            bstack1ll1ll_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫ "): bstack1l111ll1_opy_()
        })
    def bstack111ll1l1ll_opy_(self, bstack1llllll11111_opy_, result, duration=None):
        bstack1l111llllll_opy_ = bstack1l111ll1_opy_()
        if bstack1llllll11111_opy_ is not None and self.meta.get(bstack1ll1ll_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ‰")):
            step = next(filter(lambda st: st[bstack1ll1ll_opy_ (u"ࠩ࡬ࡨࠬ‱")] == bstack1llllll11111_opy_, self.meta[bstack1ll1ll_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ′")]), None)
            step.update({
                bstack1ll1ll_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩ″"): bstack1l111llllll_opy_,
                bstack1ll1ll_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴࠧ‴"): duration if duration else bstack11l1111llll_opy_(step[bstack1ll1ll_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪ‵")], bstack1l111llllll_opy_),
                bstack1ll1ll_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧ‶"): result.result,
                bstack1ll1ll_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩ‷"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1lllll1lll11_opy_):
        if self.meta.get(bstack1ll1ll_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨ‸")):
            self.meta[bstack1ll1ll_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ‹")].append(bstack1lllll1lll11_opy_)
        else:
            self.meta[bstack1ll1ll_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪ›")] = [ bstack1lllll1lll11_opy_ ]
    def bstack1llllll111ll_opy_(self):
        return {
            bstack1ll1ll_opy_ (u"ࠬࡻࡵࡪࡦࠪ※"): self.bstack111l111111_opy_(),
            **self.bstack1lllll1lllll_opy_(),
            **self.bstack1lllll1l1lll_opy_(),
            **self.bstack1lllll1ll1ll_opy_()
        }
    def bstack1llllll111l1_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack1ll1ll_opy_ (u"࠭ࡦࡪࡰ࡬ࡷ࡭࡫ࡤࡠࡣࡷࠫ‼"): self.bstack1l111llllll_opy_,
            bstack1ll1ll_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࡡ࡬ࡲࡤࡳࡳࠨ‽"): self.duration,
            bstack1ll1ll_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨ‾"): self.result.result
        }
        if data[bstack1ll1ll_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩ‿")] == bstack1ll1ll_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ⁀"):
            data[bstack1ll1ll_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡷࡵࡩࡤࡺࡹࡱࡧࠪ⁁")] = self.result.bstack11111l111l_opy_()
            data[bstack1ll1ll_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭⁂")] = [{bstack1ll1ll_opy_ (u"࠭ࡢࡢࡥ࡮ࡸࡷࡧࡣࡦࠩ⁃"): self.result.bstack111llll111l_opy_()}]
        return data
    def bstack1llllll11ll1_opy_(self):
        return {
            bstack1ll1ll_opy_ (u"ࠧࡶࡷ࡬ࡨࠬ⁄"): self.bstack111l111111_opy_(),
            **self.bstack1lllll1lllll_opy_(),
            **self.bstack1lllll1l1lll_opy_(),
            **self.bstack1llllll111l1_opy_(),
            **self.bstack1lllll1ll1ll_opy_()
        }
    def bstack1111ll1lll_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack1ll1ll_opy_ (u"ࠨࡕࡷࡥࡷࡺࡥࡥࠩ⁅") in event:
            return self.bstack1llllll111ll_opy_()
        elif bstack1ll1ll_opy_ (u"ࠩࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⁆") in event:
            return self.bstack1llllll11ll1_opy_()
    def bstack111l11llll_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1l111llllll_opy_ = time if time else bstack1l111ll1_opy_()
        self.duration = duration if duration else bstack11l1111llll_opy_(self.started_at, self.bstack1l111llllll_opy_)
        if result:
            self.result = result
class bstack111ll1ll1l_opy_(bstack1111llllll_opy_):
    def __init__(self, hooks=[], bstack111ll111ll_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111ll111ll_opy_ = bstack111ll111ll_opy_
        super().__init__(*args, **kwargs, bstack1l1ll1llll_opy_=bstack1ll1ll_opy_ (u"ࠪࡸࡪࡹࡴࠨ⁇"))
    @classmethod
    def bstack1llllll11l1l_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1ll1ll_opy_ (u"ࠫ࡮ࡪࠧ⁈"): id(step),
                bstack1ll1ll_opy_ (u"ࠬࡺࡥࡹࡶࠪ⁉"): step.name,
                bstack1ll1ll_opy_ (u"࠭࡫ࡦࡻࡺࡳࡷࡪࠧ⁊"): step.keyword,
            })
        return bstack111ll1ll1l_opy_(
            **kwargs,
            meta={
                bstack1ll1ll_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࠨ⁋"): {
                    bstack1ll1ll_opy_ (u"ࠨࡰࡤࡱࡪ࠭⁌"): feature.name,
                    bstack1ll1ll_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ⁍"): feature.filename,
                    bstack1ll1ll_opy_ (u"ࠪࡨࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨ⁎"): feature.description
                },
                bstack1ll1ll_opy_ (u"ࠫࡸࡩࡥ࡯ࡣࡵ࡭ࡴ࠭⁏"): {
                    bstack1ll1ll_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ⁐"): scenario.name
                },
                bstack1ll1ll_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ⁑"): steps,
                bstack1ll1ll_opy_ (u"ࠧࡦࡺࡤࡱࡵࡲࡥࡴࠩ⁒"): bstack1111111l111_opy_(test)
            }
        )
    def bstack1lllll1lll1l_opy_(self):
        return {
            bstack1ll1ll_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧ⁓"): self.hooks
        }
    def bstack1lllll1ll11l_opy_(self):
        if self.bstack111ll111ll_opy_:
            return {
                bstack1ll1ll_opy_ (u"ࠩ࡬ࡲࡹ࡫ࡧࡳࡣࡷ࡭ࡴࡴࡳࠨ⁔"): self.bstack111ll111ll_opy_
            }
        return {}
    def bstack1llllll11ll1_opy_(self):
        return {
            **super().bstack1llllll11ll1_opy_(),
            **self.bstack1lllll1lll1l_opy_()
        }
    def bstack1llllll111ll_opy_(self):
        return {
            **super().bstack1llllll111ll_opy_(),
            **self.bstack1lllll1ll11l_opy_()
        }
    def bstack111l11llll_opy_(self):
        return bstack1ll1ll_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࠬ⁕")
class bstack111ll11lll_opy_(bstack1111llllll_opy_):
    def __init__(self, hook_type, *args,bstack111ll111ll_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1ll111lll1l_opy_ = None
        self.bstack111ll111ll_opy_ = bstack111ll111ll_opy_
        super().__init__(*args, **kwargs, bstack1l1ll1llll_opy_=bstack1ll1ll_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩ⁖"))
    def bstack111l1l1111_opy_(self):
        return self.hook_type
    def bstack1llllll11l11_opy_(self):
        return {
            bstack1ll1ll_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡸࡾࡶࡥࠨ⁗"): self.hook_type
        }
    def bstack1llllll11ll1_opy_(self):
        return {
            **super().bstack1llllll11ll1_opy_(),
            **self.bstack1llllll11l11_opy_()
        }
    def bstack1llllll111ll_opy_(self):
        return {
            **super().bstack1llllll111ll_opy_(),
            bstack1ll1ll_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠ࡫ࡧࠫ⁘"): self.bstack1ll111lll1l_opy_,
            **self.bstack1llllll11l11_opy_()
        }
    def bstack111l11llll_opy_(self):
        return bstack1ll1ll_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࠩ⁙")
    def bstack111lll111l_opy_(self, bstack1ll111lll1l_opy_):
        self.bstack1ll111lll1l_opy_ = bstack1ll111lll1l_opy_