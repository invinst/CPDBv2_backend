## CR [/cr/{crid}/]

### Get CR [GET]

+ Parameters
    + crid (number) - number ID of Allegation

+ Response 200 (application/json)

        {
            "crid": "12345",
            'most_common_category': {
                'category': 'Operation/Personnel Violations',
                'allegation_name': 'NEGLECT OF DUTY/CONDUCT UNBECOMING - ON DUTY'
            },
            "coaccused": [
                {
                    "id": 123,
                    "full_name": "Robert O'Niell",
                    "gender": "Male",
                    "race": "White",
                    "birth_year": 1975,
                    "complaint_count": 43,
                    "sustained_count": 1,
                    "final_outcome": "Reprimand",
                    "final_finding": "Sustained",
                    "recommended_outcome": "10 Day Suspension",
                    "category": "Operation/Personnel Violations",
                    "complaint_percentile": 99.861,
                    "percentile": {
                        "percentile_allegation": "99.8610",
                        "percentile_allegation_civilian": "99.8810",
                        "percentile_allegation_internal": "80.5690",
                        "percentile_trr": "92.1100",
                        "id": 123,
                        "year": 2016
                    }
                },
                {
                    "id": 456,
                    "full_name": "Alex Foo",
                    "gender": "Male",
                    "race": "Black",
                    "birth_year": 1980,
                    "complaint_count": 23,
                    "sustained_count": 0,
                    "final_outcome": "Unknown",
                    "final_finding": "Sustained",
                    "category": "Operation/Personnel Violations",
                    "complaint_percentile": 99.861,
                    "percentile": {
                        "percentile_allegation": "99.8610",
                        "percentile_allegation_civilian": "99.8810",
                        "percentile_allegation_internal": "80.5690",
                        "percentile_trr": "92.1100",
                        "id": 456,
                        "year": 2016
                    }
                }
            ],
            "complainants": [
                {
                    "race": "White",
                    "gender": "Male",
                    "age": 18
                },
                {
                    "race": "Black",
                    "gender": "Female",
                    "age": 20
                }
            ],
            "victims": [
                {
                    "race": "Black",
                    "gender": "Male",
                    "age": 53
                },
                {
                    "race": "Black",
                    "gender": "Female",
                    "age": 20
                }
            ],
            "summary": "Lorem ipsum dolor.",
            "point": {
                "lon": -87.664606,
                "lat": 41.68731
            },
            "incident_date": "2002-02-28",
            "start_date": "2002-02-30",
            "end_date": "2002-04-21",
            "address": "3510 Michigan Ave, Chicago, IL 60653",
            "location": "Police Building",
            "beat": "23",
            "involvements": [
                {
                    "officer_id": 1,
                    "involved_type": "investigator",
                    "full_name": "Lauren Skol",
                    "badge": "CPD",
                    "percentile_allegation_civilian": 99.881,
                    "percentile_allegation_internal": 80.569,
                    "percentile_trr": 92.110
                },
                {
                    "officer_id": 2,
                    "involved_type": "police_witness",
                    "full_name": "Raymond Piwinicki",
                    "allegation_count": 10,
                    "sustained_count": 3,
                    "percentile_allegation_civilian": 99.881,
                    "percentile_allegation_internal": 80.569,
                    "percentile_trr": 92.110
                },
                {
                    "officer_id": 3,
                    "involved_type": "police_witness",
                    "full_name": "German Felix",
                    "allegation_count": 10,
                    "sustained_count": 3,
                    "percentile_allegation_civilian": 99.881,
                    "percentile_allegation_internal": 80.569,
                    "percentile_trr": 92.110
                }
            ],
            "attachments": [
                {
                    "title": "CHI - R-00001275 Red",
                    "file_type": "video",
                    "url": "http://foo.com",
                    "preview_image_url": "http://foo.com/bar.jpg"
                },
                {
                    "title": "CHI - R-00001275 Red",
                    "file_type": "audio",
                    "url": "http://foo.com",
                    "preview_image_url": "http://foo.com/bar.jpg"
                },
                {
                    "title": "CHI - R-00001275 Red",
                    "file_type": "document",
                    "url": "http://foo.com",
                    "preview_image_url": "http://foo.com/bar.jpg"
                }
            ]
        }
