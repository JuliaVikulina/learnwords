from datetime import datetime, timedelta
from pprint import pprint

import psycopg2

conn = psycopg2.connect(dbname='learnwords_db', user='learnwords', host='localhost', password='learnwords')
conn.autocommit = True

print(conn)
cur = conn.cursor()
cur.execute('SELECT version()')
ver = cur.fetchone()
print(ver)

# cur.execute("SELECT * FROM words")
# ver = cur.fetchall()
# pprint(ver)

fetch_koeff = dict(fetched=2, not_fetched=1)


def get_words_by_user(username):
    cur.execute("SELECT * FROM words")
    response = cur.fetchall()
    pprint(response)


def add_word_for_user(word, translation, pronunciation, last_repeated, delta, username):
    last_repeated_datetime = datetime.fromtimestamp(last_repeated)
    interval = timedelta(days=delta)
    repeat_after = last_repeated_datetime + interval
    learnt = bool(0)
    cur.execute("""INSERT INTO words VALUES (default, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (word, translation, pronunciation,
                 last_repeated_datetime,
                 repeat_after, interval, username, learnt))


def set_word_learnt(word_id, date_unix, username):
    last_repeated = datetime.fromtimestamp(date_unix)
    delta = timedelta(days=1)
    repeat_after = last_repeated + delta
    # TODO debug this
    cur.execute("UPDATE words SET learnt=%s, last_repeated=%s, delta=%s WHERE id=%s AND username=%s",
                (last_repeated, repeat_after, delta, word_id, username))


def count_words_to_repeat(date_unix, username):
    repeat_after = datetime.fromtimestamp(date_unix)
    cur.execute("SELECT count(*) FROM words WHERE username=%s AND learnt=1 AND repeat_after<=%s",
                (username, repeat_after))
    return cur.fetchone()[0]


def get_one_word_to_repeat(date_unix, username):
    repeat_after = datetime.fromtimestamp(date_unix)
    cur.execute("SELECT id, word FROM words WHERE username=%s AND repeat_after<=%s ORDER BY repeat_after DESC LIMIT 1",
                (username, repeat_after))
    return cur.fetchone()


def get_word_by_id(word_id, username):
    cur.execute("SELECT * FROM words WHERE id=%s AND username<=%s LIMIT 1",
                (word_id, username))
    return cur.fetchone()


def set_fetched_word(word_id,
                     date_unix,
                     direction,
                     status,
                     username):
    last_repeated = datetime.fromtimestamp(date_unix)

    word = get_word_by_id(word_id, username)
    delta = timedelta(minutes=1)
    if status == 0:
        delta = word[6] * fetch_koeff['fetched']
    elif status == -1:
        delta = word[6] * fetch_koeff['not_fetched']

    if delta == timedelta(0):
        delta = timedelta(days=1)

    repeat_after = last_repeated + delta
    cur.execute("UPDATE words SET last_repeated=%s, repeat_after=%s, delta=%s WHERE id=%s AND username=%s",
                (last_repeated, repeat_after, delta, word_id, username))
    cur.execute("""INSERT INTO repetitions VALUES (default, %s, %s, %s, %s, %s)""",
                (word_id, username, last_repeated, direction, status))
    print("Number of rows updated: %d".format(cur.rowcount))
    return repeat_after


def update_translation_of_word_for_user(word_id, translation,  username):
    # TODO what for?
    cur.execute("UPDATE words SET translation=%s WHERE id=%s AND username=%s", (translation, word_id, username))

    print("Number of rows updated: %d".format(cur.rowcount))


if __name__ == '__main__':
    get_words_by_user("julia_vikulina")

# for table in meta.tables:
#      print(table)
#
# slams = meta.tables['slams']
#
# clause = slams.insert().values(name='Wimbledon', country='United Kingdom')
#
# # con.execute(clause)
#
# clause = slams.insert().values(name='Roland Garros', country='France')
#
# # result = con.execute(clause)
# #
# # print(result)
# #
# # print(result.inserted_primary_key)
#
# victories = [
#     {'slam': 'Wimbledon', 'year': 2003, 'result': 'W'},
#     {'slam': 'Wimbledon', 'year': 2004, 'result': 'W'},
#     {'slam': 'Wimbledon', 'year': 2005, 'result': 'W'}
# ]
#
# # print(con.execute(meta.tables['results'].insert(), victories))
#
# results = meta.tables['results']
# print(results.c)
# for col in results.c:
#     print(col)
#
# clause = results.select().where(results.c.year == 2005)
# for row in con.execute(clause):
#     print(row)