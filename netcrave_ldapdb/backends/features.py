"""Features module for netcrave_ldapdb backend."""

from django.db.backends.base.features import BaseDatabaseFeatures


class DatabaseFeatures(BaseDatabaseFeatures):
    """Database features specific to LDAP."""

    # Django ORM features that are supported
    can_use_chunked_reads = True
    can_release_savepoints = False
    connection_persists_old_columns = False
    requires_sql_for_aggregation = True
    supports_boolean_expr_in_select_clause = False
    supports_default_keyword_in_bulk_insert = False
    supports_expression_indexes = False
    supports_ignore_conflicts = False
    supports_json_field_null = False
    supports_json_field_contains = False
    supports_partially_nullable_unique_constraints = False
    supports_primitives_in_json_field = False
    supports_regex_backreferencing = False
    supports_select_intersection = False
    supports_select_related = False  # LDAP doesn't have JOINs
    supports_sequence_reset = False
    supports_savepoints = False
    supports_transactions = False
    supports_timezones = True
    supports_timesince = True
    supports_unsaved_relation = False

    # LDAP-specific limitations
    can_introspect_autofield = True
    can_introspect_big_integer_field = True
    can_introspect_decimal_field = True
    can_introspect_duration_field = True
    can_introspect_empty_char_field = True
    can_introspect_foreign_keys = False  # DN references, not real FKs
    can_introspect_ip_address_field = True
    can_introspect_positive_integer_field = True
    can_introspect_small_integer_field = True
    can_introspect_text_field = True

    has_bulk_insert = False
    has_select_for_update = False
    has_select_for_update_nowait = False
    has_select_for_update_of = False
    uses_savepoints = False
    can_return_columns_from_insert = False
    can_return_multiple_columns_from_insert = False
    can_return_rows_from_bulk_insert = False
