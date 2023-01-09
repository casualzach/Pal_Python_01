#readme for instructions

import os
from dotenv import load_dotenv
import csv
import shutil
import textwrap
import openai
from time import time,sleep
import re

# define filepath to source chat
chatpath = '../Chat_Example/_chat.txt'
#how may characters per chunk
chunksize = 6000 

load_dotenv()

openai.api_key = os.getenv('OPEN_AI_KEY')


#open the chatfile and check if the first line is the generic whatsapp encryption message
source_chat = open(chatpath,'r')
working_chat = open('../Chat_Example/workingchat.txt', 'w+')
WA_firstline="Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them."
firstline=source_chat.readline()

#first 23 characters of each line are the whatsapp timestamp, remove in working file
def removeTimestamp(file):
    source_chat.seek(0)
    lines = source_chat.readlines()
    for lines in lines:
        if lines[0] == '[' and lines[21] == ']':
            working_chat.write(lines[23:])
        else:
            working_chat.write(lines)
    working_chat.truncate()

#on fresh chats first message will appear as a whatsapp notification about their encryption; removing here
def removeWAmessage(file):
    print('now viewing working chat')
    file.seek(0)
    #print(file.readline())
    fL = file.readline()
    data = file.read()
    file.seek(0)
    file.write(data)
    file.truncate()
    return fL

def open_file(filepath):
    with open(filepath, 'r') as infile:
        return infile.read()

def save_file(content, filepath):
    with open(filepath, 'w') as outfile:
        outfile.write(content)

def gpt3_completion(prompt, engine='text-davinci-003', temp=0.4, top_p=1.0, tokens=500, freq_pen=0.0, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            #text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)



if __name__ == '__main__':
    #remove the timestamp from source chat, create working chat copy and close file
    removeTimestamp(source_chat)
    source_chat.close()

    #check if firstline of working chat is whatsapp notification and remove if necessary
    if WA_firstline in firstline:
        removeWAmessage(working_chat)
        print("Whatsapp opener removed")
    else:
    #    working_chat.close()
        print("Chat not starting at beginning")
    #working_chat.close()
    working_chat.seek(0)
    lines = working_chat.readlines()
    line_count = len(lines)
    working_chat.seek(0)
    working_chat = working_chat.read()
    char_count = len(working_chat)
    #chunks = textwrap.wrap(working_chat, 4000)
    result = list()
    count = 0 
    print('Characters in chat: ',char_count)
    print('Lines in chat: ',line_count)
    print('Char per line: ', char_count/line_count)

    #init line counters for chunk iteration
    line_start = 0
    line_end = 0
    
    #create chunks by line ensuring we pass a max of {chunksize} characters (+ line overhang)
    while line_end < line_count:
        chars = 0
        while chars < chunksize and line_end < line_count:
            chars = chars + len(lines[line_end])
            line_end+=1

        #print('start: ', line_start,' end: ', line_end)

        chunk = " "
        chunk = chunk.join(lines[line_start:line_end])

        line_start = line_end + 1

        print(trun(line_end/line_count*100))
        prompt = open_file('prompt.txt').replace('<<Chat>>', chunk)
        summary = gpt3_completion(prompt)
        result.append(summary)
    save_file('\n\n'.join(result), './output/output_%s.txt' % time())


   
