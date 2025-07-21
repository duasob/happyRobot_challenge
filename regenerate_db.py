from database import DatabaseManager

if __name__ == "__main__":
    import os
    # Always remove and regenerate carriers.db in the project root
    if os.path.exists("carriers.db"):
        os.remove("carriers.db")
    db = DatabaseManager(db_path="carriers.db")
    print("Database regenerated and sample data inserted.")