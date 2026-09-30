from urllib.parse import quote_plus

def _link(platform: str, query: str) -> str:
    q = quote_plus(query)
    links = {
        "Amazon": f"https://www.amazon.in/s?k={q}",
        "Flipkart": f"https://www.flipkart.com/search?q={q}",
        "IKEA": f"https://www.ikea.com/in/en/search/?q={q}",
        "Swiggy": f"https://www.swiggy.com/search?query={q}",
        "Zomato": f"https://www.zomato.com/search?query={q}",
        "OYO": f"https://www.oyorooms.com/search?location={q}",
    }
    return links.get(platform, f"https://www.google.com/search?q={q}")

def home_fallback(req):
    categories = list(req.items.keys()) or ["Lighting", "Furniture", "Decor"]
    per = round(req.budget / len(categories), 2)
    recs = []
    for i, category in enumerate(categories):
        platform = ["Amazon", "IKEA", "Flipkart"][i % 3]
        query = f"{category} {req.style} home decor"
        recs.append({
            "category": category,
            "name": f"Budget {req.style} {category}",
            "estimated_price": per,
            "platform": platform,
            "url": _link(platform, query),
            "why": f"Practical {req.style.lower()} option within the allocated category budget."
        })
    return {
        "title": "Home Interior Budget Plan",
        "summary": f"A {req.style} setup planned around ₹{req.budget:,.0f}.",
        "budget": req.budget,
        "allocations": [{"category": c["category"], "amount": per} for c in recs],
        "recommendations": recs,
        "assumptions": ["Prices are estimates, not live inventory prices.", "Shipping/taxes are not included."]
    }

def party_fallback(req):
    allocation = {
        "Catering": round(req.budget * .50, 2),
        "Decoration": round(req.budget * .20, 2),
        "Entertainment": round(req.budget * .15, 2),
        "Venue/Stay": round(req.budget * .15, 2)
    }
    recs = [
        {"category":"Catering","name":f"{req.event_type} catering for {req.guests} guests","estimated_price":allocation["Catering"],"platform":"Swiggy","url":_link("Swiggy",f"{req.event_type} catering {req.city}"),"why":"Guest count directly affects catering needs."},
        {"category":"Food alternative","name":f"{req.event_type} restaurants","estimated_price":allocation["Catering"],"platform":"Zomato","url":_link("Zomato",f"{req.event_type} {req.city}"),"why":"Useful for comparing restaurant choices."},
        {"category":"Venue/Stay","name":f"Event-friendly stay near {req.city or 'your city'}","estimated_price":allocation["Venue/Stay"],"platform":"OYO","url":_link("OYO",req.city or "India"),"why":"Included as an optional venue/stay search."},
        {"category":"Decoration","name":f"{req.event_type} decoration supplies","estimated_price":allocation["Decoration"],"platform":"Amazon","url":_link("Amazon",f"{req.event_type} party decoration"),"why":"Keeps decoration spending separate from food."}
    ]
    return {
        "title": f"{req.event_type} Party Budget Plan",
        "summary": f"Budget allocation for {req.guests} guests.",
        "budget": req.budget,
        "allocations": [{"category":k,"amount":v} for k,v in allocation.items()],
        "recommendations": recs,
        "assumptions": ["Venue costs vary by city and date.", "Food and vendor prices are estimates."]
    }

def jewelry_fallback(budget, occasion, style, image_present):
    names = [("Necklace","necklace"),("Earrings","earrings"),("Bracelet","bracelet")]
    per = round(budget / 3, 2)
    recs = []
    for i, (cat, noun) in enumerate(names):
        platform = ["Amazon","Flipkart","Amazon"][i]
        query = f"{style} {occasion} {noun} jewelry"
        recs.append({
            "category":cat,
            "name":f"{style} {occasion} {noun}",
            "estimated_price":per,
            "platform":platform,
            "url":_link(platform,query),
            "why":"Matches the requested occasion and style; inspect current listings through the platform."
        })
    return {
        "title":f"{occasion} Jewelry Plan",
        "summary":f"Style-matched jewelry ideas within ₹{budget:,.0f}." + (" Outfit image was received." if image_present else ""),
        "budget":budget,
        "allocations":[{"category":"Jewelry selection","amount":budget}],
        "recommendations":recs,
        "assumptions":["Listings and prices are not live product data.","Image-based color analysis is available when Gemini is configured."]
    }
