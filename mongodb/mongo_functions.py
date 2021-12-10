from pymongo import MongoClient
from pprint import pprint

class DB:
  def __init__(self, ip='127.0.0.1', port=27017, database='test_database'):
    self.client = MongoClient( 'mongodb://{}:{}/'.format(ip, port))
    self.knowledge_base = self.client[database]

  def add(self, theme, element):
    result = self.knowledge_base[theme].insert_one(element)
    return result.inserted_id

  def delete(self, theme, element):
    self.knowledge_base[theme].delete_one(element)

  def show(self, theme):
    for obj in list(self.knowledge_base[theme].find({})):
      print(obj)

  def clear(self, theme):
    for obj in list(self.knowledge_base[theme].find({})):
      self.delete(theme=theme, element=obj)

  def find(self, theme, named_entities, answer_field):
    tmp = answer_field
    answer_field = dict()
    for element in tmp:
      answer_field[element] = 1
    answer_field['_id'] = 0
    
    out = []
    if named_entities != {}:
      for key in named_entities.keys():
        if isinstance(named_entities[key], list):
          for element in named_entities[key]:
            out.append({key : element})
        else:
          out.append({key : named_entities[key]})

      named_entities = {'$and' : out}

    
    result = list(self.knowledge_base[theme].find(named_entities, answer_field))
    return result

  def find_manual(self, theme, named_entities, answer_field):
    tmp = answer_field
    answer_field = dict()
    for element in tmp:
      answer_field[element] = 1
    answer_field['_id'] = 0
    
    result = list(self.knowledge_base[theme].find(named_entities, answer_field))
    return result


if __name__ == '__main__':
  db = DB(ip='192.168.0.1', port=27017, database='test_database')
  theme = 'test_theme'
  
  test_info = [{'data_1' : '0',
                'data_2' : [1, 2, 3]},
               {'data_1' : '1',
                'data_2' : [7, 4, 8]}
               {'data_1' : '2',
                'data_2' : [9, 10, 11]}]
               

  db.clear(theme) 
  for i in test_info:
    db.add(theme=theme, element=i)

  print('data_1 == 0')
  named_entities = {'data_1' : '0'}
  answer_field = ['data_2']
  answer = db.find_manual(theme = theme,
                named_entities = named_entities,
                answer_field = answer_field)
  pprint(answer)


  print('data_1 more than 0 and less than 2')
  named_entities = {'data_1' : {'$lt' : 0, '$gt' : 2}}
  answer_field = ['data_2']
  answer = db.find_manual(theme = theme,
                named_entities = named_entities,
                answer_field = answer_field)
  pprint(answer)


