#coding:utf-8
#!/bin/python3
import random,math,pygame,time
import _thread
from pygame.locals import *

tex,tey=1000,800
pygame.init()
fenetre=pygame.display.set_mode([tex,tey])
pygame.key.set_repeat(40,30)
font=pygame.font.SysFont("Serif",15)
cam=[0,0]

mats=[["eau",997,(0,50,150),None],["bois sapin",450,(43,30,8),None] , ["acier",7850,(150,150,150),None] , ["or",19300,(88,78,10),None] , ["bronze",8800,(27,18,3),None] , ["argent",10500,(185,185,185),None],["Soleil",1410,(250,250,0),"images/Soleil.png"],["Terre",5510,(100,100,200),"images/Terre.png"],["trou noir",135740000,(20,20,20),None]]
#0=nom , 1=masse volumique , 2=couleur , 3=image

cg=6.67408*10**-11 #Constante gravitationelle

objs=[] #liste des objets
objsel=None #objets selectioné/ suivi
msel=0 #matiere selctioné
tcurs=10 #taille du curseur 
activtraces=True #Si les traces sont activées
fps=0 #nombre de fps

dc=None
pause=False #Si le jeu est en pause
encour=True #Si le jeu lance
vitcam=10 #la vitesse de la camera a l'ecran
tpa=0.5

tpact=0.001

tet=tpact #Temps entre les traces
nbtracestoaff=100 #nombre de traces maximal d'affichage
tpeg=tpact #Temps entre l'actualisation de la gravité
dgr=time.time() #Derniere gravitée
tpaff=tpact #Temps entre l'actualisation de l'affichage
daff=time.time() #Derniere affichage

#Classe Objet
class Objet:
    def __init__(self,x,y,t,m,vix,viy):
        self.px=x #Sa position X
        self.py=y #Sa position Y
        self.ray=t  #Son rayon, l'objet est un disque
        self.mat=m #Sa matière
        self.aire=math.pi*math.pow(self.ray,2) #Son aire
        self.masse=m[1]*self.aire  #Sa masse
        self.cl=m[2] #Sa couleur
        self.rect=pygame.draw.circle(fenetre,self.cl,(self.px,self.py),self.ray,0) #Son  rectangle de collision
        self.vitx=vix #Sa vitesse X
        self.vity=viy #Sa vitesse Y
        self.image=None #Son Image
        self.traces=[] #Ses Traces
        if m[3]!=None: #Si il y a une image pour la matiere de l'objet
            self.image=pygame.transform.scale(pygame.image.load(m[3]),[self.ray*2,self.ray*2])  #on prend son image
        self.ct=time.time() #derniere fois qu'il a calculé sa trace
        self.dgr=time.time() #Derniere actualisation de la gravité

def aff(objs,msel,tcurs,poscurs,fps,dc,pause,cam,objsel,activtraces): # fonction aff
    fenetre.fill((0,0,0)) #on nettoie l'écran
    noa=0 #Nombre d'Objets qui sont en collision avec le curseur de la souris
    for o in objs: #on parcour les images
        if o.px-o.ray >= 0 and o.px+o.ray <= tex and o.py-o.ray >= 0 and o.py+o.ray <= tey:
            if o.image==None: o.rect=pygame.draw.circle(fenetre,o.cl,(cam[0]+int(o.px),cam[1]+int(o.py)),o.ray,0)  #on affiche l'objet avec sa couleur
            else: o.rect=fenetre.blit(o.image,[cam[0]+int(o.px-o.ray),cam[1]+int(o.py-o.ray)]) #on affiche l'objet avec son image
            if o.rect.collidepoint(poscurs): #si l'objet touche le curseur de la souris
                fenetre.blit(font.render("objet : pos : "+str(int(o.px))+" , "+str(int(o.py))+"  mat : "+o.mat[0]+" masse : "+str(o.masse/1000)+"kg aire : "+str(o.aire)+"px²",15,(255,255,255)),[15,110+15*noa]) #on affiche ses informations
                noa+=1 #on augmente le nombre d'objets qui sont en collision avec le curseur de la souris
        if activtraces: #si les traces sont activées
            for t in o.traces[-nbtracestoaff:]: #on parcour toutes les traces
                t1x,t1y=cam[0]+t[0],cam[1]+t[1] #on calcule les positions de la trace
                t2x,t2y=cam[0]+t[2],cam[1]+t[3] #on calcule les positions de la trace
                if (t1x>=0 and t1x<tex and t1y >= 0 and t1y < tey) or (t2x>=0 and t2x<tex and t2y >= 0 and t2y < tey): #si la trace est dans l'écran
                    pygame.draw.line(fenetre,o.cl,(t1x,t1y),(t2x,t2y),1) #on affiche la trace
    if dc!=None:
        pygame.draw.line(fenetre,(0,0,255),dc,pos,2)
    pygame.draw.circle(fenetre,(0,0,255),(poscurs[0],poscurs[1]),tcurs,1)
    fenetre.blit(font.render("matiere sel : "+mats[msel][0],15,(255,255,255)),[15,50])
    fenetre.blit(font.render(str(fps)+" fps",15,(255,255,255)),[15,15])
    fenetre.blit(font.render("nb objs : "+str(len(objs)),15,(255,255,255)),[15,90])
    if pause: fenetre.blit(font.render("PAUSE",15,(255,185,0)),[505,15])
    if activtraces: fenetre.blit(font.render("traces",15,(0,185,85)),[805,15])
    if objsel!=None: fenetre.blit(font.render("objsel = "+str(objs[objsel]),15,(255,185,0)),[505,45])
    pygame.display.update()

def grav(objs,pause,activtraces):
    if not pause:
        for o in objs:
            for oo in objs:
                if o!=oo and (o.px!=oo.px or o.py!=oo.py):
                    fg=(cg*o.masse*oo.masse)/math.pow(math.sqrt(math.pow(o.px-oo.px,2)+math.pow(o.py-oo.py,2)),2)
                    #fg/=o.masse
                    v=fg
                    a=oo.px-o.px
                    b=oo.py-o.py
                    c=math.sqrt(a*a+b*b)
                    if c<=v:
                        o.px=oo.px
                        o.py=oo.py
                    else:
                        e=(b*v)/c
                        d=(a*v)/c
                        o.vitx+=d
                        o.vity+=e
        for o in objs:
            ax=o.px
            ay=o.py
            o.px+=o.vitx
            o.py+=o.vity
            if activtraces and time.time()-o.ct>=tet:
                o.ct=time.time()
                o.traces.append([ax,ay,o.px,o.py])


def gere_obj_grav(io):
    global objs,objsel,msel,tcurs,activtraces,dc,pause,encour,vitcam,tpa,tet,nbtracestoaff,fps,cam,pos,daff,dgr
    while encour:
        o=objs[io]
        if time.time()-o.dgr>=tpeg:
            o.dgr=time.time()
            #
            for oo in objs:
                if o!=oo and (o.px!=oo.px or o.py!=oo.py):
                    fg=(cg*o.masse*oo.masse)/math.pow(math.sqrt(math.pow(o.px-oo.px,2)+math.pow(o.py-oo.py,2)),2)
                    #fg/=o.masse
                    v=fg
                    a=oo.px-o.px
                    b=oo.py-o.py
                    c=math.sqrt(a*a+b*b)
                    if c<=v:
                        o.px=oo.px
                        o.py=oo.py
                    else:
                        e=(b*v)/c
                        d=(a*v)/c
                        o.vitx+=d
                        o.vity+=e
            #
            ax=o.px
            ay=o.py
            o.px+=o.vitx
            o.py+=o.vity
            if activtraces and time.time()-o.ct>=tet:
                o.ct=time.time()
                o.traces.append([ax,ay,o.px,o.py])


def thread_grav():
    global objs,objsel,msel,tcurs,activtraces,dc,pause,encour,vitcam,tpa,tet,nbtracestoaff,fps,cam,pos,daff,dgr
    while encour:
        if time.time()-dgr>=tpeg:
            dgr=time.time()
            grav(objs,pause,activtraces)

def thread_aff():
    global objs,objsel,msel,tcurs,activtraces,dc,pause,encour,vitcam,tpa,tet,nbtracestoaff,fps,cam,pos,daff,dgr
    while encour:
        if time.time()-daff>=tpaff:
            t1=time.time()
            #
            daff=time.time()
            if objsel!=None:
                cam=[int(tex/2-objs[objsel].px),int(tey/2-objs[objsel].py)]
            aff(objs,msel,tcurs,pos,fps,dc,pause,cam,objsel,activtraces)
            #
            tt=time.time()-t1
            if tt!=0: fps=int(1.0/tt)
     
        
def main_thread():
    global objs,objsel,msel,tcurs,activtraces,dc,pause,encour,vitcam,tpa,tet,nbtracestoaff,fps,cam,pos,daff,dgr
    while encour:
        pos=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==QUIT: exit()
            elif event.type==KEYDOWN:
                if event.key in [K_ESCAPE,K_q]: encour=False
                elif event.key==K_SPACE:
                    pause=not pause
                    time.sleep(tpa)
                elif event.key==K_BACKSPACE:
                    objs=[]
                    objsel=None
                elif event.key==K_UP: cam[1]+=vitcam
                elif event.key==K_DOWN: cam[1]-=vitcam
                elif event.key==K_LEFT: cam[0]+=vitcam
                elif event.key==K_RIGHT: cam[0]-=vitcam
                elif event.key==K_PAGEUP:
                    if objsel==None and objs!=[]:
                        objsel=0
                    else:
                        objsel+=1
                        if objsel>=len(objs): objsel=None
                    time.sleep(tpa)
                elif event.key==K_PAGEDOWN:
                    if objsel==None and objs!=[]:
                        objsel=len(objs)-1
                    else:
                        objsel-=1
                        if objsel<0: objsel=None
                    time.sleep(tpa)
                elif event.key==K_t:
                    activtraces=not activtraces
                    for o in objs: o.traces=[]
                    time.sleep(tpa)
            if event.type==MOUSEBUTTONDOWN:
                dc=pos
            if event.type==MOUSEBUTTONUP:
                if event.button==1:
                    avitx=(pos[0]-dc[0])/100
                    avity=(pos[1]-dc[1])/100
                    objs.append( Objet(-cam[0]+pos[0],-cam[1]+pos[1],tcurs,mats[msel],avitx,avity) )
                    #_thread.start_new_thread(gere_obj_grav , (len(objs)-1,))

                if event.button==3:
                    msel+=1
                    if msel >= len(mats): msel=0
                if event.button==4:
                    if tcurs<150: tcurs+=1
                if event.button==5:
                    if tcurs>1: tcurs-=1
                dc=None
        

_thread.start_new_thread(thread_grav , ())
_thread.start_new_thread(thread_aff , ())
main_thread()









