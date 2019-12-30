## Pinboard mobile relevant documents [/mobile/pinboards/{pinboard_id}/relevant-documents/{?offset,limit}]

### Get Pinboard relevant documents list [GET]

+ Parameters
    + pinboard_id (number) - number ID of the pinboard
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
          "count": 100,
          "previous": "http://cpdp.co/pinboards/f871a13f/relevant-documents/?",
          "next": "http://cpdp.co/pinboards/f871a13f/relevant-documents/?limit=20&offset=40",
          "results": [
            'id': 2,
            'preview_image_url': "https://assets.documentcloud.org/CRID-2-CR-p1-normal.gif",
            'url': 'http://cr-2-document.com/',
            'allegation': {
              'crid': '2',
              'category': 'Unknown',
              'incident_date': '2002-02-22',
              'officers': [
                {
                  'id': 4,
                  'rank': 'Senior Police Officer',
                  'full_name': 'Raymond Piwinicki',
                  'coaccusal_count': None,
                  'percentile': {
                      'year': 2016,
                  }
                },
                {
                  'id': 2,
                  'rank': 'Detective',
                  'full_name': 'Edward May',
                  'coaccusal_count': None,
                  'percentile': {
                      'year': 2016,
                      'percentile_trr': '11.1100',
                      'percentile_allegation': '22.2200',
                      'percentile_allegation_civilian': '33.3300',
                      'percentile_allegation_internal': '44.4400',

                  }
                },
              ]
            }
          }, {
            'id': 1,
            'preview_image_url': "https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
            'url': 'http://cr-1-document.com/',
            'allegation': {
              'crid': '1',
              'category': 'Operation/Personnel Violations',
              'incident_date': '2002-02-21',
              'officers': [{
                'id': 1,
                'rank': 'Police Officer',
                'full_name': 'Jerome Finnigan',
                'coaccusal_count': None,
                'percentile': {
                    'year': 2016,
                    'percentile_trr': '99.9900',
                    'percentile_allegation': '88.8800',
                    'percentile_allegation_civilian': '77.7700',
                    'percentile_allegation_internal': '66.6600',
                }
              }]
            },
            ...
          ]
        }


## Pinboard mobile relevant coaccusals [/mobile/pinboards/{pinboard_id}/relevant-coaccusals/{?offset,limit}]

### Get Pinboard relevant coaccusals list [GET]

+ Parameters
    + pinboard_id (number) - number ID of the pinboard
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

            {
              'id': 11,
              'rank': 'Police Officer',
              'full_name': 'Jerome Finnigan',
              'coaccusal_count': 5,
              'percentile': {
                'year': 2016,
                'percentile_trr': '11.1100',
                'percentile_allegation': '22.2200',
                'percentile_allegation_civilian': '33.3300',
                'percentile_allegation_internal': '44.4400',
              },
            }, {
              'id': 21,
              'rank': 'Senior Officer',
              'full_name': 'Ellis Skol',
              'coaccusal_count': 4,
              'percentile': {
                'year': 2016,
                'percentile_trr': '33.3300',
                'percentile_allegation': '44.4400',
                'percentile_allegation_civilian': '55.5500',
              },
            },
            ...
          ]
        }


## Pinboard mobile relevant complaints [/mobile/pinboards/{pinboard_id}/relevant-complaints/{?offset,limit}]

### Get Pinboard relevant complaints list [GET]

+ Parameters
    + pinboard_id (number) - number ID of the pinboard
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
          "count": 100,
          "previous": "http://cpdp.co/pinboards/f871a13f/relevant-complaints/?",
          "next": "http://cpdp.co/pinboards/f871a13f/relevant-complaints/?limit=20&offset=40",
          "results": [
            {
              'crid': '2',
              'category': 'Unknown',
              'incident_date': '2002-02-22',
              'officers': [{
                'id': 2,
                'rank': 'Senior Officer',
                'full_name': 'Ellis Skol',
                'coaccusal_count': None,
                'percentile': {
                    'year': 2016,
                    'percentile_trr': '33.3300',
                    'percentile_allegation': '44.4400',
                    'percentile_allegation_civilian': '55.5500',
                },
              }],
              'point': None,
            }, {
              'crid': '1',
              'category': 'Operation/Personnel Violations',
              'incident_date': '2002-02-21',
              'officers': [{
                'id': 99,
                'rank': 'Detective',
                'full_name': 'Edward May',
                'coaccusal_count': None,
                'percentile': {
                    'year': 2016,
                },
              }, {
                'id': 1,
                'rank': 'Police Officer',
                'full_name': 'Jerome Finnigan',
                'coaccusal_count': None,
                'percentile': {
                    'year': 2016,
                    'percentile_trr': '11.1100',
                    'percentile_allegation': '22.2200',
                    'percentile_allegation_civilian': '33.3300',
                    'percentile_allegation_internal': '44.4400',
                },
              }],
              'point': {'lon': 0.01, 'lat': 0.02},
            },
            ...
          ]
        }
