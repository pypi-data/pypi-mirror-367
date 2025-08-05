#!/usr/bin/env python

import sys
sys.path.insert(0, '...')

from reportlab.platypus import Spacer

from noWord.common.PluginInterface import PluginInterface
from reportlab.lib.units import cm, mm


class VSpaceBlock(PluginInterface):
    def __init__(self):
        pass

    def Name(self):
        return 'vspace'

    def init(self, context):
        pass

    def prepare(self, block, context):
        pass

    def process(self, block, context):

        # height element, default 12
        height = block["height"] * cm if "height" in block else 12

        content = []
        content.append(Spacer(1, height))
        return content
