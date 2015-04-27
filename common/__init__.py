# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

def rand_str(length, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))
