import pandas as pd
import chromadb

# Load ChromaDB Client
chroma_client = chromadb.PersistentClient(path="./first_vectordb")

# Create or Get Collection
ipc_collection = chroma_client.get_or_create_collection(name="ipc_sections")

# Load CSV File
csv_file_path = "Final_IPC_Sections.csv"  # Update with your actual CSV path

try:
    df = pd.read_csv(csv_file_path, encoding="ISO-8859-1")
    
    # 🔹 Ensure all values are strings and replace NaN values
    df = df.fillna("").astype(str)

except Exception as e:
    print(f"❌ Error loading CSV: {e}")
    exit()

# Insert Data into VectorDB
inserted_count = 0
skipped_count = 0

for index, row in df.iterrows():
    section_id = row["Section"].strip()  # Ensure Section ID is a string
    description = row["Description"].strip()  # Ensure description is a string

    # Skip rows with empty Section ID or Description
    if not section_id or not description:
        print(f"⚠️ Skipping row {index} due to missing Section ID or Description.")
        skipped_count += 1
        continue

    # Extract metadata safely (convert everything to a string)
    metadata = {
        "section": section_id,
        "description": description,
        "offense": row.get("Offense_fir", "").strip(),
        "punishment": row.get("Punishment_fir", "").strip(),
        "cognizable": row.get("Cognizable", "").strip(),
        "bailable": row.get("Bailable", "").strip(),
        "court": row.get("Court", "").strip(),
        "url": row.get("URL", "").strip(),
        "replaced_with": row.get("Replaced with (BNS)", "").strip()
    }

    try:
        ipc_collection.add(
            ids=[section_id],
            documents=[description],
            metadatas=[metadata]
        )
        print(f"✅ Inserted {section_id} into first_vectordb")
        inserted_count += 1
    except Exception as e:
        print(f"❌ Error inserting {section_id}: {e}")

print(f"\n🚀 Insertion Complete! ✅ {inserted_count} inserted, ⚠️ {skipped_count} skipped.")
