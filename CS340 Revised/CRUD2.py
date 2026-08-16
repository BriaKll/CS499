from pymongo import MongoClient
from bson.objectid import ObjectId
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
    #Input data formatted as per the Pymongo API
    #Example: ({""name": "Rex", 'age_upon_outcome': '2 months'})
    def createRecord(self, data):
        if data:
            _insertValid = self.dataBase.animals.insert_one(data)
            #check the status of the inserted value 
            return True if _insertValid.acknowledged else False
	
        else:
            raise Exception("No document to save. Data is empty.")
    
    #todo implement the R
    #get documents by the GUID
    #This is more for a test but could be used after the createRecord
    #Since the document returned by insert_one contains the newly created _id
    def getRecordId(self, postId):
        _data = self.dataBase.find_one({'_id': ObjectId(postId)})
                                  
        return _data
    
    #Get records with criteria
    #All records are returned if criteria is None
    #Default is None
    #Example: ({""name": "Rex", 'age_upon_outcome': '2 months'})
    #do not return the _id
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
    def updateRecord(self, query, newValue):
        if not query:
            raise Exception("No search criteria is present.")
        elif not newValue:
            raise Exception("No update value is present.")
        else:
            _updateValid = self.dataBase.animals.update_many(query, {"$set": newValue})
            self.records_updated = _updateValid.modified_count
            self.records_matched = _updateValid.matched_count

            return True if _updateValid.modified_count > 0 else False
    
    #delete a record
    def deleteRecord(self, query):
        if not query:
            raise Exception("No search criteria is present.")
        
        else:
            _deleteValid = self.dataBase.animals.delete_many(query)
            self.records_deleted = _deleteValid.deleted_count

            return True if _deleteValid.deleted_count > 0 else False                   