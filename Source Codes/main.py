'''
PROJECT TITLE: Paninda Pro: A Sari-Sari Store Inventory Management System

AUTHOR: 
Gabriel A. Vargas
Bachelor of Science in Computer Engineering
School of Electrical, Electronics, and Computer Engineering
Mapua University

DATE: May 5, 2023 [Version 1.0.3]

PROJECT DESCRIPTION:
Paninda Pro is a streamlined Inventory Management System (IMS) designed to assist small 
enterprises, such as sari-sari stores, in effectively managing their inventories. With a 
user-friendly dashboard, comprehensive inventory management features, and a flexible account 
management system, Paninda Pro offers a powerful solution for optimizing inventory operations. 
Developed using Python, Paninda Pro combines the visual prowess of Qt Designer and the 
customization capabilities of Qt Style Sheet (QSS) to deliver a professional and intuitive 
frontend interface. The backend leverages SQL and Python, ensuring reliable data storage, 
retrieval, and seamless integration of data management processes.

'''

import sys
import sqlite3
import os
import os.path
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QMessageBox, QLineEdit, QTableWidgetItem, QStyledItemDelegate
from PyQt5.QtCore import QTextStream, QFile, pyqtSlot, Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QPainter, QRegion, QStandardItemModel, QStandardItem
from PyQt5.QtSql import QSqlQuery
from PyQt5 import QtCore, QtGui, QtWidgets

from paninda_pro_ui import Ui_MainWindow

# connection to sqlite3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "paninda_pro.db")
db_connect = sqlite3.connect(db_path)
cursor = db_connect.cursor()

class MainWindow(QMainWindow):

    def __init__(self): 
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # initializing window to login
        self.ui.stackedWidget_main.setCurrentIndex(0)
        self.ui.lineEdit_username.setFocus()
        self.ui.pushButton_incorrect.hide()
        self.ui.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.setTabOrder(self.ui.lineEdit_username, self.ui.lineEdit_password)

        # connecting the login button to the validate_account() 
        self.ui.pushButton_login.clicked.connect(self.validate_account)

        # connecting to the logout dialog
        self.ui.pushButton_icon_logout.clicked.connect(self.showLogoutConfirmation)
        self.ui.pushButton_full_logout.clicked.connect(self.showLogoutConfirmation)

        # set shadow design of window
        self.ui.page_menu.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0))
        self.ui.widget_login_bg.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=30, xOffset=0, yOffset=0))
        self.ui.widget_login_space.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=0))

        # set shadow design of page contents
        self.ui.widget_dashboard_header.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=8, xOffset=0, yOffset=0))
        self.ui.widget_dashboard_content_1.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=8, xOffset=0, yOffset=0))
        self.ui.widget_dashboard_content_2.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=8, xOffset=0, yOffset=0))
        self.ui.widget_dashboard_content_3.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=8, xOffset=0, yOffset=0))

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(1200, 900)

        self.show()
        
        # hide the report button because it is not used
        self.ui.pushButton_full_report.hide()
        self.ui.pushButton_icon_report.hide()

        ### CONNECT TO MOUSE for dragging window
        # connecting the signals to the slots for dragging the window - title bar
        self.ui.widget_title.mousePressEvent = self.mouse_press_event
        self.ui.widget_title.mouseMoveEvent = self.mouse_move_event
        self.ui.widget_title.mouseReleaseEvent = self.mouse_release_event
        
        # connecting the signals to the slots for dragging the window - login
        self.ui.widget_login_bg.mousePressEvent = self.mouse_press_event
        self.ui.widget_login_bg.mouseMoveEvent = self.mouse_move_event
        self.ui.widget_login_bg.mouseReleaseEvent = self.mouse_release_event
        

        # initialize variables for dragging  window
        self.dragging = False
        self.offset = QPoint(0, 0)


        ### CONNECT BUTTONS TO EVENTS
        # connecting the min and close buttons to their slot functions
        self.ui.pushButton_minimize.clicked.connect(self.minimize_win)
        self.ui.pushButton_close.clicked.connect(self.close_win)

        # connecting the icon and full menu buttons to uncheck functions
        self.ui.pushButton_icon_menu.clicked.connect(self.uncheck_pushButton_full_menu)
        self.ui.pushButton_full_menu.clicked.connect(self.uncheck_pushButton_icon_menu)

        self.ui.pushButton_full_menu.clicked.connect(self.show_full_dashboard)
        self.ui.pushButton_icon_menu.clicked.connect(self.show_cropped_dashboard)

        '''
        # connecting the login and logout buttons to their uncheck functions
        self.ui.pushButton_login.clicked.connect(self.uncheck_pushButton_icon_logout)
        self.ui.pushButton_login.clicked.connect(self.uncheck_pushButton_full_logout)
        self.ui.pushButton_icon_logout.clicked.connect(self.uncheck_pushButton_login)
        self.ui.pushButton_full_logout.clicked.connect(self.uncheck_pushButton_login)
        '''
        
        # connecting the dashboard buttons to the navigate_to_dashboard() 
        self.ui.pushButton_icon_dashboard.clicked.connect(self.navigate_to_dashboard)
        self.ui.pushButton_full_dashboard.clicked.connect(self.navigate_to_dashboard)

        # connecting the inbound buttons to the navigate_to_inbound() 
        self.ui.pushButton_icon_inbound.clicked.connect(self.navigate_to_inbound)
        self.ui.pushButton_full_inbound.clicked.connect(self.navigate_to_inbound)

        # connecting the outbound buttons to the navigate_to_otbound() 
        self.ui.pushButton_icon_outbound.clicked.connect(self.navigate_to_outbound)
        self.ui.pushButton_full_outbound.clicked.connect(self.navigate_to_outbound)

        # connecting the inbentory buttons to the navigate_to_inventory() 
        self.ui.pushButton_icon_inventory.clicked.connect(self.navigate_to_inventory)
        self.ui.pushButton_full_inventory.clicked.connect(self.navigate_to_inventory)

        # connecting the report buttons to the navigate_to_report() 
        self.ui.pushButton_icon_report.clicked.connect(self.navigate_to_report)
        self.ui.pushButton_full_report.clicked.connect(self.navigate_to_report)

        # connecting the accounts buttons to the navigate_to_accounts() 
        self.ui.pushButton_icon_accounts.clicked.connect(self.navigate_to_accounts)
        self.ui.pushButton_full_accounts.clicked.connect(self.navigate_to_accounts)
        
        # connecting the profile buttons to the navigate_to_profile() 
        self.ui.pushButton_icon_profile.clicked.connect(self.navigate_to_profile)
        self.ui.pushButton_full_profile.clicked.connect(self.navigate_to_profile)


        #__________INVENTORY__________
        # initializing inventory menu to products tab - view all
        self.ui.stackedWidget_inventory.setCurrentIndex(0)
        self.ui.pushButton_inventory_products.setChecked(True)

        # connecting the tab buttons to their functions 
        self.ui.pushButton_inventory_products.clicked.connect(self.navigate_to_products_viewall)
        # self.ui.pushButton_inventory_brands.clicked.connect(self.navigate_to_brands_viewall)
        self.ui.pushButton_inventory_categories.clicked.connect(self.navigate_to_categories_viewall)


        #__________PRODUCTS__________
        # connecting the add button to the navigate_to_products_add() 
        self.ui.pushButton_products_add.clicked.connect(self.navigate_to_products_add)

        # connecting the edit button to the navigate_to_products_edit() 
        self.ui.pushButton_products_edit.clicked.connect(self.navigate_to_products_edit)

        # connecting the edit button to the navigate_to_products_edit() 
        self.ui.pushButton_products_delete.clicked.connect(self.delete_product) 

        # connecting the cancel buttons to the navigate_to_products_viewall() 
        self.ui.pushButton_products_add_cancel.clicked.connect(self.navigate_to_products_viewall)
        self.ui.pushButton_products_edit_cancel.clicked.connect(self.navigate_to_products_viewall)

  
        #_____CATEGORIES_____
        # connecting the add button to the navigate_to_category_add() 
        self.ui.pushButton_category_add.clicked.connect(self.navigate_to_category_add)

        # connecting the edit button to the navigate_to_category_edit() 
        self.ui.pushButton_category_edit.clicked.connect(self.navigate_to_category_edit)

        # connecting the edit button to the navigate_to_category_edit() 
        self.ui.pushButton_category_delete.clicked.connect(self.delete_category) 

        # connecting the cancel buttons to the navigate_to_category_viewall() 
        self.ui.pushButton_category_add_cancel.clicked.connect(self.navigate_to_categories_viewall)
        self.ui.pushButton_category_edit_cancel.clicked.connect(self.navigate_to_categories_viewall)

        # the save buttons for add and edit connections are to be defined in navigate_to_category_add and navigate_to_category_edit methods


        #__________ACCOUNTS__________
        # initializing accounts menu to view all
        self.ui.stackedWidget_accounts.setCurrentIndex(0)

        # connecting the add button to the navigate_to_accounts_add() 
        self.ui.pushButton_accounts_add.clicked.connect(self.navigate_to_accounts_add)

        # connecting the edit button to the check_to_accounts_edit() 
        self.ui.pushButton_accounts_edit.clicked.connect(self.navigate_to_accounts_edit)

        # connecting the delete button to the showDeleteAccountConfirmation()) 
        self.ui.pushButton_accounts_delete.clicked.connect(self.delete_account)

        # connecting the cancel buttons to the navigate_to_accounts_viewall() 
        self.ui.pushButton_accounts_add_cancel.clicked.connect(self.navigate_to_accounts_viewall)
        self.ui.pushButton_accounts_edit_cancel.clicked.connect(self.navigate_to_accounts_viewall)

        # the save buttons for add and edit connections are defined in navigate_to_accounts_add and navigate_to_accounts_edit methods
        

        #__________PROFILE__________
        # initializing accounts menu to view all
        self.ui.stackedWidget_profile.setCurrentIndex(0)

        # connecting the add button to the navigate_to_accounts_add() 
        # define this in the view_profile()

        # connecting the cancel button to the navigate_to_profile_view() 
        self.ui.pushButton_profile_edit_cancel.clicked.connect(self.navigate_to_profile_view)

        # the save buttons for edit connection are defined in navigate_to_profile_edit
        # self.ui.pushButton_profile_edit.clicked.connect(self.navigate_to_profile_edit)
        
        # initialize functions for design and viewing
        self.get_product_with_lowest_stock()
        self.get_product_with_highest_stock()
        self.get_product_count()

        self.design_inbound()
        self.design_outbound()

        self.view_all_accounts()
        self.design_add_accounts()
        self.design_edit_accounts()
       
        self.view_all_products()
        self.design_add_product()
        self.design_edit_product()

        self.view_all_categories()
        


    ### MOUSE DRAG EVENTS
    # Function to handle mouse press event
    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging_window = True
            self.offset = event.pos()

    # Function to handle mouse move event
    def mouse_move_event(self, event):
        if self.is_dragging_window:
            self.move(self.pos() + event.pos() - self.offset)

    # Function to handle mouse release event
    def mouse_release_event(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging_window = False
    
    def showLogoutConfirmation(self):
        messageBox = QMessageBox.question(self, "Logout Confirmation", "Are you sure you want to logout?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if messageBox == QMessageBox.Yes:
            self.navigate_to_login()
        else:
            pass



    ### NAVIGATE AND OTHER BUTTON EVENTS
    # function to minimize window
    def minimize_win(self):
        self.setWindowState(Qt.WindowMinimized)
    
    # function to close window
    def close_win(self):
        self.close()

    # function to uncheck menu icon button
    def uncheck_pushButton_icon_menu(self):
        self.ui.pushButton_icon_menu.setChecked(False)

    # function to uncheck menu full button
    def uncheck_pushButton_full_menu(self):
        self.ui.pushButton_full_menu.setChecked(False)


    def show_cropped_dashboard(self):
        self.ui.widget_dashboard_content_2.hide()


    def show_full_dashboard(self):
        self.ui.widget_dashboard_content_2.show()



    #__________LOGIN__________
    def validate_account(self):
        username = self.ui.lineEdit_username.text()
        password = self.ui.lineEdit_password.text()


        query = "SELECT user_id, role_id FROM table_accounts WHERE username = ? AND password = ?"
        result = cursor.execute(query, (username, password)).fetchone()

        if result is not None:
            user_id = result[0]
            self.view_profile(user_id)
            self.design_dashboard_header(username) 


            if result[1] == 1:
                self.ui.pushButton_full_inbound.show()
                self.ui.pushButton_icon_inbound.show()

                self.ui.pushButton_full_accounts.show()
                self.ui.pushButton_icon_accounts.show()

                self.ui.pushButton_full_inventory.show()
                self.ui.pushButton_icon_inventory.show()

                self.ui.widget_dashboard_content_2.show()

                self.navigate_to_main()
            elif result[1] == 2:
                self.ui.pushButton_full_inbound.hide()
                self.ui.pushButton_icon_inbound.hide()

                self.ui.pushButton_full_accounts.hide()
                self.ui.pushButton_icon_accounts.hide()

                self.ui.pushButton_full_inventory.hide()
                self.ui.pushButton_icon_inventory.hide()

                self.ui.widget_dashboard_content_2.show()


                self.navigate_to_main()
        else:
            self.navigate_to_login_incorrect()

    # function to navigate to login page
    def navigate_to_login(self):
        self.ui.pushButton_incorrect.hide()
        self.ui.lineEdit_username.setText("")
        self.ui.lineEdit_password.setText("")
        self.ui.stackedWidget_main.setCurrentIndex(0)
        self.ui.pushButton_login.setChecked(False)

    def navigate_to_login_incorrect(self):
        self.ui.pushButton_incorrect.show()
        self.ui.lineEdit_username.setText("")
        self.ui.lineEdit_password.setText("")
        self.ui.stackedWidget_main.setCurrentIndex(0)
        self.ui.pushButton_login.setChecked(False)

    # function to navigate to admin page
    def navigate_to_main(self):
        # go to main admin
        self.ui.stackedWidget_main.setCurrentIndex(1)

        # initializing the design of the main admin
        self.ui.widget_full_menu.hide()
        self.ui.widget_icon_menu.show()
        self.ui.stackedWidget_pages.setCurrentIndex(0)
        self.ui.pushButton_icon_dashboard.setChecked(True)
        self.ui.pushButton_icon_menu.setChecked(False)

    # function to navigate to user page
    def navigate_to_main_user(self):
        self.ui.widget_full_menu.hide()
        self.ui.widget_icon_menu.show()
        self.ui.stackedWidget_main.setCurrentIndex(2)
        self.ui.stackedWidget_pages.setCurrentIndex(0)
        self.ui.pushButton_icon_dashboard.setChecked(True)
        self.ui.pushButton_icon_menu.setChecked(False)


    #__________NAVIGATION FUNCTIONS__________

    #_____MAIN MENU_____
    # function to navigate to inbound page
    def navigate_to_dashboard(self):
        self.ui.stackedWidget_pages.setCurrentIndex(0)

    # function to navigate to inbound page
    def navigate_to_inbound(self):
        self.ui.stackedWidget_pages.setCurrentIndex(1)

    # function to navigate to outbound page
    def navigate_to_outbound(self):
        self.ui.stackedWidget_pages.setCurrentIndex(2)

    # function to navigate to outbound page
    def navigate_to_inventory(self):
        self.ui.stackedWidget_pages.setCurrentIndex(3)

    # function to navigate to outbound page
    def navigate_to_report(self):
        self.ui.stackedWidget_pages.setCurrentIndex(4)

    # function to navigate to outbound page
    def navigate_to_accounts(self):
        self.ui.stackedWidget_pages.setCurrentIndex(5)

    # function to navigate to outbound page
    def navigate_to_profile(self):
        self.ui.stackedWidget_pages.setCurrentIndex(6)

    
    #__________DASHBOARD__________
    def design_dashboard_header(self, username):
        self.ui.label_username.setText(username)

    def get_product_with_lowest_stock(self):

        # Execute the query to get the product with the lowest stock
        query = '''
        SELECT stock, product_name, COUNT(*) as count
        FROM table_inventory
        WHERE stock = (
            SELECT MIN(stock)
            FROM table_inventory
        )
        GROUP BY stock
        '''
        cursor.execute(query)
        result = cursor.fetchall()

        stock = result[0][0]
        product_name = result[0][1]

        stock_3digits = "{:03d}".format(stock)
        
        self.ui.label_content_1_number.setWordWrap(True)
        self.ui.label_content_1_number.setText(stock_3digits)

        self.ui.label_content_1_details.setWordWrap(True)
        self.ui.label_content_1_details.setText(product_name)

        count = result[0][2]

        if count > 1:
            count_others = count - 1

            if count_others > 1: 

                self.ui.label_content_1_additional.setWordWrap(True)
                self.ui.label_content_1_additional.setText(f"and {count_others} more are low on stock ")
            else: 
                
                self.ui.label_content_1_additional.setWordWrap(True)
                self.ui.label_content_1_additional.setText(f"and another is low on stock ")

        else:
            if stock >=0 and stock < 10:
                self.ui.label_content_1_additional.setText("Oh noes, def time to restock!")
            elif stock >=10 and stock <100:
                self.ui.label_content_1_additional.setText("Looking good!\n")
            elif stock >= 100 and stock < 400:
                self.ui.label_content_1_additional.setText("Oh, your safe!\n")
            elif stock >= 400:
                self.ui.label_content_1_additional.setText("Hey, when you gonna sell these?")
        
        if stock >=0 and stock < 10:
            self.ui.label_content_1_number.setStyleSheet("color: rgba(103, 25, 25, 255)")
        elif stock >=10 and stock <100:
            self.ui.label_content_1_number.setStyleSheet("color: rgba(22, 66, 110, 255)")
            

    def get_product_with_highest_stock(self):

        # Execute the query to get the product with the lowest stock
        query = '''
        SELECT stock, product_name, COUNT(*) as count
        FROM table_inventory
        WHERE stock = (
            SELECT MAX(stock)
            FROM table_inventory
        )
        GROUP BY stock
        '''
        cursor.execute(query)
        result = cursor.fetchall()

        stock = result[0][0]
        product_name = result[0][1]

        stock_3digits = "{:03d}".format(stock)

        self.ui.label_content_3_number.setWordWrap(True)
        self.ui.label_content_3_number.setText(stock_3digits)

        self.ui.label_content_3_details.setWordWrap(True)
        self.ui.label_content_3_details.setText(product_name)

        count = result[0][2]

        if count > 1:
            
            count_others = count - 1

            if count_others > 1: 

                self.ui.label_content_3_additional.setWordWrap(True)
                self.ui.label_content_3_additional.setText(f"and {count_others} more are high on stock ")
            else: 
                
                self.ui.label_content_3_additional.setWordWrap(True)
                self.ui.label_content_3_additional.setText(f"and another is high on stock")
        
        else:
            if stock >=0 and stock < 10:
                self.ui.label_content_3_additional.setText("Oh noes, def time to restock!")
                self.ui.label_content_3_number.setStyleSheet("color: rgba(103, 25, 25, 255)")
            elif stock >=10 and stock <100:
                self.ui.label_content_3_additional.setText("Looking good!\n")
                self.ui.label_content_3_number.setStyleSheet("color: rgba(22, 66, 110, 255)")
            elif stock >= 100 and stock < 400:
                self.ui.label_content_3_additional.setText("Oh, your safe!\n")
            elif stock >= 400:
                self.ui.label_content_3_additional.setText("Hey, when you gonna sell these?")

        if stock >=0 and stock < 10:
            self.ui.label_content_3_number.setStyleSheet("color: rgba(103, 25, 25, 255)")
        elif stock >=10 and stock <100:
            self.ui.label_content_3_number.setStyleSheet("color: rgba(22, 66, 110, 255)")


    def get_product_count(self):

        cursor.execute("SELECT COUNT(*) FROM table_inventory")
        count = cursor.fetchone()[0]
        
        count_3digits = "{:03d}".format(count)
        
        self.ui.label_content_2_number.setText(count_3digits)
        if count >=0 and count < 10:
            self.ui.label_content_2_additional.setText("Well, that looks few.\n")
        elif count >=10 and count <80:
            self.ui.label_content_2_additional.setText("Getting big, huh?\n")
        elif count >= 80:
            self.ui.label_content_2_additional.setText("Sweet, Paninda Pro!\n")

        if count >=0 and count < 10:
            self.ui.label_content_2_number.setStyleSheet("color: rgba(103, 25, 25, 255)")
        elif count >=10 and count <80:
            self.ui.label_content_2_number.setStyleSheet("color: rgba(22, 66, 110, 255)")


    # __________INBOUND__________
    def design_inbound(self):
        self.ui.comboBox_inbound_category.clear()
        self.ui.comboBox_inbound_category.addItem("Select category")
        cursor.execute('SELECT category_id, category FROM table_category')
        data = cursor.fetchall()

        # Populate the first combo box (comboBox_inbound_category)
        for category_id, category in data:
            self.ui.comboBox_inbound_category.addItem(category, category_id)

        self.ui.comboBox_inbound_products.addItem("Select product")

        # Disable select options
        self.ui.comboBox_inbound_category.model().item(0).setFlags(Qt.ItemFlags(Qt.NoItemFlags))
        self.ui.comboBox_inbound_products.model().item(0).setFlags(Qt.ItemFlags(Qt.NoItemFlags))

        # Connect the currentIndexChanged signal of the first combo box to the update_design_inbound slot
        self.ui.comboBox_inbound_category.currentIndexChanged.connect(self.update_design_inbound)

        self.ui.pushButton_inbound_save.clicked.connect(self.add_stocks)

    def update_design_inbound(self):
        category_id = self.ui.comboBox_inbound_category.currentData()  # Get the selected category_id
        self.ui.comboBox_inbound_products.clear()  # Clear the second combo box
        self.ui.comboBox_inbound_products.addItem("Select product")
        self.ui.comboBox_inbound_products.model().item(0).setFlags(Qt.ItemFlags(Qt.NoItemFlags))

        # Fetch products for the selected category from the database and populate the second combo box
        cursor.execute("SELECT inventory_id, product_name FROM table_inventory WHERE category_id = ?", (category_id,))
        products = cursor.fetchall()
        for inventory_id, product_name in products:
            self.ui.comboBox_inbound_products.addItem(product_name, inventory_id)
        

    def add_stocks(self):
        category = self.ui.comboBox_inbound_category.currentText()
        inventory = self.ui.comboBox_inbound_products.currentText()

        category_id = self.ui.comboBox_inbound_category.currentData()
        inventory_id = self.ui.comboBox_inbound_products.currentData()
        stocks_to_add = self.ui.lineEdit_inbound_stocks.text()

        if category == "Select category" and inventory == "Select product":
            QMessageBox.warning(self, "Warning", "Please select a category and product.")
            self.ui.pushButton_inbound_save.setChecked(False)
            return

        if category == "Select category":
            QMessageBox.warning(self, "Warning", "Please select a category.")
            self.ui.pushButton_inbound_save.setChecked(False)
            return

        if inventory == "Select product":
            QMessageBox.warning(self, "Warning", "Please select a product.")
            self.ui.pushButton_inbound_save.setChecked(False)
            return

        if stocks_to_add == "":
            QMessageBox.warning(self, "Warning", "Please indicate the number of stocks to add.")
            self.ui.pushButton_inbound_save.setChecked(False)
            return

        if not stocks_to_add.isnumeric():
            QMessageBox.warning(self, "Warning", "Please enter a numeric value for stocks to add.")
            self.ui.pushButton_inbound_save.setChecked(False)
            return

        stocks_to_add = int(stocks_to_add)

        cursor.execute("SELECT stock FROM table_inventory WHERE inventory_id = ?", (inventory_id,))
        current_stock = cursor.fetchone()[0]

        new_stock = current_stock + stocks_to_add
        cursor.execute("UPDATE table_inventory SET stock = ? WHERE inventory_id = ?", (new_stock, inventory_id))
        db_connect.commit()

        self.ui.tableWidget_products.clearContents()
        self.ui.tableWidget_products.setRowCount(0)
        self.view_all_products()

        self.ui.comboBox_inbound_category.setCurrentIndex(0)
        self.ui.comboBox_inbound_products.setCurrentIndex(0)
        self.ui.lineEdit_inbound_stocks.setText("")

        QMessageBox.information(self, "Success", "Product stock level updated successfully!")
        self.ui.pushButton_inbound_save.setChecked(False)

                
    def refresh_category_comboBoxes(self):
        # FOR OUTBOUND
        self.ui.comboBox_outbound_category.clear()
        self.ui.comboBox_outbound_category.addItem("Select category")
        
        cursor.execute('SELECT category_id, category FROM table_category')
        data = cursor.fetchall()

        # Populate the combo box with updated category data
        for category_id, category in data:
            self.ui.comboBox_outbound_category.addItem(category, category_id)
        
        # Disable select option
        self.ui.comboBox_outbound_category.model().item(0).setFlags(Qt.NoItemFlags)


        # FOR INBOUND
        self.ui.comboBox_inbound_category.clear()
        self.ui.comboBox_inbound_category.addItem("Select category")
        
        cursor.execute('SELECT category_id, category FROM table_category')
        data = cursor.fetchall()

        # Populate the combo box with updated category data
        for category_id, category in data:
            self.ui.comboBox_inbound_category.addItem(category, category_id)
        
        # Disable select option
        self.ui.comboBox_inbound_category.model().item(0).setFlags(Qt.NoItemFlags)


        # FOR INVENTORY ADD
        self.ui.comboBox_products_category_add.clear()
        self.ui.comboBox_products_category_add.addItem("Select category")
        
        cursor.execute('SELECT category_id, category FROM table_category')
        data = cursor.fetchall()

        # Populate the combo box with updated category data
        for category_id, category in data:
            self.ui.comboBox_products_category_add.addItem(category, category_id)
        
        # Disable select option
        self.ui.comboBox_products_category_add.model().item(0).setFlags(Qt.NoItemFlags)

        # FOR INVENTORY EDIT
        self.ui.comboBox_products_category_edit.clear()
        self.ui.comboBox_products_category_edit.addItem("Select category")
        
        cursor.execute('SELECT category_id, category FROM table_category')
        data = cursor.fetchall()

        # Populate the combo box with updated category data
        for category_id, category in data:
            self.ui.comboBox_products_category_edit.addItem(category, category_id)
        
        # Disable select option
        self.ui.comboBox_products_category_edit.model().item(0).setFlags(Qt.NoItemFlags)

    # __________OUTBOUND__________
    def design_outbound(self):
        self.ui.comboBox_outbound_category.clear()
        self.ui.comboBox_outbound_category.addItem("Select category")
        cursor.execute('SELECT category_id, category FROM table_category')
        data = cursor.fetchall()

        # Populate the first combo box (comboBox_outbound_category)
        for category_id, category in data:
            self.ui.comboBox_outbound_category.addItem(category, category_id)

        self.ui.comboBox_outbound_products.addItem("Select product")

        # Disable select options
        self.ui.comboBox_outbound_category.model().item(0).setFlags(Qt.ItemFlags(Qt.NoItemFlags))
        self.ui.comboBox_outbound_products.model().item(0).setFlags(Qt.ItemFlags(Qt.NoItemFlags))

        # Connect the currentIndexChanged signal of the first combo box to the update_design_outbound slot
        self.ui.comboBox_outbound_category.currentIndexChanged.connect(self.update_design_outbound)

        self.ui.pushButton_outbound_save.clicked.connect(self.delete_stocks)

    def update_design_outbound(self):
        category_id = self.ui.comboBox_outbound_category.currentData()  # Get the selected category_id
        self.ui.comboBox_outbound_products.clear()  # Clear the second combo box
        self.ui.comboBox_outbound_products.addItem("Select product")
        self.ui.comboBox_outbound_products.model().item(0).setFlags(Qt.ItemFlags(Qt.NoItemFlags))

        # Fetch products for the selected category from the database and populate the second combo box
        cursor.execute("SELECT inventory_id, product_name FROM table_inventory WHERE category_id = ?", (category_id,))
        products = cursor.fetchall()
        for inventory_id, product_name in products:
            self.ui.comboBox_outbound_products.addItem(product_name, inventory_id)


        

    def delete_stocks(self):
        category = self.ui.comboBox_outbound_category.currentText()
        inventory = self.ui.comboBox_outbound_products.currentText()

        category_id = self.ui.comboBox_outbound_category.currentData()
        inventory_id = self.ui.comboBox_outbound_products.currentData()
        stocks_to_delete = self.ui.lineEdit_outbound_stocks.text()

        if category == "Select category" and inventory == "Select product":
            QMessageBox.warning(self, "Warning", "Please select a category and product.")
            self.ui.pushButton_outbound_save.setChecked(False)
            return

        if category == "Select category":
            QMessageBox.warning(self, "Warning", "Please select a category.")
            self.ui.pushButton_outbound_save.setChecked(False)
            return

        if inventory == "Select product":
            QMessageBox.warning(self, "Warning", "Please select a product.")
            self.ui.pushButton_outbound_save.setChecked(False)
            return

        if stocks_to_delete == "":
            QMessageBox.warning(self, "Warning", "Please indicate the number of stocks to add.")
            self.ui.pushButton_outbound_save.setChecked(False)
            return

        if not stocks_to_delete.isnumeric():
            QMessageBox.warning(self, "Warning", "Please enter a numeric value for stocks to add.")
            self.ui.pushButton_outbound_save.setChecked(False)
            return

        stocks_to_delete = int(stocks_to_delete)

        cursor.execute("SELECT stock FROM table_inventory WHERE inventory_id = ?", (inventory_id,))
        current_stock = cursor.fetchone()[0]

        if current_stock >= stocks_to_delete:
            new_stock = current_stock - stocks_to_delete
            cursor.execute("UPDATE table_inventory SET stock = ? WHERE inventory_id = ?", (new_stock, inventory_id))
            db_connect.commit()

            self.ui.tableWidget_products.clearContents()
            self.ui.tableWidget_products.setRowCount(0)
            self.view_all_products()

            self.ui.comboBox_outbound_category.setCurrentIndex(0)
            self.ui.comboBox_outbound_products.setCurrentIndex(0)
            self.ui.lineEdit_outbound_stocks.setText("")

            QMessageBox.information(self, "Success", "Product stock level updated successfully!")
            self.ui.pushButton_outbound_save.setChecked(False)
        else:
            QMessageBox.warning(self, "Error", "Insufficient stocks")
            self.ui.pushButton_outbound_save.setChecked(False)
            return


    #__________INVENTORY__________
    # PRODUCTS
    # function to navigatet to view all (can also be used to cancel add and edit)
    def navigate_to_products_viewall(self):
        self.ui.stackedWidget_inventory.setCurrentIndex(0)
        self.ui.buttonGroup_products.setExclusive(False)
        for button in self.ui.buttonGroup_products.buttons():
            button.setChecked(False)

    # function to navigate to products add
    def navigate_to_products_add(self):
        self.ui.lineEdit_products_name_add.setText("")
        self.ui.lineEdit_products_pricepiece_add.setText("")
        self.ui.lineEdit_products_stocks_add.setText("")
        self.ui.comboBox_products_category_add.setCurrentIndex(0)

        self.ui.stackedWidget_inventory.setCurrentIndex(1)
        self.ui.buttonGroup_products_add.setExclusive(False)
        for button in self.ui.buttonGroup_products_add.buttons():
            button.setChecked(False)
        self.ui.pushButton_products_add_save.clicked.connect(self.add_product)

    
    # function to navigate to products edit
    def navigate_to_products_edit(self):

        selected_row = self.ui.tableWidget_products.currentRow()
        if selected_row < 0:
            messageBox = QMessageBox.warning(self, "Warning", "Please select a row to edit!", QMessageBox.Ok)
            if messageBox == QMessageBox.Ok:
                self.navigate_to_accounts_viewall()
                return
            return
        

        # get user id of selected row
        inventory_id_item = self.ui.tableWidget_products.item(selected_row, 0)
        inventory_id = int(inventory_id_item.text())

        # get current values of selected row
        product_item = self.ui.tableWidget_products.item(selected_row, 1)
        product = product_item.text()

        price_piece_item = self.ui.tableWidget_products.item(selected_row, 2)
        price_piece = int(price_piece_item.text())

        stock_item = self.ui.tableWidget_products.item(selected_row, 3)
        stock = int(stock_item.text())


        category_item = self.ui.tableWidget_products.item(selected_row, 5)
        category = category_item.text()


        # populate fields with current values
        self.ui.lineEdit_products_name_edit.setText(product)
        self.ui.lineEdit_products_pricepiece_edit.setText(str(price_piece))
        self.ui.lineEdit_products_stocks_edit.setText(str(stock))
        self.ui.comboBox_products_category_edit.setCurrentText(category)

        self.ui.stackedWidget_inventory.setCurrentIndex(2)
        self.ui.buttonGroup_products_edit.setExclusive(False)
        for button in self.ui.buttonGroup_products_edit.buttons():
            button.setChecked(False)

        self.ui.pushButton_products_edit_save.clicked.connect(lambda: self.edit_product(inventory_id))

    


    def view_all_products(self):

        self.get_product_with_lowest_stock()
        self.get_product_with_highest_stock()
        self.get_product_count()
        
        query = """
            SELECT i.inventory_id, i.product_name, i.price_per_piece, i.stock, i.total_price, c.category
            FROM table_inventory i
            JOIN table_category c ON i.category_id = c.category_id;
        """
        cursor.execute(query)
        data = cursor.fetchall()

        headers = ['Inventory ID', 'Product', 'Price', 'Stock', 'Total Price', 'Category']
        self.ui.tableWidget_products.setColumnCount(len(headers))
        self.ui.tableWidget_products.setHorizontalHeaderLabels(headers)

        row = 0
        for row_data in data:
            self.ui.tableWidget_products.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.ui.tableWidget_products.setItem(row, col, item)
            row += 1
            
    def design_add_product(self):
        self.ui.comboBox_products_category_add.addItem("Select category")
        cursor.execute('SELECT category FROM table_category')
        data = cursor.fetchall()
        
        # populate comboBox with data from SQL query
        for role in data:
            self.ui.comboBox_products_category_add.addItem(role[0])
        model = QStandardItemModel()
        delegate = QStyledItemDelegate()
        for i in range(self.ui.comboBox_products_category_add.count()):
            item = QStandardItem(self.ui.comboBox_products_category_add.itemText(i))
            if i == 0:
                item.setEnabled(False)  # Disable "Select role" item
            model.appendRow(item)
        self.ui.comboBox_products_category_add.setModel(model)
        self.ui.comboBox_products_category_add.setItemDelegate(delegate)

    def design_edit_product(self):
        self.ui.comboBox_products_category_edit.addItem("Select category")
        cursor.execute('SELECT category FROM table_category')
        data = cursor.fetchall()
        
        # populate comboBox with data from SQL query
        for role in data:
            self.ui.comboBox_products_category_edit.addItem(role[0])
        model = QStandardItemModel()
        delegate = QStyledItemDelegate()
        for i in range(self.ui.comboBox_products_category_edit.count()):
            item = QStandardItem(self.ui.comboBox_products_category_edit.itemText(i))
            if i == 0:
                item.setEnabled(False)  # Disable "Select role" item
            model.appendRow(item)
        self.ui.comboBox_products_category_edit.setModel(model)
        self.ui.comboBox_products_category_edit.setItemDelegate(delegate)

    def add_product(self):

        product_name = self.ui.lineEdit_products_name_add.text()
        price_piece = self.ui.lineEdit_products_pricepiece_add.text()
        stock = self.ui.lineEdit_products_stocks_add.text()
        category = self.ui.comboBox_products_category_add.currentText()

        if not price_piece.isnumeric() or not stock.isnumeric():
            QMessageBox.warning(self, "Warning", "Please enter numeric values for price and stock.")
            return
        
        price_piece = int(price_piece)
        stock = int(stock)
        price_total = price_piece * stock

        if category == "Select category":
            QMessageBox.warning(self, "Warning", "Please select a category.")
            return
        

        # check if there is no similar product name
        cursor.execute("SELECT COUNT(*) FROM table_inventory WHERE product_name = ?", (product_name,))
        result = cursor.fetchone()


        if result is not None:
            # If result is 1, meaning there is already an instance of the username. so return
            if result[0] > 0:
                QMessageBox.warning(self, "Warning", "Product already exists.")
                return
            else: 

                cursor.execute("SELECT category_id FROM table_category WHERE category = ?", (category,))
                category_id = cursor.fetchone()[0]    

                cursor.execute("INSERT INTO table_inventory (product_name, price_per_piece, stock, total_price, category_id) VALUES (?, ?, ?, ?, ?)",
                            (product_name, price_piece, stock, price_total, category_id))
      
                db_connect.commit()
                QMessageBox.information(self, "Success", "Product added successfully!")

                self.ui.tableWidget_products.clearContents()
                self.ui.tableWidget_products.setRowCount(0)
                self.view_all_products()
                self.navigate_to_products_viewall()

        self.ui.pushButton_products_add_save.clicked.disconnect()


    def edit_product(self, inventory_id):
        # get edited values


  
        edited_product = self.ui.lineEdit_products_name_edit.text()
        edited_price_piece = self.ui.lineEdit_products_pricepiece_edit.text()
        edited_stock = self.ui.lineEdit_products_stocks_edit.text()
        edited_category = self.ui.comboBox_products_category_edit.currentText()

        if not edited_price_piece.isnumeric() or not edited_stock.isnumeric():
            QMessageBox.warning(self, "Warning", "Please enter numeric values for price and stock.")
            return
        
        edited_price_piece = int(edited_price_piece)
        edited_stock = int(edited_stock)
        edited_price_total = edited_price_piece * edited_stock

        # check if there is no similar product name
        cursor.execute("SELECT COUNT(*) FROM table_inventory WHERE product_name = ? AND inventory_id <> ?", (edited_product, inventory_id))
        result = cursor.fetchone()


        if result is not None:
            # If result is 1, meaning there is already an instance of the username. so return
            if result[0] > 0:
                QMessageBox.warning(self, "Warning", "Product already exists.")
                return
            else: 

            # execute stored procedure to update row in database
            
            
                cursor.execute("SELECT category_id FROM table_category WHERE category = ?", (edited_category,))
                edited_category_id = cursor.fetchone()[0]    

                cursor.execute("UPDATE table_inventory SET product_name = ?, price_per_piece = ?, stock = ?, total_price = ?, category_id = ? WHERE inventory_id = ?",
                        (edited_product, edited_price_piece, edited_stock, edited_price_total, edited_category_id, inventory_id))
                db_connect.commit()
                QMessageBox.information(self, "Success", "Product updated successfully!")

                self.ui.tableWidget_products.clearContents()
                self.ui.tableWidget_products.setRowCount(0)
                self.view_all_products()
                self.navigate_to_products_viewall()

        self.ui.pushButton_products_edit_save.clicked.disconnect()


    def delete_product(self):
        selected_row = self.ui.tableWidget_products.currentRow()
        if selected_row < 0:
            messageBox = QMessageBox.warning(self, "Warning", "Please select a row to delete!", QMessageBox.Ok)
            if messageBox == QMessageBox.Ok:
                self.navigate_to_products_viewall()
                return
            return
        
        messageBox = QMessageBox.question(self, "Delete Confirmation", "Are you sure you want to delete this product?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if messageBox == QMessageBox.Yes:

            # get user id of selected row
            inventory_id_item = self.ui.tableWidget_products.item(selected_row, 0)
            inventory_id = int(inventory_id_item.text())
            
            cursor.execute("DELETE FROM table_inventory WHERE inventory_id = ?", (inventory_id,))
            db_connect.commit()
           
            
            self.ui.tableWidget_products.clearContents()
            self.ui.tableWidget_products.setRowCount(0)
            self.view_all_products()
            self.navigate_to_products_viewall()
            QMessageBox.information(self, "Success", "Product deleted successfully!")

        else:
            pass


    # CATEGORIES
    # function to navigatet to view all (can also be used to cancel add and edit)
    def navigate_to_categories_viewall(self):
        self.ui.stackedWidget_inventory.setCurrentIndex(6)
        self.ui.buttonGroup_categories.setExclusive(False)
        for button in self.ui.buttonGroup_categories.buttons():
            button.setChecked(False)
   
    # function to navigate to category add
    def navigate_to_category_add(self):
        self.ui.lineEdit_category_name_add.setText("")

        self.ui.stackedWidget_inventory.setCurrentIndex(7)
        self.ui.buttonGroup_categories_add.setExclusive(False)
        for button in self.ui.buttonGroup_categories_add.buttons():
            button.setChecked(False)
        self.ui.pushButton_category_add_save.clicked.connect(self.add_category)

    # function to navigate to category edit
    def navigate_to_category_edit(self):

        selected_row = self.ui.tableWidget_category.currentRow()
        if selected_row < 0:
            messageBox = QMessageBox.warning(self, "Warning", "Please select a row to edit!", QMessageBox.Ok)
            if messageBox == QMessageBox.Ok:
                self.navigate_to_accounts_viewall()
                return
            return
        

        # get category id of selected row
        category_id_item = self.ui.tableWidget_category.item(selected_row, 0)
        category_id = int(category_id_item.text())

        # get current values of selected row
        category_item = self.ui.tableWidget_category.item(selected_row, 1)
        category = category_item.text()



        # populate fields with current values
        self.ui.lineEdit_category_name_edit.setText(category)


        self.ui.stackedWidget_inventory.setCurrentIndex(8)
        self.ui.buttonGroup_categories_edit.setExclusive(False)
        for button in self.ui.buttonGroup_categories_edit.buttons():
            button.setChecked(False)

        self.ui.pushButton_category_edit_save.clicked.connect(lambda: self.edit_category(category_id))



    def view_all_categories(self):
        
        query = """
        SELECT category_id, category FROM table_category;
        """
        cursor.execute(query)
        data = cursor.fetchall()

        headers = ['Category ID', 'Category']
        self.ui.tableWidget_category.setColumnCount(len(headers))
        self.ui.tableWidget_category.setHorizontalHeaderLabels(headers)

        row = 0
        for row_data in data:
            self.ui.tableWidget_category.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.ui.tableWidget_category.setItem(row, col, item)
            row += 1


    def add_category(self):

        category_name = self.ui.lineEdit_category_name_add.text()

        if category_name == "":
            QMessageBox.warning(self, "Warning", "Please input category name")
            return
        
        #check if there is no similar category already
        cursor.execute("SELECT COUNT(*) FROM table_category WHERE category = ?", (category_name,))
        result = cursor.fetchone()

        if result is not None:
            # If result is 1, meaning there is already an instance of the username. so return
            if result[0] > 0:
                QMessageBox.warning(self, "Warning", "Category already exists.")
                return
            else:


                cursor.execute("INSERT INTO table_category (category) VALUES (?)",(category_name,))        
                db_connect.commit()
                QMessageBox.information(self, "Success", "Category added successfully!")

                self.ui.tableWidget_category.clearContents()
                self.ui.tableWidget_category.setRowCount(0)
                # update table
                self.view_all_categories()
                # update combo boxes
                self.refresh_category_comboBoxes()
                
                self.navigate_to_categories_viewall()

        self.ui.pushButton_category_add_save.clicked.disconnect()


    
    def edit_category(self, category_id):
        # get edited values
  
        edited_category = self.ui.lineEdit_category_name_edit.text()

        # check if there is no similar usernmae
        cursor.execute("SELECT COUNT(*) FROM table_category WHERE category = ? AND category_id <> ?", (edited_category, category_id))
        result = cursor.fetchone()


        if result is not None:
            # If result is 1, meaning there is already an instance of the username. so return
            if result[0] > 0:
                QMessageBox.warning(self, "Warning", "Category already in records.")
                return
            else: 

            # execute stored procedure to update row in database


                cursor.execute("UPDATE table_category SET category = ? WHERE category_id = ?",
                        (edited_category, category_id))
                db_connect.commit()
                QMessageBox.information(self, "Success", "Category name updated successfully!")

                self.ui.tableWidget_category.clearContents()
                self.ui.tableWidget_category.setRowCount(0)
                # update table
                self.view_all_categories()
                # update combo boxes
                self.refresh_category_comboBoxes()
                
                self.navigate_to_categories_viewall()

        self.ui.pushButton_category_edit_save.clicked.disconnect()


    def delete_category(self):
        selected_row = self.ui.tableWidget_category.currentRow()
        if selected_row < 0:
            messageBox = QMessageBox.warning(self, "Warning", "Please select a row to delete!", QMessageBox.Ok)
            if messageBox == QMessageBox.Ok:
                self.navigate_to_categories_viewall()
                return
            return
        
        messageBox = QMessageBox.question(self, "Delete Confirmation", "Are you sure you want to delete this category?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if messageBox == QMessageBox.Yes:

            # get user id of selected row
            category_id_item = self.ui.tableWidget_category.item(selected_row, 0)
            category_id = int(category_id_item.text())
            
            cursor.execute("DELETE FROM table_category WHERE category_id = ?", (category_id,))
            db_connect.commit()
           
            
            self.ui.tableWidget_category.clearContents()
    
            self.ui.tableWidget_category.setRowCount(0)
            # update table
            self.view_all_categories()
            # update combo boxes
            self.refresh_category_comboBoxes()

            self.navigate_to_categories_viewall()
            QMessageBox.information(self, "Success", "Category deleted successfully!")  

        else:
            pass



    #__________ACCOUNTS__________
    # function to navigatet to view all (can also be used to cancel add and edit)
    def navigate_to_accounts_viewall(self):

        self.ui.stackedWidget_accounts.setCurrentIndex(0)
        self.ui.buttonGroup_accounts.setExclusive(False)
        for button in self.ui.buttonGroup_accounts.buttons():
            button.setChecked(False)

    # function to navigate to accounts add
    def navigate_to_accounts_add(self):
        self.ui.lineEdit_accounts_username_add.setText("")
        self.ui.lineEdit_accounts_password_add.setText("")
        self.ui.comboBox_accounts_role_add.setCurrentIndex(0)

        self.ui.stackedWidget_accounts.setCurrentIndex(1)
        self.ui.buttonGroup_accounts_add.setExclusive(False)
        for button in self.ui.buttonGroup_accounts_add.buttons():
            button.setChecked(False)

        self.ui.pushButton_accounts_add_save.clicked.connect(self.add_account)

    # function to navigate to accounts edit
    def navigate_to_accounts_edit(self):
        selected_row = self.ui.tableWidget_accounts.currentRow()
        if selected_row < 0:
            messageBox = QMessageBox.warning(self, "Warning", "Please select a row to edit!", QMessageBox.Ok)
            if messageBox == QMessageBox.Ok:
                self.navigate_to_accounts_viewall()
                return
            return
        

        # get user id of selected row
        user_id_item = self.ui.tableWidget_accounts.item(selected_row, 0)
        user_id = int(user_id_item.text())

        # get current values of selected row
        username_item = self.ui.tableWidget_accounts.item(selected_row, 1)
        username = username_item.text()

        password_item = self.ui.tableWidget_accounts.item(selected_row, 2)
        password = password_item.text()

        role_item = self.ui.tableWidget_accounts.item(selected_row, 3)
        role = role_item.text()


        # populate fields with current values
        self.ui.lineEdit_accounts_username_edit.setText(username)
        self.ui.lineEdit_accounts_password_edit.setText(password)
        self.ui.comboBox_accounts_role_edit.setCurrentText(role)

        self.ui.stackedWidget_accounts.setCurrentIndex(2)
        self.ui.buttonGroup_accounts_add.setExclusive(False)
        for button in self.ui.buttonGroup_accounts_add.buttons():
            button.setChecked(False)

        self.ui.pushButton_accounts_edit_save.clicked.connect(lambda: self.edit_account(user_id))

    def view_all_accounts(self):
        
        query = """
            SELECT a.user_id, a.username, a.password, r.role
            FROM table_accounts a
            JOIN table_role r ON a.role_id = r.role_id
        """
        cursor.execute(query)
        data = cursor.fetchall()

        headers = ['User ID', 'Username', 'Password', 'Role']
        self.ui.tableWidget_accounts.setColumnCount(len(headers))
        self.ui.tableWidget_accounts.setHorizontalHeaderLabels(headers)

        row = 0
        for row_data in data:
            self.ui.tableWidget_accounts.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.ui.tableWidget_accounts.setItem(row, col, item)
            row += 1

    def design_add_accounts(self):
        self.ui.comboBox_accounts_role_add.addItem("Select role")
        cursor.execute('SELECT role FROM table_role')
        data = cursor.fetchall()
        
        # populate comboBox with data from SQL query
        for role in data:
            self.ui.comboBox_accounts_role_add.addItem(role[0])
        model = QStandardItemModel()
        delegate = QStyledItemDelegate()
        for i in range(self.ui.comboBox_accounts_role_add.count()):
            item = QStandardItem(self.ui.comboBox_accounts_role_add.itemText(i))
            if i == 0:
                item.setEnabled(False)  # Disable "Select role" item
            model.appendRow(item)
        self.ui.comboBox_accounts_role_add.setModel(model)
        self.ui.comboBox_accounts_role_add.setItemDelegate(delegate)

    def design_edit_accounts(self):
        self.ui.comboBox_accounts_role_edit.addItem("Select role")
        cursor.execute('SELECT role FROM table_role')
        data = cursor.fetchall()
        
        # populate comboBox with data from SQL query
        for role in data:
            self.ui.comboBox_accounts_role_edit.addItem(role[0])
        model = QStandardItemModel()
        delegate = QStyledItemDelegate()
        for i in range(self.ui.comboBox_accounts_role_edit.count()):
            item = QStandardItem(self.ui.comboBox_accounts_role_edit.itemText(i))
            if i == 0:
                item.setEnabled(False)  # Disable "Select role" item
            model.appendRow(item)
        self.ui.comboBox_accounts_role_edit.setModel(model)
        self.ui.comboBox_accounts_role_edit.setItemDelegate(delegate)


    def add_account(self):

        username = self.ui.lineEdit_accounts_username_add.text()
        password = self.ui.lineEdit_accounts_password_add.text()
        role = self.ui.comboBox_accounts_role_add.currentText()


        if role == "Select role":
            QMessageBox.warning(self, "Warning", "Please select a role.")
            return

        # check if there is no similar usernmae
        query = "SELECT COUNT(*) FROM table_accounts WHERE username = ?"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        count  = result[0]

        if result is not None:
            if count > 0:
                # If result is 1, meaning there is already an instance of the username. so return
                QMessageBox.warning(self, "Warning", "Username not available")
                return
        
                
            else:
            
                cursor.execute("SELECT role_id FROM table_role WHERE role = ?", (role,))
                role_id = cursor.fetchone()[0]    

                cursor.execute("INSERT INTO table_accounts (username, password, role_id) VALUES (?, ?, ?)",
                    (username, password, role_id))        
                db_connect.commit()
                QMessageBox.information(self, "Success", "Account added successfully!")

                self.ui.tableWidget_accounts.clearContents()
                self.ui.tableWidget_accounts.setRowCount(0)

                self.view_all_accounts()
                
                self.navigate_to_accounts_viewall()
        self.ui.pushButton_accounts_add_save.clicked.disconnect()

    '''
    def add_account(self):

        username = self.ui.lineEdit_accounts_username_add.text()
        password = self.ui.lineEdit_accounts_password_add.text()
        role = self.ui.comboBox_accounts_role_add.currentText()

        if not role == "" and not username == "" and not password == "":
            

            if role == "Select role":
                QMessageBox.warning(self, "Warning", "Please select a role.")
                return

            # check if there is no similar usernmae
            query = "SELECT COUNT(*) FROM table_accounts WHERE username = ?"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            count  = result[0]

            if count is not None and count > 0:
                # If result is 1, meaning there is already an instance of the username. so return
                QMessageBox.warning(self, "Warning", "Username not available")
            
                
            else:
            
                cursor.execute("SELECT role_id FROM table_role WHERE role = ?", (role,))
                role_id = cursor.fetchone()[0]    

                cursor.execute("INSERT INTO table_accounts (username, password, role_id) VALUES (?, ?, ?)",
                    (username, password, role_id))        
                db_connect.commit()
                QMessageBox.information(self, "Success", "Account added successfully!")

                self.ui.tableWidget_accounts.clearContents()
                self.ui.tableWidget_accounts.setRowCount(0)
                self.ui.lineEdit_accounts_username_add.clear()
                self.ui.lineEdit_accounts_password_add.clear()
                self.ui.comboBox_accounts_role_add.clear()

                self.view_all_accounts()
                
                self.navigate_to_accounts_viewall()
                    
    ''' 



    def edit_account(self, user_id):
        # get edited values
  
        edited_username = self.ui.lineEdit_accounts_username_edit.text()
        edited_password = self.ui.lineEdit_accounts_password_edit.text()
        edited_role = self.ui.comboBox_accounts_role_edit.currentText()

        # check if there is no similar usernmae
        cursor.execute("SELECT COUNT(*) FROM table_accounts WHERE username = ? AND user_id <> ?", (edited_username, user_id))
        result = cursor.fetchone()


        if result is not None:
            # If result is 1, meaning there is already an instance of the username. so return
            if result[0] > 0:
                QMessageBox.warning(self, "Warning", "Username not available.")
                return
            else: 

            # execute stored procedure to update row in database
            
            
                cursor.execute("SELECT role_id FROM table_role WHERE role = ?", (edited_role,))
                edited_role_id = cursor.fetchone()[0]    

                cursor.execute("UPDATE table_accounts SET username = ?, password = ?, role_id = ? WHERE user_id = ?",
                        (edited_username, edited_password, edited_role_id, user_id))
                db_connect.commit()
                QMessageBox.information(self, "Success", "Account updated successfully!")

                self.ui.tableWidget_accounts.clearContents()
                self.ui.tableWidget_accounts.setRowCount(0)
                self.view_all_accounts()
                self.navigate_to_accounts_viewall()

        self.ui.pushButton_accounts_edit_save.clicked.disconnect()

    def delete_account(self):
        selected_row = self.ui.tableWidget_accounts.currentRow()
        if selected_row < 0:
            messageBox = QMessageBox.warning(self, "Warning", "Please select a row to delete!", QMessageBox.Ok)
            if messageBox == QMessageBox.Ok:
                self.navigate_to_accounts_viewall()
                return
            return
        
        messageBox = QMessageBox.question(self, "Delete Confirmation", "Are you sure you want to delete this account?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if messageBox == QMessageBox.Yes:

            # get user id of selected row
            user_id_item = self.ui.tableWidget_accounts.item(selected_row, 0)
            user_id = int(user_id_item.text())
            
            cursor.execute("DELETE FROM table_accounts WHERE user_id = ?", (user_id,))
            db_connect.commit()
           
            
            self.ui.tableWidget_accounts.clearContents()
    
            self.ui.tableWidget_accounts.setRowCount(0)
            self.view_all_accounts()
            self.navigate_to_accounts_viewall()
            QMessageBox.information(self, "Success", "Account deleted successfully!")
            


        else:
            pass

    def view_profile(self, user_id):
        # QMessageBox.information(self, "Success", f"user_id is {user_id}")
        
        query = """
            SELECT a.user_id, a.username, a.password, r.role
            FROM table_accounts a
            JOIN table_role r ON a.role_id = r.role_id
            WHERE user_id = ?
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        username = self.ui.lineEdit_profile_username_view.setText(result[1])
        password = self.ui.lineEdit_profile_password_view.setText(result[2])
        role = self.ui.lineEdit_profile_role_view.setText(result[3])


        self.ui.lineEdit_profile_username_view.setReadOnly(True)
        self.ui.lineEdit_profile_password_view.setReadOnly(True)
        self.ui.lineEdit_profile_role_view.setReadOnly(True)

        self.ui.lineEdit_profile_password_view.setEchoMode(QLineEdit.Password)

        self.ui.pushButton_profile_edit.clicked.connect(lambda: self.navigate_to_profile_edit(user_id))

        

    #_____PROFILE_____
    # function to navigatet to view (can also be used to cancel edit)
    def navigate_to_profile_view(self):
        self.ui.stackedWidget_profile.setCurrentIndex(0)
        self.ui.pushButton_profile_edit.setChecked(False)

    def navigate_to_profile_edit(self, user_id):

        # QMessageBox.information(self, "Success", f"user_id is {user_id}")

        query = """
            SELECT a.user_id, a.username, a.password, r.role
            FROM table_accounts a
            JOIN table_role r ON a.role_id = r.role_id
            WHERE user_id = ?
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()


        # Populate fields with current values
        self.ui.lineEdit_profile_username_edit.setText(result[1])
        self.ui.lineEdit_profile_password_edit.setText(result[2])


        query = "SELECT role_id FROM table_accounts WHERE user_id = ?"
        result_role = cursor.execute(query, (user_id,)).fetchone()

        if result_role is not None:
            if result_role[0] == 1:
                self.design_edit_profile_admin()

            elif result_role[0] == 2:
                self.design_edit_profile_cashier()

        self.ui.comboBox_profile_role_edit.setCurrentText(result[3])
        

        self.ui.stackedWidget_profile.setCurrentIndex(1)
        self.ui.buttonGroup_profile_edit.setExclusive(False)
        for button in self.ui.buttonGroup_profile_edit.buttons():
            button.setChecked(False)
        

        self.ui.pushButton_profile_edit_save.clicked.connect(lambda: self.edit_profile(user_id))



    def design_edit_profile_admin(self):
        self.ui.comboBox_profile_role_edit.clear()
        self.ui.comboBox_profile_role_edit.addItem("Select role")
        cursor.execute('SELECT role FROM table_role')
        data = cursor.fetchall()
        
        # populate comboBox with data from SQL query
        for role in data:
            self.ui.comboBox_profile_role_edit.addItem(role[0])
        model = QStandardItemModel()
        delegate = QStyledItemDelegate()
        for i in range(self.ui.comboBox_profile_role_edit.count()):
            item = QStandardItem(self.ui.comboBox_profile_role_edit.itemText(i))
            if i == 0:
                item.setEnabled(False)  # Disable "Select role" item
            model.appendRow(item)
        self.ui.comboBox_profile_role_edit.setModel(model)
        self.ui.comboBox_profile_role_edit.setItemDelegate(delegate)

    def design_edit_profile_cashier(self):
        self.ui.comboBox_profile_role_edit.clear()
        self.ui.comboBox_profile_role_edit.addItem("Select role")
        cursor.execute('SELECT role FROM table_role')
        data = cursor.fetchall()
        
        # populate comboBox with data from SQL query
        for role in data:
            self.ui.comboBox_profile_role_edit.addItem(role[0])
        model = QStandardItemModel()
        delegate = QStyledItemDelegate()
        for i in range(self.ui.comboBox_profile_role_edit.count()):
            item = QStandardItem(self.ui.comboBox_profile_role_edit.itemText(i))
            if i == 0 or i == 1:
                item.setEnabled(False)  # Disable "Select role" item
            model.appendRow(item)
        self.ui.comboBox_profile_role_edit.setModel(model)
        self.ui.comboBox_profile_role_edit.setItemDelegate(delegate)



    def edit_profile(self, user_id):
        # get edited values
        # QMessageBox.information(self, "Success", f"user_id: {user_id}")

        edited_username = self.ui.lineEdit_profile_username_edit.text()
        edited_password = self.ui.lineEdit_profile_password_edit.text()
        edited_role = self.ui.comboBox_profile_role_edit.currentText()

        # check if there is no similar usernmae
        cursor.execute("SELECT COUNT(*) FROM table_accounts WHERE username = ? AND user_id <> ?", (edited_username, user_id))
        result = cursor.fetchone()


        if result is not None:
            # If result is 1, meaning there is already an instance of the username. so return
            if result[0] > 0:
                QMessageBox.warning(self, "Warning", "Username not available.")
                return
            else: 

            # execute stored procedure to update row in database
            
            
                cursor.execute("SELECT role_id FROM table_role WHERE role = ?", (edited_role,))
                edited_role_id = cursor.fetchone()[0]    

                cursor.execute("UPDATE table_accounts SET username = ?, password = ?, role_id = ? WHERE user_id = ?",
                        (edited_username, edited_password, edited_role_id, user_id))
                db_connect.commit()
                QMessageBox.information(self, "Success", "Account updated successfully!")


                self.ui.tableWidget_accounts.clearContents()
                self.ui.tableWidget_accounts.setRowCount(0)
                self.view_all_accounts()
                self.view_profile(user_id)
                self.navigate_to_profile_view()

        self.ui.pushButton_profile_edit_save.clicked.disconnect()



if __name__ == "__main__":

    # this part installs the needed font. only works when app is run as administrator
    '''
    
    import os
    import subprocess

    def install_font(font_folder):
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), font_folder)
        for filename in os.listdir(font_dir):
            if filename.endswith(".ttf"):
                font_path = os.path.join(font_dir, filename)
                try:
                    # Copy font to Fonts directory
                    subprocess.run(["cmd", "/c", "copy", font_path, "%WINDIR%\\Fonts"], check=True)

                    # Register font in Windows registry
                    subprocess.run(["reg", "add", "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts", "/v", filename, "/t", "REG_SZ", "/d", filename, "/f"], check=True)
                    subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts", "/v", filename, "/t", "REG_SZ", "/d", filename, "/f"], check=True)
                    

                except Exception as e:
                    pass

    # Usage
    font_folder = 'Font'  
    install_font(font_folder)
    '''

        
    app = QApplication(sys.argv)

    with open("style.qss", "r") as style_file:
        style_str = style_file.read()

    app.setStyleSheet(style_str)

    window = MainWindow()
    window.show()
    '''
    window.setWindowTitle("Paninda Pro: A Sari-Sari Store IMS")
    '''

    sys.exit(app.exec())