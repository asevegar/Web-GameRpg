from flask import Flask, render_template,request, redirect, url_for, session, jsonify
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is secret'

@app.route('/')
def index():
	if 'loggedin' in session:
		if 'id_char' in session:
			return redirect(url_for('homepage'))
		return redirect(url_for('chosechar'))
	return render_template('index.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
	if request.method == 'GET':
		if 'loggedin' in session:
			return redirect(url_for('index'))
		return render_template('signup.html')
	else:
		d_username = request.form['username']
		d_password = request.form['password']

		data = {
			"username" : d_username,
			"password" : d_password
		}

		req_link = 'http://127.0.0.1:5000/signup/'
		req = requests.post(req_link, json=data, headers={"Content-Type": "application/json"})
		if req.status_code == 200:
			return redirect(url_for('index'))
		else:
			return redirect(url_for('signup'))

@app.route("/login",methods=['GET','POST'])
def login():
	if request.method == 'GET':
		if 'loggedin' in session:
			return redirect(url_for('index'))		
		return render_template("login.html")
	else:
		d_username = request.form['username']
		d_password = request.form['password']

		url = 'http://127.0.0.1:5000/login/'

		data = {
			"username" :d_username,
			"password" :d_password
		}

		req  = requests.post(url,json=data,headers={"Content-Type": "application/json"})
		if req.status_code == 200:
			datas = req.json()['hasil']
			session['id_user'] = datas['id_user']
			session['loggedin'] = True
			return redirect(url_for('index'))
		else:
			return redirect(url_for('login'))

@app.route("/logout")
def logout():
	session.clear()
	return redirect(url_for('index'))

@app.route("/chosechar",methods=['GET','POST'])
def chosechar():
	if 'loggedin' in session:
		if 'id_char' in session:
			return redirect(url_for('homepage'))
		if request.method == 'GET':
			url = 'http://127.0.0.1:5000/character/'
			params = {"id_user" : session['id_user']}
			req = requests.get(url,params=params)
			if req.status_code == 200:
				result = req.json()['hasil']
				return render_template('chosechar.html',datas=result)
			return "Error"
		else:
			session['id_char'] = int(request.form['id_char'])
			session['nickname'] = request.form['nickname']
			session['level'] = request.form['level']
			return redirect(url_for('homepage'))
	return redirect(url_for('login'))

@app.route('/character',methods=['GET','POST'])
def character():
	if 'loggedin' in session:
		if 'id_char' in session:
			return redirect(url_for('homepage'))
		if request.method == 'GET':
			url = 'http://127.0.0.1:5000/quest/'
			req  = requests.get(url)
			if req.status_code == 200:
				req = req.json()['hasil']
				return render_template('character.html',datas=req)
			else:
				return 'Connection Error'
		else:
			nickname = request.form['nickname']
			quest = int(request.form['quest'])
			id_user = int(session['id_user'])
			id_pangkat = 3
			data = {
				'id_user' : id_user,
				'id_pangkat' : id_pangkat,
				'id_quest' : quest,
				'nickname' : nickname
			}
			url = 'http://127.0.0.1:5000/character/'
			req  = requests.post(url,json=data,headers={"Content-Type": "application/json"})
			if req.status_code == 200:
				return redirect(url_for('chosechar'))
			elif req.status_code == 400:
				req = req.json()['hasil']
				return req
			elif req.status_code == 410:
				req = req.json()['hasil']
				return req
			elif req.status_code == 409:
				req = req.json()['hasil']
				return req
			else:
				return 'Error'
	return redirect(url_for('index'))
	
@app.route('/homepage')
def homepage():
	if 'loggedin' and 'id_char' in session:
		return render_template('homepage.html')
	return redirect(url_for('index'))

@app.route('/item', methods=['GET','POST'])
def item():
	if 'loggedin' and 'id_char' and 'level' in session:
		if session['level'] == 'administrator':
			if request.method == 'GET':
				url = 'http://127.0.0.1:5000/items/'
				req = requests.get(url)
				req = req.json()['hasil']
				return render_template('item.html',hasil=req)
			else:
				nama_item = str(request.form['nama_item'])
				point = int(request.form['point'])
				
				data = {
					'nama_item' : nama_item,
					'point' : point
				}

				url = 'http://127.0.0.1:5000/items/'
				req = requests.post(url,json=data,headers={"Content-Type": "application/json"})
				if req.status_code == 201:
					return redirect(request.url)
				return redirect(request.url)
		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/delitem/<int:id_item>')
def delitem(id_item):
	if 'loggedin' and 'id_char' and 'level' in session:
		if session['level'] == 'administrator':
			id_item = id_item
			data = {
				'id_item' : id_item
			}
			url = 'http://127.0.0.1:5000/items/'

			req = requests.delete(url,json=data,headers={"Content-Type": "application/json"})
			if req.status_code == 201:
				return redirect(url_for('item'))
			else:
				return redirect(url_for('item'))

		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/updtitem',methods=['POST'])
def updtitem():
	nama_item = request.form['nama_item']
	point = int(request.form['point'])
	id_item = int(request.form['id_item'])

	data = {
		'nama_item':nama_item,
		'point':point,
		'id_item':id_item
	}

	url = 'http://127.0.0.1:5000/items/'
	req = requests.put(url,json=data,headers={"Content-Type": "application/json"})

	if req.status_code == 201:
		return redirect(url_for('item'))
	return redirect(url_for('item'))


@app.route('/maps',methods=['GET','POST'])
def maps():
	if 'loggedin' and 'id_char' and 'level' in session:
		if session['level'] == 'administrator':
			if request.method == 'GET':
				url = 'http://127.0.0.1:5000/maps/'
				req = requests.get(url)
				req = req.json()['hasil']
				return render_template('maps.html',hasil=req)
			else:
				nama_maps = request.form['nama_maps']
				data = {
					'nama_maps' : nama_maps
				}
				
				url = 'http://127.0.0.1:5000/maps/'

				req = requests.post(url,json=data,headers={"Content-Type": "application/json"})
				if req.status_code == 201:
					return redirect(request.url)
				return redirect(request.url)
		return redirect(url_for('index'))
	return redirect(url_for('index'))	

@app.route('/pangkat',methods=['GET','POST'])
def pangkat():
	if 'loggedin' and 'id_char' and 'level' in session:
		if session['level'] == 'administrator':
			if request.method == 'GET':
				url = 'http://127.0.0.1:5000/pangkat/'
				req = requests.get(url)
				req = req.json()['hasil']
				return render_template('pangkat.html',hasil=req)
			else:
				nama_pangkat = request.form['nama_pangkat']

				data = {
					'nama_pangkat' : nama_pangkat
				}

				url = 'http://127.0.0.1:5000/pangkat/'
				req = requests.post(url, json=data, headers={"Content-Type": "application/json"})
				if req.status_code == 201:
					return redirect(request.url)
				else:
					return redirect(request.url)

		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.route('/quest',methods = ['GET','POST'])
def quest():
	if 'loggedin' and 'id_char' and 'level' in session:
		if session['level'] == 'administrator':
			if request.method == 'GET':
				url = 'http://127.0.0.1:5000/quest/'
				req = requests.get(url)
				req = req.json()['hasil']
				return render_template('quest.html',hasil=req)
			else:
				nama_quest = request.form['nama_quest']

				data = {
					'nama_quest' : nama_quest
				}
				url = 'http://127.0.0.1:5000/quest/'

				req = requests.post(url,json=data,headers={"Content-Type": "application/json"})
				if req.status_code == 201:
					return redirect(request.url)
				else:
					return redirect(request.url)
		return redirect(url_for('index'))
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True,port=5001)