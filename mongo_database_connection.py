from pymongo import MongoClient
import motor.motor_asyncio
import keys
def get_database():
 
   CONNECTION_STRING = keys.connection_string
 
   client =  motor.motor_asyncio.AsyncIOMotorClient(CONNECTION_STRING)
 
   return client['bongbotdatabase']


if __name__ == "__main__":
   bongbotdatabase = get_database()
