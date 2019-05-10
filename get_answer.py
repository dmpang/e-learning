# encoding=utf-8

import sqlite3
import time, re
from splinter import Browser
import logging

logger = logging.getLogger()
# import os

# Create table
# c.execute('''CREATE TABLE all_answers
#              (exam_name text  ,
#              question text,
#              body text,
#              answer text,
#              primary key(exam_name,question)
#              )
#            ''')

db_path = 'answers.db'


def get(exam, question):
    answer = '' 
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    t = ('%' + exam + '%', '%' + question + '%')
    logger.info(f'"select answer from all_answers where exam_name like ? and question like ?", {t}')
    c.execute("select answer from all_answers where exam_name like ? and question like ?", t)
    result = c.fetchone()
    if result is None or result[0] == '':
        logger.info(f'"select answer from all_answers where question like ?", {(t[1],)}')
        c.execute("select answer from all_answers where question like ?", (t[1],))
        result = c.fetchone()
    if result:
        answer = result[0]
    conn.close()
    return answer


def get2(exam, question):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    t = (exam, question)
    logger.info(f'"select answer from all_answers where exam_name = ? and question = ?", {t}')
    c.execute("select answer from all_answers where exam_name = ? and question = ?", t)
    answer = c.fetchone()[0]
    conn.close()
    logger.info(answer)
    return answer

def get_count(exam, question):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    t = (exam, question)
    c.execute("select count(1) from all_answers where exam_name = ? and question = ?", t)
    count = c.fetchone()[0]
    conn.close()
    return count

def see_all():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("select * from all_answers order by 5 desc")
    for i in c.fetchall():
        print(i)
    conn.close()


def get_all2(exam):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    t = ('%' + exam + '%',)
    c.execute("select * from all_answers where exam_name like ? ", t)
    answer = [i for i in c.fetchall()]
    print(len(answer))
    for a in answer:
        print(a)
    conn.close()
    logger.info(answer)
    return answer


def delete_exam(exam):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    t = (exam,)
    c.execute("delete from all_answers where exam_name  =  ? ", t)
    conn.commit()
    conn.close()




def set_body(exam, question, body):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    t = (body, exam, question)
    c.execute("update all_answers set body = ? where exam_name = ? and question = ?", t)
    conn.commit()
    conn.close()


def set_answer(exam, question, answer):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    t = (answer, exam, question)
    c.execute("update all_answers set answer = ? where exam_name = ? and question = ?", t)
    conn.commit()
    conn.close()


def readfile(filename):
    values = []
    with open(filename, "r", encoding='gbk') as r:
        lines = r.readlines()
        for line in lines:
            tmp = eval(line)
            values.append((filename.split('\\')[-1][:-4], tmp[0], '', tmp[1].split('：')[-1]))
    return values


def insert_from_file(filename):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Insert a row of data
    # for root,dir,files in os.walk('answer'):
    #     for f in files:
    #         if f.endswith('txt'):
    #             filename = os.path.join(root,f)
    #             logger.info(readfile(filename))
    #             c.executemany('INSERT INTO all_answers VALUES (?,?,?,?)', readfile(filename))

    c.executemany('INSERT INTO all_answers VALUES (?,?,?,?)', readfile(filename))
    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def insert_many(values):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Insert a row of data
    # for root,dir,files in os.walk('answer'):
    #     for f in files:
    #         if f.endswith('txt'):
    #             filename = os.path.join(root,f)
    #             logger.info(readfile(filename))
    #             c.executemany('INSERT INTO all_answers VALUES (?,?,?,?)', readfile(filename))

    c.executemany('INSERT INTO all_answers(exam_name,question,body,answer) VALUES (?,?,?,?)', values)
    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def insert_single(value):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Insert a row of data
    # for root,dir,files in os.walk('answer'):
    #     for f in files:
    #         if f.endswith('txt'):
    #             filename = os.path.join(root,f)
    #             logger.info(readfile(filename))
    #             c.executemany('INSERT INTO all_answers VALUES (?,?,?,?)', readfile(filename))

    c.execute('INSERT INTO all_answers(exam_name,question,body,answer) VALUES (?,?,?,?)', value)
    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def get_answers_html(exam_title):
    logger.info(f"beging: get_answers_html,q = {exam_title}")
    html = ''
    browser = Browser(driver_name='chrome', executable_path='chromedriver.exe', headless=True)
    examtitle = exam_title
    # examtitle = 'POS机、银行卡概述'
    url = 'https://www.tiku88.com/'
    browser.visit(url)
    browser.fill('q', examtitle)
    time.sleep(2)
    browser.find_by_id('search_submit').click()
    time.sleep(2)
    html = browser.html

    while True:
        try:
            browser.find_link_by_partial_text('下一页').first.click()
            time.sleep(3)
            print("追加下一页的内容")
            html += browser.html
        except Exception as e:
            print("没有下一页")
            break
    browser.quit()
    return html


def get_question_answer(text):
    title = re.findall(r'<li><span>(.*)</span><span style="color: red">(.*)</span></li>', text)
    courses = re.findall(r'<a class="exam_url" href=".*">&gt;&gt;查看此课程相关问题：(.*)</a>', text)
    logger.info(courses)
    question_answer = []
    for index, i in enumerate(title):
        question_answer.append(
            [i[0].replace('<span class="highlighted">', '').replace('</span>', ''), i[1], courses[index]])
    return question_answer


def get_question_selection(text):
    covert = {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E', '6': 'F', '7': 'G', '8': 'H'}
    reg = r'''<ol start="(.*)" style="list-style-type: upper-alpha">
                        <li>(.*)</li>
                        </ol>'''

    selecttion = [[], ]
    body = re.findall(reg, text)
    cursor = 0
    for index, item in enumerate(body):
        if index != 0 and item[0] == '1':
            cursor += 1
            selecttion.append([])
        selecttion[cursor].append([covert[item[0]], item[1]])
    return selecttion


def insert_answersInfo_to_db(exam_title):
    html = get_answers_html(exam_title)
    ques_ans = get_question_answer(html)
    selection = get_question_selection(html)
    values = []

    for i, qa in enumerate(ques_ans):
        values.append(
            (qa[2],
             qa[0].replace('　','').replace(' ', '').replace('（', '(').replace('）', ')').replace('，', ',').replace('“', '"').replace('”', '"'),
             repr(selection[i]),
             qa[1].replace('答案：', '')
             )
        )
    # logger.info("\n".join(lines),file=open(examtitle+'.txt',"w"))
    # logger.info(values)
    logger.info(f"共获取题目 {len(values)} 个")

    tmp_str = ""
    for v in values:
        logger.info(v)
        tmp_str += repr(v)
        tmp_str += '\n'
    # logger.info(tmp_str, file=open(exam_title + ".txt", "w", encoding='gbk'))
    for v in values:
        try:
            insert_single(v)
        except Exception as e:
            logger.info(f"insert_answersInfo_to_db : {e}")


def insert_answersInfo_to_db_byHand(values):
    '''
    :param values:[('exam','question','selection','answer'),
                    ('exam','question','selection','answer'),]
    :return:
    True :insert success
    False: insert failed
    '''
    for v in values:
        try:
            insert_single(v)
        except Exception as e:
            logger.info(f"insert_answersInfo_to_db_byHand : {e}")


def fix_answersInfo_to_db_byHand(values):
    '''
    :param values:[('exam','question','selection','answer'),
                    ('exam','question','selection','answer'),]
    :return:
    True :insert success
    False: insert failed
    '''
    for v in values:
        try:
            print(v)
            count = get_count(v[0],v[1])
            if count == 0:
                print(f"insert,insert_single({v})")
                insert_single(v)
            else:
                print(f"update,set_single({v[0],v[1],v[3]})")
                set_answer(v[0],v[1],v[3])
        except Exception as e:
            logger.info(f"fix_answersInfo_to_db_byHand : {e}")

if __name__ == "__main__":
    # get("1111点滴行动  助力反洗钱","银行客户可以采取以下哪些措施远离洗钱")
    # get_all2('第四章 证券市场典型违法违规行为及法律责任')
    # insert_answersInfo_to_db(exam_title='开展“两学一做”学习教育的总体要求')
    # delete_exam('开展“两学一做”学习教育的总体要求')
    # insert_answersInfo_to_db(exam_title='习近平全面从严治党新思路')
    # get_all2('开展“两学一做”学习教育的总体要求')
    # set_answer('开展“两学一做”学习教育的总体要求','领导要成为活动的','D')
    # print(get('开展“两学一做”学习教育的总体要求','领导要成为活动的'))
    # print(get('在反腐倡廉方面做合格的共产党员','()是政党的宗旨和行为规范'))
    # get_all2('习近平全面从严治党新思路')
    # delete_exam('在反腐倡廉方面做合格的共产党员')
    # insert_answersInfo_to_db(exam_title='在反腐倡廉方面做合格的共产党员')
    # get_all2('在反腐倡廉方面做合格的共产党员')
    # print(get('在反腐倡廉方面做合格的共产党员','(),指作为具有先进性的组织,它的纪律应高于法律'))
    # print(get('在反腐倡廉方面做合格的共产党员', '要善于发掘全党创新手段,把创新不断引向深入层面,开拓创新新局面'))
    see_all()
    # print(get('第二章 证券从业人员管理','下列不属于证券、期货投资咨询人员申请取得证券、期货投资咨询从业资格'))
    # get_all2('第二章 证券从业人员管理')
