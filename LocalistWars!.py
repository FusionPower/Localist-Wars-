#!/usr/bin/env python3


WLL = 390 # High and low wave length limits of visible light
WLH = 700
word_amount=7
numi_grab_bag=5 #Number of items per grab bag
objects_per_game=5


WL_interval=(WLH-WLL)//(word_amount)#this retrieves the amount of letters we want for the initial population



deviation=5
use_random_deviation=1
deviation_lower=2
deviation_upper=15
random_dictionary=0
reduce_to_average=1 #turns samples into a unique representativa value


########
##GAME##
########
lower_fitness_move_more=1 #0 if lower fitness seek farther possible mates and talkers
fixed_movement=3  #how far do beings look for partners. X if lower fitness dont move more, at least X if lower fitness move more
possible_object=30 #meassures how near an abject has to be to the closest sample to be counted as possible
tie_breaker=7
paradigmatic=10    #how much closer an object has to be to be counter as a better choice
distinguishable=20 #how far away two objects must be to tell them apart
pass_game_on_bad_context=1 #if context is bad, dont play



bad_word_score=-4 #how low a word must be to eliminate it
learning_difference=2
new_word_threshold=15 #how different a word must be to learn ir


communicate_randomly=0 #0 if chosing most adequate partner 1 if chosen randomly locally
pair_randomly=0
literate_randomly=0

literate=1

fitness_prize=100
fitness_punishment=50
age_limit=30 
age_limit_variation=5

initial_fitness=500
number_of_beings=100
max_population=4000

probability_of_reproduction=80
minimum_age_of_reproduction=10

print_avoided_games=0
print_lost_games=0
print_won_games=0




import sys
import random
import string
import numpy

print("Welcome to the localist world!")

def take_average(temp):
    s=0
    for i in temp:
        s+=i
    s//=len(temp)
    return [s]
def setup_dictionary():
    dictionary={}
    if random_dictionary==1:
        for i,v in enumerate(lexicon):
            center=random.randint(WLL,WLH)
            if use_random_deviation==1:
                s=random.randint(deviation_lower,deviation_upper)
            else:
                s=deviation
            temp=list(map(int,numpy.random.normal(loc=center, scale=s, size=word_amount)))
            for j,w in reversed(list(enumerate(temp))):
                if w<WLL:
                    temp.pop(j)
                if w>WLH:
                    temp.pop(j)
            if reduce_to_average==1:
                temp=take_average(temp)
            dictionary[v]=temp
    else:
        for i,v in enumerate(lexicon):
                center=(WLL+i*WL_interval+WLL+(i+1)*WL_interval)//2
                temp=list(map(int,numpy.random.normal(loc=center, scale=deviation, size=word_amount)))
                if reduce_to_average==1:
                    temp=take_average(temp)
                dictionary[v]=temp
    return dictionary
def score(dictionary):
    s={}
    for i in dictionary.keys():
        s[i]=0
    return s
class Being:

    def __init__(self):
        
        self.birth_date=clock
        self.max_age=age_limit+random.randint(-age_limit_variation,age_limit_variation)
        self.dictionary=setup_dictionary()
        self.fitness=initial_fitness
        self.score=score(self.dictionary)
    def age(self):
        return clock-self.birth_date
        

def start():
    being=[0]*number_of_beings

    for i in range (number_of_beings):
        being[i]=Being()
    return being


def get_a_scenario():
    context=[]
    i=0
    while i<objects_per_game:
        x=random.randint(WLL,WLH)
        if x not in context:
            context.append(x)
            i+=1

    ans=random.randint(0,objects_per_game-1)

    return context,context[ans]

def lost_game(speaker,listener,word,ans,guess):
    speaker.fitness-=fitness_punishment
    listener.fitness-=fitness_punishment
    
    
    if type(word)==int:
        if word==4:
            for x in string.ascii_letters:
                if x not in speaker.dictionary.keys():
                    speaker.dictionary[x]=[ans]
                    speaker.score[x]=0
                    learn_word(x,speaker,listener)
                    break
            
    
    elif type(word)!=int:
        speaker.score[word]-=1
        if speaker.score[word]<bad_word_score:
            del speaker.dictionary[word]
            del speaker.score[word]
        try: ##in case of -6
            listener.score[word]-=1
            if listener.score[word]<bad_word_score:
                del listener.dictionary[word]
                del listener.score[word]
        except:
            try:
                learn_word(word,speaker,listener)
            except:
                pass
        speaker.fitness-=fitness_punishment
        listener.fitness-=fitness_punishment
        

    
    
def won_game(speaker,listener,word):  
    speaker.fitness+=fitness_prize
    listener.fitness+=fitness_prize
    speaker.score[word]+=1
    listener.score[word]+=1
    


def minimum_distance(wl, dictionary):
    possible=[]
    for word in dictionary.keys():
        minimum=WLH-WLL
        for sample in dictionary[word]:
            if abs(wl-sample)<minimum:
                minimum=abs(wl-sample)
        if minimum<=possible_object:
            possible.append([word,minimum])
    return possible            


def disambiguate_objects(possible_object):
    #run until there is no change in the list
    r=1
    poss=dict(possible_object)
    while r==1:
        r=0
        for i in poss.keys():
            #if you can only get the object with one word, we lock that object with the word
            if len(poss[i])==1:                
                for j in possible_object.keys():
                    for k in reversed(possible_object[j]):
                        if k[0]==poss[i][0][0] and len(poss[j])>1:
                            possible_object[j].remove(k)
                            r=1
        for i in possible_object.keys():
            #if you can only get the object with one word, we lock that object with the word
            if len(possible_object[i])==1:                
                for j in possible_object.keys():
                    for k in reversed(possible_object[j]):
                        if k[0]==poss[i][0][0] and len(possible_object[j])>1:
                            possible_object[j].remove(k)
                            r=1

                
def disambiguate_words(possible_word,possible_object):
    for i in possible_word.keys():
        if len(possible_word[i])>1:
            for j in reversed(possible_word[i]):
                if len(possible_object[j[0]])>1:
                    for k in reversed(possible_object[j[0]]):
                        if k[0]==i:
                            possible_object[j[0]].remove(k)
                    possible_word[i].remove(j)
    
def get_possible_object(being,context):
    possible={}
    for wave in context:
        possible[wave]=[]
    for wave in context:
        possible_for_wl=minimum_distance(wave,being.dictionary)
        if 0<len(possible_for_wl):
            #word,score
            possible[wave]=possible_for_wl
    return possible



def turn_organization(possible):
    new={}
    for i in possible.values():
        for j in i:
            new[j[0]]=[]
    for i in possible.keys():
        for j in possible[i]:
            new[j[0]].append([i,j[1]])    
    return new
        

def get_possible_word(being,context):
    possible={}
    for word in being.dictionary.keys():
        possible[word]=[]
    for wave in context:
        word_possibility=minimum_distance(wave,being.dictionary)
        if 0<len(word_possibility):
            for i in word_possibility:
                possible[i[0]].append([wave,i[1]])
    return possible


def clean_choice(possible):
    
    for i in possible.keys():
        for j in possible[i]:
            if j[1]<=paradigmatic:
                for k in possible.keys():
                    for l in reversed(possible[k]):
                        if l[0]==j[0] and l[1]>paradigmatic:
                            possible[k].remove(l)
                        


def eliminate_obvious(possible):
    retired={}
    possible2=turn_organization(possible)
    for i in possible.keys():
        if len(possible[i])==1 and len(possible2[possible[i][0][0]])==1:
            retired[i]=possible[i]
    return retired

def readible(retired):
    d={}
    if type(list(retired.keys())[0])==int:
        for i in retired.keys():
            d[retired[i][0][0]]=i
    else:
        for i in retired.keys():
            d[i]=retired[i][0][0]
    return d


def speaker_strategy(speaker,context,ans):
    possible_object=get_possible_object(speaker,context)
    
    if len(possible_object[ans])==0:
        return 4 #DEFINATELY LEARN WORD
    clean_choice(possible_object)
    
    sparadigmatic=eliminate_obvious(possible_object)
    try:
        error_diagnostic["s_paradigmatic"]=readible(sparadigmatic)
        return sparadigmatic[ans][0][0]
    except:
        pass 

    
    disambiguate_objects(possible_object)

    sdiss_obj=eliminate_obvious(possible_object)
    try:
        for i in sdiss_obj.keys():
            if i not in list(sparadigmatic.keys()):
                error_diagnostic["s_object_dissambiguation"]=readible(sdiss_obj)
                break
        return sdiss_obj[ans][0][0]
    except:
        pass
    
    possible_word=turn_organization(possible_object)
    possible_object=turn_organization(possible_word)
    disambiguate_words(possible_word,possible_object)

    sdiss_word=eliminate_obvious(possible_object)
    try:
        for i in sdiss_word.keys():
            if i not in list(sdiss_obj.keys()):
                error_diagnostic["s_word_dissambiguation"]=readible(sdiss_word)
                break
        return sdiss_word[ans][0][0]
    except:
        pass
    
    
    try:
        length=len(possible_object[ans])
    except:
        return 1 #fair loss, not enough ambiguity was too conflicting. Word had better pragmatic case.
    if length==1:
        return possible_object[ans][0][0]
    
    
    
    possible_object[ans].sort(key=lambda x: x[1])
    if len(possible_object[ans])==2 and len(possible_word[possible_object[ans][0][0]])==1 and len(possible_word[possible_object[ans][1][0]])==1:
        error_diagnostic["s_two_options"]={possible_object[ans][0][0]:ans}
        return possible_object[ans][0][0]
    else:
        return 2 #too many conflicting cases
    
    
    
def listener_strategy(listener,context,word):

    possible=get_possible_word(listener,context)
    
    try:
        possible[word]
    except:
        return -6 #unknown word, learn
    if len(possible[word])==0:
        return 0 #Word had no salient options, diferent samples in speaker and Listener
    if len(possible[word])==1:
        error_diagnostic["l_obvious"]=possible[word][0][0]
        return possible[word][0][0]
    
    possible_object=turn_organization(possible)
    clean_choice(possible_object)
    lparadigmatic=eliminate_obvious(possible_object)
    possible=turn_organization(possible_object)

    
    try:
        error_diagnostic["l_paradigmatic"]=readible(lparadigmatic)
        if len(possible[word])==1:
            return possible[word][0][0]
    except:
        pass
    
    disambiguate_objects(possible_object)
    
    ldiss_obj=eliminate_obvious(possible_object)
    possible=turn_organization(possible_object)
    
    try:
        for i in ldiss_obj.keys():
            if i not in list(lparadigmatic.keys()):
                error_diagnostic["l_object_dissambiguation"]=readible(ldiss_obj)
        if len(possible[word])==1:
            return possible[word][0][0]
    except:
        pass

  
            
    possible_word=turn_organization(possible_object)

    try:
        if len(possible_word[word])==1:
            return possible_word[word][0][0]
        else:
            possible_word[word].sort(key= lambda x:x[1])
            if possible_word[word][1][1]-possible_word[word][0][1]>tie_breaker:
                return possible_word[word][0][0]
            else:
                return -3 #Ambiguous cases. Not better option
    except KeyError:
        return -5 #No object was retrieved with Word


#get a context, speaker chooses a word, listener evaluates best outcome
def play_game(speaker,listener):
    context,ans=get_a_scenario()
    error_diagnostic.clear()
    error_diagnostic["context"]=context
    error_diagnostic["ans"]=ans
    error_diagnostic["os_dictionary"]=dict(speaker.dictionary)   
    error_diagnostic["ol_dictionary"]=dict(listener.dictionary)
    
    
    word=speaker_strategy(speaker,context,ans)
    error_diagnostic["word"]=word
    

    if pass_game_on_bad_context==1:        
        for i in context:
            if i!=ans:
                if abs(i-ans)<distinguishable:
                    error_diagnostic["word"]=-1
                    return -1

    if type(word)==int:
        guess=-4 #no word given
    else:
        guess=listener_strategy(listener,context,word)
    error_diagnostic["guess"]=guess
    if guess==ans:
        error_diagnostic["outcome"]="WIN"
        won_game(speaker,listener,word)
        return 1       
    else:
        error_diagnostic["outcome"]="LOSE"
        lost_game(speaker,listener,word,ans,guess)  
        return 0

def fitness_info():
    max_fit=being[0].fitness
    min_fit=being[0].fitness
    #find max, min and average fitness and also average age
    fitness_avg=0
    age_avg=0
    for v in being:
        
        if v.fitness>max_fit:
            max_fit=v.fitness
        elif v.fitness<min_fit:
            min_fit=v.fitness

        fitness_avg+=v.fitness
        age_avg+=v.age()
    
    fitness_avg/=(len(being))
    age_avg/=(len(being))
    avg[0]=fitness_avg
    avg[1]=age_avg
    fitness_max_min[0]=max_fit
    fitness_max_min[1]=min_fit


    
def movement_of_beings(fitness_of_being):
    if lower_fitness_move_more==0:
        movement_of_beings=fixed_movement 
    else:
        movement_of_beings=fixed_movement-1+fitness_max_min[0]//fitness_of_being
    return movement_of_beings  


def random_selection_of_partner(pairing_control,i):
    number_of_beings=len(being)
    mb=movement_of_beings(being[i].fitness)
    starting_index=(i-mb)%number_of_beings
    step=0
    options=[]
    while step<2*mb+1:
        possible_index=(starting_index+step)%number_of_beings
        if pairing_control[possible_index]==0 and possible_index not in options:
            options.append(possible_index)
        step+=1
    if len(options)>0:
        return random.choice(options)
    else:
        return "No partner found"
    
 
def select_fitness_equivalent_partner(pairing_control,i):
    number_of_beings=len(being)
    mb=movement_of_beings(being[i].fitness)
    starting_index=(i-mb)%number_of_beings
    step=0
    closest_partner=9999999999
    while step<2*mb+1:
        possible_index=(starting_index+step)%number_of_beings
        if pairing_control[possible_index]==0:
            if abs(being[possible_index].fitness-being[i].fitness)<closest_partner:
                closest_partner=abs(being[possible_index].fitness-being[i].fitness)
                possible_mate=possible_index
        step+=1

    if closest_partner<9999999999:
        return possible_mate
    else:
        return "No partner found"
  


def game():
    aux=[]
    pairing_control=[0]*number_of_beings
    correct=0
    incorrect=0
    if pass_game_on_bad_context==1:
        avoided=0
    for speaker,v in enumerate(pairing_control):
        if v==0:
            pairing_control[speaker]=1
            if communicate_randomly==1:
                listener=random_selection_of_partner(pairing_control,speaker)
            else:
                listener=select_fitness_equivalent_partner(pairing_control,speaker)
            if type(listener)==int:
                pairing_control[listener]=1
                count=play_game(being[speaker],being[listener])
                if being[listener].fitness>0:
                    aux.append(being[listener])
            if being[speaker].fitness>0:
                aux.append(being[speaker])
            if count==1:
                correct+=1
                lwon.append(dict(error_diagnostic))

            if count==0:
                incorrect+=1
                llost.append(dict(error_diagnostic))

            if count==-1:
                avoided+=1
                error_diagnostic["outcome"]="AVOIDED"
                error_diagnostic["guess"]=0
                lavoided.append(dict(error_diagnostic))
    try:
        ratio=correct/(correct+incorrect)
    except:
        ratio=0.0
    print("Correct,Incorrect:",correct,incorrect)
    print("Ratio:", ratio)
    if pass_game_on_bad_context==1:
        print("Avoided:",avoided)
        

    for i in range(len(being)):
        being.pop()
    for i in aux:
        if clock-i.birth_date<i.max_age:
            being.append(i)

    fitness_info()
    return ratio
  
def reproductive_success(a,b):
    c=Being()
    x=list(set(a.dictionary.keys()|b.dictionary.keys()))
    for i in x:
        c.dictionary[i]=[]
        c.score[i]=0
    for i in x:
        if i in a.dictionary.keys():
            if i in b.dictionary.keys():
                r=random.randint(0,1)
                if r==1:
                    c.dictionary[i]=a.dictionary[i] 
                else:
                    c.dictionary[i]=b.dictionary[i]
            else:
                c.dictionary[i]=a.dictionary[i]
        else:
            c.dictionary[i]=b.dictionary[i]
    return c    
    
def reproduction():
#partners get selected
    aux=[]
    number_of_beings=len(being)
    pairing_control=[0]*number_of_beings
    
    for seeker,v in enumerate(pairing_control):
        if v==0:
            pairing_control[seeker]=1
            if len(being)+len(aux)<max_population:
                if pair_randomly==1:
                    complier=random_selection_of_partner(pairing_control,seeker)
                else:
                    complier=select_fitness_equivalent_partner(pairing_control,seeker)
                if type(complier)==int:
                    first=int(being[seeker].fitness*probability_of_reproduction/fitness_max_min[0])
                    second=int(being[complier].fitness*probability_of_reproduction/fitness_max_min[0])
                    aux.append(being[complier])
                    
                    if random.randint(0,99)<first and random.randint(0,99)<second and being[seeker].age()>=minimum_age_of_reproduction and being[complier].age()>=minimum_age_of_reproduction:
                        c=reproductive_success(being[seeker],being[complier])
                        aux.append(c)
                    pairing_control[complier]=1
            aux.append(being[seeker])
        
    for i in range(len(being)):
        being.pop()

    for i in aux:
        if clock-i.birth_date<i.max_age:
            being.append(i)
    fitness_info()


def learn_word(letter,a,b): 
    #a wants to teach b
    
    if letter not in b.dictionary.keys():
        minimum=9999
        for i in a.dictionary[letter]:
            for j in b.dictionary.keys():
                for k in b.dictionary[j]:
                    if abs(k-i)<minimum:
                        minimum=k-i
                        synonym=j
        if minimum<new_word_threshold:
            if b.score[synonym]>a.score[letter]:
                if synonym not in a.dictionary.keys():
                    a.dictionary[synonym]=a.dictionary[letter]
                    for i in a.dictionary[synonym]:
                        i+=random.randint(-learning_difference,learning_difference)
                    a.score[synonym]=0
                    del a.dictionary[letter]
                    del a.score[letter]
            else:
                b.dictionary[letter]=b.dictionary[synonym]
                for i in b.dictionary[letter]:
                        i+=random.randint(-learning_difference,learning_difference)
                b.score[letter]=0
                del b.dictionary[synonym]
                del b.score[synonym]
    else:
        if b.score[letter]>a.score[letter]:
            a.dictionary[letter]=b.dictionary[letter]
            for i in a.dictionary[letter]:
                i+=random.randint(-learning_difference,learning_difference)
            a.score[letter]=0

        else:
            b.dictionary[letter]=a.dictionary[letter]
            for i in b.dictionary[letter]:
                    i+=random.randint(-learning_difference,learning_difference)
            b.score[letter]=0
 

def get_words(a,b):
    max_a=bad_word_score
    max_b=bad_word_score
    for i in a.score.keys():
        if a.score[i]>max_a:
            letter_a=i
            max_a=a.score[i]
    for i in b.score.keys():
        if b.score[i]>max_b:
            letter_b=i
            max_b=b.score[i]
    learn_word(letter_a,a,b)
    learn_word(letter_b,b,a)
        
def literate():
    aux=[]
    number_of_beings=len(being)
    pairing_control=[0]*number_of_beings
    for a,v in enumerate(pairing_control):
        if v==0:
            pairing_control[a]=1
            if communicate_randomly==1:
                b=random_selection_of_partner(pairing_control,a)
            else:
                b=select_fitness_equivalent_partner(pairing_control,a)
            if type(b)==int:
                pairing_control[b]=1
                get_words(being[a],being[b])
                aux.append(being[a])
                aux.append(being[b])
            else:
                aux.append(being[a])
    for i in range(len(being)):
        being.pop()
    for i in aux:
        being.append(i) 
        
        
def cycle_of_life():  
    r=game()
    fitness_avg=avg[0]
    age_avg=avg[1]
    print("Current population:", len(being))
    print("Fitness limits:",fitness_max_min)
    print("Average fitness:", fitness_avg)
    print("Age average:",age_avg)
    print("Clock:", clock+1)
    print()
    reproduction()
    if literate==1:
        literate()
    return r  



    

import pygame
spectrum=pygame.image.load('/home/samuel/Documents/Estancia MIT 2019/Simulation/IMG/spectrum.png')
title=pygame.image.load('/home/samuel/Documents/Estancia MIT 2019/Simulation/IMG/Localist-Wars.png')
arrowl=pygame.image.load('/home/samuel/Documents/Estancia MIT 2019/Simulation/IMG/arrow.png')
arrowr=pygame.image.load('/home/samuel/Documents/Estancia MIT 2019/Simulation/IMG/arrowr.png')
pygame.init()


pygame.mixer.pre_init(44100,16,2,4096)
pygame.mixer.music.load('/home/samuel/Documents/Estancia MIT 2019/Simulation/IMG/MuTeArt.mp3')
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1)





#locations
spectrumx=200
spectrumy=700
buttonsc=485
obj_radius=15

#colors
green=(0,140,0)
white=(255,255,255)

#screen
screen = pygame.display.set_mode((1600, 1000))
pygame.display.set_caption("Localist Wars!")




def split_game_steps(gs):
    context=gs["context"]
    ans=gs["ans"]
    speaker=gs["os_dictionary"]
    listener=gs["ol_dictionary"]
    word=gs["word"]
    guess=gs["guess"]
    s_events={}
    l_events={}
    outcome=gs["outcome"]
    for i in gs.keys():
        if i[0]=="s":
            s_events[i]=gs[i]
        elif i[0]=="l":
            l_events[i]=gs[i]      
    return context,ans,speaker,listener,s_events,l_events,word,guess,outcome

def scale(wl):
    r=int((1200/(WLH-WLL))*(wl-WLL))+170
    if r<200:
        return 200
    if r >1400:
        return 1400
    return r
def get_color(posx,posy):
    return screen.get_at((posx, posy))
def show_game(context,ans):
    
    for i in context:
        posx=scale(i)
        pygame.draw.line(screen,get_color(posx,spectrumy+15),(posx,spectrumy+10),(posx,spectrumy-10),2)
        pygame.draw.circle(screen,get_color(posx,spectrumy+15),(posx+1,spectrumy-25),obj_radius,obj_radius)
#        message_display(str(i),(posx,spectrumy-40),20,(150,150,150))
    if type(ans)==int and ans>10:
        pygame.draw.line(screen,(150,150,150),(scale(ans),spectrumy-50),(scale(ans)-8,spectrumy-55),2)
        pygame.draw.line(screen,(150,150,150),(scale(ans),spectrumy-50),(scale(ans)+8,spectrumy-55),2)
        pygame.draw.line(screen,(150,150,150),(scale(ans),spectrumy-50),(scale(ans),spectrumy-70),3)

#    pygame.draw.circle(screen,(255,255,255),(scale(ans),spectrumy-15),11,1)
    pygame.display.flip()
    return

def text_objects(text,font,color):
    surface=font.render(text,True,color)
    return surface,surface.get_rect()

def message_display(text,location,size,color):
    font=pygame.font.SysFont("linuxbiolinumo",size)
    surface,rectangle=text_objects(text,font,color)
    rectangle.center=location
    screen.blit(surface,rectangle)

def word_spacing(objects):  
    return 1400//(objects+1)

def word_button(color_of_word,level,word_location,spacing,being,stage,speaker_order):
    mouse=pygame.mouse.get_pos()
    click=pygame.mouse.get_pressed()    

    for wod,x in enumerate(word_location):
#word_location[xleft,xright,letter,click_status,index_occupied, object paired]

        if x[0]<mouse[0]<x[1] and 485<mouse[1]<535:
            if x[3]==0:
                pygame.draw.rect(screen,(200,200,200),(x[0],buttonsc,50,30))
            else:
                pygame.draw.rect(screen,(150,150,150),(x[0],buttonsc,50,30))
                
            if click[0]==1:
                if x[3]==0:
                    for index,value in enumerate(level):
                        if value==0:
                            for i in being[x[2]]:
                                pygame.draw.line(screen,color_of_word[wod],(scale(i-possible_object),spectrumy+20+(index*4)),(scale(i+possible_object),spectrumy+20+(index*4)),3)
                                if x[5]!=0:
                                    pygame.draw.line(screen,color_of_word[wod],((x[0]+x[1])//2,505),(scale(x[5]),spectrumy-(15+2*obj_radius)))
                            x[4]=index
                            level[index]=1
                            x[3]=1
                            break
                    
                else:
                    for i in being[x[2]]:
                        pygame.draw.line(screen,(0,0,0),(scale(i-possible_object),spectrumy+20+(x[4]*4)),(scale(i+possible_object),spectrumy+20+(x[4]*4)),3)
                        if x[5]!=0:
                            pygame.draw.line(screen,(0,0,0),((x[0]+x[1])//2,505),(scale(x[5]),spectrumy-(15+2*obj_radius)))
                    level[x[4]]=0
                    x[4]=0
                    x[3]=0
                

        else:  
            if x[3]==0:
                pygame.draw.rect(screen,color_of_word[wod],(x[0],buttonsc,50,30))     
            else:
                pygame.draw.rect(screen,(150,150,150),(x[0],buttonsc,50,30))
                
        message_display(x[2],(25+x[0],500),20,(0,0,0))
        
    return color_of_word,level,word_location,spacing
def color_of_words(being):
    c=[]
    for i in being.keys():
        s=0
        for j in being[i]:
            s+=j
        s//=len(being[i])
        c.append(get_color(scale(s),spectrumy+15))
    return c
def stage_button(stage):
    arrowright=pygame.transform.scale(arrowr, (50, 50))
    arrowleft=pygame.transform.scale(arrowl, (50, 50))
    mouse=pygame.mouse.get_pos()
    click=pygame.mouse.get_pressed() 
    
    if stage[0]!=1:
        screen.blit(arrowleft,(50,400))
    else:
        pygame.draw.rect(screen,(0,0,0),(50,400,50,50))
    if stage[-1]!=1:
        screen.blit(arrowright,(1500,400))
    else:
        pygame.draw.rect(screen,(0,0,0),(1500,400,50,50))  
    
    if 50<mouse[0]<100 and 400<mouse[1]<450:                
        if click[0]==1 and stage[0]!=1:
            for i,v in enumerate(stage):
                if v==1:
                    stage[i]=0
                    stage[i-1]=1
                    return 
    
    if 1500<mouse[0]<1550 and 400<mouse[1]<450:
        if click [0]==1 and stage[-1]!=1:
            for i,v in enumerate(stage):
                if v==1:
                    stage[i]=0
                    stage[i+1]=1
                    return 
def pair_stage(stage,speaker_order,word_location):  
    for i,v in enumerate(stage):
        if v==1:
            step=i
            break
        
    if step>0 and step< len(stage)-1:
        
        ev=list(speaker_order[step-1].keys())
        for i,v in enumerate(word_location):
            if v[2] in ev:
                
                word_location[i][5]=speaker_order[step-1][v[2]]
            else:
                word_location[i][5]=0
    elif step==0:
        for i,v in enumerate(word_location):
            word_location[i][5]=0

     
def speaker_order_foo(s_events,word):
    speaker_order=[]
    speaker_order_names=["First stage, click words to see what they mean"]
    try:
        speaker_order.append(s_events["s_paradigmatic"])
        speaker_order_names.append("Speaker pairs words with an unambiguously paradigmatic objects")        
    except:
        pass
    try:
        speaker_order.append(s_events["s_object_dissambiguation"])
        speaker_order_names.append("Speaker solves ambiguity by paring object that don't have other word options")                
    except:
        pass
    try:
        speaker_order.append(s_events["s_word_dissambiguation"])    
        speaker_order_names.append("Speaker dissambiguates by chosing words less prone to ambiguity")                

    except:
        pass
    try:
        speaker_order.append(s_events["s_two_options"]) 
        speaker_order_names.append("Speaker chooses one of equaly ambiguous words if both work")                
        
    except:
        pass
    if type(word)==int:
        speaker_order_names.append("No good word found")
    else:
        speaker_order_names.append("Speaker choses word")
    speaker_order.append(word)
    return speaker_order,speaker_order_names

def speaker_stage(context,ans,speaker,s_events,word):
    screen.fill((0,0,0))
    running = True
    screen.blit(spectrum,(spectrumx,spectrumy))
    screen.blit(title,(430,100))
    
#    message_display("Wavelength",(150,spectrumy-40),20,(150,150,150))
    word_location=[]
    spacing=word_spacing(len(speaker.keys()))
    speaker_order,speaker_order_names=speaker_order_foo(s_events,word)
    
    for i,v in enumerate(list(speaker.keys())):
        #word_location[xleft,xright,letter,click_status,index_occupied, object paired]
        word_location.append([75+(i+1)*spacing,125+(i+1)*spacing,v,0,0,0])
    level=[0]*len(word_location)
    pygame.draw.rect(screen,(150,150,150),(30,890,220,25))
    message_display("Speaker Interpretation",(140,900),20,(0,0,0))
    stage=[1]+[0]*(len(s_events)+1)
    color_of_word=color_of_words(speaker)
    while running:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
                
        show_game(context,ans)
        stage_button(stage)
        pair_stage(stage,speaker_order,word_location)
        color_of_word,level,word_location,spacing=word_button(color_of_word,level,word_location,spacing,speaker,stage,speaker_order)
        if stage[-1]==1:
            for letter in word_location:
                if letter[2]==speaker_order[-1]:
                    pygame.draw.rect(screen,(200,200,200),(letter[0],buttonsc,50,30),3)
                    pygame.draw.rect(screen,(150,150,150),(1300,890,200,25))
                    message_display("Click for listener",(1400,900),20,(0,0,0))
                    mouse=pygame.mouse.get_pos()
                    click=pygame.mouse.get_pressed() 
                    if 1300<mouse[0]<1500 and 890<mouse[1]<915 and click[0]==1:
                        return
            if type(speaker_order[-1])==int:

                pygame.draw.rect(screen,(150,150,150),(1300,890,200,25))
                message_display("Click for Outcome",(1400,900),20,(0,0,0))
                mouse=pygame.mouse.get_pos()
                click=pygame.mouse.get_pressed() 
                if 1300<mouse[0]<1500 and 890<mouse[1]<915 and click[0]==1:
                    return
                
        else:
            for i in word_location:
                if i[2]==speaker_order[-1]:
                    pygame.draw.rect(screen,(0,0,0),(i[0],buttonsc,50,30),3)
            pygame.draw.rect(screen,(0,0,0),(1300,890,200,25))
        for i,v in enumerate(stage):
            if v==1:
                pygame.draw.rect(screen,(0,0,0),(200,270,1200,60))
                message_display(speaker_order_names[i],(800,300),30,(0,140,0))
           
        pygame.display.update()


def listener_order_foo(l_events,guess):
    listener_order=[]
    listener_order_names=["First stage, click words to see what they mean"]
    
    try:
        listener_order.append(l_events["l_paradigmatic"])
        listener_order_names.append("Listener pairs words with an unambiguously paradigmatic objects")                
    except:
        pass
    try:
        listener_order.append(l_events["l_object_dissambiguation"])    
        listener_order_names.append("Listener solves ambiguity by paring object that don't have other word options")                

    except:
        pass
    try:
        listener_order.append(l_events["l_obvious"])
        listener_order_names.append("Trivial object found")        
    except:
        pass
    listener_order_names.append("Final Guess")
    listener_order.append(guess)
    return listener_order,listener_order_names

def show_word(word,word_location):
    for i,v in enumerate(word_location):
        if v[2]==word:
            pygame.draw.rect(screen,(255,255,250),(v[0],buttonsc,50,30),6)
            return
    
    
def listener_stage(listener,context,word,guess,l_events):    
    screen.fill((0,0,0))    
    running = True
    screen.blit(spectrum,(spectrumx,spectrumy))
    screen.blit(title,(430,100))
    
#    message_display("Wavelength",(150,spectrumy-40),20,(150,150,150))
    word_location=[]
    spacing=word_spacing(len(listener.keys()))
    listener_order,listener_order_names=listener_order_foo(l_events,guess)
    
    for i,v in enumerate(list(listener.keys())):
        #word_location[xleft,xright,letter,click_status,index_occupied, object paired]
        word_location.append([75+(i+1)*spacing,125+(i+1)*spacing,v,0,0,0])
    level=[0]*len(word_location)
    pygame.draw.rect(screen,(150,150,150),(30,890,220,25))
    message_display("Listener Interpretation",(140,900),20,(0,0,0))
    stage=[1]+[0]*(len(l_events))
    
    color_of_word=color_of_words(listener)
    
    while running:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
                
        show_game(context,"e")
        show_word(word,word_location)
        
        stage_button(stage)
        
        
        
        pair_stage(stage,listener_order,word_location)
        color_of_word,level,word_location,spacing=word_button(color_of_word,level,word_location,spacing,listener,stage,listener_order)
        if listener_order[-1]>10:
            if stage[-1]==1:
                pygame.draw.line(screen,(150,150,150),(scale(guess),spectrumy-50),(scale(guess)-8,spectrumy-55),2)
                pygame.draw.line(screen,(150,150,150),(scale(guess),spectrumy-50),(scale(guess)+8,spectrumy-55),2)
                pygame.draw.line(screen,(150,150,150),(scale(guess),spectrumy-50),(scale(guess),spectrumy-70),3)
            else:
                pygame.draw.line(screen,(0,0,0),(scale(guess),spectrumy-50),(scale(guess)-8,spectrumy-55),2)
                pygame.draw.line(screen,(0,0,0),(scale(guess),spectrumy-50),(scale(guess)+8,spectrumy-55),2)
                pygame.draw.line(screen,(0,0,0),(scale(guess),spectrumy-50),(scale(guess),spectrumy-70),3)
        else:
            if stage[-1]==1:
                message_display("No good guess",(800,400),30,(0,140,0))
        if stage[-1]==1:
            mouse=pygame.mouse.get_pos()
            click=pygame.mouse.get_pressed()
            pygame.draw.rect(screen,(150,150,150),(1300,890,200,25))
            message_display("Click to End",(1400,900),20,(0,0,0))
            mouse=pygame.mouse.get_pos()
            click=pygame.mouse.get_pressed() 
            if 1300<mouse[0]<1500 and 890<mouse[1]<915 and click[0]==1:
                return
        
        else:
            pygame.draw.rect(screen,(0,0,0),(1300,890,200,25))
        for i,v in enumerate(stage):
            if v==1:
                pygame.draw.rect(screen,(0,0,0),(200,270,1200,60))
                message_display(listener_order_names[i],(800,300),30,(0,140,0))
            
        pygame.display.update()
def option_animations(option):
    pygame.draw.rect(screen,(140,140,140),(1100,option*100+450,400,80))
    pygame.draw.rect(screen,(180,0,0),(1098,option*100+448,404,84),4)
    for i in range(4):
        if i!=option:
            pygame.draw.rect(screen,(0,0,0),(1097,i*100+447,406,86),5)

    return



    
def end(outcome,size):
    screen.fill((0,0,0))
    running = True
    pygame.display.update()
    message_display(outcome,(800,500),size,(0,140,0))
    while running:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
                
        mouse=pygame.mouse.get_pos()
        click=pygame.mouse.get_pressed() 
        pygame.draw.rect(screen,(150,150,150),(1300,890,200,25))
        message_display("Main Menu",(1400,900),20,(0,0,0))
        if 1300<mouse[0]<1500 and 890<mouse[1]<915 and click[0]==1:
            return
        pygame.display.update()

def error_screen(ratio, do):
    screen.fill((0,0,0))
    running = True
    pygame.display.update()
    message_display("Incomplete parameters",(800,400),150,(140,0,0))
    message_display("Select Game type and type cycles",(800,700),80,(0,140,0))

    while running:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
                
        mouse=pygame.mouse.get_pos()
        click=pygame.mouse.get_pressed() 
        pygame.draw.rect(screen,(150,150,150),(1300,890,200,25))
        message_display("Main Menu",(1400,900),20,(0,0,0))
        if 1300<mouse[0]<1500 and 890<mouse[1]<915 and click[0]==1:
            screen.fill((0,0,0))

            return
        pygame.display.update()
        
def messages():
    screen.blit(title,(430,100))
    message_display(("Welcome to the localist world!"),(750,250),30,(0,140,0))
    message_display(("Population:"+str(len(being))),(300,350),30,(140,140,140))
    message_display(("Maximum Population:"+str(max_population)),(300,400),30,(0,140,0))
    message_display(("Win Game Prize:"+str(fitness_prize)),(300,450),30,(0,140,0))
    message_display(("Lose Game Punishment:"+str(fitness_punishment)),(300,500),30,(0,140,0))
    message_display(("Initial Fitness:"+str(initial_fitness)),(300,550),30,(0,140,0))
    message_display(("Word Amount:"+str(word_amount)),(300,600),30,(0,140,0))
    message_display(("Number of Items In Grab Bag:"+str(numi_grab_bag)),(300,650),30,(0,140,0))
    message_display(("Objects in Game:"+str(objects_per_game)),(300,700),30,(0,140,0))
    message_display(("Lower Bound:"+str(WLL)),(300,750),30,(0,140,0))
    message_display(("Higher Bound:"+str(WLH)),(300,800),30,(0,140,0))
       
def main_menu(ratio,do):
    screen.fill((0,0,0))
    running = True
    
    
    
    
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    font = pygame.font.Font(None, 32)
    text = ''
    pygame.display.update()
    option="t"
    while running:
        mouse=pygame.mouse.get_pos()
        click=pygame.mouse.get_pressed()
        messages()
        pygame.draw.rect(screen,(150,0,0),(750,900,100,50))
        message_display("EXIT",(800,925),20,(0,0,0))
        if 750<mouse[0]<850 and 900<mouse[1]<950:
            pygame.draw.rect(screen,(150,70,70),(750,900,100,50))
            message_display("EXIT",(800,925),20,(0,0,0))
            if click[0]==1:
                running=False
                
                
        input_box = pygame.Rect(1250, 380, 140, 32)
        if do==1:
            message_display(("Last Cycle Win Rate:"+str(ratio*100)[0:4]),(800,700),30,(0,140,0))
        pygame.draw.rect(screen,(140,140,140),(1100,350,400,80),3)
        message_display(("Cycles:"),(1170,390),40,(140,140,140))
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if event.unicode in string.digits and len(text)<4:
                            text += event.unicode

        
        pygame.draw.rect(screen,(140,140,140),(1100,450,400,80))
        pygame.draw.rect(screen,(140,140,140),(1100,550,400,80))
        pygame.draw.rect(screen,(140,140,140),(1100,650,400,80))
        pygame.draw.rect(screen,(140,140,140),(1100,750,400,80))
        
        message_display(("Click for lost game"),(1300,490),30,(0,0,0))
        message_display(("Click for won game"),(1300,590),30,(0,0,0))
        message_display(("Click for avoided game"),(1300,690),30,(0,0,0))
        message_display(("Click for random game"),(1300,790),30,(0,0,0))
        # Render the current text.
        if 1100<mouse[0]<1500:
            if 450<mouse[1]<530:
                pygame.draw.rect(screen,(180,180,180),(1100,450,400,80))
                message_display(("Click for lost game"),(1300,490),30,(0,0,0))
                if click[0]==1:
                    option=0
                    option_animations(option)
                    message_display(("Click for lost game"),(1300,490),30,(0,0,0))
        if 1100<mouse[0]<1500:
            if 550<mouse[1]<630:
                pygame.draw.rect(screen,(180,180,180),(1100,550,400,80))
                message_display(("Click for won game"),(1300,590),30,(0,0,0))
                if click[0]==1:
                    option=1
                    option_animations(option)     
                    message_display(("Click for won game"),(1300,590),30,(0,0,0))
        if 1100<mouse[0]<1500:
            if 650<mouse[1]<730:
                pygame.draw.rect(screen,(180,180,180),(1100,650,400,80))
                message_display(("Click for avoided game"),(1300,690),30,(0,0,0))
                if click[0]==1:
                    option=2
                    option_animations(option)  
                    message_display(("Click for avoided game"),(1300,690),30,(0,0,0))

        if 1100<mouse[0]<1500:
            if 750<mouse[1]<830:
                pygame.draw.rect(screen,(180,180,180),(1100,750,400,80))
                message_display(("Click for random game"),(1300,790),30,(0,0,0))
                if click[0]==1:
                    option=3
                    option_animations(option)
                    message_display(("Click for random game"),(1300,790),30,(0,0,0))
    
        pygame.draw.circle(screen,(200,50,50),(800,500),100,5)
        
        if 700<mouse[0]<900 and 400<mouse[1]<600 and click[0]==1:
            if option!="t" and text!="":
                if option==3:
                    option=random.randint(0,2)
                return int(text),option
            else:
                error_screen(ratio, do)
        
        if text!="":
            if option==1 or option==2 or option==0 or option ==3:
                message_display(("START"),(800,500),50,(120,200,120))
            
        pygame.draw.rect(screen,(0,0,0),(1255,385,130,20))

        txt_surface = font.render(text, True, color)
        pygame.display.update()

        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        # Blit the text.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.update()
#    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
        


lexicon=[string.ascii_letters[i] for i in range(word_amount)]
fitness_max_min=[0,0]
avg=[0,0]

clock=0
ratio=0
being=start()


fitness_info()

ticks=0  
ratio_do=0
send=1
running=True

while running:
    lavoided=[]
    llost=[]
    lwon=[]
    
    add,game_type=main_menu(send,ratio_do)    
    ticks+=add
    if add==0:
        break
    while clock<ticks:
        error_diagnostic={}
        r=cycle_of_life()
        clock+=1
        number_of_beings=len(being)
        ratio+=r
    print(ratio/clock)
    send=ratio/clock
    ratio_do=1
    try:
        if game_type==0:
            game_steps=random.choice(llost)
        elif game_type==1:
            game_steps=random.choice(lwon)
        else:
            game_steps=random.choice(lavoided)
    except:
        end("No matches found, other game selected", 80)
        try:
            game_steps=random.choice(lwon)
        except:
            game_steps=random.choice(lavoided)
    context,ans,speaker,listener,s_events,l_events,word,guess,outcome=split_game_steps(game_steps)
    speaker_stage(context,ans,speaker,s_events,word)
    if type(game_steps["word"])!=int:
        listener_stage(listener,context,word,guess,l_events)
    end(outcome,300)
    
        
    

    


pygame.quit()
