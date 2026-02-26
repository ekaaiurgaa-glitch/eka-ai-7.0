import asyncio
from app.db.session import AsyncSessionLocal
from app.modules.knowledge.service import ingest_document

KNOWLEDGE_DATA = [
    {
        "title": "Brake System Diagnosis - Maruti Swift",
        "content": "If a grinding noise is heard when braking, it usually indicates worn out brake pads. Inspect pads immediately. Minimum thickness should be 2mm. If lower, replace pads and inspect rotors for scoring.",
        "url": "https://manual.eka.ai/swift/brakes"
    },
    {
        "title": "Engine Overheating - Common Causes",
        "content": "Overheating in modern hatchbacks is often caused by low coolant levels, a faulty thermostat, or a blocked radiator. Check coolant reservoir and look for white residue which indicates leaks.",
        "url": "https://manual.eka.ai/general/engine"
    },
    {
        "title": "Suspension Noise - Thudding on Bumps",
        "content": "A thudding noise when driving over bumps in a sedan typically points to worn out suspension bushings or leaking shock absorbers. Hydraulic fluid on the strut body confirms a leak.",
        "url": "https://manual.eka.ai/general/suspension"
    },
    {
        "title": "Clutch Slipping Symptoms",
        "content": "Clutch slipping is evident when engine RPM increases but vehicle speed does not. This is usually due to a worn clutch plate or weak pressure plate. Requires clutch kit replacement.",
        "url": "https://manual.eka.ai/general/transmission"
    },
    {
        "title": "Battery Maintenance",
        "content": "Check car battery terminals for corrosion (white/blue powder). Clean with hot water and apply petroleum jelly. A battery older than 3 years may need a load test.",
        "url": "https://manual.eka.ai/general/electrical"
    }
]

async def seed_knowledge():
    print("Seeding Knowledge Base...")
    async with AsyncSessionLocal() as db:
        for doc in KNOWLEDGE_DATA:
            chunks = await ingest_document(
                db, 
                title=doc["title"], 
                content=doc["content"], 
                tenant_id="tenant_admin", 
                source_url=doc["url"]
            )
            print(f"Added '{doc['title']}' ({chunks} chunks)")
    print("Knowledge seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_knowledge())
