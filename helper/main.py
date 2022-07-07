
database = dict()

from basic_functions import database as db1

database.update(db1)

def find(s): 
    for key, element in database.items():
        if s in key:
            for k, text in element.items():
                print('{}: \n{}'.format(k, text))
            print('_________________________________')



if __name__ == '__main__':
    s = ''
    while s != 'q':
        s = input('\nAsk for help: ')
        print('Results:\n')
        find(s)
        print('#################################')
