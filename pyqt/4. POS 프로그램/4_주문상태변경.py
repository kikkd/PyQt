from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import QTimer
from ui import Ui_MainWindow
import datetime
import sys

orders = [
    {"menu":"에스프레소 L", "quantity":"10", "order_amount":"10000", "time":"2022-07-22 09:14", "status":"waiting"},
    {"menu":"라떼 S", "quantity":"10", "order_amount":"10000", "time":"2022-07-22 09:14", "status":"waiting"},
    {"menu":"아메리카노 M", "quantity":"10", "order_amount":"10000", "time":"2022-07-22 09:14", "status":"processing"},
    {"menu":"에스프레소 S", "quantity":"10", "order_amount":"10000", "time":"2022-07-22 09:14", "status":"delivery"},
    {"menu":"에스프레소 M", "quantity":"10", "order_amount":"10000", "time":"2022-07-22 09:14", "status":"done"},
]

menu_widgets=[
    "radio_espresso",
    "radio_americano",
    "radio_latte",
    "radio_mocha",
    "radio_choco_smoothie",
    "radio_strawberry_smoothie",
]

size_widgets=[
    "radio_size_s",
    "radio_size_m",
    "radio_size_l",
    "radio_size_xl",
]


class MainWindow(QMainWindow):
    quantity_lock = False
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.timer = QTimer()
        self.timer.setInterval(990)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        self.load()
        
        for w in menu_widgets + size_widgets:
            widget = getattr(self.ui,w)
            widget.clicked.connect(self.calc)
        
        self.calc()

        self.ui.spin_quantity.valueChanged.connect(self.sync_quantity)
        self.ui.hs_quantity.valueChanged.connect(self.sync_quantity)
        self.ui.vs_quantity.valueChanged.connect(self.sync_quantity)
        self.ui.dial_quantity.valueChanged.connect(self.sync_quantity)

        self.ui.btn_order.clicked.connect(self.order)
        
        self.ui.table_orders.cellDoubleClicked.connect(self.change_order)

    def tick(self):
        now = datetime.datetime.now()
        self.ui.lb_now.setText(f"현재 시각 : {now}")
    
    def load(self):
        self.ui.table_orders.setRowCount(0)
        
        for d in orders:
            r = self.ui.table_orders.rowCount()
            self.ui.table_orders.insertRow(r)
            self.ui.table_orders.setItem(r,0,QTableWidgetItem(d["menu"]))
            self.ui.table_orders.setItem(r,1,QTableWidgetItem(d["quantity"]))
            self.ui.table_orders.setItem(r,2,QTableWidgetItem(d["order_amount"]))
            self.ui.table_orders.setItem(r,3,QTableWidgetItem(d["time"]))
            self.ui.table_orders.setItem(r,4,QTableWidgetItem(d["status"]))

        # lcd 주문 현황 업데이트
        self.ui.lcd_num_of_orders.display(len(orders))
        waiting = [x for x in orders if x["status"]=="waiting"]
        self.ui.lcd_num_of_orders_waiting.display(len(waiting))
        processing = [x for x in orders if x["status"]=="processing"]
        self.ui.lcd_num_of_orders_processing.display(len(processing))
        delivery = [x for x in orders if x["status"]=="delivery"]
        self.ui.lcd_num_of_orders_delivery.display(len(delivery))
        done = [x for x in orders if x["status"]=="done"]
        self.ui.lcd_num_of_orders_done.display(len(done))
        
    def calc(self):
        menu_price = {
            "에스프레소" : 1000,
            "아메리카노" : 1500,
            "라떼" : 3000,
            "모카" : 3500,
            "초코 스무디" : 5500,
            "딸기 스무디" : 5500,
        }
        size_price = {
            "S" : 0,
            "M" : 500,
            "L" : 1000,
            "XL" : 1500,
        }

        price = 0
        for w in menu_widgets:
            menu = getattr(self.ui, w)
            # menu = self.ui.radio_espresso
            # menu = self.ui.radio_americano
            if menu.isChecked():
                price = menu_price[menu.text()]
                break

        for w in size_widgets:
            size = getattr(self.ui, w)
            if size.isChecked():
                price += size_price[size.text()]
                break
        
        quantity = self.ui.spin_quantity.value()
        price = price * quantity

        self.ui.lb_order_amount.setText(f"총 주문 금액 : {price}원")
        
        return price

    def sync_quantity(self):
        if self.quantity_lock:
            return
        self.quantity_lock =  True
        spin = self.ui.spin_quantity
        hs = self.ui.hs_quantity
        vs = self.ui.vs_quantity
        dial = self.ui.dial_quantity
        # 사용자는 4개중 1개의 값만 변경이 가능
        values = [spin.value(),hs.value(),vs.value(),dial.value()]
        dup = {}
        target = 0
        for v in values:
            dup[v]= dup.get(v,0)+1
        for k,v in dup.items():
            if v == 1:
                target = k
        spin.setValue(target)
        hs.setValue(target)
        vs.setValue(target)
        dial.setValue(target)

        self.calc()

        self.quantity_lock = False
    
    def order(self):
        menu = ""
        for w in menu_widgets:
            radio = getattr(self.ui,w)
            if radio.isChecked():
                menu=radio.text()
                break
        
        for w in size_widgets:
            radio = getattr(self.ui,w)
            if radio.isChecked():
                menu += " "+radio.text()
                break
        
        quantity = self.ui.spin_quantity.value()

        order = {
            "menu" : menu,
            "quantity" : str(quantity),
            "order_amount" : str(self.calc()),
            "time" : str(datetime.datetime.now()),
            "status" : "waiting",

        }

        orders.append(order)
        mb = QMessageBox()
        mb.setText("발주 되었습니다.")
        mb.exec()

        self.load()

    def change_order(self,r,c):
        # waiting, processing, delivery, done
        status = ["waiting", "processing", "delivery", "done", "done"] # orders[r]["status"]에 status + 1을 해주기 때문에 done이 하나 더 들어감
        # orders_status = orders[r]["status"]
        # idx_orders_status = status.index(orders_status)
        # orders[r]["status"] = status[idx_orders_status+1]
        
        orders[r]["status"] = status[status.index(orders[r]["status"])+1]
        self.load()
        

if __name__ == "__main__":
    app = QApplication()

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())