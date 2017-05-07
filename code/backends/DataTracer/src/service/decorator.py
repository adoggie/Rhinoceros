#coding:utf-8

import traceback
from functools import wraps
from flask import request,g

from camel.fundamental.application.app import instance
from camel.rhinoceros.webapi import CallReturn,ErrorReturn
from service.access_user import AccessUserManager
from camel.rhinoceros.errors import ErrorDefs
from camel.rhinoceros.webapi import CallReturn,ErrorReturn,ErrorDefs
from camel.rhinoceros.token import encode_user_token,decode_user_token



def user_access_check(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        ticket = request.values.get('ticket')
        if not ticket:
            return ErrorReturn(ErrorDefs.TokenInvalid).json
        user_info = decode_user_token(ticket)
        if not user_info:
            return ErrorReturn(ErrorDefs.TokenInvalid).json

        user_id = user_info.get('user_id')
        user = AccessUserManager.instance().getUser(user_id)
        user.delta = user_info
        g.user = user
        try:
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
            return ErrorReturn(ErrorDefs.SystemError, errmsg=traceback.format_exc()).json
    return _wrapper




