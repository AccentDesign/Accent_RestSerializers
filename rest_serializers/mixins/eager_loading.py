class EagerLoadingMixin:
    SELECT_RELATED_FIELDS = []
    PREFETCH_RELATED_FIELDS = []

    @classmethod
    def setup_eager_loading(cls, queryset):
        if cls.SELECT_RELATED_FIELDS:
            queryset = queryset.select_related(*cls.SELECT_RELATED_FIELDS)
        if cls.PREFETCH_RELATED_FIELDS:
            queryset = queryset.prefetch_related(*cls.PREFETCH_RELATED_FIELDS)
        return queryset
