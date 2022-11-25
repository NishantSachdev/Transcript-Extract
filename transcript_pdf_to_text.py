path = r"{pdf_file_path}"

# Using pymupdf
import fitz  

# Extract text page by page
with fitz.open(path) as doc:
    text_list = []
    no = 0
    for page in doc:
        page_text = page.get_text("text")
        list_page_text = page_text.split('\n')
        # remove header/footer of a page. The lines of header/footer changes from pdf to pdf. So this is not generic 
        del list_page_text[0:2]
        del list_page_text[-2:]
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
    if ':' in x:
        try:
            iter = num + 1
            str_question_and_ans = x
            while ':' not in list_text_needed[iter]:
                str_question_and_ans = str_question_and_ans + list_text_needed[iter]
                iter += 1
            list_question_and_ans.append(str_question_and_ans)
        except:
            pass

# Print dialogues
file_str_question_and_ans = ""
for x in list_question_and_ans:
    file_str_question_and_ans += str(x) + "\n"
    print(x)
    print("\n")

# Write string to file
text_file = open(r"{path_for_a_text_file}", "w")
n = text_file.write(file_str_question_and_ans)
text_file.close()

