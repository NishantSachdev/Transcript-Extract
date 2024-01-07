import json
import logging
import pypyodbc as odbc
import fitz


# Set up logging without log file
logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    logging.info("------------ BEGIN: Data Extraction from Concall Transcript PDF ------------")

    config_obj = config_reader()
    db_name = config_obj["DATABASE_NAME"]
    filename = config_obj["FILENAME"]

    path = f"input/transcripts/{filename}"

    logging.info("Reading text from all pages of pdf and store it in a list where each element is a line of text...")
    list_full_pdf_text = extract_text_from_pdf(path)

    logging.info("Discarding everything before moderator begins to speak...")
    list_text_needed = discard_intro(list_full_pdf_text)

    logging.info("Extracting QnA from a list where each element is a line of text...")
    list_question_and_ans = extract_qna(list_text_needed)
    
    logging.info("Creating string of all dialogues to store in a text file for manual proof reading when required...")
    file_str_question_and_ans = store_all_dialogues(list_question_and_ans)
    
    logging.info("Finding names of important company representators...")
    moderator, ceo, cfo, relations = find_names_of_imp_company_representators(list_full_pdf_text)

    logging.info("Breaking the full data string into multiple strings of maximum allowed length of a column in sql server...")
    qna_dict = preparing_data_for_db_storage(file_str_question_and_ans)

    # Dummy data for fields yet to be found
    compamy_name = "abc"
    concall_date = "20230129"

    logging.info("Establishing DB connection...")
    conn_str = create_connection_string(config_obj)
    conn, cursor = db_connection(conn_str)

    # Separating out the insert to DB code so that huge amount of data can be parsed without breaching the maximum allowed insertion data for MS SQL Server
    logging.info("Inserting data into DB...")
    id, conn, cursor = insert_data_into_db_1(compamy_name, concall_date, moderator, ceo, cfo, relations, qna_dict, db_name, conn, cursor)
    insert_data_into_db_2(id, qna_dict, db_name, conn, cursor)

    logging.info("------------ END: Data Extraction from Concall Transcript PDF ------------")


######################################## Sub Main Functions #######################################
    

# Reads text from all pages of a pdf and stores in a list where each element is a line of text
def extract_text_from_pdf(path):
    with fitz.open(path) as doc:
        list_full_pdf_text = []
        for page in doc:
            page_text = page.get_text("text")
            list_page_text = page_text.split("\n")
            x = 0

            # Discard page header
            while True:
                if x == 9:
                    break
                elif "Page" in list_page_text[x]:
                    break
                x += 1
            del list_page_text[0: x + 1]

            # Discard page footer
            y = -1
            while len(list_page_text[y]) != 0:
                y -= 1
            del list_page_text[y:]

            list_full_pdf_text += list_page_text

        return list_full_pdf_text
    

# Discards everything before moderator begins to speak
def discard_intro(list_full_pdf_text):
    for num, sentence in enumerate(list_full_pdf_text):
        if "moderator:" in sentence.lower():
            list_text_needed = list_full_pdf_text[num:]
            break

    return list_text_needed


# Try to extract QnA from a list where each element is a line of text
def extract_qna(list_text_needed):
    list_question_and_ans = []    # empty list to store the conversation where each element is a dialogue by 1 person
    max_name_length = 40    # assuming max length of a name would be 40 characters

    """ Using logic - if ":" is found in a sentence keep adding sentences until another ":" is found
    This will help seperate the text by dialogues hoping someone doesn't use ":" in a dialogue which is highly unlikely """
    for num, x in enumerate(list_text_needed):
        str_question_and_ans = ""
        # TODO: if there is a number before or after ":" it is not start of a dialogue and could be time like 12:45
        if (":" in x[:max_name_length + 1]):  # assuming : before 'max_name_length' would not be a new dialogue.
            try:
                iter = num + 1
                str_question_and_ans = x
                while ":" not in list_text_needed[iter][:max_name_length + 1]:
                    str_question_and_ans = str_question_and_ans + " " + list_text_needed[iter]
                    iter += 1
                list_question_and_ans.append(" ".join(str_question_and_ans.split()))    # removing extra spaces if any
            except:
                pass

    return list_question_and_ans


# Create string of all dialogues to store in a text file for manual proof reading during development
def store_all_dialogues(list_question_and_ans):
    file_str_question_and_ans = ""
    for x in list_question_and_ans:
        file_str_question_and_ans += str(x) + "\n\n"
    text_file = open(r"extract.txt", "w")
    text_file.write(file_str_question_and_ans)
    text_file.close()

    return file_str_question_and_ans


# Find names of important company representators
def find_names_of_imp_company_representators(list_full_pdf_text):

    list_individuals = ["moderator", "ceo", "cfo", "relations"]
    list_actual_name = []

    for name in list_individuals:
        for sentence in list_full_pdf_text:
            if name in sentence.lower():
                actual_name = sentence[(len(name)+1):]
                break
            else:
                actual_name = ""
        list_actual_name.append(actual_name)

    moderator = list_actual_name[0]
    ceo = list_actual_name[1]
    cfo = list_actual_name[2]
    relations = list_actual_name[3]

    # TODO: identify and handle different edge cases

    return moderator, ceo, cfo, relations


# Break the full data string into multiple strings of maximum allowed length of a column in sql server
def preparing_data_for_db_storage(file_str_question_and_ans):
    
    file_str_question_and_ans = file_str_question_and_ans.replace("'", "")   # removing single quotes from string to avoid sql error
    qna_dict = dict()
    max_char_len = 4000    # max characters allowed in a column in sql server
    max_qnas = 12   

    len_qna = len(file_str_question_and_ans)
    if len_qna <= max_char_len:
        qna1 = file_str_question_and_ans
        qna_dict["qna1"] = qna1
    else:
        # qna1
        qna_dict["qna1"] = file_str_question_and_ans[0:max_char_len]

        # qna2 - qna12
        for x in range(2, max_qnas + 1):
            if len_qna > (x * max_char_len):
                qna_dict[f"qna{x}"] = file_str_question_and_ans[
                    (x - 1) * max_char_len: x * max_char_len
                ]
            elif max_char_len <= len_qna < x * max_char_len:
                qna_dict[f"qna{x}"] = file_str_question_and_ans[
                    (x - 1) * max_char_len: len_qna
                ]
            else:
                qna_dict[f"qna{x}"] = ""

    return qna_dict


########################################## DB Functions ##########################################


# Create connection string using DB config for SQL Server
def create_connection_string(config_obj):

    conn_str = f"""
        DRIVER={{{config_obj["DRIVER_NAME"]}}};
        SERVER={config_obj["SERVER_NAME"]};
        DATABASE={config_obj["DATABASE_NAME"]};
        Trust_Connnection=yes;
    """

    return conn_str


def db_connection(conn_str):
    try: 
        conn = odbc.connect(conn_str)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        logging.error(f"Error while connecting to DB: {e}")


# Insert data into DB part 1
def insert_data_into_db_1(compamy_name, concall_date, moderator, ceo, cfo, relations, qna_dict, db_name, conn, cursor):
    try: 
        sql1 = f"""
            INSERT INTO {db_name}.dbo.TranscriptExtract(Company_Name, Concall_Date, Moderator, ceo, cfo, relations, qna_1, qna_2, qna_3, qna_4)
            VALUES ('{compamy_name}', '{concall_date}', '{moderator}', '{ceo}', '{cfo}', '{relations}', '{qna_dict['qna1']}', '{qna_dict['qna2']}', '{qna_dict['qna3']}', '{qna_dict['qna4']}')
        """

        id_sql = f""" 
            SELECT top 1 id FROM {db_name}.dbo.TranscriptExtract
            ORDER BY id desc
        """

        cursor.execute(sql1)
        conn.commit()
        cursor.execute(id_sql)
        id = cursor.fetchone()[0]

        return id, conn, cursor
    except Exception as e:
        logging.error(f"Error while inserting data into DB: {e}")


# Insert data into DB part 2
def insert_data_into_db_2(id, qna_dict, db_name, conn, cursor):
    try:
        sql2 = f"""
            UPDATE {db_name}.dbo.TranscriptExtract
            SET qna_5 = '{qna_dict['qna5']}',
            qna_6 = '{qna_dict['qna6']}',
            qna_7 = '{qna_dict['qna7']}',
            qna_8 = '{qna_dict['qna8']}'
            WHERE id = {id}
            """
        
        sql3 = f"""
            UPDATE {db_name}.dbo.TranscriptExtract
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
    except Exception as e:
        logging.error(f"Error while inserting data into DB: {e}")
    

######################################## Utility Functions ########################################
    

# Function to read from a json config file and return a dictionary
def config_reader():
    with open("input/config.json") as json_file:
        config = json.load(json_file)

    return config

    
###################################################################################################

if __name__ == "__main__":
    main()