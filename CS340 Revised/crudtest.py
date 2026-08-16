from bson.objectid import ObjectId
from CRUD import AnimalShelter


db = AnimalShelter()

# CREATE
record_id = db.createRecord({
    "animal_id": "TEST001",
    "animal_type": "Dog",
    "breed": "Test Breed",
    "name": "Test Animal"
})

print("Created:", record_id)


# READ
record = db.getRecordId(record_id)

print("Read:", record)


# UPDATE
update_result = db.updateRecord(
    {"_id": ObjectId(record_id)},
    {"name": "Updated Test Animal"}
)

print("Updated:", update_result)


# READ UPDATED RECORD
updated_record = db.getRecordId(record_id)

print("Updated record:", updated_record)


# DELETE
delete_result = db.deleteRecord({
    "_id": ObjectId(record_id)
})

print("Deleted:", delete_result)


# CONFIRM DELETION
deleted_record = db.getRecordId(record_id)

print("Record after deletion:", deleted_record)
print("Indexes:", db.createIndexes())
print("Outcome summary:", db.getSummary())