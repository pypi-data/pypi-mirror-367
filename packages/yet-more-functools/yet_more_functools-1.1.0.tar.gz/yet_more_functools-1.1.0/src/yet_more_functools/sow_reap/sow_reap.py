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
_SOW_REAP_CONTEXT = cv.ContextVar('SOW_REAP_CONTEXT', default={})

DESTINATION_TYPE = ty.Union[ty.Collection, ty.Callable[[], ty.Collection], ty.Callable[[ty.Any], ty.Any], None]


def sow(x: ty.Any, tag: ty.Union[ty.Hashable, ty.Sequence[ty.Hashable]] = None) -> ty.Any:
    """
    Calls to sow work in conjunction with "reap" or "reaper". Together they allow intermediate values to be returned
    from arbitrarily deep in the call hierarchy of a function without requiring any modification of the return
    signatures of the function(s) being called or any intermediates.

    Sow appends a value x onto collection for later delivery by a corresponding reap call somewhere higher up the call
    hierarchy, or alternatively it invokes a callback function on x.  The particular collection or callback used is
    identified by a hashable tag (defaults to None).  Each tag must be setup by a higher level, encapsulating call to
    reap.  Calls to reap may be nested inside calls to sow, even using the same tag.

    sow(x, [tag=None])

    See also: reap, reaper.

    example:

    .. code-block:: python

        def f(n):
            return sum(sow(i) for i in range(n))

        reap(f, 10)

    will return

    (45, {None: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]})

    :param  x: The value that is appended or called back.
    :param tag: The (hashable) tag value or sequence of tags for which the value x is to be sown, matching tag or
        tags in an enclosing reap or reaper.
                Default is None.
    :return: x
    """

    if not isinstance(tag, str) and not isinstance(tag, tuple) and isinstance(tag, ty.Sequence):
        # A sequence of tags.
        for t in tag:
            sow(x, t)
    else:
        # A single tag.
        if tag in _SOW_REAP_CONTEXT.get():
            send(x, tag)
        else:
            if None in _SOW_REAP_CONTEXT.get():
                warnings.warn(f'No tag {tag} found as there is no outer reap for this specific tag.  Values will '
                              f'be pushed onto the tag=None queue which does exist as tuples of (tag, value).')
                # Send (tag, value) to destination=None.
                # noinspection PyTypeChecker
                send((tag, x), None)
            else:
                warnings.warn(f'No tag {tag} found as there is no outer reap for this tag OR tag=None.',
                              category=UserWarning)

    return x


@cl.contextmanager
@reform_tag(list) # Default collection constructor is list.
def reaper(tag: ty.Dict = None) -> ty.Generator[ty.Callable[[], ty.Any], None, None]:
    """
    Reaper works in conjunction with sow. It is a context manager that sets up collections or callbacks on specific
    tags, which the act as destinations for any values sow is called on, with those tags, within the managed block.
    The calls to sow can be made arbitrarily deep in the call hierarchy.  The context manager emits a callable that
    when called outside the managed block returns a dict keyed by the tags, with values of either the collections of
    values that sow was called on, or the callbacks previously registered.  Reaper may be nested inside sow,
    even using the same tags.

    Example:

    .. code-block:: python

        def f(n):
            return sum(sow(i) for i in range(n))

        with reaper() as rp:
            result = f(10)
        print((result, rp()))

    Will produce:

    (45, {None: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]})

    :param tag: A hashable id, a 2-tuple: (a hashable id, a destination), or a mixed sequence of the same.  A
    destination may be a collection (with an append method), a zero argument collection constructor (e.g. list) or a
    single argument callback.  If a destination is set to None (note: the destination not the tag) then any calls to
    sow using that tag inside the managed block will be ignored.  If a destination is not explicitly provided the
    constructor "list" is used.
        Default is None.
    :return:  A zero-argument callable that returns a dict {tag:collection|callback} of any tag data pushed on to tag
        collections queues by calls to sow during the evaluation of f or the callbacks previously registered under
        those tags.  This can only be called after the managed block has exited.
    """

    tag = {k: v for k, v in (resolve_destination(k, v) for k, v in tag.items())}

    def return_reaped() -> ty.Any:
        """This is the callable that is returned by the context manager to carry the reaped data."""
        if return_reaped.reaped is None:
            raise RuntimeError("Context manager 'reaper' context manager block has not exited: Nothing to reap.")
        return return_reaped.reaped

    return_reaped.reaped = None

    try:
        scatter(tag, _SOW_REAP_CONTEXT)
        yield return_reaped
    finally:
        return_reaped.reaped = gather(tag, _SOW_REAP_CONTEXT)


def reap(f: ty.Callable, *args, tag: ty.Sequence = None, **kwargs) -> ty.Tuple[ty.Any, ty.Dict]:
    """
    Reap works in conjunction with calls to 'sow'.  Reap takes a function and its arguments and keyword-arguments and
    executes it within a reaper context managed block, using the given tags. Reap then returns a 2-tuple: (the result
    of the function call, a dict keyed by the tags, with values of either the collections of  values that sow was
    called on, or the callbacks previously registered).  Reap may be nested inside sow, even using the same tags.

    reap(f, *args, **kwargs, [tag=None])

    See also: sow.

    example:

    .. code-block:: python

        def f(n):
            return sum(sow(i) for i in range(n))

        reap(f, 10)

    will return:

    (45, {None: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]})

    :param f: A function passed to reap which will then be called with the args and kwargs provided, i.e. reap will
        execute result=f(*args, **kwargs) and return this as the first element of the 2-tuple returned.
    :param args: Passed to the function f.
    :param kwargs: Passed to the function f.
    :param tag: A hashable id, or a 2-tuple of (a hashable id, a destination) or sequence of these.  A destination
        may be a collection (with an append method), a zero-argument constructor for a collection (with an append
        method, e.g. list) or a single-argument callback function.  Setting a destination to None effectively
        disables any calls to sow made using that tag. If a call to sow(x, [tag=None]) is made during the execution
        of f, anywhere in the call hierarchy, the value f will either be appended to the collection with the
        corresponding tag OR the callback associated with that tag will be invoked on x.  A dictionary of the tags and
        collections or callbacks will be returned by reap.
        The default tag is None and the implied destination is list.
    :returns: A 2-tuple of the result of the call to f(*args, **kwargs) and a dict of any tag data pushed on to tag
        collections by calls to sow during the evaluation of f or the callbacks previously registered under those tags.
    """

    with reaper(tag) as rp:
        result = f(*args, **kwargs)
    return result, rp()


def send(x: ty.Any, tag: ty.Hashable) -> None:
    """
    Destination is the most recent [-1] entry in the stack for this tag.  If destination is a callable function,
    call that with the payload,  if not then append payload (it will be an appendable collection). If destination is
    None then the outer reap has explicitly disabled the sow, do nothing.
    :param x: The value to send.
    :param tag: The tag to use to look up the destination in the context dict.
    :return: None
    """
    if (destination := _SOW_REAP_CONTEXT.get()[tag][-1]) is not None:
        if callable(destination):
            # Callback
            destination(x)
        else:
            # Collection
            destination.append(x)


def resolve_destination(tag: ty.Hashable,
                        dest: ty.Union[ty.Collection,
                        ty.Callable[[], ty.Collection],
                        ty.Callable[[ty.Any], ty.Any],
                        None]) -> \
        ty.Tuple[ty.Hashable, ty.Union[None, ty.Callable[[ty.Any], ty.Any], ty.Collection]]:
    """
    This checks the destination 'dest' for the given tag.  This should be None, a collection with an 'append' method
    or a callback. It attempts to call the potential collection constructor 'dest' with no arguments.  If this is
    successful and the result is a collection with an 'append' method then this is returned in place of the function.
     If this is not successful then the function itself, presumably a callback is returned.
    :param tag: A hashable tag.
    :param dest: A collection, a collection-constructor,  a callback, or None.
    :return: A 2-tuple: (tag, a collection | a callback | None)
    """
    if callable(dest):
        try:
            dest = dest()
            if dest is None:
                warnings.warn(f"Call to {dest} on {tag} returned None, not a collection.")
        except TypeError:
            pass
    if dest is None or hasattr(dest, "append") or callable(dest):
        return tag, dest

    raise ValueError(
        f"Destination {dest} on tag {tag} is not None, a collection (or did not build a collection) with an append "
        f"method or a callback.")
