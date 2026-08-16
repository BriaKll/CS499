from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone
import urllib.parse

#Example code found at w3schools.com/python/python_mongodb_fid.asp

class AnimalShelter(object):
    
    #property variables
    records_updated = 0 #keep a record of the records updated in an operation; CYA
    records_matched = 0 #keep a record of the records macthed in an operation; CYA
    records_deleted = 0 #keep a record of the records deleted in an operation; CYA

    #constructor to init the mongodb
    #to do: this should be a singleton
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.dataBase = self.client["AAC"]
       
    #Mehtod to create a record

    def createRecord(self, data):
        """Create one animal record."""

        if not isinstance(data, dict) or not data:
            raise ValueError("A non-empty record is required.")

        required_fields = [
            "animal_id",
            "animal_type",
            "breed"
        ]

        for field in required_fields:
            value = data.get(field)

            if value is None or str(value).strip() == "":
                raise ValueError(f"{field} is required.")

        result = self.dataBase.animals.insert_one(data)

        if not result.acknowledged:
            raise RuntimeError("The record could not be created.")

        auditRecord_id = str(result.inserted_id)

        self.logAction(
            "CREATE",
            {
                "record_id": auditRecord_id,
                "animal_id": data.get("animal_id")
            }
        )

        return auditRecord_id

    def getRecordId(self, record_id):
        """Return one animal record using its MongoDB ID."""

        if not record_id or not ObjectId.is_valid(record_id):
            raise ValueError("A valid record ID is required.")

        return self.dataBase.animals.find_one({
            "_id": ObjectId(record_id)
        })
    def getRecordCriteria(self, criteria=None):
        """Return only the fields required by the dashboard."""

        query = criteria or {}

        projection = {
            "_id": 0,
            "animal_id": 1,
            "name": 1,
            "animal_type": 1,
            "breed": 1,
            "color": 1,
            "sex_upon_outcome": 1,
            "age_upon_outcome": 1,
            "age_upon_outcome_in_weeks": 1,
            "outcome_type": 1,
            "outcome_subtype": 1,
            "datetime": 1,
            "location_lat": 1,
            "location_long": 1
        }

        return self.dataBase.animals.find(query, projection)
    
    #Update a record
    def updateRecord(self, query, new_values):

        if not isinstance(query, dict) or not query:
            raise ValueError("Search criteria are required.")

        if not isinstance(new_values, dict) or not new_values:
            raise ValueError("Update values are required.")

        result = self.dataBase.animals.update_many(
            query,
            {"$set": new_values}
        )
        self.logAction(
            "UPDATE",
            {
                "query": query,
                "new_values": new_values,
                "matched": result.matched_count,
                "updated": result.modified_count
            }
        )

        return {
            "matched": result.matched_count,
            "updated": result.modified_count
        }
    #delete a record
    def deleteRecord(self, query):
        """Delete animal records that match the query."""

        if not isinstance(query, dict) or not query:
            raise ValueError("Search criteria are required.")

        result = self.dataBase.animals.delete_many(query)

        self.logAction(
            "DELETE",
            {
                "query": query,
                "deleted": result.deleted_count
            }
        )

        return {
            "deleted": result.deleted_count
        }

    def logAction(self, action, details):
        """Record a database action in log."""

        log_entry = {
            "action": action,
            "details": details,
            "timestamp": datetime.now(timezone.utc)
        }

        self.dataBase.audit_log.insert_one(log_entry)

    def createIndexes(self):
        """Create indexes for fields frequently used by dashboard filters."""

        animals = self.dataBase.animals

        return {
            "animal_type": animals.create_index("animal_type"),
            "breed": animals.create_index("breed"),
            "sex": animals.create_index("sex_upon_outcome"),
            "outcome": animals.create_index("outcome_type"),
            "age": animals.create_index("age_upon_outcome_in_weeks")
        }

    def getSummary(self):

        pipeline = [
            {
                "$match": {
                    "outcome_type": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$outcome_type", "count": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "count": -1
                }
            },
            {
                "$project": {
                    "_id": 0, "outcome_type": "$_id", "count": 1
                }
            }
        ]

        return list(self.dataBase.animals.aggregate(pipeline))