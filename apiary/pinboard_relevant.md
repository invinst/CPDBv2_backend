## Pinboard relevant documents [/pinboards/{pinboard_id}/relevant-documents/{?offset,limit}]

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
            {
              "id": 1,
              "preview_image_url": "https://assets.documentcloud.org/CRID-1-CR-p1-normal.gif",
              "url": "http://cr-1-document.com/",
              "allegation": {
                  "crid": "1",
                  "category": "Operation/Personnel Violations",
                  "incident_date": "2002-02-21",
                  "coaccused": [{
                      "id": 1,
                      "rank": "Police Officer",
                      "full_name": "Jerome Finnigan",
                      "coaccusal_count": None,
                      "allegation_count": 10,
                      "percentile_trr": "99.9900",
                      "percentile_allegation": "88.8800",
                      "percentile_allegation_civilian": "77.7700",
                      "percentile_allegation_internal": "66.6600",
                  }]
                }
                "point": {"lon": 12.0, "lat": 21.0},
              }
            },
            {
              "preview_image_url": "http://via.placeholder.com/121x157",
              "url": "https://assets.documentcloud.org/documents/5680384/CRID-1083633-CR-CRID-1083633-CR-Tactical.pdf",
              "allegation": {
                "crid": "1079876",
                "category": "Operations/Personnel Violation",
                "incident_date": "2014-05-02",
                "coaccused": [{
                    "id": 1,
                    "rank": "Police Officer",
                    "full_name": "Jerome Finnigan",
                    "coaccusal_count": None,
                    "allegation_count": 10,
                    "percentile_trr": "99.9900",
                    "percentile_allegation": "88.8800",
                    "percentile_allegation_civilian": "77.7700",
                    "percentile_allegation_internal": "66.6600",
                }]
              }
            },
            ...
          ]
        }


## Pinboard relevant coaccusals [/pinboards/{pinboard_id}/relevant-coaccusals/{?offset,limit}]

### Get Pinboard relevant coaccusals list [GET]

+ Parameters
    + pinboard_id (number) - number ID of the pinboard
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
          "count": 100,
          "previous": "http://cpdp.co/pinboards/f871a13f/relevant-coaccusals/?",
          "next": "http://cpdp.co/pinboards/f871a13f/relevant-coaccusals/?limit=20&offset=40",
          "results": [{
              "id": 11,
              "full_name": "Jerome Finnigan",
              "date_of_appt": "2000-01-02",
              "date_of_resignation": "2010-02-03",
              "badge": "456",
              "gender": "Female",
              "to": "/officer/11/jerome-finnigan/",
              "birth_year": 1950,
              "race": "Black",
              "rank": "Police Officer",
              "unit": {
                  "id": 4,
                  "unit_name": "004",
                  "description": "District 004",
                  "long_unit_name": "Unit 004"
              },
              "percentile_trr": "11.1100",
              "percentile_allegation": "22.2200",
              "percentile_allegation_civilian": "33.3300",
              "percentile_allegation_internal": "44.4400",
              "allegation_count": 1,
              "civilian_compliment_count": 2,
              "sustained_count": 4,
              "discipline_count": 6,
              "trr_count": 7,
              "major_award_count": 8,
              "honorable_mention_count": 3,
              "honorable_mention_percentile": 88.88,
              "coaccusal_count": 5,
          }, {
              "id": 21,
              "full_name": "Ellis Skol",
              "date_of_appt": "2000-01-02",
              "date_of_resignation": "2010-02-03",
              "badge": "456",
              "gender": "Female",
              "to": "/officer/21/ellis-skol/",
              "birth_year": 1950,
              "race": "Black",
              "rank": "Senior Officer",
              "unit": {
                  "id": 4,
                  "unit_name": "004",
                  "description": "District 004",
                  "long_unit_name": "Unit 004"
              },
              "percentile_trr": "33.3300",
              "percentile_allegation": "44.4400",
              "percentile_allegation_civilian": "55.5500",
              "allegation_count": 1,
              "civilian_compliment_count": 2,
              "sustained_count": 4,
              "discipline_count": 6,
              "trr_count": 7,
              "major_award_count": 8,
              "honorable_mention_count": 3,
              "honorable_mention_percentile": 88.88,
              "coaccusal_count": 4,
            },
            ...
          ]
        }


## Pinboard relevant complaints [/pinboards/{pinboard_id}/relevant-complaints/{?offset,limit}]

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
          "results": [{
              'crid': '2',
              'address': '',
              'category': 'Unknown',
              'incident_date': '2002-02-22',
              'victims': [],
              'point': None,
              'to': '/complaint/2/',
              'sub_category': 'Unknown',
              'coaccused': [{
                  'id': 2,
                  'rank': 'Senior Officer',
                  'full_name': 'Ellis Skol',
                  'coaccusal_count': None,
                  'allegation_count': 1,
                  'percentile': {
                      'year': 2016,
                      'percentile_trr': '33.3300',
                      'percentile_allegation': '44.4400',
                      'percentile_allegation_civilian': '55.5500',
                  },
              }],
          }, {
              'crid': '1',
              'address': '',
              'category': 'Operation/Personnel Violations',
              'incident_date': '2002-02-21',
              'victims': [{
                  'gender': 'Male',
                  'race': 'Black',
                  'age': 35,
              }],
              'point': {'lon': 0.01, 'lat': 0.02},
              'to': '/complaint/1/',
              'sub_category': 'Subcategory',
              'coaccused': [{
                  'id': 99,
                  'rank': 'Detective',
                  'full_name': 'Edward May',
                  'coaccusal_count': None,
                  'allegation_count': 5,
                  'percentile': {
                      'year': 2016,
                  },
              }, {
                  'id': 1,
                  'rank': 'Police Officer',
                  'full_name': 'Jerome Finnigan',
                  'coaccusal_count': None,
                  'allegation_count': 2,
                  'percentile': {
                      'year': 2016,
                      'percentile_trr': '11.1100',
                      'percentile_allegation': '22.2200',
                      'percentile_allegation_civilian': '33.3300',
                      'percentile_allegation_internal': '44.4400',
                  },
              }],
            },
            ...
          ]
        }
