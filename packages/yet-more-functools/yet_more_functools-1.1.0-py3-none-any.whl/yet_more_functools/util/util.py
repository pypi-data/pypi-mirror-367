# SPDX-FileCopyrightText: © 2025 Roger Wilson
#
# SPDX-License-Identifier: MIT

import contextvars as cv
import functools as ft
import typing as ty
import warnings


def scatter(tag: ty.Union[ty.Dict[ty.Hashable, ty.Any], None], context: cv.ContextVar) -> None:
    """
    Appends the value for each given tag onto the FIFO stacks for each tag.
    Setting up a new stack for any unknown tag.
    :param tag:  An explicit sequence of 2-tuples: (hashable tag, value)
    :param context: A contextvars.ContextVar object holding a dict as default, to store the value stacks for each tag
    in a thread/async safe manner.
    :return: None
    """

    if tag is None:
        return None
    for t, v in tag.items():
        if t not in context.get():
            # Set up a stack for this tag.
            context.get()[t] = []
        # Add the value for this tag onto the stack for this tag.
        context.get()[t].append(v)
    return None


def gather(tag: ty.Union[ty.Hashable, ty.Dict[ty.Hashable, ty.Any], None], context: cv.ContextVar) -> \
        ty.Union[ty.Dict, None]:
    """
    Search through the context for the outermost values for those tags and return as a dict vs tag.  Popping these
    off the stacks for those tags.  If a stack for a tag becomes empty were have reached the outermost level for that
    tag so remove that tag (key) from the context dict.
    :param tag: A single hashable tag or a sequence of 2-tuples: (hashable tag, value).
    :param context: A contextvars.ContextVar object holding a dict as default, to store the value stacks for each tag
    in a thread/async safe manner.
    :return: A dict of tag:value.
    """
    if isinstance(tag, ty.Hashable):
        # Get the last (innermost) stack in the list of stacks for this tag.
        gathered = context.get()[tag].pop()
        if len(context.get()[tag]) == 0:
            context.get().pop(tag)
        return {tag: gathered}
    else:
        if tag is not None:
            return ft.reduce(lambda a, b: a | b, (gather(t, context) for t in tag.keys()))
    return None


def reform_tag(bare_tag_default):
    def reform_tag_wrapper(f: ty.Callable) -> ty.Callable:
        """
        Intercepts calls to the decorated function and processes the single argument tag, transforming it from a
        hashable object, a 2-tuple of a hashable object and an associated value of some kind, a dict or a mixed
        sequence of these, into a dict before calling the decorated function on this.
        :param f: A function which takes a single argument tag which must be a dict.
        :return: A function accepting the various other forms of the single argument tag.
        """

        # noinspection PyShadowingNames
        def is_pair(tag: ty.Any) -> bool:
            if isinstance(tag, ty.Tuple) and \
                    len(tag) == 2 and \
                    isinstance(tag[0], ty.Hashable):
                warnings.warn(
                    "tag:destination pairs should be given as a dict. 2-tuples where the first element is hashable "
                    "are supported now but will be removed in version 2. So tag=(None, None) should be given as tag={"
                    "None:None}.  As of version 2.0.0 tuple tag values include pairs will be regarded as bare tags, "
                    "not tag/destination pairs.",
                    DeprecationWarning)
                return True
            return False

        # noinspection PyShadowingNames
        def is_bare(tag: ty.Any) -> bool:
            return isinstance(tag, ty.Hashable)

        # noinspection PyShadowingNames
        def is_sequence(tag: ty.Any) -> bool:
            return isinstance(tag, ty.Sequence) \
                and not isinstance(tag, str) \
                and all(isinstance(x, dict) or is_pair(x) or is_bare(x) for x in tag)

        # noinspection PyShadowingNames
        def process(tag: ty.Any) -> ty.Dict[ty.Hashable, ty.Any]:
            if isinstance(tag, dict):
                return tag
            if isinstance(tag, ty.Hashable):
                if is_pair(tag):
                    # noinspection PyTypeChecker
                    return dict([tag])
                elif is_bare(tag):
                    return {tag: bare_tag_default}
            raise ValueError(f"Cannot handle tag of type {tag}. Note as tags can be tuples, "
                             f"any tuples of tags must be pairs of hashable and None|Collection|Callable.")

        @ft.wraps(f)
        def reformed(tag=None) -> ty.Any:
            if isinstance(tag, dict):
                return f(tag)
            elif is_bare(tag) or is_pair(tag):
                return f(process(tag))
            elif is_sequence(tag):
                return f(ft.reduce(lambda a, b: a | b, (process(x) for x in tag)))

            raise ValueError(f"Cannot handle tag of type {tag}. Note as tags can be tuples, "
                             f"any tuples of tags must be pairs of hashable and None|Collection|Callable.")

        return reformed

    return reform_tag_wrapper
