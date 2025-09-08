import random
import datetime
from faker import Faker
from sqlalchemy.orm import Session

from models import User, Address, CreditCard, SessionLocal

fake = Faker()

def generate_about_me(gender, company=None):
    """Generate a personalized 'about me' description"""

    hobbies = [
        "reading", "photography", "hiking", "cooking", "painting", "gaming",
        "gardening", "traveling", "yoga", "dancing", "writing", "music",
        "cycling", "swimming", "running", "chess", "pottery", "knitting",
        "rock climbing", "skiing", "surfing", "meditation", "volunteering",
        "astronomy", "bird watching", "fishing", "camping", "martial arts"
    ]

    personality_traits = [
        "curious", "adventurous", "creative", "analytical", "empathetic",
        "optimistic", "detail-oriented", "spontaneous", "thoughtful",
        "ambitious", "laid-back", "passionate", "resourceful", "friendly",
        "independent", "collaborative", "innovative", "patient", "energetic"
    ]

    interests = [
        "technology", "science", "history", "art", "literature", "movies",
        "sports", "nature", "culture", "food", "fashion", "architecture",
        "psychology", "philosophy", "sustainability", "fitness", "business",
        "languages", "politics", "economics", "health", "education"
    ]

    life_goals = [
        "learn new languages", "travel the world", "start my own business",
        "make a positive impact", "continue growing personally",
        "build meaningful relationships", "stay healthy and active",
        "pursue creative projects", "help others", "explore new cultures",
        "master new skills", "achieve work-life balance", "give back to community"
    ]

    selected_hobbies = random.sample(hobbies, random.randint(2, 4))
    selected_traits = random.sample(personality_traits, random.randint(1, 3))
    selected_interests = random.sample(interests, random.randint(1, 3))
    selected_goals = random.sample(life_goals, random.randint(1, 2))

    about_templates = [
        f"I'm a {', '.join(selected_traits)} person who loves {', '.join(selected_hobbies)}. I'm passionate about {' and '.join(selected_interests)} and always looking to {' and '.join(selected_goals)}.",
        f"When I'm not working{f' at {company}' if company else ''}, you can find me {selected_hobbies[0]} or {selected_hobbies[1]}. I consider myself {selected_traits[0]} and have a deep interest in {selected_interests[0]}. My goal is to {selected_goals[0]}.",
        f"Life is all about balance for me. I enjoy {', '.join(selected_hobbies[:2])} in my free time and I'm particularly interested in {selected_interests[0]}. As a {selected_traits[0]} person, I believe in {selected_goals[0]}.",
        f"I'm passionate about {selected_hobbies[0]} and {selected_hobbies[1]}, and I love exploring topics related to {selected_interests[0]}. Friends would describe me as {' and '.join(selected_traits)}. Currently focused on {selected_goals[0]}.",
        f"My interests include {', '.join(selected_hobbies[:3])} and I'm always eager to learn about {selected_interests[0]}. I'm a {selected_traits[0]} individual who values {selected_goals[0]}. Looking forward to new adventures and experiences!",
        f"As someone who's {selected_traits[0]}, I find great joy in {selected_hobbies[0]} and {selected_hobbies[1]}. I'm fascinated by {selected_interests[0]} and my current focus is on {selected_goals[0]}.",
        f"People often describe me as {' and '.join(selected_traits)}. In my spare time, I love {selected_hobbies[0]} and exploring {selected_interests[0]}. I'm working towards {selected_goals[0]}.",
        f"I believe in living life to the fullest! My hobbies include {', '.join(selected_hobbies[:2])} and I'm deeply interested in {selected_interests[0]}. Being {selected_traits[0]}, I aim to {selected_goals[0]}.",
        f"What drives me? {selected_interests[0]} and {selected_hobbies[0]}! I'm naturally {selected_traits[0]} and spend my free time {selected_hobbies[1]}. My aspiration is to {selected_goals[0]}.",
        f"I'm someone who values {selected_interests[0]} and finds peace in {selected_hobbies[0]}. My {selected_traits[0]} nature leads me to {selected_hobbies[1]}, and I'm determined to {selected_goals[0]}.",
        f"Hello! I'm a {selected_traits[0]} individual with a passion for {selected_hobbies[0]} and {selected_interests[0]}. When not {selected_hobbies[1]}, I'm usually planning to {selected_goals[0]}.",
        f"My friends know me as the {selected_traits[0]} one who's always {selected_hobbies[0]} or {selected_hobbies[1]}. I have a deep appreciation for {selected_interests[0]} and dream of {selected_goals[0]}.",
        f"Life's too short not to pursue what you love! For me, that's {selected_hobbies[0]}, {selected_interests[0]}, and {selected_hobbies[1]}. Being {selected_traits[0]}, I'm committed to {selected_goals[0]}.",
        f"I find fulfillment in {selected_hobbies[0]} and have always been drawn to {selected_interests[0]}. My {selected_traits[0]} personality helps me enjoy {selected_hobbies[1]}, and I'm working to {selected_goals[0]}.",
        f"As a {selected_traits[0]} person, I'm energized by {selected_hobbies[0]} and captivated by {selected_interests[0]}. Whether I'm {selected_hobbies[1]} or planning my next adventure, I aim to {selected_goals[0]}.",
        f"I'm passionate about creating a life filled with {selected_hobbies[0]}, {selected_interests[0]}, and meaningful connections. My {selected_traits[0]} approach to life includes {selected_hobbies[1]} and {selected_goals[0]}.",
        f"What makes me tick? A combination of {selected_hobbies[0]}, {selected_interests[0]}, and being {selected_traits[0]}. I love spending time {selected_hobbies[1]} and I'm focused on {selected_goals[0]}.",
        f"I'm drawn to {selected_interests[0]} and find joy in simple pleasures like {selected_hobbies[0]}. Being naturally {selected_traits[0]}, I also enjoy {selected_hobbies[1]} and hope to {selected_goals[0]}.",
        f"My life revolves around {selected_hobbies[0]}, {selected_interests[0]}, and being {selected_traits[0]}. Whether I'm {selected_hobbies[1]} or exploring new ideas, I'm always working towards {selected_goals[0]}.",
        f"I consider myself a {selected_traits[0]} soul who finds happiness in {selected_hobbies[0]} and {selected_hobbies[1]}. I'm particularly interested in {selected_interests[0]} and committed to {selected_goals[0]}.",
        f"There's nothing I love more than {selected_hobbies[0]} and diving deep into {selected_interests[0]}. My {selected_traits[0]} nature drives me to {selected_hobbies[1]} and pursue {selected_goals[0]}.",
        f"I'm someone who thrives on {selected_hobbies[0]} and has a genuine curiosity about {selected_interests[0]}. Being {selected_traits[0]}, I make time for {selected_hobbies[1]} while working to {selected_goals[0]}.",
        f"My world is enriched by {selected_hobbies[0]}, {selected_interests[0]}, and the joy of being {selected_traits[0]}. I love {selected_hobbies[1]} and am passionate about {selected_goals[0]}.",
        f"I'm a firm believer in following your passions - mine being {selected_hobbies[0]} and {selected_interests[0]}. As a {selected_traits[0]} person, I enjoy {selected_hobbies[1]} and strive to {selected_goals[0]}.",
        f"What defines me? My love for {selected_hobbies[0]}, fascination with {selected_interests[0]}, and {selected_traits[0]} personality. I spend my free time {selected_hobbies[1]} and am dedicated to {selected_goals[0]}.",
        f"I'm energized by {selected_hobbies[0]} and constantly learning about {selected_interests[0]}. My {selected_traits[0]} spirit leads me to {selected_hobbies[1]}, and I'm determined to {selected_goals[0]}.",
        f"Life is an adventure, and mine includes {selected_hobbies[0]}, {selected_interests[0]}, and being authentically {selected_traits[0]}. I love {selected_hobbies[1]} and am working towards {selected_goals[0]}.",
        f"I'm passionate about {selected_hobbies[0]} and have developed a deep interest in {selected_interests[0]}. Being {selected_traits[0]} by nature, I also enjoy {selected_hobbies[1]} and hope to {selected_goals[0]}.",
        f"My ideal day involves {selected_hobbies[0]}, exploring {selected_interests[0]}, and embracing my {selected_traits[0]} side. I regularly practice {selected_hobbies[1]} and am focused on {selected_goals[0]}.",
        f"I find meaning in {selected_hobbies[0]} and am constantly inspired by {selected_interests[0]}. As someone who's {selected_traits[0]}, I love {selected_hobbies[1]} and am committed to {selected_goals[0]}.",
        f"My approach to life is simple: be {selected_traits[0]}, enjoy {selected_hobbies[0]}, and stay curious about {selected_interests[0]}. I make time for {selected_hobbies[1]} while pursuing {selected_goals[0]}.",
        f"I'm someone who values {selected_hobbies[0]}, is fascinated by {selected_interests[0]}, and embraces being {selected_traits[0]}. My free time is spent {selected_hobbies[1]} and planning to {selected_goals[0]}.",
        f"What brings me joy? {selected_hobbies[0]}, {selected_interests[0]}, and living as a {selected_traits[0]} individual. I'm passionate about {selected_hobbies[1]} and dedicated to {selected_goals[0]}.",
        f"I believe in pursuing what makes you happy - for me, that's {selected_hobbies[0]} and {selected_interests[0]}. My {selected_traits[0]} personality shines when I'm {selected_hobbies[1]} or working to {selected_goals[0]}.",
        f"My life is a blend of {selected_hobbies[0]}, {selected_interests[0]}, and authentic {selected_traits[0]} living. I cherish time spent {selected_hobbies[1]} and am passionate about {selected_goals[0]}.",
        f"I'm driven by my love for {selected_hobbies[0]} and curiosity about {selected_interests[0]}. Being naturally {selected_traits[0]}, I find fulfillment in {selected_hobbies[1]} and strive to {selected_goals[0]}.",
        f"As a {selected_traits[0]} person, I'm energized by {selected_hobbies[0]} and constantly exploring {selected_interests[0]}. My free time is dedicated to {selected_hobbies[1]} and {selected_goals[0]}.",
        f"I find balance through {selected_hobbies[0]} and stay inspired by {selected_interests[0]}. My {selected_traits[0]} nature helps me enjoy {selected_hobbies[1]} while working towards {selected_goals[0]}.",
        f"My passions include {selected_hobbies[0]}, {selected_interests[0]}, and living authentically as a {selected_traits[0]} individual. I love spending time {selected_hobbies[1]} and am focused on {selected_goals[0]}.",
        f"I'm someone who thrives on {selected_hobbies[0]} and has a deep appreciation for {selected_interests[0]}. Being {selected_traits[0]} by nature, I enjoy {selected_hobbies[1]} and hope to {selected_goals[0]}.",
        f"What makes life meaningful? For me, it's {selected_hobbies[0]}, {selected_interests[0]}, and embracing my {selected_traits[0]} spirit. I regularly practice {selected_hobbies[1]} and am committed to {selected_goals[0]}.",
        f"I'm passionate about {selected_hobbies[0]} and find myself constantly drawn to {selected_interests[0]}. My {selected_traits[0]} personality leads me to {selected_hobbies[1]} and pursue {selected_goals[0]}.",
        f"Life is about finding what you love - mine happens to be {selected_hobbies[0]} and {selected_interests[0]}. As a {selected_traits[0]} person, I enjoy {selected_hobbies[1]} and am working to {selected_goals[0]}.",
        f"I believe in living fully, which for me means {selected_hobbies[0]}, exploring {selected_interests[0]}, and being genuinely {selected_traits[0]}. I make time for {selected_hobbies[1]} while pursuing {selected_goals[0]}.",
        f"My world revolves around {selected_hobbies[0]}, {selected_interests[0]}, and the joy of being {selected_traits[0]}. I'm passionate about {selected_hobbies[1]} and dedicated to {selected_goals[0]}.",
        f"I'm energized by {selected_hobbies[0]} and have developed a fascination with {selected_interests[0]}. Being {selected_traits[0]} helps me appreciate {selected_hobbies[1]} and stay focused on {selected_goals[0]}.",
        f"What drives me daily? My love for {selected_hobbies[0]}, curiosity about {selected_interests[0]}, and {selected_traits[0]} approach to life. I cherish {selected_hobbies[1]} and am determined to {selected_goals[0]}.",
        f"I find fulfillment in {selected_hobbies[0]} and am constantly learning about {selected_interests[0]}. My {selected_traits[0]} nature shines when I'm {selected_hobbies[1]} or planning to {selected_goals[0]}.",
        f"As someone who's naturally {selected_traits[0]}, I'm drawn to {selected_hobbies[0]} and fascinated by {selected_interests[0]}. My free time includes {selected_hobbies[1]} and working towards {selected_goals[0]}.",
        f"I believe in following your heart - mine leads to {selected_hobbies[0]} and {selected_interests[0]}. Being {selected_traits[0]}, I find joy in {selected_hobbies[1]} and am passionate about {selected_goals[0]}.",
        f"My life is enriched by {selected_hobbies[0]}, {selected_interests[0]}, and authentic {selected_traits[0]} living. I love spending time {selected_hobbies[1]} while pursuing {selected_goals[0]}.",
        f"I'm someone who values {selected_hobbies[0]} and stays curious about {selected_interests[0]}. My {selected_traits[0]} personality helps me enjoy {selected_hobbies[1]} and remain committed to {selected_goals[0]}.",
        f"What brings meaning to my days? {selected_hobbies[0]}, {selected_interests[0]}, and living as a {selected_traits[0]} individual. I'm passionate about {selected_hobbies[1]} and focused on {selected_goals[0]}.",
        f"I thrive on {selected_hobbies[0]} and have a genuine interest in {selected_interests[0]}. Being naturally {selected_traits[0]}, I make time for {selected_hobbies[1]} while working to {selected_goals[0]}.",
        f"My approach to happiness includes {selected_hobbies[0]}, exploring {selected_interests[0]}, and embracing my {selected_traits[0]} side. I regularly practice {selected_hobbies[1]} and strive to {selected_goals[0]}.",
        f"I'm passionate about creating a life filled with {selected_hobbies[0]} and {selected_interests[0]}. As a {selected_traits[0]} person, I enjoy {selected_hobbies[1]} and am dedicated to {selected_goals[0]}.",
        f"Life is an adventure that includes {selected_hobbies[0]}, {selected_interests[0]}, and being authentically {selected_traits[0]}. I love {selected_hobbies[1]} and hope to {selected_goals[0]}.",
        f"I find balance through {selected_hobbies[0]} and stay inspired by my interest in {selected_interests[0]}. My {selected_traits[0]} nature leads me to {selected_hobbies[1]} and pursue {selected_goals[0]}.",
        f"What defines my journey? A combination of {selected_hobbies[0]}, {selected_interests[0]}, and living as a {selected_traits[0]} individual. I'm passionate about {selected_hobbies[1]} and committed to {selected_goals[0]}.",
        f"I'm energized by {selected_hobbies[0]} and constantly exploring the world of {selected_interests[0]}. Being {selected_traits[0]} by nature, I cherish {selected_hobbies[1]} and am working towards {selected_goals[0]}.",
        f"My ideal life includes {selected_hobbies[0]}, deep dives into {selected_interests[0]}, and authentic {selected_traits[0]} expression. I make time for {selected_hobbies[1]} while pursuing {selected_goals[0]}.",
        f"I believe in living with purpose, which for me means {selected_hobbies[0]} and {selected_interests[0]}. As a {selected_traits[0]} person, I find joy in {selected_hobbies[1]} and strive to {selected_goals[0]}.",
        f"What makes me unique? My passion for {selected_hobbies[0]}, fascination with {selected_interests[0]}, and {selected_traits[0]} personality. I love {selected_hobbies[1]} and am focused on {selected_goals[0]}.",
        f"I'm someone who thrives on {selected_hobbies[0]} and has developed a love for {selected_interests[0]}. My {selected_traits[0]} spirit helps me appreciate {selected_hobbies[1]} and stay dedicated to {selected_goals[0]}.",
        f"Life's journey includes {selected_hobbies[0]}, exploring {selected_interests[0]}, and embracing being {selected_traits[0]}. I regularly practice {selected_hobbies[1]} and am passionate about {selected_goals[0]}.",
        f"I find meaning in {selected_hobbies[0]} and am constantly inspired by {selected_interests[0]}. Being naturally {selected_traits[0]}, I enjoy {selected_hobbies[1]} and hope to {selected_goals[0]}.",
        f"My world is shaped by {selected_hobbies[0]}, {selected_interests[0]}, and authentic {selected_traits[0]} living. I'm passionate about {selected_hobbies[1]} and committed to {selected_goals[0]}.",
        f"I'm driven by my love for {selected_hobbies[0]} and curiosity about {selected_interests[0]}. As a {selected_traits[0]} individual, I make time for {selected_hobbies[1]} while working to {selected_goals[0]}.",
        f"What brings joy to my life? {selected_hobbies[0]}, {selected_interests[0]}, and living as a {selected_traits[0]} person. I cherish {selected_hobbies[1]} and am determined to {selected_goals[0]}.",
        f"I believe in following what inspires you - for me, that's {selected_hobbies[0]} and {selected_interests[0]}. My {selected_traits[0]} nature shines when I'm {selected_hobbies[1]} or pursuing {selected_goals[0]}.",
        f"My life philosophy centers around {selected_hobbies[0]}, {selected_interests[0]}, and being genuinely {selected_traits[0]}. I find fulfillment in {selected_hobbies[1]} and am focused on {selected_goals[0]}.",
        f"I'm energized by {selected_hobbies[0]} and have a deep appreciation for {selected_interests[0]}. Being {selected_traits[0]} helps me enjoy {selected_hobbies[1]} while staying committed to {selected_goals[0]}.",
        f"What makes each day special? My passion for {selected_hobbies[0]}, interest in {selected_interests[0]}, and {selected_traits[0]} approach to life. I love {selected_hobbies[1]} and am working towards {selected_goals[0]}.",
        f"I find balance through {selected_hobbies[0]} and stay curious about {selected_interests[0]}. My {selected_traits[0]} personality leads me to {selected_hobbies[1]} and pursue {selected_goals[0]}.",
        f"Life is about creating moments that matter - mine include {selected_hobbies[0]} and {selected_interests[0]}. As a {selected_traits[0]} person, I enjoy {selected_hobbies[1]} and strive to {selected_goals[0]}.",
        f"I'm passionate about {selected_hobbies[0]} and constantly exploring {selected_interests[0]}. Being naturally {selected_traits[0]}, I make time for {selected_hobbies[1]} and am dedicated to {selected_goals[0]}.",
        f"My journey includes {selected_hobbies[0]}, deep interest in {selected_interests[0]}, and authentic {selected_traits[0]} expression. I regularly practice {selected_hobbies[1]} while pursuing {selected_goals[0]}.",
        f"I believe in living authentically, which means {selected_hobbies[0]} and {selected_interests[0]}. My {selected_traits[0]} spirit helps me appreciate {selected_hobbies[1]} and stay focused on {selected_goals[0]}.",
        f"What drives my passion? A combination of {selected_hobbies[0]}, {selected_interests[0]}, and being {selected_traits[0]}. I find joy in {selected_hobbies[1]} and am committed to {selected_goals[0]}.",
        f"I'm someone who values {selected_hobbies[0]} and is fascinated by {selected_interests[0]}. Being {selected_traits[0]} by nature, I love {selected_hobbies[1]} and hope to {selected_goals[0]}.",
        f"My ideal world includes {selected_hobbies[0]}, exploration of {selected_interests[0]}, and living as a {selected_traits[0]} individual. I'm passionate about {selected_hobbies[1]} and working to {selected_goals[0]}.",
        f"I find fulfillment in {selected_hobbies[0]} and have developed a genuine love for {selected_interests[0]}. My {selected_traits[0]} nature leads me to {selected_hobbies[1]} and pursue {selected_goals[0]}.",
        f"Life's adventure includes {selected_hobbies[0]}, {selected_interests[0]}, and embracing my {selected_traits[0]} side. I make time for {selected_hobbies[1]} while remaining dedicated to {selected_goals[0]}.",
        f"I'm energized by {selected_hobbies[0]} and constantly learning about {selected_interests[0]}. Being {selected_traits[0]} helps me enjoy {selected_hobbies[1]} and stay committed to {selected_goals[0]}.",
        f"What makes life meaningful? My passion for {selected_hobbies[0]}, curiosity about {selected_interests[0]}, and {selected_traits[0]} approach to everything. I cherish {selected_hobbies[1]} and am focused on {selected_goals[0]}.",
        f"I believe in creating a life filled with {selected_hobbies[0]} and {selected_interests[0]}. As a {selected_traits[0]} person, I find balance through {selected_hobbies[1]} while pursuing {selected_goals[0]}.",
        f"My world revolves around {selected_hobbies[0]}, fascination with {selected_interests[0]}, and authentic {selected_traits[0]} living. I'm passionate about {selected_hobbies[1]} and determined to {selected_goals[0]}.",
        f"I'm driven by my love for {selected_hobbies[0]} and deep interest in {selected_interests[0]}. Being naturally {selected_traits[0]}, I make time for {selected_hobbies[1]} and am working towards {selected_goals[0]}.",
        f"What shapes my perspective? A blend of {selected_hobbies[0]}, {selected_interests[0]}, and living as a {selected_traits[0]} individual. I regularly practice {selected_hobbies[1]} while staying focused on {selected_goals[0]}.",
        f"I find joy in {selected_hobbies[0]} and am constantly inspired by {selected_interests[0]}. My {selected_traits[0]} spirit helps me appreciate {selected_hobbies[1]} and remain committed to {selected_goals[0]}.",
        f"Life is a journey that includes {selected_hobbies[0]}, exploration of {selected_interests[0]}, and being genuinely {selected_traits[0]}. I love {selected_hobbies[1]} and am passionate about {selected_goals[0]}.",
        f"I'm someone who thrives on {selected_hobbies[0]} and has a deep appreciation for {selected_interests[0]}. Being {selected_traits[0]} by nature, I find fulfillment in {selected_hobbies[1]} and strive to {selected_goals[0]}.",
        f"My approach to happiness centers around {selected_hobbies[0]}, {selected_interests[0]}, and authentic {selected_traits[0]} expression. I make time for {selected_hobbies[1]} while pursuing {selected_goals[0]}.",
        f"I believe in living with intention, which means {selected_hobbies[0]} and {selected_interests[0]}. As a {selected_traits[0]} person, I enjoy {selected_hobbies[1]} and am dedicated to {selected_goals[0]}.",
        f"What brings meaning to each day? My passion for {selected_hobbies[0]}, interest in {selected_interests[0]}, and {selected_traits[0]} outlook on life. I cherish {selected_hobbies[1]} and hope to {selected_goals[0]}.",
        f"I'm energized by {selected_hobbies[0]} and constantly exploring the depths of {selected_interests[0]}. My {selected_traits[0]} nature leads me to {selected_hobbies[1]} and pursue {selected_goals[0]}.",
        f"Life's beauty lies in {selected_hobbies[0]}, {selected_interests[0]}, and embracing being {selected_traits[0]}. I find balance through {selected_hobbies[1]} while working towards {selected_goals[0]}.",
        f"I'm passionate about creating experiences around {selected_hobbies[0]} and {selected_interests[0]}. Being naturally {selected_traits[0]}, I love {selected_hobbies[1]} and am focused on {selected_goals[0]}.",
        f"My world is enriched by {selected_hobbies[0]}, fascination with {selected_interests[0]}, and living as a {selected_traits[0]} individual. I regularly practice {selected_hobbies[1]} and am committed to {selected_goals[0]}.",
        f"I find purpose in {selected_hobbies[0]} and am constantly inspired by {selected_interests[0]}. My {selected_traits[0]} spirit helps me enjoy {selected_hobbies[1]} while staying dedicated to {selected_goals[0]}.",
        f"What defines my journey? A love for {selected_hobbies[0]}, curiosity about {selected_interests[0]}, and {selected_traits[0]} approach to life. I make time for {selected_hobbies[1]} and am working to {selected_goals[0]}.",
        f"I believe in living fully, which includes {selected_hobbies[0]} and {selected_interests[0]}. As a {selected_traits[0]} person, I find joy in {selected_hobbies[1]} and strive to {selected_goals[0]}.",
        f"My ideal day involves {selected_hobbies[0]}, exploring {selected_interests[0]}, and authentic {selected_traits[0]} expression. I'm passionate about {selected_hobbies[1]} and determined to {selected_goals[0]}.",
        f"I'm driven by {selected_hobbies[0]} and have developed a profound interest in {selected_interests[0]}. Being {selected_traits[0]} helps me appreciate {selected_hobbies[1]} and remain focused on {selected_goals[0]}.",
        f"Life is about finding what moves you - for me, that's {selected_hobbies[0]} and {selected_interests[0]}. My {selected_traits[0]} nature shines when I'm {selected_hobbies[1]} or pursuing {selected_goals[0]}.",
        f"I find fulfillment through {selected_hobbies[0]} and stay curious about {selected_interests[0]}. Being naturally {selected_traits[0]}, I cherish {selected_hobbies[1]} and am passionate about {selected_goals[0]}.",
        f"What makes each moment special? My love for {selected_hobbies[0]}, interest in {selected_interests[0]}, and {selected_traits[0]} perspective on everything. I enjoy {selected_hobbies[1]} while working towards {selected_goals[0]}."
    ]

    return random.choice(about_templates)

def generate_date_of_birth():
    """Generate a realistic date of birth"""
    current_year = datetime.date.today().year
    age = random.randint(18, 80)
    birth_year = current_year - age

    birth_month = random.randint(1, 12)

    if birth_month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif birth_month in [4, 6, 9, 11]:
        max_day = 30
    else:
        if birth_year % 4 == 0 and (birth_year % 100 != 0 or birth_year % 400 == 0):
            max_day = 29
        else:
            max_day = 28

    birth_day = random.randint(1, max_day)

    return datetime.date(birth_year, birth_month, birth_day)

def generate_credit_card():
    """Generate a valid-looking credit card number with CVV and expiration date"""
    card_num = ''.join([str(random.randint(0, 9)) for _ in range(16)])
    formatted_num = '-'.join([card_num[i:i+4] for i in range(0, len(card_num), 4)])
    cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    current_year = datetime.datetime.now().year
    exp_year = random.randint(current_year + 1, current_year + 5)
    exp_month = random.randint(1, 12)
    exp_date = f"{exp_month:02d}/{exp_year}"

    return {
        "num": formatted_num,
        "cvv": cvv,
        "exp_date": exp_date
    }

def generate_address():
    """Generate a realistic address"""
    return {
        "country": fake.country(),
        "city": fake.city(),
        "street": fake.street_address(),
        "flat_house": random.choice([
            f"Apt {random.randint(1, 999)}",
            f"Unit {random.randint(1, 50)}",
            f"Suite {random.randint(100, 999)}",
            f"#{random.randint(1, 999)}",
            f"House {random.randint(1, 999)}"
        ])
    }

def generate_user_data():
    """Generate complete user data"""
    gender = random.choice(['male', 'female', 'other'])
    if gender == 'male':
        first_name = fake.first_name_male()
    elif gender == 'female':
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name()

    last_name = fake.last_name()
    email_domain = random.choice([
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'company.com', 'example.org', 'test.edu', 'business.net'
    ])
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{email_domain}"
    phone = fake.phone_number()
    date_of_birth = generate_date_of_birth()

    if random.random() < 0.7:
        company = fake.company()
        salary = round(random.uniform(30000, 200000), 2)
    else:
        company = None
        salary = None
    about_me = generate_about_me(gender, company)

    return {
        "name": first_name,
        "surname": last_name,
        "email": email,
        "phone": phone,
        "date_of_birth": date_of_birth,
        "gender": gender,
        "company": company,
        "salary": salary,
        "about_me": about_me,
        "address": generate_address(),
        "credit_card": generate_credit_card()
    }

def create_user_in_db(db: Session, user_data: dict):
    """Create a user and related records in the database"""
    try:
        db_user = User(
            name=user_data["name"],
            surname=user_data["surname"],
            email=user_data["email"],
            phone=user_data["phone"],
            date_of_birth=user_data["date_of_birth"],
            gender=user_data["gender"],
            company=user_data["company"],
            salary=user_data["salary"],
            about_me=user_data["about_me"]
        )
        db.add(db_user)
        db.flush()

        db_address = Address(
            user_id=db_user.id,
            country=user_data["address"]["country"],
            city=user_data["address"]["city"],
            street=user_data["address"]["street"],
            flat_house=user_data["address"]["flat_house"]
        )
        db.add(db_address)

        db_credit_card = CreditCard(
            user_id=db_user.id,
            num=user_data["credit_card"]["num"],
            cvv=user_data["credit_card"]["cvv"],
            exp_date=user_data["credit_card"]["exp_date"]
        )
        db.add(db_credit_card)

        db.commit()
        return db_user.id

    except Exception as e:
        db.rollback()
        print(f"Error creating user {user_data['email']}: {str(e)}")
        return None

def generate_test_users(count: int = 1000):
    """Generate specified number of users and insert them into the database"""
    print(f"Starting generation of {count} users...")

    db = SessionLocal()
    created_count = 0
    failed_count = 0

    try:
        for i in range(count):
            user_data = generate_user_data()
            user_id = create_user_in_db(db, user_data)

            if user_id:
                created_count += 1
                if created_count % 100 == 0:  # Progress update every 100 users
                    print(f"Created {created_count} users...")
            else:
                failed_count += 1

        print(f"\nGeneration complete!")
        print(f"   Successfully created: {created_count} users")
        print(f"   Failed: {failed_count} users")
        print(f"   Total database records: {created_count}")

    except Exception as e:
        print(f"Error during user generation: {str(e)}")
    finally:
        db.close()
