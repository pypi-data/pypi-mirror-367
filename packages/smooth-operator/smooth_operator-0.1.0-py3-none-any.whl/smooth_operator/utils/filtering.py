# smooth_operator/utils/filtering.py
from typing import List, Optional, Callable
from ..core.site import Site


def filter_sites(
        sites: List[Site],
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        custom_filter: Optional[Callable[[Site], bool]] = None
) -> List[Site]:
    """
    Filter sites based on criteria.

    Args:
        sites: List of sites to filter
        include: Site names to include
        exclude: Site names to exclude
        tags: Tags that sites must have (any of these tags)
        custom_filter: Optional custom filter function

    Returns:
        Filtered list of sites
    """
    result = sites

    # Apply include filter
    if include:
        result = [site for site in result if site.name in include]

    # Apply exclude filter
    if exclude:
        result = [site for site in result if site.name not in exclude]

    # Apply tag filter
    if tags:
        result = [site for site in result
                  if any(tag in site.tags for tag in tags)]

    # Apply custom filter
    if custom_filter:
        result = [site for site in result if custom_filter(site)]

    return result