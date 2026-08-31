"""导出本地数据库为 SQL INSERT 语句"""
import sqlite3

conn = sqlite3.connect('riddles.db')
lines = []

# Export textbooks
rows = conn.execute('SELECT id, name, grade, term FROM textbooks').fetchall()
for r in rows:
    lines.append(
        f"INSERT OR IGNORE INTO textbooks (id, name, grade, term) "
        f"VALUES ({r[0]}, '{r[1]}', {r[2]}, {r[3]});"
    )

# Export riddles
rows = conn.execute(
    'SELECT id, question, answer, difficulty, textbook_id, grade, '
    'source, likes, dislikes, quality, status, submitter FROM riddles'
).fetchall()
for r in rows:
    q = r[1].replace("'", "''")
    a = r[2].replace("'", "''")
    src = (r[6] or 'manual').replace("'", "''")
    sub = 'NULL' if r[11] is None else "'" + str(r[11]).replace("'", "''") + "'"
    tb = 'NULL' if r[4] is None else str(r[4])
    lines.append(
        f"INSERT OR IGNORE INTO riddles "
        f"(id, question, answer, difficulty, textbook_id, grade, source, "
        f"likes, dislikes, quality, status, submitter) "
        f"VALUES ({r[0]}, '{q}', '{a}', {r[3]}, {tb}, {r[5]}, "
        f"'{src}', {r[7]}, {r[8]}, '{r[9]}', '{r[10]}', {sub});"
    )

# Export character_info
rows = conn.execute(
    'SELECT char, pinyin, radical, strokes, structure, meaning, decompose '
    'FROM character_info'
).fetchall()
for r in rows:
    vals = []
    for v in r:
        if v is None:
            vals.append('NULL')
        else:
            vals.append("'" + str(v).replace("'", "''") + "'")
    lines.append(
        f"INSERT OR IGNORE INTO character_info "
        f"(char, pinyin, radical, strokes, structure, meaning, decompose) "
        f"VALUES ({', '.join(vals)});"
    )

with open('sync_data.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"Exported {len(lines)} INSERT statements to sync_data.sql")
conn.close()
