import json
import os

filename = 'my_films.json'


def write_json(data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


if not os.path.exists('./my_films.json'):
    empty_j = {'films': []}
    write_json(empty_j)


with open(filename, 'r') as uptodatefilms:
    outfilms = json.load(uptodatefilms)
allnames = []

for k in outfilms['films']:
    allnames.append(str(k['name']))


def add_film(title):
    film = {'films': []}
    film['films'].append({
        'name': title,
        'status': 'todo'
    })

    if os.stat(filename).st_size != 0:
        temp = outfilms['films']
        for p in film['films']:
            temp.append(p)
        write_json(outfilms)

    else:
        write_json(film)


def status(view):
    if os.stat(filename).st_size != 0:
        for i in outfilms['films']:
            if view == str(i['status']):
                print('{} : {}'.format(str(i['name']), str(i['status'])))
            elif view == 'all':
                print('{} : {}'.format(str(i['name']), str(i['status'])))
    else:
        print('No films yet. Please add!')


def remove_film(filmtitle):

    if filmtitle in allnames:
        for i in outfilms['films'][:]:
            if str(i['name']) == filmtitle:
                outfilms['films'].remove(i)
        write_json(outfilms)
        print('"{}" has been removed!'.format(filmtitle))

    else:
        print('"{}" does not exists!'.format(filmtitle))


def edit_title(filmtitle):

    if filmtitle in allnames:
        newName = None
        for i in outfilms['films']:
            if str(i['name']) == filmtitle:
                print('Name: {}'.format(str(i['name'])))
                newName = input('Enter new name: ')
                i['name'] = newName
        write_json(outfilms)
        print('"{}" has been edited to "{}"!'.format(filmtitle, newName))

    else:
        print('"{}" does not exists!'.format(filmtitle))


def change_status(filmtitle):

    if filmtitle in allnames:
        newStatus = None
        for i in outfilms['films']:
            if str(i['name']) == filmtitle:
                if str(i['status']) == 'todo':
                    i['status'] = 'done'
                elif str(i['status']) == 'done':
                    i['status'] = 'todo'
                newStatus = str(i['status'])
        write_json(outfilms)
        print('"{}"`s status has been changed to "{}"!'.format(filmtitle, newStatus))

    else:
        print('"{}" does not exists!'.format(filmtitle))


def entry():
    status('all')
    action = input('\nPlease chose an action :'
                   '\ncheck todo'
                   '\ncheck done'
                   '\nadd film'
                   '\nremove film'
                   '\nedit film'
                   '\nstatus\n: ')

    if action == 'check done':
        status('done')

    elif action == 'check todo':
        status('todo')

    elif action == 'add film':
        filmTitle = input("Title: ")
        add_film(filmTitle.title())
        print('Film "{}" has been added!\n'.format(filmTitle.title()))

    elif action == 'remove film':
        toRemoveFilm = input("Title to remove: ")
        remove_film(toRemoveFilm.title())

    elif action == 'edit film':
        toEditTitle = input("Title to edit: ")
        edit_title(toEditTitle)

    elif action == 'status':
        toEditTitle = input("Title to change status: ")
        change_status(toEditTitle)

    else:
        print('Wrong action!')


entry()
