from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient

uri= "mongodb+srv://aryan:aryan123@cluster0.o8yki.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)


db=client.student_db
collection_name=db["student_collection"]