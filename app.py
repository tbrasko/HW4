from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
import secrets
import os


conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser,secrets.dbpass, secrets.dbhost, secrets.dbname)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbname = os.environ.get('DBNAME')

class tbrasko_players(db.Model):
    playerId = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    hometown = db.Column(db.String(255))
    team = db.Column(db.String(255))
    player_number = db.Column(db.Integer)

class PlayerForm(FlaskForm):
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])
    hometown = StringField('Hometown:', validators=[DataRequired()])
    team = StringField('Team:', validators=[DataRequired()])
    player_number = StringField('Player Number:', validators=[DataRequired()])



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




if __name__ == '__main__':
    app.run(debug=True)