#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################

from flask.views import MethodView
from holado.common.context.session_context import SessionContext

def _get_session_context():
    return SessionContext.instance()

class ContainerView(MethodView):
    
    # def post(self, body: dict):
    #     pass
    #
    # def put(self, container_name, body: dict):
    #     pass
    #
    # def delete(self, container_name):
    #     pass
    
    def get(self, name=None, limit=100):
        if name is not None:
            if not _get_session_context().docker_client.has_container(name):
                return f"Container '{name}' doesn't exist", 406
            
            cont = _get_session_context().docker_client.get_container(name)
            cont.container.reload()
            res = cont.container.attrs
        else:
            names = _get_session_context().docker_client.get_all_container_names()
            res = [{'name':n, 'status':_get_session_context().docker_client.get_container(n).status} for n in names]
        return res
