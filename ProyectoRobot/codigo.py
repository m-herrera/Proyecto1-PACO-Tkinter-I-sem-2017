from tkinter import *
from PIL import Image, ImageTk
import os
import time
from threading import Thread
import random
import winsound
from tkinter import messagebox

#define que se inició el programa y las alertas estan vigentes
global alerta
global primera_alerta
alerta = True
primera_alerta = True

#Crear ventana principal que tendrá toda la interfaz
#Y configuraciones de ventana
ventana_p = Tk()
ventana_p.resizable(width = False, height = False)  
ventana_p.geometry("600x605+0+0")   
ventana_p.title("P.A.C.O")  

#Crear contenedor principal, que tendrá la parte de animacion
contenedor_p = Canvas(ventana_p, height = "400", width = "600")
contenedor_p.pack()
color_text = contenedor_p.create_text(526,52, text = "color de fondo", font = ("Courier New", 12))
"""==================================================================================================="""

#esta funcion se ejecuta cuando se cambia el color de fondo
#tiene de restricciones los colores: black,green,red,yellow
#si no es una restriccion, hace un try para cambiar el color de fondo
#si el color no es valido, ejecuta except
def color_fondo():
    global posiciony
    color_f = color.get().lower()
    if color_f == "black":
        posiciony += 18
        shell_escribir.place(x=40,y= posiciony)
        shell["text"] = shell["text"] +"\"" + color_f + "\" es muy oscuro" + "\n♦♦♦ "
        shell.update()
    elif color_f == "green" or color_f == "yellow" or color_f == "red":
        posiciony += 18
        shell_escribir.place(x=40,y= posiciony)
        shell["text"] = shell["text"] +"\"" + color_f + "\" podria interferir con la bateria" + "\n♦♦♦ "
        shell.update()
    else:
        try:
            contenedor_p.config(bg = color_f)
            contenedor_p.update()
            guardar_estado()
        except:
            posiciony += 18
            shell_escribir.place(x=40,y= posiciony)
            shell["text"] = shell["text"] +"\"" + color_f + "\" no es un color valido" + "\n♦♦♦ "
            shell.update()    
    
    if posiciony >= 598:
        time.sleep(1)
        posiciony = 406
        shell_escribir.place(x=40,y= posiciony)
        shell["text"] = "♦♦♦ "
    return True

"""==================================================================================================="""

#aqui se crea el shell inicial
#se crea un shell que consta de una entrada de texto movil y una etiqueta que contiene texto
posiciony = 424
shell = Label(ventana_p,  height = "200", width = "600", text = "♦♦♦ Escribe \"help\" para obtener información \n♦♦♦ ", bg = "#FFFFFF", anchor = NW, justify = "left", font =("Courier New", 12))
shell.pack()
shell_escribir = Entry(ventana_p, width = "69", bd = 0, highlightthickness = 0, font = ("Courier New", 12))
shell_escribir.place(x=40,y=posiciony)
shell_escribir.focus_set() #hace que el cursor esté sobre la entrada de texto por default

"""==================================================================================================="""

#esta funcion recupera los datos del archivo de texto, para asi definir
#el estado inicial del robot. Los datos que se recuperan son: el nivel
#de la bateria, las coordenadas de posicion, el estado (vivo,muerto),
#la direccion (left,right) y el color de fondo. Estos valores se guardan
#en variables globales ya que se necesitan a lo largo de todo el codigo

def estado_inicio():
    global nivel_bateria
    global alive
    global right
    global coordenadax
    global coordenaday
    global bg_color
    
    archivo = open("robot.txt","r")
    #nivel de bateria
    archivo.seek(73)
    bateria = archivo.read(3)
    nivel_bateria = int(bateria)
    #estado
    archivo.seek(25)
    estado = archivo.read(1)
    alive = int(estado)
    #direccion
    archivo.seek(61)
    direccion = archivo.read(1) 
    right =int(direccion)
    #posicion eje x
    archivo.seek(34)
    posx = archivo.read(3)
    coordenadax = int(posx)
    #posicion eje y
    archivo.seek(45)
    posy = archivo.read(3)
    coordenaday = int(posy)
    #color de fondo
    archivo.seek(161)
    bg_color = archivo.readline()
    # revisa el nivel de bateria inicial
    bateria_revisar()
    archivo.close()
    
"""==================================================================================================="""

#esta función modifica el archivo de texto "robot.txt" el cual contiene los
#parametros de inicio del robot, en otras palabras, esta funcion guarda el
#estado del robot, y se llama, cada vez que se realiza un cambio.
def guardar_estado():
    archivo = open("robot.txt","w")
    archivo.seek(0)
    archivo.write("Nombre: P.A.C.O\n")
    archivo.write("Estado: "+str(int(alive))+ "\n")  
    if coordenadax < 100: 
        archivo.write("posx: 0"+str(coordenadax)+ "\n")
    else:
        archivo.write("posx: "+str(coordenadax)+ "\n")
    archivo.write("posy: "+str(coordenaday)+ "\n")
    archivo.write("Direccion: "+str(int(right))+ "\n")
    if nivel_bateria < 10:
        archivo.write("Bateria: 00"+str(nivel_bateria)+ "\n")
    elif nivel_bateria < 100:
        archivo.write("Bateria: 0"+str(nivel_bateria)+ "\n")
    else:
        archivo.write("Bateria: "+str(nivel_bateria)+ "\n")
    archivo.write("Fecha de creacion: 12/04/2017 \n")
    archivo.write("Imagen: ProyectoRobot\imagenes\Idle.png \n")
    archivo.write("Bg color:" + contenedor_p.cget("bg")) # guarda el color del canvas en ese momento
    archivo.close()

"""==================================================================================================="""

#esta funcion CREA una imagen mediante la libreria PIL (python imaging library), a partir
#del nombre de la imagen y el tamaño deseado. Además se encarga de crear la imagen segun
#la direccion necesaria, ya sea derecha o izquierda.
def crear_imagen(nombre,tamaño):
    ruta = os.path.join("imagenes/", nombre)
    imagen = Image.open(ruta)
    imagen.thumbnail((tamaño,tamaño))#define el tamaño de la imagen
    if right:
        imagen = imagen.transpose(Image.FLIP_LEFT_RIGHT) #gira la imagen si es necesario
    return imagen

"""==================================================================================================="""

#esta función se encarga de crear una imagen al llamar a la funcion "crear_imagen" y ademas
#la convierte a un formato aceptado por tkinter "PhotoImage", por ultimo le asigna una etiqueta
#que corresponde a las primeras 4 letras del nombre de la imagen.
#recibe 3 argumentos, el nombre de la imagen y las coordenadas en las que se va a crear.
#notese que al llamar a la funcion varias veces, la variable contenedor_p.imagenx se está
#redefiniendo y por lo tanto solo se muestra la ultima llamada de la funcion.
#Esto es muy util para crear animaciones.
def cargar_imagen(nombre,posx,posy):
    imagen1 = crear_imagen(nombre,300)
    contenedor_p.imagenx = ImageTk.PhotoImage(image = imagen1)#contenedor_p es para mantener restro
    tag = nombre[0:4]
    imagen = contenedor_p.create_image(posx,posy,image = contenedor_p.imagenx, tags = (tag))
    return imagen

"""==================================================================================================="""

#estas funciones se encargan de crear la forma de la bateria, la cual consta de
#varios rectangulos, pero al analizar los pares ordenados de los vertices se
#notó un patrón que permite realizar la recursividad aunque requiere de agregar
#muchas variables. En fin esta funcion crea la forma exterior de la bateria
def crear_bateria(posx1,posx2,posy1,posy2):
    borde_bateria = contenedor_p.create_rectangle(posx1,posy1,posx2,posy2)
    contenedor_p.create_line(crear_bateria_aux(posx1+10,posx2,posy1,posy2,[],True,True))

#parte recursiva de la funcion crear_bateria
def crear_bateria_aux(posx1,posx2,posy1,posy2,lista, flag1,flag2):
    if posx1 == posx2:
        return tuple(lista)
    elif flag1 and flag2:
        lista += [posx1,posy1]
        return crear_bateria_aux(posx1,posx2,posy1,posy2,lista,True,False)
    elif flag1 and not flag2:
        lista += [posx1,posy2]
        return crear_bateria_aux(posx1+10, posx2,posy1,posy2,lista,False,True)
    elif not flag1 and flag2:   
        lista += [posx1,posy2]
        return crear_bateria_aux(posx1,posx2,posy1,posy2,lista,False,False) 
    else:
        lista += [posx1,posy1]
        return crear_bateria_aux(posx1+10, posx2, posy1,posy2,lista,True,True)
    
"""==================================================================================================="""

#esta funcion se encarga de revisar el nivel de la bateria, se ejecuta cada vez que se usa
#un comando, cambia el color de la bateria dependiendo del nivel, muestra una alerta si se
#encuentra menor a 20 y pregunta si desea seguir recibiendo alertas, esto se hace con variables
#globales que funcionan de puertas, además esta funcion llama a la funcion vivo si la bateria
#es diferente de cero y el estado es muerto; de igual manera, si la bateria es igual a 0 y el
#estado es vivo se llama a la funcion muerto, estas dos funciones son animaciones del robot.
#por ultimo llama a la funcion guardar_estado para guardar todos los cambios.
def bateria_revisar():
    global color_bateria
    global alerta
    global primera_alerta
    global alive
    if nivel_bateria <= 20 and nivel_bateria > 0:
        color_bateria = "red"
        if alerta:
            messagebox.showwarning("Bateria Baja", "La bateria se esta descargando, se encuentra \na un " + str(nivel_bateria) +"% de su capacidad puedes modificarla \ncon el comando \"power(nivel numerico de energia)\" ")
            if primera_alerta:
                primera_alerta = False
                alerta = messagebox.askyesno("Bateria baja", "¿Desea seguir recibiendo notificaciones de \nbateria baja mientras esta sea menor a 20%? \nEsta configuracion se restaurara cuando el \nnivel de la bateria sea mayor al 20% de nuevo")

    elif nivel_bateria <= 50:
        alerta = True
        primera_alerta = True
        color_bateria = "yellow"
    else:
        alerta = True
        primera_alerta = True
        color_bateria = "green"
    if nivel_bateria == 0 and alive:
        muerto()
        alive = False
    elif nivel_bateria != 0 and not alive:
        vivo()
        alive = True
    guardar_estado()
    
"""==================================================================================================="""

#esta funcion se encarga de reproducir un sonido y habilitar la entrada de texto
def reproducir(nombre):
    winsound.PlaySound('sonido/'+nombre+".WAV", winsound.SND_FILENAME)
    shell_escribir.config(state=NORMAL)

"""==================================================================================================="""

#esta funcion reproduce un sonido con un saludo y el nombre del robot, ademas ejecuta
#un animacion de saludo. La primera parte se encarga de llamar a la funcion reproducir
#con un thread para asi permitir la reproduccion del sonido y la animacion de forma simultanea
#la animacion se ejecuta en la segunda parte de la función.
#ademas escribe el mensaje de saludo en el shell por lo tanto hay que modificar la posicion
#de la entrada de texto y analizar el caso en que esta se encuentre al final de la ventana.
def hello():
    hello_thread = Thread(target = reproducir, args = ("hola",))
    hello_thread.start()
    global posiciony
    posiciony += 18
    shell_escribir.config(state=DISABLED)
    shell["text"] = shell["text"] + "Hola, mi nombre es P.A.C.O" + "\n♦♦♦ "
    shell_escribir.place(x=40,y= posiciony)
    
    for x in range(3):
        cargar_imagen("dance1.png",coordenadax,coordenaday)
        contenedor_p.update()
        time.sleep(0.5)
        cargar_imagen("dance2.png",coordenadax,coordenaday)
        contenedor_p.update()
        time.sleep(0.5)
    cargar_imagen("Idle.png",coordenadax,coordenaday)
    contenedor_p.update()
    
    if posiciony >= 598:
        posiciony = 406
        shell_escribir.place(x=40,y= posiciony)
        shell["text"] = "♦♦♦ "

"""==================================================================================================="""

#esta funcion reproduce un sonido con la fecha de creacion del robot. Ademas
#la escribe en el shell por lo tanto hay que modificar la posicion de la entrada
#de texto y analizar el caso en que esta se encuentre al final de la ventana.
def built():
    built_thread = Thread(target = reproducir, args = ("built",))
    built_thread.start()
    global posiciony
    posiciony += 18
    shell_escribir.place(x=40,y= posiciony)
    shell["text"] = shell["text"] + "Fui creado el 11/04/2017" + "\n♦♦♦ "
    shell_escribir.config(state=DISABLED)
    contenedor_p.update()
    time.sleep(8.3)
    
    if posiciony >= 598:
        posiciony = 406
        shell_escribir.place(x=40,y= posiciony)
        shell["text"] = "♦♦♦ "

"""==================================================================================================="""

#esta funcion recibe un valor numérico y actualiza el nivel de energia del robot al valor recibido
#de amanera que actualiza tambien la animacion de la bateria y el texto sobre ella 
def power(porcentaje):
    contenedor_p.delete("bateria")
    return power_aux(10,210,15,30,porcentaje)

def power_aux(posx1,posx2,posy1,posy2,porcentaje):
    contenedor_p.create_text((posx1+posx2)//2,posy1-6,text = str(porcentaje)+"%", font = ("Courier New", 12), tags = ("bateria"))
    tamaño = int(posx2-(posx2-posx1)*(porcentaje/100))
    bateria_interna = contenedor_p.create_rectangle(tamaño,posy1,posx2,posy2, fill = color_bateria, tags = ("bateria"))
    contenedor_p.tag_lower("bateria") #pone la barra de color de bateria debajo las barras de bateria  

"""==================================================================================================="""

#esta función escribe en el "Shell" el nivel de energia actual del robot, por lo tanto
#actualiza la etiqueta y mueve la entrada de texto, por lo que debe verificar si esta
#se encuentra al final de la ventana.
def status():
    global posiciony
    posiciony += 18
    shell_escribir.place(x=40,y= posiciony)
    shell["text"] = shell["text"] + "Tengo " + str(nivel_bateria) + "% de bateria" + "\n♦♦♦ "
    shell.update()    
    if posiciony >= 598:
        posiciony = 406
        time.sleep(1.5)
        shell_escribir.place(x=40,y= posiciony)
        shell["text"] = "♦♦♦ "

"""==================================================================================================="""

#esta función crea una animacion de el robot caminando hacia adelante, basicamente
#al llamar a la funcion cargar_imagen con distintas imagenes en distintas posiciones
#ademas se deshabilita la entrada de texto mientras se ejecuta la animacion, para evitar
#la interrupción de la acción, además se disminuye el valor del nivel de bateria.
def goahead():
    shell_escribir.config(state=DISABLED)
    contenedor_p.delete("Idle")
    global nivel_bateria
    nivel_bateria -= 1
    power(nivel_bateria)
    if right:
        return goahead_aux(1,False, coordenadax, coordenaday,-10,10,590)
    else:
        return goahead_aux(1,False, coordenadax, coordenaday,10,590,10)
    
def goahead_aux(x,flag, coordx,coordy,direccion,limite_r,limite_l):
    global coordenadax
    global coordenaday
    if coordx == limite_r:
        goahead_aux(1,flag,limite_l, coordy,direccion,limite_r,limite_l)
    elif x == 5 and flag:
        cargar_imagen("Idle.png",coordx,coordy)
        contenedor_p.update()
        coordenadax = coordx
        coordenaday = coordy
        shell_escribir.config(state=NORMAL)
        return None
    elif x == 9:
        flag = True
        return goahead_aux(1,flag,coordx,coordy,direccion,limite_r,limite_l)
    else:
        y = str(x)
        contenedor_p.delete("Run"+ y)
        coordx +=direccion
        cargar_imagen("Run" + y + ".png",coordx,coordy)
        contenedor_p.update()
        time.sleep(0.05)
        return goahead_aux(x+1,flag,coordx,coordy,direccion,limite_r,limite_l)

"""==================================================================================================="""

#esta función crea una animacion de el robot caminando hacia atras. Esta funcion es muy similar
#a la funcion goahead solo que la posicion y las imagenes se recorren en sentido contrario.
#de igual forma se deshabilita la entrada de texto y se disminuye el nivel de bateria.
def goback():
    shell_escribir.config(state=DISABLED)
    contenedor_p.delete("Idle")
    global nivel_bateria
    nivel_bateria -= 1
    power(nivel_bateria)
    if right:
        return goback_aux(8,False, coordenadax,coordenaday,-10,590,10)
    else:
        return goback_aux(8,False, coordenadax,coordenaday,10,10,590)
    
def goback_aux(x,flag, coordx,coordy,direccion,limite_r,limite_l):
    global coordenadax
    global coordenaday
    if coordx == limite_r:
        goback_aux(8,flag,limite_l, coordy,direccion,limite_r,limite_l)
    elif x == 4 and flag:
        cargar_imagen("Idle.png",coordx,coordy)
        contenedor_p.update()
        coordenadax = coordx
        coordenaday = coordy
        shell_escribir.config(state=NORMAL)
        return None
    elif x == 0:
        flag = True
        return goback_aux(8,flag,coordx, coordy,direccion,limite_r,limite_l)
    else:
        y = str(x)
        contenedor_p.delete("Run"+ y)
        coordx -=direccion
        cargar_imagen("Run" + y + ".png",coordx,coordy)
        contenedor_p.update()
        time.sleep(0.05)
        return goback_aux(x-1,flag,coordx,coordy,direccion,limite_r,limite_l)
    
"""==================================================================================================="""

#esta funcion cambia el valor de la direccion del robot y luego carga la imagen lo cual
#produce que se cambie de direccion, y reduce en uno el nivel de energia del robot. Si
#el robot ya se encontraba en esta direccion, el cambio no se nota, y la energía no se afecta.
def right():
    global nivel_bateria
    global right
    if right:
        nivel_bateria -= 1
    right = False
    power(nivel_bateria)
    cargar_imagen("Idle.png",coordenadax,coordenaday)

"""==================================================================================================="""

#esta es la funcion opueta a la funcion right por lo tanto se comporta igual
#esta funcion cambia el valor de la direccion del robot y luego carga la imagen lo cual
#produce que se cambie de direccion, y reduce en uno el nivel de energia del robot. Si
#el robot ya se encontraba en esta direccion, el cambio no se nota, y la energía no se afecta.
def left():
    global nivel_bateria
    global right
    if not right:
        nivel_bateria -= 1
    right = True
    power(nivel_bateria)
    cargar_imagen("Idle.png",coordenadax,coordenaday)

"""==================================================================================================="""

#esta funcion cambia aleatoriamente un conjunto de imagenes produciendo el efecto de un baile
#funciona basicamente igual que las demas animaciones, al cargar una diferente imagen, pero en
#este caso no se cambia la posicion, tambien se altera el nivel de bateria del robot, además
#alterna la direccion de las imagenes (derecha,izquierda) para mejorar el efecto, al igual que
#en las demás animaciones, se deshabilita la entrada de texto mientras  se ejecuta
def dance():
    shell_escribir.config(state=DISABLED)
    global nivel_bateria
    nivel_bateria -= 2
    power(nivel_bateria)
    i = random.randrange(1,5) #valor aleatorio
    return dance_aux(i,1,coordenadax,coordenaday)

def dance_aux(i,fin,coordx,coordy):
    global right
    if fin == 15:
        cargar_imagen("Idle.png",coordx,coordy)
        time.sleep(0.4)
        contenedor_p.update()
        shell_escribir.config(state=NORMAL)
        return None
    elif i == 5:
        cargar_imagen("Idle.png",coordx,coordy)
        time.sleep(0.4)
        contenedor_p.update()
        return dance_aux(1,fin+1,coordx,coordy)
    else:
        coordenadas = contenedor_p.coords("Idle")
        cargar_imagen("dance"+str(i)+".png",coordx,coordy)
        time.sleep(0.4)
        contenedor_p.update()
        right = not right
        i = random.randrange(1,5)
        return dance_aux(i,fin+1,coordx,coordy)

"""==================================================================================================="""

#esta funcion reproduce musica de manera permanente pero sin intervenir con las demas acciones
#del robot ya que el argumento winsound.SND_ASYNC produce el efecto de un thread, ya que no
#espera que el sonido termine, sino que ejecuta la siguiente linea de codigo. Y el argumento
#winsound.SND_LOOP lo reproduce indefinidamente. Tamabien se afecta el nivel de energía, y se
#escribe el nombre de la canción en el shell, por lo tanto se necesita mover la entrada de
#texto y analizar si esta se encuentra al final de la ventana.
#cabe destacar que la reproduccion de otros archivos de sonido como "hello" o "built" tienen
#prioridad sobre esta funcion, por lo tanto si se ejecuta "music_on" y posteriormente una
#de las funciones mencionadas, la musica se detendrá y se reproducirá el otro sonido.
def music_on():
    global nivel_bateria
    global posiciony
    posiciony += 18
    nivel_bateria -=1
    power(nivel_bateria)
    shell_escribir.place(x=40,y= posiciony)
    shell["text"] = shell["text"] + "Ahora suena \"High\". No copyright sounds" + "\n♦♦♦ "
    shell.update()
    if posiciony >= 598:
        time.sleep(1)
        posiciony = 406
        shell_escribir.place(x=40,y= posiciony)
        shell["text"] = "♦♦♦ "
    winsound.PlaySound("sonido/High.WAV", winsound.SND_ASYNC|winsound.SND_LOOP)

"""==================================================================================================="""

#esta funcion detiene la reproduccion de cualquier sonido que se esté ejecutando en ese momento
#en este caso detiene la reproduccion de la musica
def music_off():
    winsound.PlaySound(None, winsound.SND_ASYNC)

"""==================================================================================================="""

#esta funcion simplemente cambia la imagen existente por una similar pero el robot
#muestra los dientes, esto sucede por unos segundos, y la entrada de texto se deshabilita
#en ese lapso.

def smile():
    shell_escribir.config(state=DISABLED)
    cargar_imagen("Smile.png",coordenadax,coordenaday)
    contenedor_p.update()
    time.sleep(3)
    cargar_imagen("Idle.png",coordenadax,coordenaday)
    shell_escribir.config(state=NORMAL)
    contenedor_p.update()

"""==================================================================================================="""

#esta funcion produce el efecto de que el robot está llorando, primero se cambia la imagen por una
#del robot triste, y posteriormente se crean 2 imagenes de gotas, y se colocan en la posicion de
#los ojos, estas posiciones varian dependiendo de la direccion en la que se encuentre el robot;
#luego con recursividad, se cambian las coordenadas de cada una de las gotas poco a poco hasta que
#lleguen al suelo, esto se logra con el metodo coords() y actualizando el contenedor.
#las gotas no se pueden crear con la funcion cargar_imagen ya que remplazarian la imagen existente
def cry():
    global nivel_bateria
    shell_escribir.config(state=DISABLED)
    nivel_bateria -= 1
    power(nivel_bateria)
    lagrima = crear_imagen("lagrima.png",35)    
    if not right:
        cargar_imagen("dead1.png",coordenadax+50,coordenaday+10)
        contenedor_p.imagen1 = ImageTk.PhotoImage(image = lagrima)
        cry1 = contenedor_p.create_image(coordenadax+30,coordenaday,image = contenedor_p.imagen1, tags = ("cry1"))
        contenedor_p.imagen2 = ImageTk.PhotoImage(image = lagrima)
        cry2 = contenedor_p.create_image(coordenadax-20,coordenaday-15,image = contenedor_p.imagen2, tags = ("cry2"))
        contenedor_p.update()
        time.sleep(0.5)
        cry_aux(coordenadax+30,coordenaday,coordenadax-20,coordenaday-15)
    else:
        cargar_imagen("dead1.png",coordenadax-50,coordenaday+10)
        contenedor_p.imagen1 = ImageTk.PhotoImage(image = lagrima)
        cry1 = contenedor_p.create_image(coordenadax+20,coordenaday-15,image = contenedor_p.imagen1, tags = ("cry1"))
        contenedor_p.imagen2 = ImageTk.PhotoImage(image = lagrima)
        cry2 = contenedor_p.create_image(coordenadax-40,coordenaday,image = contenedor_p.imagen2, tags = ("cry2"))
        contenedor_p.update()
        time.sleep(0.5)
        cry_aux(coordenadax+20,coordenaday-15,coordenadax-40,coordenaday)
    time.sleep(0.15)
    cargar_imagen("Idle.png",coordenadax,coordenaday)

#parte recursiva de la funcion "cry"
def cry_aux(lagrima1x,lagrima1y,lagrima2x,lagrima2y):
    if lagrima1y == 390:
        contenedor_p.delete("cry1")
        contenedor_p.update()
        shell_escribir.config(state = NORMAL)
        return None
    elif lagrima2y == 390:
        contenedor_p.delete("cry2")
        contenedor_p.coords("cry1",lagrima1x, lagrima1y+5)
        time.sleep(0.025)
        contenedor_p.update()
        return cry_aux(lagrima1x, lagrima1y+5,lagrima2x,lagrima2y)
    elif lagrima2y >= 270:
        contenedor_p.coords("cry1",lagrima1x, lagrima1y)
        contenedor_p.coords("cry2",lagrima2x, lagrima2y)
        time.sleep(0.025)
        contenedor_p.update()
        return cry_aux(lagrima1x,lagrima1y+5,lagrima2x,lagrima2y+5)
    else:
        contenedor_p.coords("cry2",lagrima2x, lagrima2y)
        time.sleep(0.025)
        contenedor_p.update()
        return cry_aux(lagrima1x,lagrima1y,lagrima2x,lagrima2y+5)
    
"""==================================================================================================="""

#esta funcion produce le efecto de que el robot está disparando, la funcion se comporta similar
#a la funcion "cry" pero cambia la coordenada "x" y no la coordenada "y", primero se cambia la
#imagen del robot por una con el brazo extendido, luego se crea una imagen de una bala en la
#posicion del brazo y luego su mueve con el metodo coords() hasta el final de la ventana y ahi
#desaparece, notese que todas las coordenadas y posiciones dependen de la direccion del robot
#y se debe tomar en cuenta, tambien se disminuye el nivel de la bateria.
def shoot():
    global nivel_bateria
    nivel_bateria -= 2
    power(nivel_bateria)
    shell_escribir.config(state = DISABLED)
    cargar_imagen("shoot.png",coordenadax,coordenaday)
    contenedor_p.update()
    bala = crear_imagen("Bullet.png",40)
    if not right:
        contenedor_p.bala1 = ImageTk.PhotoImage(image = bala)
        contenedor_p.create_image(coordenadax+100,coordenaday+20, image = contenedor_p.bala1, tags = ("bala"))
        contenedor_p.update()
        time.sleep(0.02)
        shoot_aux(coordenadax+100,coordenaday+20,5)
    else:
        contenedor_p.bala2 = ImageTk.PhotoImage(image = bala)
        contenedor_p.create_image(coordenadax-100,coordenaday+20, image = contenedor_p.bala2, tags = ("bala"))
        contenedor_p.update()
        time.sleep(0.02)
        shoot_aux(coordenadax-100,coordenaday+20,-5)
    time.sleep(0.1)
    cargar_imagen("Idle.png",coordenadax,coordenaday)
#parte recursiva de la funcion "shoot" que mueve la bala
def shoot_aux(posx,posy,avanzar):
    if posx <= 0 or posx >= 600:
        contenedor_p.delete("bala")
        contenedor_p.update()
        time.sleep(0.02)
        shell_escribir.config(state = NORMAL)
        return None
    else:
        contenedor_p.coords("bala",posx+5,posy)
        contenedor_p.update()
        time.sleep(0.02)
        return shoot_aux(posx+avanzar,posy,avanzar)

"""==================================================================================================="""

#esta funcion produce el efecto de que el robot está volando. Para ello se cambia la imagen
#por una con la mano levantada y luego se mueve esta imagen hacia arriba hasta alcanzar una
#posicion definida, luego se carga una imagen rotada (dependiendo de la direccion del robot)
#y luego se mueve en el eje x (dependiendo de la direccion del robot) hasta que se vuelve
#a alcanzar la posicion definida, posteriormente se carga la imagen sin rotar y se mueve
#hacia abajo hasta la posicion inicial y luego se carga la imagen original del robot.
#tambien se modifica el nivel de energia del robot y se deshabilita la entrada de texto. 
def fly():
    global nivel_bateria
    shell_escribir.config(state=DISABLED)
    nivel_bateria -= 2
    power(nivel_bateria)
    contenedor_p.delete("Idle")
    fly = crear_imagen("dance4.png",300)
    if not right:
        fly_rotate = fly.transpose(Image.ROTATE_270)
        direccion = 10
        limite_r = 590
        limite_l = 10
    else:
        fly_rotate = fly.transpose(Image.ROTATE_90)
        direccion = -10
        limite_r = 10
        limite_l = 590
    contenedor_p.fly1 = ImageTk.PhotoImage(image = fly)
    fly1 = contenedor_p.create_image(coordenadax,coordenaday,image = contenedor_p.fly1, tags = ("fly1"))
    fly_aux(coordenadax,coordenaday,-5,direccion,limite_r,limite_l,fly_rotate)

#parte recursiva de la funcion fly, que produce el movimiento en el eje "y"
def fly_aux(posx,posy,arriba,direccion,limite_r,limite_l,fly_rotate):
    if arriba == -5:
        if posy ==200:
            contenedor_p.delete("fly1")
            contenedor_p.fly1_rotate = ImageTk.PhotoImage(image = fly_rotate)
            posy = 240
            fly1_rotate = contenedor_p.create_image(posx,posy,image = contenedor_p.fly1_rotate, tags = ("fly1_r"))
            posx += direccion
            contenedor_p.update()
            fly_aux2(posx,posy,fly_rotate,direccion,limite_r,limite_l)
        else:
            contenedor_p.coords("fly1",posx,posy)
            time.sleep(0.15)
            contenedor_p.update()
            return fly_aux(posx,posy+arriba,arriba,direccion,limite_r,limite_l,fly_rotate)
    else:
        if posy ==coordenaday:
            contenedor_p.delete("danc")
            cargar_imagen("Idle.png",coordenadax,coordenaday)
            return None
        else:
            contenedor_p.coords("danc",posx,posy)
            time.sleep(0.15)
            contenedor_p.update()
            return fly_aux(posx,posy+arriba,arriba,direccion,limite_r,limite_l,fly_rotate)
  
#parte recursiva de la funcion fly, que produce el movimiento en el eje "x"
def fly_aux2(posx,posy,fly_rotate,direccion,limite_r,limite_l):
    if posx == coordenadax:
        contenedor_p.delete("fly1_r")
        cargar_imagen("dance4.png",posx,posy-40)
        contenedor_p.update()
        shell_escribir.config(state=NORMAL)
        fly_aux(posx,posy,5,direccion,limite_r,limite_l,fly_rotate)
        return None
    elif posx == limite_r:
        posx = limite_l
        return fly_aux2(posx,posy,fly_rotate,direccion,limite_r,limite_l)
    else:
        contenedor_p.coords("fly1_r",posx,posy)
        time.sleep(0.05)
        contenedor_p.update()
        return fly_aux2(posx+direccion,posy,fly_rotate,direccion,limite_r,limite_l)

"""==================================================================================================="""

#esta funcion crea una nueva ventana la cual contiene informacion de ayuda sobre el proyecto
#como el texto es muy grande, se decidió guardarlo en un archivo de texto aparte, por lo tanto
#esta funcion debe abrirlo y luego crear un texto en el contenedor con el contenido del archivo
#tambien se crea una "scrollbar" para recorreer el texto.
def help1():
    ventana_help = Toplevel()
    ventana_help.geometry("610x605+600+0")
    ventana_help.resizable(width = False, height = False) 
    ventana_help.title("Help")
    contenedor_help = Canvas(ventana_help,bg = "black", scrollregion=(0,0,610,1900))#area que se puede recorrer
    contenedor_help.pack(expand = TRUE, fill = BOTH)
    texto_help = open("help.txt","r")
    texto_help.seek(0)
    texto = contenedor_help.create_text(305,950, text = texto_help.read() ,fill = "white", justify = LEFT,font =("Courier New", 11))
    barra = Scrollbar(contenedor_help, orient = VERTICAL)
    barra.pack(side=RIGHT,fill=Y)
    barra.config(command = contenedor_help.yview)
    contenedor_help.config(yscrollcommand=barra.set)
    texto_help.close()
    
"""==================================================================================================="""

#esta funcion destruye la ventana principal y cierra el "shell" de python
def exit1():
    ventana_p.destroy()
    exit()
    
"""==================================================================================================="""

#esta funcion ejecuta una animacion del robot muriendo, al cambiar
#una serie de imagenes especificas, sin alterar su posicion.
def muerto():
    time.sleep(0.3)
    shell_escribir.config(state=DISABLED)
    contenedor_p.delete("Idle")
    return muerto_aux(1,coordenadax,coordenaday)

#parte recursiva de la funcion "muerto"
def muerto_aux(x,coordx,coordy):
    if x==5:
        shell_escribir.config(state=NORMAL)
        return None
    else:
        y = str(x)
        cargar_imagen("Dead" + y + ".png",coordx,coordy)
        contenedor_p.update()
        time.sleep(0.3)
        return muerto_aux(x+1,coordx,coordy)

"""==================================================================================================="""

#esta funcion ejecuta una animacion del robot reviviendo, al cambiar
#una serie de imagenes específicas, sin alterar su posicion
def vivo():
    time.sleep(0.2)
    shell_escribir.config(state=DISABLED)
    contenedor_p.delete("Dead")
    return vivo_aux(4,coordenadax,coordenaday)

#parte recursiva de la funcion "vivo"
def vivo_aux(x,coordx,coordy):
    if x==0:
        shell_escribir.config(state=NORMAL)
        cargar_imagen("Idle.png",coordx,coordy)
        return None
    else:
        y = str(x)
        cargar_imagen("Dead" + y + ".png",coordx,coordy)
        contenedor_p.update()
        time.sleep(0.2)
        return vivo_aux(x-1,coordx,coordy)

"""==================================================================================================="""

#este diccionario relaciona una palabra con su respectiva funcion, y contiene todos
#los comandos permitidos por el robot.
validacion_de_comandos = ({"hello":hello, "built":built, "power":power,
                           "status":status, "goahead":goahead, "goback":goback,
                           "right":right, "left":left, "dance":dance,
                           "music-on":music_on, "music-off":music_off, "smile":smile,
                           "cry":cry, "own1":shoot, "shoot":shoot, "own2":fly,
                           "fly":fly, "help": help1, "exit" : exit1 })

"""==================================================================================================="""

#esta funcion se explica extensamente pues es la mas importante y un poco confusa
#esta funcion es la encargada de obtener los comandos del shell y ejecutar las
#funciones respectivas, por lo tanto tambien es la encargada de llevar a cabo
#la mayoria de validaciones. Tine un event como argumento ya que se ejecuta al
#presionar la tecla <RETURN>. Al ejecutarse, la PRIMERA PARTE revisa la posicion
#de la entrada de texto y si esta se encuentra al final se reinicia el shell, sino
#se mueve una fila hacia abajo. La SEGUNDA PARTE cambia todos los parentesis de
#la entrada de texto por Asteriscos, de manera que si no hay ninguno no pasa nada,
#pero en el caso del comando power(n) se obtendría power*n*, luego se crean tres
#textos con los elementos separados por los asteriscos, mediante el metodo split
#ejemplo power*n*: texto1 = power, texto2 = n, texto3 = ''. Luego se hace una
#validacion del commando power(n) ya que para que este sea valido text3 = '', y
#texto2 debe estar entre 0 y 100, si se cumple se ejecuta power, ademas verifica
#que el texto1 esté en los comados validos si no hay parentesis como es el caso
#de los demas comandos, el try se cae al intentar ejecutar el segundo split y se
#va al caso except donde inicia la TERCERA PARTE e intenta otro conjunto de comandos
#se sabe que si el texto es power se debe ejecutar el primer try así que si ahora el
#texto es power, este no es un comando valido, por ejemplo power() da este caso, y se
#indica que no es un comando valido. si no se trata de power entonces se revisa en el
#diccionario si se logra, se analiza la bateria para ver si se puede ejecutar el
#commando y se llama a la funcion ejecutar_shell, gran parte de esto es validar cuales
#comandos se pueden hacer segun el nivel de bateria, sino indica que no tiene bateria
#si el comando no está en el diccionario el try se cae y el except dice que el
#commando no es valido, por ultimo se verifica si la entrada de texto se encuentra al
#final de la ventana y se mueve al inicio

def actualizar_shell(event):
    #se cambia a minuscula
    texto = shell_escribir.get().lower()
    #primera parte
    global posiciony
    if posiciony >= 580:
        posiciony = 424
        shell["text"] = "♦♦♦ "
    else:
        posiciony += 18
    shell_escribir.place(x=40,y= posiciony)
    shell_escribir.delete("0", "end")
    #segunda parte
    try:
        texto0 = texto.replace(")","*").replace("(","*")
        texto1 = texto0.split("*")[0]
        texto2 = int(texto0.split("*")[1])
        texto3 = texto0.split("*")[2:]
        
        if texto3 == [''] and texto2>=0 and texto2<=100:
            validacion_de_comandos[texto1]
            shell["text"] = shell["text"] + texto + "\n" + "♦♦♦ "
            global nivel_bateria
            nivel_bateria = texto2
            bateria_revisar()
            power(nivel_bateria)    
        else:
            posiciony += 18
            shell_escribir.place(x=40,y= posiciony) 
            shell["text"] = shell["text"] + "\"" + texto + "\" " +"No es un comando valido\n" + "♦♦♦ Escribe \"help\" para mas informacion\n" + "♦♦♦ "     
    #tercera parte
    except:
        try:
            if texto == "power":
                posiciony += 18
                shell_escribir.place(x=40,y= posiciony)
                shell["text"] = shell["text"] + "\"" + texto + "\" " +"No es un comando valido\n" + "♦♦♦ Escribe \"help\" para mas informacion\n" + "♦♦♦ "     
            else:
                validacion_de_comandos[texto]
                if nivel_bateria ==1 and (texto == "dance" or texto  == "fly" or texto == "shoot"):
                    shell["text"] = shell["text"] + "no se puede ejecutar"+ " \"" + texto + "\", " + "no hay bateria suficiente" + "\n" + "♦♦♦ "
                    
                elif nivel_bateria > 0 or texto == "exit" or texto == "help" or texto == "status":
                    shell["text"] = shell["text"] + texto + "\n" + "♦♦♦ "
                    ejecutar_shell(validacion_de_comandos[texto])
                else:
                    shell["text"] = shell["text"] + "no se puede ejecutar"+ " \"" + texto + "\", " + "no hay bateria" + "\n" + "♦♦♦ " 
        except:
            posiciony += 18
            shell_escribir.place(x=40,y= posiciony)
            shell["text"] = shell["text"] + "\"" + texto + "\" " +"No es un comando valido\n" + "♦♦♦ Escribe \"help\" para mas informacion\n" + "♦♦♦ "
            
    if posiciony >= 598:
        shell.update()
        time.sleep(1)
        posiciony = 406
        shell_escribir.place(x=40,y= posiciony)
        shell["text"] = "♦♦♦ "

ventana_p.bind("<Return>", actualizar_shell)
"""==================================================================================================="""

#esta funcion ejecuta las funciones del diccionario de funciones validas
#y luego revisa la bateria  y por ende guarda el estado del robot en el
#archivo de texto, esto cada vez que se ejecute un comando.
def ejecutar_shell(comando):
    comando()
    bateria_revisar()
        
"""==================================================================================================="""

#esta funcion se ejecuta con el boton REINICIAR y basicamente vuelve todo al estado
#predefinido del robot, posicion, bateria, estado, direccion...
def default():
    global alive
    global coordenadax
    global coordenaday
    global right
    global nivel_bateria
    global posiciony
    alive = True
    coordenadax = 300
    coordenaday = 260
    right = True
    nivel_bateria = 100
    bateria_revisar()
    power(nivel_bateria)
    iniciar()
    bateria = crear_bateria(10,210,15,30)
    posiciony = 424
    shell_escribir.place(x=40, y = posiciony)
    shell["text"] = "♦♦♦ Escribe \"help\" para obtener información \n♦♦♦ "
    shell_escribir.delete("0", "end")
    color.delete(0,END)
    color.insert(0, "silver")
    color_fondo()
    contenedor_p.update()
    music_off()
    guardar_estado()
        
"""==================================================================================================="""

#esta funcion llama al estado_inicio y luego carga en la ventana la configuracion
#anterior del robot, bateria, color fondo, estado. Se ejecuta cada vez que se
#inicia el programa
def iniciar():
    estado_inicio()
    if alive:
        cargar_imagen("Idle.png",coordenadax,coordenaday)
    else:
        cargar_imagen("Dead4.png",coordenadax,coordenaday)
    crear_bateria(10,210,15,30)
    power(nivel_bateria)
    color.insert(0,bg_color)
    color_fondo()

"""==================================================================================================="""

#se define el boton de REINICIAR y la entrada de texto para el color, la cual se
#valida al tener "focusout" y se valida mediante la funcion color_fondo
reiniciar = Button(contenedor_p,text = "REINICIAR", command = default,font = ("Courier New", 12), bg = "black", fg = "white", relief = RAISED)
reiniciar.place(x = 475,y = 10)
color = Entry(contenedor_p,width = 10,justify = CENTER,font = ("Courier New", 12),validate = "focusout", validatecommand = color_fondo)
color.place(x=485,y = 60)

contenedor_p.refresh = ImageTk.PhotoImage(image = crear_imagen("refresh.png",17))
refresh = Button(contenedor_p,image = contenedor_p.refresh,command = color_fondo)
refresh.place(x=460,y=60)
#se ejecuta la funcion iniciar
iniciar()

#se cierra el mainloop
ventana_p.mainloop()



