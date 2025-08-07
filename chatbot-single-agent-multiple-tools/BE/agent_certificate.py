import json
from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain.agents import tool

class CertificateOfEmploymentInput(BaseModel):
    employee_name: str = Field(description="The full name of the employee.")
    employee_id: Optional[str] = Field(None, description="The unique identifier for the employee.")
    destination_country: Optional[str] = Field(None, description="The country the employee is applying for a visa to.")

@tool(args_schema=CertificateOfEmploymentInput)
def generate_certificate_of_employment(data: Any) -> str:
    """
    Generate a Certificate of Employment for visa application.
    Accepts structured input or JSON string inside employee_name field.
    """

    name = None
    emp_id = None
    country = None

    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            name = parsed.get("employee_name")
            emp_id = parsed.get("employee_id")
            country = parsed.get("destination_country")
        except json.JSONDecodeError:
            return "Invalid input: not a valid JSON string."

    elif hasattr(data, "employee_name"):
        name = data.employee_name
        emp_id = data.employee_id
        country = data.destination_country

        if isinstance(name, str) and name.strip().startswith("{"):
            try:
                parsed = json.loads(name)
                name = parsed.get("employee_name", name)  # fallback to original
                emp_id = parsed.get("employee_id", emp_id)
                country = parsed.get("destination_country", country)
            except json.JSONDecodeError:
                return "Invalid JSON inside employee_name."

    else:
        return "Invalid input type. Must be structured object or JSON string."

    missing_fields = []
    if not name:
        missing_fields.append("employee_name")
    if not emp_id:
        missing_fields.append("employee_id")
    if not country:
        missing_fields.append("destination_country")

    if not missing_fields:
        return f"Certificate generated for {name} (ID: {emp_id}) to apply for visa to {country}."
    else:
        return f"Missing required fields: {', '.join(missing_fields)}."