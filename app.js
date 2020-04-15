const express = require('express'),
	app = express(),
	bodyParser = require('body-parser'),
	mongoose = require('mongoose'),
	session = require('express-session'),
	passport = require('passport'),
	LocalStrategy = require('passport-local'),
	passportLocalMongoose = require('passport-local-mongoose');

app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

mongoose.connect('mongodb+srv://admin:qqLuPTe9fZZGo5ai@cluster0-aiymc.mongodb.net/hookup?retryWrites=true&w=majority', { useNewUrlParser: true, useUnifiedTopology: true });

app.use(
	session({
		secret: 'whatever you want',
		resave: false,
		saveUninitialized: false
	})
);

app.use(passport.initialize());
app.use(passport.session());

const userSchema = new mongoose.Schema({
	username: String,
	password: String
});

userSchema.plugin(passportLocalMongoose);

const User = mongoose.model('User', userSchema);

passport.use(new LocalStrategy({ usernameField: 'email' }, User.authenticate()));
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());

app.get('/', function(req, res) {
	res.render('register.ejs');
});

app.post('/', function(req, res) {
	User.register({ username: req.body.username }, req.body.password, function(err, user) {
		if (!err) {
			res.redirect('/');
		}
	});
});


app.listen(3001, function() {
	console.log('Server Started Sucessfully on Port 3001');
});
