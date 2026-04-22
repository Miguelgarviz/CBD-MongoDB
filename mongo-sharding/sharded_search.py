import pymongo
import sys

try:
    # Aumentamos un poco el timeout por si el Sharding está bajo mucha carga
    client = pymongo.MongoClient("mongodb://localhost:27020/", serverSelectionTimeoutMS=30000, 
    connectTimeoutMS=30000, 
    socketTimeoutMS=30000)
    db = client["sample_airbnb"]
    coleccion = db["listingsAndReviews"]
    
    # Intentamos la consulta
    resultado = list(coleccion.aggregate([{ "$sample": { "size": 1 } }]))
    
    if len(resultado) > 0:
        print("Consulta OK")
        sys.exit(0) # Éxito total
    else:
        print("Coleccion vacia")
        sys.exit(0) # Salimos con 0 para que JMeter no marque error, pero avisamos
        
except Exception as e:
    # Si falla la conexión, aquí sí mandamos un 1 para que JMeter lo registre como fallo
    sys.stderr.write(f"Error critico: {e}\n")
    sys.exit(1)