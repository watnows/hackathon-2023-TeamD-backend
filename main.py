# (1) 必要なライブラリをインポートする
import os
from pymongo import MongoClient
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from fastapi.middleware.cors import CORSMiddleware
import random



load_dotenv()

clint = MongoClient(os.environ['MONGO_URL'])


client_id = '49b607371e524745b0200c82ae283fba'
client_secret = 'f8100708fd044216bf3dfd9cd4854558'
 
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

 
    

# (2) User型を定義する
@strawberry.type
class User:
    name: str
    age: int
    

@strawberry.type
class Song:
    song_name : str
    
    
@strawberry.type
class Room:
    user_id : int
    name : str
    
    


# (3) Query(データの読み込み)を行うクラスを定義する
@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Shota", age=22)
    
    @strawberry.field
    def song(self, keyword:str) -> list[Song]:
        keyword_list = keyword.split(",")
        
        songs = []
        for k in keyword_list:
            results = sp.search(q=k, limit=10, market="JP",type='track')
            for idx, track in enumerate(results['tracks']['items']):
                songs.append(Song(song_name=str(track['name'])))
        
                
        # ここでsongsをシャッフルする
        random.shuffle(songs)
        
        return songs
    
    @strawberry.field
    def room(self) -> Room:
        return Room(user_id=1, name='部屋1')



# (4) スキーマを定義する
schema = strawberry.Schema(query=Query)

sdl = str(schema)

with open("schema.graphql","w") as f:
    f.write(sdl)

# (5) GraphQLエンドポイントを作成する
graphql_app = GraphQL(schema)

# (6) FastAPIアプリのインスタンスを作る
app = FastAPI()


# (7) /graphqlでGraphQL APIへアクセスできるようにし、適切なレスポンスを出力
app.add_route("/graphql", graphql_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 許可するオリジンを指定。安全な設定に注意してください。
    allow_credentials=True,
    allow_methods=["*"],  # 許可するHTTPメソッドを指定。必要に応じて調整してください。
    allow_headers=["*"],  # 許可するHTTPヘッダーを指定。必要に応じて調整してください。
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello")
async def root():
    return {"message": "Hello"}

