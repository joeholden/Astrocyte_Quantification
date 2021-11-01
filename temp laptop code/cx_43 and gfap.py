import os

list_of_docs = []
list_related_docs = []

for doc in sorted(os.listdir('Area_Excel')):
    if 'With_Zeros' in doc:
        list_of_docs.append(doc.strip('.xlsx'))
    # Naming scheme for binaries... either cx43_binary_# or gfap_binary_#

# for entry, position in enumerate(list_of_docs):

x = enumerate(list_of_docs)
print(list(x))

for index, stripped_filename in x:
    animal_number = stripped_filename.split('_')[2]
    related = []
    for i, s_f in x:
        if animal_number == s_f.split('_')[2]:
            related.append(i, s_f)

    print(related)
    print('yuh')


print(list_of_docs[1].split('_'))





# or just sort the whole fucking thing and hard code take adjacent samples. You know they are related.
