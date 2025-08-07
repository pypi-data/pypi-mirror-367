from typing import *
from collections import deque
from zoneinfo import ZoneInfo

from collections import defaultdict
from datetime import datetime, time, timezone, timedelta, tzinfo
from wcd_envoyer.channels import TemplatedMessages, MessageData

from ..models import ChannelAvailability, EventAvailability


__all__ = 'TZ_KEY', 'IMMEDIATE_KEY', 'split_scheduled_messages',


TimeRange = Tuple[time, time]
TimeRanges = List[TimeRange]
TZ_KEY = 'tz'
IMMEDIATE_KEY = 'send_immediate'


def resolve_tz(tz: Optional[Union[str, tzinfo]]) -> Optional[tzinfo]:
    if tz is None or isinstance(tz, tzinfo):
        return tz

    if isinstance(tz, str):
        return ZoneInfo(tz)


def normalize_ranges(ranges: Iterable[TimeRange]) -> TimeRanges:
    result = []
    q = deque(sorted(ranges))

    while q:
        f_since, f_till = q.popleft()

        while q:
            s_since, s_till = nxt = q.popleft()

            if not (f_till >= s_since and f_since <= s_till):
                q.appendleft(nxt)
                break

            f_since = min(f_since, s_since)
            f_till = max(f_till, s_till)

        result.append((f_since, f_till))

    return result


def intersect_timeranges(first: TimeRanges, second: TimeRanges) -> TimeRanges:
    if len(first) == 0:
        return second

    if len(second) == 0:
        return first

    intersects = []

    for f_since, f_till in first:
        for s_since, s_till in second:
            if s_since > f_till:
                break

            if f_till >= s_since and f_since <= s_till:
                intersects.append((max(f_since, s_since), min(f_till, s_till)))

    return sorted(intersects)


def fit_closest_date(
    now: datetime,
    ranges: TimeRanges,
    tz: Optional[tzinfo] = None,
) -> datetime:
    if ranges is None:
        return now

    previous_tz = now.tzinfo
    result = now if tz is None else now.astimezone(tz)
    current_time = result.time()
    result_time = None
    ranges = sorted(ranges)

    for since, till in ranges:
        if till >= current_time >= since:
            result_time = current_time
            break

        if since > current_time:
            result_time = since
            break

    if result_time is None:
        result += timedelta(days=1)
        result_time = ranges[0][0]

    result = result.replace(
        hour=result_time.hour,
        minute=result_time.minute,
        second=result_time.second,
        microsecond=result_time.microsecond,
    )

    return result.astimezone(previous_tz)


def split_recipients(
    recipients: Iterable[dict],
    now: datetime,
    available: TimeRanges,
    tz_key: str = TZ_KEY,
    immediate_key: str = IMMEDIATE_KEY,
) -> Dict[datetime, List[dict]]:
    to_tz = defaultdict(list)
    result = defaultdict(list)

    for recipient in recipients:
        if recipient.get(immediate_key, False):
            result[now].append(recipient)
            continue

        to_tz[resolve_tz(recipient.get(tz_key, None))].append(recipient)

    tz_to_send_at = {
        tz: fit_closest_date(now, available, tz=tz)
        for tz in to_tz
    }

    for tz, send_at in tz_to_send_at.items():
        result[send_at] += to_tz[tz]

    return result


def split_scheduled_messages(
    channel_availability: List[ChannelAvailability],
    messages: TemplatedMessages,
    now: datetime,
    tz_key: str = TZ_KEY,
    immediate_key: str = IMMEDIATE_KEY,
    events_availability: Dict[str, List[EventAvailability]] = {},
) -> Dict[datetime, TemplatedMessages]:
    to_date = defaultdict(list)
    channel_available = normalize_ranges(
        (x.available_since, x.available_till)
        for x in channel_availability
    )
    event_messages = defaultdict(list)

    for templated_message in messages:
        event_messages[templated_message[0].event].append(templated_message)

    event_available = {
        event: intersect_timeranges(channel_available, normalize_ranges(
            (x.available_since, x.available_till)
            for x in events_availability.get(event, [])
        ))
        for event in event_messages
    }

    for event, messages in event_messages.items():
        available = event_available[event]

        if len(available) == 0:
            to_date[now] += messages
            continue

        for message, template in messages:
            for send_at, recipients in split_recipients(
                message.recipients, now, available, tz_key=tz_key,
                immediate_key=immediate_key,
            ).items():
                to_date[send_at].append((
                    MessageData(
                        channel=message.channel, event=message.event,
                        recipients=recipients, context=message.context,
                    ),
                    template,
                ))

    return to_date
