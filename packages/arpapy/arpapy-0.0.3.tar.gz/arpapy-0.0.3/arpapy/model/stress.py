# -*- coding: utf-8 -*-
from enum import Enum,unique

@unique
class Stress(Enum):
    No = 0,
    Primary = 1,
    Secondary = 2,

    def mark_ipa(self):
        if Stress.No == self:
            return ''
        elif Stress.Primary == self:
            return 'ˈ'
        else:
            return 'ˌ'

    def mark_arpabet(self):
        return str(self.value[0])
