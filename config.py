def conf_to_dict(file_path_conf):
    '''open config.txt and get parameters to dict'''
    configuration = {}
    with open(file_path_conf) as file:
        while (temp:=file.readline()):
            temp = temp.replace('\n','')
            temp = temp.replace(' ', '')
            temp = temp.lower().split('=')
            configuration[temp[0]] = temp[1]
    return configuration