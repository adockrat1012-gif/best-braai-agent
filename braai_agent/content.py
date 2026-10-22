"""Picks what to post on a given day and writes the words for it.

Priority: special day (holiday) > weekend vibe (Fri/Sat/Sun) > month-end payday >
seasonal topic / charcoal & briquette tips.
"""
import random
from datetime import date

from . import calendar_sa

# ---------------------------------------------------------------------------
# Theme bank. {brand} and {cta} are filled in from config.yaml.
# Each theme: headlines (big text on image), subs (small text), captions,
# queries (free-image search words), tips (middle slide of the reel), tags.
# ---------------------------------------------------------------------------

SPECIAL = {
    "heritage_day": dict(
        headlines=["Happy National Braai Day!", "Heritage Day = Braai Day", "Light the fire, Mzansi!"],
        subs=["24 September - celebrate who we are around the fire"],
        captions=["Happy Heritage Day, Mzansi! 🇿🇦🔥 Nothing unites us like a braai. Whatever your heritage, "
                  "today we light the fire together. Tag the people you're braaiing with!"],
        queries=["braai fire", "barbecue grill meat flames", "grill party friends"],
        tips=["Today, every South African is a braai master. Wors, chops, pap & chakalaka!"],
        tags=["#HeritageDay", "#NationalBraaiDay", "#BraaiDay"]),
    "new_year": dict(
        headlines=["Happy New Year, Mzansi!", "First braai of the year"],
        subs=["New year, same love for the fire"],
        captions=["Happy New Year from all of us at {brand}! 🎆🔥 May the year be full of good coals, "
                  "good food and good people. Who's braaiing today?"],
        queries=["barbecue celebration", "grill summer party", "barbecue fire night"],
        tips=["Start the year right: good coals, good food, good friends."],
        tags=["#HappyNewYear", "#NewYearBraai"]),
    "new_years_eve": dict(
        headlines=["New Year's Eve braai?", "End the year by the fire"],
        subs=["Stock up before the shops close"],
        captions=["Last braai of the year tonight? 🎆 Make it a big one! Stock up on charcoal and briquettes "
                  "early, because the shops will be packed. {cta}"],
        queries=["barbecue night fire", "grill party", "charcoal fire night"],
        tips=["Get your fire going early. Big group = start with double the charcoal."],
        tags=["#NewYearsEve", "#FestiveBraai"]),
    "christmas": dict(
        headlines=["Merry Christmas!", "A very braai Christmas"],
        subs=["From our fire to yours"],
        captions=["Merry Christmas from {brand}! 🎄🔥 A South African Christmas is gammon, salads "
                  "and a lekker braai in the sun. Enjoy the day with your loved ones!"],
        queries=["christmas barbecue", "summer barbecue family", "grilled meat platter"],
        tips=["Braaied gammon steaks with a pineapple glaze. Trust us."],
        tags=["#MerryChristmas", "#ChristmasBraai"]),
    "christmas_eve": dict(
        headlines=["Christmas braai sorted?", "Ready for Christmas?"],
        subs=["Charcoal, briquettes, firelighters: tick, tick, tick"],
        captions=["Christmas is tomorrow! 🎄 Don't be the one who runs out of coals halfway through. "
                  "{cta}"],
        queries=["charcoal bag", "barbecue preparation", "charcoal briquettes"],
        tips=["Checklist: charcoal, briquettes, firelighters, tongs, and a cold drink."],
        tags=["#ChristmasEve", "#ChristmasBraai"]),
    "day_of_goodwill": dict(
        headlines=["Leftover braai day!", "Happy Day of Goodwill"],
        subs=["Fire it up one more time"],
        captions=["Day of Goodwill = day of leftovers on the braai 😄🔥 Braaibroodjies with yesterday's "
                  "gammon? Yes please."],
        queries=["toasted sandwich grill", "barbecue grill", "grill summer"],
        tips=["Braaibroodjie upgrade: leftover gammon, cheese, tomato and onion."],
        tags=["#DayOfGoodwill", "#Braaibroodjie"]),
    "reconciliation_day": dict(
        headlines=["Day of Reconciliation", "Together around the fire"],
        subs=["16 December - share a meal, share the fire"],
        captions=["Happy Day of Reconciliation 🇿🇦 The fire has always brought us together. "
                  "Invite the neighbours, share the meat, share the stories."],
        queries=["friends barbecue", "outdoor barbecue group", "barbecue fire"],
        tips=["Bring a dish, share a fire. That's the South African way."],
        tags=["#DayOfReconciliation", "#Mzansi"]),
    "freedom_day": dict(
        headlines=["Happy Freedom Day!", "Freedom tastes like braai"],
        subs=["27 April - celebrate with fire and friends"],
        captions=["Happy Freedom Day, South Africa! 🇿🇦🔥 Celebrate the freedom to gather, share and "
                  "braai together. Long weekend sorted?"],
        queries=["barbecue friends", "grill autumn", "barbecue fire"],
        tips=["Long weekend tip: buy extra charcoal. You WILL braai twice."],
        tags=["#FreedomDay"]),
    "youth_day": dict(
        headlines=["Happy Youth Day!", "Youth Day braai"],
        subs=["16 June - honour the past, fire up the future"],
        captions=["Happy Youth Day 🇿🇦 Remembering 1976, and celebrating the young people building "
                  "Mzansi. Winter braai today? Keep warm by the fire 🔥"],
        queries=["winter fire", "barbecue fire", "campfire"],
        tips=["Winter braai? Briquettes give long-lasting, steady heat."],
        tags=["#YouthDay", "#WinterBraai"]),
    "womens_day": dict(
        headlines=["Happy Women's Day!", "She rules the braai"],
        subs=["9 August - wathint' abafazi"],
        captions=["Happy Women's Day to all the queens of Mzansi 👑🔥 Today, the tongs are yours. "
                  "Tag a woman who braais better than everyone!"],
        queries=["woman grilling barbecue", "barbecue grill", "grill fire"],
        tips=["Today's braai master: her. Everyone else is on salad duty."],
        tags=["#WomensDay", "#WomenWhoBraai"]),
    "workers_day": dict(
        headlines=["Happy Workers' Day!", "You've earned this braai"],
        subs=["1 May - rest, relax, light the fire"],
        captions=["Happy Workers' Day! 🔥 You work hard all year. Today, the only job is keeping "
                  "the fire going. {cta}"],
        queries=["barbecue relax", "grill meat", "barbecue fire"],
        tips=["Today's only job: turn the meat once and relax."],
        tags=["#WorkersDay"]),
    "human_rights_day": dict(
        headlines=["Happy Human Rights Day", "A braai is a human right"],
        subs=["21 March - public holiday braai!"],
        captions=["Happy Human Rights Day 🇿🇦 Enjoy the public holiday with family, friends and a lekker fire."],
        queries=["barbecue family", "grill autumn", "barbecue fire"],
        tips=["Public holiday + braai = perfect day."],
        tags=["#HumanRightsDay"]),
    "good_friday": dict(
        headlines=["Easter weekend braai", "Long weekend is here!"],
        subs=["Fish on Friday, braai all weekend"],
        captions=["Easter long weekend is here! 🐣🔥 Snoek or fish on the braai today? "
                  "Stock up for the whole weekend. {cta}"],
        queries=["grilled fish", "barbecue fish", "barbecue grill"],
        tips=["Fish on the braai: hinged grid, oil the grid, skin side down first."],
        tags=["#Easter", "#GoodFriday", "#LongWeekend"]),
    "family_day": dict(
        headlines=["Happy Family Day!", "Family + fire = Family Day"],
        subs=["One more braai before the week starts"],
        captions=["Happy Family Day! 👨‍👩‍👧‍👦🔥 The best braai is the one with the whole family around the fire."],
        queries=["family barbecue", "barbecue outdoor", "grill"],
        tips=["Give the kids a job: marshmallows on the coals at the end."],
        tags=["#FamilyDay", "#Easter"]),
    "mothers_day": dict(
        headlines=["Happy Mother's Day!", "Mom's day off. Dad's on braai."],
        subs=["Spoil her today"],
        captions=["Happy Mother's Day! 💐 Today Mom relaxes, and the rest of the family handles the fire. "
                  "Tag the best mom you know!"],
        queries=["family barbecue", "barbecue table", "grilled food"],
        tips=["Spoil her: lamb chops, a fresh salad, and no dishes for her today."],
        tags=["#MothersDay"]),
    "fathers_day": dict(
        headlines=["Happy Father's Day!", "To the king of the braai"],
        subs=["Spoil Dad with a proper fire"],
        captions=["Happy Father's Day to every dad who guards the fire like it's a national treasure 🔥👑 "
                  "Tag the braai legend in your life! {cta}"],
        queries=["man grilling", "barbecue steak", "barbecue fire"],
        tips=["Gift idea: a bag of charcoal and a good steak. He'll love it."],
        tags=["#FathersDay", "#BraaiMaster"]),
    "valentines": dict(
        headlines=["Love at first braai", "Happy Valentine's Day"],
        subs=["The way to the heart is through the fire"],
        captions=["Happy Valentine's! ❤️🔥 Skip the fancy restaurant. A sunset braai for two is the "
                  "most romantic thing in Mzansi."],
        queries=["barbecue sunset", "steak grill", "candle dinner outdoor"],
        tips=["Date night: a ribeye each, a small fire, and good music."],
        tags=["#ValentinesDay", "#BraaiForTwo"]),
}

WEEKDAY = {
    4: dict(  # Friday
        headlines=["Happy Friday! Ready to braai?", "Weekend loading... 🔥", "It's Friday. Light the fire!",
                   "Happy weekend, braai people!"],
        subs=["Are you ready for the braai?", "Weekend plans: fire, friends, food",
              "Stock up on charcoal & briquettes today"],
        captions=["Happy Friday, Mzansi! 🔥 The weekend is here. Are you ready to braai? "
                  "Grab your charcoal and briquettes on the way home. {cta}",
                  "It's Friday! 🙌 Who's lighting the fire tonight? Drop a 🔥 in the comments. {cta}",
                  "Weekend loading... ⏳🔥 Coals, wors, chops, cold drinks. What's on your braai this weekend?"],
        queries=["barbecue grill meat", "grill fire evening", "barbecue party"],
        tips=["Friday tip: start the fire 45 min before you want to eat. Good coals take time."],
        tags=["#FridayFeeling", "#WeekendBraai", "#FridayBraai"]),
    5: dict(  # Saturday
        headlines=["Saturday = Braai Day", "Saturday fire is lit!", "Lekker Saturday!"],
        subs=["What's on your grid today?", "Rugby, sun & a lekker braai"],
        captions=["Saturday means one thing in South Africa: braai! 🔥 What's on your grid today? "
                  "Show us in the comments.",
                  "Match day, sunshine, fire. Saturday sorted. 🏉🔥 {cta}"],
        queries=["barbecue grill sausage", "grill meat outdoor", "barbecue steak"],
        tips=["Boerewors tip: don't prick it! Keep the juice in, turn it once or twice."],
        tags=["#SaturdayBraai", "#Boerewors"]),
    6: dict(  # Sunday
        headlines=["Sunday Funday = Braai Day!", "Sunday Funday 🔥", "Lazy Sunday braai"],
        subs=["Family, friends & a lekker fire", "Slow fire, slow day, good food"],
        captions=["Sunday Funday is Braai Day! ☀️🔥 Family around the fire, music playing, meat on the grid. "
                  "That's the good life. {cta}",
                  "Lazy Sunday? Perfect for a slow braai 😎 Who's on tong duty today?"],
        queries=["family barbecue", "barbecue outdoor sunny", "grill chicken"],
        tips=["Sunday special: whole chicken (spatchcock) over medium coals, about 45-60 min."],
        tags=["#SundayFunday", "#SundayBraai", "#BraaiDay"]),
}

PAYDAY = dict(
    headlines=["Payday weekend = Braai weekend!", "Payday? Treat yourself."],
    subs=["Upgrade the braai this month-end"],
    captions=["It's payday weekend! 💰🔥 Time for the good cuts: T-bones, lamb chops, a proper fire. {cta}"],
    queries=["t-bone steak grill", "lamb chops grill", "steak barbecue"],
    tips=["Payday treat: thick T-bone, high heat, 4-5 min a side, rest 5 min."],
    tags=["#Payday", "#MonthEnd"])

SEASON = {
    "summer": [
        dict(headlines=["Summer braai season", "Hot days, hotter coals"],
             subs=["Long evenings, cold drinks, lekker fire"],
             captions=["South African summer = braai every chance we get ☀️🔥 Sosaties, mielies, salads, "
                       "and a sunset. Who's in?"],
             queries=["summer barbecue", "grilled corn", "kebab grill"],
             tips=["Summer tip: braai before the afternoon storm rolls in. Start early!"],
             tags=["#SummerBraai", "#Sosaties"]),
        dict(headlines=["Sosatie season!", "Skewers on the grid"],
             subs=["Apricot, onion, lamb. Classic."],
             captions=["Nothing says summer like sosaties on the braai 🍢🔥 Soak your wooden skewers in water "
                       "first so they don't burn!"],
             queries=["kebab grill", "skewers barbecue", "grilled kebabs"],
             tips=["Soak wooden skewers 30 min in water so they don't burn."],
             tags=["#Sosaties", "#SummerBraai"]),
    ],
    "autumn": [
        dict(headlines=["Autumn evenings by the fire", "Cool nights, warm coals"],
             subs=["Perfect braai weather is here"],
             captions=["Autumn in SA is braai perfection 🍂🔥 Not too hot, not too cold, just right for a "
                       "fire under the stars."],
             queries=["campfire evening", "barbecue autumn", "fire pit"],
             tips=["Autumn tip: cooler evenings mean coals last longer. Use less, enjoy more."],
             tags=["#AutumnBraai"]),
        dict(headlines=["Potjie season starts now", "Bring out the potjie!"],
             subs=["Slow food, good company"],
             captions=["As the evenings cool down, it's time to dust off the potjie 🍲🔥 What's your "
                       "favourite potjie recipe?"],
             queries=["cast iron pot fire", "stew over fire", "dutch oven campfire"],
             tips=["Potjie rule #1: layer it, don't stir it!"],
             tags=["#Potjiekos", "#AutumnBraai"]),
    ],
    "winter": [
        dict(headlines=["Winter braai? Always.", "Cold outside, fire inside"],
             subs=["South Africans braai all year round"],
             captions=["It's cold, but a South African never stops braaiing ❄️🔥 Gather round the fire, "
                       "the warmest place in the house is the braai. {cta}"],
             queries=["winter campfire", "fire night", "glowing charcoal grill"],
             tips=["Winter tip: use more coals. Cold air steals heat from the fire."],
             tags=["#WinterBraai", "#BraaiAllYear"]),
        dict(headlines=["Potjiekos weather!", "Winter = Potjie time"],
             subs=["Slow-cooked on the coals"],
             captions=["Winter calls for potjiekos 🍲🔥 Oxtail, lamb or chicken, slow-cooked for hours over "
                       "the coals. What's in your pot this weekend?"],
             queries=["cast iron pot fire", "stew cooking fire", "dutch oven campfire"],
             tips=["Potjie: low coals under the pot only, 3 hours, lid ON."],
             tags=["#Potjiekos", "#WinterBraai"]),
        dict(headlines=["Briquettes: winter's best friend", "Long-lasting winter coals"],
             subs=["Steady heat for cold nights"],
             captions=["Briquettes give steady, long-lasting heat: perfect for chilly winter nights "
                       "around the fire 🔥 {cta}"],
             queries=["charcoal briquettes", "glowing charcoal", "winter fire night"],
             tips=["Briquettes burn longer and steadier. Ideal for winter braais."],
             tags=["#Briquettes", "#WinterBraai"]),
    ],
    "spring": [
        dict(headlines=["Braai season is back!", "Spring has sprung. Light the fire!"],
             subs=["Longer days = more braai time"],
             captions=["Spring is here, Mzansi! 🌸🔥 The days are longer, the weather's lekker, and the "
                       "braai season is officially back. {cta}"],
             queries=["spring barbecue garden", "barbecue outdoor", "grill garden"],
             tips=["Spring clean your braai: scrape the grid and clear old ash."],
             tags=["#SpringBraai", "#BraaiSeason"]),
        dict(headlines=["Clean grid, happy braai", "Spring clean your braai"],
             subs=["New season, fresh start"],
             captions=["New season, clean grid! 🧽🔥 Heat the grid over the coals, then scrub with a "
                       "crumpled ball of foil. Easy."],
             queries=["barbecue grill grate", "clean grill", "grill grate fire"],
             tips=["Heat the grid first, then scrub with crumpled foil. Done."],
             tags=["#SpringBraai", "#BraaiTips"]),
    ],
}

FUEL_TIPS = [
    dict(headlines=["Charcoal & Briquettes", "Everything for your fire"],
         subs=["Charcoal & briquettes at Best Braai"],
         captions=["Charcoal or briquettes: whatever your fire needs, we've got you covered 🔥 {cta}"],
         queries=["charcoal grill", "glowing charcoal", "charcoal briquettes grill"],
         tips=["Charcoal or briquettes. Pick your fire."],
         tags=["#Charcoal", "#Briquettes"]),
    dict(headlines=["Ready for a big braai?", "Stock up. Light up."],
         subs=["Charcoal & briquettes"],
         captions=["Big braai coming up? 🔥 Stock up on charcoal and briquettes so the fire "
                   "keeps going from the first chop to the last braaibroodjie. {cta}"],
         queries=["steak charcoal grill", "barbecue grill meat charcoal", "charcoal embers"],
         tips=["Good fuel = steady heat from the first chop to the last braaibroodjie."],
         tags=["#Charcoal", "#Briquettes"]),
    dict(headlines=["Charcoal or briquettes?", "The great braai debate"],
         subs=["Charcoal = fast & hot. Briquettes = long & steady."],
         captions=["Charcoal or briquettes? 🤔🔥 Charcoal lights fast and burns hot. Briquettes give "
                   "steady, even heat that lasts. Team charcoal or team briquettes? Comment below! {cta}"],
         queries=["charcoal grill", "charcoal briquettes", "charcoal embers"],
         tips=["Short on time? Charcoal. Long braai? Briquettes."],
         tags=["#Charcoal", "#Briquettes", "#BraaiTips"]),
    dict(headlines=["Which fuel for which meat?", "Pick your fire"],
         subs=["Each one has its moment"],
         captions=["Which fuel for which braai? 🔥 Charcoal: quick and hot, great for steak and chops. "
                   "Briquettes: steady heat that lasts, perfect for chicken, ribs and long braais. "
                   "What's your favourite? {cta}"],
         queries=["charcoal briquettes grill", "glowing charcoal", "grilled chicken charcoal"],
         tips=["Steak & chops: charcoal. Chicken & ribs: briquettes."],
         tags=["#Charcoal", "#Briquettes"]),
    dict(headlines=["The 5-second hand test", "Are your coals ready?"],
         subs=["Hold your hand above the grid"],
         captions=["How do you know the coals are ready? ✋🔥 Hold your hand 10 cm above the grid. "
                   "2 seconds = very hot (steak). 4-5 seconds = medium (chops & wors). "
                   "7+ seconds = low (chicken & potjie)."],
         queries=["glowing charcoal", "hot coals grill", "embers fire"],
         tips=["2 sec = steak. 5 sec = chops & wors. 7+ sec = chicken."],
         tags=["#BraaiTips", "#BraaiHacks"]),
    dict(headlines=["Wait for white coals", "Patience = perfect braai"],
         subs=["No flames. Just glowing coals."],
         captions=["The #1 braai mistake? Putting the meat on too early 😬 Wait until the flames die "
                   "down and the coals are covered in white ash. Patience pays off!"],
         queries=["glowing charcoal", "charcoal embers", "hot coals"],
         tips=["Flames burn. Coals cook. Wait for the white ash."],
         tags=["#BraaiTips", "#Charcoal"]),
    dict(headlines=["Skip the lighter fluid", "Light it like a pro"],
         subs=["Firelighters + kindling + patience"],
         captions=["Lighter fluid makes your meat taste like petrol ⛽🤢 Use firelighters, newspaper and "
                   "dry kindling under your charcoal or briquettes for a clean fire. {cta}"],
         queries=["lighting fire kindling", "fire starting", "campfire flames"],
         tips=["Firelighter at the bottom, kindling on top, charcoal or briquettes on top of that."],
         tags=["#BraaiTips", "#Firelighters"]),
    dict(headlines=["Two-zone fire = braai master", "Hot side, cool side"],
         subs=["Sear on the hot side, finish on the cool side"],
         captions=["Pro tip: bank your coals to one side 🔥 Sear on the hot side, then move the meat "
                   "to the cooler side to finish without burning."],
         queries=["barbecue grill steak", "charcoal grill meat", "grill flames"],
         tips=["Hot side to sear. Cool side to cook through. Never burn a chop again."],
         tags=["#BraaiTips", "#BraaiMaster"]),
    dict(headlines=["Let the meat rest", "Don't cut it yet!"],
         subs=["5 minutes. Juicy every time."],
         captions=["Cutting the steak straight off the fire? 🛑 Let it rest 5 minutes so the juices "
                   "settle. Your patience will be rewarded."],
         queries=["steak cutting board", "grilled steak", "steak grill"],
         tips=["Rest your steak 5 min under foil. Juicy every time."],
         tags=["#BraaiTips", "#Steak"]),
    dict(headlines=["The braaibroodjie rule", "Braaibroodjies, the real MVP"],
         subs=["Last on, first gone"],
         captions=["Let's be honest: the braaibroodjies disappear first 🥪🔥 Cheese, tomato, onion, "
                   "chutney, buttered on the outside. Low coals, turn often."],
         queries=["grilled cheese sandwich", "toasted sandwich", "grill bread"],
         tips=["Butter on the OUTSIDE, low coals, turn often. Perfection."],
         tags=["#Braaibroodjie", "#BraaiTips"]),
    dict(headlines=["Stock up for the weekend", "Never run out of coals"],
         subs=["Charcoal, briquettes & firelighters"],
         captions=["Nothing worse than running out of coals mid-braai 😩 Stock up now and you're "
                   "ready for the weekend. {cta}"],
         queries=["charcoal bag", "charcoal briquettes", "charcoal pile"],
         tips=["Rule of thumb: 1 bag of charcoal or briquettes per 4-6 people."],
         tags=["#Charcoal", "#Briquettes"]),
]

SEASON_LINES = {
    "summer": "☀️ Summer braai season in Mzansi",
    "autumn": "🍂 Autumn evenings by the fire",
    "winter": "❄️ Winter warmer: braai all year round",
    "spring": "🌸 Spring braai season is back",
}

# Close-up braai photos: meat on the grid over real coals. One of these is always the
# feed photo, so every post shows food on the fire.
FOOD_SHOTS = {
    "all": ["steak on charcoal grill", "meat grilling over charcoal", "lamb chops on grill",
            "sausages on charcoal grill", "chicken on barbecue grill charcoal", "t-bone steak grill",
            "grilled meat flames", "barbecue grill embers meat", "ribs on charcoal grill",
            "boerewors braai", "kebab skewers charcoal grill"],
    "summer": ["grilled corn barbecue", "grilled kebabs summer", "grilled fish barbecue"],
    "autumn": ["grilled steak dark", "cast iron pot fire"],
    "winter": ["cast iron pot campfire", "meat grilling charcoal night", "fire pit grill night"],
    "spring": ["barbecue garden grill meat", "grilled chicken wings charcoal"],
}

BASE_TAGS = ["#braai", "#SouthAfrica", "#Mzansi", "#bbq", "#barbecue", "#ShisaNyama",
             "#LekkerBraai", "#BraaiLife"]


def _tag(theme_id, season):
    """Small label above the headline."""
    if theme_id.startswith("weekday_"):
        return {"4": "Weekend braai", "5": "Saturday braai", "6": "Sunday braai"}[theme_id[-1]]
    if theme_id.startswith("fuel_tip"):
        return "Braai tip"
    if theme_id == "payday":
        return "Payday weekend"
    if theme_id.startswith("season_"):
        return f"{season} braai season"
    return "Braai day"


def _queries(theme, season, rng):
    """Food-on-the-coals shot first (feed photo), then alternate theme and food searches."""
    food = FOOD_SHOTS["all"] + FOOD_SHOTS[season] * 2
    picks = rng.sample(food, 3)
    out = []
    for i in range(3):
        out += [picks[i], theme["queries"][i % len(theme["queries"])]]
    return list(dict.fromkeys(out))


def pick_theme(d: date, every_n_days: int = 2):
    """Returns (theme_id, theme_dict)."""
    rng = random.Random(d.toordinal())
    # Cover special days that fall before the next posting day.
    special = calendar_sa.upcoming_special(d, lookahead=every_n_days - 1)
    if special and special[0] in SPECIAL:
        return special[0], SPECIAL[special[0]]
    if d.weekday() in WEEKDAY:
        return f"weekday_{d.weekday()}", WEEKDAY[d.weekday()]
    if calendar_sa.is_payday_weekend(d):
        return "payday", PAYDAY
    # Mid-week: alternate between seasonal topics and charcoal/briquette tips.
    s = calendar_sa.season(d)
    if d.toordinal() // 2 % 2 == 0:
        i = rng.randrange(len(SEASON[s]))
        return f"season_{s}_{i}", SEASON[s][i]
    i = (d.toordinal() // 4) % len(FUEL_TIPS)
    return f"fuel_tip_{i}", FUEL_TIPS[i]


def build_post(d: date, cfg: dict) -> dict:
    """All the words for one posting day: feed image, story and reel."""
    rng = random.Random(d.toordinal() * 7)
    theme_id, t = pick_theme(d, int(cfg["schedule"].get("every_n_days", 2)))
    s = calendar_sa.season(d)
    brand = cfg["brand"]["name"]
    cta = cfg["brand"].get("cta", "")
    fill = lambda text: text.format(brand=brand, cta=cta).strip()

    headline = rng.choice(t["headlines"])
    tags = list(dict.fromkeys(t["tags"] + BASE_TAGS + cfg["brand"].get("hashtags", [])))[:15]
    caption = "\n\n".join([fill(rng.choice(t["captions"])), SEASON_LINES[s], " ".join(tags)])

    story_cta = cfg["brand"].get("story_cta", cta) or "Tap to follow for braai tips"
    return {
        "date": d.isoformat(),
        "theme": theme_id,
        "season": s,
        "tag": _tag(theme_id, s),
        "queries": _queries(t, s, rng),
        "feed": {"headline": headline, "sub": rng.choice(t["subs"])},
        "story": {"headline": headline, "sub": fill(story_cta)},
        "reel": {
            "slides": [
                {"headline": headline, "sub": rng.choice(t["subs"])},
                {"headline": fill(rng.choice(t["tips"])), "sub": ""},
                {"headline": brand, "sub": fill(story_cta)},
            ]
        },
        "caption": caption,
    }
