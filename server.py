from flask import Flask, send_from_directory, request
import csv
import json
import random
import os.path
import string
# import gspread
import pandas as pd
import spacy
from model.modeling import run_multilayer

def clean_string(content):
    cleaned = content.lower()
    tokenized = sp(cleaned)

    stop = ['PRON', 'AUX', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART', 'NUM', 'X', 'INTJ', 'PUNCT']
    return list(filter(lambda w: w != '', 
                       map(lambda w: w.lemma_ if (
                               (w.pos_ not in stop and len(w.text) > 1 and not w.lex.is_stop)
                                   ) else '', 
                           tokenized)))

sp = spacy.load('en_core_web_sm')
# from model import modeling

# gc = gspread.oauth()
# spread = gc.open_by_key('1aKISSDBa3o0wPoSOqmFkbkQNNx18A1h8uZY0IRfUfKk')


class atdict(dict):
    __getattr__= dict.__getitem__
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__


class Spreadsheet:
    """
    Instantiate a spreadsheet object to interface with gspread

    If csvfile exists: read-only
    """

    def __init__(self, gid=None, csvfile=None):
        """
        gid: at the end of sheet url
        """
        self.gid = gid
        self.csvfile = csvfile

        if self.gid is not None:
            # self.table = spread.get_worksheet_by_id(self.gid)
            pass

        elif self.csvfile is not None:
            self.table = None

        # doc_tag_table, etc.
        self.relationships = {}

    def column(self, column_names, filter_pks=None):
        """
        Returns rows given column_names, which can be either:
            1. an integer
            2. a string, containing the column header name
            3. or a list of either
        """
        if type(column_names) is not list:
            column_names = [column_names]
        if filter_pks is not None: 
            if type(filter_pks) is not list:
                filter_pks = [filter_pks]
            filter_pks = [str(pk) for pk in filter_pks]

        all_columns = []
        
        if self.gid is not None:
            # gspread object
            all_cells = self.table.get_all_values()
            pivot_table = list(zip(*all_cells))

            pks = pivot_table[0][1:]
            header = all_cells[0]

            for column_name in column_names:
                if type(column_name) == int:
                    column = pivot_table[column_name - 1][1:]
                elif type(column_name) == str:
                    column = pivot_table[header.index(column_name)][1:]
                else:
                    raise ValueError("column_name must be an integer or a string")

                if filter_pks is not None:
                    column = [c for i, c in enumerate(column) if pks[i] in filter_pks]
                
                all_columns.append(column)

                    
        elif self.csvfile is not None:
            # csv object
            if type(column_names[0]) != str:
                raise ValueError("To read from CSV files, you must provide string-type column names")

            # if filter_pks is None:
            #     raise ValueError("To read from CSV files, you must filter by primary keys")

            with open(self.csvfile, 'r', newline='') as f:
                reader = csv.DictReader(f)

                for i in range(len(column_names)):
                    all_columns.append([])
                
                for line in reader:
                    if (filter_pks is None or line['id'] in filter_pks):
                        for i, col in enumerate(column_names):
                            all_columns[i].append(line[col])
        
        if not any(all_columns):
            return []

        if len(all_columns) == 1:
            return all_columns[0]

        if filter_pks is not None:
            if len(filter_pks) == 1 and len(all_columns) > 1:
                return [inner for outer in all_columns for inner in outer]
        
        return all_columns

    __call__ = column

    def set_relationship(self, name, spreadsheet2, manytomany=None):
        """
        Define related and/or join tables
        """
        self.relationships[name] = [spreadsheet2, manytomany]

    def get_relationship(self, name, pk, column_names):
        """
        Retrieves related objects given the primary object id
        """
        related_table = self.relationships[name][0]
        join_table = self.relationships[name][1]

        # breakpoint()

        if type(pk) is not list:
            pk = [pk]
        
        if join_table:
            related_table.merge(join_table, left_on='id', right_on='')\
                .merge(self.table.merge(join_table), on='id_high')\
                .groupby(['Example_x','Example_y'])['id_high'].agg(list)\
                .reset_index()

        all_related_pks = []
        for (origin_pk, related_pk) in zip(*join_table([2,3])):
            if origin_pk in pk:
                all_related_pks.append(related_pk)

        result = related_table(column_names, all_related_pks)
    
        return result

    def update_relationship(self, name, pk1, pk2, prev_pk1=None, update=False):
        """
        Creates an entry in the join table
        """
        join_table = self.relationships[name][1]
        # row_id = 0
        for x, y in zip(*join_table([2,3])):
            if x == pk1 and y == pk2:
                return "Join entry already exists for this pair"
            
            # if update:
            #     if prev_pk1 == None:
            #         # delete cell
            #         print('delete cell')
            #     else:
            #         if x == prev_pk1 and y == pk2:
            #             breakpoint()
            #             return join_table.update_row('category_id', str(row_id), pk1)
            # row_id += 1


        return join_table.post_row([pk1, pk2])

    def post_row(self, new_row):
        """
        Given an array, places the data in the table with an incremented primary key
        """
        str_list = list(filter(None, self.table.col_values(1)))
        row_num = len(str_list)+1

        self.table.update_cell(row_num, 1, row_num-2)
        for i, content in enumerate(new_row):
            self.table.update_cell(row_num, i+2, content)
        
        return str(row_num-2)

    def update_row(self, name, pk, new_data):
        """
        Given a primary key and array, updates row at key with new data
        """
        col_names = list(filter(None, self.table.row_values(1)))

        if name not in col_names:
            return "Give valid column to update"
        col_num = col_names.index(name) + 1

        str_list = list(filter(None, self.table.col_values(1)))
        row_num = str_list.index(str(pk)) + 1

        self.table.update_cell(row_num, col_num, new_data)

        return pk



doc_table = Spreadsheet(csvfile='client/data/doc_table.csv')
# code_table = Spreadsheet(292312135)
# category_table = Spreadsheet(15450054)
# highlight_table = Spreadsheet(1521788917)
# tag_table = Spreadsheet(28265543)

# doc_tag_table = Spreadsheet(720580560)
# doc_table.set_relationship('tag', tag_table, doc_tag_table)

# doc_code_table = Spreadsheet(628713232)
# doc_table.set_relationship('code', code_table, doc_code_table)

# doc_highlight_table = Spreadsheet(1976914557)
# doc_table.set_relationship('highlight', highlight_table, doc_highlight_table)

# highlight_code_table = Spreadsheet(1131558209)
# highlight_table.set_relationship('code', code_table, highlight_code_table)

# category_code_table = Spreadsheet(0)
# category_table.set_relationship('code', code_table, category_code_table)

# removed_word_topics = Spreadsheet(1209028090)


app = Flask(__name__)

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


# @app.route("/run_model", methods=["POST"])
# def run_model():
#     """
#     Get all the model data
#     """
#     codeinfo = []
#     p1 = pd.DataFrame(code_table.table.get_all_records())
#     p2 = pd.DataFrame(category_table.table.get_all_records())
#     pm = pd.DataFrame(category_code_table.table.get_all_records())
    
#     try:
#         p1.iloc[0]
#     except:
#         return ('', 204)

#     codes = p2.merge(p1.merge(pm, left_on="id", right_on="code_id", how="outer"), left_on="id", right_on="category_id", how="outer")
#     codes = codes.fillna('').to_dict(orient='records')

#     # get doc_id, highlighted segment, and related codes
#     for c in codes:
#         if int(c["category_id"]) != 0:
#             codeinfo.append([c["category"], c['code']])
    
#     breakpoint()

#     run_multilayer(codeinfo, p1[['code','words']].to_numpy().tolist())
#     return ('', 201)
        


@app.route("/strip", methods=["POST"])
def get_stripped_text():
    """
    Normalize text data for algorithms
    """
    payload = request.get_json()
    # breakpoint()

    # if type(payload) == list:
    #     output = [content.lower().translate(str.maketrans('','', string.punctuation)).split(sep=None) for content in payload]
    # elif type(payload) == str:
    #     output = payload.lower().translate(str.maketrans('','', string.punctuation)).split(sep=None)
    cleaned = payload.lower()
    tokenized = sp(cleaned)

    stop = ['PRON', 'AUX', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PART', 'NUM', 'X', 'INTJ', 'PUNCT']
    return json.dumps({'content': list(filter(lambda w: w != '', 
                       map(lambda w: w.lemma_ if (
                               (w.pos_ not in stop and len(w.text) > 1 and not w.lex.is_stop)
                                   ) else '', 
                           tokenized)))
    })
        
    # return json.dumps({'content': output})

# @app.route("/model")
# def get_model():
#     modeling.run_model()

### TO DO: allow user to upload or manually input file name from the tool or create functionality to switch between files
### TO DO: allow user to specify if tags already exist in raw data
@app.route("/createtables", methods=['POST'])
def createtables():
    """
    READ data file containing textual data
    CREATE/WRITE to doc_table.csv file, id title text
    CREATE (/WRITE if tags given) to tag_table.csv file, header (and given tags if they exist)
    CREATE (/WRITE if tags given) to doc_tag_table.csv file header (and any given relationships)

    current assumption: no tags given
    """
    # open text data file and save contents
    
    doc_data = []
    clean_texts = []
    with open('client/data/simplyrecipes.csv', 'r', newline='') as f:
        reader = csv.DictReader(f)
        
        i = 0
        for line in reader:
            doc_data.append({'id': i, 'title': line['name'], 'content': line['description']})
            i += 1

            # clean_texts.append(clean_string(line['description']))
    
    # create / write to doc_table.csv
    # with open('client/data/clean_texts.json', 'w', newline='') as f:
    #     json.dump(clean_texts, f)

    return "Successfully created csv files!"
    


@app.route("/text/<doc_id>")
def get_text(doc_id):
    """
    READ data from doc_table.csv, save and return title and content of entry where id == doc_id
    """
    doctext = {'title': 'No title found', 'content': 'No file found :('}

    result = doc_table(['title', 'content'], filter_pks=doc_id)

    doctext['title'] = result[0]
    doctext['content'] = result[1]
    
    return json.dumps(doctext)


@app.route("/titles/")
def get_titles():
    """
    READ data from doc_table.csv, save and return title and content of entry where id == doc_id
    """
    result = doc_table(['title'])
    
    return json.dumps(result)

# @app.route("/codes/")
# def get_codes():
#     """
#     READ data from doc_table.csv, save and return title and content of entry where id == doc_id
#     """
#     result = code_table(['id', 'code'])

#     codes = []
#     if len(result) != 0:
#         codes = result
    
#     return json.dumps(codes)



@app.route("/texts/<term>")
def get_search_results(term):
    """
    READ data from doc_table.csv, save and return title and content of entry where id == doc_id
    """
    queried = []
    with open('client/data/doc_table.csv', 'r', newline='') as f:
        reader = csv.DictReader(f)
        for line in reader:
            if term in line['content']:
                queried.append(line['id'])
    
    return json.dumps(queried)

    
@app.route("/documenthead")
def get_textsection():
    result = doc_table(['id', 'title', 'content'])

    doc_ids = result[0]
    titles = result[1]
    content = result[2]

    head = []
    for i in range(len(doc_ids)):
        if len(content[i]) < 1000:
            head.append({'id': doc_ids[i], 'title': titles[i], 'head': content[i]})
        else:
            head.append({'id': doc_ids[i], 'title': titles[i], 'head': content[i][0:1000] + '...'})

    return json.dumps(head)


@app.route("/tags/<doc_id>")
def get_doc_tags(doc_id):
    """
    READ doc_tag_table.csv, save tag_id for every row with doc_id == given doc_id into list
    READ tag_table, append name of tag for every tag_id in list from previous step
    return list of tags as json
    """
    if doc_id == "all":
        result = tag_table(['id', 'tag'])
        return json.dumps([{'id': result[0][i], 'tagname': result[1][i]} for i in range(len(result[0]))])

    doc_tags = doc_table.get_relationship('tag', doc_id, 'tag')
    
    return json.dumps(doc_tags)


# @app.route("/getdoccodetable")
# def get_doctagtable():
#     result = doc_code_table(["doc_id", "code_id"])

#     doc_code = []
#     if len(result) != 0:
#         doc_code = [{'doc_id': result[0][i], 'code_id': result[1][i]} for i in range(len(result[0]))]
    
#     return json.dumps(doc_code)



# @app.route("/addtag/<doc_id>/<new_tag>", methods = ['POST'])
# def add_tag(doc_id, new_tag):
#     """
#     READ tag_table.csv check if tag already exists, if exists, do nothing save exists to TRUE -> save tag_id, 
#     else APPEND new tag to end of file: id, name -> save tag_id
#     if exists is TRUE, READ doc_tag_table.csv, if relationship exists, do nothing, else APPEND to end of file: id, doc_id, tag_id
#     else (exist is FALSE) APPEND to end of file: id, doc_id, tag_id
#     """

#     tag_id = tag_table.post_row([new_tag])
#     doc_table.update_relationship('tag', doc_id, tag_id)

#     return "Tag and edge tables updated!"
                


# @app.route("/addcodehighlight", methods = ['POST'])
# def add_code():
#     """
#     READ highlight table, get last highlight id
#     WRITE to highlight table, add new highlight to the end, id = last_highlight_id + 1
#     READ code table, check if code already exists, if exists get code_id,
#     WRITE if not exists add to end and assign code_id

#     WRITE to doc-highlight table new entry
#     WRITE to highlight-code table new entry
#     WRITE to doc-code table new entry
#     """
#     data = json.loads(request.data.decode('utf-8'))
#     highlight_id = data['id']
#     doc_id = data['doc_id']
#     codes = data['codes']
#     highlight = data['highlight']
#     memo = data['memo']
#     words = data['words']

#     if highlight_id == -1:
#         highlight_id = highlight_table.post_row([highlight[0], highlight[1], memo, doc_id])
#         doc_table.update_relationship('highlight', doc_id, highlight_id)
#     else:
#         highlight_table.update_row('memo', highlight_id, memo)

#     existing_codes = code_table(['id', 'code', 'words'])

#     # joined_rows = highlight_code_table(['highlight_id', 'code_id'])
#     for new_code in codes:
#         if len(existing_codes) <= 0 or new_code not in existing_codes[1]:
#             code_words = list(set(words))
#             code_id = code_table.post_row([new_code, "", ",".join(code_words)])
#             category_code_table.post_row([0, code_id])
#         else:
#             code_id = existing_codes[0][existing_codes[1].index(new_code)]
#             # breakpoint()
#             code_words = list(set(existing_codes[2][existing_codes[1].index(new_code)].split(",") + words))
#             code_table.update_row('words', code_id, ",".join(code_words))
        
#         # if code_id not in joined_rows[1]:
#         highlight_table.update_relationship('code', highlight_id, code_id)    
#         doc_code_table.post_row([doc_id, code_id, 1])
        
#         # need to add case where code is deleted
#     return "Highlight codes memo added"



# @app.route("/removewordtopic/<word_topic_id>", methods = ['GET', 'POST'])
# def removetopic(word_topic_id):
#     if request.method == 'POST':
#         # assume that the word_topic_id has not already been added
#         removed_word_topics.post_row([word_topic_id])
            
#     if request.method == 'GET':
#         return json.dumps(removed_word_topics(2))

#     return "done!"




# @app.route("/gethighlightinfo")
# def get_highlightinfo():
#     highlightinfo = []

#     p1 = pd.DataFrame(highlight_table.table.get_all_records())
#     p2 = pd.DataFrame(code_table.table.get_all_records())
#     pm = pd.DataFrame(highlight_code_table.table.get_all_records())

#     try:
#         p2.iloc[0]
#     except:
#         return json.dumps([])

#     highlights = p2.merge(p1.merge(pm, left_on="id", right_on="highlight_id"), left_on="id", right_on="code_id")\
#         .groupby(['highlight_start', 'highlight_end', 'memo_y', 'doc_id'])['code']\
#         .agg(list).reset_index().to_dict(orient='records')

#     # get doc_id, highlighted segment, and related codes
#     for h in highlights:
#         doc_id = h['doc_id']

#         document = doc_table(
#             ['title', 'content'], 
#             doc_id
#         )
#         # breakpoint()
#         hobj = {
#             "highlight": document[1][int(h['highlight_start']):int(h['highlight_end'])], 
#             "doc_title": document[0],
#             "doc_id": doc_id,
#             "start_idx": h['highlight_start'],
#             "end_idx": h['highlight_end'],
#             "codes":     h['code'],
#             "memo":      h['memo_y']
#         }
        
#         highlightinfo.append(hobj)
#     # breakpoint()

#     return json.dumps(highlightinfo)



# @app.route("/addcodecategory", methods = ['POST'])
# def add_codecategory():
#     data = json.loads(request.data.decode('utf-8'))

#     code_id = str(data['code_id'])
#     code_name = data['code_name']
#     category = data['category']
#     category_id = str(data['category_id'])
#     memo = data['memo']
#     update_cat = data['update']

#     # check if category has changed
#     if update_cat and category:
#         # If new category entered, create new entry in category_table
#         if (category_id == "-1"):
#             category_id = category_table.post_row([category])

#         # check if code is already assigned to category, change relationship if true, create new if false
#         joined_rows = category_code_table(['id', 'category_id', 'code_id'])
#         if code_id in joined_rows[2]:
#             category_code_table.update_row('category_id', joined_rows[0][joined_rows[2].index(code_id)], category_id)
#         else:
#             category_table.update_relationship('code', category_id, code_id)

#     # update code memo
#     code_table.update_row('memo', code_id, memo)
#     code_table.update_row('code', code_id, code_name)

#     return "code category added!"




# @app.route("/getcodeinfo")
# def get_codeinfo():
#     codeinfo = []

#     p1 = pd.DataFrame(code_table.table.get_all_records())
#     p2 = pd.DataFrame(category_table.table.get_all_records())
#     pm = pd.DataFrame(category_code_table.table.get_all_records())
    
#     try:
#         p1.iloc[0]
#     except:
#         return json.dumps([])

#     codes = p2.merge(p1.merge(pm, left_on="id", right_on="code_id", how="outer"), left_on="id", right_on="category_id", how="outer")
#     codes = codes.fillna('').to_dict(orient='records')

#     # get doc_id, highlighted segment, and related codes
#     for c in codes:
#         if c['code'] != '':
#             cobj = {
#                 "id": c["id_x"], 
#                 "code": c['code'],
#                 "category": c["category"],
#                 "category_id": c["category_id"],
#                 "memo": c["memo"],
#                 "words": c["words"]
#             }
        
#             codeinfo.append(cobj)

#     return json.dumps(codeinfo)


# @app.route("/getcategories")
# def get_categories():
#     category_info = []
#     categories = category_table(["id", "category"])

#     if len(categories) != 0:
#         for id, category in zip(categories[0], categories[1]):
#             category_info.append({"id": id, "text": category})

#     return json.dumps(category_info)


# @app.route("/getdocinfo/<doc_id>")
# def get_docinfo(doc_id):
#     doc_tags = doc_table.get_relationship('tag', doc_id, 'tag')
#     doc_highlights = doc_table.get_relationship('highlight', doc_id, 'highlight_start')

#     doc_info = {"doc_id": doc_id, "tags": doc_tags, "highlights": len(doc_highlights)}

    
#     return json.dumps(doc_info)


if __name__ == "__main__":
    app.run(debug=True, port=8999)