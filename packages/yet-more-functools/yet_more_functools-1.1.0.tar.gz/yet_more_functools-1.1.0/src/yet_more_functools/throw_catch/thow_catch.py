# SPDX-FileCopyrightText: © 2025 Roger Wilson
#
# SPDX-License-Identifier: MIT

import contextlib as cl
import contextvars as cv
import typing as ty
import warnings

from ..util import gather
from ..util import reform_tag
from ..util import scatter

# This contextvar must be created on main thread.
_THROW_CATCH_CONTEXT = cv.ContextVar('THROW_CATCH_CONTEXT', default={})


class ThrowCatchException(Exception):
    """
    This is a carrier exception which transports the object "thrown" to a catch/catcher listening for the same tag.
    """

    def __init__(self, thrown, tag=None):
        super().__init__()
        self.thrown = thrown
        self.tag = tag


def throw(x: ty.Any, tag: ty.Union[ty.Hashable, ty.Sequence[ty.Hashable]] = None):
    """
    Calls to sow work in conjunction with calls to "catch" or "catcher".  Together they allow intermediate values to
    be returned from arbitrarily deep in the call hierarchy, interrupting the execution flow.

    throw(x, [tag=None])

    See also: catch, catcher.

    Example.

    .. code-block:: python

        def f(x):
            if x==0:
                throw(x)
            return x+1

        catch(f, 0)

    will return (None, 0) : As the throw executed, so f did not return,  and None is the default tag for both throw
    and catch.

    catch(f, 1)

    will return 2 : As the throw didn't execute so f returned normally.

    Execution flow is interrupted by raising a special type of exception but only if throw knows an encapsulating
    catcher or catch is waiting to handle it with a matching tag.

    :param x: The value being thrown.
    :param tag: The (hashable) tag value or sequence of tags for which the value x is to be thrown, matching tag or
        tags in an enclosing catch or catcher.
        Default is None.
    :return: The value throw is called with, x, IF it has been disabled for the given tag.
    """
    if not isinstance(tag, str) and not isinstance(tag, tuple) and isinstance(tag, ty.Sequence):
        for t in tag:
            throw(x, tag=t)
    else:
        if tag in _THROW_CATCH_CONTEXT.get():
            if _THROW_CATCH_CONTEXT.get()[tag][-1]:
                raise ThrowCatchException(x, tag=tag)
        elif None in _THROW_CATCH_CONTEXT.get():
            if _THROW_CATCH_CONTEXT.get()[None][-1]:
                warnings.warn(
                    f'No tag {tag} found as there is no outer catch for this specific tag.  Values will be sent to the '
                    f'tag=None catch which does exist as tuples of (tag, value).')
                raise ThrowCatchException((tag, x), tag=None)
        else:
            warnings.warn(f'No tag {tag} found as there is no outer catch for this tag OR tag=None.',
                          category=UserWarning)
    return x


TAG_TYPE = ty.Union[ty.Hashable, ty.Tuple[ty.Hashable, bool]]

CATCHER_TAG_TYPE = ty.Union[TAG_TYPE, ty.Sequence[TAG_TYPE], ty.Dict[ty.Hashable, bool]]


@cl.contextmanager
@reform_tag(True)  # Default to catch is on for each tag.
def catcher(tag: CATCHER_TAG_TYPE = None) -> ty.Generator[ty.Callable[[], ty.Tuple[ty.Hashable, ty.Any]], None, None]:
    """
    Catcher is a context manager which wraps around the execution of arbitrary code and catches the values 'thrown'
    by any calls to throw made inside the managed block.  It emits a callable which may be called after the block
    completes that carries any value thrown, as a 2-tuple: (tag, value), or None is nothing was thrown.

    catcher([tag=None])

    Example:

    .. code-block:: python

        def f(x):
            if x==0:
                throw(x)
            return x+1

        with catcher() as ct:
            print(f"The return value was {f(0)}.")
        print(f"The caught value was {ct()}")

        with catcher() as ct:
            print(f"The return value was {f(1)}.")
        print(f"The caught value was {ct()}")


    Will produce:
    .. code-block:: text

        The caught value was (None, 0)
        The return value was 2.
        The caught value was None

    Note that the first print in the first context-managed block does not actually run.  Execution is interrupted
    inside f and returns into the context-manager catcher.

    :param tag: A hashable tag, a 2-tuple: (hashable tag, boolean) or a mixed sequence of these.
    :return: A zero-argument executable which will return a 2-tuple: (tag, value thrown) or None if no throw on any
        of the tags given occurs.
    """

    def return_caught():
        """This is the callable that is returned by the context manager to carry the caught data."""
        if not hasattr(return_caught, "caught"):
            raise RuntimeError("Context manager 'catcher' context manager block has not exited: Nothing to catch.")
        return return_caught.caught

    _tce = None
    try:
        scatter(tag, _THROW_CATCH_CONTEXT)
        try:
            yield return_caught
        except ThrowCatchException as tce:
            _tce = tce
    finally:
        # Setting return_caught.caught (it existing as an attribute) lets us know that gather has been executed,
        # and we are therefore out of the context try block. Different to reaper, as in reaper the result of gather
        # will always be something, whereas here it can be None.
        gathered = gather(tag, _THROW_CATCH_CONTEXT)
        return_caught.caught = None
        if _tce is not None:
            if any(v for k, v in gathered.items()):
                return_caught.caught = (_tce.tag, _tce.thrown)
            else:
                raise _tce


def catch(f: ty.Callable, *args, tag: CATCHER_TAG_TYPE = None, **kwargs) -> ty.Any:
    """
    Catch executes the function f with the given args and kwargs within a catcher context managed block and returns
    either the result of the call to f or any value thrown during the execution of f on any of the tags given.

    catch(f, *args, **kwargs, [tag=None])

    examples:

    .. code-block:: python

        def f(x):
            if x==0:
                throw(x)
            return x+1

        print(f"catch(f, 0) = {catch(f, 0)}")

        print(f"catch(f, 1) = {catch(f, 1)}")

    Will produce:

    .. code-block:: text

        catch(f, 0) = (None, 0)
        catch(f, 1) = 2

    In the first case throw is executed and f is interrupted so the return from catch is a 2-tuple of (None,
    0) where None is the default tag and 0 is the value thrown.  In the second case 2 returned as f executes to the end.

    :param f: An executable function.
    :param args: Passed to f.
    :param tag: A hashable tag, a 2-tuple: (hashable tag, boolean) or a mixed sequence of these.
    :param kwargs: Passed to f.
    :return: The value returned by f (if no throw occurs) or a 2-tuple: (tag, value thrown) if a throw does occur.
    """
    if not callable(f):
        raise TypeError('First argument to catch must be a callable.')

    with catcher(tag) as ct:
        result = f(*args, **kwargs)

    if (caught := ct()) is not None:
        return caught
    return result
