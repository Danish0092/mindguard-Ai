
from sqlalchemy import text
from app.db.database import engine

query = text("""
    SELECT student_id, COUNT(*) AS active_cases
    FROM escalations
    WHERE status IN ('OPEN', 'ACKNOWLEDGED')
    GROUP BY student_id
    HAVING COUNT(*) > 1
""")

with engine.connect() as connection:
    rows = connection.execute(query).all()
    print("Students with duplicate active cases:", rows)
