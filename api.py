import flask
import logging

from flask import request, jsonify, abort
from craigslist import CraigslistForSale
from pprint import pprint

app = flask.Flask('craigslist-service')

QUERY_FILTERS = {
    'bundle_duplicates': True
}

def filter_result_fields(result):
    return {
        'datetime': result['datetime'],
        'last_updated': result['last_updated'],
        'url': result['url'],
        'price': result['price'],
        'name': result['name']
    }

@app.route('/', methods=['GET'])
def get_craigslist_query():
    '''
        Request body:
        - keywords: [string]
        - locations: [string]
    '''
    # get query arguments
    keywords = request.args.get('keywords', '').split(',')
    locations = request.args.get('locations', '').split(',')
    app.logger.info(f'Received request with keywords={keywords} locations={locations}')

    # validate request parameters
    if not keywords or not locations:
        app.logger.error('Empty keywords/locations')
        abort(400, 'Missing keywords and/or locations')

    # run query
    results = []
    for location in locations:
        for keyword in keywords:
            found_results = CraigslistForSale(site=location, filters={'query': keyword}) \
                                .get_results(sort_by='newest')
            results += list(found_results)

    # respond with results
    app.logger.info(f'Found {len(results)} results')

    results = list(map(lambda result: filter_result_fields(result), results))

    return jsonify(results)

app.run()
