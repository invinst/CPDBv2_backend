## Social graph network data [/social-graph/network/{?officer_ids,unit_id,pinboard_id,complaint_origin,threshold}]

### Get Pinboard relevant complaints list [GET]

+ Parameters
    + We only need to pass one of these parameters:
      + officer_ids (string) - a comma separated list of number ID of the officers
      + unit_id (number) - number ID of the unit
      + pinboard_id (number) - number ID of the pinboard
    + complaint_origin (string, optional) - type of complaint
      + Accepted values: `CIVILIAN`, `OFFICER`, `ALL`
      + Default: `CIVILIAN`
    + threshold (number, optional) - the minimum number of coaccusals officer
      + Accepted values: `1` -> `4`
      + Default: `2`


+ Response 200 (application/json)

        {
          "pinboard_id": "f871a13f",
          "coaccused_data": [
            {
              "officer_id_1": 3663,
              "officer_id_2": 4881,
              "incident_date": "1994-05-24",
              "accussed_count": 2
            },
            {
              "officer_id_1": 3663,
              "officer_id_2": 31945,
              "incident_date": "1998-11-09",
              "accussed_count": 2
            },
            {
              "officer_id_1": 3663,
              "officer_id_2": 31945,
              "incident_date": "1998-12-03",
              "accussed_count": 3
            },
            {
              "officer_id_1": 30209,
              "officer_id_2": 31945,
              "incident_date": "1998-12-03",
              "accussed_count": 2
            },
            {
              "officer_id_1": 3663,
              "officer_id_2": 30209,
              "incident_date": "1998-12-03",
              "accussed_count": 2
            },
            {
              "officer_id_1": 4881,
              "officer_id_2": 31945,
              "incident_date": "2000-04-28",
              "accussed_count": 2
            },
            {
              "officer_id_1": 3663,
              "officer_id_2": 31945,
              "incident_date": "2002-09-28",
              "accussed_count": 4
            },
            {
              "officer_id_1": 3663,
              "officer_id_2": 31945,
              "incident_date": "2002-10-13",
              "accussed_count": 5
            }
          ],
          "officers": [
            {
              "id": 30209,
              "full_name": "Bennie Watson",
              "percentile": {
                "percentile_trr": "0.0000",
                "percentile_allegation_civilian": "35.4196",
                "percentile_allegation_internal": "83.0449"
              }
            },
            {
              "id": 3663,
              "full_name": "Donnell Calhoun",
              "percentile": {
                "percentile_allegation_civilian": "87.4780",
                "percentile_allegation_internal": "96.5164"
              }
            },
            {
              "id": 4881,
              "full_name": "Gilbert Cobb",
              "percentile": {
                "percentile_trr": "0.0000",
                "percentile_allegation_civilian": "85.1838",
                "percentile_allegation_internal": "0.0000"
              }
            },
            {
              "id": 31945,
              "full_name": "Melvin Ector",
              "percentile": {
                "percentile_trr": "0.0000",
                "percentile_allegation_civilian": "94.1100",
                "percentile_allegation_internal": "61.1521"
              }
            }
          ],
          "list_event": [
            "1994-05-24",
            "1998-11-09",
            "1998-12-03",
            "2000-04-28",
            "2002-09-28",
            "2002-10-13"
          ]
        }
