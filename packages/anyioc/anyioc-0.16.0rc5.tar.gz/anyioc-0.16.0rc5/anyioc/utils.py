# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import logging
from typing import Callable

from ._utils import get_module_name as _get_module_name
from .ioc import IServiceProvider
from .symbols import Symbols


def auto_enter[R](func: Callable[..., R]) -> Callable[[IServiceProvider], R]:
    '''
    auto enter the context manager when it created.

    the signature of func should be `(ioc) => any`.
    '''
    def new_func(ioc: IServiceProvider, /) -> R:
        mgr = func(ioc)
        rv = ioc.enter(mgr) # type: ignore
        return rv

    return new_func

def get_logger(ioc: IServiceProvider, /) -> logging.Logger:
    '''
    a helper that use to get logger from ioc.

    Usage:

    ``` py
    ioc.register_transient('logger', get_logger) # use transient to ensure no cache
    logger = ioc['logger']
    assert logger.name == __name__ # the logger should have module name
    ```
    '''
    fr = ioc[Symbols.caller_frame]
    name = _get_module_name(fr)
    return logging.getLogger(name)

def is_root(provider: IServiceProvider) -> bool:
    '''
    Test is the IServiceProvider is the root provider or not.
    '''
    return provider[Symbols.provider_root] is provider

def get_scope_depth(provider: IServiceProvider) -> int:
    '''
    Get the depth of scopes.

    The root provider is 0.
    '''
    depth = 0
    root = provider[Symbols.provider_root]
    while provider is not root:
        provider = provider[Symbols.provider_parent]
        depth += 1
    return depth
