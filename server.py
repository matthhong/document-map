from flask import Flask, send_from_directory, request
import csv
import json
import random
import os.path
import string
import pandas as pd
import spacy

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


app = Flask(__name__)

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)




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



if __name__ == "__main__":
    app.run(debug=True, port=8999)