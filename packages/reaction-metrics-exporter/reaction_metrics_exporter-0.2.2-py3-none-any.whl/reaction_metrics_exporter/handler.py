import asyncio
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Self

from asyncio_simple_http_server import HttpHeaders, HttpResponse, uri_mapping
import prometheus_client
from prometheus_client.core import (
    CounterMetricFamily,
    GaugeMetricFamily,
    Metric,
    REGISTRY,
)
from prometheus_client.registry import Collector
import structlog

from reaction_metrics_exporter import __version__

from .models.config import Config
from .models.metric import PendingAction, ReactionMetrics
from .reaction import Reaction

logger = structlog.get_logger()
config = Config.get_config()


class MetricsHandler:
    HEADERS = HttpHeaders().set("Content-Type", "text/plain; charset=UTF-8")

    def __init__(self, metrics: ReactionMetrics):
        self._collector = ReactionCollector(metrics)
        self._metrics = metrics

        if not config.internals:
            REGISTRY._collector_to_names = {}
        REGISTRY.register(self._collector)

    @classmethod
    async def create(cls, metrics: ReactionMetrics) -> Self:
        inst = cls(metrics)
        asyncio.create_task(inst.clear())
        return inst

    @uri_mapping("/metrics")
    async def metrics(self):
        # calls collect on every collector
        logger.debug("got a request on /metrics")
        async with asyncio.Lock():
            openmetrics = prometheus_client.generate_latest(REGISTRY)
        return HttpResponse(200, self.HEADERS, openmetrics)

    async def clear(self):
        """
        ensure matches and actions are not cleared from 10 minutes.
        this is to avoid that a small scraping interval, followed by
        a systematic clear, gives false results (such as 0 increase).
        usually time series are not so short-lived, this is why
        we need to adapt.
        """
        while True:
            await asyncio.sleep(config.check_clear)
            now = datetime.now()
            delta = timedelta(seconds=config.clear_after)
            async with asyncio.Lock():
                for (stream, filter, matches), time in self._metrics.last_seen.items():
                    if now - time > delta:
                        self._remove_from_spec(stream, filter, matches)

    def _remove_from_spec(self, stream: str, filter: str, matches: tuple[str, ...]):
        for match in list(self._metrics.matches):
            if match.values == (stream, filter, *matches):

                print(match.values, (stream, filter, *matches))
                del self._metrics.matches[match]
        for action in list(self._metrics.actions):
            print(action.__dict__, matches)
            if action.stream == stream and action.filter == filter and action.matches == matches:
                del self._metrics.actions[action]
        # pending actions live largely longer than scrape time, so
        # we don't need to address them


class ReactionCollector(Collector):
    def __init__(self, metrics: ReactionMetrics) -> None:
        self._metrics = metrics

    def collect(self) -> tuple[prometheus_client.Metric, ...]:
        logger.debug("start metrics collection")
        collected: list[Metric] = []

        # all the metrics we are going to export
        # they do not accumulate: one object per collection
        build_info = GaugeMetricFamily(
            "reaction_exporter_build_info",
            "A metric with a constant '1' value labeled by version of the reaction_metrics_exporter.",
            labels=("version",),
        )
        collected.append(build_info)

        build_info.add_metric((__version__,), 1.0)
        if config.matches:
            match_total = CounterMetricFamily(
                "reaction_match_total",
                "Total number of matched logs.",
            )
            collected.append(match_total)
            # labels can vary with patterns and action names
            # we need to change global setting everytime because
            # the way the prometheus lib is made

            for match, count in self._metrics.matches.items():
                match_total._labelnames = match.labels
                match_total.add_metric(match.values, count)
        if config.actions:
            action_total = CounterMetricFamily(
                "reaction_action_total",
                "Total number of matched logs.",
            )
            collected.append(action_total)
            for action, count in self._metrics.actions.items():
                action_total._labelnames = action.labels
                action_total.add_metric(action.values, count)

        n_pending = 0
        if config.pending:

            pending_count = GaugeMetricFamily(
                "reaction_pending_count",
                "Current number of pending actions.",
            )
            collected.append(pending_count)
            # pending actions cannot easily be inferred from logs: use `reaction show`
            for pending, count in self._collect_pending():
                pending_count._labelnames = pending.labels
                pending_count.add_metric(pending.values, count)
                n_pending += count

        logger.info(
            f"end collecting metrics; {self._metrics.n_matches} new matches; {self._metrics.n_actions} new actions; {n_pending} pending actions"
        )

        return tuple(collected)

    def _collect_pending(self):
        show: OrderedDict[str, Any] = Reaction.show()
        for stream, filters in show.items():
            for filter, state in filters.items():
                for matches, data in state.items():
                    # i.e. action pending for this (stream, filter)
                    if "actions" in data:
                        for action, _ in data["actions"].items():
                            metric = PendingAction.from_show(stream, filter, matches, action)
                            yield metric, len(data["actions"])
