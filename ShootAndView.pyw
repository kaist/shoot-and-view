#coding:utf-8
"""
    Copyright (C) 2010 Igor zalomskij <igor.kaist@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from Tkinter import *
from ttk import *
import sdwificard
import glob
import ImageTk
import os
import Image
import tkMessageBox
import sys



if hasattr(sys,"frozen") and sys.frozen == "windows_exe":
    os.chdir(os.path.dirname(sys.executable))


root=Tk()
root.title('Shoot&View Transcend WiFi')
root.minsize(640,360)

HOME_DIR=os.path.expanduser('~')
if not os.path.exists(HOME_DIR+'/'+'ShootAndView'):
	os.mkdir(HOME_DIR+'/'+'ShootAndView')
HOME_DIR=HOME_DIR+'/ShootAndView/'
#sys.stderr=open(HOME_DIR+'err.txt','w')

if sys.platform=='win32':
	root.iconbitmap('app/images/icon.ico')
	#root.resizable(0,0)
	root.state("zoomed")
else:
	root.geometry("%sx%s+0+0"%(root.winfo_screenwidth(),root.winfo_screenheight()))

class CreateImages:
	def __init__(self):
		self.img={}
		for i in glob.glob('app/images/*.png'):
			self.img[i.split(os.sep)[-1].split('.')[0]]=ImageTk.PhotoImage(file=i)
imgs=CreateImages()


class App:
	def __init__(self):
		self.sd=sdwificard.SDCard(home_dir=HOME_DIR)
		self.current_image=0
		self.exiftoolflag=False
		
		Style().configure('big.TButton',font=('bold',18),width=15)
		
		self.start_screen=Frame(root)
		self.start_screen.pack(expand=1,fill=BOTH)
		self.main_main_screen=Frame(root)

		self.main_screen=Frame(self.main_main_screen)
		self.main_screen.pack(expand=1,fill=BOTH)		

		
		root.bind('<KeyPress-Left>',self.key_press_left)		
		root.bind('<KeyPress-Right>',self.key_press_right)
		root.bind('<space>',self.key_press_space)
		root.bind('<B1-Motion>',self.c_motion)
		root.bind('<Button-1>',self.c_press)
		self.zoom_state=0

		self.download_frame=Frame(self.main_screen)
		self.download_frame.place(relx=0.5,rely=0.5,anchor=CENTER)
		self.download_label=Label(self.download_frame,text='Start shooting now!',font=('Tahoma',24))
		self.download_label.grid(row=0,column=0)
		self.download_progress=Progressbar(self.download_frame,length=400)
		self.download_progress.grid(row=1,column=0)
		

		self.status_frame=Frame(self.main_main_screen,relief=GROOVE)
		self.status_frame.pack(pady=2,padx=50,fill=X)
		self.info_label=Label(self.status_frame,text='')
		self.info_label.pack(padx=5,pady=2)


		self.canvas = Canvas(self.main_screen, bd=0)
		self.canvas.place(relx=0,rely=0,anchor=SE)
		
		
		self.image_label=Label(self.main_screen,text='')
		self.image_label.place(relx=0.0,rely=0.0,anchor=CENTER)
		
		self.start_button_frame=Frame(self.start_screen)
		self.start_button_frame.place(relx=0.5,rely=0.5,anchor=CENTER)

		
		self.chk_state = IntVar()
		self.chk_state.set(True)
		try:ln=len(eval(open(HOME_DIR+'last_session.dat').read()))
		except:
			ln=0

		self.check = Checkbutton(self.start_button_frame, text="Use the previous session of %s photos. Or "%(ln), variable=self.chk_state)
		self.check.grid(row=1,column=0,padx=0,pady=10)
		
		
		self.delete_session_button=Button(self.start_button_frame,text='delete',command=self.delete_session)
		self.delete_session_button.grid(row=1,column=1,padx=0,pady=10)		
		
		if ln==0:
			self.chk_state.set(False)
			self.check['state']='disable'
			self.delete_session_button['state']='disable'
			

			
		Label(self.start_button_frame,text='all images.').grid(row=1,column=2,padx=0,pady=10)
		
		self.search_button=Button(self.start_button_frame,style='big.TButton',image=imgs.img['find'],compound='left',text='Search SD card',command=self.start_search)
		self.search_button.grid(row=0,column=0,columnspan=3)
		
		self.ip_panel=Labelframe(self.start_screen,text='IP adress of computer')
		self.ip_panel.place(relx=0,rely=1,anchor=SW)
		self.ip_entry=Entry(self.ip_panel,width=20,cursor='xterm')
		self.ip_entry.grid(row=0,column=0,padx=5,pady=5)
		self.ip_entry.insert(END,self.sd.ip)
		self.ip_entry['state']='disable'
		
		self.change_button_state=False
		self.edit_button=Button(self.ip_panel,text='Change',command=self.change_button_callback)
		self.edit_button.grid(row=0,column=1,padx=5,pady=5)

	def delete_session(self):
		if tkMessageBox.askyesno("Delete", "Delete last session and all images from computer (not camera)?"):
			os.remove(HOME_DIR+'last_session.dat')
			for x in os.listdir(HOME_DIR):
				os.remove(HOME_DIR+x)

			self.chk_state.set(False)
			self.check['text']="Use the previous session of 0 photos. Or "
			self.check['state']='disable'
			self.delete_session_button['state']='disable'


	def change_button_callback(self):
		if self.change_button_state==False:
			self.ip_entry['state']='normal'
			self.edit_button['text']='Save'
		else:
			self.ip_entry['state']='disable'		
			self.edit_button['text']='Change'
			self.sd.ip=self.ip_entry.get()
		self.change_button_state=not self.change_button_state
		
	
	def start_search(self):

		self.search_button['text']='Searching...'
		self.search_button['state']='disable'
		self.search_button['image']=imgs.img['wait']
		self.sd.find_card(callback=self.find_callback)
	
	def find_callback(self,ip):
		if not ip:return
		if self.chk_state.get():
			self.sd.all_files=eval(open(HOME_DIR+'last_session.dat').read())
			self.current_image=len(self.sd.all_files)-1
		self.start_screen.destroy()
		self.main_main_screen.pack(expand=1,fill=BOTH)
		#root.update()
		self.sd.start_listen(self.new_callback,self.download_callback,self.download_complete)
		
		if self.chk_state.get():
			self.sd.all_files=eval(open(HOME_DIR+'last_session.dat').read())
			self.current_image=len(self.sd.all_files)-1
			self.update_screen()
		
		
	def download_callback(self,blocks, block_size, total_size):
		try:pers=int(float(blocks*block_size)/float(total_size)*100.0)
		except:pass
		if self.sd.all_files[self.current_image]==self.sd.download_now:
			#self.download_label['image']=imgs.img['wait']
			if self.zoom_state==2:
				self.canvas.delete(ALL)
				self.canvas.place(relx=0,rely=0,anchor=CENTER)
				self.zoom_state=1
			self.download_frame.place(relx=0.5,rely=0.5,anchor=CENTER)
			self.image_label.place(relx=0.0,rely=0.0,anchor=SE)
			self.download_label['text']='Downloading '+self.sd.download_now.split('/')[-1]
			
			self.info_label['text']='Downloading %s %s%%'%(self.sd.download_now.split('/')[-1],pers)
			
			self.download_progress['value']=pers
			self.zoom_state=0
		
	def new_callback(self,new_file):
		open(HOME_DIR+'last_session.dat','w').write(repr(self.sd.all_files))
		self.current_image=len(self.sd.all_files)-1
		self.update_screen()
		
		
	def download_complete(self,file):
		if self.sd.all_files[self.current_image]==file:

			img=Image.open(HOME_DIR+file.split('/')[-1])
			img.load()
			rotate,exf=self.orient(HOME_DIR+file.split('/')[-1])
			if rotate:img=img.rotate(rotate)
			self.info_label['text']='(%s/%s) %s (%sx%s)               f/%s     1/%s    ISO:%s    %s mm.'%(self.current_image+1,len(self.sd.all_files),file.split('/')[-1],img.size[0],img.size[1],exf['f'],exf['s'],exf['iso'],exf['focal'])
			
			img.thumbnail((self.main_screen.winfo_width(),self.main_screen.winfo_height()))


			self.screen_img=ImageTk.PhotoImage(img)
			self.zoom_state=1

			self.image_label['image']=self.screen_img
			self.download_frame.place(relx=0,rely=0,anchor=SE)

			self.image_label.place(relx=0.5,rely=0.5,anchor=CENTER)



		
	def update_screen(self):
		file=self.sd.all_files[self.current_image].split('/')[-1]
		if not os.path.exists(HOME_DIR+file):
			if self.zoom_state==2:
				self.canvas.delete(ALL)
				self.canvas.place(relx=0,rely=0,anchor=SE)
				self.zoom_state=0
			self.download_frame.place(relx=0.5,rely=0.5,anchor=CENTER)
			self.image_label.place(relx=0.0,rely=0.0,anchor=SE)
			self.download_label['text']='Downloading '+file
			self.zoom_state=0
			self.download_progress['value']=0
			if self.sd.all_files[self.current_image] not in self.sd.in_queue:
				self.sd.download_list.put(self.sd.all_files[self.current_image])
		else:
			try:
				img=Image.open(HOME_DIR+file.split('/')[-1])
				img.load()
				rotate,exf=self.orient(HOME_DIR+file.split('/')[-1])
				if rotate:img=img.rotate(rotate)
				self.info_label['text']='(%s/%s) %s (%sx%s)               f/%s     1/%s    ISO:%s    %s mm.'%(self.current_image+1,len(self.sd.all_files),file.split('/')[-1],img.size[0],img.size[1],exf['f'],exf['s'],exf['iso'],exf['focal'])
			except:
				return
			if self.zoom_state==2:
				self.canvas.delete(ALL)
				self.canvas.place(relx=0,rely=0,anchor=SE)
				self.zoom_state=0
			img.thumbnail((self.main_screen.winfo_width(),self.main_screen.winfo_height()))

			self.zoom_state=1
			self.screen_img=ImageTk.PhotoImage(img)

			self.image_label['image']=self.screen_img
			self.download_frame.place(relx=0,rely=0,anchor=SE)

			self.image_label.place(relx=0.5,rely=0.5,anchor=CENTER)
			

	def key_press_left(self,button):

		if self.current_image>0:
			self.current_image-=1
			self.update_screen()

	def key_press_right(self,button):
		if (self.current_image+1)<len(self.sd.all_files):
			self.current_image+=1
			self.update_screen()

	def key_press_space(self,button=None):
		if self.zoom_state==0:return
		
		if self.zoom_state==2:
			self.canvas.delete(ALL)
			self.canvas.place(relx=0,rely=0,anchor=SE)
			self.zoom_state=0
			self.update_screen()
			return
			
		file=self.sd.all_files[self.current_image].split('/')[-1]
		
		self.download_frame.place(relx=0.0,rely=0.0,anchor=SE)
		self.image_label.place(relx=0.0,rely=0.0,anchor=SE)	
		self.canvas.place(relx=0.5,rely=0.5,anchor=CENTER)
		img=Image.open(HOME_DIR+file.split('/')[-1])
		rotate,exf=self.orient(HOME_DIR+file.split('/')[-1])
		if rotate:img=img.rotate(rotate)
		self.big_img=ImageTk.PhotoImage(img)
		self.canvas.config(width=img.size[0], height=img.size[1])
		self.canvas.create_image(0,0,image=self.big_img,anchor=NW,tag='img')
		self.zoom_state=2
		
	def c_motion(self,event):
		if self.zoom_state<>2:return
		d_x,d_y=event.x-self.c_x,event.y-self.c_y
		
		self.canvas.move('img',d_x,d_y)
		self.c_x,self.c_y=event.x,event.y		
		
	def c_press(self,event):
		if self.zoom_state<>2:
			if self.zoom_state==1:
				self.key_press_space()
			return
		self.c_x,self.c_y=event.x,event.y

		
	def orient(self,fname):
		


		if not self.exiftoolflag:
			import exiftool
			self.tool=exiftool.ExifTool()
			self.tool.start()
			self.exiftoolflag=True

		if sys.platform=='win32':data=self.tool.get_metadata(HOME_DIR+fname .split('/')[-1].encode('mbcs'))
		else:data=self.tool.get_metadata(HOME_DIR+fname .split('/')[-1].encode('utf-8'))
		orient=int(data['EXIF:Orientation'])
		





			

		exf={}
		try:exf['iso']=data['EXIF:ISO']
		except:exf['iso']='???'
		
		try:exf['focal']=data['EXIF:FocalLength']
		except:exf['focal']='???'

		try:exf['f']=data['EXIF:FNumber']
		except:exf['f']='???'
			
		try:exf['s']=int(1.0/float(data['EXIF:ShutterSpeedValue']))/10*10
		except:exf['s']='???'			



		rotate=0
		if orient==8:
			rotate=90
		elif orient==6:
			rotate=270
		elif orient==3:
			rotate=180
		return rotate,exf


		

app=App()

def upd():
	root.update()
	root.after(100,upd)

if sys.platform=='darwin':root.after(100,upd)

root.mainloop()