from fastapi import APIRouter, HTTPException
from models.student import Student, Address  # Assuming these are your Pydantic models
from config.database import collection_name  # MongoDB collection
from schema.schema import list_serial, individual_serial  # Serialization functions
from bson import ObjectId  # ObjectId conversion

router = APIRouter()











# Define the root endpoint for checking API health or returning a message
@router.get("/")
def read_root():
    return {"message": "Welcome to the Student API!"}









# Endpoint to get all students (with optional filters)
@router.get("/students", response_model=list[Student])  # You can modify response model as needed
def get_students(country: str = None, age: int = None):
    """
    Fetch students with optional filtering by country and age.
    """
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    
    students = collection_name.find(query)  # MongoDB query

    if not students:
        raise HTTPException(status_code=404, detail="No students found")
    
    # Serializing the list of students
    return list_serial(students)









# Endpoint to get a single student by ID
@router.get("/students/{id}", response_model=Student)
def get_student(id: str):
    """
    Fetch a single student by their ID.
    """
    # Convert the string ID to an ObjectId for MongoDB lookup
    try:
        student = collection_name.find_one({"_id": ObjectId(id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Serializing the individual student
    return individual_serial(student)










# POST: Create a new student
@router.post("/students", response_model=Student)
def create_student(student: Student):
    """
    Create a new student in the database.
    """
    # Convert Pydantic model to dictionary, ensuring nested models are serialized
    student_data = student.dict(by_alias=True, exclude_unset=True)  

    # Insert student data into MongoDB
    result = collection_name.insert_one(student_data)

    # Add the MongoDB generated ID to the student data
    student_data["id"] = str(result.inserted_id)

    return student_data  # Return the created student with the ID






import logging



from fastapi import HTTPException
from bson import ObjectId
import logging

# Helper function to serialize MongoDB documents
def individual_serial1(student):
    """
    Helper function to serialize the student document.
    """
    if "_id" in student:
        student["id"] = str(student.pop("_id"))
    return student

@router.patch("/students/{id}", response_model=Student)
def update_student(id: str, student: Student):
    """
    Update a student's details by ID while preserving existing data for unset fields.
    """
    # Convert string ID to ObjectId
    try:
        student_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    
    # Fetch the existing student from the database
    existing_student = collection_name.find_one({"_id": student_id})
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Convert Pydantic model to dictionary and filter only provided fields
    update_data = student.dict(exclude_unset=True)

    # Manually merge the address field (or any other nested field) to preserve existing values
    if "address" in update_data:
        # If address is partially provided, merge it with existing address data
        existing_address = existing_student.get("address", {})
        update_data["address"] = {**existing_address, **update_data["address"]}

    # Perform the update in MongoDB
    updated_student = collection_name.find_one_and_update(
        {"_id": student_id},
        {"$set": update_data},  # Update fields
        return_document=True
    )

    # If no student found, return 404
    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Serialize and return the updated student
    return individual_serial1(updated_student)
    """
    Update a student's details by ID.
    """
    logging.debug(f"PATCH request for student with ID: {id}")
    logging.debug(f"Incoming data for update: {student.dict()}")

    # Convert string ID to ObjectId
    try:
        student_id = ObjectId(id)
    except Exception:
        logging.error("Invalid ObjectId format")
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    # Extract fields to update
    update_data = student.dict(exclude_unset=True)
    logging.debug(f"Extracted update data: {update_data}")

    if not update_data:
        logging.warning("No fields provided for update")
        raise HTTPException(status_code=400, detail="No fields to update")

    # Update the student in MongoDB
    updated_student = collection_name.find_one_and_update(
        {"_id": student_id},
        {"$set": update_data},
        return_document=True
    )

    if not updated_student:
        logging.error(f"No student found with ID: {id}")
        raise HTTPException(status_code=404, detail="Student not found")

    logging.debug(f"Document after update: {updated_student}")

    # Serialize and return the updated document
    serialized_student = individual_serial1(updated_student)
    logging.debug(f"Serialized student: {serialized_student}")
    return serialized_student









# DELETE: Delete a student by ID
@router.delete("/students/{id}", response_model=Student)
def delete_student(id: str):
    """
    Delete a student from the database by ID.
    """
    try:
        student_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    # Try to delete the student
    deleted_student = collection_name.find_one_and_delete({"_id": student_id})

    if not deleted_student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Serializing the deleted student
    return individual_serial(deleted_student)