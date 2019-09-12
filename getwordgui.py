# Program to launch a GUI app where a user can enter a word to be requested and called from a dictionary/thesaurus API
# Will have interactive functions and widgets to thoroughly explore returned information

import tkinter
import tkinter.messagebox
import json
import urllib.request
# import pygame

# using a global dictionary for the main API response, to avoid making the same call multiple times for each individual
# widget callback function, since they are specific enough that one callback function cannot manage all variables
# and all changes in variables that could happen in the main window.
global respdict


# Function for making the main request to the Oxford Dictionary API, using my account credentials
def callapi():
    # setting up request for dictionary api
    appkey = "527c5d29e9802b72a92663bad9b8c3f6"
    appid = "14631769"

    header = {'app_id': appid, 'app_key': appkey}

    word = invar.get()
    word = word.lower()

    # loop to format white spaces in case any are included
    for index in range(0, len(word)):
        if word[index] == ' ':
            word = word[:index] + '_' + word[index+1:]

    # using Oxfords Lemmas request to make sure we have a 'findable' word (or root of word)
    # to make dictionary request with
    lemmaurl = "https://od-api.oxforddictionaries.com/api/v2/lemmas/en/" + word
    lemmareq = urllib.request.Request(lemmaurl, data=None, headers=header)

    # try-except block for making the actual call to the api; used to avoid the program crashing if there is an error.
    try:
        lemmares = urllib.request.urlopen(lemmareq)

    except Exception as err:
        tkinter.messagebox.showerror("Error", str(err))

    else:
        if lemmares.getcode() != 200:
            tkinter.messagebox.showerror("Error", "Response error: " + lemmares.getcode())

        else:
            resp = lemmares.read()
            resp = resp.decode("utf-8")
            lemmadict = json.loads(resp)
            word = lemmadict["results"][0]["lexicalEntries"][0]["inflectionOf"][0]["text"]
            print(word)

            url = "https://od-api.oxforddictionaries.com/api/v2/entries/en-gb/" + word
            wordreq = urllib.request.Request(url, data=None, headers=header)

            # try-except block for making the second call to the api
            try:
                wordres = urllib.request.urlopen(wordreq)

            except Exception as err:
                tkinter.messagebox.showerror("Error", str(err))

            else:
                if wordres.getcode() != 200:
                    tkinter.messagebox.showerror("Error", "Response error: " + wordres.getcode())

                else:
                    # reading api response into a processable python dictionary object
                    response = wordres.read()
                    response = response.decode("utf-8")
                    global respdict
                    respdict = json.loads(response)

                    count = 0

                    # shorthand to help with the length of the nested dictionary key references
                    res = 'results'
                    le = 'lexicalEntries'
                    ens = 'entries'
                    sen = 'senses'
                    defs = 'definitions'

                    # the final string that will be sent to the output box
                    textblock = respdict[res][0]["id"] + "\n\n"

                    # loop to check for any etymology information included in response
                    if 'etymologies' in respdict[res][0][le][0][ens][0]:
                        textblock += "Etymology:\n\n" + respdict[res][0][le][0][ens][0]["etymologies"][0] +\
                                    "\n\nDefinitions:\n"

                        # loop to find every instance of a definition and it's related examples in each list entry within
                        # the larger response dictionary
                        for index in range(0, len(respdict[res][0][le])):
                            if 'entries' in respdict[res][0][le][index]:
                                count += 1
                                textblock += "\n" + str(count) + ". " + \
                                         respdict[res][0][le][index]["lexicalCategory"]["text"] + ": " + \
                                         respdict[res][0][le][index][ens][0][sen][0][defs][0] + "\n"
                                if "examples" in respdict[res][0][le][index][ens][0][sen][0]:
                                    for i in range(0, len(respdict[res][0][le][index][ens][0][sen][0]["examples"])):
                                        if 'text' in respdict[res][0][le][index][ens][0][sen][0]["examples"][i]:
                                            textblock += "\tExample: " +\
                                                     respdict[res][0][le][index][ens][0][sen][0]["examples"][i]["text"]\
                                                     + "\n"

                    defout.set(textblock)

                # resetting the optional word list output boxes, so every time a new word is searched,
                # there is no residual information from the previous call
                synout.set("")
                antout.set("")
                rhyout.set("")


# Function to handle case changes from the radio buttons
def casechange():
    # importing all current displayed text
    textblock2 = defout.get()
    textblock3 = synout.get()
    textblock4 = antout.get()
    textblock5 = rhyout.get()

    if casevar.get() == 2:
        # switching all displayed text to lower case
        textblock2 = textblock2.lower()
        textblock3 = textblock3.lower()
        textblock4 = textblock4.lower()
        textblock5 = textblock5.lower()
    elif casevar.get() == 3:
        # switching all displayed text to upper case
        textblock2 = textblock2.upper()
        textblock3 = textblock3.upper()
        textblock4 = textblock4.upper()
        textblock5 = textblock5.upper()
    elif casevar.get() == 1:
        # returning definition text to sentence case - all lower except after a new line, a '-' or a list number
        for index in range(0, len(textblock2)):
            if index == 0:
                textblock2 = textblock2[0].upper() + textblock2[1:]
                continue
            elif index != len(textblock2)-1:
                if textblock2[index].isalpha() and (textblock2[index-1] == '\n' or textblock2[index-1] == '\t' or
                                                    ((textblock2[index-2] == ':' or textblock2[index-2] == '.') and
                                                        textblock2[index-1] == ' ')):
                    textblock2 = textblock2[:index] + textblock2[index].upper() + textblock2[index+1:]
                else:
                    textblock2 = textblock2[:index] + textblock2[index].lower() + textblock2[index+1:]
            else:
                continue

        # returning synonym list to sentence case - all lower except first letter of every word
        if textblock3 != "":
            textblock3 = textblock3[0].upper() + textblock3[1:]
            for index2 in range(1, len(textblock3)):
                if index2 < len(textblock3):
                    if textblock3[index2-1] == '\n':
                        textblock3 = textblock3[:index2] + textblock3[index2].upper() + textblock3[index2+1:]
                    else:
                        textblock3 = textblock3[:index2] + textblock3[index2].lower() + textblock3[index2+1:]
                else:
                    continue

        # returning antonym list to sentence case - all lower except first letter of every word
        if textblock4 != "":
            textblock4 = textblock4[0].upper() + textblock4[1:]
            for index3 in range(1, len(textblock4)):
                if index3 < len(textblock4):
                    if textblock4[index3-1] == '\n':
                        textblock4 = textblock4[:index3] + textblock4[index3].upper() + textblock4[index3+1:]
                    else:
                        textblock4 = textblock4[:index3] + textblock4[index3].lower() + textblock4[index3 + 1:]
                else:
                    continue

        # returning rhyme list to sentence case - all lower except first letter of every word
        if textblock5 != "":
            textblock5 = textblock5[0].upper() + textblock5[1:]
            for index4 in range(1, len(textblock5)):
                if index4 < len(textblock5):
                    if textblock5[index4-1] == '\n':
                        textblock5 = textblock5[:index4] + textblock5[index4].upper() + textblock5[index4+1:]
                    else:
                        textblock5 = textblock5[:index4] + textblock5[index4].lower() + textblock5[index4 + 1:]
                else:
                    continue
    else:
        tkinter.messagebox.showerror("Option Error", "Error with Radiobutton options. Please restart program.")

    # sending newly-cased text back to the output boxes
    defout.set(textblock2)
    synout.set(textblock3)
    antout.set(textblock4)
    rhyout.set(textblock5)


# Function to call, format, and output the synonym and antonym lists
def wordlists(listopt):
    # formatting and data for api call
    appkey = "527c5d29e9802b72a92663bad9b8c3f6"
    appid = "14631769"

    fields = "?fields='synonyms,antonyms'"

    word2 = invar.get()
    word2 = word2.lower()

    for index in range(0, len(word2)):
        if word2[index] == ' ':
            word2 = word2[:index] + '_' + word2[index+1:]

    url2 = "https://od-api.oxforddictionaries.com/api/v2/thesaurus/en/" + word2 + fields

    header = {'app_id': appid, 'app_key': appkey}

    wordreq2 = urllib.request.Request(url2, data=None, headers=header)

    # call to Oxford Dictionary API, requesting only synonyms & antonyms of specified word
    try:
        wordres2 = urllib.request.urlopen(wordreq2)

    except Exception as err:

        tkinter.messagebox.showerror("Error", "Error connecting to server:" + str(err))

    else:
        if wordres2.getcode() != 200:
            tkinter.messagebox.showerror("Error", "Response error:\n" + wordres2.getcode())

        else:
            response2 = wordres2.read()
            response2 = response2.decode("utf-8")
            respdict2 = json.loads(response2)

            res = 'results'
            le = 'lexicalEntries'
            ens = 'entries'
            sen = 'senses'
            ant = 'antonyms'
            syn = 'synonyms'
            subs = 'subsenses'

            textblock = "Synonyms:\n\n"
            textblock2 = "Antonyms:\n\n"

            # each word list initialized as a set, to avoid returning multiple instances of a word
            synset = set()
            antset = set()

            # loop/if statement combination to search each entry and each entry in each sub-dictionary
            # for anything listed as a synonym or antonym, to be added to the respective sets
            for i4 in range(0, len(respdict2[res])):
                for index in range(0, len(respdict2[res][i4][le])):
                    if ens in respdict2[res][i4][le][index]:
                        for index2 in range(0, len(respdict2[res][i4][le][index][ens][0][sen])):
                            if syn in respdict2[res][i4][le][index][ens][0][sen][index2]:
                                for si in range(0, len(respdict2[res][i4][le][index][ens][0][sen][index2][syn])):
                                    synset.add(respdict2[res][i4][le][index][ens][0][sen][index2][syn][si]["id"])
                            if ant in respdict2[res][i4][le][index][ens][0][sen][index2]:
                                for ai in range(0, len(respdict2[res][i4][le][index][ens][0][sen][index2][ant])):
                                    antset.add(respdict2[res][i4][le][index][ens][0][sen][index2][ant][ai]["id"])

                            if subs in respdict2[res][i4][le][index][ens][0][sen][index2]:
                                for i2 in range(0, len(respdict2[res][i4][le][index][ens][0][sen][index2][subs])):
                                    if syn in respdict2[res][i4][le][index][ens][0][sen][index2][subs][i2]:
                                        for i3 in range(0,
                                                        len(respdict2[res][i4][le][index][ens][0][sen][index2]
                                                            [subs][i2][syn])):
                                            synset.add(
                                                respdict2[res][i4][le][index][ens][0][sen][index2][subs][i2][syn]
                                                [i3]["id"])
                                    if ant in respdict2[res][i4][le][index][ens][0][sen][index2][subs][i2]:
                                        for ai3 in range(0,
                                                         len(respdict2[res][i4][le][index][ens][0][sen][index2][subs]
                                                             [i2][ant])):
                                            antset.add(respdict2[res][i4][le][index][ens][0][sen][index2]
                                                       [subs][i2][ant][ai3]["id"])

            # changing the sets to lists so they can be sorted and formatted to remove/replace anything
            # not cleaned up by the decode call (specifically whitespaces and apostrophes)
            # also refers to the current setting of the scale bar variable to determine the length of the lists
            synset = sorted(list(synset))
            if not synset:
                textblock += "--NONE--"
            else:
                for item in range(0, listnum.get()):
                    if item < len(synset):
                        synset[item] = synset[item][0].upper() + synset[item][1:]
                        while '_' in synset[item]:
                            x = synset[item].index('_')
                            synset[item] = synset[item][:x] + ' ' + synset[item][x+1:]
                        if '%' in synset[item]:
                            y = synset[item].index('%')
                            synset[item] = synset[item][:y] + "'" + synset[item][y+3:]
                        textblock += synset[item] + "\n"
                    else:
                        break

            antset = sorted(list(antset))
            if not antset:
                textblock2 += "--NONE--"
            else:
                for item2 in range(0, listnum.get()):
                    if item2 < len(antset):
                        antset[item2] = antset[item2][0].upper() + antset[item2][1:]
                        while '_' in antset[item2]:
                            x = antset[item2].index('_')
                            antset[item2] = antset[item2][:x] + ' ' + antset[item2][x+1:]
                        if '%' in antset[item2]:
                            z = antset[item2].index('%')
                            antset[item2] = antset[item2][:z] + "'" + antset[item2][z+3:]
                        textblock2 += antset[item2] + "\n"
                    else:
                        break

            # determining which lists to include in output, based on the option menu widget
            # any list not included is 'reset' to an empty string
            if listopt == "Synonyms Only":
                synout.set(textblock)
                antout.set("")
            elif listopt == "Antonyms Only":
                antout.set(textblock2)
                synout.set("")
            else:
                synout.set(textblock)
                antout.set(textblock2)


# Function to call, format, and output a list of rhyming words from the datamuse API
def rhymewords():
    # checking value of checkbox - will not make extraneous call to api if not checked
    if rhymelist.get() == 1:

        word = invar.get()
        word = word.lower()

        for char in word:
            if char == ' ':
                word = word[:char.index()] + '+' + word[(char.index() + 1):]

        url = "https://api.datamuse.com/words?rel_rhy=" + word + "&max=25"

        try:
            rhyres = urllib.request.urlopen(url)

        except Exception as err:
            tkinter.messagebox.showerror("Server Error", "Error connecting to server:" + str(err))

        else:
            if rhyres.getcode() != 200:
                tkinter.messagebox.showerror("Error", "Response error: " + rhyres.getcode())

            else:
                response = rhyres.read()
                response = response.decode("utf-8")

                rhydict = json.loads(response)

                rhyblock = "Rhyming words:\n\n"

                if not rhydict:
                    rhyblock += "--NONE--"
                else:
                    # formatting and compiling list of rhymes from api response dictionary
                    # refers to the current setting of the scale bar variable to determine the length of the list
                    for index in range(0, listnum.get()):
                        if index < len(rhydict):
                            word = rhydict[index]['word']
                            word = word[0].upper() + word[1:]
                            rhyblock += word + "\n"

                rhyout.set(rhyblock)
    else:
        rhyout.set("")


# Function to produce the audio pronunciation file
# while also creating a popup message box with thr IPA phonetic spelling
# def hearword():
#     # initializing audio
#     pygame.mixer.init()
#
#     # returning the relevant mp3 information from the global dicionary created upon the original api request
#     mp3url = respdict['results'][0]['lexicalEntries'][0]["pronunciations"][0]["audioFile"]
#
#     # retrieval, and playback of mp3 file from the given url
#     mp3file, headers = urllib.request.urlretrieve(mp3url)
#
#     pygame.mixer.music.load(mp3file)
#     pygame.mixer.music.play()
#
#     # while the audio file is being processed and played by pygame's module, the event manager will create a popup
#     # which includes the phonetic spelling of the word currently being heard
#     tkinter.messagebox.showinfo("Pronunciation", "IPA Phonetic Spelling: " +
#                                 respdict['results'][0]['lexicalEntries'][0]["pronunciations"][0]["phoneticSpelling"])
#
#     pygame.mixer.quit()


# Function to update the three word lists based on any change in the scale bar
# (as prompted by the user hitting the "update" button)
def wordlists2():
    # re-calls the original functions for both the option menu and check box
    wordlists(listopt.get())
    rhymewords()


# Main Program

# Window creation and specs
popup = tkinter.Tk()
popup.title("Dictionary & Thesaurus Look Up")
popup.lift()
popup.minsize(800, 500)
popup.configure(bg="light blue")

# Widget creation and specs

# Labels for both the instructions and options area, and denoting the results area
instructlabel = tkinter.Label(popup, text="To start a new search, enter word and click 'Lookup'")
instructlabel.grid(row=0, column=0, columnspan=6, sticky="nesw")
instructlabel.config(bg="light blue")

resultlabel = tkinter.Label(popup, text="Results")
resultlabel.grid(row=5, column=0, columnspan=6, sticky="nesw")
resultlabel.config(bg="light blue")

# entry box for entering the word to search
invar = tkinter.StringVar()
wordbox = tkinter.Entry(popup, textvariable=invar)
wordbox.grid(row=2, column=0, columnspan=2, rowspan=2, sticky="nesw")

# result text box for definition and etymology information
defout = tkinter.StringVar()
resultbox = tkinter.Message(popup, textvariable=defout)
resultbox.grid(row=6, column=0, columnspan=3, sticky="nesw")
resultbox.config(anchor='nw', bg="white")

# button to call to main api request function, and to produce the definition results
getword = tkinter.Button(popup, text="Lookup", command=callapi)
getword.grid(row=2, column=2, rowspan=2, sticky="nesw")
getword.config(bg="grey")

# button to trigger hearing and seeing the popup pronunciation information
pron = tkinter.Button(popup, text="Pronunciation", command=None)
pron.grid(row=4, column=3, sticky="nesw")
pron.config(bg="grey")

# settings for the option menu widget - used to see the synonyms & antonyms lists
listopt = tkinter.StringVar()
listopt.set("Synonyms & Antonyms")
listopts = ["Synonyms & Antonyms", "Synonyms Only", "Antonyms Only"]

listselect = tkinter.OptionMenu(popup, listopt, *listopts, command=wordlists)
listselect.grid(row=1, column=4, columnspan=2, sticky="nesw")
listselect.config(bg="grey")

# checkbutton settings to select whether or not rhyming words are displayed
rhymelist = tkinter.IntVar()
rhymelist.set(0)
listrhymes = tkinter.Checkbutton(popup, variable=rhymelist, text="List Rhyming Words", command=rhymewords)
listrhymes.grid(row=2, column=4, columnspan=2, sticky="nesw")
listrhymes.config(bg="light blue")

# results boxes for the three optional word lists
synout = tkinter.StringVar()
resultbox2 = tkinter.Message(popup, textvariable=synout)
resultbox2.grid(row=6, column=3, sticky="nesw")
resultbox2.config(anchor='nw', bg="white")

antout = tkinter.StringVar()
resultbox3 = tkinter.Message(popup, textvariable=antout)
resultbox3.grid(row=6, column=4, sticky="nesw")
resultbox3.config(anchor='nw', bg="white")

rhyout = tkinter.StringVar()
resultbox4 = tkinter.Message(popup, textvariable=rhyout)
resultbox4.grid(row=6, column=5, sticky="nesw")
resultbox4.config(anchor='nw', bg="white")

# settings and creation of the three case options as radio buttons
casevar = tkinter.IntVar()
casevar.set(1)

case1 = tkinter.Radiobutton(popup, variable=casevar, text="Sentence Case", value=1, command=casechange)
case2 = tkinter.Radiobutton(popup, variable=casevar, text="Lower Case", value=2, command=casechange)
case3 = tkinter.Radiobutton(popup, variable=casevar, text="Upper Case", value=3, command=casechange)

case1.grid(row=1, column=3, sticky="news")
case2.grid(row=2, column=3, sticky="news")
case3.grid(row=3, column=3, sticky="news")

case1.config(bg="light blue")
case2.config(bg="light blue")
case3.config(bg="light blue")

# settings for the scale bar, which determines how long the optional word lists should be (from 1 to 25 words)
listnum = tkinter.IntVar()
listnum.set(1)
listscroll = tkinter.Scale(popup, from_=1, to=25, orient=tkinter.HORIZONTAL, variable=listnum)
listscroll.grid(row=3, column=4, columnspan=2, sticky="nesw")
listscroll.config(bg="light blue", label="Length of word lists:")

# button to update word lists based on changes made to the scale bar
changelists = tkinter.Button(popup, text="Update Word Lists", command=wordlists2)
changelists.grid(row=4, column=4, columnspan=2, sticky="nesw")
changelists.config(bg="grey")

# configuration settings for the main grid in the root window
popup.rowconfigure(0, weight=0)
popup.rowconfigure(1, weight=0)
popup.rowconfigure(2, weight=0)
popup.rowconfigure(3, weight=0)
popup.rowconfigure(4, weight=0)
popup.rowconfigure(5, weight=0)
popup.rowconfigure(6, weight=3)

popup.columnconfigure(0, weight=1)
popup.columnconfigure(1, weight=1)
popup.columnconfigure(2, weight=1)
popup.columnconfigure(3, weight=1)
popup.columnconfigure(4, weight=1)
popup.columnconfigure(5, weight=1)

# call to event manager
popup.mainloop()
