"""
Contains the `Celery Beat schedule
<http://celery.rtfd.org/en/latest/userguide/periodic-tasks.html>`_.
"""

from datetime import timedelta

from celery.schedules import crontab

from ichnaea.models import (
    BlueShard,
    CellShard,
    DataMap,
    WifiShard,
)


def celerybeat_schedule(app_config):
    """Return the celery beat schedule as a dictionary."""

    sections = app_config.sections()

    schedule = {

        # Monitoring

        'monitor-queue-size': {
            'task': 'ichnaea.data.tasks.monitor_queue_size',
            'schedule': timedelta(seconds=60),
            'options': {'expires': 57},
        },
        'monitor-api-users': {
            'task': 'ichnaea.data.tasks.monitor_api_users',
            'schedule': timedelta(seconds=600),
            'options': {'expires': 570},
        },
        'monitor-api-key-limits': {
            'task': 'ichnaea.data.tasks.monitor_api_key_limits',
            'schedule': timedelta(seconds=600),
            'options': {'expires': 570},
        },

        # Statistics

        'update-statcounter': {
            'task': 'ichnaea.data.tasks.update_statcounter',
            'schedule': crontab(minute=3),
            'options': {'expires': 2700},
        },
        'update-statregion': {
            'task': 'ichnaea.data.tasks.update_statregion',
            'schedule': timedelta(seconds=3600 * 6),
            'options': {'expires': 3600 * 5},
        },

        # Data Pipeline

        'schedule-export-reports': {
            'task': 'ichnaea.data.tasks.schedule_export_reports',
            'schedule': timedelta(seconds=6),
            'options': {'expires': 10},
        },
        'update-incoming': {
            'task': 'ichnaea.data.tasks.update_incoming',
            'schedule': timedelta(seconds=5),
            'options': {'expires': 10},
        },

        'update-cellarea': {
            'task': 'ichnaea.data.tasks.update_cellarea',
            'schedule': timedelta(seconds=14),
            'options': {'expires': 20},
        },
        'update-cellarea-ocid': {
            'task': 'ichnaea.data.tasks.update_cellarea_ocid',
            'schedule': timedelta(seconds=15),
            'options': {'expires': 20},
        },

        'update-score': {
            'task': 'ichnaea.data.tasks.update_score',
            'schedule': timedelta(seconds=9),
            'options': {'expires': 10},
        },

    }

    for shard_id in BlueShard.shards().keys():
        schedule.update({
            'update-blue-' + shard_id: {
                'task': 'ichnaea.data.tasks.update_blue',
                'schedule': timedelta(seconds=18),
                'kwargs': {'shard_id': shard_id},
                'options': {'expires': 20},
            }
        })

    for shard_id in CellShard.shards().keys():
        schedule.update({
            'update-cell-' + shard_id: {
                'task': 'ichnaea.data.tasks.update_cell',
                'schedule': timedelta(seconds=11),
                'kwargs': {'shard_id': shard_id},
                'options': {'expires': 15},
            }
        })

    for shard_id in DataMap.shards().keys():
        schedule.update({
            'update-datamap-' + shard_id: {
                'task': 'ichnaea.data.tasks.update_datamap',
                'schedule': timedelta(seconds=14),
                'kwargs': {'shard_id': shard_id},
                'options': {'expires': 20},
            },
        })

    for shard_id in WifiShard.shards().keys():
        schedule.update({
            'update-wifi-' + shard_id: {
                'task': 'ichnaea.data.tasks.update_wifi',
                'schedule': timedelta(seconds=10),
                'kwargs': {'shard_id': shard_id},
                'options': {'expires': 15},
            }
        })

    if 'assets' in sections and app_config.get('assets', 'bucket', None):
        # only configure tasks if target bucket is configured
        schedule.update({
            'cell-export-full': {
                'task': 'ichnaea.data.tasks.cell_export_full',
                'schedule': crontab(hour=0, minute=13),
                'options': {'expires': 39600},
            },
            'cell-export-diff': {
                'task': 'ichnaea.data.tasks.cell_export_diff',
                'schedule': crontab(minute=3),
                'options': {'expires': 2700},
            },
        })

    if 'import:ocid' in sections:
        schedule.update({
            'monitor-ocid-import': {
                'task': 'ichnaea.data.tasks.monitor_ocid_import',
                'schedule': timedelta(seconds=600),
                'options': {'expires': 570},
            },
            'cell-import-external': {
                'task': 'ichnaea.data.tasks.cell_import_external',
                'schedule': crontab(minute=52),
                'options': {'expires': 2700},
            },

        })

    return schedule
