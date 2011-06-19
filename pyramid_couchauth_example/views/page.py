# Copyright (c) 2011, Ryan Bourgeois <bluedragonx@gmail.com>
# All rights reserved.
#
# This software is licensed under a modified BSD license as defined in the
# provided license file at the root of this project.  You may modify and/or
# distribute in accordance with those terms.
#
# This software is provided "as is" and any express or implied warranties,
# including, but not limited to, the implied warranties of merchantability and
# fitness for a particular purpose are disclaimed.

from pyramid.security import authenticated_userid

def public(context, request):
    username = authenticated_userid(request)
    if username is None:
        username = ""
    return {'username': username}

def private(context, request):
    return {}

