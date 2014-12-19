from pyramid.httpexceptions import HTTPNotFound

from ichnaea.service.base import check_api_key
from ichnaea.service.error import (
    JSONParseError,
    preprocess_request,
)
from ichnaea.service.geolocate.views import NOT_FOUND
from ichnaea.service.geolocate.schema import GeoLocateSchema
from ichnaea.service.locate import (
    search_all_sources,
    map_data,
)

EMPTY_REQUEST = '{}'


def configure_country(config):
    config.add_route('v1_country', '/v1/country')
    config.add_view(country_view, route_name='v1_country', renderer='json')


# Disable API key checks and logging for this API, for the initial wave
# @check_api_key('country', error_on_invalidkey=False)
def country_view(request):
    if request.body == EMPTY_REQUEST:
        # Optimize common case of geoip-only request
        data = {}
    else:
        data, errors = preprocess_request(
            request,
            schema=GeoLocateSchema(),
            response=JSONParseError,
            accept_empty=True,
        )
        data = map_data(data)

    session = request.db_slave_session
    result = search_all_sources(
        session, 'country', data,
        client_addr=request.client_addr,
        geoip_db=request.registry.geoip_db,
        api_key_log=False,
        api_key_name=None,
        result_type='country')

    if not result:
        result = HTTPNotFound()
        result.content_type = 'application/json'
        result.body = NOT_FOUND
        return result

    return result