# Resumex
Resumex is an App that allows you to compute similarity between a job offer and resumes in order to save time and select best applicants.<br>
You can find a ligth [word2vec](https://code.google.com/archive/p/word2vec/) pre-trained Google News model here: [(GoogleNews-vectors-negative300)](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM)<br>
Live demo availaible here : http://resumx.herokuapp.com/.<br>
Find some exemples in the /exemple folder and test with the existing job offer.<br>
Purchase tha App (Fake functionnality with Stripe : https://stripe.com/docs/testing) if you want to add you own job offers.<br>
<br>
<p align="center"><img src="https://raw.githubusercontent.com/ansa-aboudou/resumex/master/media/login.jpg" width="128px"><p>
<p align="center"><img src="https://raw.githubusercontent.com/ansa-aboudou/resumex/master/media/home.jpg" width="128px"><p>
<p align="center"><img src="https://raw.githubusercontent.com/ansa-aboudou/resumex/master/media/results.jpg" width="128px"><p>

## Setup
Download [(GoogleNews-vectors-negative300)](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM) and put it in root folder<br>
```
git clone https://github.com/ansa-aboudou/resumex
cd Flaskex
pip install -r requirements.txt
python app.py
```
## Credits
<br>
These repositories helped me build this project, thank you guys :) :<br>
- https://github.com/v1shwa/document-similarity<br>
- https://github.com/eyaler/word2vec-slim<br>
- https://github.com/anfederico/Flaskex<br>
