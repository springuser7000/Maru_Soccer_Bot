import time
import threading

#discord io
import discord
import asyncio
from discord import team

#beautiful soup
import requests
from bs4 import BeautifulSoup
from soupsieve import SoupSieve

#firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


# 더 만들어야할 함수 - 모든 객체를 조회하고 거기에 특정한 클럽이 있는지 찾아내서 객체를 반환하는 함수/ -> 멀티쓰레딩으로 제작해야함.



#기본적으로 필요한 값들이나 모듈에서 제공하는 객체
cred = credentials.Certificate('D:\\ChatBot\\(tokenfilename).json')
firebase_admin.initialize_app(cred, {
    'databaseURL': '###'
})
client = discord.Client()
ref = db.reference()

# 유저 데이터(딕셔너리)
user = {}

# Match로 만들어진 객체번호 ( match0, match1, match2.. 이렇게 네이밍하기 위한 숫자)
object_number = 0

#Match 클래스 정의
class Match() :
    def __init__(self, home, away, time, score):
        self.home = home
        self.away = away
        self.time = time
        self.score = score

#생 html코드를 원하는 2개의 정보 리스트로 만들어주는 함수
def html_to_string(inputedstring) :
    started = False
    mainstring = ""
    n,m = [], []
    # 원래 html to string 함수가 html 값만 string으로 반환하는 과정
    for i in inputedstring:
        if i == "<": started = True 
        if i == ">": 
            started = False
            continue
        if started == False: mainstring += i
    
    #info to object에 있던 string을 2개의 리스트에 쪼개서 반환하는 과정
    splited_string = mainstring.split("       ")
    del splited_string[0]
    del splited_string[int(len(splited_string))-1]
    for i in splited_string:
        n.append(i) if splited_string.index(i) % 2 == 1 else m.append(i)
    return n,m

#자신이 팬클럽으로 지정한 팀의 경기가 30분간격으로 체크하는 함수 (미완)

client = discord.Client()

async def checking_match(message):
    while True:
        #for i in range(0,object_number+1)
        print("hello thread")
        #author = client.get_user("springmaru").create_dm()
        #author.send("on_ready가 호출되었습니다.")
        await message.channel.send("hello thread")
        time.sleep(2)



# 프로그램이 시작되었을때 (__init__와 비슷한 이벤트),
@client.event
async def on_ready():
    global object_number, user
    # 6월 12일 전까지라면 12일부터 17일까지의 경기정보 받아와 Match 객체로 만듬
    #if 12 > int(time.strftime("%d", time.localtime(time.time()))):
            #info_to_object()
    # 6월 12일 후라면 그날 후  5일동안의 경기정보 받아와서 Match 객체로 만듬

    try:
        for i in range(0,5):
            webpage = requests.get("https://www.goal.com/kr/euro/%EC%9D%BC%EC%A0%95-%EA%B2%B0%EA%B3%BC/" +
                "{}-{}-{}".format(time.strftime("%Y", time.localtime(time.time())), time.strftime("%m", time.localtime(time.time())),str(int(time.strftime("%d", time.localtime(time.time())))+i))
            +"/8tddm56zbasf57jkkay4kbf11")
            soup = BeautifulSoup(webpage.content, "html.parser")

            teamlist, infolist = html_to_string(str(soup.find_all(attrs={'class':'widget-competition-matches'})[0])) #html 코드에서 필요한 값을 2개의 리스트로 쪼갬
            print(teamlist, infolist)
            for j in teamlist:
                globals()["match{}".format(str(object_number))] = Match(str(j).split("     ")[0],str(j).split("     ")[1],infolist[teamlist.index(j)].replace("   ","").split(")")[0] + ")",infolist[teamlist.index(j)].replace("   ","").split(")")[1])
                object_number +=1
    except:
        for i in range(2,7):
            webpage = requests.get("https://www.goal.com/kr/euro/%EC%9D%BC%EC%A0%95-%EA%B2%B0%EA%B3%BC/" +
            "2021-06-1{}".format(i)
            +"/8tddm56zbasf57jkkay4kbf11")
            soup = BeautifulSoup(webpage.content, "html.parser")
            teamlist, infolist = html_to_string(str(soup.find_all(attrs={'class':'widget-competition-matches'})[0])) #html 코드에서 필요한 값을 2개의 리스트로 쪼갬
            print(teamlist, infolist)
            for j in teamlist:
                globals()["match{}".format(str(object_number))] = Match(str(j).split("     ")[0],str(j).split("     ")[1],infolist[teamlist.index(j)].replace("   ","").split(")")[0] + ")",infolist[teamlist.index(j)].replace("   ","").split(")")[1])
                object_number +=1
            
            #info_to_object(html_to_string(str(soup.find_all(attrs={'class':'widget-competition-matches'})[0])).split("       "))
    ref = db.reference()
    user = ref.get()
    #await checking_match()
    check = threading.Thread(target=checking_match)
    check.start()
    
    print("Ready")


# 채팅을 쳤을때 일어나는 이벤트
@client.event
async def on_message(message):
    global object_number, user
    # 새로운 유저인지 확인하고 새로운 유저면 user 딕셔너리에 유저 정보등을 추가하고 firebase db와 동기화(firebase는 json을 쓰기 때문에 딕셔너리형태로 바로 올리면 됨)
    try:
        a = user[message.author.id]
    except KeyError:
        user[message.author.id] = {"fanclub": "RealMadrid(defult)", "name": message.author.name, "password": "0000"}
        print(user)
        ref = db.reference()
        ref.update({message.author.id:user[message.author.id]})
        user = ref.get()


    # 메세지 내용이 무엇인지 확인하고 거기에 맞는 작업 수행


    if message.content.startswith('!일정보기'):
        text= ""
        for i in range(0,object_number):
            objectname = eval("match"+str(i))
            text  += "{}  {}  {}  {} \n".format(objectname.home, objectname.away, objectname.time, objectname.score)
        await message.channel.send("앞으로 약 5일동안 있을 경기입니다.")
        await message.channel.send(text)
    
    
    #계정 관리(수정)
    if message.content.startswith('!팬클럽'):
        try:
            ref = db.reference(str(message.author.id))
            
            ref.update({"fanclub":message.content.split()[1]})
            await message.channel.send("수정되었습니다.")
        except:
            await message.channel.send("잘못된 값입니다. !팬클럽 좋아하는클럽이름 으로 입력해주세요.")

    if message.content.startswith('!비밀번호'):
        try:
            ref = db.reference(str(message.author.id))
            
            ref.update({"password":message.content.split()[1]})
            await message.channel.send("수정되었습니다.")
        except:
            await message.channel.send("잘못된 값입니다. !비밀번호 새비밀번호 으로 입력해주세요.")

    if message.content.startswith('!아이디'):
        try:
            ref = db.reference(str(message.author.id))
            
            ref.update({"name":message.content.split()[1]})
            await message.channel.send("수정되었습니다.")
            sync_user_with_firebase()
        except:
            await message.channel.send("잘못된 값입니다. !아이디 새아이디 으로 입력해주세요.")

client.run('//토큰//')
