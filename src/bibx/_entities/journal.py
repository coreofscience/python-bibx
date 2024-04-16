from bisect import bisect_left
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Journal:
    title: str
    abbr: str
    issn: str
    classifications: Dict[int, str]

    def classification(self, year: int) -> Optional[str]:
        years = sorted(self.classifications.keys())
        if not years:
            return None
        if len(years) == 1:
            first = last = years[0]
        else:
            first, last = years[0], years[-1]
        if year < first:
            return None
        if year > last:
            return self.classifications[last]
        index = bisect_left(years, year)
        if years[index] != year:
            return self.classifications[years[index - 1]]
        return self.classifications[years[index]]
