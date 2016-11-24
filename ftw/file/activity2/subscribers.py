from ftw.activity.catalog import get_activity_soup
from ftw.activity.catalog.record import ActivityRecord


def make_file_downloaded_activity(context, event):
    file_downloaded(context)


def file_downloaded(context, actor_userid=None, date=None):
    record = ActivityRecord(context, 'file:downloaded',
                            actor_userid=actor_userid, date=date)
    return get_activity_soup().add(record)
