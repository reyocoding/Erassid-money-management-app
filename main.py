import datetime, uuid, os, pandas as pd
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList
from kivy.core.window import Window
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDRoundFlatButton
from kivymd.uix.screen import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.lang.builder import Builder
from functools import partial

# Set app window size (mobile size)
Window.size = (360, 600)
dialog_helper = """
MDBoxLayout:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "100dp"

    MDTextField:
        id: amount_field
        hint_text: "Enter amount"
        helper_text: "Enter the amount please"
        helper_text_mode: "on_focus"
        icon_right: "cash"
    
    MDTextField:
        id: details_field
        hint_text: "add describtion ?"
        helper_text_mode: "on_focus"
    
    
"""

dialog_details_hlper = """
MDBoxLayout:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDBoxLayout:
        size_hint_y: None
        height: "40dp"
        MDLabel:
            text: "Transaction date:"
            halign: "left"
        MDLabel:
            id: trans_date
            text: ""
            halign: "right"
    
    MDBoxLayout:
        size_hint_y: None
        height: "40dp"
        MDLabel:
            text: "Details:"
            halign: "left"
        MDLabel:
            id: details_text
            text: ""
            halign: "right"
"""

class MainWidget(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.9, 0.9, 0.9, 1)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (165, 300)
        self.pos_hint = {"center_x": 0.3, "center_y": 0.7}  
        self.dialog = None
        self.current_side_dialog = None
        self.selected_transactions = []
        self.selected_transaction_ids_csv = []

        # Upper section code name
        self.top_box = MDBoxLayout(
            pos_hint = {"center_x": 0.5, "center_y": 0.5}
        )
        self.pen_mode = False

        self.edit_icon = MDIconButton(
            id ="EDIT_CHECK_ICON",
            icon = "pen",
            on_release = self.Trigger_edit,
            size=(40, 40),
            pos_hint={"x":1,"center_y": 0.5}
        )
        
        self.code_label = MDLabel(
            text="H",
            halign="center",
            size_hint_x=0.8
        )
        self.top_box.add_widget(self.code_label)
        self.top_box.add_widget(self.edit_icon)

        # Middle section (Debit | credit)
        self.middle_box = MDBoxLayout(size_hint_y=None, height=40)
        self.debit_label = MDLabel(text="Debit", halign="center")
        self.credit_label = MDLabel(text="credit", halign="center")
        self.middle_box.add_widget(self.debit_label)
        self.middle_box.add_widget(self.credit_label)

        # Horizontal line
        self.horizontal_line = MDBoxLayout(md_bg_color=(0, 0, 1, 1), size_hint_y=None, height=2)

        # Bottom section with vertical line
        self.bottom_box = MDBoxLayout(size_hint_y=None, height=198)

        # Left and right sections for transactions
        self.left_section = MDBoxLayout(orientation="vertical")
        self.right_section = MDBoxLayout(orientation="vertical")

        # Initialize MDList and ScrollView for Debit transactions
        self.list_view_left = MDList()
        self.scroll_left = ScrollView()
        self.scroll_left.add_widget(self.list_view_left)
        self.list_view_right = MDList()
        self.scroll_right = ScrollView()
        self.scroll_right.add_widget(self.list_view_right)

        # Vertical Line
        self.vertical_line = MDBoxLayout(md_bg_color=(0, 0, 1, 1), size_hint_x=None, width=2)

        # Initialize transaction lists
        self.debit_transactions = []
        self.credit_transactions = []
        self.debit_widgets = []
        self.credit_widgets = []

        # Construct bottom box
        self.bottom_box.add_widget(self.scroll_left)
        self.bottom_box.add_widget(self.vertical_line)
        self.bottom_box.add_widget(self.scroll_right)
        
        # Add under box for buttons
        self.under_box = MDBoxLayout(size_hint_y=None, height=40, pos_hint={"center_x": 0.5, "center_y": 0.5})

        # Add everything to main layout
        self.add_widget(self.top_box)
        self.add_widget(self.middle_box)
        self.add_widget(self.horizontal_line)
        self.add_widget(self.bottom_box)
        self.add_widget(self.under_box)

    def Trigger_edit(self, obj):
        self.pen_mode = not self.pen_mode
        obj.icon = "checkbox-marked-outline" if self.pen_mode else "pen"
        self.add_rem_funds_btn(self.pen_mode)
        print(f"the pen mode is : {self.pen_mode}")
        
    def add_rem_funds_btn(self, pen_mode):
        def button_make(Text, side):
            button_layout = MDBoxLayout(
                size_hint_y=None,
                size_hint_x=1,
                height=30,
                md_bg_color=(0.9, 0.9, 0.9, 1),  # Fixed color instead of random
                padding=[5, 0])
            button = MDRectangleFlatButton(
                text=Text,
                size_hint_y=None,
                size_hint_x=1,
                height=30,
                on_release=lambda x: self.dialog_pop_up(side),
                md_bg_color=(0.9, 0.9, 0.9, 1),  # Fixed color instead of random
                padding=[5, 0])
            button_layout.add_widget(button)
            return button_layout
        
        self.list_view_left.clear_widgets()
        self.list_view_right.clear_widgets()
        self.under_box.clear_widgets()
        
        self.left_btn = button_make("ADD debit", "debit")
        self.right_btn = button_make("ADD credit", "credit")
        self.rm_btn = MDRectangleFlatButton(
            text="Remove",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            on_release=self.rm_dialog_pop_up
        )
        
        if pen_mode:
            self.under_box.add_widget(self.rm_btn)
            self.list_view_left.add_widget(self.left_btn)
            self.list_view_right.add_widget(self.right_btn)
        
        # Rebuild transactions with selection capability
        self.selected_transactions = []
        self.selected_transaction_ids_csv = []  # Clear selected IDs too
        for transaction in self.debit_widgets:
            self.list_view_left.add_widget(transaction)
        for transaction in self.credit_widgets:
            self.list_view_right.add_widget(transaction)

    def rm_dialog_pop_up(self, obj):
        if len(self.selected_transactions) == 0:
            return
        self.rm_dialog = MDDialog(
            title = "Remove selected transactions",
            text = "Are you sure you want to remove the selected transactions?",
            buttons=[
                MDRoundFlatButton(
                    text="Cancel",
                    on_release=lambda x: self.rm_dialog.dismiss()
                ),
                MDRoundFlatButton(
                    text = "Remove",
                    on_release = self.remove_selected_transactions
                )
            ],
        )
        self.rm_dialog.open()

    def remove_selected_transactions(self, instance):
        # Create copies to avoid modifying lists during iteration
        self.rm_dialog.dismiss()
        debit_to_remove = []
        credit_to_remove = []
        ids_to_remove = []
        
        for transaction in self.selected_transactions:
            # Get the label text (amount) from the transaction
            label = transaction.children[0]
            amount_text = label.text
            try:
                amount = float(amount_text)
                # Check if it's in debit or credit
                if transaction in self.debit_widgets:
                    debit_to_remove.append(amount)
                    self.debit_widgets.remove(transaction)
                    ids_to_remove.append(transaction.transaction_id)
                    
                elif transaction in self.credit_widgets:
                    credit_to_remove.append(amount)
                    self.credit_widgets.remove(transaction)
                    ids_to_remove.append(transaction.transaction_id)
            except ValueError:
                print(f"Error converting {amount_text} to float")
        
        # Remove from the transaction lists
        for amount in debit_to_remove:
            if amount in self.debit_transactions:
                self.debit_transactions.remove(amount)
        
        for amount in credit_to_remove:
            if amount in self.credit_transactions:
                self.credit_transactions.remove(amount)
        
        # Remove from CSV using transaction IDs
        self.remove_from_csv(ids_to_remove)

        # Clear selected transactions and rebuild the interface
        self.selected_transactions = []
        self.selected_transaction_ids_csv = []
        self.add_rem_funds_btn(self.pen_mode)
        
        # Update size
        self.update_size()

    def remove_from_csv(self, ids_to_remove):
        try:
            df = pd.read_csv('TRAN_V2.csv')
            Account = self.code_label.text
            
            # Create a mask for rows to keep (all rows where ID is not in ids_to_remove)
            mask = ~df['id'].isin(ids_to_remove)
            
            # Filter the dataframe
            df = df[mask]
            
            # Save the updated dataframe
            df.to_csv("TRAN_V2.csv", index=False)
            
        except Exception as e:
            print(f"Error removing from CSV: {e}")
        
    def add_money_using_dialog(self, side):
        print("you are going to add to the " + side)
        if self.dialog:
            amount_field = self.dialog.content_cls.ids.amount_field
            details_field = self.dialog.content_cls.ids.details_field
            details = details_field.text
            amount = amount_field.text
            transaction_id = str(uuid.uuid4())
            if amount:
                self.add_transaction(amount, side, transaction_id,details,transaction_date = None)
                self.dialog.dismiss()

    def dialog_pop_up(self, side):
        self.current_side_dialog = side
        content = Builder.load_string(dialog_helper)
        
        print("working")
        self.dialog = MDDialog(
            title=f"ADD {side}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRoundFlatButton(
                    text="Cancel",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRoundFlatButton(
                    text="add money",
                    on_release=lambda x: self.add_money_using_dialog(side)
                )
            ]
        )
        self.dialog.open()
    
    def select_transaction(self, transaction, touch):
        if not self.pen_mode:
            self.details_dialog(transaction)
            return
            
            
        if transaction in self.selected_transactions:
            self.selected_transactions.remove(transaction)
            if transaction.transaction_id in self.selected_transaction_ids_csv:
                self.selected_transaction_ids_csv.remove(transaction.transaction_id)
            # Change background color back
            transaction.md_bg_color = (0.9, 0.9, 0.9, 1)  # Fixed color
        else:
            self.selected_transactions.append(transaction)
            self.selected_transaction_ids_csv.append(transaction.transaction_id)
            # Change background color to indicate selection
            transaction.md_bg_color = (0.3, 0.3, 0.9, 1)  # Selection color
            print(f"Selected: {transaction.children[0].text}")


    def add_transaction(self, amount, side, transaction_id,details,transaction_date, csv_write=True):
        """Add a new transaction to either debit or credit side"""
        try:
            amount = float(amount) 
        except (ValueError, TypeError):
            print(f"Warning: Invalid amount '{amount}'")
            amount = 0.00

        # Create transaction box
        transaction_item = transaction_class(amount, side, transaction_id , details,transaction_date)
        
        # Bind the touch event to the transaction item itself
        transaction_item.bind(on_touch_down=lambda widget, touch: self.select_transaction(widget, touch) 
                            if widget.collide_point(*touch.pos) else None)
        
        if csv_write:    
            df = pd.read_csv("TRAN_V2.csv")
            time = datetime.datetime.now().strftime("%Y-%m-%d")
            new_transaction_dict = {
                "Account": self.code_label.text,
                "date": time,
                "type": side,
                "value": amount,
                "id": transaction_id,  # Use the passed ID
                "details": details
            }
            df.loc[len(df)] = new_transaction_dict
            df.to_csv('TRAN_V2.csv', index=False)
    
        # Add to appropriate side
        if side == "debit":
            self.list_view_left.add_widget(transaction_item)
            self.debit_transactions.append(float(amount))
            self.debit_widgets.append(transaction_item)
        else:
            self.list_view_right.add_widget(transaction_item)
            self.credit_transactions.append(float(amount))
            self.credit_widgets.append(transaction_item)

        # Update size
        self.update_size()
        
    def update_size(self):
        # Calculate needed height based on number of transactions
        needed_height = max(len(self.debit_transactions), len(self.credit_transactions)) * 30 + 40
        # Set minimum height
        needed_height = max(needed_height, 198)
        self.bottom_box.height = needed_height
        
        # Add height of other elements: top_box (~40) + middle_box (40) + horizontal_line (2) + under_box (40)
        total_height = needed_height + 122
        self.size = (self.size[0], total_height)


    def details_dialog(self, transaction):
        content = Builder.load_string(dialog_details_hlper)
        
        # Find transaction details from the CSV
        try:
            df = pd.read_csv('TRAN_V2.csv')
            transaction_row = df[df['id'] == transaction.transaction_id]
            
            if not transaction_row.empty:
                date = transaction_row['date'].values[0]
                details = transaction_row['details'].values[0] if 'details' in transaction_row.columns else "No details available"
            else:
                date = "Unknown"
                details = "Unknown"
                
            # Set the content values
            content.ids.trans_date.text = str(date)
            content.ids.details_text.text = str(details)
        except Exception as e:
            print(f"Error loading transaction details: {e}")
            content.ids.trans_date.text = "Error"
            content.ids.details_text.text = "Unable to load details"
        
        details_dialog = MDDialog(
            title=f"Transaction: {transaction.transaction_label.text}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRoundFlatButton(
                    text="Close",
                    on_release=lambda x: details_dialog.dismiss()
                )
            ]
        )
        details_dialog.open()



class transaction_class(MDBoxLayout):
    def __init__(self, amount, side, transaction_id=None,details = None, transaction_date = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint_y = None
        self.size_hint_x = 1
        self.height = 30 
        self.md_bg_color = (0.9, 0.9, 0.9, 1)  # Fixed color instead of random
        self.padding = [5, 0]
        
        # Use the provided transaction_id or generate a new one
        self.transaction_id = transaction_id if transaction_id else str(uuid.uuid4())
        self.transaction_date = transaction_date if transaction_date else "UNKOWN"
        self.details = details if details else ""
        self.priority = None

        self.transaction_label = MDLabel(
            text = str(amount),
            size_hint_x = 1,
            font_size = "10sp" if len(str(amount)) < 7 else "5sp",
            height = 30,
            halign = "left" if side == 'debit' else "right"
        )
        self.add_widget(self.transaction_label)


class MyeraApp(MDApp):
    def build(self):
        screen = Screen()
        scroll = ScrollView(size_hint=(1, 0.9), pos_hint={"center_x": 0.5, "center_y": 0.5})    

        grid = MDGridLayout(id="MAINGRID", cols=2, spacing=10, padding=10, size_hint_y=None, height=0)
        grid.bind(minimum_height=grid.setter('height'))
        
        # Read data from CSV
        def read_data():
            df = pd.read_csv("TRAN_V2.csv")

            # Group transactions by account
            accounts_dict = {}
            
            # First pass: create T-accounts for each unique account
            for account in df['Account'].unique():
                t_account = MainWidget()
                t_account.code_label.text = str(account)
                accounts_dict[account] = t_account
                grid.add_widget(t_account)
            
            # Second pass: add transactions to the appropriate T-account
            for _, row in df.iterrows():
                account_code = row["Account"]
                value_to_add = row["value"]
                transaction_date = row["date"]
                transaction_type = row["type"]
                transaction_id = row["id"]
                transaction_details = row["details"]
                
                # Get the T-account for this account code
                if account_code in accounts_dict:
                    t_account = accounts_dict[account_code]
                    
                    # Add transaction to the appropriate side, passing the ID from CSV
                    if transaction_type == "debit":
                        t_account.add_transaction(value_to_add, "debit", transaction_id,transaction_details,transaction_date, csv_write=False)
                    elif transaction_type == "credit":
                        t_account.add_transaction(value_to_add, "credit", transaction_id,transaction_details,transaction_date,csv_write=False)
            
            # Update the size of all T-accounts after adding transactions
            for t_account in accounts_dict.values():
                t_account.update_size()
            
            return list(accounts_dict.keys())
                
        acc = read_data()
        scroll.add_widget(grid)
        screen.add_widget(scroll)
        return screen
if __name__=="__main__":
    MyeraApp().run()