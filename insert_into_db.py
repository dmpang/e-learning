#encoding=utf-8

import sqlite3
import os

# Create table
# c.execute('''CREATE TABLE all_answers
#              (exam_name text  ,
#              question text,
#              body text,
#              answer text,
#              primary key(exam_name,question)
#              )
#            ''')

def readfile(filename):
    values= []
    with open(filename,"r",encoding='gbk') as r:
        lines = r.readlines()
        for line in lines:
            tmp = eval(line)
            values.append((filename.split('\\')[-1][:-4],tmp[0],'',tmp[1].split('：')[-1]))
    return values


def insert_from_file(filename):
    conn = sqlite3.connect('answers.db')
    c = conn.cursor()
    # Insert a row of data
    # for root,dir,files in os.walk('answer'):
    #     for f in files:
    #         if f.endswith('txt'):
    #             filename = os.path.join(root,f)
    #             print(readfile(filename))
    #             c.executemany('INSERT INTO all_answers VALUES (?,?,?,?)', readfile(filename))

    c.executemany('INSERT INTO all_answers VALUES (?,?,?,?)', readfile(filename))
    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

def insert_many(values):
    conn = sqlite3.connect('answers.db')
    c = conn.cursor()
    # Insert a row of data
    # for root,dir,files in os.walk('answer'):
    #     for f in files:
    #         if f.endswith('txt'):
    #             filename = os.path.join(root,f)
    #             print(readfile(filename))
    #             c.executemany('INSERT INTO all_answers VALUES (?,?,?,?)', readfile(filename))

    c.executemany('INSERT INTO all_answers(exam_name,question,body,answer) VALUES (?,?,?,?)', values)
    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

def insert(value):
    conn = sqlite3.connect('answers.db')
    c = conn.cursor()
    # Insert a row of data
    # for root,dir,files in os.walk('answer'):
    #     for f in files:
    #         if f.endswith('txt'):
    #             filename = os.path.join(root,f)
    #             print(readfile(filename))
    #             c.executemany('INSERT INTO all_answers VALUES (?,?,?,?)', readfile(filename))

    c.execute('INSERT INTO all_answers(exam_name,question,body,answer) VALUES (?,?,?,?)', value)
    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
