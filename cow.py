# -*- coding: utf-8 -*-
"""
/***************************************************************************
 cow
                                 A QGIS plugin
 collar localizador
                              -------------------
        begin                : 2015-11-30
        git sha              : $Format:%H$
        copyright            : (C) 2015 by yo
        email                : yo
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from cow_dialog import cowDialog
import os.path, pycurl, cStringIO, time,datetime, random, sys, math
from math import radians, sin, cos, sqrt, asin

from qgis.gui import QgsMapTool
from qgis.core import QgsMapLayerRegistry,QgsFeature,QgsVectorLayer,QgsPoint,QgsGeometry, QgsFeatureRequest
class cow():
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'cow_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = cowDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Locator')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'cow')
        self.toolbar.setObjectName(u'cow')

        #connect the ui buttons to the methods
        self.dlg.pushButton.clicked.connect(self.on_1)
        self.dlg.pushButton_4.clicked.connect(self.on_2)
        self.dlg.pushButton_6.clicked.connect(self.on_3)
        self.dlg.pushButton_7.clicked.connect(self.track_1)
        self.dlg.pushButton_8.clicked.connect(self.close)
        self.dlg.button_box.accepted.connect(self.close)
        self.dlg.button_box.rejected.connect(self.close)
        self.dlg.pushButton_9.clicked.connect(self.drawLimits2)
        self.dlg.pushButton_10.clicked.connect(self.take)

        #create timer for the tracking method
        self.timer_1 = QTimer()

        #tool to manage mouse events
        self.tool = PointTool(iface.mapCanvas())

        #dialog always on top  and adujst size and position
        self.dlg.setWindowFlags(self.dlg. windowFlags() | Qt.WindowStaysOnTopHint)
        self.dlg.move(10,130)
        self.dlg.setFixedSize(690,220)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('cow', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/cow/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Collar localizador'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Locator'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):        
        """Run method that performs all the real work"""   
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    #repetitive tracking method
    def Time(self):
        #create list with number of IPs and take its values from de ui
        ips=[]
        ips.append(self.dlg.lineEdit.text())
        ips.append(self.dlg.lineEdit_2.text())
        ips.append(self.dlg.lineEdit_3.text())
        #ask for location
        for i in range(3):
            if ips[i][:3]=="192":
                self.actuate(i+1,ips[i],0)
            else:
                print "Direccion IP de collar %i incorrecta"%(i+1)


    #enable shock in IP nº1
    def on_1(self):
        option=1
        ip=self.dlg.lineEdit.text()
        self.actuate(option,ip,1)

    #enable shock in IP nº2
    def on_2(self):
       option=2
       ip=self.dlg.lineEdit_2.text()
       self.actuate(option,ip,1)

    #enable shock in IP nº3
    def on_3(self):
       option=3
       ip=self.dlg.lineEdit_3.text()
       self.actuate(option,ip,1)


    #tracking method asociated to button start tracking
    def track_1(self):
        self.timer_1.timeout.connect(self.Time)
        self.timer_1.start(5000)

    #Stop tracking method asociated to acept, cancel and stop trackig buttons
    def close (self):
        self.timer_1.stop()

    #method to take the points from map the canvas
    def take(self):
        self.iface.mapCanvas().setMapTool(self.tool)
        self.tool.polygon=[]

    #method to draw the limit points in a vector layer
    def drawLimits (self):
        self.dlg.listWidget.clear()
        #comprobate if the layer already exists and delete it
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "Limites":
                QgsMapLayerRegistry.instance().removeMapLayer( lyr.id() )
                break

        #crete a vector layer with a expecific name and color
        v_layer = QgsVectorLayer("LineString", "Limites", "memory")
        symbols =v_layer.rendererV2().symbols()
        symbol=symbols[0]
        symbol.setColor(QColor('magenta'))
        #create the provider and add the layer
        pr = v_layer.dataProvider()
        QgsMapLayerRegistry.instance().addMapLayers([v_layer])
        seg = QgsFeature()
        iterations=len(self.tool.polygon)
        #draw the lines between the buttons in order
        for i in range (iterations):
            if i== iterations-1:
                seg.setGeometry(QgsGeometry.fromPolyline([self.tool.polygon[i], self.tool.polygon[0]]))
            else:
                seg.setGeometry(QgsGeometry.fromPolyline([self.tool.polygon[i], self.tool.polygon[i+1]]))
            #add the lines to the provider and update the layer
            pr.addFeatures( [ seg ] )
            v_layer.updateExtents()
            v_layer.triggerRepaint()

        #add the points to the QlistWidget
        for i in range (len(self.tool.polygon)):
            self.addItem(i)


    def drawLimits2 (self):
        self.dlg.listWidget.clear()
        #comprobate if the layer already exists and delete it
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "Limites":
                QgsMapLayerRegistry.instance().removeMapLayer( lyr.id() )
                break

        #crete a vector layer with a expecific name and color
        v_layer = QgsVectorLayer("Polygon", "Limites", "memory")
        v_layer.setLayerTransparency(70)
        symbols =v_layer.rendererV2().symbols()
        symbol=symbols[0]
        symbol.setColor(QColor('green'))
        #create the provider and add the layer
        pr = v_layer.dataProvider()
        poly = QgsFeature()
        #draw the lines between the buttons in order
        points = self.tool.polygon
        #print points[0].x()
        poly.setGeometry(QgsGeometry.fromPolygon([self.tool.polygon]))
        #add the lines to the provider and update the layer
        pr.addFeatures([poly])
        v_layer.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayers([v_layer])

        #add the points to the QlistWidget
        for i in range (len(self.tool.polygon)):
            self.addItem(i)


    def pointInLimits(self,x,y):
        poly=[]
        for i in range(len(self.tool.polygon)):
            poly.append([self.tool.polygon[i].x(),self.tool.polygon[i].y()])
        n = len(poly)
        inside =False

        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside

    #method to add the items to the QlistWidget
    def addItem (self,i):
        item=QListWidgetItem()
        item.setText("Punto %i: "%(i+1)+ str(self.tool.polygon[i]))
        self.dlg.listWidget.addItem(item)


    #method to request the positcion and activate the shock
    def actuate(self,option,direction,onOff):
        # comprobate if the layers of each cow exist
        v_layer=None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if option==1:           
                if lyr.name() == "Vaca_1":
                    v_layer = lyr
                    break
            elif option==2:
                if lyr.name() == "Vaca_2":
                    v_layer = lyr
                    break
            elif option==3:
                if lyr.name() == "Vaca_3":
                    v_layer = lyr
                    break

        #create the layer with the name and the color
        if v_layer==None: 
            if option==1:
                v_layer = QgsVectorLayer("Point", "Vaca_1", "memory")
            elif option==2:
                v_layer = QgsVectorLayer("Point", "Vaca_2", "memory")
            elif option==3:
                v_layer = QgsVectorLayer("Point", "Vaca_3", "memory")
            symbols =v_layer.rendererV2().symbols()
            symbol=symbols[0]
            if option==1:
                symbol.setColor(QColor('red'))
            elif option==2:
                symbol.setColor(QColor('yellow'))
            elif option==3:
                symbol.setColor(QColor('cyan'))
  #          pr = v_layer.dataProvider()
  #          QgsMapLayerRegistry.instance().addMapLayers([v_layer])
  #          seg = QgsFeature()




        url=direction+'/hola='+str(onOff)


        #perform the request using pycurl
        try:
            buf = cStringIO.StringIO()            
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.CONNECTTIMEOUT, 3)
            c.setopt(pycurl.TIMEOUT, 3)
            c.setopt(pycurl.WRITEFUNCTION, buf.write)
            c.perform()
            texto=buf.getvalue()
            buf.close()
            self.dlg.label_4.setText("Conexion correcta")
            print "OK"

        except:
            texto= "Latitud: 91.0000000	Longitud: 181.0000000"
            print "Connection error"
            self.dlg.label_4.setText("Conexion incorrecta")

        #xtract the coordinates from the obtanied message
        Latitud=(texto[texto.find("Latitud: ")+9:texto.find("Longitud: ")-1])
        Longitud=(texto[texto.find("Longitud: ")+10:])

        if onOff==0:
            self.draw_position(Latitud,Longitud,v_layer,option)



    def draw_position(self,Latitud,Longitud,v_layer,option):

        #create the provider and add the layer
        pr = v_layer.dataProvider()
        QgsMapLayerRegistry.instance().addMapLayers([v_layer])
        seg = QgsFeature()

        #create the point and paint it
        try:
            point_A = QgsPoint((float(Longitud)-181-6.339908),(float(Latitud)-91+39.478360))
            seg.setGeometry(QgsGeometry.fromPoint(point_A))
            pr.addFeatures( [ seg ] )
            v_layer.updateExtents()
            v_layer.triggerRepaint()
            label=None
            if option==1:
                label=self.dlg.label_6
            elif option==2:
                label=self.dlg.label_7
            elif option==3:
                label=self.dlg.label_8
            if  self.pointInLimits(point_A.x(),point_A.y())==True:
                label.setText("IN")
                self.distances(point_A.x(),point_A.y(),option)

            else:
                label.setText("OUT")

            self.deletePoints(v_layer)
        except:
                pass

    def deletePoints(self,layer):
        request = QgsFeatureRequest().setFilterExpression(u'"DN"!=3')
        ids = []
        for f in layer.getFeatures(request):
            ids.append(f.id())
        if len(ids)>30:
            layer.startEditing()
            layer.deleteFeature(ids[0])
            layer.commitChanges()





    def lineMagnitude (self,x1, y1, x2, y2):
        lineMagnitude = math.sqrt(math.pow((x2 - x1), 2)+ math.pow((y2 - y1), 2))
        return lineMagnitude

    def haversine(self,lat1, lon1, lat2, lon2):

      R = 6372800 # Earth radius in kilometers

      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)

      a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
      c = 2*asin(sqrt(a))

      return R * c

    #Calc minimum distance from a point and a line segment (i.e. consecutive vertices in a polyline).
    def DistancePointLine (self,px, py, x1, y1, x2, y2):
        LineMag = self.lineMagnitude(x1, y1, x2, y2)

        if LineMag < 0.00000001:
            DistancePointLine = 9999
            return DistancePointLine

        u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
        u = u1 / (LineMag * LineMag)


        if (u < 0.00001) or (u > 1):
               #// closest point does not fall within the line segment, take the shorter distance
               #// to an endpoint
               ix = self.lineMagnitude(px, py, x1, y1)
               iy = self.lineMagnitude(px, py, x2, y2)
               if ix > iy:
                   DistancePointLine = self.haversine(py, px, y2, x2)
               else:
                   DistancePointLine = self.haversine(py, px, y1, x1)
        else:

            # Intersecting point is on the line, use the formula
            ix = x1 + u * (x2 - x1)
            iy = y1 + u * (y2 - y1)
            DistancePointLine = self.haversine(py, px, iy, ix)

        return DistancePointLine


    def distances(self,x,y,option):
        poly=[]
        for i in range(len(self.tool.polygon)):
            poly.append([self.tool.polygon[i].x(),self.tool.polygon[i].y()])
        n = len(poly)
        inside =False

        p1x,p1y = poly[0]
        maxIntensity=0
        intensity=0
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if i>0:
                distance=self.DistancePointLine(x,y,p1x,p1y,p2x,p2y)
                limit=self.dlg.spinBox.value()
                step=limit/9
                print "Distance with line: %i:"%(i)," %f meters" %(distance)
                if distance<=limit:
                    for i in range(9):
                        if distance>(step*i) and distance<(step*(i+1)):
                           intensity=((i+1)-10)*(-1)
                           print "Intenisdad: %i"%(intensity)
                           if intensity>maxIntensity:
                               maxIntensity=intensity
            p1x,p1y = p2x,p2y

        if maxIntensity>0:
            print "Intenisdad final: %i"%(maxIntensity)
            if option==1:
                ip= self.dlg.lineEdit.text()
            elif option==2:
                ip=self.dlg.lineEdit_2.text()
            elif option==3:
                ip=self.dlg.lineEdit_3.text()
            time.sleep(0.6)
            self.actuate(option,ip,maxIntensity)




class PointTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.polygon = []

    def canvasPressEvent(self, event):
        pass

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)


    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.polygon.append(point)


    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
