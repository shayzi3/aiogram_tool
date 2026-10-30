### v1.2.7
Move `middleware_data` from the `Resolver` class's `__init__` method into the individual methods; if you leave the passing of `middleware_data` at the `update.outer_middleware` level, the dependency will not be able to access data provided by subsequent middlewares.
