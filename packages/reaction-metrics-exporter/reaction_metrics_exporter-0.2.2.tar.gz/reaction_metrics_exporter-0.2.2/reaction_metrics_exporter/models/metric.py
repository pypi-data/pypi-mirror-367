# for forward references
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import jinja2
import structlog

from ..reaction import Reaction
from .config import Config
from .event import Action, LogEvent, Match
from .exception import UnmatchedAction


logger = structlog.get_logger()
config = Config.get_config()


@dataclass(frozen=True)
class MatchMetric:
    stream: str
    filter: str
    # each element of pattern has its match at same index in matches
    patterns: tuple[str, ...]
    matches: tuple[str, ...]

    # to render matches values
    _env = jinja2.Environment()

    @property
    def labels(self) -> tuple[str, ...]:
        return ("stream", "filter", *self.patterns)

    @property
    def values(self) -> tuple[str, ...]:
        return (self.stream, self.filter, *self.matches)

    @classmethod
    def add(cls, match: Match, metrics: ReactionMetrics) -> MatchMetric:
        patterns: tuple[str, ...] = Reaction.patterns(match.stream, match.filter, match.matches)
        matches: tuple[str, ...] = config.render(match.stream, match.filter, patterns, match.matches)
        metric = cls(match.stream, match.filter, patterns, matches)
        # actions need patterns anyway
        metrics.last_match[(match.stream, match.filter)] = metric
        metrics.last_seen[(metric.stream, metric.filter, metric.matches)] = datetime.now()
        # remove patterns
        if not config.matches_extra:
            metric = MatchMetric(metric.stream, metric.filter, (), ())
        logger.debug(f"new match: stream {metric.stream}, filter {metric.filter}, patterns {metric.patterns}, matches {metric.matches}")
        metrics.matches[metric] += 1
        return metric


@dataclass(frozen=True)
class ActionMetric:
    stream: str
    filter: str
    action: str
    patterns: tuple[str, ...]
    matches: tuple[str, ...]

    @property
    def labels(self) -> tuple[str, ...]:
        return ("stream", "filter", "action", *self.patterns)

    @property
    def values(self) -> tuple[str, ...]:
        return (self.stream, self.filter, self.action, *self.matches)

    @classmethod
    def add(cls, action: Action, metrics: ReactionMetrics) -> ActionMetric:
        # get last corresponding match to fetch patterns
        if last_match := metrics.last_match.get((action.stream, action.filter)):
            metric = ActionMetric(action.stream, action.filter, action.action, last_match.patterns, last_match.matches)
        else:
            logger.warning(
                f"action {action.action} triggered for stream {action.stream} and filter {action.filter} but not previous match found: cannot fetch patterns"
            )
            metric = ActionMetric(action.stream, action.filter, action.action, (), ())
        # do not record patterns
        if not config.actions_extra:
            metric = ActionMetric(action.stream, action.filter, action.action, (), ())
        metrics.last_seen[(metric.stream, metric.filter, metric.matches)] = datetime.now()
        metrics.actions[metric] += 1
        return metric


@dataclass(frozen=True)
class PendingAction:
    stream: str
    filter: str
    action: str
    patterns: tuple[str, ...]
    matches: tuple[str, ...]

    @property
    def labels(self) -> tuple[str, ...]:
        return ("stream", "filter", "action", *self.patterns)

    @property
    def values(self) -> tuple[str, ...]:
        return (self.stream, self.filter, self.action, *self.matches)

    @classmethod
    def from_show(cls, stream: str, filter: str, matches_str: str, action: str) -> PendingAction:
        # reaction show uses space to delimitate matches
        # won't work if space in match
        matches = tuple(matches_str.split(" "))
        if config.pending_extra:
            patterns = Reaction.patterns(stream, filter, matches)
            matches = config.render(stream, filter, patterns, matches)
        else:
            patterns, matches = (), ()
        return cls(stream, filter, action, patterns, matches)


class ReactionMetrics:
    def __init__(self) -> None:
        # meant to be monotonic counters
        self.matches: dict[MatchMetric, int] = defaultdict(int)
        self.actions: dict[ActionMetric, int] = defaultdict(int)

        # holds the last match for the given (stream, filter) pair.
        # the next action for (stream, filter) is considered to be
        # triggered by match. this is true if the logs are well-ordered.
        self.last_match: dict[tuple[str, str], MatchMetric] = {}

        # to keep matches (and derived) a bit of time before
        # cleaning, so that increase-like function won't miss values
        # record stream, filter and matches
        self.last_seen: dict[tuple[str, str, tuple[str, ...]], datetime] = {}

    def add(self, event: LogEvent):
        match event:
            case Action():
                if config.actions:
                    ActionMetric.add(event, self)
            case Match():
                if config.matches:
                    MatchMetric.add(event, self)
            case _:
                raise TypeError(f"unsupported event type: {type(event)}")

    @property
    def n_matches(self) -> int:
        return sum(self.matches.values())

    @property
    def n_actions(self) -> int:
        return sum(self.actions.values())

    def clear(self):
        # reset metrics af if is was first launch
        self.matches.clear()
        self.actions.clear()
        self.last_match.clear()

    def __repr__(self):
        return str(self.__dict__)
