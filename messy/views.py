""" 
Views for Messy.
"""

from django.http import HttpResponseRedirect, JsonResponse
from messy import stats_writer

def get_stats(request):
    """ 
    Gets the aggregate message stats.
    
    Note: This is the high-traffic view - notice how we don't hit
    the database from here.
    """
    stats_url = stats_writer.get_url()
    if not stats_url is None:
        return HttpResponseRedirect(stats_url) # forward to S3 data
    
    # Stats URL not properly seeded
    data = {
        'result':'error',
        'error':'Stats Not Ready'
    }
    return JsonResponse(data)

def write_message(request):
    """ 
    Writes the message.
    """
    try:
        data = request.POST if request.method == 'POST' else request.GET
        stats_writer.write_message(data['username'],data['city'],data['state'],data['message'])
        return JsonResponse({'response':'OK'})
    except KeyError as ke:
        return JsonResponse({'response':'ERROR','message':unicode(ke)})

