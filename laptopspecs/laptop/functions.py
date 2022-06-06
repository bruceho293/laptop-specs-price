from django.db.models import Func

# A SubString Regex Function to get the Capacity from the Component Name
class SubStrRegex(Func):
    function = 'REGEx_SUBSTR'
    template = "%(function)s(%(expressions)s)"

    def as_postgresql(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection,
            function='SUBSTRING',
            template="%(function)s(%(expressions)s)",
            **extra_context
        )