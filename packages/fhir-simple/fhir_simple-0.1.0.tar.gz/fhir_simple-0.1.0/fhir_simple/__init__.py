def fhir_patient_to_simple_json(fhir_obj):
    """
    Extracts key patient info from a FHIR Patient resource dict and returns a simplified dict.
    Args:
        fhir_obj (dict): FHIR Patient resource as a dict.
    Returns:
        dict: Simplified patient info.
    """
    try:
        result = {
            "fhirId": fhir_obj.get("id"),
            "active": fhir_obj.get("active"),
            "firstName": None,
            "lastName": None,
            "gender": fhir_obj.get("gender"),
            "birthDate": fhir_obj.get("birthDate"),
        }
        # Extract first name and last name from the first name entry
        names = fhir_obj.get("name", [])
        if names and isinstance(names, list):
            first_name_entry = names[0]
            given = first_name_entry.get("given", [])
            if given and isinstance(given, list):
                result["firstName"] = given[0]
            result["lastName"] = first_name_entry.get("family")
        return result
    except Exception as e:
        raise ValueError(f"Invalid FHIR Patient object: {e}")
