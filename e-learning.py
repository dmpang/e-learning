# encoding=utf-8 
from splinter import Browser
import time, re, sys
import get_answer
import logging
from threading import Thread
from optparse import OptionParser


logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename="info.log")
formatter = logging.Formatter('%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)  # 将日志输出至屏幕
logger.addHandler(fh)  # 将日志输出至文件


class AutoLearning(object):
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd
        self.browser = None
        self.base_url = 'http://e-learning.jsnx.net'
        self.map_url = 'http://e-learning.jsnx.net/els/html/index.parser.do?id=0007'

    def login(self):
        self.browser = Browser(driver_name='chrome', executable_path='chromedriver.exe')
        self.browser.visit(self.base_url)
        time.sleep(3)
        self.browser.fill('loginName', self.username)
        self.browser.fill('password', self.passwd)
        self.browser.find_by_xpath('//*[@id="form-login"]/div/div[3]/input').click()
        time.sleep(3)
        try:
            self.browser.find_by_value('继续登录').click()
            time.sleep(2)
        except:
            pass

    def get_my_courses(self, skip_num=0, learning=True):
        time.sleep(3)
        self.browser.find_by_text('课程中心').click()
        time.sleep(5)
        # logger.info(self.browser.windows)
        self.browser.windows.current = self.browser.windows[1]
        time.sleep(5)
        # self.browser.find_link_by_partial_href()
        self.browser.find_by_text('''
                        我的课程''').click()
        time.sleep(5)
        # logger.info(self.browser.html)

        self.browser.find_by_text('未学习').click()
        time.sleep(5)
        if learning:
            self.browser.find_by_text('进行中').click()
            time.sleep(5)

        # 翻页
        page = 1
        while True:
            time.sleep(3)
            total_courses = re.findall(r'<h3 class="card-title" title="(.*)" style="margin-bottom: 12px;">',
                                       self.browser.html)
            logger.info(f"当前第{page}页共有课程: {len(total_courses)} 个: {total_courses}.")
            courses = total_courses[skip_num:]
            if skip_num:
                logger.info(f"跳过开头 {skip_num} 个")
            for index, c in enumerate(courses):
                time.sleep(2)
                logger.info(f" begin to learn {c}.")
                self.do_learn(index + 1 + skip_num, c, None)  # 获取 xpath 使用
                time.sleep(2)
            page += 1
            try:
                self.browser.find_by_text(page).click()
            except Exception as e:
                logger.info(f"已无法再进行翻页 {e}")
                break

    def get_learn_map(self, skip_num=0,learn_number = 1):

        self.browser.visit(self.map_url)
        time.sleep(3)
        self.browser.find_by_xpath(f'//*[@id="trackList"]/ul/li[{learn_number}]/div[2]/div[2]/div[1]/a').first.click()
        time.sleep(3)
        regex = re.compile('<a href="#" id="(.*)" title="(.*)" class="innercan goCourseByStudy"')
        time.sleep(3)
        toltal_courses = re.findall(regex, self.browser.html)
        courses = toltal_courses[skip_num:]
        if skip_num:
            logger.info(f"跳过开头 {skip_num} 个")

        course_names = '\n'.join([c[1] for c in courses])
        logger.info(f"will learn {len(courses)} courses, they are: {course_names}")
        for index, course in enumerate(courses):
            logger.info(f" begin to learn {course[1]}.")
            self.do_learn(index + 1, course[1], course_id=course[0])
            time.sleep(3)

    def do_learn(self, xpath_id, course_name, course_id=None):
        # 每多少秒检查一次状态
        freuency = 30
        try:
            if course_id:
                logger.info(f"will click id = {course_id}, course_name = {course_name}")
                self.browser.find_by_id(course_id).click()
            else:
                try:
                    self.browser.find_by_xpath(f'//*[@id="studyTaskList"]/ul/li[{xpath_id}]/a/div[2]/h3').click()
                except Exception as e:
                    logger.info(f"do_learn: {e}")
                    self.browser.click_link_by_partial_text(course_name)
            time.sleep(3)
            self.browser.windows.current = self.browser.windows.current.next
            time.sleep(10)
            now_text = self.browser.html
            time.sleep(10)

            ##如果是课后测试页，那么做题，否则继续往下进行。
            if self.auto_answer(now_text):
                time.sleep(3)
                self.browser.windows.current = self.browser.windows.current.prev
                return 0

            ##如果有课前测试页
            self.auto_pre_test(now_text)

            wait_count = 0
            quit_count = 0
            while True:
                time.sleep(freuency)
                if self.canNext():
                    self.evaluation()
                    time.sleep(6)
                    self.auto_answer(self.browser.html)
                    break
                else:
                    wait_count += 1
                    if self.isMoreVedio(self.browser.html):
                        # logger.info(f" 有多个视频项目")
                        if self.isPlaying(self.browser.html):
                            # logger.info(f" 正在播放:{course_name}")
                            pass
                        else:
                            logger.info(f" 播放完毕，刷新")
                            self.browser.reload()
                            time.sleep(5)

                    else:
                        # logger.info(f"有1个视频项目")
                        pass
                    ##防止验证码
                    if (wait_count * freuency / 60) % 10 == 0:
                        logger.info(f" 超过 {wait_count*freuency/60} 分钟，刷新")
                        self.browser.reload()
                    ##防止死等，如果很久都过不去，那么自动跳过此课程学习
                    if (wait_count * freuency / 60) >= 120:
                        logger.info(f" 超过 {wait_count*freuency/60} 分钟，退出本课程")
                        wait_count = 0
                        self.browser.windows.current = self.browser.windows.current.prev
                        return
            self.browser.windows.current = self.browser.windows.current.prev
        except Exception as e:
            logger.info(f"do_learn error: {e}")

    def canNext(self):
        try:
            # driver.find_element_by_xpath('//*[@id="elpui-layer1"]/div[3]/a').click()
            try:
                self.browser.find_by_text('确定').click()
            except:
                pass
            time.sleep(5)
            self.browser.find_by_xpath('//*[@id="goNextStep"]/a').click()
            time.sleep(3)
            return True
        except Exception as e:
            # logger.info("canNext",e)
            return False

    def isMoreVedio(self, text):
        regex_count_item = re.compile(
            '<a href="javascript:;" data-id=".*" title="(.*)" class="scormItem-no cl-catalog-link cl-catalog-link-sub')
        vedios = re.findall(regex_count_item, text)
        if vedios and len(vedios) > 0:
            return True
        else:
            return False

    def isPlaying(self, text):
        regex_count_item = re.compile('item-no cl-catalog-playing')
        playings = re.findall(regex_count_item, text)
        if playings and len(playings) > 0:
            # logger.info(playings)
            return True
        else:
            return False

    def evaluation(self):
        try:
            ##开始进行课程评估
            logger.info(f" 开始进行课程评估")
            time.sleep(2)
            self.browser.find_by_xpath(
                u"(.//*[normalize-space(text()) and normalize-space(.)='★'])[3]/following::input[1]").click()
            time.sleep(1)
            self.browser.find_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='B'])[1]/following::span[1]").click()
            time.sleep(1)
            self.browser.find_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='B'])[2]/following::span[1]").click()
            time.sleep(1)
            self.browser.find_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='B'])[3]/following::span[1]").click()
            time.sleep(1)
            self.browser.find_by_xpath(
                "(.//*[normalize-space(text()) and normalize-space(.)='B'])[4]/following::span[1]").click()
            time.sleep(2)
            self.browser.find_by_id("courseEvaluateSubmit").click()
            time.sleep(2)
            self.browser.find_by_text(u"确定").click()
            time.sleep(2)
            try:
                self.browser.find_by_text(u"进入下一步").click()
                time.sleep(2)
            except:
                logger.info("此课程不需要测试")
                self.browser.find_by_text(u"查看结果").click()
                time.sleep(2)
            logger.info(f"已提交课程评估")
        except Exception as e:
            logger.info(f"evaluate 1: {e}")
            pass


    def auto_answer(self, text):
        '''
        :param text:
        :return:
         True 此页是课后测试页
         False 此页不是课后测试页
        '''
        global answerByHand
        answerByHand = False  # 默认不手工做题
        logger.info("auto_answer:begin")

        def get_user_confirm():
            global answerByHand
            logger.info("是否手工做题，并将答案自动记录在数据库中(yes)：（yes/no）? ")
            a = input("是否手工做题，并将答案自动记录在数据库中(yes)：（yes/no）? ")
            if a != 'no':
                print(a)
                answerByHand = True

        try:
            # exam 可以通过 get_html_test 来获取
            exam, tmp = self.get_html_test(text)
            if exam is None or tmp is None:
                logger.info("此页不是课后测试页")
                return False
            test = [t for t in tmp]
            # logger.info(exam,test)
            if test == []:
                logger.info("此页不是课后测试页")
                return False
            # values = []
            logger.info("开始获取答案")
            # values_into_db = []

            skip_flag = False  # 是否跳过爬取答案
            for t in test:
                answer = []
                question_str = t[0].replace('　', '').replace(' ', '').replace('（', '(').replace('）', ')').replace('，',
                                                                                                                  ',').replace(
                    '“', '"').replace('”', '"')
                logger.info(f"get_answer.get('{exam}','{question_str}')")
                answer = get_answer.get(exam, question_str)
                if answer == '' and skip_flag is False:  # 不必重复爬取课程
                    get_answer.insert_answersInfo_to_db(exam_title=exam)
                    answer = get_answer.get(exam, question_str)

                if answer == '':
                    get_answer.insert_answersInfo_to_db(exam_title=question_str)
                    answer = get_answer.get(exam, question_str)

                logger.info(answer)
                # 保存答案对应的id
                # 如果无答案就保存下来手工做题并插入数据库中
                if answer == '':
                    skip_flag = True
                    # tmp_list = []
                    # for k in t[1]:
                    #     tmp_list.append([k[0], k[1], k[2]])
                    # values_into_db.append([exam,  # 课程
                    #                        question_str,
                    #                        tmp_list,  # 选项
                    #                        # 答案
                    #                        ])
                # 如果有答案，则自动勾选
                else:
                    for temp in t[1]:
                        if temp[0] in answer:
                            self.browser.find_by_id('answer_item_' + temp[1]).click()
                            time.sleep(1)

                # 需要手工做题确认 30 秒

            if skip_flag:  # 如果有跳过的题目，说明此题无法自动做答，等待 30 秒看是否需要手工做题
                Thread(target=get_user_confirm, daemon=True).start()
                time.sleep(30)
                if answerByHand:
                    a = input("是否做题完并跳转到结果页面：(yes/no)? ")
                    if a == "yes":
                        logger.info("开始修正题目答案")
                        time.sleep(6)
                        self.get_html_test_right_answer(self.browser.html)
                    #     id_options = self.get_answers_id_byHand(self.browser.html)
                    #     print(id_options)
                    #     for index, va in enumerate(values_into_db):
                    #         tmp = []
                    #         for k in va[2]:
                    #             if k[1] in id_options:
                    #                 tmp.append(k[0])
                    #         values_into_db[index].append("".join(tmp))
                    #
                    #     values = []
                    #     for v in values_into_db:
                    #         tmp = [[x[0], x[2]] for x in v[2]]
                    #         values.append((v[0], v[1], repr(tmp), v[3]))
                    #     logger.info(repr(values))
                    #     get_answer.insert_answersInfo_to_db_byHand(values)
                    # else:
                        return True
                else:
                    return True
            # 点击确定，提交答案
            time.sleep(2)
            self.browser.find_by_id('goNext').click()
            time.sleep(2)
            self.browser.find_by_text('确定').click()
            time.sleep(2)
            logger.info("auto_answer:end")
            return True
        except Exception as e:
            logger.info(f"auto_answer_function: {e}")
            return True

    def get_html_test(self, html):
        '''
        :param html:
        :return:
        (exam,[(question,[(option,id,description)],),()])

        '''
        logger.info("get_html_test:begin")
        exam_name_reg = '<h3 class="cs-header-title" title="(.*)" style="cursor:pointer;" data-id='
        # title_reg = '<h5 class="cs-test-question"><span>\d+</span>、(.*)（<span class="sc-test-point">.*</span>分）'
        question_reg = '<h5 class="cs-test-question"><span>\d+</span>、(.*)（.*'
        questions = re.findall(question_reg, html)
        logger.info(f"本页共有题目: {len(questions)}")
        exam_name = re.findall(exam_name_reg, html)
        # logger.info(titles)
        # logger.info(exam_tmp)
        if exam_name == [] or questions == []:
            return (None, None)
        exam = exam_name[0]
        answer_reg = 'id="answer_item_(.*)">(.*)<'
        cs_option_row_reg = '<p class="cs-option-row" \w+="\w+">(.*\n*.*)</p>'
        # '<p class="cs-option-row" id="answer_item_93968b399d3449e8b50e2b3b89526d98">正确</p>'
        options = re.findall(cs_option_row_reg, html)
        logger.info(f"本页共有选项: {len(options)}")
        answers = re.findall(answer_reg, html)
        logger.info(f"本页共有选项2: {len(answers)}")
        answers_new = []
        for index, item in enumerate(answers):
            tmp = item[1]
            if item[1] == '正确':
                tmp = 'A'
            elif item[1] == '错误':
                tmp = 'B'
            else:
                pass
            answers_new.append((tmp, item[0], options[index]))
        i = 0
        values = [[] for _ in questions]
        for index, item in enumerate(answers_new):
            # logger.info(index,item)
            if index != 0 and item[0] == 'A':
                i += 1
            values[i].append(item)
        logger.info("get_html_test:end")
        return (exam, zip(questions, values))

    def get_html_test_right_answer(self, html):
        '''
        :param html:
        :return:
        (exam,[(question,[(option,id,description)],),()])

        '''
        logger.info("get_html_test:begin")
        exam_name_reg = '<h3 class="cs-header-title" title="(.*)" style="cursor:pointer;" data-id='
        # title_reg = '<h5 class="cs-test-question"><span>\d+</span>、(.*)（<span class="sc-test-point">.*</span>分）'
        question_reg = '<h5 class="cs-test-question"><span>\d+</span>、(.*)（.*'
        questions = re.findall(question_reg, html)
        logger.info(f"本页共有题目: {len(questions)}")
        exam_name = re.findall(exam_name_reg, html)
        # logger.info(titles)
        # logger.info(exam_tmp)
        exam = exam_name[0]
        answer_reg = 'id="answer_item_(.*)">(.*)<'
        cs_option_row_reg = '<p class="cs-option-row" \w+="\w+">(.*\n*.*)</p>'
        # '<p class="cs-option-row" id="answer_item_93968b399d3449e8b50e2b3b89526d98">正确</p>'
        options = re.findall(cs_option_row_reg, html)
        logger.info(f"本页共有选项: {len(options)}")
        answers = re.findall(answer_reg, html)
        logger.info(f"本页共有选项2: {len(answers)}")

        right_answers_reg = '<p class="cs-test-answer">正确答案:<span class="cs-answer-mark" id="answer_\w+">(.*)</span></p>'
        right_answers = re.findall(right_answers_reg, html)

        logger.info(f"本页共有正确答案: {len(right_answers)}")

        answers_new = []
        for index, item in enumerate(answers):
            tmp = item[1]
            if item[1] == '正确':
                tmp = 'A'
            elif item[1] == '错误':
                tmp = 'B'
            else:
                pass
            answers_new.append((tmp, item[0], options[index]))
        i = 0
        values = [[] for _ in questions]
        for index, item in enumerate(answers_new):
            # logger.info(index,item)
            if index != 0 and item[0] == 'A':
                i += 1
            values[i].append(item)
        # print(exam)
        right_values = []
        for value in zip(questions, values, right_answers):
            question_str = value[0].replace('　', '').replace(' ', '').replace('（', '(').replace('）', ')').replace('，',
                                                                                                                  ',').replace(
                '“', '"').replace('”', '"')
            selections = [[item[0], item[2]] for item in value[1]]
            selections_str = repr(selections)
            right_values.append((exam, question_str, selections_str, value[2].replace(' ','').replace('　','')))
            # print((exam,question_str,selections_str,value[2]))
        get_answer.fix_answersInfo_to_db_byHand(right_values)

    def get_answers_id_byHand(self, html):
        '''
        :param html:
        :return:
        (exam,[(question,[(option,id,description)],),()])

        '''
        # print(html)
        cs_option_row_reg = 'value="(.*)" class="cs-option-radio" checked="checked"'
        options = re.findall(cs_option_row_reg, html)
        return options

    def auto_pre_test(self, text):
        try:
            reg = '<span class="cs-ins-title">说明：课前测试是测试您对课程内容的初期掌握情况，带着问题参与学习，测试结果不计入考试成绩。</span>'
            is_pre = re.findall(reg, text)
            if is_pre:
                logger.info("课前测试")
            else:
                logger.info("非课前测试")
                return 0
            all_option_reg = '<p class="cs-option-row" id="answer_item_(.*)">'
            options = re.findall(all_option_reg, text)
            logger.info(options)
            for index, option in enumerate(options):
                if index % 2 == 0:
                    self.browser.find_by_id("answer_item_" + option).click()
                    time.sleep(0.5)
            time.sleep(1)
            self.browser.find_by_text(u'进入下一步').click()
        except Exception as e:
            logger.info(f"auto_pre_test_fuck: {e}")


if __name__ == '__main__':
    # logger.info(sys.argv)
    parser = OptionParser(usage="%prog [-u] [-s] [-c] [-s] [fix]", version="%prog 1.0")
    parser.add_option("-u", "--username", dest="username", help="input your account name")
    parser.add_option("-p", "--password", dest="password", help="input your password")
    parser.add_option("-c", "--course", dest="course", help="learn which one? [学习地图=0 我的课程=1]")
    parser.add_option("-s", "--skipnum", dest="skipnum", help="skip number,跳过开头多少个课程，防止卡住，一般不常用")
    parser.add_option("-n", "--number", dest="number", help="number,学习地图中从上到下第几个要学的任务，默认为1")

    (options, args) = parser.parse_args()
    if options.username is None and args == []:
        parser.print_help()
        parser.error("incorrect number of arguments or args.")

    skipNum = int(options.skipnum) if options.skipnum else 0
    learnNum = int(options.number) if options.number else 1
    auto = AutoLearning(options.username,options.password)
    if args != [] and args[0]=="fix":
        print("使用 right.html 来修正答案")
        auto.get_html_test_right_answer(open("right.html","r",encoding='utf-8').read())
        exit(0)
    auto.login()
    if options.course == '0':
        auto.get_learn_map(skip_num=skipNum,learn_number=learnNum)
    else:
        auto.get_my_courses(skip_num=skipNum)
    time.sleep(10)
    auto.browser.quit()
