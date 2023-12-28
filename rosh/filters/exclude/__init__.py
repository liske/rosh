from rosh.filters.include import RoshIncludeFilter


class RoshExcludeFilter(RoshIncludeFilter):
    description = 'exclude items matching a regex'

    combine = all

    def match(self, item):
        return not super().match(item)

is_rosh_filter = True
rosh_filter = RoshExcludeFilter
