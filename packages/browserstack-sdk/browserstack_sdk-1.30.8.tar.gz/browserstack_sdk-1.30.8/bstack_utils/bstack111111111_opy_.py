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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1llll111_opy_, bstack11l1lll1lll_opy_, bstack11l1llll11l_opy_
import tempfile
import json
bstack111l1llll1l_opy_ = os.getenv(bstack1ll1ll_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡍ࡟ࡇࡋࡏࡉࠧᶨ"), None) or os.path.join(tempfile.gettempdir(), bstack1ll1ll_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡩ࡫ࡢࡶࡩ࠱ࡰࡴ࡭ࠢᶩ"))
bstack111ll11111l_opy_ = os.path.join(bstack1ll1ll_opy_ (u"ࠨ࡬ࡰࡩࠥᶪ"), bstack1ll1ll_opy_ (u"ࠧࡴࡦ࡮࠱ࡨࡲࡩ࠮ࡦࡨࡦࡺ࡭࠮࡭ࡱࡪࠫᶫ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack1ll1ll_opy_ (u"ࠨࠧࠫࡥࡸࡩࡴࡪ࡯ࡨ࠭ࡸ࡛ࠦࠦࠪࡱࡥࡲ࡫ࠩࡴ࡟࡞ࠩ࠭ࡲࡥࡷࡧ࡯ࡲࡦࡳࡥࠪࡵࡠࠤ࠲ࠦࠥࠩ࡯ࡨࡷࡸࡧࡧࡦࠫࡶࠫᶬ"),
      datefmt=bstack1ll1ll_opy_ (u"ࠩࠨ࡝࠲ࠫ࡭࠮ࠧࡧࡘࠪࡎ࠺ࠦࡏ࠽ࠩࡘࡠࠧᶭ"),
      stream=sys.stdout
    )
  return logger
def bstack1ll1llll1l1_opy_():
  bstack111l1l1llll_opy_ = os.environ.get(bstack1ll1ll_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡇࡉࡇ࡛ࡇࠣᶮ"), bstack1ll1ll_opy_ (u"ࠦ࡫ࡧ࡬ࡴࡧࠥᶯ"))
  return logging.DEBUG if bstack111l1l1llll_opy_.lower() == bstack1ll1ll_opy_ (u"ࠧࡺࡲࡶࡧࠥᶰ") else logging.INFO
def bstack1l1llll1111_opy_():
  global bstack111l1llll1l_opy_
  if os.path.exists(bstack111l1llll1l_opy_):
    os.remove(bstack111l1llll1l_opy_)
  if os.path.exists(bstack111ll11111l_opy_):
    os.remove(bstack111ll11111l_opy_)
def bstack11l1l11ll1_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l1llll11_opy_ = log_level
  if bstack1ll1ll_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨᶱ") in config and config[bstack1ll1ll_opy_ (u"ࠧ࡭ࡱࡪࡐࡪࡼࡥ࡭ࠩᶲ")] in bstack11l1lll1lll_opy_:
    bstack111l1llll11_opy_ = bstack11l1lll1lll_opy_[config[bstack1ll1ll_opy_ (u"ࠨ࡮ࡲ࡫ࡑ࡫ࡶࡦ࡮ࠪᶳ")]]
  if config.get(bstack1ll1ll_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫᶴ"), False):
    logging.getLogger().setLevel(bstack111l1llll11_opy_)
    return bstack111l1llll11_opy_
  global bstack111l1llll1l_opy_
  bstack11l1l11ll1_opy_()
  bstack111l1lllll1_opy_ = logging.Formatter(
    fmt=bstack1ll1ll_opy_ (u"ࠪࠩ࠭ࡧࡳࡤࡶ࡬ࡱࡪ࠯ࡳࠡ࡝ࠨࠬࡳࡧ࡭ࡦࠫࡶࡡࡠࠫࠨ࡭ࡧࡹࡩࡱࡴࡡ࡮ࡧࠬࡷࡢࠦ࠭ࠡࠧࠫࡱࡪࡹࡳࡢࡩࡨ࠭ࡸ࠭ᶵ"),
    datefmt=bstack1ll1ll_opy_ (u"ࠫࠪ࡟࠭ࠦ࡯࠰ࠩࡩ࡚ࠥࡉ࠼ࠨࡑ࠿ࠫࡓ࡛ࠩᶶ"),
  )
  bstack111l1llllll_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l1llll1l_opy_)
  file_handler.setFormatter(bstack111l1lllll1_opy_)
  bstack111l1llllll_opy_.setFormatter(bstack111l1lllll1_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l1llllll_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack1ll1ll_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳ࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴ࠱ࡶࡪࡳ࡯ࡵࡧ࠱ࡶࡪࡳ࡯ࡵࡧࡢࡧࡴࡴ࡮ࡦࡥࡷ࡭ࡴࡴࠧᶷ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l1llllll_opy_.setLevel(bstack111l1llll11_opy_)
  logging.getLogger().addHandler(bstack111l1llllll_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l1llll11_opy_
def bstack111l1ll11l1_opy_(config):
  try:
    bstack111l1ll1l11_opy_ = set(bstack11l1llll11l_opy_)
    bstack111l1ll11ll_opy_ = bstack1ll1ll_opy_ (u"࠭ࠧᶸ")
    with open(bstack1ll1ll_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹ࡮࡮ࠪᶹ")) as bstack111ll1111ll_opy_:
      bstack111l1lll1ll_opy_ = bstack111ll1111ll_opy_.read()
      bstack111l1ll11ll_opy_ = re.sub(bstack1ll1ll_opy_ (u"ࡳࠩࡡࠬࡡࡹࠫࠪࡁࠦ࠲࠯ࠪ࡜࡯ࠩᶺ"), bstack1ll1ll_opy_ (u"ࠩࠪᶻ"), bstack111l1lll1ll_opy_, flags=re.M)
      bstack111l1ll11ll_opy_ = re.sub(
        bstack1ll1ll_opy_ (u"ࡵࠫࡣ࠮࡜ࡴ࠭ࠬࡃ࠭࠭ᶼ") + bstack1ll1ll_opy_ (u"ࠫࢁ࠭ᶽ").join(bstack111l1ll1l11_opy_) + bstack1ll1ll_opy_ (u"ࠬ࠯࠮ࠫࠦࠪᶾ"),
        bstack1ll1ll_opy_ (u"ࡸࠧ࡝࠴࠽ࠤࡠࡘࡅࡅࡃࡆࡘࡊࡊ࡝ࠨᶿ"),
        bstack111l1ll11ll_opy_, flags=re.M | re.I
      )
    def bstack111ll1111l1_opy_(dic):
      bstack111l1lll111_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l1ll1l11_opy_:
          bstack111l1lll111_opy_[key] = bstack1ll1ll_opy_ (u"ࠧ࡜ࡔࡈࡈࡆࡉࡔࡆࡆࡠࠫ᷀")
        else:
          if isinstance(value, dict):
            bstack111l1lll111_opy_[key] = bstack111ll1111l1_opy_(value)
          else:
            bstack111l1lll111_opy_[key] = value
      return bstack111l1lll111_opy_
    bstack111l1lll111_opy_ = bstack111ll1111l1_opy_(config)
    return {
      bstack1ll1ll_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡺ࡯࡯ࠫ᷁"): bstack111l1ll11ll_opy_,
      bstack1ll1ll_opy_ (u"ࠩࡩ࡭ࡳࡧ࡬ࡤࡱࡱࡪ࡮࡭࠮࡫ࡵࡲࡲ᷂ࠬ"): json.dumps(bstack111l1lll111_opy_)
    }
  except Exception as e:
    return {}
def bstack111l1ll1ll1_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack1ll1ll_opy_ (u"ࠪࡰࡴ࡭ࠧ᷃"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l1ll111l_opy_ = os.path.join(log_dir, bstack1ll1ll_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࡣࡨࡵ࡮ࡧ࡫ࡪࡷࠬ᷄"))
  if not os.path.exists(bstack111l1ll111l_opy_):
    bstack111l1ll1lll_opy_ = {
      bstack1ll1ll_opy_ (u"ࠧ࡯࡮ࡪࡲࡤࡸ࡭ࠨ᷅"): str(inipath),
      bstack1ll1ll_opy_ (u"ࠨࡲࡰࡱࡷࡴࡦࡺࡨࠣ᷆"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack1ll1ll_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡤࡱࡱࡪ࡮࡭ࡳ࠯࡬ࡶࡳࡳ࠭᷇")), bstack1ll1ll_opy_ (u"ࠨࡹࠪ᷈")) as bstack111l1ll1l1l_opy_:
      bstack111l1ll1l1l_opy_.write(json.dumps(bstack111l1ll1lll_opy_))
def bstack111l1lll11l_opy_():
  try:
    bstack111l1ll111l_opy_ = os.path.join(os.getcwd(), bstack1ll1ll_opy_ (u"ࠩ࡯ࡳ࡬࠭᷉"), bstack1ll1ll_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡧࡴࡴࡦࡪࡩࡶ࠲࡯ࡹ࡯࡯᷊ࠩ"))
    if os.path.exists(bstack111l1ll111l_opy_):
      with open(bstack111l1ll111l_opy_, bstack1ll1ll_opy_ (u"ࠫࡷ࠭᷋")) as bstack111l1ll1l1l_opy_:
        bstack111l1lll1l1_opy_ = json.load(bstack111l1ll1l1l_opy_)
      return bstack111l1lll1l1_opy_.get(bstack1ll1ll_opy_ (u"ࠬ࡯࡮ࡪࡲࡤࡸ࡭࠭᷌"), bstack1ll1ll_opy_ (u"࠭ࠧ᷍")), bstack111l1lll1l1_opy_.get(bstack1ll1ll_opy_ (u"ࠧࡳࡱࡲࡸࡵࡧࡴࡩ᷎ࠩ"), bstack1ll1ll_opy_ (u"ࠨ᷏ࠩ"))
  except:
    pass
  return None, None
def bstack111ll111111_opy_():
  try:
    bstack111l1ll111l_opy_ = os.path.join(os.getcwd(), bstack1ll1ll_opy_ (u"ࠩ࡯ࡳ࡬᷐࠭"), bstack1ll1ll_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡧࡴࡴࡦࡪࡩࡶ࠲࡯ࡹ࡯࡯ࠩ᷑"))
    if os.path.exists(bstack111l1ll111l_opy_):
      os.remove(bstack111l1ll111l_opy_)
  except:
    pass
def bstack1l11l11l_opy_(config):
  try:
    from bstack_utils.helper import bstack1llll11l_opy_, bstack1l11lll1l_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l1llll1l_opy_
    if config.get(bstack1ll1ll_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡻࡴࡰࡅࡤࡴࡹࡻࡲࡦࡎࡲ࡫ࡸ࠭᷒"), False):
      return
    uuid = os.getenv(bstack1ll1ll_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪᷓ")) if os.getenv(bstack1ll1ll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᷔ")) else bstack1llll11l_opy_.get_property(bstack1ll1ll_opy_ (u"ࠢࡴࡦ࡮ࡖࡺࡴࡉࡥࠤᷕ"))
    if not uuid or uuid == bstack1ll1ll_opy_ (u"ࠨࡰࡸࡰࡱ࠭ᷖ"):
      return
    bstack111ll111ll1_opy_ = [bstack1ll1ll_opy_ (u"ࠩࡵࡩࡶࡻࡩࡳࡧࡰࡩࡳࡺࡳ࠯ࡶࡻࡸࠬᷗ"), bstack1ll1ll_opy_ (u"ࠪࡔ࡮ࡶࡦࡪ࡮ࡨࠫᷘ"), bstack1ll1ll_opy_ (u"ࠫࡵࡿࡰࡳࡱ࡭ࡩࡨࡺ࠮ࡵࡱࡰࡰࠬᷙ"), bstack111l1llll1l_opy_, bstack111ll11111l_opy_]
    bstack111l1ll1111_opy_, root_path = bstack111l1lll11l_opy_()
    if bstack111l1ll1111_opy_ != None:
      bstack111ll111ll1_opy_.append(bstack111l1ll1111_opy_)
    if root_path != None:
      bstack111ll111ll1_opy_.append(os.path.join(root_path, bstack1ll1ll_opy_ (u"ࠬࡩ࡯࡯ࡨࡷࡩࡸࡺ࠮ࡱࡻࠪᷚ")))
    bstack11l1l11ll1_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack1ll1ll_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࠳࡬ࡰࡩࡶ࠱ࠬᷛ") + uuid + bstack1ll1ll_opy_ (u"ࠧ࠯ࡶࡤࡶ࠳࡭ࡺࠨᷜ"))
    with tarfile.open(output_file, bstack1ll1ll_opy_ (u"ࠣࡹ࠽࡫ࡿࠨᷝ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111ll111ll1_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l1ll11l1_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111ll111l1l_opy_ = data.encode()
        tarinfo.size = len(bstack111ll111l1l_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111ll111l1l_opy_))
    bstack1ll1l11l1l_opy_ = MultipartEncoder(
      fields= {
        bstack1ll1ll_opy_ (u"ࠩࡧࡥࡹࡧࠧᷞ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack1ll1ll_opy_ (u"ࠪࡶࡧ࠭ᷟ")), bstack1ll1ll_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱ࡻ࠱࡬ࢀࡩࡱࠩᷠ")),
        bstack1ll1ll_opy_ (u"ࠬࡩ࡬ࡪࡧࡱࡸࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᷡ"): uuid
      }
    )
    bstack111ll111l11_opy_ = bstack1l11lll1l_opy_(cli.config, [bstack1ll1ll_opy_ (u"ࠨࡡࡱ࡫ࡶࠦᷢ"), bstack1ll1ll_opy_ (u"ࠢࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠢᷣ"), bstack1ll1ll_opy_ (u"ࠣࡷࡳࡰࡴࡧࡤࠣᷤ")], bstack11l1llll111_opy_)
    response = requests.post(
      bstack1ll1ll_opy_ (u"ࠤࡾࢁ࠴ࡩ࡬ࡪࡧࡱࡸ࠲ࡲ࡯ࡨࡵ࠲ࡹࡵࡲ࡯ࡢࡦࠥᷥ").format(bstack111ll111l11_opy_),
      data=bstack1ll1l11l1l_opy_,
      headers={bstack1ll1ll_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩᷦ"): bstack1ll1l11l1l_opy_.content_type},
      auth=(config[bstack1ll1ll_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ᷧ")], config[bstack1ll1ll_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨᷨ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack1ll1ll_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥࡻࡰ࡭ࡱࡤࡨࠥࡲ࡯ࡨࡵ࠽ࠤࠬᷩ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack1ll1ll_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡳࡦࡰࡧ࡭ࡳ࡭ࠠ࡭ࡱࡪࡷ࠿࠭ᷪ") + str(e))
  finally:
    try:
      bstack1l1llll1111_opy_()
      bstack111ll111111_opy_()
    except:
      pass