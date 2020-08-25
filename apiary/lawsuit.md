## Lawsuit [/lawsuit/{case_no}/]

### Get Lawsuit [GET]

+ Parameters
    + case_no (string) - case number of lawsuit

+ Response 200 (application/json)
        {
          "case_no": "14-P-7092",
          "summary": "Around 9:45 p.m., officers responded to a call of a man breaking into cars at 41st Street.",
          "primary_cause": "EXCESSIVE FORCE/SERIOUS",
          "address": "4060 S. Pulaski Rd., Chicago IL",
          "location": "",
          "incident_date": "2014-10-20",
          "plaintiffs": [
            {
              "name": "Laquan McDonald"
            }
          ],
          "officers": [
            {
              "percentile_allegation": "93.4890",
              "percentile_trr": "94.2982",
              "percentile_allegation_civilian": "93.1732",
              "percentile_allegation_internal": "85.3249",
              "id": 29310,
              "full_name": "Jason Van Dyke",
              "allegation_count": 25,
              "sustained_count": 1,
              "birth_year": 1978,
              "race": "White",
              "gender": "Male",
              "rank": "Police Officer",
              "lawsuit_count": 1,
              "lawsuit_payment": "5000000.00"
            }
          ],
          "interactions": [],
          "services": [],
          "misconducts": [
            "Excessive force",
            "Shooting"
          ],
          "violences": [
            "Gun"
          ],
          "outcomes": [
            "Killed by officer"
          ],
          "payments": [
            {
              "payee": "PACIFIC LIFE & ANNUITY SERVICES, INC",
              "settlement": "916090.00"
            },
            {
              "payee": "LAW OFFICES OF JEFFREY J NESLUND/ESTATE OF LAQUAN MCDONALD",
              "settlement": "2386667.00"
            },
            {
              "payee": "BHG STRUCTURED SETTLEMENTS",
              "settlement": "800000.00"
            },
            {
              "payee": "BHG STRUCTURED SETTLEMENTS",
              "settlement": "897243.00"
            }
          ],
          "point": {
            "lon": -87.72404,
            "lat": 41.81842
          },
          "total_payments": {
            "total": "5000000.00",
            "total_settlement": "5000000.00",
            "total_legal_fees": "0.00"
          },
          "attachment": {
            "id": "101298",
            "title": "Case 14-P-7092",
            "file_type": "document",
            "url": "https://assets.documentcloud.org/documents/7035053/14-L-12559.pdf",
            "preview_image_url": "https://assets.documentcloud.org/documents/7035053/pages/14-L-12559-p1-normal.gif"
          }
        }
