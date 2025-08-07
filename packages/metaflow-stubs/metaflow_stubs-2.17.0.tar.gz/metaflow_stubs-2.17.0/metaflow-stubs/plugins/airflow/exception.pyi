######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.17.0                                                                                 #
# Generated on 2025-08-06T11:05:03.974322                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from ...exception import MetaflowException as MetaflowException

class AirflowException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, msg):
        ...
    ...

class NotSupportedException(metaflow.exception.MetaflowException, metaclass=type):
    ...

