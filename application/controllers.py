from jinja2 import Template
from flask import Flask,render_template,request,redirect,url_for, Flask, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError 
from flask import current_app as app
from application.models import *
from sqlalchemy import text
import os

UserStatusList = {}
AdminStatusList = {}
curr_user =0
curr_cr=0
recent_plays={}

@app.route("/", methods=["GET", "POST"])
def mainpage():
    try:
        msg = request.args.get('session')
        if msg=="logout":
            flash("Successfully Logged Out!!!")
    except:
        pass
    return render_template("index.html")

# ------------------------ ADMIN ------------------------------------------------------
@app.route("/AdminLogin/", methods=["GET", "POST"])
def adminlogin():
    try:
        err = request.args.get('login')
        if err:
            flash(err)
    except:
        pass
    if request.method=="GET":
        return render_template("AdminLogin.html")
    if request.method=="POST":
        u=request.form['uname']
        p=request.form['passs']
        if not u or not p:
            flash("Provide Some input!!")
            return redirect("/AdminLogin/")
        try:
            admin= Admin.query.filter(Admin.name==u).first()
        except:
            flash("Not Processing")
            return redirect("/AdminLogin/")
        if not admin:
            flash("Invalid Admin!!")
            return redirect("/AdminLogin/")
        x={u: admin.admin_pwd, 'username': admin.admin_id}
        if (x[u]!=p):
            flash("Invalid Password")
            return redirect("/AdminLogin/")
        AdminStatusList[x['username']] = 1
        return redirect(f"/AdminHome/{x['username']}/{u}/home")

@app.route("/AdminHome/<int:adminid>/<string:aname>/<string:view>")
def adminhome(adminid, aname, view):
    try:
        if (AdminStatusList[adminid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        usercount, creatorcount, songcount, albumcount=0,0,0,0
        qy1 = User.query.all()
        qy2 = Creator.query.all()
        qy3 = Song.query.all()
        qy4 = Album.query.all()
        songratinglist=[]
        datalist=[]
        for i in qy1:
            usercount+=1
            if view=="User":
                datalist.append([i.name, i.status, i.user_id])
        for i in qy2:
            creatorcount+=1
            if view=="Creator":
                datalist.append([i.name, i.status, i.cr_id])
        for i in qy3:
            songcount+=1
            songratinglist.append(i.Rating)
            if view=="Song":
                datalist.append([i.name, i.status, i.song_id])
        for i in qy4:
            albumcount+=1
            if view=="Album":
                datalist.append([i.name, i.status, i.album_id])
        songrating= sum(songratinglist)/len(songratinglist)
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            os.system('cmd /c "python -m pip install matplotlib.pyplot"')
        sql = text("select login_date from User")
        userqy = db.session.execute(sql)
        datadic={}
        for user in userqy:
            date= user[0][0:10]
            if date in datadic.keys():
                datadic[date]=datadic[date]+1
            else:
                datadic[date]=1
        xlist=[]
        ylist=[]
        for i in datadic:
            xlist.append(i)
            ylist.append(datadic[i])
        plt.switch_backend('agg')
        plt.style.use("ggplot")
        fig, ax = plt.subplots()
        ax.plot( xlist  ,  ylist, linestyle='--', marker='.' )
        fig.suptitle('User Registeration Analysis')
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        fig.savefig('static\my_plot.png')
        # graph for genres analysis
        sql = text("select genre, play_time from Song")
        Songqy = db.session.execute(sql)
        datadic={}
        for song in Songqy:
            genre= song[0][0:10].upper()
            if genre in datadic.keys():
                datadic[genre]=datadic[genre]+song[1]
            else:
                datadic[genre]=song[1]
        xlist=[]
        ylist=[]
        for i in datadic:
            xlist.append(i)
            ylist.append(datadic[i])
        plt.switch_backend('agg')
        plt.style.use("ggplot")
        fig, ax = plt.subplots()
        ax.plot( xlist  ,  ylist, linestyle='--', marker='.' )
        fig.suptitle('Song Genre Analysis')
        ax.set_xlabel('Genre')
        ax.set_ylabel('Playtime')
        fig.savefig('static\my_plot_genre.png')
        # graph for creator analysis
        sql = text("select cr_id, play_time from Song")
        Creatorqy = db.session.execute(sql)
        datadic={}
        for cr in Creatorqy:
            creator= Creator.query.filter(Creator.cr_id==cr[0]).first().name
            if creator in datadic.keys():
                datadic[creator]=datadic[creator]+cr[1]
            else:
                datadic[creator]=cr[1]
        xlist=[]
        ylist=[]
        for i in datadic:
            xlist.append(i)
            ylist.append(datadic[i])
        plt.switch_backend('agg')
        plt.style.use("ggplot")
        fig, ax = plt.subplots()
        ax.plot( xlist  ,  ylist, linestyle='--', marker='.' )
        fig.suptitle('Creator Analysis')
        ax.set_xlabel('creator')
        ax.set_ylabel('Playtime')
        fig.savefig('static\my_plot_creator.png')

        return render_template("AdminDash.html",file='my_plot.png', crfile='my_plot_creator.png' , genrefile='my_plot_genre.png', uc=usercount, cc=creatorcount, sc=songcount,ac=albumcount, songrating=songrating, view=view, adminid=adminid, adminname=aname, datalist=datalist)
    else:
        return redirect('/AdminLogin/?login=No Session Found')

@app.route("/Lock/<int:adminid>/<string:adminname>/<string:view>/<int:id>")
def lock(adminid, adminname,view,id):
    try:
        if (AdminStatusList[adminid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        if view== "Song":
            qy = Song.query.filter(Song.song_id == id).first()
            if qy.status==1:
                qy.status=0
            else:
                qy.status=1
        elif view== "Album":
            qy = Album.query.filter(Album.album_id == id).first()
            if qy.status==1:
                qy.status=0
            else:
                qy.status=1
        elif view== "Creator":
            qy = Creator.query.filter(Creator.cr_id == id).first()
            if qy.status==1:
                qy.status=0
            else:
                qy.status=1
        elif view== "User":
            qy = User.query.filter(User.user_id == id).first()
            if qy.status==1:
                qy.status=0
            else:
                qy.status=1
        db.session.commit()
        return redirect(f"/AdminHome/{adminid}/{adminname}/{view}")
    else:
        return redirect('/AdminLogin/?login=No Session Found')

@app.route("/adminLogout/<int:adminid>")
def adminlogout(adminid):
    try:
        AdminStatusList[adminid] = 0
    except KeyError:
        pass
    return redirect("/")

# ------------------- USER --------------------------------------------------------------
@app.route("/RegisterUser/", methods=["GET", "POST"])
def registeruser():
    if request.method == "GET":
        return render_template("RegisterUser.html")
    if request.method == "POST":
        name = request.form['uname']
        password= request.form['passs']
        if not name or not password:
            flash("Provide Some Input!!!")
            return redirect("/RegisterUser/")
        try:
            user_to_reg = User(name=name, pwd= password)
            db.session.add(user_to_reg)
            db.session.commit()
        except:
            flash("Not Processing!!!")
            return redirect("/RegisterUser/")
        return redirect('/')

@app.route("/UserLogin/", methods=["GET", "POST"])
def userlogin():
    try:
        err = request.args.get('login')
        if err:
            flash(err)
    except:
        pass
    if request.method=="GET":
        import random
        quotelist = ["Music is the Spirit for Long Tasks🤓", "Going for a long ride😶‍🌫️? We got u!!!", "If words can touch u emotionally, then I wonder what music has got for you🫣","Don't Overthink and just Dive in nd let urself flow😮‍💨"]
        return render_template("UserLogin.html", quote=random.choice(quotelist))
    if request.method=="POST":
        u=request.form['uname']
        p=request.form['passs']
        if not u or not p:
            flash("Provide Some input!!")
            return redirect("/UserLogin/")
        try:
            user= User.query.filter(User.name==u).first()
        except:
            flash("Not Processing")
            return redirect("/UserLogin/")
        if not user:
            flash("Invalid User!!")
            return redirect("/UserLogin/")
        x={u: user.pwd, 'username': user.user_id, "status": user.status}
        if (x[u]!=p):
            flash("Invalid Password")
            return redirect("/UserLogin/")
        if (x["status"]!=1):
            flash("User is Locked")
            return redirect("/UserLogin/")
        UserStatusList[x['username']] = 1
        return redirect(f"/UserHome/{x['username']}")

@app.route("/UserHome/<int:id>/hashed")
@app.route("/UserProfile/<int:id>/hashed")
@app.route("/showcreators/<int:id>/hashed")
@app.route("/ViewAlbums/<int:id>/hashed")
@app.route("/creatorprofile/<int:id>/hashed")
def userhash(id):      # special button
    return render_template("Hashed.html")

@app.route("/UserHome/<int:userid>/")
def userHome(userid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        try:        # for displaying locked creators
            err = request.args.get('login')
            if err:
                flash(err)
        except:
            pass
        mylist=[]
        songs= Song.query.all()
        for song in songs:
            mylist.append([song.song_id,song.name,song.status])
        plqy = Playlist.query.filter(Playlist.user_id==userid)
        userplsongs={}
        for pls in plqy:
            id = pls.pl_id
            plname=pls.name
            qy = PlaylistRelation.query.filter(PlaylistRelation.pl_id==id)
            songs=[]
            for i in qy:
                songs.append(i.song_id)
            for songid in songs:
                songq= Song.query.filter(Song.song_id==songid)
                for s in songq:
                    if (id,plname) in userplsongs.keys():
                        userplsongs[(id,plname)].append([s.song_id,s.name,s.status])
                    else:
                        userplsongs[(id,plname)]=[[s.song_id,s.name,s.status]]
        return render_template("Dashboard.html", mylist=mylist, user_id=userid, myplaylists=userplsongs)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/showcreators/<int:user_id>/")
def showcreators(user_id):
    try:        # if user is logged in
        if (UserStatusList[user_id] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        cr = Creator.query.all()
        list=[]
        idlist=[]
        for i in cr:
            list.append(i)
            idlist.append(i.cr_id)
        albums={}
        for id in idlist:
            qy = Album.query.filter(Album.cr_id==id)
            for i in qy:
                if id in albums.keys():
                    albums[id].append(i.name)
                else:
                    albums[id]=[i.name]
        flqy= UserCreatorFollowers.query.filter(UserCreatorFollowers.user_id==user_id)
        followerlist=[]
        for i in flqy:
            followerlist.append(i.cr_id)
        return render_template("ViewCreators.html", user_id=user_id, creators=list, albums=albums, followerlist=followerlist)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/FollowCreator", methods=["GET","POST"])
def followCreator():
    user=request.args.get('user')
    creator=request.args.get('creator')
    try:        # if user is logged in
        if (UserStatusList[int(user)] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        try:
            record = UserCreatorFollowers(user_id=user, cr_id= creator)
            print(record)
            db.session.add(record)
            db.session.commit()
        except:
            print("backend error")
        return redirect(f"/showcreators/{user}")
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/UnfollowCreator", methods=["GET","POST"])
def unfollowCreator():
    user=request.args.get('user')
    creator=request.args.get('creator')
    try:        # if user is logged in
        if (UserStatusList[int(user)] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        try:
            qy = text(f"Delete from UserCreatorFollowers where user_id={user} and cr_id={creator}")
            db.session.execute(qy)
            db.session.commit()
        except:
            print("backend error")
        return redirect(f"/showcreators/{user}")
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/ViewAlbums/<int:userid>/", methods=["GET", "POST"])
def viewalbums(userid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        album = request.args.get('album')
        if (not album):
            sql = text("select * from Album")
        else:
            sql = text(f"select * from Album where name='{album}'")
        alb = db.session.execute(sql)
        albumlist = {}
        for i in alb:
            albumlist[(i.album_id, i.name, i.likes)]=[]
        for (id, name, likes) in albumlist:            #getting songs for each 
            song=Song.query.filter(Song.album_id==id)
            for i in song:
                albumlist[(id, name, likes)].append([i.song_id,i.name, i.genre,"{:.2f}".format(i.duration), "{:.2f}".format(i.Rating)])
        return render_template("ViewAlbums.html", userid=userid, albumlist=albumlist, album=album)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/LikeAlbum/<int:userid>/<int:albumid>/", methods=["POST"])
def likealbum(userid, albumid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        qy= Album.query.filter(Album.album_id==albumid).first()
        qy.likes = (int(qy.likes)+1)
        db.session.commit()
        return redirect(f"/ViewAlbums/{userid}")
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/makenewplaylist/<int:userid>/", methods=["GET", "POST"])
def makenewplaylist(userid):
    if request.method == "GET":
        return render_template("MakeNewPlaylist.html", userid=userid)

    if request.method == "POST":
        try:        # if user is logged in
            if (UserStatusList[userid] == 1):
                status = 1
            else:
                status = 0
        except KeyError:
            status = 0
        if (status == 1):
            plname = request.form['plName']
            playlist_to_reg = Playlist(name=plname, user_id= userid)
            db.session.add(playlist_to_reg)
            db.session.commit()
            return redirect(f'/UserHome/{userid}')
        else:
            return redirect("/UserLogin/?login=No Session Found!")

@app.route("/addsongstoplaylist/<int:userid>/", methods=["GET", "POST"])
def addsongtopl(userid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        if request.method=="GET":
            qy= Song.query.all()
            songs=[]
            for i in qy:
                songs.append([i.song_id, i.name])
            pl= Playlist.query.filter(Playlist.user_id==userid)
            playlists=[]
            for i in pl:
                playlists.append([i.pl_id, i.name])
            return render_template("AddSongsToPlaylist.html", userid=userid, songs=songs, playlists=playlists)
        if request.method=="POST":
            songid = request.form['song']
            plid = request.form['playlist']
            plqy= Playlist.query.filter(Playlist.pl_id==plid).first()
            plqy.qty= plqy.qty+1
            playlist_to_reg = PlaylistRelation(song_id=songid,pl_id=plid, user_id= userid)
            db.session.add(playlist_to_reg)
            db.session.commit()
            return redirect(f'/UserHome/{userid}')
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/songPlay/<int:userid>/<int:songid>/<string:songname>/", methods=["GET", "POST"])
def songplay(userid ,songid, songname):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        with open(f"static/lyrics/{songid}.txt", 'r', encoding='utf-8') as file:
            content=file.read()
        musfile=f"{songid}.mp3"
        qy = Song.query.filter(Song.song_id==songid).first()
        rating= qy.Rating
        crid= qy.cr_id
        status = qy.status
        if status != 1:
            return render_template("SongPlay.html", status=0, userid=userid)
        crname= Creator.query.filter(Creator.cr_id==crid).first().name
        user= User.query.filter(User.user_id==userid).first()
        user.playtime=user.playtime+1
        song= Song.query.filter(Song.song_id==songid).first()
        song.play_time=song.play_time+1
        db.session.commit()
        if userid in recent_plays.keys():
            if songid not in recent_plays[userid]:
                recent_plays[userid].append([songid, songname])
        else:
            recent_plays[userid]=[[songid,songname]]
        return render_template("SongPlay.html", userid=userid, songid=songid, songname=songname, lyrics=content, file=musfile, rating=rating, creatorname=crname, status=1)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/RateSong/<int:userid>/<int:songid>/<string:songname>", methods=["GET","POST"])
def ratesong(userid, songid, songname):
    if request.method=="POST":
        rating= request.form['ratedata']
        qy= Song.query.filter(Song.song_id==songid).first()
        qy.Rating = (float(qy.Rating)+ float(rating))/2
        db.session.commit()
        with open(f"static/lyrics/{songid}.txt", 'r', encoding='utf-8') as file:
            content=file.read()
        musfile=f"{songid}.mp3"
        return render_template("SongPlay.html", userid=userid, songid=songid, songname=songname, lyrics=content, file=musfile, msg="Successfully Rated the Song!")

@app.route("/songRemove/<int:userid>/<int:songid>/<int:plid>", methods=["GET","POST"])
def songremove(userid ,songid, plid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        sql = text(f"Delete from PlaylistRelation where song_id={songid} AND pl_id={plid}")
        db.session.execute(sql)
        db.session.commit()
        return redirect(f"/UserHome/{userid}/")
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/SearchForAlbum/<int:userid>/", methods=["POST"])
def searchforalbum(userid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        data=request.form['searchdata'].lower()
        if not data:
            flash("No data")
            return redirect(f"/UserHome/{userid}/")
        sql = text(r"select * from Album where lower(name) like '%{}%'".format(data))
        alb = db.session.execute(sql)
        albumlist = {}
        for i in alb:
            albumlist[(i.album_id, i.name)]=[]
        searchfor=f"Album like: {data}"
        if albumlist!={}: 
            for (id, name) in albumlist:            #getting songs for album search 
                song=Song.query.filter(Song.album_id==id)
                for i in song:
                    albumlist[(id, name)].append([i.song_id,i.name])
        else:
            sql = text(r"select * from Song where lower(genre) like '%{}%'".format(data))
            song = db.session.execute(sql)
            albumlist[(0,"Songs:")]=[]
            for i in song:
                albumlist[(0, "Songs:")].append([i.song_id,i.name])
            searchfor=f"Genre like: {data}"
        return render_template("SearchForAlbum.html", userid=userid, albumlist=albumlist, searchfor=searchfor)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/SearchForSong/<int:userid>/", methods=["POST"])
def searchforsong(userid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        data=request.form['searchdata'].lower()
        if not data:
            flash("No data")
            return redirect(f"/UserHome/{userid}/")
        sql = text(r"select * from Song where lower(name) like '%{}%'".format(data))
        alb = db.session.execute(sql)
        songlist = []
        for i in alb:
            songlist.append([i.song_id,i.name])
        searchfor=f"song like: {data}"
        if songlist==[]: 
            sql = text(r"select * from Song where lower(genre) like '%{}%'".format(data))
            song = db.session.execute(sql)
            for i in song:
                songlist.append([i.song_id,i.name])
            searchfor=f"Genre like: {data}"
        return render_template("SearchForSong.html", userid=userid, songlist=songlist, searchfor=searchfor)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/UserProfile/<int:userid>/")
def userprofile(userid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        qy= User.query.filter(User.user_id==userid).first()
        try:
            recents = recent_plays[userid]
        except KeyError:
            recents = None
        
        return render_template("UserProfile.html", userid=userid,data=qy, recentplays= recents)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/LogoutUser/<int:userid>")
def userlogout(userid):
    try:
        UserStatusList[userid] = 0
    except KeyError:
        pass
    return redirect("/?session=logout")

# --------------------- Creator -----------------------------------------------------
@app.route("/creatorprofile/<int:userid>/", methods=["GET", "POST"])
def creator(userid):
    try:
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status ==1):
        cr = Creator.query.filter(Creator.user_id==userid)
        if not cr:
            return redirectf("/creatorprofile/RegisterCreator/{userid}")
        crid=None
        crname=None
        crstatus = None
        for i in cr:
            crid= i.cr_id
            crname = i.name
            crstatus = i.status
        print(crid)
        if (crstatus==0):
            return redirect(f"/UserHome/{userid}/?login=Creator is Blacklisted!")
        albumlist={}
        if (crid==None):
            return redirect(f"/creatorprofile/RegisterCreator/{userid}")
        alb= Album.query.filter(Album.cr_id==crid)      # getting all the albums
        for i in alb:
            albumlist[(i.album_id, i.name, i.song_qty,i.status)]=[]
        for (id, name, qty, status) in albumlist:            #getting songs for each 
            song=Song.query.filter(Song.album_id==id)
            for i in song:
                albumlist[(id, name, qty, status)].append([i.song_id,i.name, i.play_time,i.status])

        return render_template("CreatorProfile.html", crid=crid , uname=crname, albumlist=albumlist, userid=userid)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/creatorprofile/RegisterCreator/<int:userid>/", methods=["GET", "POST"])
def registercreator(userid):
    if request.method=="GET":
        return render_template("RegisterCreator.html",un= userid)
    if request.method=="POST":
        cname= request.form['cname']
        cr_to_reg = Creator(name=cname, user_id= userid)
        db.session.add(cr_to_reg)
        db.session.commit()
        return redirect('/creatorprofile/')

@app.route("/CreatorDetails/<int:userid>/<int:crid>/")
def creatordetails(userid, crid):
    try:
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        crqy= Creator.query.filter(Creator.cr_id==crid).first()
        songqy = Song.query.filter(Song.cr_id==crid)
        songrat = []
        for i in songqy:
            songrat.append(i.Rating)
        crqy.rating= sum(songrat)/len(songrat)
        db.session.commit()
        return render_template("CreatorDetails.html", userid=userid,data=crqy)
    else:
        return redirect('/UserLogin/?login=No Session Found')

@app.route("/makenewalbum/<int:crid>/", methods=["GET", "POST"])
def makenewalbum(crid):
    if request.method == "GET":
        cr = Creator.query.filter(Creator.cr_id==crid)
        for i in cr:
            userid= i.user_id
        return render_template("MakeNewAlbum.html", userid=userid, crid=crid)

    if request.method == "POST":
        albname = request.form['albumName']

        album_to_reg = Album(name=albname, cr_id= crid)
        db.session.add(album_to_reg)
        db.session.commit()
        return redirect('/UserLogin/')

@app.route("/addsong/<int:crid>/", methods=["GET", "POST"])
def addsong(crid):
    if request.method == "GET":
        cr = Creator.query.filter(Creator.cr_id==crid)
        for i in cr:
            userid= i.user_id
        album={}
        albumqy= Album.query.filter(Album.cr_id==crid)
        for alb in albumqy:
            album[alb.album_id]=alb.name
        db.session.commit()
        return render_template("AddSong.html", userid=userid, crid=crid, album=album)

    if request.method == "POST":
        Songname = request.form['songName']
        genre= request.form['genre']
        duration= request.form['duration']
        album_id= int(request.form['albumId'])
        albumqy= Album.query.filter(Album.album_id==album_id).first()
        albumqy.song_qty= int(albumqy.song_qty)+1
        Song_to_reg = Song(name=Songname, cr_id= crid, album_id=album_id, genre=genre, duration=duration)
        db.session.add(Song_to_reg)
        db.session.commit()
        id=0
        song= Song.query.filter(Song.name==Songname)
        for i in song:
            id= i.song_id
        with open(f"static/lyrics/{id}.txt", "a", encoding='utf-8') as file:
            file.write(request.form['lyrics'])
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        # if file.filename == '':
        #     flash('No selected file')
        #     return redirect(request.url)
        fn = file.filename.split(".")
        filetype=fn[1]

        file.save(f"{os. getcwd()}\\static\\{id}.{filetype}")

        return redirect(f'/UserLogin/')

@app.route("/CrSearchForSong/<int:crid>/<int:userid>/", methods=["POST"])
def crsearchforsong(crid, userid):
    try:        # if user is logged in
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        data=request.form['searchdata'].lower()
        if not data:
            flash("No data")
            return redirect(f"/creatorprofile/{userid}/")
        sql = text(r"select * from Song where lower(name) like '%{}%' and cr_id ={}".format(data,crid))
        alb = db.session.execute(sql)
        songlist = []
        for i in alb:
            songlist.append([i.song_id,i.name,i.play_time ,i.status])
        searchfor=f"song like: {data}"
        if songlist==[]: 
            sql = text(r"select * from Song where lower(genre) like '%{}%' and cr_id ={}".format(data,crid))
            song = db.session.execute(sql)
            for i in song:
                songlist.append([i.song_id,i.name,i.play_time ,i.status])
            searchfor=f"Genre like: {data}"
        return render_template("CrSearchForSong.html", userid=userid, crid=crid, songlist=songlist, searchfor=searchfor)
    else:
        return redirect("/UserLogin/?login=No Session Found!")

@app.route("/AlterAlbum/<int:userid>/<int:crid>/", methods=["GET", "POST"])
def AlterAlbum(userid, crid):
    try:
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        if request.method=="GET":
            songqy= Song.query.filter(Song.cr_id==crid)
            songs=[]
            for i in songqy:
                songs.append([i.song_id, i.name])
            albqy= Album.query.filter(Album.cr_id==crid)
            albums=[]
            for i in albqy:
                albums.append([i.album_id, i.name])
            return render_template("AlterAlbum.html", userid=userid, crid=crid,songs=songs, albums=albums)
        if request.method=="POST":
            songid=request.form['song']
            albumid= request.form['album']
            songqy = Song.query.filter(Song.song_id==songid).first()
            albumqy = Album.query.filter(Album.album_id==songqy.album_id).first()
            albumqy.song_qty= albumqy.song_qty-1
            songqy.album_id=albumid
            albumqy2 = Album.query.filter(Album.album_id==songqy.album_id).first()
            albumqy2.song_qty= albumqy.song_qty+1
            db.session.commit()
            return redirect(f'/creatorprofile/{userid}')
    else:
        return redirect('/UserLogin/?login=No Session Found')

@app.route("/EditSong/<int:userid>/<int:crid>/<songid>/", methods=["GET", "POST"])
def editsongcr(userid, crid, songid):
    try:
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        if request.method=="GET":
            s= Song.query.filter(Song.song_id==songid).first()
            qy= Album.query.all()
            albums={}
            for i in qy:
                albums[i.album_id]=i.name
            with open(f"static/lyrics/{songid}.txt", "r", encoding="utf-8") as file:
                lyrics=file.read()
            return render_template("EditSong.html", userid=userid,crid=crid, songid=songid, song=s, albums=albums, lyrics=lyrics)
        if request.method=="POST":
            qy = Song.query.filter(Song.song_id==songid).first()
            qy.name = request.form['songName']
            qy.genre = request.form['genre']
            qy.duration = request.form['duration']
            qy.cr_id=crid
            qy.album_id = request.form['albumId']
            db.session.commit()
            lys= request.form['lyrics']
            with open(f'static/lyrics/{songid}.txt','w', encoding='utf-8') as file:
                file.write(lys)
            return redirect(f"\creatorprofile\{userid}")
    else:
        return redirect('/UserLogin/?login=No Session Found')

@app.route("/DeleteSong/<int:userid>/<int:songid>/", methods=["GET", "POST"])
def deletesong(userid, songid):
    try:
        if (UserStatusList[userid] == 1):
            status = 1
        else:
            status = 0
    except KeyError:
        status = 0
    if (status == 1):
        try:
            song= text(f"delete from song where song_id={songid}")
            db.session.execute(song)
            db.session.commit()
            try:
                os.remove(f"static/lyrics/{songid}.txt") 
                os.remove(f"static/{songid}.mp3")
            except:
                flash("Song delete but no files founds to delete")
            flash("Successfully deleted!")
            return redirect(f"/creatorprofile/{userid}/")
        except:
            flash("oopps! Something went wrong")
    else:
        return redirect('/UserLogin/?login=No Session Found')

