import re
import io
from textblob import TextBlob
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import matplotlib.pyplot as plt
import base64

def clean_text(text):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

def get_sentiment(text):
    analysis = TextBlob(clean_text(text))
    sentiment = analysis.sentiment.polarity
    if sentiment > 0:
        return "positive 😊"
    elif sentiment < 0:
        return "negative 😠"
    else:
        return "neutral 😐"

app = Flask(__name__)
app.static_folder = 'static'

def create_database():
    conn = sqlite3.connect('sentiment_analysis.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            text TEXT
            sentiment TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_data(category, text, sentiment):
    conn = sqlite3.connect('sentiment_analysis.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tweets (category, text, sentiment) VALUES (?, ?, ?)', (category, text, sentiment))
    conn.commit()
    conn.close()

sample_data = [
    {"category": "kfc", "text": "Just had the best fried chicken ever! #KFC #Delicious", "sentiment": "positive"},
    {"category": "kfc", "text": "Stuck in traffic for hours. Missed my KFC craving. Terrible day!", "sentiment": "negative"},
    {"category": "kfc", "text": "KFC's original recipe is a classic. Can't go wrong with it.", "sentiment": "positive "},
    {"category": "kfc", "text": "The service at KFC was slow today. Neutral experience.", "sentiment": "neutral"},
    {"category": "kfc", "text": "KFC's spicy wings are to die for. Always a favorite.", "sentiment": "positive"},
    {"category": "kfc", "text": "The order at KFC was messed up. Feeling frustrated.", "sentiment": "negative"},
    {"category": "kfc", "text": "Craving KFC's original recipe right now. It's comfort food.", "sentiment": "positive"},
    {"category": "kfc", "text": "Just received a KFC gift card. Exciting surprise!", "sentiment": "positive"},
    {"category": "kfc", "text": "KFC's mashed potatoes are so creamy and delicious.", "sentiment": "positive"},
    {"category": "kfc", "text": "Not in the mood for KFC today. Neutral about the menu.", "sentiment": "neutral"},

    {"category": "starbucks", "text": "Starting my day with a caramel macchiato from Starbucks. It's heavenly. #MorningDelight", "sentiment": "positive"},
    {"category": "starbucks", "text": "Starbucks has the best pumpkin spice latte. A perfect fall treat. #PumpkinSpice", "sentiment": "positive"},
    {"category": "starbucks", "text": "Chilling at Starbucks with a good book. The ambiance is relaxing. #CoffeeTime", "sentiment": "positive"},
    {"category": "starbucks", "text": "Starbucks' baristas always make my day with their friendly smiles. #GreatService", "sentiment": "positive"},
    {"category": "starbucks", "text": "Starbucks' coffee is a little piece of heaven. Can't get enough. #CoffeeLover", "sentiment": "positive"},
    {"category": "starbucks", "text": "The aroma at Starbucks is so comforting. It's my happy place. #Comforting", "sentiment": "positive"},
    {"category": "starbucks", "text": "Starbucks' frappuccinos are the perfect treat on a hot day. #Refreshing", "sentiment": "positive"},
    {"category": "starbucks", "text": "Tried the new seasonal drink at Starbucks today, and it's delicious. #NewFavorite", "sentiment": "positive"},
    {"category": "starbucks", "text": "Starbucks' espresso shots are a lifesaver during busy workdays. #EnergyBoost", "sentiment": "positive"},
    {"category": "starbucks", "text": "A caramel frappuccino from Starbucks is pure bliss. #TreatYourself", "sentiment": "positive"},
    {"category": "starbucks", "text": "Starbucks messed up my order again. They need to improve their accuracy. #Disappointed", "sentiment": "negative"},
    {"category": "starbucks", "text": "Overpriced coffee at Starbucks. I can find better options elsewhere. #Overpriced", "sentiment": "negative"},
    {"category": "starbucks", "text": "I have a neutral opinion about Starbucks. It's convenient, but not always exceptional. #NeutralOpinion", "sentiment": "neutral"},

    {"category": "h&m", "text": "Just scored a great deal at H&M. Love their sales! #GreatDeal", "sentiment": "positive"},
    {"category": "h&m", "text": "H&M's clothing is stylish and affordable. Always a great choice. #Stylish", "sentiment": "positive"},
    {"category": "h&m", "text": "H&M's dresses are perfect for any occasion. #Fashionable", "sentiment": "positive"},
    {"category": "h&m", "text": "Spent the whole day shopping at H&M. So many options! #RetailTherapy", "sentiment": "positive"},
    {"category": "h&m", "text": "H&M's accessories are on point. Loved the jewelry! #Accessories", "sentiment": "positive"},
    {"category": "h&m", "text": "Can't get enough of H&M's jeans. They fit perfectly. #DenimLove", "sentiment": "positive"},
    {"category": "h&m", "text": "H&M's winter collection is a must-see. Ready for the cold season! #WinterFashion", "sentiment": "positive"},
    {"category": "h&m", "text": "H&M's sale is a shopper's paradise. Got some fantastic deals. #Sale", "sentiment": "positive"},
    {"category": "h&m", "text": "H&M's quality is unbeatable for the price. Great value. #ValueForMoney", "sentiment": "positive"},
    {"category": "h&m", "text": "Disappointed with H&M's customer service. They need to improve. #CustomerService", "sentiment": "negative"},
    {"category": "h&m", "text": "H&M's latest collection doesn't meet expectations. Lack of creativity. #Disappointing", "sentiment": "negative"},
    {"category": "h&m", "text": "I have a neutral opinion about H&M. Some items are good, while others are not. #NeutralOpinion", "sentiment": "neutral"},

    {"category": "pantaloons", "text": "Pantaloons' ethnic wear is so elegant. Perfect for special occasions. #EthnicWear", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons' summer collection is elegant,vibrant and refreshing. #SummerFashion", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons is my go-to for office wear. Their collection is professional. #OfficeWear", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons' footwear section is a hidden gem. Found stylish shoes. #Footwear", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons' fitting rooms are spacious and well-lit. Great shopping experience. #FittingRooms", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons' customer service is top-notch. They truly care about their customers. #CustomerService", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons' discounts are a steal. I saved a lot of money today. #Discounts", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons' kid's section has the cutest outfits. Loved shopping for my kids. #KidsFashion", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons' formal wear is professional and stylish. Perfect for work. #FormalWear", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Pantaloons' t-shirts are so comfortable. I could wear them all day. #Comfortable", "sentiment": "positive"},
    {"category": "pantaloons", "text": "Disappointed with Pantaloons' recent collection. Not up to the mark. #Disappointing", "sentiment": "negative"},
    {"category": "pantaloons", "text": "Pantaloons' prices are too high for the quality they offer. Not worth it. #Overpriced", "sentiment": "negative"},
    {"category": "pantaloons", "text": "I have a neutral opinion about Pantaloons. Some sections are good, while others need improvement. #NeutralOpinion", "sentiment": "neutral"},

    {"category": "leo", "text": "Just watched the new Leo DiCaprio movie. What a performance! #Amazing #Talented", "sentiment": "positive"},
    {"category": "leo", "text": "Leo's acting in Inception was mind-blowing. He's a true talent! #MindBlowing", "sentiment": "positive"},
    {"category": "leo", "text": "Leonardo DiCaprio is a true legend. His movies are always a delight. #Legend", "sentiment": "positive"},
    {"category": "leo", "text": "Can't get enough of Leo's movies. He's one of my favorite actors. #FavoriteActor", "sentiment": "positive"},
    {"category": "leo", "text": "Leo's movies always leave a lasting impression. His talent is unmatched. #Impression", "sentiment": "positive"},
    {"category": "leo", "text": "Celebrating Leo's birthday by watching his classics. He's an icon! #Icon", "sentiment": "positive"},
    {"category": "leo", "text": "Leonardo DiCaprio's versatility is unmatched. He excels in every role. #Versatile", "sentiment": "positive"},
    {"category": "leo", "text": "The Revenant wouldn't be the same without Leo. He carried the movie. #TheRevenant", "sentiment": "positive"},
    {"category": "leo", "text": "Leo's Oscar win was well-deserved. He's a phenomenal actor. #OscarWinner", "sentiment": "positive"},
    {"category": "leo", "text": "Watching Titanic, and Leo's charm still gets me. #Titanic #Charming", "sentiment": "positive"},
    {"category": "leo", "text": "I found Leo's recent movie to be disappointing. It didn't meet my expectations. #Disappointing", "sentiment": "negative"},
    {"category": "leo", "text": "Leo's acting can be overrated at times. Not all his movies are great. #Overrated", "sentiment": "negative"},
    {"category": "leo", "text": "I have a neutral opinion about Leo's movies. Some I like, some I don't. #NeutralOpinion", "sentiment": "neutral"},

    {"category": "vikram", "text": "Vikram's dedication to his roles is inspiring. Such a talented actor! #Dedication #Inspiring", "sentiment": "positive"},
    {"category": "vikram", "text": "Vikram's latest movie is a cinematic masterpiece. A must-watch! #Masterpiece", "sentiment": "positive"},
    {"category": "vikram", "text": "Vikram's versatility as an actor is unparalleled. He can do it all! #Versatile", "sentiment": "positive"},
    {"category": "vikram", "text": "The way Vikram transforms for his roles is incredible. He's a chameleon on screen. #Transformation", "sentiment": "positive"},
    {"category": "vikram", "text": "Vikram's performance in Anniyan was mind-blowing. He owned that character! #Anniyan", "sentiment": "positive"},
    {"category": "vikram", "text": "Celebrating Vikram's acting legacy. He's left a mark on the industry. #ActingLegacy", "sentiment": "positive"},
    {"category": "vikram", "text": "Vikram's acting is pure magic on screen. He brings characters to life. #Magic", "sentiment": "positive"},
    {"category": "vikram", "text": "I was disappointed with Vikram's recent movie. It didn't live up to the hype. #Disappointed", "sentiment": "negative"},
    {"category": "vikram", "text": "Vikram's acting can be hit or miss. Some roles suit him better than others. #HitOrMiss", "sentiment": "negative"},
    {"category": "vikram", "text": "I haven't formed a strong opinion about Vikram's acting. He's just okay. #NeutralOpinion", "sentiment": "neutral"},

    {"category": "samsung flip", "text": "The Samsung Flip is a game-changer for presentations. So innovative! #SamsungFlip", "sentiment": "positive"},
    {"category": "samsung flip", "text": "Just got my hands on the Samsung Flip, and it's amazing. #Impressed", "sentiment": "positive"},
    {"category": "samsung flip", "text": "The Samsung Flip simplifies collaboration. Our team loves it! #Collaboration", "sentiment": "positive"},
    {"category": "samsung flip", "text": "Samsung Flip's design is sleek and modern. It looks great in our office. #Design", "sentiment": "positive"},
    {"category": "samsung flip", "text": "The Samsung Flip's touch screen is so responsive. It makes our meetings smoother. #TouchScreen", "sentiment": "positive"},
    {"category": "samsung flip", "text": "The Samsung Flip has revolutionized our meetings. No more old whiteboards! #Meetings", "sentiment": "positive"},
    {"category": "samsung flip", "text": "The Samsung Flip's whiteboard feature is genius. We can brainstorm like pros. #Whiteboard", "sentiment": "positive"},
    {"category": "samsung flip", "text": "I find the Samsung Flip to be overpriced for what it offers. #Overpriced", "sentiment": "negative"},
    {"category": "samsung flip", "text": "Our Samsung Flip keeps having technical issues. It's frustrating! #TechnicalIssues", "sentiment": "negative"},
    {"category": "samsung flip", "text": "I'm not sure if the Samsung Flip is worth the investment. #Uncertain", "sentiment": "neutral"},

    {"category": "airpods", "text": "Airpods' sound quality is fantastic! I'm in audio heaven. #Airpods", "sentiment": "positive"},
    {"category": "airpods", "text": "I lost my Airpods again. Ugh, I can't believe it. #LostAirpods", "sentiment": "negative"},
    {"category": "airpods", "text": "Airpods' battery life is impressive. They last all day! #BatteryLife", "sentiment": "positive"},
    {"category": "airpods", "text": "Jamming to my favorite tunes with Airpods. It's a great way to start the day! #Music", "sentiment": "positive"},
    {"category": "airpods", "text": "Airpods keep falling out of my ears during workouts. So annoyingWorkoutProblems", "sentiment": "negative"},
    {"category": "airpods", "text": "The convenience of Airpods is unbeatable. No more tangled wires! #Convenience", "sentiment": "positive"},
    {"category": "airpods", "text": "Airpods' noise cancellation is a game-changer. I'm in my own world! #NoiseCancellation", "sentiment": "positive"},
    {"category": "airpods", "text": "Can't leave the house without my Airpods. They're an essential part of my day! #Essential", "sentiment": "positive"},
    {"category": "airpods", "text": "I can't justify the high price of Airpods. There are cheaper alternatives. #Expensive", "sentiment": "negative"},
    {"category": "airpods", "text": "Airpods are worth every penny. The quality is outstanding! #WorthIt", "sentiment": "positive"},

    {"category": "amazon", "text": "Amazon's same-day delivery saved my day. So convenient! #AmazonPrime", "sentiment": "positive"},
    {"category": "amazon", "text": "I received a damaged product from Amazon. Their quality control is terrible. #AmazonFail", "sentiment": "negative"},
    {"category": "amazon", "text": "I'm neutral about Amazon's product variety. It's decent but not extraordinary.", "sentiment": "neutral"},
    {"category": "amazon", "text": "Ordering from Amazon is always hassle-free. Love their service! #AmazonShopping", "sentiment": "positive"},
    {"category": "amazon", "text": "Amazon's customer service is unhelpful and slow to respond. Very disappointed. #CustomerService", "sentiment": "negative"},
    {"category": "amazon", "text": "I found a fantastic deal on Amazon today. Incredible savings! #AmazonDeals", "sentiment": "positive"},
    {"category": "amazon", "text": "Amazon's tech gadgets are innovative and cutting-edge. Love their products! #Tech", "sentiment": "positive"},
    {"category": "amazon", "text": "Amazon's book selection is a bookworm's paradise. So many options! #BookLover", "sentiment": "positive"},
    {"category": "amazon", "text": "I had to return a product, and Amazon's return policy was straightforward and efficient. #Returns", "sentiment": "positive"},
    {"category": "amazon", "text": "Amazon's recommendations are usually accurate. They know my taste! #AmazonRecommendations", "sentiment": "positive"},
    
    {"category": "walmart", "text": "Just got the best deals at Walmart today. #ShoppingSpree", "sentiment": "positive"},
    {"category": "walmart", "text": "Walmart's customer service is terrible. Never shopping there again.", "sentiment": "negative"},
    {"category": "walmart", "text": "I'm neutral about Walmart's prices. They're not the best, but not the worst.", "sentiment": "neutral"},
    {"category": "walmart", "text": "Walmart's online ordering is so convenient. Love it!", "sentiment": "positive"},
    {"category": "walmart", "text": "The long lines at Walmart are frustrating. Such a waste of time.", "sentiment": "negative"},
    {"category": "walmart", "text": "Just found some great clearance items at Walmart. Amazing deals!", "sentiment": "positive"},
    {"category": "walmart", "text": "Walmart's produce section is disappointing. Not fresh at all.", "sentiment": "negative"},
    {"category": "walmart", "text": "I'm indifferent about Walmart's selection. It's average.", "sentiment": "neutral"},
    {"category": "walmart", "text": "Walmart's pharmacy staff is always helpful. Grateful for their assistance.", "sentiment": "positive"},
    {"category": "walmart", "text": "Walmart's Black Friday sales are the best. Can't wait for this year's deals!", "sentiment": "positive"},

]


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/category')
def category():
    return render_template("category.html")

@app.route('/select_category', methods=['POST'])
def select_category():
    selected_category = request.form['category']
    if selected_category in ["kfc", "starbucks", "h&m", "pantaloons", "leo", "vikram", "samsung flip", "airpods", "amazon", "walmart"]:
        return redirect(url_for('graph', category=selected_category))
    else:
        return "Invalid category"

@app.route('/graph/<category>')
def graph(category):
    conn = sqlite3.connect('sentiment_analysis.db')
    cursor = conn.cursor()
    cursor.execute('SELECT sentiment, COUNT(sentiment) FROM tweets WHERE category = ? GROUP BY sentiment', (category,))
    data = cursor.fetchall()
    conn.close()

    sentiments = ["positive", "neutral", "negative"]
    sentiment_data = {sentiment: 0 for sentiment in sentiments}

    for row in data:
        sentiment, count = row
        sentiment_data[sentiment] = count

    labels = sentiments
    values = [sentiment_data[sentiment] for sentiment in sentiments]

    plt.figure(figsize=(8, 4))
    plt.bar(labels, values, color=['green', 'gray', 'red'])
    plt.title(f'Sentiment Analysis for {category}')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_data = base64.b64encode(buffer.read()).decode()
    plt.close()

    return render_template("graph.html", category=category, image_data=image_data)

@app.route("/predict", methods=['POST', 'GET'])
def pred():
    if request.method == 'POST':
        query = request.form['query']
        count = int(request.form['num'])

        conn = sqlite3.connect('sentiment_analysis.db')
        cursor = conn.cursor()
        cursor.execute('SELECT text, sentiment FROM tweets WHERE text LIKE ? LIMIT ?', ('%' + query + '%', count))
        fetched_tweets = [{'text': row[0], 'sentiment': row[1]} for row in cursor.fetchall()]
        conn.close()

        return render_template('result.html', result=fetched_tweets)

@app.route("/predict1", methods=['POST', 'GET'])
def pred1():
    if request.method == 'POST':
        text = request.form['txt']
        sentiment = get_sentiment(text)
        return render_template('result1.html', msg=text, result=sentiment)

if __name__ == '__main__':
    create_database()
    for data in sample_data:
        insert_data(data["category"], data["text"], data["sentiment"])
    app.debug = True
    app.run(host='localhost', port=5000)
