# TrkFin

Flask web-app that helps you track your finances. [Video demo on YouTube](https://www.youtube.com/watch?v=SRaubLMJzj0).

This is a final project for Harvard's [CS50x](https://cs50.harvard.edu/x/2022/).

Big thanks to Miguel Grinberg and his [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)!


## Installation and local hosting

Download code as zip or clone git repo:
```
$ git clone https://github.com/kftlfd/trkfin.git
$ cd trkfin
```

Inside project folder create python virtual environment and install dependencies:
```
$ python3 -m venv trkfin-venv
$ source trkfin-venv/bin/activate
(trkfin-venv) $ pip install -r requirements.txt
```

Make sure your virtual environment is enabled and run app:
```
$ source venv/bin/activate
(trkfin-venv) $ flask run
```

Now app is accessible at `http://localhost:5000/`



## License

Software is released under the GPL-3.0, see LICENSE.txt for full text, or TL;DR [here](https://gist.github.com/kn9ts/cbe95340d29fc1aaeaa5dd5c059d2e60).
