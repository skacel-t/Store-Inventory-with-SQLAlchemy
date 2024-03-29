from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
import csv

engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    product_name = Column('Product', String)
    product_quantity = Column('Quantity', Integer)
    product_price = Column('Price', Integer)
    date_updated = Column('Date Updated', Date)

    def __repr__(self):
        return (f"{self.product_id} | {self.product_name} | {self.product_quantity} "
                f"| {self.product_price} | {self.date_updated}")


# Let's begin with the functions that will be used in the app
def clean_quantity(quantity_str):
    return_quantity = int(quantity_str)
    return return_quantity


def clean_price(price_str):
    price = price_str[1:]
    price = float(price)*100
    price = round(price, 0)
    price = int(price)
    return price


def clean_date(date_str):
    date = date_str.split("/")
    day = int(date[1])
    month = int(date[0])
    year = int(date[2])
    return_date = datetime.date(year, month, day)
    return return_date


def clean_id(id_str, id_options):
    try:
        id_int = int(id_str)
    except ValueError:
        input("\nInvalid input, please enter a number from the ID options. \nPress enter to try again.")
        return None
    else:
        if id_int in id_options:
            return id_int
        else:
            input(
                "\nThere is no product associated with this ID. "
                "\nPlease choose an ID from the ID Options. \nPress enter to try again.")
            return None


def menu():
    while True:
        print("""
            \r------- STORE INVENTORY -------
            \r1) Enter 'v' to view a product
            \r2) Enter 'a' to add a new product
            \r3) Enter 'b' to make a backup of the database
            \r4) Enter 'q' to exit
            \r-------------------------------""")
        choice = input("What would you like to do?  ")
        choice = choice.lower()
        if choice in ['v', 'a', 'b', 'q']:
            return choice
        else:
            input("\nInvalid input! Please enter 'v', 'a', 'b', or 'q'. \nPress enter to try again.")


def display_product(id_num):
    product = session.query(Product).filter(Product.product_id == id_num).first()
    formatted_date = product.date_updated.strftime("%B %d, %Y")
    print(f"""
        \rProduct: {product.product_name}
        \rQuantity: {product.product_quantity}
        \rPrice: ${product.product_price / 100}
        \rDate Updated: {formatted_date}""")


def add_product():
    print("")
    while True:
        name = input("Product name:  ")
        if name == "":
            print("Invalid input. The product must be given a name.")
        else:
            break
    while True:
        try:
            quantity = input("Quantity:  ")
            quantity = int(quantity)
        except ValueError:
            print("Invalid input. Please enter a whole number.")
        else:
            break
    while True:
        try:
            price = input("Price:  ")
            price = float(price)*100
            price = round(price, 0)
            price = int(price)
        except ValueError:
            print("Invalid input. Please enter a number without including the currency symbol. \nFor example, '10.99'.")
        else:
            break
    date = datetime.date.today()
    # check for duplicate
    product_in_db = session.query(Product).filter(Product.product_name == name).one_or_none()
    if product_in_db is None:
        new_product = Product(product_name=name, product_quantity=quantity, product_price=price, date_updated=date)
        session.add(new_product)
        input("New product added! Press enter to return to menu.")
    else:
        product_in_db.product_quantity = quantity
        product_in_db.product_price = price
        product_in_db.date_updated = date
        input("Existing product info updated! Press enter to return to menu.")
    session.commit()


def backup():
    with open("backup.csv", "w") as csvfile:
        fieldnames = ["product_name", "product_price", "product_quantity", "date_updated"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in session.query(Product):
            upload_data = {'product_name': product.product_name, 'product_quantity': product.product_quantity,
                           'product_price': f"${product.product_price / 100}"}
            day = product.date_updated.day
            month = product.date_updated.month
            year = product.date_updated.year
            upload_data['date_updated'] = f"{month}/{day}/{year}"
            writer.writerow(upload_data)


def add_csv():
    with open("inventory.csv", newline="") as csvfile:
        data = csv.reader(csvfile, delimiter=",")
        rows = list(data)
        for row in rows[1:]:
            name = row[0]
            quantity = clean_quantity(row[2])
            price = clean_price(row[1])
            date = clean_date(row[3])
            product_in_db = session.query(Product).filter(Product.product_name == name).one_or_none()
            if product_in_db is None:
                product = Product(product_name=name, product_quantity=quantity, product_price=price, date_updated=date)
                session.add(product)
                session.commit()
            else:
                # if we have a more recent date, we overwrite the data...
                date_in_db = product_in_db.date_updated
                if date > date_in_db:
                    product_in_db.product_quantity = quantity
                    product_in_db.product_price = price
                    product_in_db.date_updated = date
                    session.commit()


def app():
    while True:
        choice = menu()
        choice = choice.lower()
        if choice == 'v':
            id_options = []
            for product in session.query(Product):
                id_options.append(product.product_id)
            # while id_error
            while True:
                id_choice = input(f"""
                    \rID options: {id_options}
                    \rEnter the product ID of the item you would like to view:  """)
                id_choice = clean_id(id_choice, id_options)
                if type(id_choice) is int:
                    break
            display_product(id_choice)
            input("\nPress enter to return to menu.")
        elif choice == 'a':
            # add product
            add_product()
        elif choice == 'b':
            # create csv file backup
            backup()
            input("\nBackup has been created. Press enter to return to menu.")
        elif choice == 'q':
            print("\nGoodbye!\n")
            return None


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv()
    app()
