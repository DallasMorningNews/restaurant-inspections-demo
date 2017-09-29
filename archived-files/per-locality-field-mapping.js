{  // Dallas.
  "establishment_name": "",  // establishment_name
  "address": "",  // address
  "city": "",  // city
  "zip": "",  // zip

  "inspections": [  // inspections
    {
      "type": "",
      "date": "",
      "raw_score": "",

      "violations": [  // violations
        {
          "points": "", // points_deducted
          "memo": "", // inspector_comment
          "text": "", // statute_citation
          "description": "" // infraction_category
        }
      ]
    }
  ]
}


{  // Plano.
  "establishment_name": "", // establishment_name
  "restaurantID": "",  // source_id
  "address": "", // address
  "city": "", // city
  "currentInspectedDate": "", // to be removed.
  "currentInspectedGrade": "", // to be removed.

  "restaurantHistoryList": {  // inspections
    "name": "",  // to be removed.
    "date": "",  // date (needs conversion)
    "grade": "",  // raw_score

    "violationList": {  // violations
      "severity": "", // severity
      "description": "", // infraction_category
      "comment": "", // inspector_comment
    }
  }
}


{  // Carrollton.
  "establishment_name": "",  // establishment_name
  "street_address": "",  // address
  "city": "",  // city

  "inspections": [  // inspections
    {
      "date": "",  // date
      "score": "",  // raw_score

      "violations": [  // violations
        {
          "points_deducted": "",  // points_deducted
          "rule_violated": "",  // infraction_category
          "corrective_action": "",  // inspector_comment
          "corrected_during_inspection": "",  // corrected_during_inspection
          "extra_information": "",  // extra_information
        }
      ]
    }
  ]
}


{  // Tarrant County.
  "name": "",  // establishment_name
  "address": "",  // address
  "city": "",  // city
  "zip": "",  // zip_code

  "inspections": [  // inspections
    {
      "date": "", // date
      "demerits": "", // raw_score
      "tag": "", // area
      "type": "",  // type

      "violations": [  // violations
        {
          "violation_name": "",  // infraction_category
          "violation_points": "",  // points_deducted
          "violation_description": "",  // inspector_comment
          "violation_count": "",  // violation_count
        }
      ]
    }
  ]
}


{
  "establishment_name": "",  // string (*****)
  "source_id": "",  // integer ( *   )
  "address": "",  //  string (*****)
  "city": "",  //  string (*****)
  "zip_code": "",  //  string (*  **)

  "inspections": [  // array of objects (*****)
    {
      "area": "",  // string (   **)
      "date": "",  // string of ISO date (*****)
      "type": "",  // string (*  **)
      "raw_score": "",  // string (*****)

      "violations": [  // array of objects (*****)
        {
          "points_deducted": 0,  // integer (* ***)
          "statute_citation": "",  // string (*   *)
          "infraction_category": "",  // string (*****)
          "inspector_comment": "",  // string (*****)
          "severity": "",  // string ( *   )
          "corrected_during_inspection": false,  // bool (  *  )
          "additional_information": "",  // string (  *  )
          "violation_count": 0  // integer (   * )
        }
      ]
    }
  ]
}


{  // Fort Worth.
  "establishment_name": "",  // establishment_name
  "address": "",  // address
  "city": "",  // city
  "zip": "",  // zip

  "inspections": [  // inspections
    {
      "area_name": "",  // area
      "date": "",  // date
      "inspection_type": "",  // type
      "demerits": "",  // raw_score

      "violations": [  // violations
        {
          "code": "",  // statute_citation
          "specific_infraction": "",  // infraction_category
          "demerits": "",  // points_deducted
          "description": "",  // inspector_comment
        }
      ]
    }
  ]
}
