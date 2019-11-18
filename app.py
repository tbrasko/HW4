from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
import secrets
import os

dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbname = os.environ.get('DBNAME')


conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser,dbpass,dbhost,dbname)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class tbrasko_players(db.Model):
    playerId = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    hometown = db.Column(db.String(255))
    team = db.Column(db.String(255))
    player_number = db.Column(db.Integer)

class PlayerForm(FlaskForm):
    playerId = IntegerField('Player ID:')
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    hometown = StringField('Hometown:', validators=[DataRequired()])
    team = StringField('Team:', validators=[DataRequired()])
    player_number = IntegerField('Player Number:', validators=[DataRequired()])



@app.route('/')
def index():
    all_players = tbrasko_players.query.all()
    return render_template('index.html', players = all_players, pageTitle='Soccer Players')

@app.route('/player/new', methods=['GET', 'POST'])
def add_player():
    form = PlayerForm()
    if form.validate_on_submit():
        player = tbrasko_players(first_name=form.first_name.data, last_name=form.last_name.data, hometown=form.hometown.data, team=form.team.data, player_number=form.player_number.data)
        db.session.add(player)
        db.session.commit()
        return redirect('/')

    return render_template('add_player.html', form=form, pageTitle='Add A New Player', legend='Add a new Player')

@app.route('/player/<int:player_id>', methods=['GET', 'POST'])
def player(player_id):
    player = tbrasko_players.query.get_or_404(player_id)
    return render_template('player.html', form=player, pageTitle='Player Details')


@app.route('/player/<int:player_id>/delete', methods=['POST'])
def delete_player(player_id):
    if request.method == 'POST':
        player = tbrasko_players.query.get_or_404(player_id)
        db.session.delete(player)
        db.session.commit()
        flash('Player was successfully deleted!')
        return redirect("/")
    else:
        return redirect("/")

@app.route('/player/<int:player_id>', methods=['GET', 'POST'])
def get_player(player_id):
    player = tbrasko_players.query.get_or_404(player_id)
    return render_template('player.html', form=player, pageTitle='Player Details', legend="Player Details")

@app.route('/player/<int:player_id>/update', methods=['GET','POST'])
def update_player(player_id):
    player = tbrasko_players.query.get_or_404(player_id)
    form = PlayerForm()
    if form.validate_on_submit():
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        player.hometown= form.hometown.data
        player.team = form.team.data
        player.player_number = form.player_number.data
        db.session.commit()
        return redirect(url_for('get_player', player_id=player.playerId))
    #elif request.method == 'GET':
    form.first_name.data = player.first_name
    form.last_name.data = player.last_name
    form.hometown.data = player.hometown
    form.team.data = player.team
    form.player_number.data = player.player_number
    return render_template('update_player.html', form=form, pageTitle='Update Player',
                            legend="Update A Player")
@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['search_string']
        search = "%{0}%".format(search_value)
        results = tbrasko_players.query.filter(tbrasko_players.first_name.like(search)).all()
        return render_template('index.html', players=results, pageTitle='Soccer Players', legend="Search Results")
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)