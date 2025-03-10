from .scheduler_factory import SchedulerFactory
from .searcher_factory import SearcherFactory


MIN = 'min'
MAX = 'max'

SEARCHER_PRESETS = SearcherFactory.searcher_presets
SCHEDULER_PRESETS = SchedulerFactory.scheduler_presets

RAY_BACKEND = 'ray'
CUSTOM_BACKEND = 'custom'
VALID_BACKEND = [RAY_BACKEND, CUSTOM_BACKEND]
