from django.http import HttpRequest
from django.db.models import QuerySet, CharField
from django.db.models.functions import Concat, Lower
from math import ceil

DEFAULT_PAGE_SIZE = 20
DEFAULT_PREVIEW_SIZE = 3
MAX_SEARCH_QUERY = 100

async def wrap_filters(
    request: HttpRequest, query: QuerySet, *,
    paginate: bool | int = False,
    preview: bool | int = False,
    queryable: str | list[str] = None,
):
    if queryable is not None:
        assert len(queryable) > 0
        param = request.GET.get('q', None)
        if param is not None and len(param) in range(1, MAX_SEARCH_QUERY + 1):
            expression = queryable
            if isinstance(queryable, list):
                if len(queryable) > 1:
                    expression = Concat(*queryable)
                else:
                    expression = queryable[0]
            
            query = (
                query
                    .annotate(_query = Lower(expression, output_field=CharField()))
                    .filter(_query__contains=param.lower().strip())
            )
    
    can_paginate = (
        paginate is not None 
        and (not isinstance(paginate, bool) or paginate)
    )
    has_preview = (
        preview is not None 
        and (not isinstance(preview, bool) or preview)
    )
    
    if can_paginate or has_preview:
        page = 1
        page_size = (DEFAULT_PREVIEW_SIZE if has_preview else DEFAULT_PAGE_SIZE)
        is_preview = (not has_preview or request.GET.get('preview') in ['true', 'yes', '1'])
        
        if is_preview and isinstance(preview, int):
            assert preview > 0
            page_size = preview
            
        elif can_paginate and not is_preview:
            if isinstance(paginate, int):
                assert paginate > 0
                page_size = paginate
            total_pages = ceil(await query.acount() / page_size)
            
            try:
                page = int(request.GET.get('p'))
                if page < 1:
                    page = 1
                elif page > total_pages:
                    page = total_pages
            except:
                pass
            
        query = query[(page - 1) * page_size: page * page_size]
    
    return query
