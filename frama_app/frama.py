import subprocess
from django.conf import settings
from .models import *
from django.db.models import Q


main_command = ['frama-c', '-wp', '-wp-print', "-wp-log=r:result.txt"]
delimiter = '------------------------------------------------------------'


def get_frama_output_as_list(file, prover, conditions):
    command = main_command.copy()
    if prover:
        command.append('-wp-prover')
        command.append(prover)
    for c in conditions:
        command.append('-wp-prop=@' + c)
    command.append(str(settings.MEDIA_ROOT) + '/'+ file.name)
    print("Running frama-c with command:")
    print(command)
    p = subprocess.run(command, capture_output=True, text=True)
    try :
        with open(str(settings.BASE_DIR) + "/result.txt") as f:
            file.frama_output = f.read()
    except:
        file.frama_output = 'Error when opening file'
    file.save()
    section_list = p.stdout.split(delimiter)
    section_list.pop(0)
    return section_list


def update_frama_output(file, prover = None, conditions = []):
    section_list = get_frama_output_as_list(file, prover, conditions)
    used_lines = set()
    for s in section_list:
        words = s.split()
        # if not words or words[0] == 'Function':
        #     continue
        
        index = 0
        try:
            index = words.index('line')
        except:
            continue
        line_num = words[index+1]
        line_num = int(line_num[:line_num.index(')')])
        if line_num in used_lines:
            continue
        used_lines.add(line_num)
        section = None
        try:
            section = Section.objects.get(line=line_num, file=file)
        except:
            continue
        words.reverse()
        index = words.index('returns')
        section.status_data = StatusData(data=s, user=file.owner)
        section.status_data.save()
        section.status = Section.Status[words[index-1].upper()]
        section.save()
    
    emptySections = Section.objects.filter(~Q(line__in=used_lines), file=file)

    for s in emptySections:
        if s.status_data:
            s.status_data.data = ''
            s.status_data.save()
        

def get_sections_for_output(file):
    sections = list()
    section_list = Section.objects.filter(file = file)
    for s in section_list:
        if s.status_data and s.status_data.data:
            sections.append((s.status_data.data, s.status))

    return sections
    

def create_sections(file):
    content = None
    file.file_object.seek(0)
    try:
        content = file.file_object.readlines()
    except:
        return None

    sections = list()
    i = 0
    inside_section = False
    curr_section = None
    for line in content:
        i += 1
        line = line.decode()#[:-1]
        if not inside_section:
            index = line.find('@ ')
            if index == -1:
                continue
            words = line[index+1:].split()
            category = words[0] if words[0] != 'loop' else words[1]
            curr_section = Section (
                date_created = file.date_created,
                category = Section.Category[category.upper()],
                line = i,
                file = file
            )
            inside_section=True
           
        if line.find(';') is not -1:
            inside_section = False
            sections.append(curr_section)

    return sections
        
        
