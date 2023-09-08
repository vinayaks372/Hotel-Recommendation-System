from flask import Flask, render_template, request, redirect, url_for
import csv
import pandas as pd

app = Flask(__name__)

# read data from csv file and store it in a list of dictionaries
hotels = []
users = []
with open('data.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        hotels.append(row)

with open('user.csv', mode='r') as csv_file:
    csv_read = csv.DictReader(csv_file)
    for row in csv_read:
        users.append(row)

df = pd.read_csv('user.csv')

def is_user_id_present(username, password):
    match = df[(df['userid'] == username) & (df['password'] == password)]
    return not match.empty

userrname = ""

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' not in request.form or 'password' not in request.form:
            return render_template('login.html', error='Invalid username or password.')
        username = request.form['username']
        password = request.form['password']

        # check if username and password are valid
        if is_user_id_present(username, password):
            global userrname
            userrname = username
            return redirect(url_for('index'))
            
        else:
            return render_template('signup.html')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        age = request.form['age']
        min_price = float(request.form['min_price'])
        max_price = float(request.form['max_price'])

        df1 = pd.read_csv('user.csv')
        new_row = {'userid': username, 'password': password, 'phone': phone, 'age': age, 'min_price': min_price, 'max_price': max_price}
        with open('user.csv', mode='a', newline='') as csv_file:
            fieldnames = ['userid', 'password', 'phone', 'age', 'min_price', 'max_price']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(new_row)


        df1 = df1.append(new_row, ignore_index=True)
        df1.to_csv('user.csv', index=False)
        return render_template('login.html')

@app.route('/search', methods=['POST'])
def search():
    location = request.form['location']
    # isdefault = int(request.form['default'])
    min_price = float(request.form['min_price'])
    max_price = float(request.form['max_price'])
    num_guests = int(request.form['num_guests'])
    room_type = request.form['room_type']

    filtered_hotels = []
    filtered_motels = []
    # if isdefault:
    filtered_users = []

    # check if any similar user exists
    try:
        for user in users:
            if float(user['min_price']) <= float(min_price) and float(user['max_price']) >= float(max_price):
                filtered_users.append(user)
    except:
        pass

    for hotel in hotels:
        for user in filtered_users:
            hotel1 = user['hotel1']
            hotel2 = user['hotel2']
            if hotel1 in hotel['Title']:
                filtered_motels.append(hotel)
            elif hotel2 in hotel['Title']:
                filtered_motels.append(hotel)

    for hotel in hotels:
        if location.lower() in hotel['Location'].lower() and float(hotel['Price/night']) >= min_price and float(hotel['Price/night']) <= max_price and hotel['Guests'].split(',')[0] == str(num_guests) and \
           hotel['Room type'] == room_type:
            filtered_hotels.append(hotel)

    # calculate similarity score between user inputs and each hotel
    for hotel in filtered_hotels:
        similarity_score = 0
        if location.lower() in hotel['Location'].lower():
            similarity_score += 1
        price_range = max_price - min_price
        if price_range != 0:
            price_normalized = (float(hotel['Price/night']) - min_price) / price_range #min-max normalization
            similarity_score += price_normalized
        if hotel['Guests'].split(',')[0] == str(num_guests):
            similarity_score += 1
        if hotel['Room type'] == room_type:
            similarity_score += 1

        for ht in filtered_motels:
            if hotel['Title'] in ht['Title']:
                similarity_score += 2

        hotel['similarity_score'] = similarity_score

    # sort hotels based on similarity score
    sorted_hotels = sorted(filtered_hotels, key=lambda k: float(k['similarity_score']), reverse=True)[:5]
    return render_template('results.html', hotels=sorted_hotels)

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('search'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port =8000)