path = r"LaurusLabs_20221027.pdf"

# Using pymupdf
import fitz  
import pypyodbc as odbc
import math

# Extract text page by page
with fitz.open(path) as doc:
    text_list = []
    for page in doc:
        page_text = page.get_text("text")
        list_page_text = page_text.split('\n')
        
        # remove header/footer of a page. Number of lines of header/footer changes from pdf to pdf.
        x = 0
        while True:
            if x == 9:
                break
            elif "Page" in list_page_text[x]:
                break
            x += 1
        del list_page_text[0:x+1]

        y = -1
        while len(list_page_text[y]) != 0:
            y -= 1
        del list_page_text[y:]

        text_list += list_page_text
        

# Discarding everything before moderator begins to speak
for num, sentence in enumerate(text_list):
    if "moderator:" in sentence.lower():
        list_text_needed = text_list[num:]
        break

# Fill up a list to store the conversation where each element is a dialogue by 1 person 

# Using logic - if ":" is found in a sentence keep adding sentences until another ":" is found
# This will help seperate the text by dialogues hoping someone doesn't use ":" in a dialogue which is highly unlikely
list_question_and_ans = []
for num,x in enumerate(list_text_needed):
    str_question_and_ans = ''
    # TODO: if there is a number before or after ":" it is not start of a dialogue and could be time like 12:45
    if ':' in x[:41]:    # assuming length of a name would be less than 40 characters and a ":" after 40 characters would not be a new dialogue 
        try:
            iter = num + 1
            str_question_and_ans = x
            while ':' not in list_text_needed[iter][:41]:
                str_question_and_ans = str_question_and_ans + " " + list_text_needed[iter]
                iter += 1
            list_question_and_ans.append(" ".join(str_question_and_ans.split()))    # removing extra spaces if any
        except:
            pass

# Create string to store in a text file and print dialogues
file_str_question_and_ans = ""
for x in list_question_and_ans:
    file_str_question_and_ans += str(x) + "\n\n" 

# Write string to file
text_file = open(r"extract.txt", "w")
n = text_file.write(file_str_question_and_ans)
text_file.close()

# Make sql insert statement
file_str_question_and_ans = file_str_question_and_ans.replace("'","")

# moderator
for x in text_list:
    if "moderator" in x.lower():
        moderator = x[10:]
        break
    else:
        moderator = ''

# ceo
for x in text_list:
    if "ceo" in x.lower():
        ceo = x[4:]
        break
    else:
        ceo = ''

# cfo
for x in text_list:
    if "cfo" in x.lower():
        cfo = x[4:]
        break
    else:
        cfo = ''

# relations
for x in text_list:
    if "relations" in x.lower():
        relations = x[10:]
        break
    else:
        relations = ''

qna_dict = dict()
max_char_len = 4000
max_qnas = 12

len_qna = len(file_str_question_and_ans)
if len_qna <= max_char_len:
    qna1 = file_str_question_and_ans
else: 
    # qna1
    qna_dict['qna1'] = file_str_question_and_ans[0:max_char_len]

    # qna2 - qna12
    for x in range(2,max_qnas+1):
        if len_qna>(x*max_char_len):
            qna_dict[f'qna{x}'] = file_str_question_and_ans[(x-1)*max_char_len:x*max_char_len]
        elif max_char_len <= len_qna < x*max_char_len:
            qna_dict[f'qna{x}'] = file_str_question_and_ans[(x-1)*max_char_len:len_qna]
        else:
            qna_dict[f'qna{x}'] = ''
    

compamy_name = 'abc'
concall_date = '20230129'

sql1 = f"""
    INSERT INTO MarketResearch..TranscriptExtract(Company_Name,Concall_Date,Moderator,ceo,cfo,relations,qna_1,qna_2,qna_3,qna_4)
    VALUES ('{compamy_name}','{concall_date}','{moderator}','{ceo}','{cfo}','{relations}','{qna_dict['qna1']}','{qna_dict['qna2']}','{qna_dict['qna3']}','{qna_dict['qna4']}')
"""

id_sql = """ SELECT top 1 id FROM MarketResearch..TranscriptExtract
            ORDER BY id desc
"""

# Connect to DB
DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'DESKTOP-1SPJMOG'
DATABASE_NAME = 'MarketResearch'

conn_str = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trust_Connnection=yes;
"""

conn = odbc.connect(conn_str)

cursor = conn.cursor()
cursor.execute(sql1)
conn.commit()
cursor.execute(id_sql)
id = cursor.fetchone()[0]
sql2 = f"""UPDATE MarketResearch..TranscriptExtract
    SET qna_5 = '{qna_dict['qna5']}',
    qna_6 = '{qna_dict['qna6']}',
    qna_7 = '{qna_dict['qna7']}',
    qna_8 = '{qna_dict['qna8']}'
    WHERE id = {id}
    """
sql3 = f"""UPDATE MarketResearch..TranscriptExtract
    SET qna_9 = '{qna_dict['qna9']}',
    qna_10 = '{qna_dict['qna10']}',
    qna_11 = '{qna_dict['qna11']}',
    qna_12 = '{qna_dict['qna12']}'
    WHERE id = {id}
    """
cursor.execute(sql2)
conn.commit()
cursor.execute(sql3)
conn.commit()