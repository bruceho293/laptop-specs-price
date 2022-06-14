from django.db.models import Func

# A SubString Regex Function to get the Capacity from the Component Name
class SubStrRegex(Func):
    function = 'REGEX_SUBSTR'
    template = "%(function)s(%(expressions)s)"

    def as_postgresql(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection,
            function='SUBSTRING',
            template="%(function)s(%(expressions)s)",
            **extra_context
        )

    # For MySQL Oracle
    def as_oracle(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection,
            function='REGEX_SUBSTR',
            template="%(function)s(%(expressions)s)",
            **extra_context
        )
        
    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection,
            function='REGEXP',
            template="%(function)s(%(expressions)s)",
            **extra_context
        )