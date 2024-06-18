# Importing the necessary libraries
import pandas as pd
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
from surprise import SVD, Dataset, Reader, KNNBaseline
from surprise.model_selection import train_test_split

#graphical user interface
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

#web scraping
import requests
import webbrowser

#collaborative
from collections import defaultdict
import random

#content based
from sklearn.feature_extraction.text import CountVectorizer
from scipy.stats import pearsonr
from sklearn.metrics.pairwise import euclidean_distances

# Connect to the database
mydb = mysql.connector.connect(
      host="sql11.freemysqlhosting.net",
      user="sql11701047",
      password="AIcLNtbdwB",
      database="sql11701047"
    )

videogames = pd.read_csv('videogames.csv')
videogames = videogames.sort_values('bayesian_rating', ascending=False)

videogame_users = pd.read_csv('users-videogames.csv')

df_videogames = videogames #temp variable for the videogames

boardgames = pd.read_csv('boardgames.csv')
boardgames = boardgames.sort_values('bayesaverage', ascending=False)

df_boardgames = boardgames #temp variable for the boardgames

boardgame_users = pd.read_csv('users-boardgames.csv')

user_id = 0
user_games = [] #games of logged in user
matching_games = [] #games that match
recommendations = [] #recommended games
content = []
videogame_appid = 0 #the appid of a game
mygames_check = 0 #check if the class i came from is my games
search_check = 0 #check if the class i came from is search games   
top_rated_check = 0 #check if the class i came from is top rated games
content_check = 0 #check if the class i came from is content based filtering
collaborative_check = 0 #check if the class i came from is collaborative filtering
hybrid_check = 0 #check if the class i came from is hybrid filtering 
content_category_check = 0 #check if the class i came from is content based filtering by category
content_multiplayer_check = 0 #check if the class i came from is content based filtering by multiplayer
collaborative_knn_item_check = 0 #check if the class i came from is collaborative filtering by knn item
collaborative_knn_user_check = 0 #check if the class i came from is collaborative filtering by knn user
collaborative_svd_check = 0 #check if the class i came from is collaborative filtering by svd
hybrid_category_check = 0 #check if the class i came from is hybrid filtering by category
hybrid_multiplayer_check = 0 #check if the class i came from is hybrid filtering by multiplayer
hybrid_knn_item_check = 0 #check if the class i came from is hybrid filtering by knn item
hybrid_knn_user_check = 0 #check if the class i came from is hybrid filtering by knn user
hybrid_svd_check = 0 #check if the class i came from is hybrid filtering by svd

boardgame_appid = 0 #the appid of a game
content_minage_check = 0 #check if the class i came from is content based filtering by minage
content_players_check = 0 #check if the class i came from is content based filtering by players
hybrid_minage_check = 0 #check if the class i came from is hybrid filtering by minage
hybrid_players_check = 0 #check if the class i came from is hybrid filtering by players


#Choose boardgames user or videogames user
class User_type(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)


        # Create the buttons
        self.choose_button = tk.Label(self, text="Choose your type", font=("Arial", 25, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        self.choose_button.pack(pady=100)
        self.videogames_button = tk.Button(self, text="Video-games",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogame_user_reg_login))
        self.videogames_button.pack(padx=50, pady=50)
        self.boardgames_button = tk.Button(self, text="Board-games",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgame_user_reg_login))
        self.boardgames_button.pack()


#Videogames user registration and login
class Videogame_user_reg_login(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        self.login_button = tk.Button(self,width = 10, text="Login",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogame_login))
        self.login_button.pack(padx=50, pady=(300,50))
        self.register_button = tk.Button(self, width = 10,text="Register",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogame_register))
        self.register_button.pack()

        self.back_button = tk.Button(self, text="Back",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, User_type))
        self.back_button.pack(side="bottom")


#Videogames user registration
class Videogame_register(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)


        def register():
            if username_entry.get() != "" and password_entry.get() != "" and confirm_password_entry.get() != "":
                if len(username_entry.get()) >= 5:
                    if password_entry.get() == confirm_password_entry.get():
                        if len(password_entry.get()) >= 8:
                            mycursor = mydb.cursor()
                            mycursor.execute("SELECT * FROM videogames_login WHERE username = %s", (username_entry.get(),))
                            myresult = mycursor.fetchall()
                            if myresult:
                                messagebox.showerror("Error", "Username already exists")
                                mycursor.close()
                            else:
                                mycursor.execute("INSERT INTO videogames_login (username, password) VALUES (%s, %s)", (username_entry.get(), password_entry.get()))
                                mydb.commit()
                                messagebox.showinfo("Success", "User registered successfully")
                                mycursor.close()

                                mycursor = mydb.cursor()
                                mycursor.execute("SELECT * FROM videogames_login WHERE username = %s AND password = %s", (username_entry.get(), password_entry.get()))
                                myresult = mycursor.fetchall()
                                mycursor.close()
                                global user_id
                                user_id = myresult[0][2]
                                cont.show_frame(parent, Videogame_menu)
                        else:
                            messagebox.showerror("Error", "Password must be at least 8 characters long")
                    else:
                        messagebox.showerror("Error", "Passwords do not match")
                else:
                    messagebox.showerror("Error", "Username must be at least 5 characters long")
            else:
                messagebox.showerror("Error", "Please enter Username, Password and Confirm Password")


        username_label = tk.Label(self, text="Username", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        username_label.pack(pady=(170,10))
        username_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",insertbackground="white")
        username_entry.pack(pady=(10,20))

        password_label = tk.Label(self, text="Password", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        password_label.pack(pady=10)
        password_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",show="*",insertbackground="white")
        password_entry.pack(pady=(10,20))

        confirm_password_label = tk.Label(self, text="Confirm Password", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5,
                                        highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        confirm_password_label.pack(pady=10)
        confirm_password_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",show="*",insertbackground="white")
        confirm_password_entry.pack(pady=(10,20))

        register_button = tk.Button(self, text="Register", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=register)
        register_button.pack(pady=10)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogame_user_reg_login))
        back_button.pack(side="bottom")  


#Videogames user login
class Videogame_login(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def login():
            if username_entry.get() != "" and password_entry.get() != "":
                mycursor = mydb.cursor()
                mycursor.execute("SELECT * FROM videogames_login WHERE username = %s AND password = %s", (username_entry.get(), password_entry.get()))
                myresult = mycursor.fetchall()
                if myresult:
                    #print("Welcome " + username_entry.get() + "!")
                    mycursor.close()
                    global user_id
                    user_id = myresult[0][2]
                    cont.show_frame(parent, Videogame_menu)

                else:
                    messagebox.showerror("Error", "Invalid Username or Password")
                    mycursor.close()

            else:
                messagebox.showerror("Error", "Please enter Username and Password")

        username_label = tk.Label(self, text="Username", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        username_label.pack(pady=(250,10))
        username_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",insertbackground="white")
        username_entry.pack(pady=(10,20))

        password_label = tk.Label(self, text="Password", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        password_label.pack(pady=10)
        password_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",show="*",insertbackground="white")
        password_entry.pack(pady=(10,20))


        login_button = tk.Button(self, text="Login", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=login)
        login_button.pack(pady=10)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogame_user_reg_login))
        back_button.pack(side="bottom")


#Videogames user menu
class Videogame_menu(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        mycursor = mydb.cursor()
        sqlquery = "select * from videogames_login where id = %s"
        val = (user_id, )
        mycursor.execute(sqlquery, val)
        myresult = mycursor.fetchall()
        mycursor.close()

        username = myresult[0][0]

        mycursor = mydb.cursor()
        sqlquery = "select * from videogames_user where user_id = %s"
        val = (user_id, )
        mycursor.execute(sqlquery, val)
        myresult = mycursor.fetchall()
        mycursor.close()

        global user_games
        user_games = []
        for game in myresult:
            user_games.append([game[0], game[1],game[2]])

        welcome_label = tk.Label(self, text="Welcome, " + username, font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=(50, 100))

        self.mygames_button = tk.Button(self,width = 15, text="My Games",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, My_videogames))
        self.mygames_button.pack(padx=50, pady=50)

        self.recommendations_button = tk.Button(self,width = 15, text="Recommendations",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_videogames))
        self.recommendations_button.pack()

        self.logout_button = tk.Button(self,width = 15, text="Logout",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, User_type))
        self.logout_button.pack(side="bottom")


#Videogames Recommendation methods
class Recommendations_videogames(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def content_check():
            if user_games == []:
                messagebox.showerror("Error", "You have no games in your library")
                cont.show_frame(parent, Recommendations_videogames)
            else:
                cont.show_frame(parent, Videogames_content_based)

        def collaborative_check():
            if user_games == []:
                messagebox.showerror("Error", "You have no games in your library")
                cont.show_frame(parent, Recommendations_videogames)
            else:
                cont.show_frame(parent, Videogames_collaborative_filtering)

        def hybrid_check():
            if user_games == []:
                messagebox.showerror("Error", "You have no games in your library")
                cont.show_frame(parent, Recommendations_videogames)
            else:
                cont.show_frame(parent, Videogames_hybrid_filtering)


        welcome_label = tk.Label(self, text="Choose a Recommendation", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        self.toprated_button = tk.Button(self,width = 20, text="Top Rated Games", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_top_rated))
        self.toprated_button.pack(padx=50, pady=20)

        self.search_button = tk.Button(self,width = 20, text="Search Games", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Search_videogames))
        self.search_button.pack(padx=50, pady=20)
        
        self.content_button = tk.Button(self,width=20, text="Content-Based Filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=content_check)
        self.content_button.pack(padx=50, pady=20)

        self.collaborative_button = tk.Button(self,width=20, text="Collaborative Filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=collaborative_check)
        
        self.collaborative_button.pack(padx=50, pady=20)

        self.hybrid_button = tk.Button(self,width=20, text="Hybrid Filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=hybrid_check)
        self.hybrid_button.pack(padx=50, pady=20)

        self.back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogame_menu))
        self.back_button.pack(side="bottom")


# search for videogames
class Search_videogames(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global top_rated_check
        top_rated_check = 0
        global mygames_check
        mygames_check = 0
        global search_check
        search_check = 1
        global content_check
        content_check = 0
        global collaborative_check
        content_check = 0
        global hybrid_check
        hybrid_check = 0

        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def search_games():
            global recommendations
            recommendations = []
            empty_search_check = 0


            name = self.name_entry.get()
            developer = self.developer_entry.get()
            multiplayer = self.multiplayer_combobox.get()
            category = self.category_combobox.get()
            platform = self.platform_combobox.get()

            if not name and not developer and not multiplayer and not category and not platform:
                messagebox.showerror("Error", "Please enter at least one search criteria")
                empty_search_check = 1
                cont.show_frame(parent, Search_videogames)

            if multiplayer == "MultiPlayer":
                multiplayer = "Multiplayer"
            elif multiplayer == "SinglePlayer":
                multiplayer = "No_Multiplayer"

            platform = platform.lower()
            if platform != "" and platform != "windows" and platform != "mac" and platform != "linux":
                messagebox.showerror("Error", "Invalid platform")
                empty_search_check = 1
                cont.show_frame(parent, Search_videogames)
            else:

                for i in range(len(videogames)):
                    if len(recommendations) == 20:
                        break
                    if name.lower() in videogames.iloc[i]['name'].lower() or not name:
                        if developer.lower() in videogames.iloc[i]['developer'].lower() or not developer:
                            if multiplayer.lower() in videogames.iloc[i]['multiplayer'].lower() or not multiplayer:
                                if category.lower() in videogames.iloc[i]['general_genre'].lower() or not category:
                                    if platform != "" and videogames.iloc[i][platform] == 1:
                                        recommendations.append(videogames.iloc[i]['appid'])
                                    elif platform == "":
                                        recommendations.append(videogames.iloc[i]['appid'])

                if len(recommendations) == 0:
                    messagebox.showerror("Error", "No games found")
                    empty_search_check = 1
                    cont.show_frame(parent, Search_videogames)

                if empty_search_check == 0:
                    cont.show_frame(parent, Videogames_results)

        welcome_label = tk.Label(self, text="Search Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        self.name_entry = tk.Entry(self, font=("Arial", 15, "bold"), bg="black", fg="white", insertbackground="white")
        self.name_entry.place(x=400, y=200)
        self.update_idletasks()
        label_height = self.name_entry.winfo_reqheight()

        name_label = tk.Label(self, text="Name", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        name_label.place(x=200, y=200, height=label_height)

        developer_label = tk.Label(self, text="Developer", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        developer_label.place(x=200, y=250, height=label_height)

        self.developer_entry = tk.Entry(self, font=("Arial", 15, "bold"), bg="black", fg="white", insertbackground="white")
        self.developer_entry.place(x=400, y=250)

        multiplayer_label = tk.Label(self, text="Multiplayer", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        multiplayer_label.place(x=200, y=300, height=label_height)

        self.multiplayer_combobox = ttk.Combobox(self,width=18, values=["MultiPlayer", "SinglePlayer"], font=("Arial", 15, "bold"))
        self.multiplayer_combobox.place(x=400, y=300)

        category_label = tk.Label(self, text="Category", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        category_label.place(x=200, y=350, height=label_height)

        self.category_combobox = ttk.Combobox(self,width=18, values=["Action","Casual","Violent","Sports","Other"], font=("Arial", 15, "bold"))
        self.category_combobox.place(x=400, y=350)

        platform_label = tk.Label(self, text="Platform", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        platform_label.place(x=200, y=400, height=label_height)

        self.platform_combobox = ttk.Combobox(self,width=18, values=["Windows","Mac","Linux"], font=("Arial", 15, "bold"))
        self.platform_combobox.place(x=400, y=400)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="red", highlightcolor="red", highlightthickness=2, command=search_games)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_videogames))
        back_button.pack(side="bottom")


# User's videogames library
class My_videogames(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global top_rated_check
        top_rated_check = 0
        global mygames_check
        mygames_check = 1
        global search_check
        search_check = 0
        global content_check
        content_check = 0
        global collaborative_check
        content_check = 0
        global hybrid_check
        hybrid_check = 0

        def show_more_info(appid):
            global videogame_appid
            videogame_appid = 0
            videogame_appid = appid
            print(videogame_appid)
            cont.show_frame(parent, Videogame_info)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        global user_games

        welcome_label = tk.Label(self, text="My Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        frame = Frame(self)
        frame.pack(side=LEFT, fill=BOTH, expand=True, padx=300, pady=(10, 100))

        self.canvas = Canvas(frame, bg='black')
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.mailbox_frame = Frame(self.canvas, bg='purple')
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.mailbox_frame, anchor=NW)

        mail_scroll = Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        mail_scroll.pack(side=RIGHT, fill=Y)

        self.canvas.config(yscrollcommand=mail_scroll.set)

        self.mailbox_frame.bind("<Configure>", self.OnFrameConfigure)
        self.canvas.bind('<Configure>', self.FrameWidth)

        user_games = sorted(user_games, key=lambda x: x[2], reverse=True)
        user_games_ids = [game[1] for game in user_games]


        if user_games != []:
            for game_appid in user_games_ids:
                each_game_frame = tk.Frame(self.mailbox_frame, bg="black", bd=5, highlightbackground="blue", highlightcolor="red", highlightthickness=2)
                each_game_frame.pack(fill="both", expand="yes", side="top", padx=10, pady=5)

                game_image_url = videogames[videogames['appid'] == game_appid]['header_image'].values[0]
                game_image = Image.open(requests.get(game_image_url, stream=True).raw)
                game_image = game_image.resize((320, 200), Image.LANCZOS)
                game_photo = ImageTk.PhotoImage(game_image)
                game_image_label = tk.Label(each_game_frame, image=game_photo)
                game_image_label.image = game_photo
                game_image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

                hidden_button = tk.Button(each_game_frame, image=game_photo, command=lambda appid=game_appid: show_more_info(appid), bd=0, highlightthickness=0)
                hidden_button.grid(row=0, column=0, padx=10, pady=10)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogame_menu))
        back_button.place(x=450,y=736)

    def FrameWidth(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        # Debugging output to track canvas width updates
        #print(f"Canvas width set to: {canvas_width}")

    def OnFrameConfigure(self, event):
        # Update the scroll region to encompass the entire canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Debugging output to track scroll region updates
        #print(f"Scroll region updated to: {self.canvas.bbox('all')}")


# top rated videogames
class Videogames_top_rated(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global top_rated_check
        top_rated_check = 1
        global mygames_check
        mygames_check = 0
        global search_check
        search_check = 0
        global content_check
        content_check = 0
        global collaborative_check
        content_check = 0
        global hybrid_check
        hybrid_check = 0

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def top_rated_games():
            number = int(number_of_games.get())

            global recommendations
            recommendations = []
            recommendations = videogames.head(number)['appid'].tolist()
            print(recommendations)
            cont.show_frame(parent, Videogames_results)    
           
        def check():
            if number_of_games.get().isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            elif int(number_of_games.get()) > 100 or int(number_of_games.get()) < 1:
                messagebox.showerror("Error", "Please enter a number between 1 and 100")
            elif number_of_games.get() == "":
                messagebox.showerror("Error", "Please enter a number")
            else:
                top_rated_games()


        welcome_label = tk.Label(self, text="Top Rated Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Number of games in the result", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        number_of_games = tk.Entry(self,width = 10, font=("Arial", 20, "bold"), bg="black", fg="white", insertbackground="white")
        number_of_games.pack()

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=check)
        search_button.pack(pady=10)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_videogames))
        back_button.pack(side="bottom")


# Videogames content based filtering
class Videogames_content_based(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global content_check
        content_check = 1
        global collaborative_check
        collaborative_check = 0
        global hybrid_check
        hybrid_check  = 0
        global search_check
        search_check = 0
        global mygames_check
        mygames_check = 0
        global top_rated_check
        top_rated_check = 0

        global content_category_check
        content_category_check = 0
        global content_multiplayer_check
        content_multiplayer_check = 0

        def top_rated():
            global df_videogames
            df_videogames = videogames.sort_values('bayesian_rating', ascending=False)[:10000]
            df_videogames = df_videogames.reset_index(drop=True)

            global matching_games
            matching_games = []

            indices = pd.Series(df_videogames.index, index=df_videogames['appid']).drop_duplicates()

            top_rated_users_games = [game for game in user_games if game[2] > 5]

            for i in range(len(df_videogames)):
                if df_videogames.iloc[i]['appid'] in [game[1] for game in top_rated_users_games]:
                    idx = indices[df_videogames.iloc[i]['appid']]
                    matching_games.append(idx)
                    #print("the new indexes are "+ str(matching_games))

                
            if len(matching_games) == 0:
                messagebox.showerror("Error", "No games found with this category")
                cont.show_frame(parent, Videogames_content_based)
            else:
                cont.show_frame(parent, Videogames_choose_complexity)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        content_label = tk.Label(self, text="Content Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        content_label.pack(pady=50)

        choose_label  = tk.Label(self, text="Choose a filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=(10, 50))

        category_button = tk.Button(self, text="Category",width = 10, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_content_based_category))
        category_button.pack(pady=20)

        multiplayer_button = tk.Button(self, text="Multiplayer",width=10, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_content_based_multiplayer))
        multiplayer_button.pack(pady=20)

        top_rated_button = tk.Button(self, text="Top Rated", width=10,font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=top_rated)
        top_rated_button.pack(pady=20)
     
        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_videogames))
        back_button.pack(side="bottom")


# Videogames content based category
class Videogames_content_based_category(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global content_category_check
        content_category_check = 1
        global content_multiplayer_check
        content_multiplayer_check = 0

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def category_recommendations():
            category = category_combobox.get()
            if category == "":
                messagebox.showerror("Error", "Please choose a category")
            else:
                category_remove = []
                for i in range(len(videogames)):
                    if videogames.iloc[i]['general_genre'] != category:
                        category_remove.append(videogames.iloc[i]['appid'])

                global df_videogames
                df_videogames = videogames[~videogames['appid'].isin(category_remove)].reset_index(drop=True)
                df_videogames = df_videogames.sort_values('bayesian_rating', ascending=False)[:13000]
                df_videogames = df_videogames.reset_index(drop=True)
                df_videogames.to_csv("southpark.csv")

                global matching_games
                matching_games = []

                indices = pd.Series(df_videogames.index, index=df_videogames['appid']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_videogames)):
                    if df_videogames.iloc[i]['appid'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_videogames.iloc[i]['appid']]
                        matching_games.append(idx)

                
                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this category")
                    cont.show_frame(parent, Videogames_content_based_category)
                else:
                    cont.show_frame(parent, Videogames_choose_complexity)

        welcome_label = tk.Label(self, text="Category Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Choose a category", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        category_combobox = ttk.Combobox(self,width=18, values=["Action","Casual","Violent","Sports","Other"], font=("Arial", 15, "bold"))
        category_combobox.place(x=400, y=350)
        self.update_idletasks()
        label_height = category_combobox.winfo_reqheight()

        category_label = tk.Label(self, text="Category", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        category_label.place(x=200, y=350, height=label_height)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=category_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_content_based))
        back_button.pack(side="bottom")


# Videogames content based multiplayer
class Videogames_content_based_multiplayer(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global content_multiplayer_check
        content_multiplayer_check = 1
        global content_category_check
        content_category_check = 0

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def category_recommendations():
            category = category_combobox.get()
            if category == "":
                messagebox.showerror("Error", "Please choose a category")
            elif category != "MultiPlayer" and category != "SinglePlayer":
                messagebox.showerror("Error", "Please choose a valid category")
            else:
                category_remove = []
                if category == "MultiPlayer":
                    category = "Multiplayer"
                else:
                    category = "No_Multiplayer"
                for i in range(len(videogames)):
                    if videogames.iloc[i]['multiplayer'] != category:
                        category_remove.append(videogames.iloc[i]['appid'])

                global df_videogames
                df_videogames = videogames[~videogames['appid'].isin(category_remove)].reset_index(drop=True)
                df_videogames = df_videogames.sort_values('bayesian_rating', ascending=False)[:13000]
                df_videogames = df_videogames.reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_videogames.index, index=df_videogames['appid']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_videogames)):
                    if df_videogames.iloc[i]['appid'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_videogames.iloc[i]['appid']]
                        matching_games.append(idx)
                        #print("the new indexes are "+ str(matching_games))

                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this category")
                    cont.show_frame(parent, Videogames_content_based_multiplayer)
                else:
                    cont.show_frame(parent, Videogames_choose_complexity)

        welcome_label = tk.Label(self, text="Multiplayer Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Multiplayer or Singleplayer", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        category_combobox = ttk.Combobox(self,width=18, values=["MultiPlayer","SinglePlayer"], font=("Arial", 15, "bold"))
        category_combobox.place(x=400, y=350)
        self.update_idletasks()
        label_height = category_combobox.winfo_reqheight()

        category_label = tk.Label(self, text="Category", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        category_label.place(x=200, y=350, height=label_height)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=category_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_content_based))
        back_button.pack(side="bottom")


# Videogames choose filtering characteristics
class Videogames_choose_complexity(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def simple():
            if 'simple' not in df_videogames.columns:
                df_videogames['simple'] = ''
            df_videogames['simple'] = df_videogames.apply(lambda row: row['genres'] + ' ' + row['steamspy_tags'] +' '+ row['categories'], axis=1)
            tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
            #tfidf = CountVectorizer(stop_words='english', max_features=10000)
            tfidf_matrix = tfidf.fit_transform(df_videogames['simple'])
            similarity = cosine_similarity(tfidf_matrix)
            #similarity = euclidean_distances(tfidf_matrix,tfidf_matrix)

            global recommendations
            recommendations = []

            global matching_games         

            matching_games = [game for game in matching_games if game < len(df_videogames)]

            for game_index in matching_games:
                similar_games = list(enumerate(similarity[game_index]))
                similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
                #similar_games = sorted(similar_games, key=lambda x: x[1]) for euclidean
                similar_games = similar_games[1:21]  
                print(similar_games)

                for sim_game in similar_games:
                    sim_game_index = sim_game[0]
                    recommendations.append((sim_game_index, sim_game[1]))

            recommendation_dict = {}
            for appid_index, similarity_score in recommendations:
                if appid_index in recommendation_dict:
                    recommendation_dict[appid_index] += similarity_score
                else:
                    recommendation_dict[appid_index] = similarity_score

            recommendations = sorted(recommendation_dict.items(), key=lambda x: x[1], reverse=True)
            #recommendations = sorted(recommendation_dict.items(), key=lambda x: x[1]) for euclidean 

            recommendations = [rec for rec in recommendations if rec[0] not in matching_games]

            tuple_recommendations = recommendations
            recommendations = []

            #print("Recommended games: ")
            for i, (appid_index, similarity_score) in enumerate(tuple_recommendations):
                if i >= 20:
                    break
                appid = df_videogames.iloc[appid_index]['appid']
                game_name = df_videogames.iloc[appid_index]['name']
                bayesian_rating = df_videogames.iloc[appid_index]['bayesian_rating']
                #print(f"{game_name} with a rating of {bayesian_rating} and a similarity score of {similarity_score}")
                #print(f"{game_name} with a similarity score of {similarity_score}")

                recommendations.append(appid)

            cont.show_frame(parent, Videogames_results)

        def complex():
            if 'complex' not in df_videogames.columns:
                df_videogames['complex'] = ''
            df_videogames['complex'] = df_videogames.apply(lambda row: row['genres'] + ' ' + row['steamspy_tags'] +' '+ row['categories'] + ' ' + row['publisher'] + ' ' + row['developer'] + ' ' + ' '.join(map(str,row['keywords'])), axis=1)
            tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
            tfidf_matrix = tfidf.fit_transform(df_videogames['complex'])
            similarity = cosine_similarity(tfidf_matrix)

            global recommendations
            recommendations = []

            global matching_games         

            matching_games = [game for game in matching_games if game < len(df_videogames)]

            for game_index in matching_games:
                similar_games = list(enumerate(similarity[game_index]))
                similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
                similar_games = similar_games[1:21]  # Exclude the game itself and take the top 10 similar games
                print(similar_games)

                for sim_game in similar_games:
                    sim_game_index = sim_game[0]
                    recommendations.append((sim_game_index, sim_game[1]))

            recommendation_dict = {}
            for appid_index, similarity_score in recommendations:
                if appid_index in recommendation_dict:
                    recommendation_dict[appid_index] += similarity_score
                else:
                    recommendation_dict[appid_index] = similarity_score

            # Convert the dictionary back to a sorted list
            recommendations = sorted(recommendation_dict.items(), key=lambda x: x[1], reverse=True)

            # Filter out recommendations that are in matching_games
            recommendations = [rec for rec in recommendations if rec[0] not in matching_games]

            tuple_recommendations = recommendations
            recommendations = []

            #print("Recommended games: ")
            for i, (appid_index, similarity_score) in enumerate(tuple_recommendations):
                if i >= 20:
                    break
                appid = df_videogames.iloc[appid_index]['appid']
                game_name = df_videogames.iloc[appid_index]['name']
                bayesian_rating = df_videogames.iloc[appid_index]['bayesian_rating']
                #print(f"{game_name} with a rating of {bayesian_rating} and a similarity score of {similarity_score}")
                recommendations.append(appid)

            cont.show_frame(parent, Videogames_results)

        welcome_label = tk.Label(self, text="Choose Complexity", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=100)

        simple_button = tk.Button(self,width=10, text="Simple", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=simple)
        simple_button.pack(pady=50) 

        def show_simple_info():
            info_window = tk.Toplevel(self)
            info_window.title("Simple Filtering Info")
            info_window.geometry("400x300")

            info_label = tk.Label(info_window, text="Characteristics of Simple Filtering:", font=("Arial", 15, "bold"))
            info_label.pack(pady=20)

            characteristics_label = tk.Label(info_window, text="Recommendations are done based on:\n"
                                                 "1. genre\n"
                                                  "2. stremspy_tags\n"
                                                  "3. categories\n",
                                             font=("Arial", 12))
            characteristics_label.pack(pady=10) 

            close_button = tk.Button(info_window, text="Close", font=("Arial", 12), command=info_window.destroy)
            close_button.pack(pady=20)

        info_button = tk.Button(self, width=5, text="?", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="red", highlightcolor="red", highlightthickness=2, command=show_simple_info)
        info_button.place(x=600, y=310)


        complex_button = tk.Button(self,width=10, text="Complex", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=complex)
        complex_button.pack()


        def show_complex_info():
            info_window = tk.Toplevel(self)
            info_window.title("Complex Filtering Info")
            info_window.geometry("400x300")

            info_label = tk.Label(info_window, text="Characteristics of Complex Filtering:", font=("Arial", 15, "bold"))
            info_label.pack(pady=20)

            characteristics_label = tk.Label(info_window, text="Recommendations are done based on:\n"
                                                 "1. genre\n"
                                                  "2. stremspy_tags\n"
                                                  "3. categories\n"
                                                  "4. publisher\n"
                                                  "5. developer\n"
                                                  "6. keywords\n",
                                             font=("Arial", 12))
            characteristics_label.pack(pady=10) 

            close_button = tk.Button(info_window, text="Close", font=("Arial", 12), command=info_window.destroy)
            close_button.pack(pady=20)

        info_button2 = tk.Button(self, width=5, text="?", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="red", highlightcolor="red", highlightthickness=2, command=show_complex_info)
        info_button2.place(x=600, y=425)

        if content_category_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_content_based_category))
            back_button.pack(side="bottom")
        elif content_multiplayer_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_content_based_multiplayer))
            back_button.pack(side="bottom")
        else:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_content_based))
            back_button.pack(side="bottom")


# videogames collaborative filtering
class Videogames_collaborative_filtering(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global collaborative_check
        collaborative_check = 1
        global content_check
        content_check = 0
        global hybrid_check
        hybrid_check = 0
        global search_check
        search_check = 0
        global mygames_check
        mygames_check = 0
        global top_rated_check
        top_rated_check = 0

        def knn_user_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 1
            global collaborative_knn_item_check
            collaborative_knn_item_check = 0
            global collaborative_svd_check
            collaborative_svd_check = 0

            users = videogame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM videogames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            sim_options = {
                'name': 'msd',
                'user_based': True
            }

            model = KNNBaseline(k=90, sim_options=sim_options)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            # Create  anti-testset 
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_20_predictions = get_top_n_for_user(predictions, n=20)

            global recommendations
            recommendations = []

            check = 0

            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_20_predictions:
                recommendations.append(prediction.iid)
                game_name = videogames[videogames['appid'] == prediction.iid]['name'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1
            
            if check == len(top_20_predictions):
                cont.show_frame(parent, Videogames_results)

        def knn_item_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 0
            global collaborative_knn_item_check
            collaborative_knn_item_check = 1
            global collaborative_svd_check
            collaborative_svd_check = 0

            users = videogame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM videogames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            sim_options = {
                'name': 'msd',
                'user_based': False
            }

            model = KNNBaseline(k=10, sim_options=sim_options)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            # Create  anti-testset 
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_20_predictions = get_top_n_for_user(predictions, n=20)

            global recommendations
            recommendations = []

            check = 0
            
            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_20_predictions:
                recommendations.append(prediction.iid)
                game_name = videogames[videogames['appid'] == prediction.iid]['name'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1
            
            if check == len(top_20_predictions):
                cont.show_frame(parent, Videogames_results)

        def svd_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 0
            global collaborative_knn_item_check
            collaborative_knn_item_check = 0
            global collaborative_svd_check
            collaborative_svd_check = 1

            users = videogame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM videogames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()


            model = SVD(n_factors=10, n_epochs=20, lr_all=0.005, reg_all=0.02)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            # Create anti-testset
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions for a specific user
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_20_predictions = get_top_n_for_user(predictions, n=20)

            global recommendations
            recommendations = []

            check = 0

            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_20_predictions:
                recommendations.append(prediction.iid)
                game_name = videogames[videogames['appid'] == prediction.iid]['name'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1
            
            if check == len(top_20_predictions):
                cont.show_frame(parent, Videogames_results)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        content_label = tk.Label(self, text="Collaborative Filtering Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        content_label.pack(pady=50)

        choose_label  = tk.Label(self, text="Choose a Type", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=(10, 50))

        knn_user_button = tk.Button(self, text="KNN User Based",width = 15, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=knn_user_based)
        knn_user_button.pack(pady=20)

        knn_item_button = tk.Button(self, text="KNN Item Based",width=15, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=knn_item_based)
        knn_item_button.pack(pady=20)

        svd_button = tk.Button(self, text="SVD", width=15,font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=svd_based)
        svd_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_videogames))
        back_button.pack(side="bottom")


# Videogames hybrid filtering
class Videogames_hybrid_filtering(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global collaborative_check
        collaborative_check = 0
        global content_check
        content_check = 0
        global hybrid_check
        hybrid_check = 1
        global search_check
        search_check = 0
        global mygames_check
        mygames_check = 0
        global top_rated_check
        top_rated_check = 0

        global hybrid_category_check
        hybrid_category_check = 0
        global hybrid_multiplayer_check
        hybrid_multiplayer_check = 0

        def top_rated():
            global df_videogames
            df_videogames = videogames.sort_values('bayesian_rating', ascending=False)[:10000]
            df_videogames = df_videogames.reset_index(drop=True)

            global matching_games
            matching_games = []

            indices = pd.Series(df_videogames.index, index=df_videogames['appid']).drop_duplicates()

            top_rated_users_games = [game for game in user_games if game[2] > 5]

            for i in range(len(df_videogames)):
                if df_videogames.iloc[i]['appid'] in [game[1] for game in top_rated_users_games]:
                    idx = indices[df_videogames.iloc[i]['appid']]
                    matching_games.append(idx)
                    #print("the new indexes are "+ str(matching_games))

                
            if len(matching_games) == 0:
                messagebox.showerror("Error", "No games found with this category")
                cont.show_frame(parent, Videogames_hybrid_filtering)
            else:
                cont.show_frame(parent, Hybrid_videogames_choose_complexity)

        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        hybrid_label = tk.Label(self, text="Hybrid Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        hybrid_label.pack(pady=50)

        choose_label  = tk.Label(self, text="Choose a filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=(10, 50))

        category_button = tk.Button(self, text="Category",width = 10, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_videogames_category))
        category_button.pack(pady=20)

        multiplayer_button = tk.Button(self, text="Multiplayer",width=10, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_videogames_multiplayer))
        multiplayer_button.pack(pady=20)

        top_rated_button = tk.Button(self, text="Top Rated", width=10,font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=top_rated)
        top_rated_button.pack(pady=20)
     

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_videogames))
        back_button.pack(side="bottom")


# Hybrid videogames the content based part with category filtering
class Hybrid_videogames_category(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global hybrid_category_check
        hybrid_category_check = 1
        global hybrid_multiplayer_check
        hybrid_multiplayer_check = 0

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def category_recommendations():
            category = category_combobox.get()
            if category == "":
                messagebox.showerror("Error", "Please choose a category")
            else:
                category_remove = []
                for i in range(len(videogames)):
                    if videogames.iloc[i]['general_genre'] != category:
                        category_remove.append(videogames.iloc[i]['appid'])

                global df_videogames
                df_videogames = videogames[~videogames['appid'].isin(category_remove)].reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_videogames.index, index=df_videogames['appid']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]
                print(top_rated_users_games)

                for i in range(len(df_videogames)):
                    if df_videogames.iloc[i]['appid'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_videogames.iloc[i]['appid']]
                        matching_games.append(idx)
                        #print("the new indexes are "+ str(matching_games))

                
                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this category")
                    cont.show_frame(parent, Hybrid_videogames_category)
                else:
                    cont.show_frame(parent, Hybrid_videogames_choose_complexity)

        welcome_label = tk.Label(self, text="Category Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Choose a category", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        category_combobox = ttk.Combobox(self,width=18, values=["Action","Casual","Violent","Sports","Other"], font=("Arial", 15, "bold"))
        category_combobox.place(x=400, y=350)
        self.update_idletasks()
        label_height = category_combobox.winfo_reqheight()

        category_label = tk.Label(self, text="Category", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        category_label.place(x=200, y=350, height=label_height)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=category_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_hybrid_filtering))
        back_button.pack(side="bottom")


# Hybrid videogames the content based part with multiplayer filtering
class Hybrid_videogames_multiplayer(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global hybrid_category_check
        hybrid_category_check = 0
        global hybrid_multiplayer_check
        hybrid_multiplayer_check = 1

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def category_recommendations():
            category = category_combobox.get()
            if category == "":
                messagebox.showerror("Error", "Please choose a category")
            elif category != "MultiPlayer" and category != "SinglePlayer":
                messagebox.showerror("Error", "Please choose a valid category")
            else:
                category_remove = []
                if category == "MultiPlayer":
                    category = "Multiplayer"
                else:
                    category = "No_Multiplayer"
                for i in range(len(videogames)):
                    if videogames.iloc[i]['multiplayer'] != category:
                        category_remove.append(videogames.iloc[i]['appid'])

                global df_videogames
                df_videogames = videogames[~videogames['appid'].isin(category_remove)].reset_index(drop=True)
                df_videogames = df_videogames.sort_values('bayesian_rating', ascending=False)[:13000]
                df_videogames = df_videogames.reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_videogames.index, index=df_videogames['appid']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_videogames)):
                    if df_videogames.iloc[i]['appid'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_videogames.iloc[i]['appid']]
                        matching_games.append(idx)
                        #print("the new indexes are "+ str(matching_games))

                
                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this category")
                    cont.show_frame(parent, Hybrid_videogames_multiplayer)
                else:
                    cont.show_frame(parent, Hybrid_videogames_choose_complexity)

        welcome_label = tk.Label(self, text="Multiplayer Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Multiplayer or Singleplayer", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        category_combobox = ttk.Combobox(self,width=18, values=["MultiPlayer","SinglePlayer"], font=("Arial", 15, "bold"))
        category_combobox.place(x=400, y=350)
        self.update_idletasks()
        label_height = category_combobox.winfo_reqheight()

        category_label = tk.Label(self, text="Category", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        category_label.place(x=200, y=350, height=label_height)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=category_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_hybrid_filtering))
        back_button.pack(side="bottom")



# Hybrid videogames the content based part chooseing the  characteristics 
class Hybrid_videogames_choose_complexity(tk.Frame):   
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def simple():
            if 'simple' not in df_videogames.columns:
                df_videogames['simple'] = ''
            df_videogames['simple'] = df_videogames.apply(lambda row: row['genres'] + ' ' + row['steamspy_tags'] +' '+ row['categories'], axis=1)
            tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
            tfidf_matrix = tfidf.fit_transform(df_videogames['simple'])
            similarity = cosine_similarity(tfidf_matrix)

            global content
            content = []

            global matching_games         

            matching_games = [game for game in matching_games if game < len(df_videogames)]

            for game_index in matching_games:
                similar_games = list(enumerate(similarity[game_index]))
                similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
                similar_games = similar_games[1:11]  # Exclude the game itself and take the top 10 similar games
                print(similar_games)

                for sim_game in similar_games:
                    sim_game_index = sim_game[0]
                    content.append((sim_game_index, sim_game[1]))

            content_dict = {}
            for appid_index, similarity_score in content:
                if appid_index in content_dict:
                    content_dict[appid_index] += similarity_score
                else:
                    content_dict[appid_index] = similarity_score

            content = sorted(content_dict.items(), key=lambda x: x[1], reverse=True)
            content = [rec for rec in content if rec[0] not in matching_games]

            tuple_content = content
            content = []

            #print("Recommended games: ")
            for i, (appid_index, similarity_score) in enumerate(tuple_content):
                if i >= 10:
                    break
                appid = df_videogames.iloc[appid_index]['appid']
                game_name = df_videogames.iloc[appid_index]['name']
                bayesian_rating = df_videogames.iloc[appid_index]['bayesian_rating']
                #print(f"{game_name} with a rating of {bayesian_rating} and a similarity score of {similarity_score}")
                content.append(appid)

            cont.show_frame(parent, Hybrid_collaborative_method)

        def complex():
            if 'complex' not in df_videogames.columns:
                df_videogames['complex'] = ''
            df_videogames['complex'] = df_videogames.apply(lambda row: row['genres'] + ' ' + row['steamspy_tags'] +' '+ row['categories'] + ' ' + row['publisher'] + ' ' + row['developer'] + ' ' + ' '.join(map(str,row['keywords'])), axis=1)
            tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
            tfidf_matrix = tfidf.fit_transform(df_videogames['complex'])
            similarity = cosine_similarity(tfidf_matrix)

            global content
            content = []

            global matching_games         

            matching_games = [game for game in matching_games if game < len(df_videogames)]

            for game_index in matching_games:
                similar_games = list(enumerate(similarity[game_index]))
                similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
                similar_games = similar_games[1:11]  # Exclude the game itself and take the top 10 similar games
                print(similar_games)

                for sim_game in similar_games:
                    sim_game_index = sim_game[0]
                    content.append((sim_game_index, sim_game[1]))

            content_dict = {}
            for appid_index, similarity_score in content:
                if appid_index in content_dict:
                    content_dict[appid_index] += similarity_score
                else:
                    content_dict[appid_index] = similarity_score

            content = sorted(content_dict.items(), key=lambda x: x[1], reverse=True)
            content = [rec for rec in content if rec[0] not in matching_games]

            tuple_content = content
            content = []

            #print("Recommended games: ")
            for i, (appid_index, similarity_score) in enumerate(tuple_content):
                if i >= 10:
                    break
                appid = df_videogames.iloc[appid_index]['appid']
                game_name = df_videogames.iloc[appid_index]['name']
                bayesian_rating = df_videogames.iloc[appid_index]['bayesian_rating']
                #print(f"{game_name} with a rating of {bayesian_rating} and a similarity score of {similarity_score}")
                content.append(appid)


            cont.show_frame(parent, Hybrid_collaborative_method)    

        welcome_label = tk.Label(self, text="Choose Complexity", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=100)

        simple_button = tk.Button(self,width=10, text="Simple", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=simple)
        simple_button.pack(pady=50)

        complex_button = tk.Button(self,width=10, text="Complex", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=complex)
        complex_button.pack()

        if hybrid_category_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_videogames_category))
            back_button.pack(side="bottom")
        elif hybrid_multiplayer_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_videogames_multiplayer))
            back_button.pack(side="bottom")
        else:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_hybrid_filtering))
            back_button.pack(side="bottom")   


# Hybrid videogames the collaborative filtering part
class Hybrid_collaborative_method(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        def knn_user_based():

            users = videogame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM videogames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            sim_options = {
                'name': 'msd',
                'user_based': True
            }

            model = KNNBaseline(k=90, sim_options=sim_options)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            #anti-testset
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_rated_game_ids = user_rated_game_ids + content    
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_10_predictions = get_top_n_for_user(predictions, n=10)

            collaborative = []

            check = 0

            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_10_predictions:
                collaborative.append(prediction.iid)
                game_name = videogames[videogames['appid'] == prediction.iid]['name'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1
            
            for game in content:
                if game in collaborative:
                    content.remove(game)


            global recommendations
            recommendations = collaborative + content

            if check == len(top_10_predictions):
                cont.show_frame(parent, Videogames_results)

        def knn_item_based():

            users = videogame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM videogames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            sim_options = {
                'name': 'msd',
                'user_based': False
            }

            model = KNNBaseline(k=10, sim_options=sim_options)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            #anti-testset 
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_rated_game_ids = user_rated_game_ids + content
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_10_predictions = get_top_n_for_user(predictions, n=10)

            collaborative = []

            check = 0

            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_10_predictions:
                collaborative.append(prediction.iid)
                game_name = videogames[videogames['appid'] == prediction.iid]['name'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1

            for game in content:
                if game in collaborative:
                    content.remove(game)

            global recommendations
            recommendations = collaborative + content
            
            if check == len(top_10_predictions):
                cont.show_frame(parent, Videogames_results)

        def svd_based():

            users = videogame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM videogames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            model = SVD(n_factors=10, n_epochs=20, lr_all=0.005, reg_all=0.02)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            #anti-testset 
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_rated_game_ids = user_rated_game_ids + content
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_10_predictions = get_top_n_for_user(predictions, n=10)

            collaborative = []

            check = 0

            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_10_predictions:
                collaborative.append(prediction.iid)
                game_name = videogames[videogames['appid'] == prediction.iid]['name'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1

            for game in content:
                if game in collaborative:
                    content.remove(game)

            global recommendations
            recommendations = collaborative + content

            
            if check == len(top_10_predictions):
                cont.show_frame(parent, Videogames_results)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        content_label = tk.Label(self, text="Hybrid Filtering Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        content_label.pack(pady=50)

        choose_label  = tk.Label(self, text="Choose a Type", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=(10, 50))

        knn_user_button = tk.Button(self, text="KNN User Based",width = 15, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=knn_user_based)
        knn_user_button.pack(pady=20)

        knn_item_button = tk.Button(self, text="KNN Item Based",width=15, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=knn_item_based)
        knn_item_button.pack(pady=20)

        svd_button = tk.Button(self, text="SVD", width=15,font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=svd_based)
        svd_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_videogames_choose_complexity))
        back_button.pack(side="bottom")


# The recommendations results
class Videogames_results(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        def show_more_info(appid):
            global videogame_appid
            videogame_appid = 0
            videogame_appid = appid
            print(videogame_appid)
            cont.show_frame(parent, Videogame_info)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        global recommendations

        if mygames_check == 1:
            welcome_label = tk.Label(self, text="My Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif search_check == 1:
            welcome_label = tk.Label(self, text="Search Results", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif top_rated_check == 1:
            welcome_label = tk.Label(self, text="Top Rated Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif content_check == 1:
            welcome_label = tk.Label(self, text="Content Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif collaborative_check == 1 and collaborative_knn_user_check == 1:
            welcome_label = tk.Label(self, text="Collaborative KNN User-Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif collaborative_check == 1 and collaborative_knn_item_check == 1:
            welcome_label = tk.Label(self, text="Collaborative KNN Item-Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif collaborative_check == 1 and collaborative_svd_check == 1:
            welcome_label = tk.Label(self, text="Collaborative SVD Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif hybrid_check == 1:
            welcome_label = tk.Label(self, text="Hybrid Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)

        frame = Frame(self)
        frame.pack(side=LEFT, fill=BOTH, expand=True, padx=300, pady=(10, 100))

        self.canvas = Canvas(frame, bg='black')
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.mailbox_frame = Frame(self.canvas, bg='purple')
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.mailbox_frame, anchor=NW)

        mail_scroll = Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        mail_scroll.pack(side=RIGHT, fill=Y)

        self.canvas.config(yscrollcommand=mail_scroll.set)

        self.mailbox_frame.bind("<Configure>", self.OnFrameConfigure)
        self.canvas.bind('<Configure>', self.FrameWidth)

        for game_appid in recommendations:
            each_game_frame = tk.Frame(self.mailbox_frame, bg="black", bd=5, highlightbackground="blue", highlightcolor="red", highlightthickness=2)
            each_game_frame.pack(fill="both", expand="yes", side="top", padx=10, pady=10)

            game_image_url = videogames[videogames['appid'] == game_appid]['header_image'].values[0]
            game_image = Image.open(requests.get(game_image_url, stream=True).raw)
            game_image = game_image.resize((320, 200), Image.LANCZOS)
            game_photo = ImageTk.PhotoImage(game_image)
            game_image_label = tk.Label(each_game_frame, image=game_photo)
            game_image_label.image = game_photo
            game_image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

            hidden_button = tk.Button(each_game_frame, image=game_photo, command=lambda appid=game_appid: show_more_info(appid), bd=0, highlightthickness=0)
            hidden_button.grid(row=0, column=0, padx=10, pady=10)

        
        if search_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Search_videogames))
            back_button.place(x=450,y=736)
        elif top_rated_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_top_rated))
            back_button.place(x=450,y=736)
        elif content_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_choose_complexity))
            back_button.place(x=450,y=736)
        elif collaborative_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_collaborative_filtering))
            back_button.place(x=450,y=736)
        elif hybrid_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_collaborative_method))
            back_button.place(x=450,y=736)

    def FrameWidth(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        # Debugging output to track canvas width updates
        print(f"Canvas width set to: {canvas_width}")

    def OnFrameConfigure(self, event):
        # Update the scroll region to encompass the entire canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Debugging output to track scroll region updates
        print(f"Scroll region updated to: {self.canvas.bbox('all')}")


# The information of the videogame
class Videogame_info(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        global videogame_appid

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        game_name = videogames[videogames['appid'] == videogame_appid]['name'].values[0]
        game_rating = videogames[videogames['appid'] == videogame_appid]['bayesian_rating'].values[0]
        game_rating = str(game_rating)[:4]

        name_label = tk.Label(self, text=game_name, font=("Arial", 25, "bold"),wraplength=750, bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        name_label.pack(pady=10)

        game_image_url = videogames[videogames['appid'] == videogame_appid]['header_image'].values[0]
        game_image = Image.open(requests.get(game_image_url, stream=True).raw)
        game_image = game_image.resize((400, 250), Image.LANCZOS)
        game_photo = ImageTk.PhotoImage(game_image)
        game_image_label = tk.Label(self, image=game_photo)
        game_image_label.image = game_photo
        game_image_label.pack(pady=5)

        rating_label = tk.Label(self, text="Community Rating: " + str(game_rating), font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        rating_label.place(x=150, y=380)


        release_date = videogames[videogames['appid'] == videogame_appid]['release_date'].values[0]
        release_date_label = tk.Label(self, text="Release Date: " + release_date, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        release_date_label.place(x=500, y=380)

        developer = videogames[videogames['appid'] == videogame_appid]['developer'].values[0]
        developer_label = tk.Label(self, text="Developer: " + developer.split(';')[0], font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        developer_label.place(relx=0.5, y=470, anchor='center')

        category = videogames[videogames['appid'] == videogame_appid]['general_genre'].values[0]
        multiplayer = videogames[videogames['appid'] == videogame_appid]['multiplayer'].values[0]
        if multiplayer == 'Multiplayer':
            category += " - Multiplayer"
        else:
            category += " - Single Player"
        category_label = tk.Label(self, text="Category: " + category, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        category_label.place(relx=0.5, y=535, anchor='center')

        def open_description():
            description_toplevel = tk.Toplevel(self)
            description_toplevel.title("Description")
            description_toplevel.geometry("600x400")
            description_label = tk.Label(description_toplevel,wraplength=350, text=description)
            description_label.pack(pady=10)

        description = videogames[videogames['appid'] == videogame_appid]['short_description'].values[0]
        description_button = tk.Button(self, text="Description", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2, command=open_description)
        description_button.place(x=305, y=580)

        game_site = videogames[videogames['appid'] == videogame_appid]['game_site'].values[0]
        website_button = tk.Button(self, text="Website", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2, command=lambda: webbrowser.open(game_site))
        website_button.place(x=500, y=580)

        user_games_ids = [game[1] for game in user_games]

        if videogame_appid in user_games_ids:
            for game in user_games:
                if game[1] == videogame_appid:
                    rating_label = tk.Label(self, text="Your Rating: " + str(game[2]), font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
                    rating_label.place(x=110,y=655)
                    rating_combobox = ttk.Combobox(self, values=list(range(1, 11)))
                    rating_combobox.place(x=340, y=655)

                    old_rating = game[2]

                    change_rating_button = tk.Button(self, text="Change Rating", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: change_rating(rating_combobox.get(), videogame_appid,old_rating))
                    change_rating_button.place(x=490, y=655)   

                    def delete_rating_confirmation():
                        result = messagebox.askyesno("Confirmation", "Are you sure you want to delete the rating?")
                        if result == True:
                            delete_rating(videogame_appid)

                    delete_rating_button = tk.Button(self, text="Delete Rating", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=delete_rating_confirmation)
                    delete_rating_button.place(x=730, y=655)

        else:
            rating_combobox = ttk.Combobox(self, values=list(range(1, 11)))
            rating_combobox.place(x=350, y=655)

            rate_button = tk.Button(self, text="Rate", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: rate_game(rating_combobox.get(), videogame_appid))
            rate_button.place(x=500, y=655)

        if mygames_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, My_videogames))
            back_button.place(x=450,y=736)
        elif search_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_results ))
            back_button.place(x=450,y=736)
        elif top_rated_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_results))
            back_button.place(x=450,y=736)
        elif content_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_results))
            back_button.place(x=450,y=736)
        elif collaborative_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_results))
            back_button.place(x=450,y=736)
        else:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Videogames_results))
            back_button.place(x=450,y=736) 

        def rate_game(rating, appid):
            if rating == "":
                messagebox.showerror("Error", "Please enter a rating")
            elif rating.isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            elif int(rating) < 1 or int(rating) > 10:
                messagebox.showerror("Error", "Please enter a rating between 1 and 10")
            else:
                rating = int(rating)
                appid = int(appid)
                mycursor = mydb.cursor()
                sqlquery = "insert into videogames_user (user_id, game_id, rating) values (%s, %s, %s)"
                val = (user_id, appid, rating)
                mycursor.execute(sqlquery, val)
                mydb.commit()
                mycursor.close()
                messagebox.showinfo("Success", "Game rated successfully")

                user_games.append([user_id, appid, rating])
                cont.show_frame(parent, Videogame_info) 

        def change_rating(rating, appid,old_rating):
            if rating == "":
                messagebox.showerror("Error", "Please enter a rating")
            elif rating.isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            elif int(rating) < 1 or int(rating) > 10:
                messagebox.showerror("Error", "Please enter a rating between 1 and 10")
            elif int(rating) == int(old_rating):
                messagebox.showerror("Error", "Please enter a different rating")
            else:
                rating = int(rating)
                appid = int(appid)
                mycursor = mydb.cursor()
                sqlquery = "update videogames_user set rating = %s where user_id = %s and game_id = %s"
                val = (rating, user_id, appid)
                mycursor.execute(sqlquery, val)
                mydb.commit()
                mycursor.close()
                messagebox.showinfo("Success", "Rating changed successfully")

                for game in user_games:
                    if game[1] == appid:
                        game[2] = rating
                cont.show_frame(parent, Videogame_info)

        def delete_rating(appid):
            appid = int(appid)
            mycursor = mydb.cursor()
            sqlquery = "delete from videogames_user where user_id = %s and game_id = %s"
            val = (user_id, appid)
            mycursor.execute(sqlquery, val)
            mydb.commit()
            mycursor.close()
            messagebox.showinfo("Success", "Rating deleted successfully")

            for game in user_games:
                if game[1] == appid:
                    user_games.remove(game)
            if mygames_check == 1:
                cont.show_frame(parent, My_videogames)
            else:
                cont.show_frame(parent, Videogame_info)



# boardgames registration and login
class Boardgame_user_reg_login(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        self.login_button = tk.Button(self,width=10, text="Login",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgame_login))
        self.login_button.pack(padx=50, pady=(300,50))
        self.register_button = tk.Button(self,width=10, text="Register",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgame_register))
        self.register_button.pack()

        self.back_button = tk.Button(self, text="Back",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, User_type))
        self.back_button.pack(side="bottom")



# boardgames registration menu
class Boardgame_register(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def register():
            if username_entry.get() != "" and password_entry.get() != "" and confirm_password_entry.get() != "":
                if len(username_entry.get()) >= 5:
                    if password_entry.get() == confirm_password_entry.get():
                        if len(password_entry.get()) >= 8:
                            mycursor = mydb.cursor()
                            mycursor.execute("SELECT * FROM boardgames_login WHERE username = %s", (username_entry.get(),))
                            myresult = mycursor.fetchall()
                            if myresult:
                                messagebox.showerror("Error", "Username already exists")
                                mycursor.close()
                            else:
                                mycursor.execute("INSERT INTO boardgames_login (username, password) VALUES (%s, %s)", (username_entry.get(), password_entry.get()))
                                mydb.commit()
                                messagebox.showinfo("Success", "User registered successfully")
                                mycursor.close()

                                mycursor = mydb.cursor()
                                mycursor.execute("SELECT * FROM boardgames_login WHERE username = %s AND password = %s", (username_entry.get(), password_entry.get()))
                                myresult = mycursor.fetchall()
                                mycursor.close()
                                global user_id
                                user_id = myresult[0][2]
                                cont.show_frame(parent, Boardgames_menu)
                        else:
                            messagebox.showerror("Error", "Password must be at least 8 characters long")
                    else:
                        messagebox.showerror("Error", "Passwords do not match")
                else:
                    messagebox.showerror("Error", "Username must be at least 5 characters long")
            else:
                messagebox.showerror("Error", "Please enter Username, Password and Confirm Password")


        username_label = tk.Label(self, text="Username", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        username_label.pack(pady=(170,10))
        username_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",insertbackground="white")
        username_entry.pack(pady=(10,20))

        password_label = tk.Label(self, text="Password", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        password_label.pack(pady=10)
        password_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",show="*",insertbackground="white")
        password_entry.pack(pady=(10,20))

        confirm_password_label = tk.Label(self, text="Confirm Password", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5,
                                        highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        confirm_password_label.pack(pady=10)
        confirm_password_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",show="*",insertbackground="white")
        confirm_password_entry.pack(pady=(10,20))

        register_button = tk.Button(self, text="Register", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=register)
        register_button.pack(pady=10)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgame_user_reg_login))
        back_button.pack(side="bottom")


# boardgames login menu
class Boardgame_login(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def login():
            if username_entry.get() != "" and password_entry.get() != "":
                mycursor = mydb.cursor()
                mycursor.execute("SELECT * FROM boardgames_login WHERE username = %s AND password = %s", (username_entry.get(), password_entry.get()))
                myresult = mycursor.fetchall()
                if myresult:
                    print("Welcome " + username_entry.get() + "!")
                    mycursor.close()
                    global user_id
                    user_id = myresult[0][2]
                    cont.show_frame(parent, Boardgames_menu)
                else:
                    messagebox.showerror("Error", "Invalid Username or Password")
                    mycursor.close()
            else:
                messagebox.showerror("Error", "Please enter Username and Password")

        username_label = tk.Label(self, text="Username", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        username_label.pack(pady=(250,10))
        username_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",insertbackground="white")
        username_entry.pack(pady=(10,20))

        password_label = tk.Label(self, text="Password", font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        password_label.pack(pady=10)
        password_entry = tk.Entry(self, font=("Arial", 20, "bold"), bg="black", fg="white",show="*",insertbackground="white")
        password_entry.pack(pady=(10,20))


        login_button = tk.Button(self, text="Login", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=login)
        login_button.pack(pady=10)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgame_user_reg_login))
        back_button.pack(side="bottom")


# boardgames menu
class Boardgames_menu(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        mycursor = mydb.cursor()
        sqlquery = "select * from boardgames_login where id = %s"
        val = (user_id, )
        mycursor.execute(sqlquery, val)
        myresult = mycursor.fetchall()
        mycursor.close()

        username = myresult[0][0]

        mycursor = mydb.cursor()
        sqlquery = "select * from boardgames_user where user_id = %s"
        val = (user_id, )
        mycursor.execute(sqlquery, val)
        myresult = mycursor.fetchall()
        mycursor.close()

        global user_games
        user_games = []
        for game in myresult:
            user_games.append([game[0], game[1],game[2]])

        welcome_label = tk.Label(self, text="Welcome, " + username, font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=(50, 100))

        self.mygames_button = tk.Button(self,width = 15, text="My Games",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, My_boardgames))
        self.mygames_button.pack(padx=50, pady=50)

        self.recommendations_button = tk.Button(self,width = 15, text="Recommendations",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_boardgames))
        self.recommendations_button.pack()

        self.logout_button = tk.Button(self,width = 15, text="Logout",font=("Arial", 20, "bold"),bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, User_type))
        self.logout_button.pack(side="bottom")



# boardgames recommendations menu
class Recommendations_boardgames(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def content_check():
            if user_games == []:
                messagebox.showerror("Error", "You have no games in your library")
                cont.show_frame(parent, Recommendations_boardgames)
            else:
                cont.show_frame(parent, Boardgames_content_based)

        def collaborative_check():
            if user_games == []:
                messagebox.showerror("Error", "You have no games in your library")
                cont.show_frame(parent, Recommendations_boardgames)
            else:
                cont.show_frame(parent, Boardgames_collaborative_filtering)

        def hybrid_check():
            if user_games == []:
                messagebox.showerror("Error", "You have no games in your library")
                cont.show_frame(parent, Recommendations_boardgames)
            else:
                cont.show_frame(parent, Boardgames_hybrid_filtering)


        welcome_label = tk.Label(self, text="Choose a Recommendation", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        self.toprated_button = tk.Button(self,width = 20, text="Top Rated Games", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_top_rated))
        self.toprated_button.pack(padx=50, pady=20)

        self.search_button = tk.Button(self,width = 20, text="Search Games", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Search_boardgames))
        self.search_button.pack(padx=50, pady=20)
        
        self.content_button = tk.Button(self,width=20, text="Content-Based Filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=content_check)
        self.content_button.pack(padx=50, pady=20)

        self.collaborative_button = tk.Button(self,width=20, text="Collaborative Filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=collaborative_check)
        
        self.collaborative_button.pack(padx=50, pady=20)

        self.hybrid_button = tk.Button(self,width=20, text="Hybrid Filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=hybrid_check)
        self.hybrid_button.pack(padx=50, pady=20)

        self.back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_menu))
        self.back_button.pack(side="bottom")


#boardgames top rated menu
class Boardgames_top_rated(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global top_rated_check
        top_rated_check = 1
        global mygames_check
        mygames_check = 0
        global search_check
        search_check = 0
        global content_check
        content_check = 0
        global collaborative_check
        content_check = 0
        global hybrid_check
        hybrid_check = 0

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def top_rated_games():
            number = int(number_of_games.get())
            global recommendations
            recommendations = []
            recommendations = boardgames.head(number)['id'].tolist()
            cont.show_frame(parent, Boardgames_results)    
           
        def check():
            if number_of_games.get().isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            elif int(number_of_games.get()) > 100 or int(number_of_games.get()) < 1:
                messagebox.showerror("Error", "Please enter a number between 1 and 100")
            elif number_of_games.get() == "":
                messagebox.showerror("Error", "Please enter a number")
            else:
                top_rated_games()

        welcome_label = tk.Label(self, text="Top Rated Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Number of games in the result", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        number_of_games = tk.Entry(self,width = 10, font=("Arial", 20, "bold"), bg="black", fg="white", insertbackground="white")
        number_of_games.pack()

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=check)
        search_button.pack(pady=10)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_boardgames))
        back_button.pack(side="bottom")


# the user's boardgames
class My_boardgames(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global top_rated_check
        top_rated_check = 0
        global mygames_check
        mygames_check = 1
        global search_check
        search_check = 0
        global content_check
        content_check = 0
        global collaborative_check
        content_check = 0
        global hybrid_check
        hybrid_check = 0

        def show_more_info(appid):
            global boardgame_appid
            boardgame_appid = 0
            boardgame_appid = appid
            print(boardgame_appid)
            cont.show_frame(parent, Boardgame_info)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        global user_games

        welcome_label = tk.Label(self, text="My Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        frame = Frame(self)
        frame.pack(side=LEFT, fill=BOTH, expand=True, padx=300, pady=(10, 100))

        self.canvas = Canvas(frame, bg='black')
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.mailbox_frame = Frame(self.canvas, bg='purple')
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.mailbox_frame, anchor=NW)

        mail_scroll = Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        mail_scroll.pack(side=RIGHT, fill=Y)

        self.canvas.config(yscrollcommand=mail_scroll.set)

        self.mailbox_frame.bind("<Configure>", self.OnFrameConfigure)
        self.canvas.bind('<Configure>', self.FrameWidth)

        user_games = sorted(user_games, key=lambda x: x[2], reverse=True)
        user_games_ids = [game[1] for game in user_games]

        if user_games != []:
            for game_appid in user_games_ids:
                each_game_frame = tk.Frame(self.mailbox_frame, bg="black", bd=5, highlightbackground="blue", highlightcolor="red", highlightthickness=2)
                each_game_frame.pack(fill="both", expand="yes", side="top", padx=10, pady=5)

                game_image_url = boardgames[boardgames['id'] == game_appid]['image'].values[0]
                game_image = Image.open(requests.get(game_image_url, stream=True).raw)
                game_image = game_image.resize((320, 200), Image.LANCZOS)
                game_photo = ImageTk.PhotoImage(game_image)
                game_image_label = tk.Label(each_game_frame, image=game_photo)
                game_image_label.image = game_photo
                game_image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

                hidden_button = tk.Button(each_game_frame, image=game_photo, command=lambda appid=game_appid: show_more_info(appid), bd=0, highlightthickness=0)
                hidden_button.grid(row=0, column=0, padx=10, pady=10)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_menu))
        back_button.place(x=450,y=736)

    def FrameWidth(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        # Debugging output to track canvas width updates
        print(f"Canvas width set to: {canvas_width}")

    def OnFrameConfigure(self, event):
        # Update the scroll region to encompass the entire canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Debugging output to track scroll region updates
        print(f"Scroll region updated to: {self.canvas.bbox('all')}")


# boardgmaes content based filtering
class Boardgames_content_based(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global content_check
        content_check = 1
        global collaborative_check
        collaborative_check = 0
        global hybrid_check
        hybrid_check  = 0
        global search_check
        search_check = 0
        global mygames_check
        mygames_check = 0
        global top_rated_check
        top_rated_check = 0

        global content_category_check
        content_category_check = 0
        global content_players_check
        content_players_check = 0
        global content_minage_check
        content_minage_check = 0

        def top_rated():
            global df_boardgames
            df_boardgames = boardgames.sort_values('bayesaverage', ascending=False)[:10000]
            df_boardgames = df_boardgames.reset_index(drop=True)

            global matching_games
            matching_games = []

            indices = pd.Series(df_boardgames.index, index=df_boardgames['id']).drop_duplicates()

            top_rated_users_games = [game for game in user_games if game[2] > 5]

            for i in range(len(df_boardgames)):
                if df_boardgames.iloc[i]['id'] in [game[1] for game in top_rated_users_games]:
                    idx = indices[df_boardgames.iloc[i]['id']]
                    matching_games.append(idx)

                
            if len(matching_games) == 0:
                messagebox.showerror("Error", "No games found with this category")
                cont.show_frame(parent, Boardgames_content_based)
            else:
                cont.show_frame(parent, Boardgames_choose_complexity)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        content_label = tk.Label(self, text="Content Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        content_label.pack(pady=50)

        choose_label  = tk.Label(self, text="Choose a filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=(10, 50))

        category_button = tk.Button(self, text="Category",width = 12, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based_category))
        category_button.pack(pady=20)

        multiplayer_button = tk.Button(self, text="Minimum Age",width=12, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based_minage))
        multiplayer_button.pack(pady=20)

        players_button = tk.Button(self, text="Players",width=12, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based_players))
        players_button.pack(pady=20)

        top_rated_button = tk.Button(self, text="Top Rated", width=12,font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=top_rated)
        top_rated_button.pack(pady=20)
     
        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_boardgames))
        back_button.pack(side="bottom")


#boardgames content based filtering category
class Boardgames_content_based_category(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global content_category_check
        content_category_check = 1
        global content_players_check
        content_players_check = 0
        global content_minage_check
        content_minage_check = 0
        global content_multiplayer_check
        content_multiplayer_check = 0

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def category_recommendations():
            category = category_combobox.get()
            if category == "":
                messagebox.showerror("Error", "Please choose a category")
            else:
                category_remove = []
                for i in range(len(boardgames)):
                    if boardgames.iloc[i]['general_category'] != category:
                        category_remove.append(boardgames.iloc[i]['id'])

                global df_boardgames
                df_boardgames = boardgames[~boardgames['id'].isin(category_remove)].reset_index(drop=True)
                df_boardgames = df_boardgames.sort_values('bayesaverage', ascending=False)[:13000]
                df_boardgames = df_boardgames.reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_boardgames.index, index=df_boardgames['id']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_boardgames)):
                    if df_boardgames.iloc[i]['id'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_boardgames.iloc[i]['id']]
                        matching_games.append(idx)

                
                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this category")
                    cont.show_frame(parent, Boardgames_content_based_category)
                else:
                    cont.show_frame(parent, Boardgames_choose_complexity)

        welcome_label = tk.Label(self, text="Category Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Choose a category", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        category_combobox = ttk.Combobox(self,width=18, values=['Fantasy/Mythology','Educational','Historical','Strategy/War','Social/Cultural','Mechanics','Other'], font=("Arial", 15, "bold"))
        category_combobox.place(x=400, y=350)
        self.update_idletasks()
        label_height = category_combobox.winfo_reqheight()

        category_label = tk.Label(self, text="Category", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        category_label.place(x=200, y=350, height=label_height)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=category_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based))
        back_button.pack(side="bottom")


#boardgames content based filtering minimum age
class Boardgames_content_based_minage(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global content_category_check
        content_category_check = 0
        global content_players_check
        content_players_check = 0
        global content_minage_check
        content_minage_check = 1

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def min_age_recommendations():
            min_age = min_age_entry.get()
            if min_age == "":
                messagebox.showerror("Error", "Please enter a minimum age")
            elif min_age.isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            else:
                min_age_remove = []
                for i in range(len(boardgames)):
                    if boardgames.iloc[i]['minage'] < int(min_age):
                        min_age_remove.append(boardgames.iloc[i]['id'])

                global df_boardgames
                df_boardgames = boardgames[~boardgames['id'].isin(min_age_remove)].reset_index(drop=True)
                df_boardgames = df_boardgames.sort_values('bayesaverage', ascending=False)[:13000]
                df_boardgames = df_boardgames.reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_boardgames.index, index=df_boardgames['id']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_boardgames)):
                    if df_boardgames.iloc[i]['id'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_boardgames.iloc[i]['id']]
                        matching_games.append(idx)
                
                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this minimum age")
                    cont.show_frame(parent, Boardgames_content_based_minage)
                else:
                    cont.show_frame(parent, Boardgames_choose_complexity)

        welcome_label = tk.Label(self, text="Minimum Age Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Choose a Minimum Age", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        min_age_entry = tk.Entry(self, font=("Arial", 15, "bold"), bg="black", fg="white", insertbackground="white")
        min_age_entry.place(x=400, y=350)
        self.update_idletasks()
        label_height = min_age_entry.winfo_reqheight()

        min_age_label = tk.Label(self, text="Minimum Age", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=12)
        min_age_label.place(x=200, y=350, height=label_height)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=min_age_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based))
        back_button.pack(side="bottom")


#boardgames content based filtering number of players
class Boardgames_content_based_players(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global content_category_check
        content_category_check = 0
        global content_players_check
        content_players_check = 1
        global content_minage_check
        content_minage_check = 0

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def players_recommendations():
            min_players = minplayers_combobox.get()
            max_players = maxplayers_combobox.get()

            if min_players == "" and max_players == "":
                messagebox.showerror("Error", "Please enter a number")
            elif min_players != "" and min_players.isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            elif max_players != "" and max_players.isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            elif (min_players != "" and max_players != "") and int(min_players) > int(max_players):
                messagebox.showerror("Error", "Minimum players must be less than maximum players")
            else:
                players_remove = []
                for i in range(len(boardgames)):
                    if min_players != "" and max_players != "":
                        if boardgames.iloc[i]['minplayers'] != int(min_players) or boardgames.iloc[i]['maxplayers'] != int(max_players):
                            players_remove.append(boardgames.iloc[i]['id'])
                    elif min_players != "" and max_players == "":
                        if boardgames.iloc[i]['minplayers'] != int(min_players):
                            players_remove.append(boardgames.iloc[i]['id'])
                    elif min_players == "" and max_players != "":
                        if boardgames.iloc[i]['maxplayers'] != int(max_players):
                            players_remove.append(boardgames.iloc[i]['id'])

                global df_boardgames
                df_boardgames = boardgames[~boardgames['id'].isin(players_remove)].reset_index(drop=True)
                df_boardgames = df_boardgames.sort_values('bayesaverage', ascending=False)[:13000]
                df_boardgames = df_boardgames.reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_boardgames.index, index=df_boardgames['id']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_boardgames)):
                    if df_boardgames.iloc[i]['id'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_boardgames.iloc[i]['id']]
                        matching_games.append(idx)

                
                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this players number")
                    cont.show_frame(parent, Boardgames_content_based_players)
                else:
                    cont.show_frame(parent, Boardgames_choose_complexity)

        welcome_label = tk.Label(self, text="Minimum Age Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Choose  number of players", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        minplayers_combobox = ttk.Combobox(self,width=18, values=["1","2","3","4","5","6","7","8","9","10"], font=("Arial", 15, "bold"))
        minplayers_combobox.place(x=400, y=350)
        self.update_idletasks()
        label_height = minplayers_combobox.winfo_reqheight()

        minplayers_label = tk.Label(self, text="Minimum Players", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        minplayers_label.place(x=200, y=350, height=label_height)

        maxplayers_label = tk.Label(self, text="Maximum Players", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        maxplayers_label.place(x=200, y=400, height=label_height)

        maxplayers_combobox = ttk.Combobox(self,width=18, values=["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"], font=("Arial", 15, "bold"))
        maxplayers_combobox.place(x=400, y=400)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=players_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based))
        back_button.pack(side="bottom")


#boardgames content based filtering choose characteristics
class Boardgames_choose_complexity(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def simple():
            if 'simple' not in df_boardgames.columns:
                df_boardgames['simple'] = ''
            df_boardgames['simple'] = df_boardgames.apply(
    lambda row: (str(row['boardgamecategory']) if pd.notna(row['boardgamecategory']) else '') + ' ' +
                (str(row['boardgamefamily']) if pd.notna(row['boardgamefamily']) else ''),axis=1)
            tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
            #tfidf = CountVectorizer(stop_words='english', max_features=10000)
            tfidf_matrix = tfidf.fit_transform(df_boardgames['simple'])
            similarity = cosine_similarity(tfidf_matrix)
            #similarity = euclidean_distances(tfidf_matrix, tfidf_matrix)

            global recommendations
            recommendations = []

            global matching_games         

            matching_games = [game for game in matching_games if game < len(df_boardgames)]

            for game_index in matching_games:
                similar_games = list(enumerate(similarity[game_index]))
                similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
                #similar_games = sorted(similar_games, key=lambda x: x[1])
                similar_games = similar_games[1:21]  

                for sim_game in similar_games:
                    sim_game_index = sim_game[0]
                    recommendations.append((sim_game_index, sim_game[1]))

            recommendation_dict = {}
            for appid_index, similarity_score in recommendations:
                if appid_index in recommendation_dict:
                    recommendation_dict[appid_index] += similarity_score
                else:
                    recommendation_dict[appid_index] = similarity_score

            recommendations = sorted(recommendation_dict.items(), key=lambda x: x[1], reverse=True)
            #recommendations = sorted(recommendation_dict.items(), key=lambda x: x[1])

            recommendations = [rec for rec in recommendations if rec[0] not in matching_games]

            tuple_recommendations = recommendations
            recommendations = []

            #print("Recommended games: ")
            for i, (appid_index, similarity_score) in enumerate(tuple_recommendations):
                if i >= 20:
                    break
                appid = df_boardgames.iloc[appid_index]['id']
                game_name = df_boardgames.iloc[appid_index]['game']
                bayesian_rating = df_boardgames.iloc[appid_index]['bayesaverage']
                #print(f"{game_name} with a rating of {bayesian_rating} and a similarity score of {similarity_score}")
                #print(f"{game_name} with a similarity score of {similarity_score}")
                recommendations.append(appid)


            cont.show_frame(parent, Boardgames_results)

        def complex():
            if 'complex' not in df_boardgames.columns:
                df_boardgames['complex'] = ''
            df_boardgames['keywords'] = df_boardgames['keywords'].apply(lambda x: ' '.join(map(str, x)))
            df_boardgames['complex'] = df_boardgames.apply(lambda row: 
                (str(row['boardgamecategory']) if pd.notna(row['boardgamecategory']) else '') + ' ' +
                (str(row['boardgamemechanic']) if pd.notna(row['boardgamemechanic']) else '') + ' ' +
                (str(row['boardgamefamily']) if pd.notna(row['boardgamefamily']) else '') + ' ' +
                (str(row['keywords']) if pd.notna(row['keywords']) else ''),
                axis=1)
            tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
            tfidf_matrix = tfidf.fit_transform(df_boardgames['complex'])
            similarity = cosine_similarity(tfidf_matrix)

            global recommendations
            recommendations = []

            global matching_games         

            matching_games = [game for game in matching_games if game < len(df_boardgames)]

            for game_index in matching_games:
                similar_games = list(enumerate(similarity[game_index]))
                similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
                similar_games = similar_games[1:21] 

                for sim_game in similar_games:
                    sim_game_index = sim_game[0]
                    recommendations.append((sim_game_index, sim_game[1]))

            recommendation_dict = {}
            for appid_index, similarity_score in recommendations:
                if appid_index in recommendation_dict:
                    recommendation_dict[appid_index] += similarity_score
                else:
                    recommendation_dict[appid_index] = similarity_score

            recommendations = sorted(recommendation_dict.items(), key=lambda x: x[1], reverse=True)

            recommendations = [rec for rec in recommendations if rec[0] not in matching_games]

            tuple_recommendations = recommendations
            recommendations = []


            #print("Recommended games: ")
            for i, (appid_index, similarity_score) in enumerate(tuple_recommendations):
                if i >= 20:
                    break
                appid = df_boardgames.iloc[appid_index]['id']
                game_name = df_boardgames.iloc[appid_index]['game']
                bayesian_rating = df_boardgames.iloc[appid_index]['bayesaverage']
                #print(f"{game_name} with a rating of {bayesian_rating} and a similarity score of {similarity_score}")

                recommendations.append(appid)

            cont.show_frame(parent, Boardgames_results)

        welcome_label = tk.Label(self, text="Choose Complexity", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=100)

        simple_button = tk.Button(self,width=10, text="Simple", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=simple)
        simple_button.pack(pady=50)

        def show_simple_info():
            info_window = tk.Toplevel(self)
            info_window.title("Simple Filtering Info")
            info_window.geometry("400x300")

            info_label = tk.Label(info_window, text="Characteristics of Simple Filtering:", font=("Arial", 15, "bold"))
            info_label.pack(pady=20)

            characteristics_label = tk.Label(info_window, text="Recommendations are done based on:\n"
                                                 "1. boardgamecategory\n"
                                                  "2. boardgamefamily\n",
                                             font=("Arial", 12))
            characteristics_label.pack(pady=10) 

            close_button = tk.Button(info_window, text="Close", font=("Arial", 12), command=info_window.destroy)
            close_button.pack(pady=20)

        info_button = tk.Button(self, width=5, text="?", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="red", highlightcolor="red", highlightthickness=2, command=show_simple_info)
        info_button.place(x=600, y=310)

        complex_button = tk.Button(self,width=10, text="Complex", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=complex)
        complex_button.pack()

        def show_complex_info():
            info_window = tk.Toplevel(self)
            info_window.title("Complex Filtering Info")
            info_window.geometry("400x300")

            info_label = tk.Label(info_window, text="Characteristics of Complex Filtering:", font=("Arial", 15, "bold"))
            info_label.pack(pady=20)

            characteristics_label = tk.Label(info_window, text="Recommendations are done based on:\n"
                                                 "1. boardgamecategory\n"
                                                    "2. boardgamemechanic\n"
                                                    "3. boardgamefamily\n"
                                                    "4. keywords\n",
                                             font=("Arial", 12))
            characteristics_label.pack(pady=10) 

            close_button = tk.Button(info_window, text="Close", font=("Arial", 12), command=info_window.destroy)
            close_button.pack(pady=20)

        info_button2 = tk.Button(self, width=5, text="?", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="red", highlightcolor="red", highlightthickness=2, command=show_complex_info)
        info_button2.place(x=600, y=425)

        if content_category_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based_category))
            back_button.pack(side="bottom")
        elif content_minage_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based_minage))
            back_button.pack(side="bottom")
        elif content_players_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based_players))
            back_button.pack(side="bottom")
        else:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_content_based))
            back_button.pack(side="bottom")


# search for boardgames
class Search_boardgames(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global top_rated_check
        top_rated_check = 0
        global mygames_check
        mygames_check = 0
        global search_check
        search_check = 1
        global content_check
        content_check = 0
        global collaborative_check
        content_check = 0
        global hybrid_check
        hybrid_check = 0

        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def search_games():
            global recommendations
            recommendations = []
            empty_search_check = 0
            min_max_error = 0

            name = self.name_entry.get()
            year = self.year_entry.get()
            maxtime = self.maxtime_entry.get()
            minplayers = self.minplayers_combobox.get()
            maxplayers = self.maxplayers_combobox.get()
            category = self.category_combobox.get()
            minage = self.minage_entry.get()

            if year != "" and year.isdigit() == False :
                messagebox.showerror("Error", "Year must be a number")
                empty_search_check = 1
                min_max_error = 1
                cont.show_frame(parent, Search_boardgames)
            if maxtime != "" and maxtime.isdigit() == False:
                messagebox.showerror("Error", "Playing time must be a number")
                empty_search_check = 1
                min_max_error = 1
                cont.show_frame(parent, Search_boardgames)
            if minage != "" and minage.isdigit() == False:
                messagebox.showerror("Error", "Minimum age must be a number")
                empty_search_check = 1
                min_max_error = 1
                cont.show_frame(parent, Search_boardgames)
            if minplayers != "" and minplayers.isdigit() == False:
                messagebox.showerror("Error", "Minimum players must be a number")
                empty_search_check = 1
                min_max_error = 1
                cont.show_frame(parent, Search_boardgames)
            if maxplayers != "" and maxplayers.isdigit() == False:
                messagebox.showerror("Error", "Maximum players must be a number")
                empty_search_check = 1
                min_max_error = 1
                cont.show_frame(parent, Search_boardgames)
            if minplayers != "" and maxplayers != "" and int(minplayers) > int(maxplayers):
                messagebox.showerror("Error", "Minimum players must be less than maximum players")
                empty_search_check = 1
                min_max_error = 1
                cont.show_frame(parent, Search_boardgames)

            if name == "" and year == "" and maxtime == "" and minplayers == "" and maxplayers == "" and category == "" and minage == "":
                messagebox.showerror("Error", "Please enter at least one search criteria")
                empty_search_check = 1
                cont.show_frame(parent, Search_boardgames)
            if empty_search_check == 0:
                for i in range(len(boardgames)):
                    if len(recommendations) == 20:
                        break
                    if name.lower() in boardgames.iloc[i]['game'].lower() or not name:
                        if year == "" or int(year) == boardgames.iloc[i]['yearpublished']:
                            if maxtime == "" or int(maxtime) >= boardgames.iloc[i]['playingtime']:
                                if minplayers == "" or int(minplayers) == boardgames.iloc[i]['minplayers']:
                                    if maxplayers == "" or int(maxplayers) == boardgames.iloc[i]['maxplayers']:
                                        if minage == "" or int(minage) <= boardgames.iloc[i]['minage']:
                                            if category in boardgames.iloc[i]['general_category'] or not category:
                                                recommendations.append(boardgames.iloc[i]['id'])


            if len(recommendations) == 0 and min_max_error == 0:
                messagebox.showerror("Error", "No games found")
                empty_search_check = 1
                cont.show_frame(parent, Search_boardgames)

            if empty_search_check == 0:
                cont.show_frame(parent, Boardgames_results)

        welcome_label = tk.Label(self, text="Search Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        self.name_entry = tk.Entry(self, font=("Arial", 15, "bold"), bg="black", fg="white", insertbackground="white")
        self.name_entry.place(x=400, y=200)
        self.update_idletasks()
        label_height = self.name_entry.winfo_reqheight()

        name_label = tk.Label(self, text="Name", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        name_label.place(x=200, y=200, height=label_height)

        year_published_label = tk.Label(self, text="Year Published", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        year_published_label.place(x=200, y=250, height=label_height)

        self.year_entry = tk.Entry(self, font=("Arial", 15, "bold"), bg="black", fg="white", insertbackground="white")
        self.year_entry.place(x=400, y=250)

        maxtime_label = tk.Label(self, text="Playing Time", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        maxtime_label.place(x=200, y=300, height=label_height)

        self.maxtime_entry = tk.Entry(self, font=("Arial", 15, "bold"), bg="black", fg="white", insertbackground="white")
        self.maxtime_entry.place(x=400, y=300)

        minplayers_label = tk.Label(self, text="Minimum Players", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        minplayers_label.place(x=200, y=350, height=label_height)

        self.minplayers_combobox = ttk.Combobox(self,width=18, values=["1","2","3","4","5","6","7","8","9","10"], font=("Arial", 15, "bold"))
        self.minplayers_combobox.place(x=400, y=350)

        maxplayers_label = tk.Label(self, text="Maximum Players", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        maxplayers_label.place(x=200, y=400, height=label_height)

        self.maxplayers_combobox = ttk.Combobox(self,width=18, values=["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"], font=("Arial", 15, "bold"))
        self.maxplayers_combobox.place(x=400, y=400)

        minage_label = tk.Label(self, text="Minimum Age", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        minage_label.place(x=200, y=450, height=label_height)

        self.minage_entry = tk.Entry(self, font=("Arial", 15, "bold"), bg="black", fg="white", insertbackground="white")
        self.minage_entry.place(x=400, y=450)
        
        category_label = tk.Label(self, text="Category", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        category_label.place(x=200, y=500, height=label_height)

        self.category_combobox = ttk.Combobox(self,width=18, values=['Fantasy/Mythology','Educational','Historical','Strategy/War','Social/Cultural','Mechanics','Other'], font=("Arial", 15, "bold"))
        self.category_combobox.place(x=400, y=500)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="red", highlightcolor="red", highlightthickness=2, command=search_games)
        search_button.place(x=440, y=550)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_boardgames))
        back_button.pack(side="bottom")


# boardgames collaborative filtering
class Boardgames_collaborative_filtering(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global collaborative_check
        collaborative_check = 1
        global content_check
        content_check = 0
        global hybrid_check
        hybrid_check = 0
        global search_check
        search_check = 0
        global mygames_check
        mygames_check = 0
        global top_rated_check
        top_rated_check = 0


        def knn_user_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 1
            global collaborative_knn_item_check
            collaborative_knn_item_check = 0
            global collaborative_svd_check
            collaborative_svd_check = 0

            df_sampled = boardgame_users.sample(n=8000, random_state=42)
            users_samp = df_sampled[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users_samp.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM boardgames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users_samp = pd.concat([users_samp, db_users_df], ignore_index=True)

            users_samp = users_samp[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users_samp['rating'].min(), users_samp['rating'].max()))
            data = Dataset.load_from_df(users_samp[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            sim_options = {
                'name': 'pearson',
                'user_based': True
            }

            model = KNNBaseline(k=100, sim_options=sim_options)
            model.fit(trainset)

            all_game_ids = users_samp['game_id'].unique()

            # anti-testset
            user_rated_game_ids = users_samp[users_samp['user_id'] == user_id]['game_id'].tolist()
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_20_predictions = get_top_n_for_user(predictions, n=20)

            global recommendations
            recommendations = []

            check = 0
            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_20_predictions:
                recommendations.append(prediction.iid)
                game_name = boardgames[boardgames['id'] == prediction.iid]['game'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1
            
            if check == len(top_20_predictions):
                cont.show_frame(parent, Boardgames_results)

        def knn_item_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 0
            global collaborative_knn_item_check
            collaborative_knn_item_check = 1
            global collaborative_svd_check
            collaborative_svd_check = 0

            users = boardgame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM boardgames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            sim_options = {
                'name': 'cosine',
                'user_based': False
            }

            model = KNNBaseline(k=10, sim_options=sim_options)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            # anti-testset
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_20_predictions = get_top_n_for_user(predictions, n=20)

            global recommendations
            recommendations = []

            check = 0
            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_20_predictions:
                recommendations.append(prediction.iid)
                game_name = boardgames[boardgames['id'] == prediction.iid]['game'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1
            
            if check == len(top_20_predictions):
                cont.show_frame(parent, Boardgames_results)

        def svd_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 0
            global collaborative_knn_item_check
            collaborative_knn_item_check = 0
            global collaborative_svd_check
            collaborative_svd_check = 1

            users = boardgame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM boardgames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()


            model = SVD(n_factors=10, n_epochs=20, lr_all=0.005, reg_all=0.2)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            # anti-testset
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_20_predictions = get_top_n_for_user(predictions, n=20)

            global recommendations
            recommendations = []

            check = 0
            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_20_predictions:
                recommendations.append(prediction.iid)
                game_name = boardgames[boardgames['id'] == prediction.iid]['game'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1
            
            if check == len(top_20_predictions):
                cont.show_frame(parent, Boardgames_results)
            
        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        content_label = tk.Label(self, text="Collaborative Filtering Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        content_label.pack(pady=50)

        choose_label  = tk.Label(self, text="Choose a Type", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=(10, 50))

        knn_user_button = tk.Button(self, text="KNN User Based",width = 15, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=knn_user_based)
        knn_user_button.pack(pady=20)

        knn_item_button = tk.Button(self, text="KNN Item Based",width=15, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=knn_item_based)
        knn_item_button.pack(pady=20)

        svd_button = tk.Button(self, text="SVD", width=15,font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=svd_based)
        svd_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_boardgames))
        back_button.pack(side="bottom")


# boardgames hybrid filtering
class Boardgames_hybrid_filtering(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global collaborative_check
        collaborative_check = 0
        global content_check
        content_check = 0
        global hybrid_check
        hybrid_check = 1
        global search_check
        search_check = 0
        global mygames_check
        mygames_check = 0
        global top_rated_check
        top_rated_check = 0

        global hybrid_category_check
        hybrid_category_check = 0
        global hybrid_players_check
        hybrid_players_check = 0
        global hybrid_minage_check
        hybrid_minage_check = 0

        def top_rated():
            global df_boardgames
            df_boardgames = boardgames.sort_values('bayesaverage', ascending=False)[:10000]
            df_boardgames = df_boardgames.reset_index(drop=True)

            global matching_games
            matching_games = []

            indices = pd.Series(df_boardgames.index, index=df_boardgames['id']).drop_duplicates()

            top_rated_users_games = [game for game in user_games if game[2] > 5]

            for i in range(len(df_boardgames)):
                if df_boardgames.iloc[i]['id'] in [game[1] for game in top_rated_users_games]:
                    idx = indices[df_boardgames.iloc[i]['id']]
                    matching_games.append(idx)

                
            if len(matching_games) == 0:
                messagebox.showerror("Error", "No games found with this category")
                cont.show_frame(parent, Boardgames_hybrid_filtering)
            else:
                cont.show_frame(parent, Hybrid_boardgames_choose_complexity)


        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        hybrid_label = tk.Label(self, text="Hybrid Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        hybrid_label.pack(pady=50)

        choose_label  = tk.Label(self, text="Choose a filtering", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=(10, 50))

        category_button = tk.Button(self, text="Category",width = 12, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_boardgames_category))
        category_button.pack(pady=20)

        minage_button = tk.Button(self, text="Minimum Age",width=12, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_boardgames_minage))
        minage_button.pack(pady=20)

        players_button = tk.Button(self, text="Players",width=12, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_boardgames_players))
        players_button.pack(pady=20)

        top_rated_button = tk.Button(self, text="Top Rated", width=12,font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=top_rated)
        top_rated_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Recommendations_boardgames))
        back_button.pack(side="bottom")


# hybrid filtering the content part based on category
class Hybrid_boardgames_category(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global hybrid_category_check
        hybrid_category_check = 1
        global hybrid_minage_check
        hybrid_minage_check = 0
        global hybrid_players_check
        hybrid_players_check = 0


        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def category_recommendations():
            category = category_combobox.get()
            if category == "":
                messagebox.showerror("Error", "Please choose a category")
            else:
                category_remove = []
                for i in range(len(boardgames)):
                    if boardgames.iloc[i]['general_category'] != category:
                        category_remove.append(boardgames.iloc[i]['id'])

                global df_boardgames
                df_boardgames = boardgames[~boardgames['id'].isin(category_remove)].reset_index(drop=True)
                df_boardgames = df_boardgames.sort_values('bayesaverage', ascending=False)[:13000]
                df_boardgames = df_boardgames.reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_boardgames.index, index=df_boardgames['id']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_boardgames)):
                    if df_boardgames.iloc[i]['id'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_boardgames.iloc[i]['id']]
                        matching_games.append(idx)

                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this category")
                    cont.show_frame(parent, Hybrid_boardgames_category)
                else:
                    cont.show_frame(parent, Hybrid_boardgames_choose_complexity)

        welcome_label = tk.Label(self, text="Category Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Choose a category", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        category_combobox = ttk.Combobox(self,width=18, values=['Fantasy/Mythology','Educational','Historical','Strategy/War','Social/Cultural','Mechanics','Other'], font=("Arial", 15, "bold"))
        category_combobox.place(x=400, y=350)
        self.update_idletasks()
        label_height = category_combobox.winfo_reqheight()

        category_label = tk.Label(self, text="Category", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=10)
        category_label.place(x=200, y=350, height=label_height)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=category_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_hybrid_filtering))
        back_button.pack(side="bottom")


# hybrid filtering the content part based on number of players
class Hybrid_boardgames_players(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global hybrid_category_check
        hybrid_category_check = 0
        global hybrid_minage_check
        hybrid_minage_check = 0
        global hybrid_players_check
        hybrid_players_check = 1

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def players_recommendations():
            min_players = minplayers_combobox.get()
            max_players = maxplayers_combobox.get()

            if min_players == "" and max_players == "":
                messagebox.showerror("Error", "Please enter a number")
            elif min_players != "" and min_players.isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            elif max_players != "" and max_players.isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            elif (min_players != "" and max_players != "") and int(min_players) > int(max_players):
                messagebox.showerror("Error", "Minimum players must be less than maximum players")
            else:
                players_remove = []
                for i in range(len(boardgames)):
                    if min_players != "" and max_players != "":
                        if boardgames.iloc[i]['minplayers'] != int(min_players) or boardgames.iloc[i]['maxplayers'] != int(max_players):
                            players_remove.append(boardgames.iloc[i]['id'])
                    elif min_players != "" and max_players == "":
                        if boardgames.iloc[i]['minplayers'] != int(min_players):
                            players_remove.append(boardgames.iloc[i]['id'])
                    elif min_players == "" and max_players != "":
                        if boardgames.iloc[i]['maxplayers'] != int(max_players):
                            players_remove.append(boardgames.iloc[i]['id'])

                global df_boardgames
                df_boardgames = boardgames[~boardgames['id'].isin(players_remove)].reset_index(drop=True)
                df_boardgames = df_boardgames.sort_values('bayesaverage', ascending=False)[:13000]
                df_boardgames = df_boardgames.reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_boardgames.index, index=df_boardgames['id']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_boardgames)):
                    if df_boardgames.iloc[i]['id'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_boardgames.iloc[i]['id']]
                        matching_games.append(idx)
  
                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this players number")
                    cont.show_frame(parent, Hybrid_boardgames_players)
                else:
                    cont.show_frame(parent, Hybrid_boardgames_choose_complexity)

        welcome_label = tk.Label(self, text="Minimum Age Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Choose number of players", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        minplayers_combobox = ttk.Combobox(self,width=18, values=["1","2","3","4","5","6","7","8","9","10"], font=("Arial", 15, "bold"))
        minplayers_combobox.place(x=400, y=350)
        self.update_idletasks()
        label_height = minplayers_combobox.winfo_reqheight()

        minplayers_label = tk.Label(self, text="Minimum Players", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        minplayers_label.place(x=200, y=350, height=label_height)

        maxplayers_label = tk.Label(self, text="Maximum Players", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=15)
        maxplayers_label.place(x=200, y=400, height=label_height)

        maxplayers_combobox = ttk.Combobox(self,width=18, values=["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"], font=("Arial", 15, "bold"))
        maxplayers_combobox.place(x=400, y=400)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=players_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_hybrid_filtering))
        back_button.pack(side="bottom")


# hybrid filtering the content part based on minimum age
class Hybrid_boardgames_minage(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        global hybrid_category_check
        hybrid_category_check = 0
        global hybrid_minage_check
        hybrid_minage_check = 1
        global hybrid_players_check
        hybrid_players_check = 0

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def min_age_recommendations():
            min_age = min_age_entry.get()
            if min_age == "":
                messagebox.showerror("Error", "Please enter a minimum age")
            elif min_age.isdigit() == False:
                messagebox.showerror("Error", "Please enter a number")
            else:
                min_age_remove = []
                for i in range(len(boardgames)):
                    if boardgames.iloc[i]['minage'] < int(min_age):
                        min_age_remove.append(boardgames.iloc[i]['id'])

                global df_boardgames
                df_boardgames = boardgames[~boardgames['id'].isin(min_age_remove)].reset_index(drop=True)
                df_boardgames = df_boardgames.sort_values('bayesaverage', ascending=False)[:13000]
                df_boardgames = df_boardgames.reset_index(drop=True)

                global matching_games
                matching_games = []

                indices = pd.Series(df_boardgames.index, index=df_boardgames['id']).drop_duplicates()

                top_rated_users_games = [game for game in user_games if game[2] > 5]

                for i in range(len(df_boardgames)):
                    if df_boardgames.iloc[i]['id'] in [game[1] for game in top_rated_users_games]:
                        idx = indices[df_boardgames.iloc[i]['id']]
                        matching_games.append(idx)

                if len(matching_games) == 0:
                    messagebox.showerror("Error", "No games found with this minimum age")
                    cont.show_frame(parent, Hybrid_boardgames_minage)
                else:
                    cont.show_frame(parent, Hybrid_boardgames_choose_complexity)

        welcome_label = tk.Label(self, text="Minimum Age Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=50)

        choose_label = tk.Label(self, text="Choose a Minimum Age", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=10)

        min_age_entry = tk.Entry(self, font=("Arial", 15, "bold"), bg="black", fg="white", insertbackground="white")
        min_age_entry.place(x=400, y=350)
        self.update_idletasks()
        label_height = min_age_entry.winfo_reqheight()

        min_age_label = tk.Label(self, text="Minimum Age", font=("Arial", 15, "bold"), bg="black", fg="white", bd=5,
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2,width=12)
        min_age_label.place(x=200, y=350, height=label_height)

        search_button = tk.Button(self, text="Search", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=min_age_recommendations)
        search_button.place(x=440, y=450)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_hybrid_filtering))
        back_button.pack(side="bottom")


# hybrid filtering the content part based on the characteristics
class Hybrid_boardgames_choose_complexity(tk.Frame):   
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        def simple():
            if 'simple' not in df_boardgames.columns:
                df_boardgames['simple'] = ''
            df_boardgames['simple'] = df_boardgames.apply(
    lambda row: (str(row['boardgamecategory']) if pd.notna(row['boardgamecategory']) else '') + ' ' +
                (str(row['boardgamefamily']) if pd.notna(row['boardgamefamily']) else ''),axis=1)
            tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
            tfidf_matrix = tfidf.fit_transform(df_boardgames['simple'])
            similarity = cosine_similarity(tfidf_matrix)

            global content
            content = []

            global matching_games         

            matching_games = [game for game in matching_games if game < len(df_boardgames)]

            for game_index in matching_games:
                similar_games = list(enumerate(similarity[game_index]))
                similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
                similar_games = similar_games[1:11]  

                for sim_game in similar_games:
                    sim_game_index = sim_game[0]
                    content.append((sim_game_index, sim_game[1]))

            content_dict = {}
            for appid_index, similarity_score in content:
                if appid_index in content_dict:
                    content_dict[appid_index] += similarity_score
                else:
                    content_dict[appid_index] = similarity_score

            content = sorted(content_dict.items(), key=lambda x: x[1], reverse=True)
            content = [rec for rec in content if rec[0] not in matching_games]

            tuple_content = content
            content = []

            #print("Recommended games: ")
            for i, (appid_index, similarity_score) in enumerate(tuple_content):
                if i >= 10:
                    break
                appid = df_boardgames.iloc[appid_index]['id']
                game_name = df_boardgames.iloc[appid_index]['game']
                bayesian_rating = df_boardgames.iloc[appid_index]['bayesaverage']
                #print(f"{game_name} with a rating of {bayesian_rating} and a similarity score of {similarity_score}")
                content.append(appid)

            cont.show_frame(parent, Hybrid_collaborative_method_boardgames)

        def complex():
            if 'complex' not in df_boardgames.columns:
                df_boardgames['complex'] = ''
            df_boardgames['keywords'] = df_boardgames['keywords'].apply(lambda x: ' '.join(map(str, x)))
            df_boardgames['complex'] = df_boardgames.apply(lambda row: 
                (str(row['boardgamecategory']) if pd.notna(row['boardgamecategory']) else '') + ' ' +
                (str(row['boardgamemechanic']) if pd.notna(row['boardgamemechanic']) else '') + ' ' +
                (str(row['boardgamefamily']) if pd.notna(row['boardgamefamily']) else '') + ' ' +
                (str(row['keywords']) if pd.notna(row['keywords']) else ''),
                axis=1)
            tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
            tfidf_matrix = tfidf.fit_transform(df_boardgames['complex'])
            similarity = cosine_similarity(tfidf_matrix)

            global content
            content = []

            global matching_games         

            matching_games = [game for game in matching_games if game < len(df_boardgames)]

            for game_index in matching_games:
                similar_games = list(enumerate(similarity[game_index]))
                similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)
                similar_games = similar_games[1:11] 
                print(similar_games)

                for sim_game in similar_games:
                    sim_game_index = sim_game[0]
                    content.append((sim_game_index, sim_game[1]))

            content_dict = {}
            for appid_index, similarity_score in content:
                if appid_index in content_dict:
                    content_dict[appid_index] += similarity_score
                else:
                    content_dict[appid_index] = similarity_score

            content = sorted(content_dict.items(), key=lambda x: x[1], reverse=True)
            content = [rec for rec in content if rec[0] not in matching_games]

            tuple_content = content
            content = []

            #print("Recommended games: ")
            for i, (appid_index, similarity_score) in enumerate(tuple_content):
                if i >= 10:
                    break
                appid = df_boardgames.iloc[appid_index]['id']
                game_name = df_boardgames.iloc[appid_index]['game']
                bayesian_rating = df_boardgames.iloc[appid_index]['bayesaverage']
                #print(f"{game_name} with a rating of {bayesian_rating} and a similarity score of {similarity_score}")
                content.append(appid)

            cont.show_frame(parent, Hybrid_collaborative_method_boardgames)    

        welcome_label = tk.Label(self, text="Choose Complexity", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        welcome_label.pack(pady=100)

        simple_button = tk.Button(self,width=10, text="Simple", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=simple)
        simple_button.pack(pady=50)

        complex_button = tk.Button(self,width=10, text="Complex", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5,
                                        highlightbackground="red", highlightcolor="red", highlightthickness=2, command=complex)
        complex_button.pack()

        if hybrid_category_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_boardgames_category))
            back_button.pack(side="bottom")
        elif hybrid_players_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_boardgames_players))
            back_button.pack(side="bottom")
        elif hybrid_minage_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_boardgames_minage))
            back_button.pack(side="bottom")
        else:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_hybrid_filtering))
            back_button.pack(side="bottom") 


# hybrid filtering the collaborative part
class Hybrid_collaborative_method_boardgames(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        def knn_user_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 0
            global collaborative_knn_item_check
            collaborative_knn_item_check = 1
            global collaborative_svd_check
            collaborative_svd_check = 0


            df_sampled = boardgame_users.sample(n=8000, random_state=42)
            users_samp = df_sampled[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users_samp.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM boardgames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users_samp = pd.concat([users_samp, db_users_df], ignore_index=True)

            users_samp = users_samp[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users_samp['rating'].min(), users_samp['rating'].max()))
            data = Dataset.load_from_df(users_samp[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            sim_options = {
                'name': 'msd',
                'user_based': True
            }

            model = KNNBaseline(k=90, sim_options=sim_options)
            model.fit(trainset)

            all_game_ids = users_samp['game_id'].unique()

            # anti-testset
            user_rated_game_ids = users_samp[users_samp['user_id'] == user_id]['game_id'].tolist()
            user_rated_game_ids = user_rated_game_ids + content    
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_10_predictions = get_top_n_for_user(predictions, n=10)

            collaborative = []

            check = 0
           # print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_10_predictions:
                collaborative.append(prediction.iid)
                game_name = boardgames[boardgames['id'] == prediction.iid]['game'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1
            
            for game in content:
                if game in collaborative:
                    content.remove(game)

            global recommendations
            recommendations = collaborative + content

            if check == len(top_10_predictions):
                cont.show_frame(parent, Boardgames_results)

        def knn_item_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 0
            global collaborative_knn_item_check
            collaborative_knn_item_check = 1
            global collaborative_svd_check
            collaborative_svd_check = 0

            users = boardgame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM boardgames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()

            sim_options = {
                'name': 'msd',
                'user_based': False
            }

            model = KNNBaseline(k=10, sim_options=sim_options)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            # anti-testset 
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_rated_game_ids = user_rated_game_ids + content
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions 
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_10_predictions = get_top_n_for_user(predictions, n=10)
            collaborative = []

            check = 0
            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_10_predictions:
                collaborative.append(prediction.iid)
                game_name = boardgames[boardgames['id'] == prediction.iid]['game'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1

            for game in content:
                if game in collaborative:
                    content.remove(game)

            global recommendations
            recommendations = collaborative + content
            
            if check == len(top_10_predictions):
                cont.show_frame(parent, Boardgames_results)

        def svd_based():
            global collaborative_knn_user_check
            collaborative_knn_user_check = 0
            global collaborative_knn_item_check
            collaborative_knn_item_check = 0
            global collaborative_svd_check
            collaborative_svd_check = 1

            users = boardgame_users[['user_id', 'bayesian_rating', 'appid']].drop_duplicates()
            users.rename(columns={'appid': 'game_id', 'bayesian_rating': 'rating'}, inplace=True)

            # Collect all users from the database
            mycursor = mydb.cursor()
            mycursor.execute("SELECT user_id, game_id, rating FROM boardgames_user")
            myresult = mycursor.fetchall()
            mycursor.close()

            db_users = []
            for game in myresult:
                userid = game[0]
                game_id = game[1]
                rating = game[2]
                db_users.append({'user_id': userid, 'game_id': game_id, 'bayesian_rating': rating})

            db_users_df = pd.DataFrame(db_users)
            db_users_df.rename(columns={'bayesian_rating': 'rating'}, inplace=True)

            users = pd.concat([users, db_users_df], ignore_index=True)

            users = users[['user_id', 'game_id', 'rating']]

            reader = Reader(rating_scale=(users['rating'].min(), users['rating'].max()))
            data = Dataset.load_from_df(users[['user_id', 'game_id', 'rating']], reader)

            trainset = data.build_full_trainset()


            model = SVD(n_factors=10, n_epochs=20, lr_all=0.005, reg_all=0.2)
            model.fit(trainset)

            all_game_ids = users['game_id'].unique()

            # anti-testset
            user_rated_game_ids = users[users['user_id'] == user_id]['game_id'].tolist()
            user_rated_game_ids = user_rated_game_ids + content
            user_anti_testset = [(user_id, game_id, 0) for game_id in all_game_ids if game_id not in user_rated_game_ids]
            predictions = model.test(user_anti_testset)

            # Get top N predictions
            def get_top_n_for_user(predictions, n=20):
                predictions.sort(key=lambda x: x.est, reverse=True)
                top_n = predictions[:n]
                return top_n

            top_10_predictions = get_top_n_for_user(predictions, n=10)

            collaborative = []

            check = 0
            #print(f"Top 20 predictions for user_id {user_id}:")
            for prediction in top_10_predictions:
                collaborative.append(prediction.iid)
                game_name = boardgames[boardgames['id'] == prediction.iid]['game'].values[0]
                #print(f"Game ID: {prediction.iid}, Game Name: {game_name}, Estimated Rating: {prediction.est}")
                check += 1

            for game in content:
                if game in collaborative:
                    content.remove(game)

            global recommendations
            recommendations = collaborative + content

            if check == len(top_10_predictions):
                print("mphka")
                cont.show_frame(parent, Boardgames_results)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        content_label = tk.Label(self, text="Hybrid Filtering Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        content_label.pack(pady=50)

        choose_label  = tk.Label(self, text="Choose a Type", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        choose_label.pack(pady=(10, 50))

        knn_user_button = tk.Button(self, text="KNN User Based",width = 15, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=knn_user_based)
        knn_user_button.pack(pady=20)

        knn_item_button = tk.Button(self, text="KNN Item Based",width=15, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=knn_item_based)
        knn_item_button.pack(pady=20)

        svd_button = tk.Button(self, text="SVD", width=15,font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=svd_based)
        svd_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_boardgames_choose_complexity))
        back_button.pack(side="bottom")


# display the results of the recommendations
class Boardgames_results(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        def show_more_info(appid):
            global boardgame_appid
            boardgame_appid = 0
            boardgame_appid = appid
            print(boardgame_appid)
            cont.show_frame(parent, Boardgame_info)

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        global recommendations

        if mygames_check == 1:
            welcome_label = tk.Label(self, text="My Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif search_check == 1:
            welcome_label = tk.Label(self, text="Search Results", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif top_rated_check == 1:
            welcome_label = tk.Label(self, text="Top Rated Games", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif content_check == 1:
            welcome_label = tk.Label(self, text="Content Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif collaborative_check == 1 and collaborative_knn_user_check == 1:
            welcome_label = tk.Label(self, text="Collaborative KNN User-Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif collaborative_check == 1 and collaborative_knn_item_check == 1:
            welcome_label = tk.Label(self, text="Collaborative KNN Item-Based Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif collaborative_check == 1 and collaborative_svd_check == 1:
            welcome_label = tk.Label(self, text="Collaborative SVD Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)
        elif hybrid_check == 1:
            welcome_label = tk.Label(self, text="Hybrid Recommendations", font=("Arial", 25, "bold"), bg="black", fg="white", bd=5, 
                                    highlightbackground="grey", highlightcolor="red", highlightthickness=2)
            welcome_label.pack(pady=50)

        frame = Frame(self)
        frame.pack(side=LEFT, fill=BOTH, expand=True, padx=300, pady=(10, 100))

        self.canvas = Canvas(frame, bg='black')
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.mailbox_frame = Frame(self.canvas, bg='purple')
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.mailbox_frame, anchor=NW)

        mail_scroll = Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        mail_scroll.pack(side=RIGHT, fill=Y)

        self.canvas.config(yscrollcommand=mail_scroll.set)

        self.mailbox_frame.bind("<Configure>", self.OnFrameConfigure)
        #self.canvas.bind('<Configure>', self.OnFrameConfigure)
        self.canvas.bind('<Configure>', self.FrameWidth)

        for game_appid in recommendations:
            each_game_frame = tk.Frame(self.mailbox_frame, bg="black", bd=5, highlightbackground="blue", highlightcolor="red", highlightthickness=2)
            each_game_frame.pack(fill="both", expand="yes", side="top", padx=10, pady=10)

            game_image_url = boardgames[boardgames['id'] == game_appid]['image'].values[0]
            game_image = Image.open(requests.get(game_image_url, stream=True).raw)
            game_image = game_image.resize((320, 200), Image.LANCZOS)
            game_photo = ImageTk.PhotoImage(game_image)
            game_image_label = tk.Label(each_game_frame, image=game_photo)
            game_image_label.image = game_photo
            game_image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

            hidden_button = tk.Button(each_game_frame, image=game_photo, command=lambda appid=game_appid: show_more_info(appid), bd=0, highlightthickness=0)
            hidden_button.grid(row=0, column=0, padx=10, pady=10)

        if search_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Search_boardgames))
            back_button.place(x=450,y=736)
        elif top_rated_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_top_rated))
            back_button.place(x=450,y=736)
        elif content_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_choose_complexity))
            back_button.place(x=450,y=736)
        elif collaborative_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_collaborative_filtering))
            back_button.place(x=450,y=736)
        elif hybrid_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Hybrid_collaborative_method_boardgames))
            back_button.place(x=450,y=736)

    def FrameWidth(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        # Debugging output to track canvas width updates
        print(f"Canvas width set to: {canvas_width}")

    def OnFrameConfigure(self, event):
        # Update the scroll region to encompass the entire canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Debugging output to track scroll region updates
        print(f"Scroll region updated to: {self.canvas.bbox('all')}")


# display the information of the selected boardgame
class Boardgame_info(tk.Frame):
    def __init__(self, parent, cont):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        global boardgame_appid

        # Load and display the logo
        self.logo_image = Image.open("logo.jpg")
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = tk.Label(self, image=self.logo_photo)
        self.logo_label.place(x=0, y=0)

        game_name = boardgames[boardgames['id'] == boardgame_appid]['game'].values[0]
        game_rating = boardgames[boardgames['id'] == boardgame_appid]['bayesaverage'].values[0]
        game_rating = str(game_rating)[:4]

        name_label = tk.Label(self, text=game_name, font=("Arial", 25, "bold"),wraplength=750, bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        name_label.pack(pady=10)

        game_image_url = boardgames[boardgames['id'] == boardgame_appid]['image'].values[0]
        game_image = Image.open(requests.get(game_image_url, stream=True).raw)
        game_image = game_image.resize((400, 250), Image.LANCZOS)
        game_photo = ImageTk.PhotoImage(game_image)
        game_image_label = tk.Label(self, image=game_photo)
        game_image_label.image = game_photo
        game_image_label.pack(pady=5)

        rating_label = tk.Label(self, text="Community Rating: " + str(game_rating), font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        rating_label.place(x=150, y=380)

        release_date = boardgames[boardgames['id'] == boardgame_appid]['yearpublished'].values[0]
        release_date_label = tk.Label(self, text="Year Published: " + str(release_date), font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        release_date_label.place(x=500, y=380)

        playingtime = boardgames[boardgames['id'] == boardgame_appid]['playingtime'].values[0]
        playingtime_label = tk.Label(self, text="Playing Time: " + str(playingtime), font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        playingtime_label.place(x=235, y=450)

        minage = boardgames[boardgames['id'] == boardgame_appid]['minage'].values[0]
        minage_label = tk.Label(self, text="Minimum Age: " + str(minage), font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        minage_label.place(x=500, y=450)

        category = boardgames[boardgames['id'] == boardgame_appid]['general_category'].values[0]
        category_label = tk.Label(self, text="Category: " + category, font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        category_label.place(x=500, y=520)

        minplayers = boardgames[boardgames['id'] == boardgame_appid]['minplayers'].values[0]
        maxplayers = boardgames[boardgames['id'] == boardgame_appid]['maxplayers'].values[0]
        players_label = tk.Label(self, text="Number of Players: " + str(minplayers) + " - " + str(maxplayers), font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
        players_label.place(x=155, y=520)

        def open_description():
            description_toplevel = tk.Toplevel(self)
            description_toplevel.title("Description")
            description_toplevel.geometry("600x400")
            description_label = tk.Label(description_toplevel,wraplength=500, text=description)
            description_label.pack(pady=10)

        description = boardgames[boardgames['id'] == boardgame_appid]['description'].values[0]
        description_button = tk.Button(self, text="Description", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2, command=open_description)
        description_button.place(x=305, y=580)

        game_site = boardgames[boardgames['id'] == boardgame_appid]['URL'].values[0]
        website_button = tk.Button(self, text="Website", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2, command=lambda: webbrowser.open(game_site))
        website_button.place(x=500, y=580)

        user_games_ids = [game[1] for game in user_games]

        if boardgame_appid in user_games_ids:
            for game in user_games:
                if game[1] == boardgame_appid:
                    rating_label = tk.Label(self, text="Your Rating: " + str(game[2]), font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="grey", highlightcolor="red", highlightthickness=2)
                    rating_label.place(x=110,y=655)
                    rating_combobox = ttk.Combobox(self, values=list(range(1, 11)))
                    rating_combobox.place(x=340, y=655)

                    old_rating = game[2]

                    change_rating_button = tk.Button(self, text="Change Rating", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: change_rating(rating_combobox.get(), boardgame_appid,old_rating))
                    change_rating_button.place(x=490, y=655)   

                    def delete_rating_confirmation():
                        result = messagebox.askyesno("Confirmation", "Are you sure you want to delete the rating?")
                        if result == True:
                            delete_rating(boardgame_appid)

                    delete_rating_button = tk.Button(self, text="Delete Rating", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=delete_rating_confirmation)
                    delete_rating_button.place(x=730, y=655)

        else:
            rating_combobox = ttk.Combobox(self, values=list(range(1, 11)))
            rating_combobox.place(x=350, y=655)

            rate_button = tk.Button(self, text="Rate", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: rate_game(rating_combobox.get(), boardgame_appid))
            rate_button.place(x=500, y=655)

        if mygames_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, My_boardgames))
            back_button.place(x=450,y=736)
        elif search_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_results ))
            back_button.place(x=450,y=736)
        elif top_rated_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_results))
            back_button.place(x=450,y=736)
        elif content_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_results))
            back_button.place(x=450,y=736)
        elif collaborative_check == 1:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_results))
            back_button.place(x=450,y=736)
        else:
            back_button = tk.Button(self, text="Back", font=("Arial", 20, "bold"), bg="black", fg="white", bd=5, 
                                       highlightbackground="red", highlightcolor="red", highlightthickness=2, command=lambda: cont.show_frame(parent, Boardgames_results))
            back_button.place(x=450,y=736) 

        def rate_game(rating, appid):
            if rating == "":
                messagebox.showerror("Error", "Please enter a rating")
            elif rating.isdigit() == False:
                messagebox.showerror("Error", "Please enter a valid rating")
            elif int(rating) < 1 or int(rating) > 10:
                messagebox.showerror("Error", "Please enter a rating between 1 and 10")
            else:
                rating = int(rating)
                appid = int(appid)
                mycursor = mydb.cursor()
                sqlquery = "insert into boardgames_user (user_id, game_id, rating) values (%s, %s, %s)"
                val = (user_id, appid, rating)
                mycursor.execute(sqlquery, val)
                mydb.commit()
                mycursor.close()
                messagebox.showinfo("Success", "Game rated successfully")

                user_games.append([user_id, appid, rating])
                cont.show_frame(parent, Boardgame_info) 


        def change_rating(rating, appid, old_rating):
            if rating == "":
                messagebox.showerror("Error", "Please enter a rating")
            elif rating.isdigit() == False:
                messagebox.showerror("Error", "Please enter a valid rating")
            elif int(rating) < 1 or int(rating) > 10:
                messagebox.showerror("Error", "Please enter a rating between 1 and 10")
            elif int(rating) == int(old_rating):
                messagebox.showerror("Error", "Please enter a different rating")
            else:
                rating = int(rating)
                appid = int(appid)
                mycursor = mydb.cursor()
                sqlquery = "update boardgames_user set rating = %s where user_id = %s and game_id = %s"
                val = (rating, user_id, appid)
                mycursor.execute(sqlquery, val)
                mydb.commit()
                mycursor.close()
                messagebox.showinfo("Success", "Rating changed successfully")

                for game in user_games:
                    if game[1] == appid:
                        game[2] = rating
                cont.show_frame(parent, Boardgame_info)

        def delete_rating(appid):
            appid = int(appid)
            mycursor = mydb.cursor()
            sqlquery = "delete from boardgames_user where user_id = %s and game_id = %s"
            val = (user_id, appid)
            mycursor.execute(sqlquery, val)
            mydb.commit()
            mycursor.close()
            messagebox.showinfo("Success", "Rating deleted successfully")

            for game in user_games:
                if game[1] == appid:
                    user_games.remove(game)
            if mygames_check == 1:
                cont.show_frame(parent, My_boardgames)
            else:
                cont.show_frame(parent, Boardgame_info)


# The main class that will be used to run the application
class Start(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs) 
        
        self.title("Video/Board Games")
        # Set the window size
        self.geometry("1000x800")
        #self.minsize(600, 650)
        self.resizable(False, False)

        # Set the window title
        window = tk.Frame(self)
        window.pack(side="top", fill="both", expand=True)
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        self.frames = {}

        frame = User_type(window, self)
        self.frames[User_type] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(window, User_type)

    def show_frame(self, container, cont):
        if cont not in self.frames:
            frame = cont(container, self)
            self.frames[cont] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        frame = self.frames[cont]
        frame.tkraise()

        if cont in self.frames:
            for child in self.frames[cont].winfo_children():
                child.destroy()
        frame = cont(container, self)
        self.frames[cont] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()


if __name__ == "__main__":
    app = Start()
    app.mainloop()
    mydb.close() # Close the database connection
    

