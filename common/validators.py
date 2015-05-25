# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _


GithubRevisionValidator = RegexValidator(r'^[a-zA-Z0-9]+$', _('Revision must be alphanumeric'))
