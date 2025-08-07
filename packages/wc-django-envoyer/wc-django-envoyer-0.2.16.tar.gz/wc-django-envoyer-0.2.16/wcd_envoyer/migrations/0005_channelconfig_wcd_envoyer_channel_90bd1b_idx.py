from functools import lru_cache, partial
from typing import *

from unittest import mock
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.operations.base import Operation
from django.contrib.postgres.operations import AddIndexConcurrently
from django.db.migrations.state import ProjectState


class SwitchOperations(Operation):
    serialization_expand_args = ["operations"]

    def __init__(self, operations: Dict[Optional[Callable], List[Operation]]):
        self.operations = operations

    def deconstruct(self):
        kwargs = {}
        kwargs["operations"] = self.operations
        return (self.__class__.__qualname__, [], kwargs)

    def get_operations(self, app_label, schema_editor, from_state, to_state):
        for checker, operations in self.operations.items():
            if checker is not None and checker(
                app_label=app_label,
                schema_editor=schema_editor,
                from_state=from_state,
                to_state=to_state,
            ):
                return operations

        return self.operations.get(None, [])

    def state_forwards(self, app_label: str, state: ProjectState) -> None:
        for operation in self.get_operations(app_label, None, None, state):
            operation.state_forwards(app_label, state)

    def database_forwards(self, app_label: str, schema_editor: BaseDatabaseSchemaEditor, from_state: ProjectState, to_state: ProjectState) -> None:
        for operation in self.get_operations(app_label, schema_editor, from_state, to_state):
            to_state = from_state.clone()
            operation.state_forwards(app_label, to_state)
            operation.database_forwards(
                app_label, schema_editor, from_state, to_state,
            )
            from_state = to_state

    def database_backwards(self, app_label: str, schema_editor: BaseDatabaseSchemaEditor, from_state: ProjectState, to_state: ProjectState) -> None:
        operations = self.get_operations(app_label, schema_editor, from_state, to_state)
        # We calculate state separately in here since our state functions aren't useful
        to_states = {}
        for dbop in operations:
            to_states[dbop] = to_state
            to_state = to_state.clone()
            dbop.state_forwards(app_label, to_state)

        # to_state now has the states of all the database_operations applied
        # which is the from_state for the backwards migration of the last
        # operation.
        for database_operation in reversed(operations):
            from_state = to_state
            to_state = to_states[database_operation]
            database_operation.database_backwards(
                app_label, schema_editor, from_state, to_state
            )

    def describe(self):
        return "Operations might be applied with a different logic inside based on some condition"


test_index = models.Index(fields=['some'], name='other')


@lru_cache
def get_tmp_model():
    with mock.patch('django.apps.registry.Apps.register_model'):
        class TMPModel(models.Model):
            some = models.CharField(max_length=255)

    # TMPModel._meta.apps.register_model(TMPModel._meta.app_label, TMPModel)

    return TMPModel


def supports_concurrent_index_creation(app_label, schema_editor, from_state, to_state):
    if schema_editor is None:
        return False

    try:
        with mock.patch.object(schema_editor, 'execute'):
            schema_editor.add_index(get_tmp_model(), test_index, concurrently=True)

            return True
    except (TypeError, ValueError):
        return False


class AddIndexConcurrentlyIfNotExists(AddIndexConcurrently):
    def transform_sql(self, creator, *args, **kwargs):
        sql = creator(*args, **kwargs)

        if 'IF NOT EXISTS' in sql.template:
            return sql

        sql.template = sql.template.replace(
            'CREATE INDEX CONCURRENTLY',
            'CREATE INDEX CONCURRENTLY IF NOT EXISTS',
        )

        return sql

    def database_forwards(self, app_label: str, schema_editor: BaseDatabaseSchemaEditor, from_state: ProjectState, to_state: ProjectState) -> None:
        create_sql = partial(self.transform_sql, self.index.create_sql)

        with mock.patch.object(self.index, 'create_sql', create_sql):
            super().database_forwards(app_label, schema_editor, from_state, to_state)


INDEXES = [
    dict(
        model_name='channelconfig',
        index=models.Index(fields=['channel'], name='wcd_envoyer_channel_90bd1b_idx'),
    ),
    dict(
        model_name='channelconfig',
        index=models.Index(fields=['is_active'], name='wcd_envoyer_is_acti_c45179_idx'),
    ),
    dict(
        model_name='channelconfig',
        index=models.Index(fields=['-created_at'], name='wcd_envoyer_created_f7d8df_idx'),
    ),
    dict(
        model_name='channelconfig',
        index=models.Index(fields=['-updated_at'], name='wcd_envoyer_updated_1d647c_idx'),
    ),
    dict(
        model_name='message',
        index=models.Index(fields=['status'], name='wcd_envoyer_status_c3c21f_idx'),
    ),
    dict(
        model_name='message',
        index=models.Index(fields=['channel', 'event'], name='wcd_envoyer_channel_168aec_idx'),
    ),
    dict(
        model_name='message',
        index=models.Index(fields=['-created_at'], name='wcd_envoyer_created_51dbbe_idx'),
    ),
    dict(
        model_name='message',
        index=models.Index(fields=['-updated_at'], name='wcd_envoyer_updated_3f6bf7_idx'),
    ),
    dict(
        model_name='template',
        index=models.Index(fields=['channel', 'event'], name='wcd_envoyer_channel_b10879_idx'),
    ),
    dict(
        model_name='template',
        index=models.Index(fields=['is_active'], name='wcd_envoyer_is_acti_477ed6_idx'),
    ),
    dict(
        model_name='template',
        index=models.Index(fields=['-created_at'], name='wcd_envoyer_created_60fee9_idx'),
    ),
    dict(
        model_name='template',
        index=models.Index(fields=['-updated_at'], name='wcd_envoyer_updated_421505_idx'),
    ),
]


class Migration(migrations.Migration):

    atomic = False
    dependencies = [
        ('wcd_envoyer', '0004_channelconfig_is_active'),
    ]

    operations = [
        SwitchOperations(
            {
                supports_concurrent_index_creation: [
                    AddIndexConcurrentlyIfNotExists(**x),
                ],
                None: [migrations.AddIndex(**x)],
            }
        )
        for x in INDEXES
    ]
