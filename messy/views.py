""" 
Views for Messy.
"""

from django.http import HttpResponseRedirect, JsonResponse
from messy.stats_writer import get_url

def get_stats(request):
    """ 
    Gets the aggregate message stats.
    
    Note: This is the high-traffic view - notice how we don't hit
    the database from here.
    """
    stats_url = get_url()
    if not stats_url is None:
        return HttpResponseRedirect(stats_url) # forward to S3 data
    
    # Stats URL not properly seeded
    data = {
        'result':'error',
        'error':'Stats Not Ready'
    }
    return JsonResponse(data)
