import json

def calculate_leaderboard():
    # 1. Load files
    try:
        with open('matches.json') as f: matches = json.load(f)
        with open('results.json') as f: results = json.load(f)
        with open('predictions.json') as f: raw_predictions = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Convert results to a dictionary for easy lookup
    results_map = {r['id']: r for r in results if r['scoreA'] is not None}
    
    # Process predictions (skip the header row)
    leaderboard = []

    for user_entry in raw_predictions[1:]:
        username = user_entry[1]
        pin = user_entry[2]
        total_points = 0
        
        # Track actual points earned
        stats = {"winnerPoints": 0, "exactPoints": 0}
        user_match_breakdown = []

        # Each match takes 3 columns (A, B, Winner) starting at index 3
        for m_idx, match in enumerate(matches):
            match_id = match['id']
            base = 3 + (m_idx * 3)
            
            # Bounds check for the predictions array
            if base + 2 >= len(user_entry):
                break
                
            predA, predB, predW = user_entry[base], user_entry[base+1], user_entry[base+2]
            
            # Read points dynamically from matches.json
            points_config = match['points'] 
            match_points_earned = 0

            # Only calculate points if the result exists
            if match_id in results_map:
                res = results_map[match_id]
                
                # 1. Winner Points
                if predW == res['winner']:
                    match_points_earned += points_config['winner']
                    stats["winnerPoints"] += points_config['winner']
                    
                # 2. Exact Score (Calculated independently)
                if predA == res['scoreA'] and predB == res['scoreB']:
                    match_points_earned += points_config['exact']
                    stats["exactPoints"] += points_config['exact']

            total_points += match_points_earned
            user_match_breakdown.append({
                "matchId": match_id,
                "pointsEarned": match_points_earned
            })

        leaderboard.append({
            "username": username,
            "pin": pin,
            "totalPoints": total_points,
            "breakdown": stats,
            "matchPoints": user_match_breakdown
        })

    # 1. Sort by total points (Descending)
    leaderboard.sort(key=lambda x: x['totalPoints'], reverse=True)
    
    # 2. Assign Visual Rank (1224 style)
    for i in range(len(leaderboard)):
        if i == 0:
            leaderboard[i]['rank'] = 1
        else:
            if leaderboard[i]['totalPoints'] == leaderboard[i-1]['totalPoints']:
                leaderboard[i]['rank'] = leaderboard[i-1]['rank']
            else:
                leaderboard[i]['rank'] = i + 1

    # 3. Save to file
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f, indent=4)
    
    print("Leaderboard generated successfully with dynamic point breakdowns!")

if __name__ == "__main__":
    calculate_leaderboard()