from app.services.platforms import attach_search_links


def _items(rows):
    return attach_search_links(rows)


def home_fallback(data: dict) -> dict:
    budget = data["budget"]
    breakdown = {"Furniture": round(budget*.38, 2), "Lighting": round(budget*.15, 2), "Decor": round(budget*.22, 2), "Storage": round(budget*.15, 2), "Contingency": round(budget*.10, 2)}
    items = _items([
        {"name": f"{data['style']} sofa / seating search", "category":"Furniture", "estimated_price":breakdown["Furniture"], "reason":"Start with the largest functional item and keep the style consistent.", "platform":"IKEA"},
        {"name":"LED ceiling and ambient lighting set", "category":"Lighting", "estimated_price":breakdown["Lighting"], "reason":"Layered lighting can improve the room without consuming the whole budget.", "platform":"Amazon"},
        {"name":"Wall art and soft furnishings", "category":"Decor", "estimated_price":breakdown["Decor"], "reason":"Use smaller accents to reinforce the selected style.", "platform":"Flipkart"},
        {"name":"Modular storage solutions", "category":"Storage", "estimated_price":breakdown["Storage"], "reason":"Prioritize storage around the rooms with the most daily use.", "platform":"IKEA"},
    ])
    return {"planner_type":"home","title":"Your Home Budget Plan","summary":f"A balanced {data['style']} plan for {', '.join(data['rooms'])}.","budget":budget,"currency":data["currency"],"budget_breakdown":breakdown,"items":items,"tips":["Measure rooms before purchasing large furniture.","Compare dimensions, delivery charges and warranties before buying.","Keep the contingency amount uncommitted until the final shopping list is known."],"disclaimer":"Estimated planning amounts, not live product prices or availability.","source_mode":"fallback"}


def party_fallback(data: dict) -> dict:
    budget = data["budget"]
    breakdown = {"Food": round(budget*.50,2), "Venue": round(budget*.20,2), "Decoration": round(budget*.15,2), "Entertainment": round(budget*.10,2), "Contingency": round(budget*.05,2)}
    items = _items([
        {"name":f"{data['food_preference']} catering for {data['guests']} guests","category":"Food","estimated_price":breakdown["Food"],"reason":"Food gets the largest allocation because guest count directly affects the total.","platform":"Swiggy"},
        {"name":f"{data['venue']} venue search","category":"Venue","estimated_price":breakdown["Venue"],"reason":"Keep venue cost controlled so food and experience remain funded.","platform":"OYO"},
        {"name":f"{data['event_type']} decoration package","category":"Decoration","estimated_price":breakdown["Decoration"],"reason":"A focused theme can create impact with fewer decorative items.","platform":"Amazon"},
        {"name":"Entertainment / activity ideas","category":"Entertainment","estimated_price":breakdown["Entertainment"],"reason":"Reserve a smaller, defined amount for activities rather than open-ended spending.","platform":"Zomato"},
    ])
    return {"planner_type":"party","title":"Your Party Budget Plan","summary":f"A {data['event_type']} plan for {data['guests']} guests.","budget":budget,"currency":data["currency"],"budget_breakdown":breakdown,"items":items,"tips":["Ask venues for an all-inclusive quote before paying deposits.","Confirm per-person food pricing and minimum order quantities.","Keep a contingency for transport, service charges and last-minute needs."],"disclaimer":"Estimated planning allocations, not live vendor quotes or availability.","source_mode":"fallback"}


def jewelry_fallback(data: dict, image_analysis: str | None = None) -> dict:
    budget = data["budget"]
    breakdown = {"Primary jewelry": round(budget*.65,2), "Secondary piece": round(budget*.20,2), "Accessories": round(budget*.10,2), "Contingency": round(budget*.05,2)}
    items = _items([
        {"name":f"{data['style']} statement jewelry","category":"Primary jewelry","estimated_price":breakdown["Primary jewelry"],"reason":f"Suitable for a {data['occasion']} look while keeping the main allocation within budget.","platform":"Amazon"},
        {"name":"Matching earrings / secondary piece","category":"Secondary piece","estimated_price":breakdown["Secondary piece"],"reason":"Adds coordination without using the full budget on one item.","platform":"Flipkart"},
        {"name":"Minimal matching accessory","category":"Accessories","estimated_price":breakdown["Accessories"],"reason":"Use one supporting accessory to avoid a crowded look.","platform":"Amazon"},
    ])
    return {"planner_type":"jewelry","title":"Your Jewelry Budget Plan","summary":f"A {data['style']} jewelry plan for {data['occasion']}.","budget":budget,"currency":data["currency"],"budget_breakdown":breakdown,"items":items,"tips":["Check the material, size, return policy and seller rating before purchase.","Use the outfit image as a color/style reference rather than a guarantee of exact matching.","Keep some budget unused until the final choice is confirmed."],"disclaimer":"Estimated planning amounts; verify material, authenticity, seller information, price and availability before purchase.","source_mode":"fallback","image_analysis":image_analysis}
